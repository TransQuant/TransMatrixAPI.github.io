### 测例说明
本测例展示了一个ETF基金T0策略，包括特征工程、模型构建、交易信号生成、策略回测。测例详细代码可参考：——————。

### 特征工程

- 确定参考标的
- 查询数据
- 特征加工
- 数据保存

### 模型构建
- 加载数据
- 选取训练/训练集
- 导入模型
- 备选模型池模型
- 模型保存

### 交易信号生成
- 加载数据
- 加载模型
- 保存推理结果（因子）
  
### 策略回测
- 初始化组件
- 运行回测
- 获取回测结果

```python
In:
    strategy = mat.strategies['naive_arb']
    strategy.get_daily_stats()
```
<div align=center>
<img width="1000" src="8_测例代码\pics\ETF基金1.png"/>
</div>
<div align=center style="font-size:12px">回测统计</div>
<br />

```python
In:
    strategy.get_trade_table()
```
<div align=center>
<img width="1000" src="8_测例代码\pics\ETF基金2.png"/>
</div>
<div align=center style="font-size:12px">交易记录</div>
<br />