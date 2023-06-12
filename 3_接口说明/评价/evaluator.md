## [Evaluator](8_测例代码\因子服务-因子分析.md)

Evaluator: 策略评价组件, 用户通过继承该组件实现评价逻辑。

用户可在 init 函数中订阅评价器需要的数据，

并通过实现 critic，show 方法实现评价结果计算和可视化。

若要将因子注册到TransQuant 策略面板，则需要复写 regist 方法。

#### \__init__

<b> 子类的参数注册接口 </b>

```python
class MyEvaluator(Evaluator):

    def __init__(self, w, b):
        super().__init__(w, b)

a = MyEvaluator(3, 2)
b = MyEvaluator(w = 3, b = 2)
assert a.w == b.w == 3
assert a.b == b.b == 2

args = [3,4]
kwargs = {'w':3, 'b':4}

d = MyEvaluator(*args)
e = MyEvaluator(**kargs)

assert d.w == e.w == 3 and d.b == e.b == 4
```


#### init

init方法主要用于订阅评价要用到的数据，如基准收益率、股票行业信息等。

以下述代码为例，MyEvaluator 订阅了 000300.SH 的收盘价格，属性名称为 benchmark,

在回测引擎完成初始化后， MyEvaluator 实例可通过 .benchmark 获取该数据。

```python
class MyEvaluator(Evaluator):
	def init(self):
		self.subscribe_data(
			# 属性名	  # 数据库名， 数据表名， 标的代码集， 字段集，缓冲窗口长度(天)
            'benchmark', ['default', 'stock_index', '000300.SH', 'close', 0]
        )
```

#### critic

在回测交易完成后被调用。用户在该方法中编写评价计算逻辑。

```python
import pandas as pd
class MyEvaluator(Evaluator)
    def critic(self):
        # 计算账户累计收益
        self.nav = (pd.Series(self.get_pnl()).cumsum() + self.ini_cash) / self.ini_cash
        self.ret = (self.nav / self.nav.shift(1) - 1).fillna(0)
        self.yearly_ret = self.ret.mean() * 250
```


#### show
```python
class MyEvaluator(Evaluator)
    def show(self):
        # 展示账户累计收益
        self.acc_pnl.plot()
```

关于可视化模块的使用，详见[**可视化**](7_可视化模块/plot.md)。

#### regist

将回测结果注册到 TransQuant 平台策略面板。
在 self.kpis 中写入相应指标。具体说明详见 TransQuant 产品使用说明。

> 注意：Matrix配置信息中 backend 为 tqclient 时，Evaluator.regist() 注册的kpi指标才会显示在前端，否则需要通过 .kpis 属性获得。

```python

class MyEvaluator(Evaluator)

    def regist(self):
        self.kpis = {'年化收益': self.yearly_ret}

```



