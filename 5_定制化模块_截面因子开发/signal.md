## [Signal 模式](8_测例代码\策略服务-回测场景支持\因子选股)

基于 TransMatrix 基础组件（Matrix, Generator, DataApi，Scheduler等）开发的一套截面因子研究框架。

包含 SignalMatrix, SignalStrategy 和 SignalEvaluator 三个模块。

与基础框架相比主要特点为：

- 将报撤单接口替换为信号更新接口。
- 添加了评价数据与信号数据自动对齐机制。

---

### SignalMatrix

Signal模式与[普通交易模式](3_接口说明/Matrix/matrix.md)的使用流程基本相同。

#### 配置回测信息

必须参数:
- span : List[Union[str, datetime]], # 回测时间段
- codes : Union[List, str], # 回测标的

可选参数:
- universe (list): 配置动态票池.
- context  (list or dict): 自定义参数, Strategy 和 Evaluator 注册后可通过 .matrix_context 获取。
- backend (str): 控制评价展示的输出方式（包括可视化和回测kpi指标），'ipython' 指在notebook显示，'tqclient' 指在客户端显示。


```python
# SignalMatrix 无需配置 market, fee_rate, ini_cash 等交易相关字段。
config = {
    'span': ['2021-01-01','2021-01-31'],
    'codes': ['000001.SZ','000002.SZ'],
}
from transmatrix import SignalMatrix
matrix = SignalMatrix(config)
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
---

### SignalStrategy

与基础模式下的 [Strategy](3_接口说明/策略/strategy.md)一样，
SignalStrategy 也是 [Generator](3_接口说明/策略/generator.md) 的子类，可调用[订阅数据](3_接口说明/策略/generator.md#subscribe_data)、[订阅因子](3_接口说明/策略/generator.md#subscribe)、[添加定时器](3_接口说明/策略/generator.md#add_scheduler)、[注册信息流、发布信息、构建自定义回调。](3_接口说明/策略/generator.md#generator-间的信息传递)等接口。

此外，SignalStrategy 还包含以下特殊接口：

---

#### add_clock

<b> 在 init 函数中调用，添加因子更新定时器 </b>

用于注册 on_clock 函数对应的回调时点。

参数与 [Generator.add_scheduler](3_接口说明/策略/generator.md#add_scheduler) 一致。

每个SignalStrategy只允许存在一个clock（底层为定时器scheduler）, 将决定策略因子和信号的更新时点。

<b> 参数 </b>：
- scheduler (BaseScheduler, optional): [定时器实例](). Defaults to None.
- milestones (List[str], optional): 时间列表（[定时任务]()）. Defaults to None.
- freq (timedelta, optional): 回调频率（[定频任务]()）. Defaults to None.
- with_data (str, optional): 数据订阅对应的属性名(按某一[订阅数据]()触发回调). Defaults to None.
- handler (Callable): 回调函数。

注意：scheduler，milestones，freq，with_data 有且只有一个有效。

---

#### create_factor_table

<b> 在 init 函数中调用，注册因子表 </b>

注册后系统会生成一个字典用于存储因子数据 (self.facor_data)

key 为因子名称，value 为一个基于 clock 时间的 [2D数据视图](3_接口说明/数据模型/set_model_view#DataView2d), 每个数据视图的列名为 codes。

用户可在 on_clock 函数中通过 self.factor_data 获得数据视图，并通过 update_factor 更新数据。

<b> 参数 </b>: factor_names (List[str] 或 str) 因子名称（列表）

---

#### update_factor

<b> 在 on_clock 函数中调用，更新因子数据 </b>

<b>  参数: </b>
- name (str): 因子名称
- value (float): 因子值

---

#### signal (属性)

用于存储策略生成的交易信号。

交易信号指的是经过简单处理即可转化成持仓的数据。

<b>  返回值: </b>

- Dict
  - key（timestamp）: 时间
  - value (float): 信号数据

---

#### update_signal

<b> 在 init 函数中调用，更新信号数据 </b>

- 参数: 
    - value (float): 信号数据

---

#### save_factors

<b> 将因子数据存入数据库 </b>

若数据库中不存在与因子名称相同的列， 则创建该列并插入数据。

若数据库中已存在该列，则直接插入数据。

若新数据与原数据在 datetime, code 列下有交集，则覆盖原数据重合部分。

- <b> 参数 </b>: 
  - table_name (str): 表名

---

#### save_signal

<b> 将信号数据存入数据库 </b>

机制与save_factors 相同。

- <b> 参数 </b>: 
  - table_name (str): 表名
  - name (str): 信号名称

---

#### 系统回调函数

<b> on_clock </b>

基于 clock 时点的回调函数， 用于编写因子和信号计算逻辑

<b> pre_transform </b>

对订阅数据进行向量化计算 

`注意:`
- 向量化预计算仅适用于回测，用于快速验证交易逻辑。
- TransMatrix实盘交易系统中不存在与pre_transform对应的接口。

<b> post_transform </b>

对生成的因子或信号数据向量化计算


#### 代码示例

```python
from transmatrix import SignalStrategy
from transmatrix.data_api import DataView3d
import numpy as np

class MacdSignal(SignalStrategy):
    def init(self):
        self.add_clock(milestones='09:35:00') # 9:35:00 触发
        self.subscribe_data( 
            'pv', ['*','stock_bar_daily',self.codes,'close', 30] # 订阅 close 数据
        )
        self.create_factor_table(['dif', 'dea']) # 创建 dif 和 dea 两个因子
        self.pv: DataView3d # pv 为 3d 数据视图         
    
    def on_clock(self):
        
        sma26 = np.nanmean(self.pv.get_window('close', 26), axis = 0) # 计算 26 日均线
        sma12 = np.nanmean(self.pv.get_window('close', 12), axis = 0) # 计算 12 日均线
        
        dif = sma12 - sma26 # 计算 dif
        self.update_factor('dif', dif) # 更新 dif 因子
        
        dea = np.nanmean(self.factor_data.get_window('dif', 9), axis = 0) # 计算 dea
        self.update_factor('dea', dea) # 更新 dea 因子
        
        self.update_signal(2*(dif - dea)) # 更新信号(macd)
```
---

### SignalEvaluator

SignalEvaluator 与 [基础评价器](3_接口说明/评价/evaluator.md)使用流程一致。

用户可在 init 函数中订阅评价器需要的数据，

并通过实现 critic，show 方法实现评价结果计算和可视化。

若要将因子注册到TransQuant 策略面板，则需要复写 regist 方法。

#### 数据对齐

数据对齐是Signal模式的核心特性。

在评价开始前，评价器订阅的所有数据都将按照如下规则 与 clock 时间戳对齐:

<b> 1.对于 clock 中的时点 t </b>:
- 若数据中存在时点 t，则将该条数据与 t 配对。
- 若数据中不存在时点 t，则将数据中时间 t 之后的第一条数据与 t 配对 (时间戳修改为 t)。

<b> 2.保留配对数据，剔除其他数据。</b>

上述对齐机制将确保每个订阅数据与clock的时间戳一致。

