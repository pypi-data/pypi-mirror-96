# Areix IO (Alpha Test)

[Documentation](http://alphagen.areix-ai.com/doc)

## Installation
Create a virtual environment 
```
virtualenv venv --python=python3
```
Activate the virtual environment 
```python
# Macbook / Linus
source venv/bin/activate 

# Windows
venv/Scripts/activate
```
Deactivate
```
deactivate
```
Install Areix-IO package
```
pip install Areix-IO
```


## Usage
Define your strategy class:
```python
import areix_io as aio
from areix_io.utils import create_report_folder, SideType

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import pandas as pd
import numpy as np

PRED_DAYS = 2 
PCT_CHANGE = 0.004
'''
Data pre processing step
'''
def bollinger_band(data, n_lookback, n_std):
    hlc3 = (data['high'] + data['low'] + data['close']) / 3
    mean, std = hlc3.rolling(n_lookback).mean(), hlc3.rolling(n_lookback).std()
    upper = mean + n_std*std
    lower = mean - n_std*std
    return upper, lower

def update_df(df):
    upper, lower = bollinger_band(df, 20, 2)

    df['ma10'] = df.close.rolling(10).mean()
    df['ma20'] = df.close.rolling(20).mean()
    df['ma50'] = df.close.rolling(50).mean()
    df['ma100'] = df.close.rolling(100).mean()

    df['x_ma10'] = (df.close - df.ma10) / df.close
    df['x_ma20'] = (df.close - df.ma20) / df.close
    df['x_ma50'] = (df.close - df.ma50) / df.close
    df['x_ma100'] = (df.close - df.ma100) / df.close

    df['x_delta_10'] = (df.ma10 - df.ma20) / df.close
    df['x_delta_20'] = (df.ma20 - df.ma50) / df.close
    df['x_delta_50'] = (df.ma50 - df.ma100) / df.close

    df['x_mom'] = df.close.pct_change(periods=2)
    df['x_bb_upper'] = (upper - df.close) / df.close
    df['x_bb_lower'] = (lower - df.close) / df.close
    df['x_bb_width'] = (upper - lower) / df.close
    return df

def get_X(data):
    return data.filter(like='x').values

def get_y(data):
    # use price change in the future 2 days as training label
    y = data.close.pct_change(PRED_DAYS).shift(-PRED_DAYS)  
    y[y.between(-PCT_CHANGE, PCT_CHANGE)] = 0             
    y[y > 0] = 1
    y[y < 0] = -1
    return y


def get_clean_Xy(df):
    X = get_X(df)
    y = get_y(df).values
    isnan = np.isnan(y)
    X = X[~isnan]
    y = y[~isnan]
    return X, y

class MLStrategy(aio.Strategy):
    num_pre_train = 300

    def initialize(self):
        '''
        Model training step
        '''

        self.info('initialize')
        self.code = 'XRP/USDT'
        df = self.ctx.feed[self.code]
        self.ctx.feed[self.code] = update_df(df)

        self.y = get_y(df[self.num_pre_train-1:])
        self.y_true = self.y.values

        self.clf = KNeighborsClassifier(7)
        
        tmp = df.dropna().astype(float)
        X, y = get_clean_Xy(tmp[:self.num_pre_train])
        self.clf.fit(X, y)

        self.y_pred = []
    
    def before_trade(self, order):
        return True

    def on_order_ok(self, order):
        self.info(f"{order['side'].name} order {order['id']} ({order['order_type'].name}) executed #{order['quantity']} {order['code']} @ ${order['price']:2f}; Commission: ${order['commission']}; Available Cash: ${self.ctx.available_cash}; Position: #{self.ctx.get_quantity(order['code'])}; Gross P&L : ${order['pnl']}; Net P&L : ${order['pnl_net']}")


        if not order['is_open']:
            self.info(f"Trade closed, pnl: {order['pnl']}========")


    def on_market_start(self):
        # self.info('on_market_start')
        pass

    def on_market_close(self):
        # self.info('on_market_close')
        pass

    def on_order_timeout(self, order):
        self.info(f'on_order_timeout. Order: {order}')
        pass

    def finish(self):
        self.info('finish')

    def on_bar(self, tick):
        '''
        Model scoring and decisioning step
        '''
        bar_data = self.ctx.bar_data[self.code]
        hist_data = self.ctx.hist_data[self.code]

        if len(hist_data) < self.num_pre_train:
            return 
        
        open, high, low, close = bar_data.open, bar_data.high, bar_data.low, bar_data.close
        X = get_X(bar_data)
        forecast = self.clf.predict([X])[0]
        self.y_pred.append(forecast)

        self.ctx.cplot(forecast,'Forcast')
        self.ctx.cplot(self.y[tick],'Groundtruth')
        # self.info(f"focasing result: {forecast}")

        upper, lower = close * (1 + np.r_[1, -1]*PCT_CHANGE)

        if forecast == 1 and not self.ctx.get_position(self.code):
            o1 = self.order_amount(code=self.code,amount=200000,side=SideType.BUY, asset_type='Crypto')
            self.info(f"BUY order {o1['id']} created #{o1['quantity']} @ {close:2f}")
            osl = self.sell(code=self.code,quantity=o1['quantity'], price=lower, stop_price=lower, asset_type='Crypto')
            self.info(f"STOPLOSS order {osl['id']} created #{osl['quantity']} @ {lower:2f}")
            
        elif forecast == -1 and self.ctx.get_position(self.code):
            o2 = self.order_amount(code=self.code,amount=200000,side=SideType.SELL, price=upper, asset_type='Crypto',ioc=True)
            self.info(f"SELL order {o2['id']} created #{o2['quantity']} @ {close:2f}")

```

Run your strategy:
```python
if __name__ == '__main__':
    aio.set_token('xxxxxx') # Only need to run once

    base = create_report_folder()

    start_date = '2020-12-01'
    end_date = '2021-03-01'

    sdf = aio.CryptoDataFeed(
        symbols=['XRP'], 
        start_date=start_date, 
        end_date=end_date,  
        interval='4h', 
        order_ascending=True, 
        store_path=base
    )
    feed, idx = sdf.fetch_data()

    mytest = aio.BackTest(
        feed, 
        MLStrategy, 
        commission_rate=0.001, 
        min_commission=0, 
        trade_at='close', 
        benchmark=None, 
        cash=200000, 
        tradedays=idx, 
        store_path=base
    )

    mytest.start()
```

Retrieve statistic results:
```python
    prefix = ''
    stats = mytest.ctx.statistic.stats(pprint=True, annualization=252, risk_free=0.0442)
    '''
    Model evaluation step
    '''
    stats['model_name'] = 'Simple KNN Signal Generation Strategy'
    stats['algorithm'] = ['KNN', 'Simple Moving Average', 'Bollinger Band']
    stats['model_measures'] = ['f1-score','accuracy']
    ytrue = mytest.ctx.strategy.y_true[:-PRED_DAYS]
    ypred = mytest.ctx.strategy.y_pred[:-PRED_DAYS]
    # print(len(ytrue),len(ypred), ytrue, ypred)
    stats['f1-score'] = f1_score(ytrue, ypred,average='weighted')
    stats['accuracy'] = accuracy_score(ytrue, ypred)
    print(stats)

    mytest.contest_output()
```
Result:
```
start                                                2020-12-01 00:00:00+08:00
end                                                  2021-03-01 00:00:00+08:00
duration                                                      90 days 00:00:00
beginning_balance                                                       200000
ending_balance                                                   366164.673839
total_net_profit                                                 166164.673839
gross_profit                                                     253652.290254
gross_loss                                                       -87487.616415
profit_factor                                                         2.899294
return_on_initial_capital                                             0.830823
annualized_return                                                     0.325384
total_return                                                          0.830823
max_return                                                            0.845580
min_return                                                            0.000000
number_trades                                                              172
number_winning_trades                                                       46
number_losing_trades                                                        41
avg_daily_trades                                                      6.142857
avg_weekly_trades                                                    28.666667
avg_monthly_trades                                                   57.333333
win_ratio                                                             0.267442
loss_ratio                                                            0.238372
win_days                                                                    25
loss_days                                                                    9
max_win_in_day                                                    22655.999775
max_loss_in_day                                                   -2397.489768
max_consecutive_win_days                                                    55
max_consecutive_loss_days                                                    3
avg_profit_per_trade                                               2257.392982
trading_period                                         0 years 3 months 0 days
avg_daily_pnl($)                                                    307.712359
avg_daily_pnl                                                         0.001146
avg_weekly_pnl($)                                                 12781.897988
avg_weekly_pnl                                                        0.050109
avg_monthly_pnl($)                                                55388.224613
avg_monthly_pnl                                                       0.241292
avg_quarterly_pnl($)                                             166164.673839
avg_quarterly_pnl                                                     0.830823
avg_annualy_pnl($)                                               166164.673839
avg_annualy_pnl                                                       0.830823
sharpe_ratio                                                          2.151660
sortino_ratio                                                         7.659043
annualized_volatility                                                 0.113746
information_ratio                                                          N/A
omega_ratio                                                           0.000996
downside_risk                                                         0.037696
beta                                                                       N/A
alpha                                                                      N/A
calmar_ratio                                                         10.462350
tail_ratio                                                            3.454495
stability_of_timeseries                                               0.750519
max_drawdown                                                          0.031100
max_drawdown_period          (2021-02-13 00:00:00+08:00, 2021-02-13 16:00:0...
max_drawdown_duration                                          0 days 16:00:00
sqn                                                                   4.308112
model_name                               Simple KNN Signal Generation Strategy
algorithm                         [KNN, Simple Moving Average, Bollinger Band]
model_measures                                            [f1-score, accuracy]
f1-score                                                              0.485086
accuracy                                                              0.504167
```