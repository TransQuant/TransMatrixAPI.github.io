
## 简介
TransMatrix-python 是一套交易策略开发框架。

旨在帮助交易者实现：
- <b> 快速验证交易逻辑 </b>
- <b> 构建富有弹性的数据管道 </b>
- <b> 复杂交易场景的策略实现 </b>
- <b> 低成本策略部署 </b>


## 核心概念

[fig here]

- <b>  策略 (Strategy) </b>
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
  
-  <b> 评价器 (Evaluator) </b>
  - 订阅评价数据
    - 从数据库或文件中获取数据 [<b> Evaluator.subscribe_data </b> ]
  
  - 编写评价逻辑
    - 计算评价指标 [ <b> Evaluator.critic </b>]
    - 评价结果展示 [ <b> Evaluator.show </b> ]
    - 上传评价结果 (仅在接入 TransQuant 平台时有效) [ <b> Evaluator.regist </b>] 
  
- <b>  回测引擎 (Matrix) </b>
  - 设置回测时空范围 [ <b>span & codes </b>]
  - 配置市场和账户信息 [ <b> market </b>]
  - 注册策略和评价器 [ <b>Matrix.add_component </b>]
  - 运行回测 [ <b> Matrix.run </b>]
  - 运行评价并展示结果 [ <b> Matrix.eval </b>]

