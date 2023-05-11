## 1.3 Evaluator

### 1.3.1 BaseEvaluator

BaseEvaluator是因子评价组件的基类。

- 该组件在研究引擎SignalMatrix的init方法中初始化，主要包括收集订阅数据，加载数据，校准订阅数据等过程
- 因子评价的具体逻辑，需要用户继承BaseEvaluator，自己实现init，critic，regist和show方法

#### 属性：

>| 名称                | 类型                               | 说明                                       |
>| ------------------- | ---------------------------------- | ------------------------------------------ |
>| name                | String                             | 组件名称                                   |
>| matrix              | SignalMatrix或SimulationMtrix      | 研究引擎                                   |
>| strategy            | SignalStrategy或SimulationStrategy | 策略                                       |
>| datas               |                                    |                                            |
>| subscribe_data_info | Dict                               | 订阅的数据字典，key为名称，value为数据信息 |
>| codes               | Dict                               | 股票代码                                   |
>| backend             | str                                | 'ipython'或'tqclient'，评价作图输出途径    |
>| kpis                | Dict                               | 评价kpi字典                                |

#### 方法：

- init 

  - 函数作用：用于订阅评价需要的数据等，用户自行实现（<u>必须</u>）
  - 参数：无
  - 返回：无

- eval 

  - 函数作用：准备数据，运行评价，SignalMatrix运行eval方法时，调用本方法
  - 参数：无
  - 返回：无

- add_strategy 

  - 函数作用：添加strategy组件

  - 参数：

    >| 名称     | 类型                               | 说明     |
    >| -------- | ---------------------------------- | -------- |
    >| strategy | SignalStrategy或SimulationStrategy | 策略组件 |

  - 返回：无

  - 返回：无

- alignment

  - 函数作用：复制本身, 并挂载strategy

  - 参数：

    >| 名称     | 类型                               | 说明     |
    >| -------- | ---------------------------------- | -------- |
    >| strategy | SignalStrategy或SimulationStrategy | 策略组件 |

  - 返回：无

  - 返回：无

- plot

  - 函数作用：作图

  - 参数：

    >| 名称  | 类型                    | 说明                       |
    >| ----- | ----------------------- | -------------------------- |
    >| data  | DataFrame, Series或list | 作图数据                   |
    >| kind  | str                     | 'line', 'bar', 'heatmap'等 |
    >| title | str                     | 图片标题                   |
    >| name  | list或str               | 每个column的名字           |

  - 返回：无


- critic 

  - 函数作用：因子评价的具体逻辑，在准备好数据后，调用本方法，用户自行实现
  - 参数：无

  - 返回：无

- regist 

  - 函数作用：计算kpi，在准备好数据后，调用本方法，用户自行实现
  - 参数：无

  - 返回：无

- show

  - 函数作用：展示评价结果
  - 参数：无
  - 返回：无

### 1.3.2 SignalEvaluator

继承自BaseEvaluator，因子评价组件的基类。

- 继承此类后，用户可自行编写评价逻辑。

#### 属性：

>| 名称         | 类型 | 说明                                                         |
>| ------------ | ---- | ------------------------------------------------------------ |
>| signal       | Dict | 信号因子字典，键为时间，值为信号值                           |
>| aligned_data | Dict | 以待评价因子的时间戳为标准，对SignalEvaluator订阅的数据进行校准 |

#### 方法：

同BaseEvaluator。


#### 配置方式：

- yaml文件配置

```text
# 因子评价组件 [signal模式]
# 用户通过继承 SignalEvaluator 实现因子分析逻辑

evaluator:
    SimpleAlphaEval:
        class:
            - evaluator.py
            - Eval

```

#### 因子评价样例：

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
    
evaluator:
    SimpleAlphaEval:
        class:
            - evaluator.py
            - Eval

```

- strategy.py文件（同因子计算）
- evaluator.py文件

```python
from evaluator_tools.signal2weights import *
from transmatrix.evaluator.signal import SignalEvaluator

import multiprocessing as mp
import pandas as pd

class Eval(SignalEvaluator):
    def init(self):
        self.subscribe_data(
            'pv', ['common','stock_bar_daily',self.codes,'open,high,low,close', 10]
        )
        self.subscribe_data(
            'meta', ['common','critic_data', self.codes, 'is_zz500,ind', 10]
        )
        
        self.backend = 'tqclient'
    
    def critic(self):
        critic_data = self.aligned_data['pv'].to_dataframe()
        critic_data.update(self.aligned_data['meta'].to_dataframe())
        critic_data.update({'signal': self.strategy.signal})

        perf = {}
        perf.update(self._process_base(critic_data))

        stats = perf['stats']
        stats.update(self._process_500(critic_data))
        stats = pd.DataFrame(pd.Series(stats, name = 'VALUE'))
        stats.index.name = 'FIELD'
        perf['stats'] = stats

        perf.update(self._process_ind(critic_data))
        self.perf = perf
        return
        
    def show(self):
        perf = self.perf
        
        self.plot(perf['qret']['tot'], kind='bar', title = 'QuantRetTot')
        self.plot(perf['qret']['history'], title = 'QuantRetHistory')
        
        self.plot(perf['history'][['top_dd_ser', 'top_nav_ser']], second_y=1, title = 'TopNavHistory')
        self.plot(perf['history'][['ls_dd_ser', 'ls_nav_ser']], second_y=1, title = 'LSNavHistory')
        self.plot(perf['industryIC'].reset_index().rename(columns={'index':'industry'}), kind='table', title='行业IC和IR')
        
        print(self.perf['industryIC'])
        
    def regist(self):
        perf = self.perf

        kpis = {}
        kpis['回测时间区间'] = perf['stats'].loc['dates','VALUE']
        kpis['IC'] = perf['stats'].loc['ICMean','VALUE']
        kpis['IR'] = perf['stats'].loc['ICIR','VALUE']
        kpis['因子年化收益率'] = perf['stats'].loc['TopRetYL','VALUE']
        
        self.kpis = kpis
```

- run.ipynb（同因子计算）



### 1.3.3 SimulationEvaluator

继承自BaseEvaluator，策略评价组件的基类

- 继承此类后，用户可自行用户可自行编写评价逻辑。

#### 属性：

同BaseEvaluator。

#### 方法：

- add_evaluator

  - 函数作用：添加评价组件

  - 参数：

    >| 名称      | 类型                | 说明         |
    >| --------- | ------------------- | ------------ |
    >| evaluator | SimulationEvaluator | 评价组件实例 |

  - 返回：无

- get_cash 

  - 函数作用：账户现金流
  - 参数：无
  - 返回：现金流的DataFrame

- get_pnl 

  - 函数作用：账户pnl
  - 参数：无
  - 返回：pnl的DataFrame

- get_trade_table 

  - 函数作用：交易记录的DataFrame
  - 参数：无

  - 返回：交易记录

- get_daily_stats 

  - 函数作用：持仓记录
  - 参数：无

  - 返回：持仓记录的DataFrame


#### 配置方式：

- yaml文件配置

```
# 回测评价组件 [simulation]
# 用户通过继承 SimulationEvaluator 实现因子分析逻辑

evaluator:
    test_eval:
        class:
            - evaluator.py 
            - TestEval
```

#### 回测评价样例：

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

evaluator:
    test_eval:
        class:
            - evaluator.py 
            - TestEval
```

- strategy.py文件(同SimualtionStrategy)
- evaluator.py文件

```python
from transmatrix.evaluator.simulation import SimulationEvaluator

import pandas as pd
import numpy as np

class TestEval(SimulationEvaluator):
    def init(self):
        self.backend = 'tqclient'
        
        self.subscribe_data(
            'benchmark', ['default', 'stock_index', '000300.SH', 'close', 0]
        )
        # self.subscribe_data(
        #     'industry', ['common', 'critic_data', self.codes, 'ind', 0]
        # )
    
    
    def critic(self):
        ini_cash = self.strategy.account.cash
        daily_stats = self.get_daily_stats()
        pnl = self.get_pnl()
        
        dt_index = daily_stats.index.get_level_values('datetime').unique().sort_values()
        dt_index = pd.to_datetime(dt_index).date
        perf = pd.DataFrame(index=dt_index)
        
        # 策略收益
        perf['每日损益'] = pnl
        stra_netvalue = (perf['每日损益'].cumsum() + ini_cash) / ini_cash
        perf['策略净值'] = stra_netvalue
        perf['策略收益率'] = (stra_netvalue / stra_netvalue.shift(1) - 1).fillna(0)
        perf['策略累计收益率'] = (1 + perf['策略收益率']).cumprod() - 1

        # benchmark收益
        bench = self.benchmark.to_dataframe()['close']
        bench.index = pd.to_datetime(bench.index).date
        bench = bench.loc[perf.index]
        bench_netvalue = bench / bench.iloc[0]
        perf['基准净值'] = bench_netvalue
        bench_return = (bench / bench.shift(1) - 1).fillna(0)
        perf['基准收益率'] = bench_return
        perf['基准累计收益率'] = (1 + perf['基准收益率']).cumprod() - 1
        
        # 超额收益
        perf['超额收益率'] = perf['策略收益率'] - perf['基准收益率']
        perf['累计超额收益率'] = perf['策略累计收益率'] - perf['基准累计收益率']
        
        self.perf = perf      
        
    
    def show(self):
        perf = self.perf
        
        self.plot(perf[['策略净值','基准净值']], kind='line', title='策略和基准净值')
        self.plot(perf[['策略收益率','基准收益率','超额收益率']], kind='line', title='策略和基准收益率')
        self.plot(perf[['策略累计收益率','基准累计收益率','累计超额收益率']], kind='line', title='策略和基准累计收益率', areacol=0)
        self.plot(perf[['每日损益']], kind='line', title='每日损益', name='损益')
    
    def regist(self):
        perf = self.perf
        
        dates = perf.index.astype(str)
        kpis = {}
        kpis['回测时间区间'] = f"{dates[0]} ~ {dates[-1]}"
        kpis['年化收益'] = perf['策略收益率'].mean() * 250
        kpis['波动率'] = perf['策略收益率'].std() * np.sqrt(250)
        kpis['Beta'] = np.cov(perf['策略收益率'],perf['基准收益率'])[0,1] / np.var(perf['基准收益率'])
        kpis['基准年化收益'] = perf['基准收益率'].mean() * 250
        kpis['Alpha'] = kpis['年化收益'] - kpis['Beta'] * kpis['基准年化收益']
        kpis['夏普率'] = kpis['年化收益'] / kpis['波动率']
        stratret = perf['策略收益率'].to_numpy()
        std_d = np.std(stratret[stratret<0]) * np.sqrt(250)
        kpis['索提诺比率'] = kpis['年化收益'] / std_d
        
        drawdrown = (perf['策略净值'].cummax() - perf['策略净值']) / perf['策略净值'].cummax()
        kpis['最大回撤'] = drawdrown.max()
        
        mask = perf['策略净值'].cummax() > perf['策略净值'].cummax().shift(1).fillna(-np.inf)
        dd_span = pd.Series(np.nan, index=mask.index)
        dd_span[mask.values] = mask.index[mask.values]
        dd_span.ffill(inplace=True)
        loc = drawdrown.argmax()
        d0,d1 = dd_span.iloc[loc],drawdrown.index[loc]
        kpis['最大回撤时间区间'] = f"{d0} ~ {d1}"
        
        self.kpis = kpis
```



- run.ipynb(同SimualtionStrategy)