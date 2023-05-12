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


