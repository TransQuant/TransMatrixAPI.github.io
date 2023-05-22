## 机器学习容器： Supervise-learning 

TransMatrix 框架基于 [Signal](5_定制化模块_截面因子开发/signal.md) 模块开发的机器学习模型训练接口。


### TransMatrix.Containers.MLStrategy 

- 通过 Strategy 生成特征序列
- 通过 Evaluator 生成标签，并于策略特征序列匹配
- 通过 add_model 接口注册模型
- 用户继承 MLStrategy 后通过实现 make_data / train / save_model


---

#### add_model

<b> 注册模型 </b>

<b> 参数: </b> model 模型对象 e.g. torch.nn.module



---

#### make_data
<b> 生成训练数据 </b>

---

#### train

<b> 训练模型 </b>

<b> 参数 </b>: 无

---

#### save_model

<b> 保存模型 </b>

<b> 参数 </b>: 无

---

#### cache

<b> 策略及数据 </b>
