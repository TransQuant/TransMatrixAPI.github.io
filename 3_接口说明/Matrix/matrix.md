## Matrix

 <b> 系统核心组件，功能包括： </b>

  - 配置回测信息
  - 处理其他组件 (e.g. Strategy / Evaluator / Scheduler .. )的订阅信息
  - 管理回测流程中的事件流
  - 执行回测和评价
  - 返回回测结果

---

#### 配置回测信息

- 必须参数:
  - span : List[Union[str, datetime]], # 回测时间段
  - codes : Union[List, str], # 回测标的
  - market : Dict[str, Dict]
    - key: 市场名 (若为股票市场，请以 'stock' 开头)
    - value:
      - Dict:
        - data (List): [`db_name`,`table_name`]
        - matcher (str, Optional): daily/bar / tick或orderflow指定撮合器（若不提供则根据 table_name 推断）。
        - account (str): base / detail，base为基础账户，不做验资验券；detail账户将根据市场属性进行验资验券。 若不提供改字段，则采用 detail模式。
- 可选参数:
  - fee_rate (float): defaults to 0.
  - ini_cash (float): defaults to 10000000.
  - universe (list): 配置动态票池.
  - context  (list or dict): 自定义参数, Strategy 和 Evaluator 注册后可通过 .matrix_context 获取。

- 代码示例

```python
# transmatrix 支持 字典 和 配置文件传参两种模式对回测进行配置。
# 此处以字典模式为例
config = {
    'span': ['2021-01-01','2021-01-31'],
    'codes': ['000001.SZ','000002.SZ'],
    'market': {
        'stock':{
            'data': ['common','stock_bar_daily'],
            'matcher': 'daily',
            'account': 'detail',
        },
    'fee_rate': 0,
    'ini_cash': 1000000
    },
}
from transmatrix import Matrix
matrix = Matrix(config)
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


