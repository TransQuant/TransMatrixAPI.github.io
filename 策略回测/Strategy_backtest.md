# 四、策略回测
## 4.1 架构
- 策略回测主要包含3大组件：回测引擎组件SimulationMatrix，策略组件BaseStrategy，行情组件BaseMarket

- SimulationMatrix 用于指定回测参数，如回测时间段，样本空间，订阅并加载的数据，触发策略回调等等

- BaseStrategy 是回测策略的基类，策略的具体逻辑，需要**用户自己继承该类并实现**

- BaseMarket 是行情组件，用于管理所有BaseStrategy订阅的行情数据

  <div align=center>
  <img width="1000" src="pngs/backtest_arch.png"/>
  </div>
  <div align=center style="font-size:12px">策略回测架构</div>
  <br />

## 4.2 回测引擎
### 4.2.1 SimulationMatrix
- 策略回测引擎组件
  - 属性：
  >名称|类型|说明
  >----|----|----
  config|Dict|引擎相关配置字典
  codes|List|股票样本空间列表
  start|datetime|起始时间
  end|datetime|结束时间
  ini_cash|int|账户初始资金
  factor_sub|Dict|config中data键所挂载的数据
  fin_factor_sub|Dict|config中findata键所挂载的数据
  data_engine|DataEngine|数据查询引擎
  pta_backend|String|当前客户端类型，包括'ipython'和'tqclient'两类
  logging|bool|是否起用日志，默认为False
  cache_data_to_pkl|bool|是否将数据缓存到本地，默认为True
  strategies|Dict|挂载的策略所组成的字典集合
  market_category|String|当前市场类别，包括 'stock'和 'commodity'，默认为 'stock'
  code_filter|tuple|股票代码过滤器，一个由库名、表名、条件所组成的元组

- init 组件初始化（数据加载，配置策略组件，行情组件等等）
  - 参数：
    无
  - 返回：
    无

- run 运行回测，并对挂载的策略账户作结算
  - 参数：
    无
  - 返回：
    无

- analyze 回测完成后，进行回测结果分析
  - 参数：
    无
  - 返回：
    无

- save_analysis 保存回测结果
  - 参数：
    无
  - 返回：
    无

### 4.2.2 配置说明
- SimulationMatrix 配置项说明如下：
  ```text
  matrix:
      # 回测模式 ：模拟市场 / 信号交易
      mode: simulation

      # 账户参数 
      ini_cash: 1000000
      ini_position: null
      fee: 0
      market_type: stock_cn

      # 回测区间 ：[开始时间， 结束时间]
      span:
          - 2021-01-01 
          - 2021-12-31

      # 股票样本空间
      universe: &universe custom_universe.pkl
      
      # 因子订阅 ： [因子名 ：[因子表名，股票代码列表，字段集合，初始化窗口（天）]]
      data:
          macd:
              - meta_data
              - factor_data__stock_cn__tech__1day__macd
              - *universe
              - value
              - 10
  ```

### 4.2.3 配置方式
### yaml文件配置
- 将相关配置写进yaml文件，调用相关方法加载配置：
  - Python调用 : transmatrix.matrix.run_matrix('config.yaml')

### 代码配置
- 在Python代码中构造config字典
  ```python
  In:
    CODES = get_universe('custom_universe.pkl')
    config = {   
            # 回测模式 ：模拟市场 / 信号交易
            'mode' : 'simulation', # signal

            # 回测区间 ：[开始时间， 结束时间]
            'span': ['2021-01-01','2021-12-31'],

            # 因子订阅 ： [因子名 ：[因子表名，股票代码列表，字段集合，初始化窗口（天）]]
            'data' : {
                'macd' : ['*','factor_data__stock_cn__tech__1day__macd', CODES, 'value', 10]
            },

            # 账户参数 
            'ini_cash' : 1000000,
            # 'market_type': 'stock_cn'
            # 'ini_positon' : {}
            # 'fee' : 0

            # 'cache_data': False
        }

    # 实例化回测控制器对象
    matrix = SimulationMatrix(config)
    matrix
  ```
  ```text
  Out:
    <transmatrix.matrix.simulation.base.SimulationMatrix at 0x7fbc285ed370>
  ```

## 4.3 策略组件
### 4.3.1 BaseStrategy
- 策略回测组件的基类
  - 说明：
    - 该组件在研究引擎SimulationMatrix的init方法中初始化，主要包括收集订阅数据配置，初始化账户，以及运行用户自定义的初始化逻辑
    - 策略回测的具体逻辑，需要用户继承BaseStrategy，注册回调任务，并实现回调任务逻辑，行情更新回调逻辑
    - 系统提供了若干因子计算样例，参见4.5节
  
  - 属性：
  >名称|类型|说明
  >----|----|----
  name|String|组件名称
  config|Dict|组件的配置字典
  matrix|SimulationMatrix|策略回测引擎
  subscribe_info|Dict|订阅的行情数据配置
  codes|List|当前配置的股票空间，由股票代码组成的列表
  insert_delay|timedelta|订单下达延迟
  receive_delay|timedelta|订单接收延迟
  cancel_delay|timedelta|订单取消延迟
  markets|Dict|当前策略订阅的行情组件
  account_type|String|账户类型，包括 'base', 'pv', 'future'和 'account'，默认是 ' base'
  account|BaseAccount|当前的账户组件
  time|datetime|当前策略所在时间

- init_account 根据策略配置，初始化账户组件
  - 参数：
  无
  - 返回：
  无

- pending_orders 查询当前账户的挂单
  - 参数：
  无
  - 返回：
    - 形为{order_id: order}的字典集合，order为订单对象

- trade_history 当前成交历史
  - 参数：
  无
  - 返回：
    - 形为{code: List}的字典集合，code为股票代码，List是由成交记录元组信息所组成的列表

- position 当前账户持仓
  - 参数：
  无
  - 返回：
    - PositionPV对象

- get_netpos 当前账户持仓
  - 参数：
  >名称|类型|说明
  >----|----|----
  code|String|股票代码
  - 返回：
    - 指定股票的当前净持仓

- on_init 策略初始化时将调用本方法，用户自定义实现。例如
  - 参数：
  无
  - 返回：
  无

- add_factor 注册数据到策略属性
  - 参数：
  >名称|类型|说明
  >----|----|----
  name|String|指定的属性名
  factor|object|数据
  - 返回：
  无

- add_scheduler 注册回调任务到策略
  - 参数：
  >名称|类型|说明
  >----|----|----
  scheduler|BaseSchedular|任务调度器
  dofuc|method|具体的回调方法
  - 返回：
  无

- on_init 策略初始化时将调用本方法，用户自定义实现
  - 参数：
  无
  - 返回：
  无

- on_market_data_update 行情数据更新时将调用本方法，用户自定义实现
  - 参数：
  >名称|类型|说明
  >----|----|----
  data|Array3dPanel|行情数据
  - 返回：
  无

- on_trade 订单成交时将调用本方法，用户自定义实现
  - 参数：
  >名称|类型|说明
  >----|----|----
  trade|MatchResult|成交记录
  - 返回：
  无

- on_receive 账户对象接收到订单时将调用本方法，用户自定义实现
  - 参数：
  >名称|类型|说明
  >----|----|----
  order|Order|订单对象
  - 返回：
  无

- on_order_reject 订单被拒绝时将调用本方法，用户自定义实现
  - 参数：
  >名称|类型|说明
  >----|----|----
  order|Order|订单对象
  - 返回：
  无

- send_order 策略下单
  - 参数：
  >名称|类型|说明
  >----|----|----
  order|Order|订单对象
  - 返回：
  无

- buy 策略买入
  - 参数：
  >名称|类型|说明
  >----|----|----
  price|float|买入价格
  volume|float|买入数量
  offset|String|操作类型，包括 'open' (开仓)和'close' (平仓)
  code|String|代码
  market|String|行情组件名称
  - 返回：
  无

- sell 策略卖出
  - 参数：
  >名称|类型|说明
  >----|----|----
  price|float|卖出价格
  volume|float|卖出数量
  offset|String|操作类型，包括 'open' (开仓)和'close' (平仓)
  code|String|代码
  market|String|行情组件名称
  - 返回：
  无

- create_order 生成订单对象
  - 参数：
  >名称|类型|说明
  >----|----|----
  price|float|下单价格
  volume|float|下单数量
  direction|ORDER_DIRECTION枚举|下单方向，包括ORDER_OFFSET.BUY和ORDER_OFFSET.CLOSE两个方向
  offset|String|操作类型，包括 'open' (开仓)和'close' (平仓)
  code|String|代码
  market|String|行情组件名称
  strategy|BaseStrategy|策略组件
  - 返回：
    - 生成的Order对象

### 4.3.2 相关API

#### BaseAccount
- 基础账户类
  - 说明：实现了基础的账户功能
  - 属性：
  >名称|类型|说明
  >----|----|----
  strategy|BaseStrategy|当前账户所对应的策略组件
  matrix|SimulationMatrix|当前账户所对应的回测引擎
  name|String|组件名称，默认与策略同名
  order_id|int|当前订单id
  codes|List|当前配置的股票空间，等于策略的codes属性
  pending_orders|Dict|账户当前挂单，key为订单id，value为Order对象
  position|Dict|当前持仓，key为代码，value为PositionPV对象

- get_netpos 当前账户持仓
  - 参数：
  >名称|类型|说明
  >----|----|----
  code|String|股票代码
  - 返回：
    - 指定股票的当前净持仓

- send_order 账户下单
  - 参数：
  >名称|类型|说明
  >----|----|----
  order|Order|订单对象
  - 返回：
  无

- cancel_order 取消下单
  - 参数：
  >名称|类型|说明
  >----|----|----
  order|Order|订单对象
  - 返回：
  无

- on_order_receive 通知策略组件订单已接收
  - 参数：
  >名称|类型|说明
  >----|----|----
  order|Order|订单对象
  - 返回：
  无

- on_trade 通知策略组件订单已成交
  - 参数：
  >名称|类型|说明
  >----|----|----
  trade|MatchResult|成交记录
  - 返回：
  无

- settle 抽象方法，每日收盘结算(通过matrix的 eod scheduler 触发）
  - 参数：
  无
  - 返回：
  无

- final_settle 抽象方法，回测完毕后一次性结算(由matrix.run控制)
  - 参数：
  无
  - 返回：
  无

- on_match_result 抽象方法，订单成交时将调用本方法
  - 参数：
  >名称|类型|说明
  >----|----|----
  trade|MatchResult|成交记录
  - 返回：
  无

#### PVaccount
- 继承自BaseAccount，实现了具体的结算功能和订单成交响应功能

#### BaseOrder
- 基础订单类，对应对象用于记录委托订单的信息
  - 属性：
  >名称|类型|说明
  >----|----|----
  price|float|下单价格
  volume|float|下单数量
  direction|枚举|下单方向，包括 'buy'和 'sell'两个方向
  offset|String|操作类型，包括 'open' (开仓)和'close' (平仓)
  code|String|代码
  market|String|行情组件名称
  strategy|BaseStrategy|策略组件
  insert_delay|timedelta|订单下达延迟
  receive_delay|timedelta|订单接收延迟
  cancel_delay|timedelta|订单取消延迟
  insert_time|datetime|下单时间
  cancel_time|datetime|订单取消时间
  level|int|订单优先级
  seq_num|float|
  front_volume|int|

- update_state 更新日志信息
  - 参数：
  >名称|类型|说明
  >----|----|----
  time|datetime|指定时间
  - 返回：
  无

#### Order
- 继承自BaseOrder类，通用订单类

#### PositionPV
- 持仓类，刻画了指定股票的持仓
  - 属性：
  >名称|类型|说明
  >----|----|----
  code|string|股票代码
  hold|float|持仓数量
  settle|float|结算价格
  pnl|float|当前盈亏
  netpos|float|当前净持仓

- on_trade 订单成交时，调用本方法更新持仓
  - 参数：
  >名称|类型|说明
  >----|----|----
  p|float|成交价格
  v|float|成交数量
  - 返回：
  无

- on_settle 账户结算时，调用本方法结算当前股票
  - 参数：
  >名称|类型|说明
  >----|----|----
  price|float|结算价格
  - 返回：
  无

#### MatchResult
- 一条成交记录
  - 属性：
  >名称|类型|说明
  >----|----|----
  order|BaseOrder|成交记录对应的订单对象
  price|float|成交价格
  volume|float|成交数量
  time|datetime|成交时间
  trade_info|tuple|成交信息元组

### 4.3.3 配置说明
```text
  strategy:

      strategy0: # 策略名称
          class:
              - strategy.py 
              - Strategy
          
          # 订阅行情（用于on_market_data_update回调）
          market: 
              # 行情库名，行情表名，代码列表
              - ['default',stock_bar_daily, *universe]

          # 自定义做和引擎 ：引擎编写可开放给用户(基于transmatrix.Basematcher interface)
          # match_mod: DayMatcher

          # 设置 发单 / 撤单延迟 （模拟 交易系统 --> 交易所 延迟)
          # insert_deley: 0ms
          # cancel_deley : 0ms
          # 设置 回报延迟 （模拟 交易所 --> 交易系统 延迟)
          # receive_delay: 0ms,

          # 账户配置信息
          account:
              type: base
              settle_freq: 'daily'
              settle_price:
                  - default
                  - stock_bar_daily
                  - close

          
          # args: []
          # kwargs {}

      # strategy1:
          # ...

      # strategy2:
          # ...
```

### 4.3.4 配置方式
#### yaml文件配置
- 将相关配置写进yaml文件，调用相关方法加载配置，参见4.2.3
#### 代码配置
- 在Python代码中构造config字典，构造策略组件，参见4.5.1

## 4.4 行情组件
### 4.4.1 BaseMarket
- 行情组件的基类
  - 说明：
    - 该组件在研究引擎SimulationMatrix的init方法中初始化，主要包括收集所有行情数据配置，加载数据
  
  - 属性：
  >名称|类型|说明
  >----|----|----
  name|String|组件名称
  strategies|Dict|用到本行情组件的策略组件集合
  matrix|SimulationMatrix|策略回测引擎
  codes|List|当前行情组件对应的股票代码列表
  matcher|BaseMatcher|订单撮合对象
  pending_orders|Dict|挂单字典集合，key为订单id，值为Order对象

- match_all_pending_orders

- on_match_info_update

- update_matcher_context

- on_data_update

- on_order_insert

- on_order_cancel

- match_order


### 4.4.2 相关API
#### BaseMatcher
- 基础订单撮合类
  - 说明：
    - TODO

  - 属性：
  >名称|类型|说明
  >----|----|----

- update_context

- match

- match_submitting

- match_pending

- match_cancelling

- match_partial_traded

#### TickMatcher
- 基础tick撮合逻辑，
  - 说明：
    - 一般用于对taking策略回测(见价成交 / cross match)，这种逻辑下fill-rate和撤单成功率都被压到最低,属于比较保守的撮合模式

  - 属性：
  >名称|类型|说明
  >----|----|----

#### TickMatcherAllPend
- 不考虑实时成交的tick撮合
  - 说明：
    - 一般可用于making策略，相比于TickMatcher来说保守度低一点

  - 属性：
  >名称|类型|说明
  >----|----|----

#### BarMatcher
- Bar撮合
  - 说明：
    - TODO

  - 属性：
  >名称|类型|说明
  >----|----|----

#### DayMatcher
- 日Bar撮合
  - 说明：
    - TODO

  - 属性：
  >名称|类型|说明
  >----|----|----


#### OrderFlowMatherPV
- 订单薄撮合
  - 说明：
    - TODO

  - 属性：
  >名称|类型|说明
  >----|----|----

## 4.5 回测样例
### 4.5.1 Bar回测
- Strategy类继承自BaseStrategy，实现策略回测逻辑

```python
In:
  from transmatrix.matrix import SimulationMatrix
  import transmatrix.matrix.schema.scheduler as Scheduler 
  from transmatrix.trader import BaseStrategy
  from transmatrix.utils.tools import get_universe
  # 获取可交易的股票池
  CODES = get_universe('custom_universe.pkl')
  config = {   
          # 回测模式 ：模拟市场 / 信号交易
          'mode' : 'simulation', # signal

          # 回测区间 ：[开始时间， 结束时间]
          'span': ['2021-01-01','2021-12-31'],

          # 因子订阅 ： [因子名 ：[因子表名，股票代码列表，字段集合，初始化窗口（天）]]
          'data' : {
              'macd' : ['*','factor_data__stock_cn__tech__1day__macd', CODES, 'value', 10]
          },

          # 账户参数 
          'ini_cash' : 1000000,
          # 'market_type': 'stock_cn'
          # 'ini_positon' : {}
          # 'fee' : 0

          # 'cache_data': False
      }

  # 实例化回测控制器对象
  matrix = SimulationMatrix(config)
  matrix
```

```text
Out:
  <transmatrix.matrix.simulation.base.SimulationMatrix at 0x7f5c94620190>
```

```python
In:
  # 策略逻辑编写
  templete = BaseStrategy

  # 用户自定义回调 支持 定时、定频、条件触发等机制
  callback_per_50min = Scheduler.FixFreqScheduler(name ='fixTimeScheduler50min',freq = '50min', matrix = matrix) 
  callback_at_10and14 = Scheduler.FixTimeScheduler(name = 'fixfreq10_14',matrix = matrix, milestones= ['10:01:00','13:59:00'])

  class Strategy(templete):
      
      #注册定时定频任务
      def on_init(self):
          self.add_scheduler(callback_per_50min,  self.callback50min)
          self.add_scheduler(callback_at_10and14, self.callback10and14)
          self.max_pos = 300
          pass

      #回调执行逻辑：每50分钟
      def callback50min(self):
          #打印回测系统时间
          # print('callback50min', self.time)
          pass

      #回调执行逻辑：每天10点和14点
      def callback10and14(self):
          #打印回测系统时间
          # print('callback10and14', self.time)
          pass

      #回调执行逻辑： 行情更新时
      def on_market_data_update(self, market):
          data = market.data
          macd = self.macd.query(self.time, 3)['value'][self.codes].mean().sort_values()
          
          buy_codes = macd.iloc[:2].index
          for code in buy_codes:
              # 获取某只股票的仓位
              pos = self.account.get_netpos(code)

              if  pos < self.max_pos:
                  price = data.get('close', code)
                  self.buy(price, 100, 'open', code, market.name)

  strategy_cfg = {   
          # 策略名称
          'name': 'strategy0',

          # 订阅行情（用于on_market_data_update回调）
          'market':[
              # 行情库名，行情表名，代码列表
              ['meta_data','market_data__stock_cn__bar__1day',CODES]
          ],

          'kwargs' : {
              'max_pos': 300
          },

          # 自定义做和引擎 ：引擎编写可开放给用户(基于transmatrix.Basematcher interface)
          # 'match_mod': 'DayMatcher' 

          # 设置 发单 / 撤单延迟 （模拟 交易系统 --> 交易所 延迟)
          # 'insert_deley' : '0ms',
          # 'cancel_deley' : '0ms',
          # 设置 回报延迟 （模拟 交易所 --> 交易系统 延迟)
          # 'receive_delay': '0ms',
      }

  # 实例化策略对象，传入matrix以实现策略注册
  strategy = Strategy(strategy_cfg, matrix)
```

```python
In:
  # 运行回测
  matrix.init()
  matrix.run()
```

```text
Out:
  loading data market_data__stock_cn__bar__1day from datacache.
  loading data factor_data__stock_cn__tech__1day__macd from datacache.


  inserting match-info timestep events...
  inserting market timestep events...
  inserting scheduler timestep events...
```

```python
In:
  matrix.analyze() # 回测结果分析
  strategy.post_trade_analysis.trade_table # 显示成交记录
```

  <div align=center>
  <img width="1000" src="pngs/backtest_trade_table.png"/>
  </div>
  <div align=center style="font-size:12px">成交记录</div>
  <br />

```python
In:
  strategy.post_trade_analysis.daily_position # 展示每日持仓
```

  <div align=center>
  <img width="1000" src="pngs/backtest_daily_pos.png"/>
  </div>
  <div align=center style="font-size:12px">持仓记录</div>
  <br />

```python
In:
  strategy.post_trade_analysis.daily_netvalue # 展示每日净值
```

  <div align=center>
  <img width="1000" src="pngs/backtest_daily_net.png"/>
  </div>
  <div align=center style="font-size:12px">每日净值</div>
  <br />

### 4.5.2 Tick回测
- Tick回测样例

```python
In:
  from IPython.core.interactiveshell import InteractiveShell
  InteractiveShell.ast_node_interactivity = "all"

  import numpy as np
  from transmatrix.matrix import SimulationMatrix
  from transmatrix.trader import BaseStrategy

  # 初始化回测管理组件 matrix
  mat_config = {'span': ['20210103','20210130'],}
  mat = SimulationMatrix(mat_config)

  #配置策略信息
  stra_config = {
                  'name': 'tick_strategy_1',  # 策略名
                  'market':[['common','stock_tick','000001.SZ']],
                  'account_type': 'pv',
                  
                  'account':{
                      'type': 'base',
                      'settle_freq': 'daily',
                      'settle_price' : ['default','stock_bar_daily','close']
                  }
                }

  # 策略编写 
  class TestStrategy(BaseStrategy):

      # 为进行压力测试，我们让策略在多个市场随机 报/撤 单
      def on_market_data_update(self, market):
          buy = np.random.randn() > 1.96
          sell = np.random.randn() > 1.96
          cancel = np.random.randn() > 1.96
          if cancel:[self.cancel_order(order) for order in self.account.pending_orders.values()]
          if buy: 
              ap1 = market.data.get('ask_price_1','000001.SZ')
              if ap1: self.buy(ap1,100,'open','000001.SZ','stock_tick')
          if sell:
              bp1 = market.data.get('bid_price_1','000001.SZ')
              if bp1: self.sell(bp1,100,'open','000001.SZ','stock_tick')
```

```python
In:
  # 运行回测
  strategy1 = TestStrategy(stra_config, mat) 
  mat.init()
  %time mat.run()
```

```text
Out:
  loading data stock_bar_daily from datacache.

  loading data stock_tick from datacache.

  inserting match-info timestep events...
  inserting market timestep events...
  inserting scheduler timestep events...
  CPU times: user 2.17 s, sys: 9.98 ms, total: 2.18 s
  Wall time: 2.19 s
```
  <div align=center>
  <img width="1000" src="pngs/tick_backtest.png"/>
  </div>
  <div align=center style="font-size:12px">回测日志展示</div>
  <br />
