## Evaluator

Evaluator: 策略评价组件, 用户通过继承该组件实现评价逻辑。

用户可在 init 函数中订阅评价器需要的数据，

并通过实现 critic，show 方法实现评价结果计算和可视化。

若要将因子注册到TransQuant 策略面板，则需要复写 regist 方法。

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

#### regist

将回测结果注册到 TransQuant 平台策略面板。
在 self.kpis 中写入相应指标。具体说明详见 TransQuant 产品使用说明

```python

class MyEvaluator(Evalutro)

    def regist(self):
        self.kpis = {'年化收益': self.yearly_ret}

```




