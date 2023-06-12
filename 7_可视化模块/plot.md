## 可视化模块

 <b> 作图组件，功能包括： </b>

  - 可绘制图形样式：
    - 折线图、柱状图、柱线图、点线图、直方图、热力图、箱线图、表格和矩形树图；
    - 其中表格和矩形树图仅支持在前端显示。
  - 在Evaluator中使用时，可在config.yaml文件中matrix部分配置字段`backend: ipython`或`tqclient`指定可视化显示在jupyter notebook还是前端。


#### 配置说明

- 公共参数：
  - data（list，np.ndarray，pd.Series，pd.DataFrame）：**请首选pd.DataFrame**，因为其他数据类型会自动转换成DataFrame。<u>图形的x轴数据默认使用DataFrame的index。</u>
  - kind（str）："line"，"hist"，"bar"，"line+bar"，"line+marker"，"heatmap"，"box"，"table" 或 "tree"。默认为"line"。
  - title（str）：图片标题。
  - legend_name（str, list）：图例名称。图例的长度需和输入数据的列数目一致；若不指定，默认为DataFrame的列名。
  - xlabel / ylabel / y2label（str）：x轴 / y轴 / 第二y轴的名称。
  - figsize（tuple）：指定图片像素大小，仅支持`backend = 'ipython'`。

- 单独使用时：

  ```python
  from transmatrix.plot import TransmatrixPlot
  
  plt = TransmatrixPlot()
  
  data = pd.DataFrame([[1,2,3],[2,3,4],[3,4,5]], columns=['a', 'b', 'c'])
  
  # 作图
  plt.plot(data, kind='line')  # kind参数默认为'line'
  plt.plot(data, kind='bar')
  ```

- 在Evaluator中使用：

  ```python
  class Eval(SignalEvaluator):
      def init(self):
          self.subscribe_data(
              'pv', ['common','stock_bar_daily',self.codes,'open,high,low,close', 10]
          )
          self.subscribe_data(
              'meta', ['common','critic_data', self.codes, 'is_zz500,ind', 10]
          )
          
      # 省略其他函数内容
          
      def show(self):
          self.plot(perf['qret']['tot'], kind='bar', title = 'QuantRetTot')
          self.plot(perf['qret']['history'], title = 'QuantRetHistory')
          
          self.plot(perf['history'][['top_dd_ser', 'top_nav_ser']], second_y=1, title = 'TopNavHistory')
          self.plot(perf['history'][['ls_dd_ser', 'ls_nav_ser']], second_y=1, title = 'LSNavHistory')
          self.plot(perf['industryIC'].reset_index().rename(columns={'index':'industry'}), kind='table', title='行业IC和IR')
  ```
  
  > 以下示例均结合框架中Evaluator模块说明

  

#### 折线图

- `kind='line'`
- areacol（int）：定数据中要画阴影的列的下标。

```python
data = pd.DataFrame([[1,2,3],[2,3,4],[3,4,5]], columns=['a', 'b', 'c'])

# 无阴影
self.plot(
    data,
    kind='line',
    title='plot_title',
    legend_name=['line1','line2','line3'],
    xlabel='x_axis',
    ylabel='yaxis'
)
```
<div align=center>
<img width="1000" src="7_可视化模块\pngs\1.png"/>
</div>
<div align=center style="font-size:12px">折线图</div>

<br />

```python
# 有阴影
self.plot(
    data,
    kind='line',
    title='plot_title',
    legend_name=['line1','line2','line3'],
    xlabel='x_axis',
    ylabel='y_axis',
    areacol=1  # 指定data中对第2列画阴影
)
```

<div align=center>
<img width="1000" src="7_可视化模块\pngs\2.png"/>
</div>
<div align=center style="font-size:12px">带阴影的折线图</div>

#### 柱状图

- `kind='bar'`

```python
self.plot(
    data,
    kind='bar',
    title='plot_title',
    legend_name=['bar1','bar2','bar3'],
    xlabel='x_axis',
    ylabel='y_axis'
)
```

<div align=center>
<img width="1000" src="7_可视化模块\pngs\3.png"/>
</div>
<div align=center style="font-size:12px">柱状图</div>

#### 复合折线图

- 有第二y轴的折线图

  - `kind='line'`
  - second_y（int, list）：指定数据中要以第二y轴显示的列的下标。

  ```python
  self.plot(
      data,
      kind='line',
      title='plot_title',
      second_y=1,  # 指定data中对第2列以第二y轴显示
      y2label='second_y_axis',
      legend_name=['line1','line2','line3'],
      xlabel='x_axis',
      ylabel='y_axis'
  )
  ```

<div align=center>
<img width="1000" src="7_可视化模块\pngs\4.png"/>
</div>
<div align=center style="font-size:12px">带有第二y轴的折线图</div>

- 柱线图

  - `kind='line+bar'`
  - barcol（str, list）：指定数据中要以柱状图显示的列的下标。

  ```python
  self.plot(
      data,
      kind='line+bar',
      title='plot_title',
      barcol=1,  # 指定data中第2列以柱状图显示
      y2label='second_y_axis',
      legend_name=['line1','bar1','line2'],
      xlabel='x_axis',
      ylabel='y_axis'
  )
  ```

<div align=center>
<img width="1000" src="7_可视化模块\pngs\5.png"/>
</div>
<div align=center style="font-size:12px">柱线图</div>

- 点线图（打点图）

  - `kind='line+marker'`
  - 当`backend = 'ipython'`时，显示点线图，即同时显示所有折线和节点。

      ```python
      # 点线图
      self.plot(
          data,
          kind='line+marker',
          title='plot_title',
          legend_name=['line1','line2','line3'],
          xlabel='x_axis',
          ylabel='y_axis'
      )
      ```

  <div align=center>
  <img width="1000" src="7_可视化模块\pngs\6.png"/>
  </div>
  <div align=center style="font-size:12px">点线图</div>
  
  - `当backend = 'tqclient'`时，显示打点图，即用红点和绿点标记买卖行为。

    - trademarker：指定数据中被打点标记的列的下标。
    - trademarker_dir：指定数据中指定打点标记方向的列的下标，该列的值只能是1或者-1。
  
    ```python
    # 打点图
    tradedata = pd.DataFrame([[1,2,3],[-1,3,4],[1,4,5]], columns=['direction', 'price', 'volume'])
    self.plot(
        tradedata,
        kind='line+marker',
        title='plot_title',
        trademarker=2,  # 指定tradedata中第3列被打点标记
        trademarker_dir=0  # tradedata中第1列是打点标记的方向
    )
    ```

#### 直方图

- `kind='hist'`，频率统计图
- nbinsx：分组数目

```python
histdata = pd.Series([1,2,1,3,4,2])

self.plot(
    histdata,
    kind='hist',
    nbinsx=5,
    title='plot_title',
    legend_name='count_number',
    xlabel='x_axis',
    ylabel='y_axis'
)
```

<div align=center>
<img width="1000" src="7_可视化模块\pngs\7.png"/>
</div>
<div align=center style="font-size:12px">直方图</div>

#### 热力图

- `kind='heatmap'`

```python
heatmapdata = pd.DataFrame(np.random.rand(3, 3), 
                        columns=['A', 'B', 'C'], 
                        index=['X', 'Y', 'Z'])  # 横轴的值对应为columns，纵轴的值对应为index

self.plot(
    heatmapdata,
    kind='heatmap',
    title='plot_title',
    xlabel='x_axis',
    ylabel='y_axis'
)
```

<div align=center>
<img width="1000" src="8_可视化模块\pngs\8.png"/>
</div>
<div align=center style="font-size:12px">热力图</div>

#### 箱线图

- `kind='box'`

```python
self.plot(
    data,
    kind='box',
    title='plot_title',
    legend_name=['box1','box2','box3'],
    xlabel='x_axis',
    ylabel='y_axis'
)
```

<div align=center>
<img width="1000" src="8_可视化模块\pngs\9.png"/>
</div>
<div align=center style="font-size:12px">箱线图</div>

#### 表格（仅支持前端）

- `kind='table'`

```python
self.plot(
    data,
    kind='table',
    title='plot_title'
)
```

#### 矩形树图（仅支持前端）

- `kind='tree'`
- 要求输入数据的列名为：'timestamp', 'code', 'name', 'marketCode', 'marketName', 'positionMarketValue', 'cumsumProfit', 'industry', 'subIndustry'.

```python
self.plot(
    treemap_df,
    kind='tree',
    title='plot_title'
)
```

