### Generator

Generator 是 TransMatrix 系统的主要开发接口。它是 Strategy 的基类，同时它也可以被用户直接继承，用来实现因子计算逻辑。 Generator之间允许存在订阅关系，这些订阅关系构成了回测过程中的计算图。在一次回测中，Matrix引擎将以 Strategy 为入口自动获取计算图。

___

#### **\__init__**

<b> 子类的参数注册接口 </b>

TransMatrix 系统根据类名和参数确定 Generator 子类实例的 key，
系统保证 key 的全局唯一性。 即若一个 Generator 实例在[注册]()时系统中已存在与之相等（key相同）的对象，则该实例的订阅者将获得系统中已注册的实例。以下述 main.py 中的 MyGenerator 为例：

```python
# in main.py:
class MyGenerator(Generator):

    def __init__(self, w, b):
        super().__init__(w, b)

a = MyGenerator(3, 2)
b = MyGenerator(w = 3, b = 2)
c = MyGenerator(3, b = 2)

assert a == b == c
assert a.key == b.key == c.key == '__main__.MyGenerator(3,2)'
assert a.w == b.w == c.w == 3
assert a.b == b.b == c.b == 2
```

___
#### init

<b> 初始化接口 </b>

主要功能: [订阅数据]()、[订阅因子]()、[添加定时器]()、[添加自定义回调]()、[注册信息流]()

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

___
#### subscribe_data

<b> 数据订阅接口 </b>

参数:

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
    - 若财报数据，则填入'finance-report' (describe 长度为 6)
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









