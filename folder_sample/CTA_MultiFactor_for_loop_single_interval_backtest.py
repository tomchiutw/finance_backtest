from datetime import datetime

import backtestlib.account as ba
import backtestlib.commodity as bc
import folderlib.CTA_MultiFactor as cta



accounts = ba.AccountManager()
account_name = "CTA_COMMODITIES_ACCOUNT"

if account_name not in accounts.accounts:
    accounts.create_new_account(name=account_name)
else:
    accounts.accounts[account_name].reset()

account = accounts.accounts[account_name]

interval = "1d"
contract = "c1"

# 建議先縮短區間測試是否能抓到資料
backtest_start_date = datetime(2010, 1, 1, 0, 0)
backtest_end_date = datetime(2025, 12, 31, 0, 0)

commodities = bc.CommodityList.get_commodities([
    "GOLD_FUTURE",              # GC=F (你原本就有，但我已改 margin=0 fee=0)
    "WTI_CRUDE_OIL_FUTURE",     # CL=F
    "NATURAL_GAS_FUTURE",       # NG=F
    "SILVER_FUTURE",            # SI=F
    "COPPER_FUTURE",            # HG=F
    "CORN_FUTURE",              # ZC=F
    "SOYBEAN_FUTURE",           # ZS=F
    "WHEAT_FUTURE",             # ZW=F
    "COFFEE_FUTURE",            # KC=F
    "SUGAR_FUTURE",             # SB=F
    "COTTON_FUTURE",            # CT=F
])

changable_var_dict = {
    "account": account,
    "interval": interval,
    "contract": contract,
    "backtest_start_date": backtest_start_date,
    "backtest_end_date": backtest_end_date,
    "commodities": commodities,
    "initial_cash": 10000000,
    "target_vol_annual": 0.15,
    "max_contracts_per_asset": 2,
}

result = cta.folder_main(changable_var_dict, show_balance=True, show_details=True, show_pnl=False)
perf = result["output"]["performance"]
# print(perf)



