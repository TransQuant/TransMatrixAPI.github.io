#### 研究工程

TransMatrix 中的一个研究工程类似于一个代码工程目录。

目录下可以包含多个研究项目， 每个子项目可以包含一份或多份 Strategy / Evaluator 的代码。

系统允许以配置文件作为入口配置回测。

配置文件支持 pkl / py / pyc 等文件识别与读取。

配置文件之间支持通过 include 关键字实现引用。

---

#### 配置文件书写标准

文件采用 [yaml](https://www.runoob.com/w3cnote/yaml-intro.html) 语言编写。

一个可运行的 yaml 文件应包含以下字段:

- matrix: 用于配置回测信息。
  - 内容标准参照 [Matrix](3_接口说明/Matrix/matrix.md#配置回测信息) / [SignalMatrix](5_定制化模块_截面因子开发/signal.md#配置回测信息) 参数配置。
  - 此外，需提供 mode 字段，传入 simulation 表示基础模式，传入 signal 表示截面因子开发模式。

- strategy:
  - name: # 策略名称
  
    `# 通过 class 指定策略代码`

    - class: 
      - `strategy_path` # 策略代码文件的相对路径 (以.py/.pyc 结尾)
      - `strategy_cls_name` # 策略类名称 （策略类名称）
  
    `# 通过 args / kwargs `[配置参数](3_接口说明/策略/generator.md#\__init__)
    - args: 
      - ... 列表参数
    - kwargs
      - ... 字典参数

- evaluator:
  - name: # 评价器名称
  
    `# 通过 class 指定评价器代码`

    - class: 
      - `strategy_path` # 评价器代码文件的相对路径 (以.py/.pyc 结尾)
      - `strategy_cls_name` # 评价器类名称 （策略类名称）
  
    `# 通过 args / kwargs `[配置参数](3_接口说明/策略/generator.md#\__init__)
    - args: 
      - ... 列表参数
    - kwargs
      - ... 字典参数
  
--- 

配置文件示例

```yaml
# in config.yaml 
matrix:                                     # 配置回测信息

    mode: simulation                        # 指定模式 [simulation 或 signal]
    span: [2021-01-01, 2021-12-31]          # 指定起止时间 (日期 或 时间戳)
    codes: &universe custom_universe.pkl    # 同级目录下的 custom_universe.pkl 作为标的资产池
    
    market:                                 # 配置市场信息
        stock:                              # 市场名称: 国内股票市场 [名称应以 stock 开头]
            data: [common, stock_bar_daily] # 配置市场数据 [数据库名，数据表名]
            matcher: daily                  # 配置撮合器 如不提供，则根据表名中是否包含 bar/tick/order/daily 等关键字识别
            account: detail                 # 账户配置可选 detail / base


strategy:                                   # 配置策略信息

    test_strategy:                          # 策略名称
        class:                              # 策略文件和策略代码
            - ../strategies/strategy.py     # 通过相对路径指配置策略代码文件 strategy.py
            - TestStra                      # 策略类
        args: [3,5]                         # 配置参数


evaluator:                                  # 配置评价器信息 (若不提供，则不进行策略评价)
    test_eval:                              # 评价器名称
        class:
            - ../evaluators/evaluator.py    # 通过相对路径配置评价器码文件 strategy.py
            - TestEval                      # 评价器类
        kwargs:                             # 配置参数
            benchmark: '000300.SH'
```


#### 执行回测

系统支持 命令行 和 函数两种方式执行配置文件
 
命令行: Matrix -p [yaml_path]

函数执行:
```python
from transmatrix.workflow import run_matrix
matrix = run_matrix(yaml_path)
``` 
  
  

#### 引用其他配置文件

通过 include 字段引用其他 yaml 文件

更新规则:

逐级扫描被引用文件的 key 和 value，
- 如果主文件相应层级下不存在相同的key，则 value 会被并入配置。
- 如果主文件相应层级下存在相同的key，则 value 不会被并入配置（以主文件为准）。




---
代码示例：

合并 main.yaml 和 sub.yaml 的内容

main.yaml:
```
matrix:
  - code [000001.SZ, 000002.SZ]

strategy:
  - strategy1:
     - class
       - strategy.py
       - test_strategy

include: sub.yaml
```

sub.yaml
```
matrix: 
  - span: [2020-01-01, 2021-12-31]
strategy: 
  - strategy1:
     - args: 10
```

---


以上配置等价于 ：
```
matrix:
  - span [2020-01-01, 2021-12-31]  # sub.yaml 中的 matrix:span 被并入
  - code [000001.SZ, 000002.SZ]    # main.yaml 里 存在 matrix:code 字段，以 main.py 为准。
  
strategy:
  - strategy1:
     - class
       - strategy.py
       - test_strategy
     - args: 10                    # sub.yaml 中的 strategy:strategy1:args 被并入
```

---