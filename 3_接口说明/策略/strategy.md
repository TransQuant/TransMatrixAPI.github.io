## 1.2 Strategy

### 1.2.1 BaseStrategy

BaseStrategy是SignalStrategy和SimulationStrategy的基类，为因子计算和回测计算提供基础。

#### 主要属性

| 名称                | 类型                       | 说明                                                         |
| ------------------- | -------------------------- | ------------------------------------------------------------ |
| matrix              | BaseMatrix                 | strategy所使用的matrix，用于指定回测参数，如回测时间段，样本空间等 |
| time                | datetime                   | 当前回测时间                                                 |
| codes               | List                       | 股票代码                                                     |
| massages            | Dict[str, str]             |                                                              |
| subscribe_data_info | Dict[str, List]            | 订阅的数据信息                                               |
| schedulers          | Dict[str, BaseScheduler]   | 任务调度器                                                   |
| sub_generators      | Dict[str, 其他strategy]    | 本strategy订阅的其他strategies（比如其他因子）               |
| name                | str                        | 策略的名称，唯一，不可重名                                   |
| key                 | str                        | 同name                                                       |
| buffers             | Dict[str, NdarrayDataView] |                                                              |

#### 主要方法

- **init**

  - 函数作用：用户在继承Strategy类的计算组件时，需要实现init方法来指定订阅的数据、订阅的strategy类、回测发生的时间等。用户自行实现（<u>必须</u>）。
  - 参数：无
  - 返回：无

  ```python
  In:
      def init(self):
          self.add_clock(milestones='09:35:00')
          self.subscribe_data(
              'pv', ['common','stock_bar_daily',self.codes,'open,high,low,close', 10]
          )
          self.pv: DataView3d
          self.subscribe(FactorA())
  ```


- **subscribe_data**  <a id="subscribe_data"></a> 

  - 函数作用：订阅数据。

  - 参数：

    >| 名称             | 类型 | 说明                   |
    >| ---------------- | ---- | ---------------------- |
    >| name             | str  | 数据集的名称           |
    >| dataset_describe | list | 包含了描述数据集的信息 |

  - 返回：无

  ```python
  In:
      self.subscribe_data(
                      'pv', ['common','stock_bar_daily',self.codes,'open,high,low,close', 10]
                  )
  ```

  

- **subscribe**

  - 函数作用：订阅其他strategy。若系统中已存在，则返回系统中的实例（保证唯一性）；若不存在，则将 other 加入系统。

  - 参数：

    >| 名称  | 类型                               | 说明                 |
    >| ----- | ---------------------------------- | -------------------- |
    >| other | SignalStrategy或SimulationStrategy | 要另一个strategy组件 |

  - 返回：strategy对象

  ```python
  In:
      self.subscribe(FactorA())
  ```

  

- **add_scheduler**

  - 函数作用：添加任务调度器。

  - 参数：

    >| 名称       | 类型                  | 说明                                   |
    >| ---------- | --------------------- | -------------------------------------- |
    >| scheduler  | BaseScheduler类型     | 要添加的任务调度器                     |
    >| milestones | list of datetime或str | 指定执行时间点                         |
    >| freq       | str                   | 时间间隔，用于指定执行时间间隔         |
    >| with_data  | str                   | 数据集名称，用于指定当数据集更新时执行 |
    >| handler    | func                  | 回调函数，用于指定调度器执行时的操作   |

    > 如果 `scheduler` 不为空，则直接添加该调度器；否则，milestones, freq和with_data三者选其一即可，分别对应调度器类型`FixTimeScheduler`、`FixFreqScheduler` 或 `DataClock`。

  - 返回：schedular对象

  ```python
  In:
      callback_per_50min = FixTimeScheduler(milestones= ['10:01:00','13:59:00'])
      callback_at_10and14 = FixFreqScheduler(freq = '50min') 
      self.add_scheduler(schedular=callback_per_50min, handler=self.callback50min)
      self.add_scheduler(schedular=callback_at_10and14, handler=self.callback10and14)
      # self.callback50min和self.callback10and14是自行定义的回调函数
  ```

  

- **add_buffer**

  - 函数作用：添加缓存数据。

  - 参数：

    >| 名称   | 类型            | 说明           |
    >| ------ | --------------- | -------------- |
    >| name   | str             | 表示缓存的名称 |
    >| buffer | NdarrayDataView | 表示缓存的数据 |

  - 返回：无

- **callback**

  - 函数作用：添加回调函数，用于在触发器触发时执行。

  - 参数：

    >| 名称    | 类型                               | 说明                                 |
    >| ------- | ---------------------------------- | ------------------------------------ |
    >| trigger | SignalStrategy或SimulationStrategy | 表示触发器的名称                     |
    >| handler | func                               | 回调函数，用于指定触发器触发时的操作 |

  - 返回：无

- **add_massage**

  - 函数作用：添加消息，将消息的名称和数据类型存储下来，并将消息添加到事件引擎中。

  - 参数：

    >| 名称  | 类型     | 说明               |
    >| ----- | -------- | ------------------ |
    >| name  | str      | 表示消息的名称     |
    >| dtype | 任意类型 | 表示消息的数据类型 |

  - 返回：无


### 1.2.2 SignalStrategy

继承自BaseStrategy，因子计算组件的基类。

#### 属性：

>| 名称       | 类型                       | 说明                               |
>| ---------- | -------------------------- | ---------------------------------- |
>| name       | String                     | 组件名称                           |
>| signal     | Dict                       | 信号因子字典，键为时间，值为信号值 |
>| clock      |                            | 回测时刻                           |
>| steps      |                            | 一系列回测发生时间                 |
>| evaluators | Dict[str, SignalEvaluator] | 因子评价组件                       |

#### 方法：

- set_signal

  - 函数作用：对signal属性赋值

  - 参数：

    >| 名称   | 类型   | 说明   |
    >| ------ | ------ | ------ |
    >| signal | object | 因子值 |

  - 返回：无

- add_evaluator

  - 函数作用：添加评价组件

  - 参数：

    >| 名称      | 类型            | 说明         |
    >| --------- | --------------- | ------------ |
    >| evaluator | SignalEvaluator | 评价组件实例 |

  - 返回：无

- create_factor_table

  - 函数作用：创建因子表

  - 参数：

    >| 名称         | 类型      | 说明         |
    >| ------------ | --------- | ------------ |
    >| factor_names | List或str | 评价组件实例 |

  - 返回：无

- matrix_create_factor_table

  - 函数作用：
  - 参数：无
  - 返回：无

- add_clock

  - 函数作用：添加回测触发时刻
  - 参数：

  >| 名称       | 类型             | 说明   |
  >| ---------- | ---------------- | ------ |
  >| scheduler  | BaseScheduler    | 信号值 |
  >| milestones | String, datetime |        |
  >| freq       | timedelta        |        |
  >| with_data  | String           |        |

  - 返回：无

- update_signal 

  - 函数作用：添加当前时间的信号值到signal
  - 参数：

  >| 名称  | 类型   | 说明   |
  >| ----- | ------ | ------ |
  >| value | object | 信号值 |

  - 返回：无

- update_factor 

  - 函数作用：更新当前时间的因子值到factor_data
  - 参数：

  >| 名称  | 类型                | 说明                   |
  >| ----- | ------------------- | ---------------------- |
  >| name  | String              | 因子名称               |
  >| value | array-like/Iterable | 因子值，长度为股票数量 |

  - 返回：无

- signal_to_dataframe

  - 函数作用：signal转DataFrame
  - 参数：无

  - 返回：无

- save_factors 

  - 函数作用：保存factor_data的数据到数据库
  - 参数：

  >| 名称       | 类型   | 说明                     |
  >| ---------- | ------ | ------------------------ |
  >| table_name | String | 数据库表名               |
  >| freq       | String | 数据频率，默认为 'daily' |

  - 返回：无

- save_signal 

  - 函数作用：保存保存一个因子到数据库
  - 参数：

  >| 名称       | 类型   | 说明                     |
  >| ---------- | ------ | ------------------------ |
  >| table_name | String | 数据库表名               |
  >| name       | String | signal名称               |
  >| freq       | String | 数据频率，默认为 'daily' |

  - 返回：无

- on_start

  - 函数作用：用于用户重载实现
  - 参数：无
    - 返回：无

- pre_transform 

  - 函数作用：SignalMatrix数据加载完成后，将调用本方法。用于用户重载实现
  - 参数：无
  - 返回：无

- post_transform 

  - 函数作用：SignalMatrix执行完run方法后，将调用本方法。用于用户重载实现
  - 参数：无
  - 返回：无

- on_clock 

  - 函数作用：SignalMatrix执行on_clock方法时，将调用本方法。用于用户重载实现
  - 参数：无
  - 返回：无


#### 配置方式：

- yaml文件配置

```
# 策略代码组件
# 用户通过继承 SignalStrategy编写策略逻辑

strategy:

    project_1_factor:
        class: 
        	# 代码文件路径, 支持.py / .pyc 等python代码文件，
            # 支持相对路径 e.g. ../strategy.py 为 config.yaml所在路径的上一级目录下的strategy.py文件
            - strategy.py
            # 类名
            - ReverseSignal
```

#### 因子计算样例：

- ReverseSignal重载SignalStrategy，实现反转因子的计算

  - config.yaml文件

  ```text
  matrix:
  
      mode: signal
      span: [2019-01-01, 2021-12-30]
      codes: &universe ../../../custom_universe.pkl
      
      show_report: False
  
  strategy:
  
      project_1_factor:
          class: 
              - strategy.py
              - ReverseSignal
  ```

  - strategy.py文件

  ```python
  from scipy.stats import zscore
  from transmatrix.strategy import SignalStrategy
  from transmatrix.data_api import create_data_view, NdarrayData, DataView3d, DataView2d
  
  
  class ReverseSignal(SignalStrategy):
      def init(self):
          self.add_clock(milestones='09:35:00')
          self.subscribe_data(
              'pv', ['common','stock_bar_daily',self.codes,'open,high,low,close', 10]
          )
          self.pv: DataView3d
  
  
      def pre_transform(self):
          if 'reverse' not in self.pv.fields:
              pv = self.pv.to_dataframe()
              ret = (pv['close'] / pv['close'].shift(1) - 1).fillna(0)
              reverse = -ret.rolling(window = 5, min_periods = 5).mean().fillna(0)
              reverse = zscore(reverse, axis = 1, nan_policy='omit')
              self.reverse: DataView2d = create_data_view(NdarrayData.from_dataframes(reverse))
              self.reverse.align_with(self.pv)
              
      def on_clock(self):
          self.update_signal(self.reverse.get())
  ```

  - run.ipynb

  ```python
  In:
  	from transmatrix.workflow import run_matrix
  	matrix = run_matrix('config.yaml')
  ```

### 1.2.3 SimulationStrategy

继承自BaseStrategy，策略回测组件的基类。

- 继承此类后，用户可自行选择实现on_init，on_market_data_update，on_trade等方法。

#### 属性：

>| 名称       | 类型                       | 说明         |
>| ---------- | -------------------------- | ------------ |
>| name       | String                     | 组件名称     |
>| time       |                            |              |
>| latency    |                            |              |
>| accounts   |                            | 账户组件集   |
>| account    |                            | 账户组件     |
>| evaluators | Dict[str, SignalEvaluator] | 因子评价组件 |

#### 方法：

- add_evaluator

  - 函数作用：添加评价组件

  - 参数：

    >| 名称      | 类型                | 说明         |
    >| --------- | ------------------- | ------------ |
    >| evaluator | SimulationEvaluator | 评价组件实例 |

  - 返回：无

- add_account 

  - 函数作用：根据策略配置，初始化账户组件

  - 参数：

    >| 名称    | 类型        | 说明         |
    >| ------- | ----------- | ------------ |
    >| account | BaseAccount | 账户组件实例 |

  - 返回： 无

- set_latency

  - 函数作用：查询当前账户的挂单

  - 参数：

    >| 名称    | 类型 | 说明 |
    >| ------- | ---- | ---- |
    >| latency | int  |      |

  - 返回：无

- get_cash 

  - 函数作用：账户现金流
  - 参数：无
  - 返回：Dict

- get_pnl 

  - 函数作用：账户pnl
  - 参数：无
  - 返回：Dict

- get_trade_table 

  - 函数作用：交易记录
  - 参数：

  >| 名称 | 类型   | 说明     |
  >| ---- | ------ | -------- |
  >| code | String | 股票代码 |

  - 返回：指定股票的交易记录

- get_daily_stats 

  - 函数作用：持仓记录
  - 参数：

  >| 名称 | 类型   | 说明     |
  >| ---- | ------ | -------- |
  >| code | String | 股票代码 |

  - 返回：指定股票的持仓记录

- buy 

  - 函数作用：策略买入
  - 参数：

  >| 名称   | 类型   | 说明                                         |
  >| ------ | ------ | -------------------------------------------- |
  >| price  | float  | 买入价格                                     |
  >| volume | float  | 买入数量                                     |
  >| offset | String | 操作类型，包括 'open' (开仓)和'close' (平仓) |
  >| code   | String | 代码                                         |
  >| market | String | 行情组件名称                                 |

  - 返回：无

- sell 

  - 函数作用：策略卖出
  - 参数：

  >| 名称   | 类型   | 说明                                         |
  >| ------ | ------ | -------------------------------------------- |
  >| price  | float  | 卖出价格                                     |
  >| volume | float  | 卖出数量                                     |
  >| offset | String | 操作类型，包括 'open' (开仓)和'close' (平仓) |
  >| code   | String | 代码                                         |
  >| market | String | 行情组件名称                                 |

  - 返回：无

- create_order 

  - 函数作用：生成订单对象
  - 参数：

  >| 名称      | 类型                | 说明                                                       |
  >| --------- | ------------------- | ---------------------------------------------------------- |
  >| price     | float               | 下单价格                                                   |
  >| volume    | float               | 下单数量                                                   |
  >| direction | ORDER_DIRECTION枚举 | 下单方向，包括ORDER_OFFSET.BUY和ORDER_OFFSET.CLOSE两个方向 |
  >| offset    | String              | 操作类型，包括 'open' (开仓)和'close' (平仓)               |
  >| code      | String              | 代码                                                       |
  >| market    | String              | 行情组件名称                                               |
  >| strategy  | BaseStrategy        | 策略组件                                                   |

  - 返回：生成的Order对象

- send_order 

  - 函数作用：策略下单
  - 参数：

  >| 名称  | 类型  | 说明     |
  >| ----- | ----- | -------- |
  >| order | Order | 订单对象 |

  - 返回：无

- cancel_order

  - 函数作用：取消订单
  - 参数：

  >| 名称  | 类型  | 说明 |
  >| ----- | ----- | ---- |
  >| order | Order | 订单 |

  - 返回：无

- on_init 

  - 函数作用：策略初始化时将调用本方法，用户自定义实现
  - 参数：无
  - 返回：无

- on_market_data_update 

  - 函数作用：行情数据更新时将调用本方法，用户自定义实现
  - 参数：无
  - 返回：无

- on_trade 

  - 函数作用：订单成交时将调用本方法，用户自定义实现
  - 参数：

  >| 名称  | 类型        | 说明     |
  >| ----- | ----------- | -------- |
  >| trade | MatchResult | 成交记录 |

  - 返回：无

- on_receive 

  - 函数作用：账户对象接收到订单时将调用本方法，用户自定义实现
  - 参数：

  >| 名称  | 类型  | 说明     |
  >| ----- | ----- | -------- |
  >| order | Order | 订单对象 |

  - 返回：无

- on_order_reject 

  - 函数作用：订单被拒绝时将调用本方法，用户自定义实现
  - 参数：

  >| 名称  | 类型  | 说明     |
  >| ----- | ----- | -------- |
  >| order | Order | 订单对象 |

  - 返回：无

- on_market_close

  - 函数作用：休市时将调用本方法，用户自定义实现
  - 参数：

  >| 名称        | 类型   | 说明       |
  >| ----------- | ------ | ---------- |
  >| market_name | String | market名称 |

  - 返回：无

- on_market_open 

  - 函数作用：开市时将调用本方法，用户自定义实现
  - 参数：

  >| 名称        | 类型   | 说明       |
  >| ----------- | ------ | ---------- |
  >| market_name | String | market名称 |

  - 返回：无


#### 配置方式：

- yaml文件配置

```
# 策略代码组件
# 用户通过继承 SimulationStrategy编写策略逻辑

strategy:
    test_strategy:
        class:
            # 代码文件路径, 支持.py / .pyc 等python代码文件，
            # 支持相对路径 e.g. ../strategy.py 为 config.yaml所在路径的上一级目录下的strategy.py文件
            - strategy.py 
            #类名
            - TestStra
```

#### 策略回测样例：

- config.yaml文件

```text
matrix:

    mode: simulation
    span: [2021-01-01, 2021-01-31]
    codes: &universe custom_universe.pkl
    ini_cash: 1000000
    
    market:
        stock:
            data: [common, stock_bar_daily]
            matcher: daily
            account: detail

strategy:
    test_strategy:
        class:
            - strategy.py 
            - TestStra
```

- strategy.py文件

```python
from transmatrix.strategy import SimulationStrategy


#用户自定义回调 支持 定时、定频、条件触发等机制
# callback_per_50min = Scheduler.FixFreqScheduler(freq = '50min') 
# callback_at_10and14 = Scheduler.FixTimeScheduler(milestones= ['10:01:00','13:59:00'])

class TestStra(SimulationStrategy):
    def init(self):
        self.subscribe_data(
            'macd', ['common', 'factor_data__stock_cn__tech__1day__macd', self.codes, 'value', 10]
        )
        self.max_pos = 300
    
    #注册定时定频任务
    def on_init(self):
        # self.add_scheduler(schedular=callback_per_50min, handler=self.callback50min)
        # self.add_scheduler(schedular=callback_at_10and14, handler=self.callback10and14)
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
        macd = self.macd.query(self.time, 3)['value'][self.codes].mean().sort_values()
        buy_codes = macd.iloc[:2].index
        sell_codes = macd.iloc[-2:].index

        for code in buy_codes:
            # 获取某只股票的仓位
            pos = self.account.get_netpos(code)

            if  pos < self.max_pos:
                price = market.get('close', code)
                self.buy(
                    price, 
                    volume=100, 
                    offset='open', 
                    code=code, 
                    market='stock')
```

- run.ipynb

```python
In:
	from transmatrix.workflow.run_yaml import run_matrix
	mat = run_matrix('config.yaml')
```

