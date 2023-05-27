
### 基本研究流程

- <b> 构建策略 (Strategy) </b>
  - 订阅数据 
    - 从数据库或文件中获取数据 [ <b> Strategy.subscribe_data </b>]
  - 订阅因子 
    - 订阅其他策略对象 [ <b> Strategy.subscribe </b>]
    - 构建基于该对象消息的回调 [<b>  Strategy.callback </b>]
  - 添加定时器
    - 配置定时或定频任务 [<b> Strategy.add_scheduler </b>]
  - 编写策略逻辑
    - 类柜台交易接口 
    - 信号更新接口 
  
-  <b> 构建评价器 (Evaluator) </b>
  - 订阅评价数据
    - 从数据库或文件中获取数据 [<b> Evaluator.subscribe_data </b> ]
  - 编写评价逻辑
    - 计算评价指标 [ <b> Evaluator.critic </b>]
    - 评价结果展示 [ <b> Evaluator.show </b> ]
    - 上传评价结果 (仅在接入 TransQuant 平台时有效) [ <b> Evaluator.regist </b>] 
  
- <b> 配置回测信息 (Matrix) </b>
  - 设置回测时空范围 [ <b>span & codes </b>]
  - 配置市场和账户信息 [ <b> market </b>]
  - 注册策略和评价器 [ <b>Matrix.add_component </b>]
  - 运行回测 [ <b> Matrix.run </b>]
  - 运行评价并展示结果 [ <b> Matrix.eval </b>]



### 构建策略: Strategy

<b> 1. 数据订阅 </b>

在 init 函数中调用 [subscribe_data](3_接口说明/策略/generator.md#subscribe_data) 订阅数据 

```python
class MyStrategyA(Strategy):
    
	def init(self):
		self.subscribe_data(
			`attrname`, # 属性名称
			[`db_name`,`table_name`,`codes`,`fields`,`buffer`]
			# 数据库名，  数据表名，  标的代码集， 字段集， 缓冲窗口长度(天)
		)
```


<b> 2. 因子订阅 </b>

在 init 函数中:

1.调用 [subscribe](3_接口说明/策略/generator.md#subscribe) 订阅其他策略（因子）

2.调用 [callback](3_接口说明/策略/generator.md#generator-间的信息传递) 函数配置自定义回调函数

```python
class MyStrategyA(Strategy):

	def init(self):
		factor = MyStrategyB()
		self.f = self.subscribe(factor)
		self.callback(self.f['A'], self.my_callback_a)
		self.callback(self.f['B'], self.my_callback_b)

	def my_callback_a(self, msg):
		print(f'因子 f 发布消息消息 A: {msg}')

	def my_callback_b(self, msg):
		print(f'因子 f 发布消息消息 B: {msg}')
```

<b> 3. 添加定时器 </b>

在 init 函数中调用 [add_scheduler](3_接口说明/策略/generator.md#add_scheduler) 添加定时器

```python
class MyStrategyA(Strategy):

    def init(self):
        self.add_scheduler(milestones='10:00:00', self.my_callback_10)
		self.add_scheduler(milestones='14:00:00', self.my_callback_14)
	
	def my_callback_10(self):
		assert self.time.hour == 10 and self.time.minute == 0
	
	def my_callback_14(self):
		assert self.time.hour == 14 and self.time.minute == 0

```
<b> 4. 编写交易逻辑 </b>

在 [系统回调函数 或 自定义回调函数](3_接口说明/策略/3_接口说明/策略/strategy.md#系统回调函数) 中编写交易逻辑

```python
class MyStrategy(Strategy):

	def `callback`(self): 

		orders = self.pending_orders # 获取挂单信息 [link pending_orders]
		position = self.position # 获取持仓信息 [link position]
		
		# 买入指令: 价格、数量、开平、标的代码、市场代码
		self.buy(`price`,`volume`,`offset`,`code`,`market`)

		# 买入指令: 价格、数量、开平、标的代码、市场代码
		self.sell(`price`,`volume`,`offset`,`code`,`market`)

		# 撤单指令
		self.cancel_order(`order`) # [link order] 
```

### 构建评价器: Evaluator
 
<b> 1. 订阅评价数据 </b>

```python
class MyEvaluator(Evaluator):
	def init(self):
		self.subscribe_data(
			# 属性名	  # 数据库名， 数据表名， 标的代码集， 字段集，缓冲窗口长度(天)
            'benchmark', ['default', 'stock_index', '000300.SH', 'close', 0]
        )
```

<b> 2. 编写评价逻辑 </b>

```python
class MyEvaluator(Evaluator):
	def critic(self):
		self.trades = self.get_trade_table() # 获取交易记录 [link]
		self.stats = self.get_daily_stats()	# 获取各标的每日统计指标 [link]
		self.pnl = self.get_pnl() # 获取账户盈亏
		...
```
<b> 3. 编写可视化逻辑 </b>
   
```python
class MyEvaluator(Evaluator):
	  def show(self):
		  import pandas as pd
		  pd.series(self.pnl).plot()
		  ...
```


### 配置回测引擎：Matrix

<b> 使用流程 </b>

1.配置回测信息
```python
config = {
    'span': ['2021-01-01','2021-01-31'],
    'codes': ['000001.SZ','000002.SZ'],
}

matrix = Matrix(config)
```

2.添加策略
```python
from myProject import MyStrategyA, MyStrategyB

stra_a = MyStrategyA()
stra_b = MyStrategyB()
matrix.add_component(stra_a)
matrix.add_component(stra_b)
```

3.添加评价器

```python
from myProject import MyEvaluatorA, MyEvaluatorB

eval_a = MyStrategyA()
eval_b = MyStrategyB()
matrix.add_component(eval_a)
matrix.add_component(eval_b)
```

4.运行回测

```python
matrix.init() # 初始化回测引擎
matrix.run()  # 运行回测
matrix.eval() # 运行评价
```


