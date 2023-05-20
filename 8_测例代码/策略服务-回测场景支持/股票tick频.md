### 测例说明
Transmatrix框架支持不同时间频率的策略回测，这里展示了一个股票tick级别回测策略。

### 基本研究流程
- <b> 编写strategy.py </b>
  - 实现策略逻辑

```python
import numpy as np
from transmatrix import Strategy

# 策略编写 
class TestStrategy(Strategy):
    def init(self):
        pass
    
    # 为进行压力测试，我们让策略在多个市场随机 报/撤 单
    def on_market_data_update(self, market):
        buy = np.random.randn() > 1.96
        sell = np.random.randn() > 1.96
        cancel = np.random.randn() > 1.96
        if cancel:[self.cancel_order(order) for order in self.account.pending_orders.values()]
        if buy: 
            ap1 = market.get('ask_price_1','000001.SZ')
            if ap1: self.buy(ap1,100,'open','000001.SZ','stock_tick')
        if sell:
            bp1 = market.get('bid_price_1','000001.SZ')
            if bp1: self.sell(bp1,100,'open','000001.SZ','stock_tick')
```
- <b> 运行入口 </b>
  - 初始化回测组件
  - 运行回测

```python
In:
    from IPython.core.interactiveshell import InteractiveShell
    InteractiveShell.ast_node_interactivity = "all"

    import numpy as np
    from transmatrix.matrix import SimulationMatrix
    from strategy import TestStrategy

    # 初始化回测管理组件 matrix
    mat_config = {   
        'span': ['2021-01-03','2021-01-30'],
        'codes': ['000001.SZ'],
        'ini_cash':10000000,
        'market': {
            'stock':{
                'data': ['common2','stock_snapshot'], # 行情数据源
                'matcher': 'tick', # 撮合模式类型为tick
                'account': 'base',  # 有详细的stats table
            },
        },
        }
    matrix = SimulationMatrix(mat_config)   
```
```python
In:
    # 运行回测
    strategy1 = TestStrategy() 
    matrix.add_component(strategy1)
    matrix.init()
    %time matrix.run()
```
```text
Out:
    loading data common2__stock_snapshot__* from datacache.

    loading data common2__stock_bar_1day__close from datacache.

    2021-01-04 09:55:33: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_30
    2021-01-04 13:11:21: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_130
    2021-01-04 13:36:51: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_156
    2021-01-05 09:48:18: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_258
    2021-01-05 10:14:54: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_280
    2021-01-05 10:58:12: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_327
    2021-01-05 13:32:03: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_395
    2021-01-05 14:12:00: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_439
    2021-01-05 14:16:48: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_442
    2021-01-06 09:52:57: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_506
    2021-01-06 09:55:48: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_512
    2021-01-06 10:45:30: 报单已全部成交或已撤单。orderid: strategy.TestStrategy()_stock_560
    （略）
```