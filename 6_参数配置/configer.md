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

#### 引用其他配置文件

通过 include 字段引用其他 yaml 文件

逻辑如下:

main.yaml:
```
matrix:
  - span [2021-01-01, 2021-12-31]
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
  - 

---
