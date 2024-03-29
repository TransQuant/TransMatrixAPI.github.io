# Generator

Generator 是 TransMatrix 系统的主要开发接口。

它是 [Strategy](3_接口说明/策略/strategy.md) 和[SignalStrategy](5_定制化模块_截面因子开发/signal.md)的基类，也可被用户直接继承，用来实现因子计算或交易逻辑。 



## 属性列表

| 名称                | 类型                        | 说明                                                         |
| ------------------- | -------------------------- | ------------------------------------------------------------ |
| time                | datetime                   | 回测引擎当前时间                                                         |
| codes               | List                       | 股票集合 (在 Matrix 中配置)                                           |
| massages            | Dict[str, str]             | 已注册的信息                                                      |
| subscribe_data_info | Dict[str, List]            | 数据订阅信息                                                       |
| sub_generators      | Dict[str, 其他strategy]     | 因子订阅信息                                                       |
| key                 | str                        | 实例 id



## 方法
#### \__init__

<b> 子类的参数注册接口 </b>

TransMatrix 系统根据类名和其参数确定 Generator 子类实例的key，系统通过key来保证Generator对象的全局唯一性。 

若一个Generator实例在[注册](#subscribe)时系统中已存在与之相等（key相同）的对象，则该实例的订阅者将获得系统中已注册的实例（而非订阅者构造的实例本身）。

```python
class MyGenerator(Generator):

    def __init__(self, w, b):
        super().__init__(w, b)

# a, b, c等价且相同
a = MyGenerator(3, 2)
b = MyGenerator(w = 3, b = 2)
c = MyGenerator(3, b = 2)
assert a == b == c
assert a.key == b.key == c.key == '__main__.MyGenerator(3,2)'
assert a.w == b.w == c.w == 3
assert a.b == b.b == c.b == 2

args = [3,4]
kwargs = {'w':3, 'b':4}
# d, e等价且相同
d = MyGenerator(*args)
e = MyGenerator(**kargs)

assert d == e
assert d.w == e.w == 3 and d.b == e.b == 4


```



#### init

<b> 初始化接口 </b>

主要功能: [订阅数据](#subscribe_data)、[订阅因子](#subscribe)、[添加定时器](#add_scheduler)、[注册信息流、发布信息、构建自定义回调。](#generator-间的信息传递)

子类必须实现该方法
```python
class MyGenerator(Generator):

    def init(self):
        self.subscribe_data(...)
        self.subscribe(...)
        self.add_scheduler(...)
        self.callback(...)
        self.add_message(...)
```



#### subscribe_data

<b> 数据订阅接口 </b>

<b> 参数 </b>:

- name (str): 属性名称
- dataset_describe (list): 数据信息，元素依次为：
  - db_name: 数据库名 或 'file'
  - table_bame: 表名 或 [file_path]
  - codes : 代码列表 e.g. '000001.SZ, 000002.SZ...'
  - fields : 字段列表 e.g. 'open,high,low,close...'
  - lag: 
    - 若为量价数据，则传入整数，含义为缓冲期长度（天）。系统会将回测开始时间前推
    - 若为财报数据，则传入'3Q','1Y' ... 等，系统将按报告期生成滞后字段
    
  - category: 
    - 若为A股财报数据，则填入'finance-report' (describe 长度为 6)
    - 若为其他数据，则不提供该字段 (describe 长度为 5)

```python
class MyGenerator(Generator):

    def init(self):
        self.subscribe_data(
            'pv': 
            [
                'meta_data', # db_name
                'stock_bar_1day', # table_name
                '000001.SZ,000002.SZ', # codes
                'open,close,volume', # fields
                10 # lags
            ]
        )

    def my_callback(self):
        volume = self.pv.get('000001.SZ','volume')
        print(self.time, f'当前 000001.SZ 的 volume 为 {volume}')
```



#### subscribe

<b> 订阅另一个 Generator。</b>

若系统中已存在，则返回系统中的实例（保证唯一性），
若不存在，则将传入的实例加入系统。

<b> 参数 </b>: other (Generator): Generator实例


<b> 返回值 </b>: registed_generator (Generator): 注册后的 Generator 实例

```python
class MyGeneratorA(Generator):

    def init(self):
        b = MyGeneratorB()
        self.b = self.subscribe(b)
```



#### add_scheduler

<b> 添加定时器 </b>

<b> 参数 </b>：
- scheduler (BaseScheduler, optional): [定时器实例](). Defaults to None.
- milestones (List[str], optional): 时间列表（[定时任务]()）. Defaults to None.
- freq (timedelta, optional): 回调频率（[定频任务]()）. Defaults to None.
- with_data (str, optional): 数据订阅对应的属性名(按某一[订阅数据]()触发回调). Defaults to None.
- handler (Callable): 回调函数。

> 注意：scheduler，milestones，freq，with_data 有且只有一个有效。

<b> 返回值 </b>：registed_scheduler (scheduler) 注册后的 scheduler 实例。


```python
class MyGenerator(Generator):

    def init(self):
        self.add_scheduler(
            milestons = ['10:00:00','14:00:00'],
            handler = my_callback
        )
    
    def my_callback(self):
        print(self.time)
```



## Generator 间的信息传递

Generator 之间的信息传递给 Transmatrix 投研框架创造了高度的灵活性和自定义能力。

在 Generator 中，一条信息可以指代任何的 python 对象，它可以是一段话、一个数据，甚至一个类对象。这使得因子计算和交易策略之间的交互变得灵活而高效。

### 相关方法

<b> add_message </b> 

- 功能：注册信息流，通过 public 接口对外发布，订阅者可通 callback 接口建基于该信息流的回调。
- 参数：name (str): 信息名称。

<b> public </b>

- 功能: 对外发布信息 
- 参数: 
  - msg_name (str, optional): 信息名称 
  - data: 信息数据

<b> callback </b>

- 功能: 构建基于某一消息流的回调
- 参数: 
  - trigger: 消息流
  - handler: 回调函数

<b> </b>

```python
class MyGeneratorA(Generator):

    def init(self):
        self.add_message('vol_update')

    def some_callback(self):
        self.public('vol_update', self.volatility)

    
class MyGeneratorB(Generator):

    def init(self):
        a = self.subscribe(MyGeneratorA())
        self.callback(a['vol_update'], self.my_callback)

    def my_callback(self, msg):
        print(f'接收到来自 a 的波动率信息: vol = {msg}')
        
```



### 一个交易策略示例

使用 f1_gen 创造一个非定频发生的交易逻辑：当全市场交易量大于10000时，买入交易量最大的股票，否则不执行任何交易。

```python
# strategy.py
class f1_gen(Generator):
    def init(self):
        self.subscribe_data(
            'pv', ['common2','stock_bar_1day', self.codes,'volume', 1]
        )
        # 添加回测发生时间：随着数据pv的时间戳发生
        self.add_scheduler(with_data='pv', handler=self.compute_f1)
        # 添加消息流的名称
        self.add_message('f1_value')
        
    def compute_f1(self):
        volume = self.pv.get('volume')
        # 传出消息：当全市场交易量大于10000时，传出volume数据
        if np.nansum(volume) >= 10000:
        	self.public('f1_value', volume)
        

class trade(SimulationStrategy):
    def init(self):
        self.subscribe_data(
            'pv', ['common2','stock_bar_1day',self.codes,'close', 0]
        )
        # 订阅f1_gen
        f1 = self.subscribe(f1_gen())
        # 在接收f1_gen的消息f1_value时，执行self.on_f1
        self.callback(f1['f1_value'], self.on_f1)
        
    def on_f1(self, f1_value):
		# 买入交易量最大的股票
       	f1_value = np.where(np.isnan(f1_value), -np.inf, f1_value)
        buy_code = self.codes[np.argmax(f1_value)]
        price = self.pv.get('close', buy_code)
        self.buy(
            price, 
            volume=100, 
            offset='open', 
            code=buy_code, 
            market='stock'
        )
```

```yaml
# config.yaml
matrix:

    mode: simulation
    span: [2022-01-04, 2022-01-10]
    codes: custom_universe.pkl
    market:
        stock:
            data: [meta_data, stock_bar_1day] # 挂载的行情数据
            matcher: daily # 订单撮合模式为daily
            account: detail # 账户类型为detail

strategy:
    trade:
        class:
            - strategy.py
            - trade
```

