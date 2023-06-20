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

- 1.0.2
  - 数据模型功能优化：支持 DataView3d 以索引的形式获取 DataView2d。
  - Api微调：SignalStrategy.factor_data 由原有的 DataView3d 改为 Dict[str, DataView2d] 
    - 受影响的测例 (模板已更新)
      - 因子服务-因子分析，
      - 因子服务-评价模板，
      - 策略服务-回测场景支持-因子选股，
      - transmatrix 特色功能-中间变量，
      - transmatrix 特色功能-批量任务，
      - transmatrix 特色功能-数据获取，

---

  
