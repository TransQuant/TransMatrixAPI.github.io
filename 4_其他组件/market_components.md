
<b> 订单(Order) </b> 与 <b> 撮合算法（Matcher）共同构成了 TransMatrix 系统中策略与市场间的信息交互机制</b> 

系统默认支持 日频 / k线 / 快照 与 Orderflow 撮合成交。

此外，开发者可根据特定场景开发定制化的撮合算法。

---

#### Order
order 对象有以下主要属性：
- price  : float, 委托价格
- volume : int, 委托数量
- direction : ORDER_DIRECTION 买卖方向
- offset : ORDER_OFFSET 开平方向
- code   : str，标的代码
- market : str，市场代码
- strategy : str，策略id
- status: ORDER_STATUS，订单状态，初始化为 SUBMITTING
- id: str 订单id
- insert_time: datetime, 委托指令发出时间
- cancel_time: datetime, 撤单指令发出时间
- latency: 策略与市场的通信延迟
- insert_receive_time: 市场收到委托指令的时间
- cancel_receive_time: 市场收到撤单指令的时间
- pending_volume: int，未成交数量
  

其中 ORDER_DIRECTION / ORDER_OFFSET / ORDER_STATUS 为:

```python
class ORDER_DIRECTION(Enum):
    BUY = 'buy'
    SELL = 'sell'

class ORDER_OFFSET(Enum):
    OPEN = 'open'
    CLOSE = 'close'

class ORDER_STATUS(Enum):
    SUBMITTING = '提交中'
    PENDING = '未成交'
    PARTIAL_TRADE = '部分成交'
    ALL_TRADE = '全部成交'
    CANCELLING = '待撤'
    CANCELED = '已撤'
    REJECTED = '拒单'
```

---

#### Matcher

撮合器的抽象基类。

其本质上是订单在状态空间ORDER_STATUS中的转化函数。

子类必须实现 match_submitting、match_pending 、match_cancelling 与 match_partial_traded 方法。

```python
class Matcher(ABC):

    @abstractmethod
    def match_submitting(self, order:Order) -> MatchResult:
        pass
    
    @abstractmethod
    def match_pending(self, order:Order) -> MatchResult:
        pass
    
    @abstractmethod
    def match_cancelling(self, order:Order) -> MatchResult:
        pass
    
    @abstractmethod
    def match_partial_traded(self, order: Order) -> MatchResult:
        pass

# 其中：
@dataclass
class MatchResult:
    order: Orde
    event: MATCH_EVENT
    price: float = None
    volume: int = None

class MATCH_EVENT(Enum):
    NOTHING = 0        # 状态未变
    INSERT2PEND = 1    # 未成交
    PARTIAL_TRADE = 2  # 部分成交
    PARTIAL_CANCEL = 3 # 撤单时余量部分成交
    ALL_TRADE = 4      # 全部成交
    CANCEL = 5         # 余量全撤
    REJECT = 6         # 拒单

```

以下示例代码实现了一个简单的 K 线撮合器：

```python
class BarMatcher(BaseMatcher):

    def match_submitting(self, order:Order) -> MatchResult: 
        
        close = self.data.get('close', order.code) # 当前bar的收盘价         
        
        if order.direction == ORDER_DIRECTION.BUY: # 买单
            if order.price > self.data.get('limit_up', order.code): # 买单价格超过涨停价
                order.status = ORDER_STATUS.REJECTED # 拒单
                return MatchResult(order = order, event = MATCH_EVENT.REJECT) # 返回拒单事件
            elif order.price >= close: # 买单价格小于等于收盘价
                order.status = ORDER_STATUS.ALL_TRADE # 全部成交
                order.pending_volume = 0 # 挂单量调整为0
                return MatchResult(order = order, event = MATCH_EVENT.ALL_TRADE, price = close, volume = order.volume) # 返回成交事件:全部成交
            
        elif order.direction == ORDER_DIRECTION.SELL: # 卖单
            if order.price < self.data.get('limit_down', order.code): # 卖单价格低于跌停价
                order.status = ORDER_STATUS.REJECTED # 拒单
                return MatchResult(order = order, event = MATCH_EVENT.REJECT) # 返回拒单事件
            elif order.price <= close: # 卖单价格大于等于收盘价
                order.status = ORDER_STATUS.ALL_TRADE # 全部成交
                order.pending_volume = 0 # 挂单量调整为0
                return MatchResult(order = order, event = MATCH_EVENT.ALL_TRADE, price = close, volume = order.volume) # 返回成交事件:全部成交

        order.status = ORDER_STATUS.PENDING  # 若未成交，则调整为挂单      
        return MatchResult(order = order, event = MATCH_EVENT.INSERT2PEND, volume = 0) # 返回事件：委托->挂单

    def match_pending(self, order:Order) -> MatchResult:  
        high = self.data.get('high', order.code) # 当前bar的最高价
        low = self.data.get('low', order.code) # 当前bar的最低价
        if (order.direction == ORDER_DIRECTION.BUY and order.price > low) \
        or (order.direction == ORDER_DIRECTION.SELL and order.price < high): # 如果买单价格高于最低价，或卖单价格低于最高价
            order.status = ORDER_STATUS.ALL_TRADE # 全部成交
            order.pending_volume = 0 # 挂单量调整为0
            return MatchResult(order = order, event = MATCH_EVENT.ALL_TRADE, price = order.price, volume = order.volume) # 返回成交事件:全部成交
        else:
            return MatchResult(order = order, event = MATCH_EVENT.NOTHING) # 返回成交事件: 状态未变

    def match_cancelling(self, order:Order) -> MatchResult: 
        order.status = ORDER_STATUS.CANCELED # 状态改为撤单
        return MatchResult(order = order, event = MATCH_EVENT.CANCEL) # 返回事件：全部撤单
```
---