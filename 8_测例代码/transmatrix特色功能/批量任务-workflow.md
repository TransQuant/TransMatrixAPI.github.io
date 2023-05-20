### 测例说明
本测例展示了因子批量研究的流程，TransMatrix框架支持对多个因子作批量研究，包括2种模式：
- include模式：以某一父级yaml文件作为入口（通过include导入其他信息）
- workflow模式：通过yaml文件配置批量任务

### 基本研究流程
- <b> 编写各个因子的研究流程 </b>
  - 配置config.yaml文件
    - 以factor_A为例


```text
matrix:

    mode: signal
    span: [2019-01-01, 2021-12-31]
    codes: &universe ../custom_universe.pkl
    check_codes: False

    context:
        long  : 25
        short : 12
        diff  :  9

    save_signal: batch_insert
    

strategy:

    factorA:
        class: 
            - strategy.py
            - ReverseSignal

    # 可配置多个策略

evaluator:
    SimpleAlphaEval:
        class:
            - ../evaluator.py
            - EvalFull
```

  - 编写 因子计算逻辑
    - 以factor_A为例，编写strategy.py

```python
from scipy.stats import zscore
from transmatrix.strategy import SignalStrategy
from transmatrix.data_api import create_data_view, NdarrayData, DataView3d, DataView2d

class ReverseSignal(SignalStrategy):
    def init(self):
        # 订阅因子计算所需要的数据
        self.subscribe_data(
            'pv', ['default','stock_bar_1day',self.codes,'open,high,low,close', 10]
        )
        self.pv: DataView3d
        self.add_clock(milestones='09:35:00') # 添加计时器，09:35:00触发因子计算

    def pre_transform(self):
        # 实现因子计算逻辑，这里向量化计算，效率更高
        if 'reverse' not in self.pv.fields:
            pv = self.pv.to_dataframe()
            ret = (pv['close'] / pv['close'].shift(1) - 1).fillna(0) # 计算日度收益率
            reverse = -ret.rolling(window = 5, min_periods = 5).mean().fillna(0) # 计算5日均值
            reverse = zscore(reverse, axis = 1, nan_policy='omit') # 因子截面标准化
            self.reverse: DataView2d = create_data_view(NdarrayData.from_dataframes(reverse)) # 将因子数据转换为DataView2d
            self.reverse.align_with(self.pv) # 与原始数据对齐
            
    def on_clock(self):
        self.update_signal(self.reverse.get()) # 定时更新因子数据
```

- <b> 编写include_task.yaml </b>
  - 对应include模式

```text
# 引用其他yaml
# 字段覆盖规则： 
    # 1: 任务入口文件具备最高优先级, i.e., 析出的配置中包含入口文件中的所有字段，任何被引用文件相应位置的信息都将被覆盖。
    # 2: include 多个文件时， 先引用的文件优先级高于后引用的文件
include: 
    - factor_A/config.yaml

matrix:
    span : [2019-01-01, 2021-12-31]
    # logging: True
```
- <b> 编写workflow.yaml </b>
  - 对应workflow模式


```text

# workflow 用于描述业务类型，目前支持 BatchMatrix (批量计算)， 也支持OptimMatrix（参数寻优）
workflow: BatchMatrix

matrix:
    span: [2021-01-01,2021-12-31]
    logging: True

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

- <b> 运行入口 </b>
  - 运行include模式

```python
In:
    from transmatrix.workflow.run_yaml import run_matrix
    # 对应命令行 Matrix -p [config-path]
    mat = run_matrix('2.include_task.yaml') # 以某一父级yaml文件作为入口（通过include导入其他信息）
```

```Text
Out:
    loading data common__stock_bar_1day__open,high,low,close from database.

    loading data common__critic_data__is_hs300,is_zz500,ind from database.

    loading data common__stock_index__close from database.

    Cashing common__stock_bar_1day__open,high,low,close to pickle file: dataset_77bb1c24-36ef-4bac-8a3d-badbb126458f ....Cashing common__critic_data__is_hs300,is_zz500,ind to pickle file: dataset_c5f27637-db16-4fb6-b31c-35f2833d18d8 ....

    Cashing common__stock_index__close to pickle file: dataset_2f864455-c8af-4333-80ee-17a96ee7370c ....
    开始因子评价
    ----------------------------------------------------------------------------------------------------
    数据规整: 0.1235秒
    因子覆盖度 0.0046秒
    每日IC 0.7976秒
    每日超额 0.6786秒
    IC统计 0.0131秒
    月度IC和超额 0.0134秒
    分行业IC计算 0.0749秒
    分行业IC分年度 0.0743秒
    ic衰减 0.1457秒
    top组超额 0.2201秒
    完成因子评价
    ----------------------------------------------------------------------------------------------------
    saving report to /root/workspace/我的项目/功能演示/transmatrix特色功能/批量任务-workflow/批量任务/report
```

<div align=center>
<img width="1000" src="8_测例代码\pics\批量任务.png"/>
</div>
<div align=center style="font-size:12px">include模式</div>
<br />

```text
Out:
    factorA: saving signal factorA to batch_insert....
    因子库数据更新: xwq1_private batch_insert : ['factora']
    更新完毕: xwq1_private batch_insert : ['factora']
```

  - 运行workflow模式
```python
In:
    from transmatrix.workflow.run_batch import run_matrices
    # 对应命令行 BatchMatrix -p [project-path] -s span
    run_matrices('3.workflow.yaml')
```

```text
Out:
    2023-05-19 16:32:39.204721: 批量任务开始:
    loading data common__critic_data__is_hs300,is_zz500,ind from datacache.
    loading data common__critic_data__is_hs300,is_zz500,ind from datacache.
    loading data common__stock_bar_1day__open,high,low,close from datacache.

    loading data common__stock_index__close from datacache.

    loading data common__stock_index__close from datacache.
    loading data common__stock_bar_1day__open,high,low,close from datacache.


    saving report to /root/workspace/我的项目/功能演示/transmatrix特色功能/批量任务-workflow/批量任务/factor_B/report
    saving report to /root/workspace/我的项目/功能演示/transmatrix特色功能/批量任务-workflow/批量任务/factor_A/report
    factorA: saving signal factorA to batch_insert....
    factorB: saving signal factorB to batch_insert....
    因子库数据更新: xwq1_private batch_insert : ['factora']
    因子库数据更新: xwq1_private batch_insert : ['factorb']
    更新完毕: xwq1_private batch_insert : ['factora']
    更新完毕: xwq1_private batch_insert : ['factorb']
    loading data common__stock_bar_1day__open,high,low,close from datacache.
    loading data common__critic_data__is_hs300,is_zz500,ind from datacache.
    loading data common__stock_index__close from datacache.

    loading data common__stock_bar_1day__open,high,low,close from datacache.
    loading data common__critic_data__is_hs300,is_zz500,ind from datacache.

    loading data common__stock_index__close from datacache.

    saving report to /root/workspace/我的项目/功能演示/transmatrix特色功能/批量任务-workflow/批量任务/factor_D/report
    saving report to /root/workspace/我的项目/功能演示/transmatrix特色功能/批量任务-workflow/批量任务/factor_C/report
    factorD: saving signal factorD to batch_insert....
    factorC: saving signal factorC to batch_insert....
    因子库数据更新: xwq1_private batch_insert : ['factord']
    因子库数据更新: xwq1_private batch_insert : ['factorc']
    更新完毕: xwq1_private batch_insert : ['factord']
    更新完毕: xwq1_private batch_insert : ['factorc']
    2023-05-19 16:32:58.666262: 批量任务完成。
```