# 三、因子研究
## 3.1 架构
- 因子研究主要包含3大组件：研究引擎组件SignalMatrix，因子计算组件SignalStrategy，因子评价组件BaseEvaluator
- SignalMatrix 用于指定回测参数，如回测时间段，样本空间，因子计算组件需要挂载的数据，触发因子计算逻辑的时间等等
- SignalStrategy 是因子计算组件的基类，因子计算的具体逻辑，需要***用户自己继承该类并实现***
- BaseEvaluator 是因子评价组件的基类，因子评价的具体逻辑，需要***用户自己继承该类并实现***。系统也提供了默认的评价模板，以及若干典型的评价模板，参见3.4.4 评价模板样例

  <div align=center>
  <img width="1000" src="pngs/factor_research_arch.png"/>
  </div>
  <div align=center style="font-size:12px">因子研究架构</div>
  <br />

## 3.2 研究引擎 
### 3.2.1 SignalMatrix
- 因子研究引擎组件
  - 属性：
  >名称|类型|说明
  >----|----|----
  config|Dict|引擎相关配置字典
  codes|List|股票样本空间列表
  start|datetime|起始时间
  end|datetime|结束时间
  closk_info|String|触发因子计算逻辑的时间
  ini_cash|int|账户初始资金
  factor_sub|Dict|config中data键所挂载的数据
  fin_factor_sub|Dict|config中findata键所挂载的数据
  data_engine|DataEngine|数据查询引擎
  pta_backend|String|当前客户端类型，包括'ipython'和'tqclient'两类
  logging|bool|是否起用日志，默认为False
  cache_data_to_pkl|bool|是否将数据缓存到本地，默认为True
  saving_signal|bool/String|若不提供该字段（或值为False),则不会保存因子。默认为False
  showing_report|bool|是否自动调用BaseEvaluator.show()方法，默认为False
  strategies|Dict|引擎所挂载的SignalStrategy实例集合
  evaluators|Dict|引擎所挂载的BaseEvaluator实例集合
  schedulers|List|任务调度器所组成的集合
  timeline|Timeline|事件处理器

- init 组件初始化（数据加载，配置因子计算组件，因子评价组件等等）
  - 参数：
    无
  - 返回：
    无

- run 运行因子计算，得到因子数据
  - 参数：
    无
  - 返回：
    无

- eval 遍历evaluators，分别评价因子
  - 参数：
    无
  - 返回：
    无

- show_report 遍历evaluators，展示因子评价结果
  - 参数：
    无
  - 返回：
    无

- save_analysis 保存评价结果
  - 参数：
    无
  - 返回：
    无

- save_signal 遍历strategies，保存因子数据
  - 参数：
    无
  - 返回：
    无

- on_clock 遍历strategies，在每个closk_info时间点触发on_clock事件
  - 参数：
    无
  - 返回：
    无

### 3.2.2 相关API
#### BaseMatrix
- SignalMatrix和SimulationMatrix的基类，用于实现引擎的一些通用功能

#### 任务调度器
#### BaseSchedular
- 任务调度器基类
  - 属性：
  >名称|类型|说明
  >----|----|----
  name|String|调度器名称
  matrix|BaseMatrix|引擎
  dofucs|List|注册的回调函数列表
  
- regist 注册外部方法到调度器
  - 参数：
  >名称|类型|说明
  >----|----|----
  fucs|method|List|注册到本调度器的一个或多个方法
  - 返回：
    无

- do 执行注册的所有方法，每个方法相当于一个任务
  - 参数：
    无
  - 返回：
    无  
#### ExternalTimeScheduler
- 继承自BaseSchedular，用于外部已指定的时间序列，执行任务
  - 属性：
  >名称|类型|说明
  >----|----|----
  external_steps|iterator|外部指定的时间序列
  start|datetime|起始时间
  end|datetime|结束时间
  steps|List|在start和end之间的，指定的时间序列

- gen_steps 生成steps
  - 参数：
    无
  - 返回：
    无  
#### FixTimeScheduler
- 继承自BaseSchedular，每日固定时间触发任务执行
  - 属性：
  >名称|类型|说明
  >----|----|----
  milestones|String|每日触发任务执行的时间
  steps|List|用于执行任务的时间序列

- gen_steps 生成steps
  - 参数：
    无
  - 返回：
    无
#### FixFreqScheduler
- 继承自BaseSchedular，每日固定频率触发任务执行
  - 属性：
  >名称|类型|说明
  >----|----|----
  freq|String/Dateoffset|任务执行的频率，形如 '5H', '50min'，可参照pandas的timeseries.offset_aliases
  start|datetime|起始时间
  end|datetime|结束时间
  steps|List|用于执行任务的时间序列

- gen_steps 生成steps
  - 参数：
    无
  - 返回：
    无
#### CallbackDaily
- 继承自BaseSchedular，每日固定时间触发任务执行
  - 属性：
  >名称|类型|说明
  >----|----|----
  time|String|指定的时间
  steps|List|用于执行任务的时间序列

- gen_steps 生成steps
  - 参数：
    无
  - 返回：
    无

#### CallbackEOD
- 继承自CallbackDaily，每日16点（盘后）触发任务执行
  - 属性：
  >名称|类型|说明
  >----|----|----
  time|String|值为'16:00:00'

#### CallbackSOD
- 继承自CallbackDaily，每日8点（盘前）触发任务执行
  - 属性：
  >名称|类型|说明
  >----|----|----
  time|String|值为'08:00:00'

#### Timeline
- 生成一系列的事件列表

#### run_matrix
- 加载yaml配置文件，运行因子研究
- 参见3.2.4节
  - 参数：
  >名称|类型|说明
  >----|----|----
  yaml_path|String|yaml文件路径

### 3.2.3 配置说明
- SignalMatrix 配置项说明如下：
  ``` text
    # 研究模式: 
        # signal:       股票alpha因子研究
        # simulation :  模拟交易
    mode: signal

    # 回测起止时间
    span: [2019-01-01, 2021-12-30]

    # 用户自定义的交易票池
    # e.g. 此处引用了同级别目录下的 xxx.pkl文件
    # 用户可以自行定义交易票池,以列表 列表、字符串或文件的形式传入
    universe: &universe custom_universe.pkl  

    
    # 触发因子计算逻辑的时间 [signal模式特有] 
    # e.g. '09:35:00'表示每天 09:35分进行计算一次因子
    # 一般而言clock时间应当与真实策略交易时间频率一致
    # 支持日内因子: e.g. '09:35:00,11:00:00,14:00:00'
    clock: '09:35:00'   

    # 数据订阅
    data:
        # 定义一个回测中可调用的数据结构
        # e.g.名称为pv, 则可以在策略代码中使用 .pv调取到该数据
        # 每个数据是一个 Array3dPanel 实例（api使用方式详见在线文档data-api部分)
        pv: 
            # 数据配置信息: 可以理解为一条SQL语句的
            - default                        # 数据库名 
            - stock_bar_daily                # 表名 
            - *universe                      # 股票代码范围
            - open,high,low,close,volume     # 选取字段
            - 10                             # 数据buffer窗口，单位：日 (回测引擎会自动查询回测开始时间之前N天的数据，以保障在回测开始时能够拿到因子计算所需的数据)
        
        # 可订阅多个数据结构,每个数据结构可为任意频率数据
        # e.g. 上面 pv 订阅了日线数据，而下述 ashare_cashflow为财报数据（季频）
        cashflow:
            - ashare_cashflow
            - *universe
            - net_profit,invest_loss
            - 10

        # "Signal" 为 TransMatrix系统关键字
        # 当配置 Signal 数据块时，系统自动进入"已入库因子评价"模式
        # 注意事项：1.此时应当保证 data 字段下面只有 Signal 一个数据块。 2.此时不允许配置strategy字段

        # Signal:
            # - private_database
            # - daily_alpha_research
            # - macd
            # - *universe
            # - 0 

    # [signal模式特有][因子库项目特有]
    # 因子保存配置

    # ‘temp_factor_table’为表名（建议用户调用 transmatrix.data_api.create_factor_table创建因子表）
    # 若不提供该字段（或值为False),则不会保存因子
    # 系统自动将因子(对应表的字段) 命名为strategy字段下的策略名（见下方strategy部分）
    save_signal: temp_factor_table

    # [signal模式特有]
    # 是否自动调用 evaluator.show()方法
    # 系统支持多种因子评价报告模板(详见测试用例 project_signal_templeteA/B/C/D)
    show_report: True

    # 是否输出系统日志 （日志默认保存在config.yaml入口文件同级目录下的 log 文件夹中)
    logging: False

    # 全局变量（在回测运行的过程中不可修改)
    # 调用方式: Matrix实例 调用 .context, Strategy / evaluator 实例调用 .matrix_context
    context:
        long  : 26
        short : 12
        diff  : 9
  '''

### 3.2.4 配置方式
#### yaml文件配置
- 将相关配置写进yaml文件，调用相关方法加载配置：
  - 命令行调用 : Matrix -p CONFIG_PATH
  - Python调用 : transmatrix.matrix.run_matrix(CONFIG_PATH)
#### 代码配置
- 在Python代码中构造config字典
  ```python
  In:
    # 回测参数
    mat_config = {   
        'mode' : 'signal',
        'span': [START, END],
        'universe': CODES,
        'data': {
            'pv': ['*','stock_bar_daily', CODES, 'open,high,low,close,volume', 10],
        },
        'clock': '09:35:00',        
    }
    # 组件实例化
    matrix = SignalMatrix(mat_config)
    matrix
  ```
  ```text
  Out:
    <transmatrix.matrix.signal.base.SignalMatrix at 0x7f26142e0100>
  ```

## 3.3 因子计算
### 3.3.1 SignalStrategy
- 因子计算组件的基类
  - 说明：
    - 该组件在研究引擎SignalMatrix的init方法中初始化，主要包括挂载引擎订阅的数据，注册因子等过程
    - 因子计算的具体逻辑，需要用户继承SignalStrategy，自己实现pre_transform, on_clock, post_transform方法
    - 系统提供了若干因子计算样例，参见3.3.5节
  - 属性：
  >名称|类型|说明
  >----|----|----
  name|String|组件名称
  config|Dict|组件的配置字典
  matrix|SignalMatrix|因子研究引擎
  factors|Dict|外部注册的因子数据字典，键为因子名
  factor_data|Array3dPanel|由factors转换得到的Array3dPanel
  factor_frequency|String|因子数据频率，默认为 'daily'
  signal|Dict|信号因子字典，键为时间，值为信号值

- generate 注册因子到factors
  - 参数：
  >名称|类型|说明
  >----|----|----
  name|String|因子名称

  - 返回：
    无

- gen_factor_panel 生成空的factor_data
  - 参数：
    无
  - 返回：
    无

- update_signal 添加当前时间的信号值到signal
  - 参数：
  >名称|类型|说明
  >----|----|----
  value|object|信号值
  - 返回：
    无

- update_factor 更新当前时间的因子值到factor_data
  - 参数：
  >名称|类型|说明
  >----|----|----
  name|String|因子名称
  value|array-like/Iterable|因子值，长度为股票数量
  - 返回：
    无

- save_factors 保存factor_data的数据到数据库
  - 参数：
  >名称|类型|说明
  >----|----|----
  table_name|String|数据库表名
  freq|String|数据频率，默认为 'daily'
  - 返回：
    无

- save_signal 保存信号因子signal到数据库
  - 参数：
  >名称|类型|说明
  >----|----|----
  table_name|String|数据库表名
  freq|String|数据频率，默认为 'daily'
  - 返回：
    无

- pre_transform SignalMatrix数据加载完成后，将调用本方法。用于用户重载实现
  - 参数：
    无
  - 返回：
    无

- post_transform SignalMatrix执行完run方法后，将调用本方法。用于用户重载实现
  - 参数：
    无
  - 返回：
    无

- on_clock SignalMatrix执行on_clock方法时，将调用本方法。用于用户重载实现
  - 参数：
    无
  - 返回：
    无

### 3.3.2 ExternalSignal
- 继承自SignalStrategy，用于评价库内因子
  代码样例:
  ```python
  In:
    from transmatrix.matrix import ExternalSignal
    strategy = ExternalSignal(matrix = mat_instance)
    type(strategy)
  ```
  ```text
  Out:
    transmatrix.matrix.signal.trader.ExternalSignal
  ```
  - post_transform 将挂载的信号因子（类型为pandas.DataFrame赋值到signal属性）
    - 参数：
      无
    - 返回：
      无
  

### 3.3.3 配置说明
- SignalStrategy 配置项说明如下：
  ``` text
  # 策略代码组件
  # 用户通过继承 SignalStrategy（因子研究）或 BaseStrategy（模拟交易） 编写策略逻辑

  # 【注意】：当 matrix:data 下面配置了 Signal 字段时，系统自动进入"已入库因子评价"模式，该模式下无需用户编写策略（不允许配置strategy）
  strategy:

      # 策略名 [signal模式下为因子名]
      reverse_signal:
          # 策略代码信息
          class: 
              # 代码文件路径, 支持.py / .pyc 等python代码文件，
              # 支持相对路径 e.g. ../strategy.py 为 config.yaml所在路径的上一级目录下的strategy.py文件
              - strategy.py   
              # 类名
              - ReverseSignal
      
      # 可配置多个策略
      # trendy_signal:
          # class: 
              # - strategy.py
              # - TrendySignal
  ```
### 3.3.4 配置方式
#### yaml文件配置
- 将相关配置写进yaml文件，调用相关方法加载配置，参见3.2.4
#### 代码配置
- 在Python代码中构造config字典
  ```python
  In:
    # 策略参数
    stra_config = {
        'name': 'reverseSignal',
    }
    # 组件实例化
    mat = SignalMatrix(mat_config)
    strategy = ReverseSignal(stra_config, mat)
    type(strategy)
  ```
  ```text
  Out:
    strategy.ReverseSignal
  ```
### 3.3.5 因子计算样例
- ReverseSignal重载SignalStrategy，实现反转因子的计算
  - config.yaml文件
  ```text
  matrix:

      mode: signal
      market_type: stock_cn
      span: [2019-01-01, 2021-12-30]
      universe: &universe custom_universe.pkl
      clock: '09:35:00'
      check_codes: False

      data:
          pv: 
              - default
              - stock_bar_daily
              - *universe
              - open,high,low,close,volume
              - 10

      save_signal: False
      show_report: True
      
  strategy:

      signal_x:
          class: 
              - strategy.py
              - ReverseSignal
  ```

  - strategy.py文件
  
  ```python
  from transmatrix.matrix.signal.base import SignalStrategy
  from transmatrix.data_api import Array3dPanel
  from scipy.stats import zscore

  class ReverseSignal(SignalStrategy):

      def pre_transform(self):
          if 'reverse' not in self.pv.fields:
              pv = self.pv.to_dataframes()
              ret = (pv['close'] / pv['close'].shift(1) - 1).fillna(0)
              reverse = -ret.rolling(window = 5, min_periods = 5).mean().fillna(0)
              reverse = zscore(reverse, axis = 1)
              self.pv.concat(Array3dPanel.from_dataframes({'reverse' : reverse}))
          
      def on_clock(self):
          self.update_signal(self.pv.get(field = 'reverse', codes = '*'))
  ```
  
  - run.ipynb
  ```python
  In:
    from transmatrix.workflow import run_matrix
    mat = run_matrix('config.yaml')
  ```
  ```text
  Out:
    loading data stock_bar_daily from datacache.
  ```
  ```python
  In:
    strategy = mat.strategies['signal_x']
    strategy.signal.head()
  ```
  <div align=center>
  <img width="1000" src="pngs/signal_calc_sample.png"/>
  </div>
  <div align=center style="font-size:12px">因子计算结果</div>

## 3.4 因子评价
### 3.4.1 BaseEvaluator
- 因子评价组件的基类

  - 说明：
  
    - 该组件在研究引擎SignalMatrix的init方法中初始化，主要包括收集订阅数据，加载数据，校准订阅数据等过程

    - 因子评价的具体逻辑，需要用户继承BaseEvaluator，自己实现critic方法和show方法
    
    - 系统提供了若干模板供用户使用，参见3.4.4节

  - 属性：
  >名称|类型|说明
  >----|----|----
  name|String|组件名称
  subscribe|Dict|订阅的数据配置
  benchmark|List|订阅的基准
  data|Dict|订阅的数据，形为 {name : Array3dPanel} 的字典实例化数据集合
  matrix|SignalMatrix|研究引擎
  benchmark_data|pandas.DataFrame|基准行情数据
  aux_data|Dict|评价辅助数据，形为 {name : Array3dPanel} ，不含股票代码

  - eval 准备数据，运行评价，SignalMatrix运行eval方法时，调用本方法
    - 参数：
      无
    - 返回：
      无

  - critic 因子评价的具体逻辑，eval方法在准备好数据后，调用本方法
    - 参数：
    >名称|类型|说明
    >----|----|----
    critic_data|Dict|形为{name : pandas.DataFrame}的数据集合，包括因子信号数据，基准数据等等
    - 返回：
      无

  - show 展示评价结果
    - 参数：
      无
    - 返回：
      无

### 3.4.2 配置说明
- BaseEvaluator 配置项说明如下：
  ``` text
  # 因子评价组件（分析器） [signal模式特有]
  # 用户通过继承 BaseEvaluator 实现因子分析逻辑

  #【注意】：系统允许 config.yaml 中不包含 analyzer 字段，此时系统自动进入因子计算模式，该模式下系统只负责生产因子（供后续用户自行分析或落库等操作使用）
  analyzer:

      # 分析器名称
      SimpleAlphaEval:

          # 分析器配置信息
          class:
              # 代码文件路径, 支持.py / .pyc 等python代码文件，
              - evaluator.py
              # 类名
              - Eval
          
          # 数据订阅
          data: 
              # 定义一个回测中可调用的数据结构（与matrix下的data字段配置方式一致）
              # 注意：系统保证了 analyzer 下订阅的数据在策略回测过程中不会被strategy调用
              # 因子 analyzer 原则上可以订阅 收益率 等未来信息，而不必担心未来函数问题

              # 数据配置信息: 可以理解为一条SQL语句的
              pv: 
                  - default        
                  - stock_bar_daily
                  - *universe
                  - open,high,low,close,volume
                  - 10
              meta:
                  - default
                  - stock_meta_temp
                  - *universe
                  - is_300,is_500,industry1
                  - 10
  ```

### 3.4.3 配置方式
#### yaml文件配置
- 将相关配置写进yaml文件，调用相关方法加载配置，参见3.2.4
#### 代码配置
- 在Python代码中构造config字典
  ```python
  In:
    # 评价模块参数
    eval_config = {
        'name': 'base_evaluator',
        'data': {
            'pv':   ['*','stock_bar_daily', CODES, 'open,high,low,close,volume', 10],
            'meta': ['*','stock_meta_temp', CODES, 'is_300,is_500,industry1', 10]
        }
    }
    # 组件实例化
    mat = SignalMatrix(mat_config)
    eval = Eval(eval_config, mat)
    print(type(eval))
    print(eval.__class__.__base__) # 显示父类型
  ```
  ```text
  Out:
    <class 'evaluator.Eval'>
    <class 'transmatrix.matrix.signal.base.BaseEvaluator'>
  ```
### 3.4.4 库内因子评价样例
- EvalFull 重载 BaseEvaluator，进行库内因子评价
  - config.yaml文件

  ```text
  matrix:

      mode: signal
      market_type: stock_cn
      span: [2019-01-05, 2021-12-30]
      universe: &universe custom_universe.pkl
      clock: '09:35:00'
      check_codes: False

      data:
          Signal: 
              - test3
              - temp_factor_table1
              - *universe
              - signal_x
              - 0

      save_signal: False
      show_report: True

  analyzer:
      SimpleAlphaEval:
          class:
              - evaluator.py
              - EvalFull
          data: 
              pv: 
                  - default
                  - stock_bar_daily
                  - *universe
                  - open,high,low,close,volume
                  - 10
              meta:
                  - default
                  - stock_meta_temp
                  - *universe
                  - is_300,is_500,is_st,suspend,industry1
                  - 10
          benchmark: [stock_index, 000300.SH]
  ```

  - evaluator.py文件（略）

  - run.ipynb文件
  
  ```python
  In:
    from transmatrix.workflow import run_matrix
    mat = run_matrix('config.yaml')
  ```
  
  ```text
  Out:
    loading data temp_factor_table1 from datacache.

    loading data stock_bar_daily from datacache.

    loading data stock_meta_temp from datacache.

    loading data stock_index from datacache.

    开始因子评价
    ----------------------------------------------------------------------------------------------------
    数据规整: 0.2306秒
    因子覆盖度 0.0062秒
    每日IC 1.6624秒
    每日超额 0.6156秒
    IC统计 0.0138秒
    月度IC和超额 0.0178秒
    分行业IC计算 0.0751秒
    分行业IC分年度 0.0552秒
    ic衰减 0.1917秒
    top组超额 0.2644秒
    完成因子评价
    ----------------------------------------------------------------------------------------------------
    saveing report to /mnt/disk7/yyzhang/transmatrix-cluster-dev/projects/模版/因子研究/2.库内因子评价/report
  ```
  <div align=center>
  <img width="1000" src="pngs/eval_only.png"/>
  </div>
  <div align=center style="font-size:12px">因子评价结果（部分）</div>

### 3.4.5 因子评价模板样例
- 因子结果评价展示模块目前有4个模板（template）可供选择，各个模板侧重点不同，用户可参照这5个模板，编写适合自己的因子评价组件

#### 评价模板A
- 一个基础的评价模板，包括IC分析，收益分析
  - config.yaml文件
  ```text
  analyzer:

      evaluator_templete_A:
          class:

              - evaluator_templete_A.py
              - Eval
          data: 
              pv: 
                  - meta_data
                  - market_data__stock_cn__bar__1day
                  - ../custom_universe.pkl
                  - open,high,low,close,volume
                  - 10
              meta:
                  - meta_data
                  - critic_data
                  - ../custom_universe.pkl
                  - is_hs300,is_zz500,ind
                  - 10
  ```
  - evaluator_templete_A.py (略)
  
  - 评价结果

  ```text
  Out:
  ----------------------------------------------------------------------------------------------------
  stats
                                VALUE
  FIELD                              
  Factor                      reverse
  dates       2019-01-02 ~ 2021-12-29
  ICMean                      0.03155
  ICIR                       0.249986
  TopRetTol                  0.441944
  TopRetYL                   0.151766
  TopSharpYL                 0.640665
  TopMdd                    -0.427052
  LRetTol                    0.479045
  LSRetYL                    0.164507
  LSSharpYL                   0.58943
  LSMdd                     -0.108444
  ICMean_500                 0.020654
  ICIR_500                    0.13706
  ----------------------------------------------------------------------------------------------------
  history
                      top_nav_ser  top_dd_ser  ls_nav_ser  ls_dd_ser
  2019-01-02 09:35:00     0.991502   -0.008498    1.002249   0.000000
  2019-01-03 09:35:00     1.018063    0.000000    1.005035   0.000000
  2019-01-04 09:35:00     1.040050    0.000000    1.004872  -0.000164
  2019-01-07 09:35:00     1.040096    0.000000    1.008196   0.000000
  2019-01-08 09:35:00     1.049471    0.000000    1.014199   0.000000
  ...                          ...         ...         ...        ...
  2021-12-23 09:35:00     1.411556   -0.041726    1.455306  -0.009071
  2021-12-24 09:35:00     1.416388   -0.036893    1.458106  -0.006271
  2021-12-27 09:35:00     1.438391   -0.014890    1.475026   0.000000
  2021-12-28 09:35:00     1.441944   -0.011337    1.479045   0.000000
  2021-12-29 09:35:00     1.441944   -0.011337    1.479045   0.000000

  [728 rows x 4 columns]
  ----------------------------------------------------------------------------------------------------
  ```

  <div align=center>
  <img width="1000" src="pngs/evaluatorA.png"/>
  </div>
  <div align=center style="font-size:12px">评价模板A</div>

#### 评价模板B
- 考虑成交记录，以及交易费率的评价模板
  - config.yaml文件
  ```
  analyzer:
      evaluator_templete_B:
          class:
              - evaluator_templete_B.py
              - EvalTransaction
          data: 
              pv: 
                  - meta_data
                  - market_data__stock_cn__bar__1day
                  - ../custom_universe.pkl
                  - open,high,low,close,volume,vwap
                  - 10
              meta:
                  - meta_data
                  - critic_data
                  - ../custom_universe.pkl
                  - is_hs300,is_zz500,ind
                  - 10               
          fees:
              buy_cost_ratio: 0
              sell_cost_ratio: 0
              slippage: 0

          ini_cash: 100_000_000
  ```
  - evaluator_templete_B.py (略)
  - 评价结果

  ```text
  ----------------------------------------------------------------------------------------------------
  stats
                                VALUE
  FIELD                              
  Factor                      reverse
  dates       2019-01-02 ~ 2021-12-29
  ICMean                     0.032307
  ICIR                       0.268157
  TopRetTol                  0.460756
  TopRetYL                   0.158227
  TopSharpYL                 0.690165
  TopMdd                     -0.28972
  LRetTol                    0.783738
  LSRetYL                    0.269141
  LSSharpYL                   2.53609
  LSMdd                     -0.083017
  ICMean_500                 0.020654
  ICIR_500                    0.13706
  ----------------------------------------------------------------------------------------------------
  history
                      top_nav_ser  top_dd_ser  ls_nav_ser     ls_dd_ser
  2019-01-02 09:35:00     1.000000    0.000000    1.000000 -3.330669e-16
  2019-01-03 09:35:00     0.997567   -0.002433    1.003843  0.000000e+00
  2019-01-04 09:35:00     1.001745    0.000000    1.003886  0.000000e+00
  2019-01-07 09:35:00     1.033436    0.000000    1.005735  0.000000e+00
  2019-01-08 09:35:00     1.039050    0.000000    1.008046  0.000000e+00
  ...                          ...         ...         ...           ...
  2021-12-23 09:35:00     1.469218    0.000000    1.762142  0.000000e+00
  2021-12-24 09:35:00     1.447203   -0.014984    1.760665 -8.380908e-04
  2021-12-27 09:35:00     1.434568   -0.023584    1.759206 -1.665919e-03
  2021-12-28 09:35:00     1.449946   -0.013118    1.774861  0.000000e+00
  2021-12-29 09:35:00     1.460756   -0.005760    1.783738  0.000000e+00

  [728 rows x 4 columns]
  ----------------------------------------------------------------------------------------------------
  ```

  <div align=center>
  <img width="1000" src="pngs/evaluatorB.png"/>
  </div>
  <div align=center style="font-size:12px">评价模板B</div>

  ```text
  # 成交记录
  {'top':                                    price   volume
  000001.SZ 2019-02-15 09:35:00  11.034307  27800.0
            2019-02-18 09:35:00  11.216685   -300.0
            2019-02-19 09:35:00  11.372270   -100.0
            2019-02-20 09:35:00  11.402796    200.0
            2019-02-21 09:35:00  11.409945 -27600.0
  ...                                  ...      ...
  603999.SH 2021-05-31 09:35:00   5.690849  62000.0
            2021-06-01 09:35:00   5.849736  -1300.0
            2021-06-02 09:35:00   5.653068 -60700.0
            2021-06-03 09:35:00   5.627431  63700.0
            2021-06-04 09:35:00   5.567864 -63700.0
  
  [347918 rows x 2 columns],
  'longshort':                                    price   volume
  000001.SZ 2019-01-16 09:35:00  10.407035 -14200.0
            2019-01-17 09:35:00  10.310374   -100.0
            2019-01-18 09:35:00  10.422045  14300.0
            2019-01-28 09:35:00  11.022715 -13400.0
            2019-01-29 09:35:00  10.946211   -100.0
  ...                                  ...      ...
  603999.SH 2021-05-31 09:35:00   5.690849  42700.0
            2021-06-01 09:35:00   5.849736  -1300.0
            2021-06-02 09:35:00   5.653068 -41400.0
            2021-06-03 09:35:00   5.627431  43000.0
            2021-06-04 09:35:00   5.567864 -43000.0
  
  [655394 rows x 2 columns]}
  ```

#### 评价模板C
- 评价因子加权组合的表现
  - config.yaml文件
  ```text
  analyzer:
    evaluator_templete_C:
        class: 
            - evaluator_templete_C.py
            - EvalFactorWeighted
        
        data:
            pv:
                - meta_data
                - market_data__stock_cn__bar__1day
                - ../custom_universe.pkl
                - open,high,low,close,volume
                - 10

            meta:
                - meta_data
                - critic_data
                - ../custom_universe.pkl
                - is_szzs,is_hs300,is_zz500,is_kc50,is_halt,market_cap,circulating_market_cap
                - 10

        benchmark: [meta_data, market_data__stock_cn__bar__1day, 000300.SH]
  ```
  - evaluator_templete_C.py (略)
  - 评价结果

  ```text
                    alphaSharpe  alphaRtn  alphaVol   mdd%  mddDur    tr  \
  20190102-20191231        -0.06    -18.09      1.25  24.32   243.0  0.64   
  20200102-20201231        -0.05    -20.13      1.50  27.03   192.0  0.62   
  20210104-20211229         0.04     10.26      1.19   8.42   104.0  0.63   
  TOTAL                    -0.03    -27.86      1.32  40.16   727.0  0.63   

                    #holding    #long   #short    w/l   days    sh%  mktCap  \
  20190102-20191231    3474.0  1925.64  1548.36  49.14  244.0  37.50   -0.35   
  20200102-20201231    3474.0  1961.36  1512.64  48.82  243.0  36.36   -0.37   
  20210104-20211229    3474.0  1932.09  1541.91  48.87  241.0  36.06   -0.20   
  TOTAL                3474.0  1939.70  1534.30  48.95  728.0  36.64   -0.31   

                    bmCap  mktCapF bmCapF  hs300  zz500  sharpe    rtn   vol  \
  20190102-20191231  None    -0.36   None   7.81  23.53    0.06  11.20  0.80   
  20200102-20201231  None    -0.41   None   7.37  25.14    0.03   4.69  0.84   
  20210104-20211229  None    -0.73   None   7.98  23.94    0.08  12.29  0.61   
  TOTAL              None    -0.50   None   7.72  24.20    0.05  30.72  0.76   

                    mddP%  mddPDur  benchmark  sharpeB  volB  
  20190102-20191231  13.41    175.0      39.83     0.12  1.25  
  20200102-20201231   8.77    110.0      26.86     0.08  1.43  
  20210104-20211229   5.49     58.0      -6.57    -0.02  1.17  
  TOTAL              13.83    299.0      65.73     0.06  1.29  
  ```

  <div align=center>
  <img width="1000" src="pngs/evaluatorC.png"/>
  </div>
  <div align=center style="font-size:12px">评价模板C</div>

#### 评价模板D
- 包括IC分析、收益分析，以及分月度年度展示分析结果
  - config.yaml文件
  ```text
  analyzer:
      evaluator_templete_D:
          class:
              - evaluator_templete_D.py
              - EvalFull
          data: 
              pv: 
                  - meta_data
                  - market_data__stock_cn__bar__1day
                  - ../custom_universe.pkl
                  - open,high,low,close,volume
                  - 10
              meta:
                  - meta_data
                  - critic_data
                  - ../custom_universe.pkl
                  - is_hs300,is_zz500,is_st,is_halt,ind
                  - 10
          benchmark: [meta_data, market_data__stock_cn__bar__1day, 000300.SH]
  ```
  - evaluator_templete_D.py (略)
  - 评价结果
  
  <div align=center>
  <img width="1000" src="pngs/evaluatorD.png"/>
  </div>
  <div align=center style="font-size:12px">评价模板D</div>

#### 评价模板E
- 基于评价模板D，可以设置组合构建方式、加权方式、成交模式、股票过滤等，增加了归因分析，风格因子相关性分析
  - config.yaml文件
  ```text
  analyzer:
      SimpleAlphaEval:
          class:
              - evaluator/factor_board.py
              - FactorBoard
          universe: is_hs300 # 股票池
          benchmark: [meta_data, market_data__stock_cn__bar__1day, 000300.SH] # 基准
          portfolio: ls20p # 组合构建
          weighting: mkt_cap # 组合权重
          trade: close2close # 成交模式
          fees: # 手续费
              buy_cost_ratio: 0 # 买入手续费
              sell_cost_ratio: 0 # 卖出手续费
              slippage: 0 # 滑点
          filter: # 股票过滤
              skip_paused: True # 去除停牌
              skip_st: True # 去除ST
              skip_limit: True # 去除涨跌停
              skip_new: False # 去除次新股
  ``` 
  - factor_board.py文件 (略)
  - 评价结果
  
  <div align=center>
  <img width="1000" src="pngs/evaluatorE.png"/>
  </div>
  <div align=center style="font-size:12px">评价模板E</div>

## 3.5 因子研究全流程样例
- 一个完成的因子研究流程，包括因子计算和因子评价两部分
- 用户也可以只作因子计算（参见3.3.5节），或者只作库内因子评价（参见3.4.4节）
- 这里展示因子研究全流程
  - config.yaml文件

  ```text
  matrix:

      mode: signal
      span: [2019-01-01, 2021-12-30]
      universe: &universe custom_universe.pkl
      clock: '09:35:00'

      data:
          pv: 
              - meta_data
              - market_data__stock_cn__bar__1day
              - *universe
              - open,high,low,close,volume
              - 10
      
      save_signal: False
      show_report: True
      logging: True
          

  strategy:

      project_1_factor:
          class: 
              - strategy.py
              - ReverseSignal
      
  analyzer:
      SimpleAlphaEval:
          class:
              - evaluator.py
              - Eval
          data: 
              pv: 
                  - meta_data
                  - market_data__stock_cn__bar__1day
                  - *universe
                  - open,high,low,close,volume
                  - 10
              meta:
                  - meta_data
                  - critic_data
                  - *universe
                  - is_hs300,is_zz500,ind
                  - 10
  ```

  - evaluator.py (略)
  - run.ipynb文件

  ```python
  In:
    from transmatrix.workflow import run_matrix
    # 以yaml文件为入口运行回测 (对应terminal命令: Matrix -p projects/_project_show/project_1_单因子研究/config.yaml)
    matrix = run_matrix('config.yaml')
  ```

  - 评价结果

  ```text
  loading data market_data__stock_cn__bar__1day from datacache.
  loading data critic_data from datacache.

  ----------------------------------------------------------------------------------------------------
  stats
                                VALUE
  FIELD                              
  Factor                      reverse
  dates       2019-01-02 ~ 2021-12-30
  ICMean                     0.031482
  ICIR                       0.249599
  TopRetTol                  0.454296
  TopRetYL                   0.155794
  TopSharpYL                 0.643648
  TopMdd                    -0.426989
  LRetTol                    0.475388
  LSRetYL                    0.163028
  LSSharpYL                  0.587571
  LSMdd                     -0.108426
  ICMean_500                 0.020575
  ICIR_500                   0.136618
  ----------------------------------------------------------------------------------------------------
  history
                      top_nav_ser  top_dd_ser  ls_nav_ser  ls_dd_ser
  2019-01-02 09:35:00     0.991502   -0.008498    1.002249   0.000000
  2019-01-03 09:35:00     1.018063    0.000000    1.005035   0.000000
  2019-01-04 09:35:00     1.040050    0.000000    1.004872  -0.000164
  2019-01-07 09:35:00     1.040096    0.000000    1.008196   0.000000
  2019-01-08 09:35:00     1.049471    0.000000    1.014199   0.000000
  ...                          ...         ...         ...        ...
  2021-12-24 09:35:00     1.416735   -0.036902    1.457971  -0.006270
  2021-12-27 09:35:00     1.438744   -0.014894    1.474890   0.000000
  2021-12-28 09:35:00     1.442297   -0.011340    1.478908   0.000000
  2021-12-29 09:35:00     1.454296    0.000000    1.475388  -0.003520
  2021-12-30 09:35:00     1.454296    0.000000    1.475388  -0.003520

  [729 rows x 4 columns]
  ----------------------------------------------------------------------------------------------------
              IC        IR
  建筑装饰  0.045642  0.280128
  电子    0.031094  0.209733
  汽车    0.035918  0.253639
  家用电器  0.031129  0.171305
  公用事业  0.051869  0.281502
  综合    0.034798  0.166344
  商业贸易  0.033844  0.212871
  银行    0.026013  0.086420
  休闲服务  0.042460  0.179452
  轻工制造  0.023753  0.160983
  传媒    0.028063  0.177568
  非银金融  0.040242  0.185918
  纺织服装  0.033151  0.192176
  化工    0.028955  0.200796
  钢铁    0.027532  0.107244
  机械设备  0.034212  0.265870
  国防军工  0.052947  0.239787
  农林牧渔  0.026994  0.132846
  有色金属  0.030434  0.153119
  计算机   0.035262  0.247193
  采掘    0.043524  0.201118
  电气设备  0.034776  0.232861
  房地产   0.039043  0.238784
  医药生物  0.023895  0.156034
  通信    0.045999  0.262913
  建筑材料  0.035052  0.189073
  食品饮料  0.010009  0.049397
  交通运输  0.031728  0.184632
  ```

  <div align=center>
  <img width="1000" src="pngs/full_process.png"/>
  </div>
  <div align=center style="font-size:12px">因子研究全流程</div>
  <br />

## 3.6 因子批量研究
### 3.6.1 BathcMatrix
- 用于因子批量研究
  - 属性：
  >名称|类型|说明
  >----|----|----
  matrices|List|SignalMatrix组成的列表集合
  data_engine|DataEngine|数据查询引擎

  - load_data 加载各个SignalMatrix组件所订阅的数据
  - 参数：
    无
  - 返回：
    无

### 3.6.2 run_matrices
- 运行批量因子研究任务
  - 参数：
  >名称|类型|说明
  >----|----|----
  root|String|任务配置文件
  - 返回：
    无

### 3.6.3 运行模式
- 命令行运行
  - 以某一父级yaml文件作为入口（通过include加载单一因子）

    Matrix -p 2_include_task.yaml

  - 通过yaml文件配置批量任务

    BatchMatrix -p 3_workflow.yaml

- 代码运行
  - include模式：以某一父级yaml文件作为入口（通过include导入其他信息）

  ```python
  In:
    from transmatrix.workflow import run_matrix
    # 对应命令行 Matrix -p [config-path]
    mat = run_matrix('2_include_task.yaml')
  ```
  - 任务模式：通过yaml文件配置批量任务
  ```python
  In:
    from transmatrix.workflow import run_matrices
    # 对应命令行 BatchMatrix -p [project-path] -s span
    run_matrices('3_workflow.yaml')
  ```

### 3.6.4 yaml文件样例
#### include模式下yaml文件样例
```text
  # 引用其他yaml
  # 字段覆盖规则： 
      # 1: 任务入口文件具备最高优先级, i.e., 析出的配置中包含入口文件中的所有字段，任何被引用文件相应位置的信息都将被覆盖。
      # 2: include 多个文件时， 先引用的文件优先级高于后饮用的文件
  include: 
      - factor_A/config.yaml

  matrix:
      pta_backend: tqclient
      span : [2021-01-02, 2021-12-31]
      logging: True
```
#### 任务模式下yaml文件样例
```text
  # workflow 用于描述业务类型，目前支持 BatchMatrix (批量计算)， 后续支持OptimMatrix（参数寻优）
  workflow: BatchMatrix

  matrix:
      span: [2021-01-01,2021-12-31]
      logging: False


  # task 最大穿透目录层数 (defalult 为 1)
  max_child_level: 1

  # 任务流配置
  # task为两级列表
  # 第一级为batch，即每个元素代表一个批量任务，batch之间按照列表中前后顺序执行
  # 每个 batch 内包含多个字任务（每个任务指向一个config.yaml) , batch内的任务将并行执行。

  task:
      # batch 配置模式一: 
      # 以'regex '开头。利用正则表达式筛选符合条件的因子文件夹。
      # 具体而言，从当前入口文件所在目录递归地扫描子文件夹(os.walk)
      # 若某一级文件夹名称调用 re.compile('factor_[A|B]').search()返回True时，该文件夹下的config.yaml（若有）将被加入任务列表

      # batch 配置模式二:
      # 将各任务（因子文件夹相对于当前入口文件）的路径作为列表传入。
      - regex factor_[A|B]
      - 
          - factor_C
          - factor_D
```
