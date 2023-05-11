## Matrix

 <b> 系统核心组件，功能包括： </b>

  - 配置回测信息
  - 处理其他组件 (e.g. Strategy / Evaluator / Scheduler .. )的订阅信息
  - 管理回测流程中的事件流
  - 执行回测和评价
  - 返回回测结果

#### 配置回测信息
```python
config = {
    'span': ['2021-01-01','2021-01-31'],
    'codes': ['000001.SZ','000002.SZ'],
}

matrix = Matrix(cfg)
```

#### 添加策略
```python
from myProject import MyStrategyA, MyStrategyB

stra_a = MyStrategyA()
stra_b = MyStrategyB()
matrix.add_component(stra_a)
matrix.add_component(stra_b)
```


#### 添加评价器

```python
from myProject import MyEvaluatorA, MyEvaluatorB

eval_a = MyStrategyA()
eval_b = MyStrategyB()
matrix.add_component(eval_a)
matrix.add_component(eval_b)
```

#### 运行回测

```python
matrix.init() # 初始化回测引擎
matrix.run()  # 运行回测
matrix.eval() # 运行评价

```








SignalMatrix和SimulationMatrix的基类。

#### 属性：

>| 名称            | 类型       | 说明                                                         |
>| -------------- | ---------- | ------------------------------------------------------------ |
>| strategies     | Dict       | strategy字典，key为名称，value为SignalStrategy或SimulationStrategy |
>| sub_strategies | Dict       | 订阅的其他strategy字典，key为名称，value为SignalStrategy或SimulationStrategy |
>| all_strategies | Dict       | strategies和sub_strategies的集合                             |
>| evaluators     | Dict       | evaluator字典，key为名称，value为SignalEvaluator或SimulationEvaluator |
>| schedulers     | Dict       | 任务调度器字典                                               |
>| context        | List或Dict | 环境变量                                                     |
>| modules        | Dict       | 挂载的模组字典，包括策略组件、评价组件等                     |
>| datasets       | Dict       | 订阅数据集字典                                               |

#### 方法

- init 

  - 函数作用：组件初始化（数据加载，配置因子计算组件，因子评价组件等等）
  - 参数：无
  - 返回：无

- run 

  - 函数作用：运行因子计算或回测计算
  - 参数：无
  - 返回：无

- eval 

  - 函数作用：遍历evaluators，分别评价因子
  - 参数：无
  - 返回：无

- add_component 

  - 函数作用：组件初始化（数据加载，配置因子计算组件，因子评价组件等等）

  - 参数：

    >| 名称      | 类型                                              | 说明         |
    >| --------- | ------------------------------------------------- | ------------ |
    >| component | SignalStrategy, SimulationStrategy, BaseEvaluator | 要添加的组件 |

  - 返回：无

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

### 1.1.2 SignalMatrix

继承自BaseMatrix，因子研究引擎的基类。

#### 属性：

>| 名称   | 类型 | 说明     |
>| ------ | ---- | -------- |
>| config | Dict | 配置字典 |
>| type   | str  | 'signal' |

#### 方法：

- show_report

  - 函数作用：遍历evaluators，分别运行show函数，展示评价作图
  - 参数：无
  - 返回：无
- save_signal

  - 函数作用：遍历strategies，分别运行show函数，展示评价作图
  - 参数：无
  - 返回：无


#### 配置方式：

- yaml文件配置

```text
# 因子引擎组件 [signal模式]

matrix:

    mode: signal
    span: [2019-01-01, 2021-12-30]
    codes: &universe ../../../custom_universe.pkl
    
    show_report: False
```



### 1.1.3 SimulationMatrix

继承自BaseEvaluator，策略评价组件的基类

- 继承此类后，用户可自行用户可自行编写评价逻辑。

#### 属性：

>| 名称    | 类型 | 说明                            |
>| ------- | ---- | ------------------------------- |
>| config  | Dict | 配置字典                        |
>| type    | str  | 'simulation'                    |
>| markets | Dict |                                 |
>| modules | Dict | strategies, evaluators和markets |

#### 方法：

同BaseMatrix。


#### 配置方式：

- yaml文件配置

```
# 回测引擎组件组件 [simulation]

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
```

