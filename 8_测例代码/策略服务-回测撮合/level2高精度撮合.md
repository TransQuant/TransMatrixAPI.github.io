### 测例说明
TransMatrix框架的策略回测支持高频交易场景，在高频撮合成交判定方面能贴近市场实际情况。本测例采用股票3秒快照数据作为行情源，随机生成买卖信号发单，并展示交易撮合结果。
<div align=center>
<img width="1000" src="8_测例代码\pics\level2撮合.png"/>
</div>
<div align=center style="font-size:12px">level2撮合</div>
<br />

### 基本研究流程
- <b> 配置config.yaml文件 </b>
  - 配置Matrix组件回测信息
  - 配置策略组件信息

```text
# 配置Matrix组件回测信息
matrix:

    mode: simulation
    span:
        - 2022-05-05 10:00:00
        - 2022-05-05 10:15:00
    logging: True
    show_runtime: True
    ini_cash: 1000000
    codes: &universe 000651.SZ

    market:
        stock:
            data: [common, stock_level2_test] # 回测数据源
            matcher: order # 订单撮合模式
            latency: 100 # 延迟100ms
            
# 配置策略组件信息  
strategy:
    stress_test:
        class:
            - hft_stress_test.py
            - TestStrategy

```


- <b> 编写strategy.py </b>
  - 实现策略逻辑

```python
from transmatrix import Strategy
import numpy as np

CODE = '000651.SZ'
MKT  = 'stock_level2_test'

class TestStrategy(Strategy):
   
    def init(self):
        pass
    
    
    def on_market_data_update(self, market):

        for order in self.account.pending_orders.values():
            prob = np.random.randn()
            if prob > 1.96:
                self.cancel_order(order)

        ap1 = market.get('ask_price_1', codes = CODE) # 获取当前市场的卖一价
        bp1 = market.get('bid_price_1', codes = CODE) # 获取当前市场的买一价

        prob = np.random.randn()
        if prob > 2.5:
            self.buy(ap1,100,'open',CODE,MKT) # 以卖一价挂买单
        elif prob < -2.5:
            self.sell(bp1,100,'open',CODE,MKT) # 以买一价挂卖单
```

- <b> 运行入口 </b>
  - 运行策略

```python
In:
   from transmatrix.workflow import run_matrix
    mat = run_matrix('config.yaml') # latency = 100 
```
```text
Out:
    CPU times: user 2 µs, sys: 0 ns, total: 2 µs
    Wall time: 4.05 µs
    loading data common__stock_level2_test__* from database.

    loading data common2__stock_bar_1day__close from database.

    Cashing common__stock_level2_test__* to pickle file: dataset_1f7ae7dc-714a-4593-a16c-2e540832c2c0 ....Cashing common2__stock_bar_1day__close to pickle file: dataset_5943366c-3b04-492d-aa73-13637de16447 ....

    <transmatrix-1.0.0>/transmatrix/account/account.py:92: UserWarning: 账户 hft_stress_test.TestStrategy(10)_stock 缺少结算价数据, 将无法结算！
    2022-05-05 10:00:27.037852: 报单已全部成交或已撤单。orderid: hft_stress_test.TestStrategy(10)_stock_13
    2022-05-05 10:00:27.171148: 报单已全部成交或已撤单。orderid: hft_stress_test.TestStrategy(10)_stock_12
    2022-05-05 10:00:27.391144: 报单已全部成交或已撤单。orderid: hft_stress_test.TestStrategy(10)_stock_11
    2022-05-05 10:00:27.394715: 报单已全部成交或已撤单。orderid: hft_stress_test.TestStrategy(10)_stock_12
    2022-05-05 10:00:32.749615: 报单已全部成交或已撤单。orderid: hft_stress_test.TestStrategy(10)_stock_26
    2022-05-05 10:00:32.807757: 报单已全部成交或已撤单。orderid: hft_stress_test.TestStrategy(10)_stock_26
    2022-05-05 10:00:34.214094: 报单已全部成交或已撤单。orderid: hft_stress_test.TestStrategy(10)_stock_29
    2022-05-05 10:00:34.231684: 报单已全部成交或已撤单。orderid: hft_stress_test.TestStrategy(10)_stock_29
    2022-05-05 10:00:34.689533: 报单已全部成交或已撤单。orderid: hft_stress_test.TestStrategy(10)_stock_32
    （略）
```