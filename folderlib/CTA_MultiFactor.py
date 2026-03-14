# -*- coding: utf-8 -*-
"""
CTA Multi-Factor (MVP)
- Universe: commodity futures (yfinance tickers like CL=F, GC=F...)
- Interval: 1d
- Margin: set to 0 (per your config); order sizing uses notional-based heuristic
"""

import numpy as np
import pandas as pd

import backtestlib.backtest as bb
import backtestlib.tradingpanel as bt
import folderlib.folder as ff


def _zscore(s: pd.Series, window: int = 60) -> pd.Series:
    mean = s.rolling(window).mean()
    std = s.rolling(window).std(ddof=0)
    z = (s - mean) / std.replace(0, np.nan)
    return z


def _is_month_end(dt: pd.Timestamp, calendar_index: pd.DatetimeIndex) -> bool:
    if dt not in calendar_index:
        return False
    pos = calendar_index.get_loc(dt)
    if isinstance(pos, slice) or isinstance(pos, np.ndarray):
        return False
    if pos == len(calendar_index) - 1:
        return True
    next_dt = calendar_index[pos + 1]
    return next_dt.month != dt.month


def folder_main(changable_var_dict, show_balance=False, show_details=False, show_pnl=False):
    """
    changable_var_dict required:
      - account
      - interval: '1d'
      - contract: 'c1'
      - backtest_start_date, backtest_end_date
      - commodities: list[Commodity]
    optional:
      - initial_cash (default 100000)
      - target_vol_annual (default 0.15)
      - max_contracts_per_asset (default 2)
    """
    account = changable_var_dict["account"]
    interval = changable_var_dict["interval"]
    contract = changable_var_dict["contract"]
    backtest_start_date = changable_var_dict["backtest_start_date"]
    backtest_end_date = changable_var_dict["backtest_end_date"]
    commodities = changable_var_dict["commodities"]

    initial_cash = changable_var_dict.get("initial_cash", 100000)
    target_vol_annual = changable_var_dict.get("target_vol_annual", 0.15)
    max_contracts_per_asset = changable_var_dict.get("max_contracts_per_asset", 2)

    # reset & fund account
    account.reset()
    account.deposit(initial_cash)

    # build trading panel & load data
    tradingpanel = bt.TradingPanel(account)
    for commodity in commodities:
        md = commodity.marketdata[contract]
        if commodity.data_source == "yfinance":
            md.automatic_get_data_from_yfinance(interval, backtest_start_date, backtest_end_date)
        else:
            md.get_data_from_xlsx(interval, backtest_start_date, backtest_end_date)
        tradingpanel.append_marketdata(md, interval)

    # collect Close prices
    close_df = pd.DataFrame()
    for commodity in commodities:
        md = commodity.marketdata[contract]
        md_name = bt.get_marketdata_name(md, interval)
        df = tradingpanel.marketdatas[md_name].copy()
        close_df[commodity.symbol] = df["Close"]

    close_df = close_df.dropna(how="all")
    ret_df = close_df.pct_change()

    mom_60 = close_df.pct_change(60)
    rev_5 = close_df.pct_change(5)
    vol_20 = ret_df.rolling(20).std(ddof=0)

    # score = z(mom_60) + z(-rev_5)
    score = pd.DataFrame(index=close_df.index)
    for sym in close_df.columns:
        z_mom = _zscore(mom_60[sym], window=60)
        z_rev = _zscore(-rev_5[sym], window=60)
        score[sym] = z_mom + z_rev

    # folder object
    folder = ff.Folder(name="CTA_MultiFactor", description="Multi-factor CTA (mom+reversal) with vol targeting")
    folder.folder_dict["account"] = account
    folder.folder_dict["interval"] = interval
    folder.folder_dict["tradingpanel"] = tradingpanel

    folder.commodities = {c.symbol: c for c in commodities}
    folder.contract = contract
    folder.score = score
    folder.vol_20 = vol_20
    folder.close_df = close_df
    folder.target_vol_annual = target_vol_annual
    folder.max_contracts_per_asset = max_contracts_per_asset

    folder._init_folder()

    out = bb.single_interval_backtest(
        backtest_start_date,
        backtest_end_date,
        folder,
        show_balance=show_balance,
        show_details=show_details,
        show_pnl=show_pnl,
    )
    return {"output": out}


def CTA_MultiFactor(self, time_index):
    # rebalance at month end only
    calendar_index = self.close_df.index
    t = pd.Timestamp(time_index)
    if not _is_month_end(t, calendar_index):
        return

    if time_index not in self.score.index:
        return

    s = self.score.loc[time_index].dropna()
    if s.empty:
        return

    # cross-sectional weights: sum(abs(w))=1
    w = s.clip(-3, 3)
    if w.abs().sum() == 0:
        return
    w = w / w.abs().sum()

    # vol targeting
    vol = self.vol_20.loc[time_index].reindex(w.index)
    ann_vol = vol * np.sqrt(252)
    ann_vol = ann_vol.replace(0, np.nan)

    w_risk = (w / ann_vol).replace([np.inf, -np.inf], np.nan).dropna()
    if w_risk.empty:
        return
    w_risk = w_risk / w_risk.abs().sum()

    account = self.folder_dict["account"]
    tradingpanel = self.folder_dict["tradingpanel"]
    interval = self.folder_dict["interval"]
    contract = self.contract

    # total notional = balance (MVP 1x)
    balance = getattr(account, "balance", None)
    cash = getattr(account, "cash", None)
    if balance is None:
        balance = cash if cash is not None else 0
    if balance <= 0:
        balance = cash if cash is not None else 0

    notional_total = float(balance)

    for sym, weight in w_risk.items():
        commodity = self.commodities.get(sym)
        if commodity is None:
            continue

        md = commodity.marketdata[contract]
        md_name = bt.get_marketdata_name(md, interval)
        if md_name not in tradingpanel.marketdatas:
            continue

        df = tradingpanel.marketdatas[md_name]
        if time_index not in df.index:
            continue

        price = float(df.loc[time_index, "Close"])
        if not np.isfinite(price) or price <= 0:
            continue

        target_notional = float(weight) * notional_total
        target_contracts_float = target_notional / (price * float(commodity.contract_size))

        # round & clamp
        target_contracts = int(np.sign(target_contracts_float) * min(abs(target_contracts_float), self.max_contracts_per_asset))

        # current net position size (contracts)
        # inventory key style in your repo commonly uses "{symbol}_{contract}"
        current = account.inventory.get_net_position_size(f"{commodity.symbol}_{contract}")

        delta = target_contracts - current
        if delta == 0:
            continue

        direction = "long" if delta > 0 else "short"
        qty = abs(int(delta))

        account.orderbook.add_order(
            identity=f"rebalance_{sym}",
            commodity=commodity,
            contract=contract,
            order_type="market on opening order",
            direction=direction,
            folder=self.name,
            order_time=time_index,
            quantity=qty,
            price=0,
            remark=f"target={target_contracts}, current={current}, w={weight:.4f}",
        )


# IMPORTANT: backtestlib.backtest.single_interval_backtest calls:
# getattr(folder, folder.name)(time_index)
# so we must attach method with the same name as folder.name
setattr(ff.Folder, "CTA_MultiFactor", CTA_MultiFactor)