# finance_backtest
Tools for finance backtesting.  Using data from investing.com or yfinance.

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
  Track executed and pending orders in backtesting, including order type (market, stop), direction, execution price, fees, timestamps, and status.
![image](https://github.com/user-attachments/assets/1a5caca0-aa89-4377-ac6c-ce329b067a33)

- **Performance Evaluation Metrics**:  
  Analyze strategy performance using key financial indicators such as total return, CAGR, maximum drawdown, Calmar ratio, and rolling period returns (e.g., three-month, six-month, YTD, one-year).
![image](https://github.com/user-attachments/assets/f09ca8a5-a624-446a-a37c-f97d706d21b9)

## Optimizer
To use optimizer of parameters, in this example, we test for two parameters (short_entry_percentage, short_close_percentage) combination with higher return.

```bash
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
