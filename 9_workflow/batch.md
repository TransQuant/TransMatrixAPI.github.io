
### 通过yaml文件配置任务流

系统支持通过 yaml 文件配置任务流。

一个任务流包含多个顺序执行的批任务，每个批任务中包含多个可并行子任务。

每个子任务为一个标准的回测任务，包含名为 config.yaml 的入口配置文件。

通过 BatchMatrix -p [config_path] 或 transmatrix.workflow.run_matrices 函数运行任务。

---

任务流工程文件结构示意：
```
taskflow
├── evaluator.py
├── factor_A
│   ├── config.yaml
│   └── strategy.py
├── factor_B
│   ├── config.yaml
│   └── strategy.py
├── factor_C
│   ├── config.yaml
│   └── strategy.py
├── factor_D
│   ├── config.yaml
│   └── strategy.py
└── taskflow.yaml
```
---

### 配置文件书写标准

一个可执行的任务流配置文件包含模式参数、公有信息、任务信息三部分

---

<b> 模式参数 </b> ：
- workflow: 填入 'BatchMatrix' 提示系统进入任务流模式
- max_child_level: 子任务搜寻最大穿透目录层数 (defalult 为 1)

---

<b> 公有信息：</b>

公有信息可以是[标准配置文件](6_参数配置/configer.md)中 matrix / strategy / evaluator 中的任何信息，
其将覆盖子任务相应为之的配置信息（机制同 [include](6_参数配置/configer.md#引用其他配置文件) ）。


---

<b> 任务信息：</b>

<b> 通过 task 字段配置任务信息 </b>
```
task 为两级列表
第一级为 batch，每个元素代表一个批量务，batch 之间按照列表中前后顺序执行
每个 batch 内包含多个子任务（每个任务指向一个config.yaml）, batch内的任务将并行执行。
```


<b> 通过 batch 字段配置批任务信息 </b>

batch 支持正则表达式和相对路径列表两种模式


<b> 正则表达式 </b>:
```
以'regex '开头, 其余内容为正则表达式对象(记作RE)
从当前入口文件所在目录递归地扫描子文件夹
若某一级文件夹名称调用 re.compile(RE).search()返回 True 且该文件夹下存在 config.yaml, 则将被加入任务列表。
```

<b> 相对路径 </b>: 将各任务（因子文件夹相对于当前入口文件）的路径作为列表传入。


---

### 配置文件示例

```yaml
# in taskflow.yaml             
workflow: BatchMatrix               # 指定系统进入任务流模式

matrix:                             # 配置公有信息
    span: [2021-01-01,2021-12-31]   # 指定所有子任务时间区间

max_child_level: 1                  # task 最大穿透目录层数 (defalult 为 1)

task:
    - regex factor_[A|B]            # 正则表达式配置批任务
    - 
        - factor_C                  # 相对路径列表配置批任务
        - factor_D
```


