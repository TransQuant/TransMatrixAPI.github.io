# 二、数据获取API
## 2.1 Dataset
- 用于描述一个数据集合
  - 属性：
  >名称|类型|说明
  >----|----|----
  db_name|String|数据库名称
  table|String|数据表名
  start|String/datetime|查询起始日期
  end|String/datetime|查询截止日期
  codes|String/List|查询股票代码列表，若为"*"表示所有股票
  fields|String/List|查询字段，若为"*"表示所有字段
  data_category|Enum|数据类别枚举，类型为DATA_CATEGORY，包括以下4种类别：MARKET_DATA, FACTOR_DATA, META_DATA, MATCH_DATA，默认是MARKET_DATA
  panel_category|String|面板数据类型，包括以下2种类别：'price-volume'(量价类数据), 'finance-report'(财务类数据)，默认是'price-volume'
  lag|String/int|滞后天数，若为int类型，则查询时从start往前多取lag天的数据，若为'nQ'或'nY'格式（n为数字），则对应财务截面数据查询，参见FinancePanelData
  drop_dirty|bool|标识是否处理掉查询结果中的脏数据，默认为False

- load_data 加载数据
  - 参数：
    无

  - 返回：
   - 三维数据集合对象Array3dPanel，或财报数据集合对象FinancePanelData

    代码样例:

    ```python
    In:
      from transmatrix.data_api import Dataset

      dataset = Dataset(
          table_name = 'stock__bar__1day',
          start_time = '20210101',
          codes = ['000001.SZSE','000002.SZSE'],
          fields = ['open','high','low','close','volume'],
          end_time = '20210120',
      )  # 构建数据集

      dataset.load_data() #加载数据
      type(dataset.data)  #加载后数据以Array3dPanel的形式保存在.data属性中
    ```
    ```text
    Out:
      transmatrix.data_api.panel_engine.panel_database.Array3dPanel
    ```

## 2.2 Array3dPanel
- 三维数据集合对象
  - 属性：
  >名称|类型|说明
  >----|----|----
   data|numpy的ndarray|数据
   idx|pandas的DatetimeIndex|时间戳序列
   fields|List| 字段集合
   codes|List| 代码集合
   cursor|int| 当前游标位置 <br>初始化为-1，由回测引擎控制。 <br> 给定回测引擎时间T，游标为idx中T时刻之前最新一条数据对应的序号
   shape|tuple|日期窗口长度，股票数量

  - from_panel 类方法，将VanillaPanelData实例转换为Array3dPanel
    - 参数：
    >名称|类型|说明
    >----|----|----
    panel|VanillaPanelData|面板数据

    - 返回：
      - Array3dPanel

  - from_dataframes 类方法，将多个DataFrame数据转换为Array3dPanel
    - 参数：
    >名称|类型|说明
    >----|----|----
    panel|Dict|形为 {name : pd.Dataframe} 的字典实例化数据集合

    - 返回：
      - Array3dPanel    

    代码样例
    ```python
    In:
      from transmatrix.data_api import Array3dPanel

      idx = list(pd.date_range('20210101 09:30:00','20210105 09:30:00'))
      codes = ['000001.SZSE','000002.SZSE']

      panelA = pd.DataFrame(index = idx, columns = codes).fillna(1) 
      panelB = pd.DataFrame(index = idx, columns = codes).fillna(2) 

      panel3d = Array3dPanel.from_dataframes({'A': panelA, 'B': panelB})
      panel3d.data.shape
      panel3d.idx
      panel3d.fields
      panel3d.codes
    ```
    ```text
    Out:
      (5, 2, 2)
      {Timestamp('2021-01-01 09:30:00'): 0,
      Timestamp('2021-01-02 09:30:00'): 1,
      Timestamp('2021-01-03 09:30:00'): 2,
      Timestamp('2021-01-04 09:30:00'): 3,
      Timestamp('2021-01-05 09:30:00'): 4}

      {'A': 0, 'B': 1}

      {'000001.SZSE': 0, '000002.SZSE': 1}
    ```    

  - copy 复制当前的Array3dPanel
    - 参数：
      无
    - 返回:
      - Array3dPanel

  - to_dataframes 将当前Array3dPanel转换成形为 {name : pd.Dataframe} 的字典实例化数据集合
    - 参数
    >名称|类型|说明
    >----|----|----
    col|String|值为'code'或者'field'。若为'code'则返回字典的key为字段，value的列为股票代码，若为'field'则返回字典的key为股票代码，value的列为字段
    
    - 返回:
      - 形为 {name : pd.Dataframe} 的字典实例化数据集合
  
    代码样例
    ```python
    In:
      panel3d.to_dataframes()
    ```
    ```text
    Out:
      {'A':                      000001.SZSE  000002.SZSE
        2021-01-01 09:30:00            1            1
        2021-01-02 09:30:00            1            1
        2021-01-03 09:30:00            1            1
        2021-01-04 09:30:00            1            1
        2021-01-05 09:30:00            1            1,
        'B':                      000001.SZSE  000002.SZSE
        2021-01-01 09:30:00            2            2
        2021-01-02 09:30:00            2            2
        2021-01-03 09:30:00            2            2
        2021-01-04 09:30:00            2            2
        2021-01-05 09:30:00            2            2}
    ```

  - concat 向数据中加入新的字段 (同频拼接)
    - 参数：
    >名称|类型|说明
    >----|----|----
    other|Array3dPanel|另一个3维面板数据
    - 返回:
      无

    代码样例
    ```python
    In:
      other = Array3dPanel.from_dataframes(
          {
              'C':pd.DataFrame(index = idx, columns = codes).fillna(3),
              'D':pd.DataFrame(index = idx, columns = codes).fillna(4),
          }
      )
      panel3d.concat(other)

      panel3d.data.shape
      panel3d.idx
      panel3d.fields
      panel3d.codes
    ```
    ```text
    Out:
      (5, 4, 2)
      {Timestamp('2021-01-01 09:30:00'): 0,
      Timestamp('2021-01-02 09:30:00'): 1,
      Timestamp('2021-01-03 09:30:00'): 2,
      Timestamp('2021-01-04 09:30:00'): 3,
      Timestamp('2021-01-05 09:30:00'): 4}
      {'A': 0, 'B': 1, 'C': 2, 'D': 3}
      {'000001.SZSE': 0, '000002.SZSE': 1}
    ```

  - calibrate 匹配timestamps, 保留有效数据。对于timestamps中的任意一个时间戳，匹配该时间之后的第一条数据。
    - 参数：
    >名称|类型|说明
    >----|----|----
    timestamps|Iterator|datetime组成的集合
    - 返回:
      无

    代码样例
    ```python
    In:
      # 低频时间戳（e.g. 策略日频发单信号）
      clock_steps = pd.date_range('20210101 09:35:00','20210105 09:35:00', freq = '1d')

      # 高频数据 (e.g. 频率为1分钟, 未来15分钟窗口的 twap / vwap)
      idx = list(pd.date_range('20210101 09:30:00','20210105 15:00:00', freq = '1min'))
      codes = ['000001.SZSE','000002.SZSE']
      panelA = pd.DataFrame(index = idx, columns = codes).fillna(1) 
      panelB = pd.DataFrame(index = idx, columns = codes).fillna(2) 
      panel3d = Array3dPanel.from_dataframes({'twap': panelA, 'vwap': panelB})

      '校准前:'
      panel3d.data.shape
      list(panel3d.fields.keys())
      f'N timestamps : {len(clock_steps)},  Length panel3d : {len(panel3d.idx)}.'
    ```
    ```text
    Out:
      '校准前:'
      (6091, 2, 2)
      ['twap', 'vwap']
      'N timestamps : 5,  Length panel3d : 6091.'
    ```
    ```python
    In:
      '校准后:'
      panel3d.calibrate(clock_steps)
      panel3d.data.shape
      panel3d.to_dataframes()
    ```  
    ```text
    Out:
      '校准后:'
      (5, 2, 2)
      {'twap':                      000001.SZSE  000002.SZSE
      2021-01-01 09:35:00            1            1
      2021-01-02 09:35:00            1            1
      2021-01-03 09:35:00            1            1
      2021-01-04 09:35:00            1            1
      2021-01-05 09:35:00            1            1,
      'vwap':                      000001.SZSE  000002.SZSE
      2021-01-01 09:35:00            2            2
      2021-01-02 09:35:00            2            2
      2021-01-03 09:35:00            2            2
      2021-01-04 09:35:00            2            2
      2021-01-05 09:35:00            2            2}
    ```

  - query 指定截止时间，和另一条件，查询数据
    - 参数：
    >名称|类型|说明
    >----|----|----
    time|datetime|给定的查询截止时间
    periods |int| 返回N条数据，periods, start_time, window三个参数只需要指定其中之一。
    start_time |datetime | 返回某时刻之后的数据
    window |timedelta | 返回一段时间的数据
    - 返回:
      - 形如 {filed_name : dataframe}的字典

    代码样例
    ```python
    In: 
      panel3d.query(datetime(2021,1,4,9,36), periods = 3)
    ```
    ```text
    Out:
      {'twap':                      000001.SZSE  000002.SZSE
      2021-01-02 09:35:00            1            1
      2021-01-03 09:35:00            1            1
      2021-01-04 09:35:00            1            1,
      'vwap':                      000001.SZSE  000002.SZSE
      2021-01-02 09:35:00            2            2
      2021-01-03 09:35:00            2            2
      2021-01-04 09:35:00            2            2}
    ```
    ```python
    In:
      panel3d.query(datetime(2021,1,4,9,36), start_time = datetime(2021,1,3,9,30))
    ```
    ```text  
    Out:
      {'twap':                      000001.SZSE  000002.SZSE
      2021-01-03 09:35:00            1            1
      2021-01-04 09:35:00            1            1,
      'vwap':                      000001.SZSE  000002.SZSE
      2021-01-03 09:35:00            2            2
      2021-01-04 09:35:00            2            2}
    ```
    ```python
    In:
      panel3d.query(datetime(2021,1,4,9,36), window = timedelta(days=2))
    ```
    ```text
    Out:
      {'twap':                      000001.SZSE  000002.SZSE
      2021-01-03 09:35:00            1            1
      2021-01-04 09:35:00            1            1,
      'vwap':                      000001.SZSE  000002.SZSE
      2021-01-03 09:35:00            2            2
      2021-01-04 09:35:00            2            2}
    ```

  - get 返回某个字段 *游标* 位置最新一条数据
    - 参数：
    >名称|类型|说明
    >----|----|----
    field|String|查询字段
    codes|List/String/None|查询股票代码，若指定为'*'，则为所有股票
    - 返回
      - array / float，查询结果

    代码样例
    ```python
    In:
      panel3d.cursor = 3
      panel3d.get(field = 'twap')
      panel3d.get(field = 'twap', codes = '000001.SZSE')
    ```
    ```text
    Out:
      array([1, 1])
      1
    ```

- get_fields: 返回多个字段 *游标* 位置最新一条数据
    - 参数:
    >名称|类型|说明
    >----|----|----
    fileds|List|查询字段列表
    codes|List/String/None|查询股票代码，若指定为'*'，则为所有股票
    - 返回
      - array / float，查询结果

    代码样例
    ```python
    In:
      twap, vwap = panel3d.get_fields(['twap','vwap'])
      twap, vwap
    ```
    ```text
    Out:
      (array([1, 1]), array([2, 2]))
    ```

- get_window:返回某个字段 *游标* 位置最新一条数据
    - 参数:
    >名称|类型|说明
    >---|---|---
     length|int|窗口长度
     filed|String|字段名
     codes|List/String/None |查询股票代码，若指定为'*'，则为所有股票
    - 返回
      - array / float，查询结果

  代码样例
  ```python
  In:
    twap = panel3d.get_window(3,'twap')
    vwap = panel3d.get_window(3,'vwap')
    {'twap': twap,
    'vwap': vwap}
  ```
  ```text
  Out:
    {'twap': array([[1, 1],
    [1, 1],
    [1, 1]]),
    'vwap': array([[2, 2],
    [2, 2],
    [2, 2]])} 
  ```

## 2.3 FinancePanelData(财报数据接口)
- 财报数据集合对象，*通过Dataset构造*
  - 属性：
  >名称|类型|说明
  >----|----|----
   data|pandas.DataFrame|财务数据
   period|pandas.Series|财报序号
   period_group_data|pandas.DataFrame|财报序号为索引组成的财务数据

    代码样例
    ```python
    In:
      from transmatrix.data_api import FinancePanelData
      codes = ['000001.SZ','000002.SZ','000004.SZ','000005.SZ','000006.SZ']

      finpanel : FinancePanelData \
              = Dataset(
                  db_name = 'common2',
                  table_name = 'cashflow',
                  start_time = '20190501',
                  end_time = '20211110',
                  codes = codes,
                  fields = ['net_profit','invest_loss'],
                  #指定返回财报数据结构
                  panel_category = 'finance-report' # 默认为 price-volume 即非财报（基本面）数据
                  ).load_data()

      type(finpanel)
    ```
    ```text
    Out:
      transmatrix.data_api.panel_engine.panel_database.FinancePanelData
    ```
    ```python
    In:
      finpanel.data.head()
    ```
    <div align=center>
    <img width="1000" src="pngs/findata_data.png"/>
    </div>
    <div align=center style="font-size:12px">FinancePanelData属性data</div>
    <br />

    ```python
      In:
      finpanel.period_group_data.head()
    ```
    <div align=center>
    <img width="1000" src="pngs/findata_period_group_data.png"/>
    </div>
    <div align=center style="font-size:12px">FinancePanelData属性period_group_data</div>

  - copy 复制当前的FinancePanelData
    - 参数：
      无
    - 返回：
      - FinancePanelData

  - query 指定截止时间，和另一条件，查询数据
    - 参数：
    >名称|类型|说明
    >----|----|----
    time|datetime|给定的查询截止时间
    periods |int| 返回N条数据，periods, start_time, window三个参数只需要指定其中之一。
    start_time |datetime|返回某时刻**对应的报告期**及其之后的数据
    window |timedelta|返回一段时间的数据
    shift |int|返回前数第N条数据
    - 返回：
      - pandas.DataFrame
      - 
    代码样例
    ```python
    In:
      finpanel.query(time = datetime(2021,10,23), periods = 3) 
    ```
    <div align=center>
    <img width="1000" src="pngs/findata_query.png"/>
    </div>
    <div align=center style="font-size:12px">FinancePanelData方法query</div>

    代码样例
    ```python
    In:
      finpanel.query(time = datetime(2021,10,23), start_time = datetime(2020,3,30))
    ```    
    <div align=center>
    <img width="1000" src="pngs/findata_query2.png"/>
    </div>
    <div align=center style="font-size:12px">FinancePanelData方法query</div>
    <br />

### 2.3.1 截面查询样例
- 查询当前截面最新可用财报数据，以及对应历史截面财报数据
  
  说明：
  
  指定panel_category为'finance-report'，lag参数格式为'nQ'或'nY'的格式。例如当lag为'8Q'时，表示取当前最新可用的财务数据，并取过去连续8个季度的财务数据；当lag为'8Y'时，表示取当前最新可用的财务数据，并取过去8年同一季度的财务数据。
  ```python
  In:
    from transmatrix.data_api import FinancePanelData
    codes = ['000001.SZ','000002.SZ','000004.SZ','000005.SZ','000006.SZ']
    data_engine = DataEngine(parallel=False)
    data_set = Dataset(
                db_name='common2',
                table_name = 'cashflow',
                start_time = '20210501',
                end_time = '20221110',
                codes = codes,
                fields = ['net_profit','invest_loss'],
                #指定返回财报数据结构
                panel_category = 'finance-report', # 默认为 price-volume 即非财报（基本面）数据,
                lag = '8Q', # 往前取8个季度的财报
                )

    data_engine.add_data(data_set)
    data_engine.load_data()
    data_set.data
  ```
  ```text
  Out:
    <transmatrix.data_api.panel_engine.panel_database.Array3dPanel at 0x7fbb48131dc0>
  ```
  ```python
  In:
    data_set.data.fields
  ```
  ```text
  Out:
    {'net_profit_lag0Q': 0,
    'invest_loss_lag0Q': 1,
    'net_profit_lag1Q': 2,
    'invest_loss_lag1Q': 3,
    'net_profit_lag2Q': 4,
    'invest_loss_lag2Q': 5,
    'net_profit_lag3Q': 6,
    'invest_loss_lag3Q': 7,
    'net_profit_lag4Q': 8,
    'invest_loss_lag4Q': 9,
    'net_profit_lag5Q': 10,
    'invest_loss_lag5Q': 11,
    'net_profit_lag6Q': 12,
    'invest_loss_lag6Q': 13,
    'net_profit_lag7Q': 14,
    'invest_loss_lag7Q': 15,
    'net_profit_lag8Q': 16,
    'invest_loss_lag8Q': 17}
  ```
  ```python
  In:
    dic_data = data_set.data.to_dataframes()
    # net_profit_lag0Q表示截止某一横截面，各个股票最新的net_profit。
    # 注意在该截面上，不同股票的net_profit可能来源于不同的财报。
    # 例如，2021年4月28日这一截面上，部分股票公布了21Q1财报，
    # 部分股票公布了20Q4财报，部分股票公布了20Q3财报。net_profit_lag1Q表示各个股票上一季度的net_profit。
    dic_data['net_profit_lag0Q']
  ```
  <div align=center>
  <img width="1000" src="pngs/findata_section.png"/>
  </div>
  <div align=center style="font-size:12px">财务截面数据</div>
  <br />
  
  ```python
  In:
    # 上一季度的net_profit，依此类推，net_profit_lag2Q表示上上季度的net_profit
    dic_data['net_profit_lag1Q']
  ```
  <div align=center>
  <img width="1000" src="pngs/findata_section2.png"/>
  </div>
  <div align=center style="font-size:12px">财务截面数据</div>
  <br />

## 2.4 DataEngine
- 数据查询引擎
  - 在因子研究（参见第三章）或者策略回测（参见第四章）时，会订阅需要用到的数据，这些订阅的数据统一由DataEngine来获取和维护
  - 属性：
  >名称|类型|说明
  >----|----|----
   datasets|Dict|dataset组成的字典集合
   parallel|bool|是否采用并行模式查询数据
  
- join 将另一DataEngine的datasets合并到datasets
  - 参数：
  > 名称|类型|说明 
  > ----|----|----
    other|DataEngine|另一指定的DataEngine
  - 返回：
    无

- add_data 添加一个Dataset到datasets字典，若字典已包含该Dataset则不重复添加
  - 参数：
  > 名称|类型|说明 
  > ----|----|----
    dataset|Dataset|指定的Dataset
  - 返回：
    - Dataset本身

- load_data 加载datasets中所有Dataset的数据，数据挂载在各个Dataset的data属性
  - 参数：
  > 名称|类型|说明 
  > ----|----|----
    sudo|bool|是否只从数据库中读取数据
  - 返回：
    - 无

- cache 把数据缓存在本地
  - 参数：
    无
  - 返回：
    无

- save_factors 保存因子数据
  - 参数：
  > 名称|类型|说明 
  > ----|----|----
    table_name|String|数据库表名
    factor_name|String|指定的因子名称
    factor_data|Array3dPanel|因子数据
    freq|String|因子频率
    save2db|bool|标识因子数据是保存在数据库还是本地，若为False，则保存在本地，table_name不起作用
  - 返回：
    无