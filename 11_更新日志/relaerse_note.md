2023

---

- 1.0.0
  - 1.strategy 模块优化 SignalStrategy / SimulationStartegy 新增 api 接口： 数据订阅 / 相互订阅 /  定时器注册 / 信息发布 / 自定义回调 
  - 2.evaluator 模块优化 统一了 SignalEvaluator / SimulationEvaluator 的 api 接口 ：critic / show / regist
  - 3.matrix 模块优化 提升了 Strategy / Evaluator 存在多对多关系时的鲁棒性
  - 4.data-engine 模块优化 优化了多个组件订阅同一个数据时的数据共享逻辑
  
---

- 1.0.1 
  - 1.添加 BasketStrategy， 同时支持篮子下单和单票下单；  添加 BatchAlgoMatcher， 支持篮子单的算法成交模拟。    
  - 2.支持自定义动态票池 (通过 universe 配置） 
  - 3.支持自定义撮合器。 
  - 4.加入 debug 模式（在终端输出系统事件流) 。

---

