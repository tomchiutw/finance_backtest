# finance_backtest
Tools for finance backtesting. Using data from investing.com or yfinance.

## Installation

```bash
pip install -r requirements.txt
# or install as a package
pip install -e .
```

## Quick Start

```python
from datetime import datetime
import backtestlib.account as ba
import backtestlib.commodity as bc
import folderlib.F0001 as f

accounts = ba.AccountManager()
account = accounts.accounts['1st_account']

commodity_future = bc.create_commodity(bc.CommodityList.VIX_FUTURE)
commodity_spot   = bc.create_commodity(bc.CommodityList.VIX_INDEX)

changable_var_dict = {
    'account': account,
    'backtest_start_date': datetime(2020, 1, 1),
    'backtest_end_date':   datetime(2024, 1, 1),
    'commodity_future': commodity_future,
    'commodity_spot':   commodity_spot,
    'interval': '1d',
    'contract': 'c1',
    'short_entry_percentage': 0.05,
    'short_close_percentage': 0.05,
    'short_close_percentage_2': 0.03,
    'spread': 0.0,
    'long_entry_percentage': 0.05,
    'long_close_percentage': 0.0,
    'long_stop_percentage': 0.05,
    'settlement': 1,
    'leverage': 0.3,
    'liability_percentage': 0.0,
}

result = f.folder_main(changable_var_dict)
```

## Configuration

Strategy parameters and commodity definitions can be loaded from YAML files in the
`config/` directory:

```python
from backtestlib.config_loader import load_strategy_config, load_commodities_config

strategy_cfg    = load_strategy_config()    # config/strategy_config.yaml
commodities_cfg = load_commodities_config() # config/commodities_config.yaml

params = strategy_cfg['F0001']
```

## Testing

```bash
pytest tests/
```

## Project Structure

```
finance_backtest/
├── backtestlib/          # Core backtesting library
│   ├── account.py        # Account and AccountManager
│   ├── commodity.py      # Commodity definitions
│   ├── config_loader.py  # YAML configuration loader
│   ├── data_validator.py # Market data quality checks
│   ├── exceptions.py     # Custom exception classes
│   ├── marketdata.py     # Market data download / storage (xlsx + parquet)
│   ├── order.py          # Order and OrderBook
│   ├── report.py         # Backtest performance reporting
│   └── risk_manager.py   # Risk management system
├── config/               # YAML configuration files
│   ├── strategy_config.yaml
│   └── commodities_config.yaml
├── folderlib/            # Strategy implementations
│   └── F0001.py          # VIX futures mean-reversion strategy
├── folder_sample/        # Example backtest scripts
├── tests/                # pytest unit tests
├── requirements.txt      # Python dependencies
└── setup.py              # Package installation script
```

## Risk Management

```python
from backtestlib.risk_manager import RiskManager

rm = RiskManager(max_drawdown=0.2, max_position_size=0.5, max_leverage=2.0)
rm.check_risk_limits(account)
size = rm.calculate_position_size(account, volatility=500.0)
```

## Backtest Reporting

```python
from backtestlib.report import BacktestReport

report = BacktestReport(equity_series)
metrics = report.calculate_metrics()
report.generate_html_report('reports/backtest.html')
report.plot_equity_curve()
```

## Preview

- **Account Performance Tracking**:  
  Visualize account balance, cash, and asset positions over time using a structured DataFrame. 
![image](https://github.com/user-attachments/assets/397743bb-8e6e-43db-a698-8acd0e452fa2)

- **Portfolio Balances**: 
![image](https://github.com/user-attachments/assets/5951c5b2-85ca-4d9a-b334-56e9d49519f0)

- **Historical Transactions**:  
  Maintain a comprehensive record of trades, including entry and exit times, position sizes, open and close prices, realized P&L, and fees. 
![image](https://github.com/user-attachments/assets/ba52c6ee-bebd-4a89-8622-d8ed0093f482)

- **Position Inventory Management**:  
  Track open positions in real-time during backtesting, including position size, direction, entry price, fees, and unrealized P&L.
![image](https://github.com/user-attachments/assets/bfd84485-13f3-4af6-9814-30b10a99cfea)

- **Order Book Management**:  
  Track executed and pending orders in backtesting, including order type (limit, market,stop,market on opening order,market on closing order), direction, execution price, fees, timestamps, and status.
![image](https://github.com/user-attachments/assets/1a5caca0-aa89-4377-ac6c-ce329b067a33)

- **Performance Evaluation Metrics**:  
  Analyze strategy performance using key financial indicators such as total return, CAGR, maximum drawdown, Calmar ratio, and rolling period returns (e.g., three-month, six-month, YTD, one-year).
![image](https://github.com/user-attachments/assets/f09ca8a5-a624-446a-a37c-f97d706d21b9)

## Optimizer
To use optimizer of parameters, in this example, we test for two parameters (short_entry_percentage, short_close_percentage) combination with highest return.

```python
import backtestlib.optimizer as bop
# ----------------------------
if is_optimizer:
    # optimizer
    # input next year params from optimizer
    params = {
        'short_entry_percentage': [0.03,0.05,0.07],
        'short_close_percentage': [0.03,0.05,0.07],
    }
    method='MAX_RETURN'
    optimizer=bop.Optimizer(params, method, changable_var_dict,f.folder_main)
    optimize_results[year]=optimizer.optimize(show_balance=False,show_details=False,show_pnl=False)
    changable_var_dict['account'].reset()
    # optimizer end
# ---------------------
```


## License

[MIT](https://choosealicense.com/licenses/mit/)
