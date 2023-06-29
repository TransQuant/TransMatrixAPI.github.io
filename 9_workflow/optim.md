### 参数优化

Transmatrix框架支持参数优化功能，这里给出相关介绍，并对因子提供一个样例。

#### 待优化参数（超参数）类型

超参数类型可接受Sequence，Box，Discrete，Category和Bool。

- **Sequence**：数值型的等差数列，输入[low, high, step]，超参数的样本空间为np.arange(low, high, step)。比如输入[1,5,1]，得到np.arange(low,high,step)。
- **Box**：数值型的连续空间，输入[low, high]，超参数的样本空间为一个连续区间[low, high]。比如输入[1,5]，得到连续区间[1,5]。
- **Discrete**：数值型的离散空间，比如输入[1,3,4]，超参数的样本空间为一个list [1,3,4]。
- **Category**：分类变量，比如输入['a','b','c']，超参数的样本空间为一个list ['a','b','c']。
- **Bool**：布尔值空间，输入[True, False]，超参数的样本空间为一个list [True, False]。

#### 优化算法

- 网格搜索 **gridsearch**：支持除Box外的所有参数类型

  - 简介：通过在指定的超参数空间中搜索所有可能的参数组合，来寻找最优的超参数组合。
- 随机搜索 **randomsearch**：支持所有参数类型

  - 简介：在指定的超参数空间中随机选择参数组合进行评估。
  - 算法参数：
    - seed：随机种子
    - max_iter：最大迭代数目
- 贝叶斯搜索 **bayessearch**：仅支持数值型参数

  - 简介：基于贝叶斯优化，建立一个代表超参数和评估目标之间关系的高斯过程模型，利用之前的结果来指导下一次搜索，从而更快地找到最优参数组合。
  - 算法参数：
    - seed：随机种子
    - max_iter：最大迭代数目
    - n_warmup：初始化高斯过程模型的随机点个数
    - ac_func：选择下一个采样点的采样策略，可选择EI, PI
- 强化随机搜索 **ARS**：仅支持Sequence和Box类型的参数

  - 简介：基于随机搜索的增强学习算法，核心思想是使用随机噪声来超参数空间，并使用近似梯度来获得下一个参数组合，原文[Mania, Horia, Aurelia Guy, and Benjamin Recht. &quot;Simple random search provides a competitive approach to reinforcement learning.&quot; arXiv preprint arXiv:1803.07055 (2018)](https://arxiv.org/pdf/1803.07055.pdf)。
  - 算法参数：
  
    - seed：随机种子
    - max_iter：最大迭代数目
    - lr：学习率
    - initial_values：参数初值，字典类型。若为空，则随机生成一个点作为初值
    - noise：指定对待优化参数每次探索长度的标准差，形如[待优化参数1的探索长度的标准差, 待优化参数2的探索长度的标准差, ...]的list
    - num_directions：在每个迭代中探索多少个随机方向 
    - num_top_directions：在每个迭代中保留多少个最好的随机方向
- 遗传算法 **GA**：支持所有参数类型

  - 简介：每个参数组合都被视为一个个体，整个超参数空间被视为一个种群，通过模拟遗传过程（选择、交叉和变异）来搜索最优参数组合。
  - 算法参数：
    - seed：随机种子
    - max_iter：最大迭代数目
    - population_size：种群大小
    - tournament_size：每次迭代中选取多少个最优个体不经过交叉、变异，直接复制进入下一代
    - pc：交叉概率
    - pm：变异概率


> 其他：
>
> 早停法 earlystopping
>
> - 简介：在训练过程中监控模型的性能，一旦发现模型性能不再提升，就停止训练。
> - 算法参数：
>   - patience：不再提升的容忍次数
>   - delta：提升的最小变化量



#### 结合参数优化的因子研究

- <b> 配置config.yaml文件 </b>

  - 配置OptimMatrix组件回测信息

    ```yaml
    OptimMatrix:
        max_workers: 20    # 并行运算的worker数量
        policy: gridsearch    # 参数优化方法，可选择gridsearch, randomsearch, bayessearch, GA, ARS
        # 参数优化的算法参数设置
        policy_params: 
        	# 不同优化算法都有的公共参数
            seed: 81    # 随机种子
            max_iter: 30    # 最大迭代数目
    		
    		# 以下为不同优化算法特有的参数    
            ## bayessearch
            n_warmup: 20    # 初始化高斯过程模型的随机点个数
            ac_func: 'EI'    # 选择下一个采样点的采样策略，可选择EI, PI
    		
            ## ARS
            lr: 0.5    # 学习率
            noise: [5,3]    # [待优化参数1的探索长度的标准差, 待优化参数2的探索长度的标准差, ...]
            num_directions: 5    # 在每个迭代中探索多少个随机方向 
            num_top_directions: 3    # 在每个迭代中保留多少个最好的随机方向
    
            ## GA
            population_size: 10    # 种群大小
            tournament_size: 2    # 每次迭代中选取多少个最优个体不经过交叉、变异，直接复制进入下一代
            pc: 0.3    # 交叉概率
            pm: 0.5    # 变异概率
    
    	# 早停法，可选
        earlystopping:
            patience: 3    # 不再提升的容忍次数
            delta: 0.0001    # 提升的最小变化量
    
    	# 待优化的超参数，以[样本空间, 空间类型]的形式配置:
        params:
            ret:  [[1,5,1], 'Sequence']
            roll: [[5,15,1], 'Sequence']
    ```
    
  - 配置Matrix组件，策略逻辑和评价组件
  
    ```yaml
    matrix:
        mode: signal
        span: [2020-01-01, 2021-12-30]
        codes: &universe custom_universe.pkl
    
    strategy:
        reverse_signal:
            class: [strategy.py, ReverseSignal]
                    
    evaluator:
        rank_ic:
            class: [evaluator.py, Eval]
    ```
  
- <b> 编写strategy.py </b>

  - 订阅数据、定时器，实现因子逻辑
  - 调用待优化参数

  ```python
  from scipy.stats import zscore
  from transmatrix.strategy import SignalStrategy
  from transmatrix.data_api import create_data_view, NdarrayData, DataView3d
  
  class ReverseSignal(SignalStrategy):
      
      def init(self):
          self.subscribe_data(
              'pv', ['default','stock_bar_1day',self.codes,'open,high,low,close', 10]
          )
          self.add_clock(milestones='09:35:00') 
  
      def pre_transform(self):
          # 获得待优化参数ret和roll。注意：在参数优化过程中整数的数据类型会被转为浮点数，使用int()获得正确的数据类型。
          param = self.param
          ret_window = int(param['ret'])
          roll_window = int(param['roll'])
  
          pv = self.pv.to_dataframe()
          ret = (pv['close'] / pv['close'].shift(ret_window) - 1).fillna(0) 
          reverse = -ret.rolling(window = roll_window, min_periods = roll_window).mean().fillna(0)
          reverse = zscore(reverse, axis = 1, nan_policy='omit') # 因子标准化
          
          self.reverse: DataView3d = create_data_view(NdarrayData.from_dataframes({'reverse':reverse})) 
          self.reverse.align_with(self.pv) # 与原始数据对齐
              
      def on_clock(self):
          self.update_signal(self.reverse.get('reverse')) # 定时更新因子数据
  
  ```

- 编写evaluator.py

  - 订阅数据，实现评价逻辑
  - critic函数的返回值作为参数优化的目标函数值，优化方向为越大越好

  ```python
  import pandas as pd
  from transmatrix.evaluator.signal import SignalEvaluator
  
  def vec_rankIC(factor_panel: pd.DataFrame, ret_panel: pd.DataFrame):
      return factor_panel.T.corrwith(ret_panel.T, method = 'spearman').mean()
  
  
  class Eval(SignalEvaluator):
      def init(self):
          # 订阅因子评价所需要的数据
          self.subscribe_data(
              'pv', ['*','stock_bar_1day',self.codes,'open,high,low,close', 10]
          )
      
      
      def critic(self):
          critic_data = self.aligned_data['pv'].to_dataframe()
          critic_data.update({'signal': self.strategy.signal})
          
          price = critic_data['close']
          factor = critic_data['signal']
          ret_1d = price.shift(-1) / price - 1
          ic = vec_rankIC(factor, ret_1d)
          
          return np.abs(ic)
  
  ```

- <b> 运行入口 </b>

  - 运行结合参数优化的因子计算和评价

  ```python
  from transmatrix.workflow.run_optim import run_optim_matrix
  result = run_optim_matrix('config.yaml')
  result
  ```

  <div align=center>
  <img width="200" src="9_workflow\pics\参数优化.png"/>
  </div>
  <div align=center style="font-size:12px">优化结果</div>

