### [数据管理](8_测例代码\transmatrix特色功能\数据获取-data_api\量价数据)
TransMatrix-python 框架使用 numpy 作为默认的数据后端。

在回测引擎中，数据管理分为[数据订阅]()和数据回放两个阶段:

数据订阅：用户的一次数据订阅将产生一个指向目标[数据集合](#Dataset)的[视图](#DataView)。

数据回放：数据视图的时间状态随着回测进行更新。

数据视图对外提供丰富的查询接口，保证用户获取最新数据。

---
--- 

### Dataset

描述一个数据集合

---
<b> \__init__ </b>

- 参数: 
  - data_model (str): 'ndarray' / 'finance-report'，分别对应普通数据和财报数据。
  - describe (dict):
      - source: 'db' / 'file', (传入db 表示从数据库中读取数据 / 传入 file 表示从文件读取数据)
      - db_name (str): 数据库名 (source 为 db 时)。
      - table_name (str): 数据表名 (source 为 db 时)。
      - file_path (str) : 数据文件路径 (source 为 file 时)。
      - start: 开始时间
      - end: 结束时间
      - codes (List[str]): 标的代码列表
      - fields: (List[str]) : 字段列表
  - use_cache: bool 是否采用数据缓存。Defaults to True.

---
<b> load_data </b>： 读取数据

- 参数：meta_info (dict), 缓存信息。 Defaults to None（将读取系统默认的缓存信息文件）。
- 返回值： [Data3d](#NdarrayData) / [FinanceReportData](#FinanceReportData)

---

<b> cache </b>： 缓存数据

- 参数：meta_info (dict), 缓存信息。 Defaults to None（将读取系统默认的缓存信息文件）。
- 返回值： 无
---

---
### DataModel

数据模型基类，用于存放一个数据集。

目前系统提供了 Data3d, Data2d 和 FinanceReportData 三个数据模型。 

---

#### Data3d

一个三维数据集合，后端为 numpy.ndarray。

系统默认使用 （时间，字段，标的代码）的三维数据结构。

---

<b> \__init__ </b>

- 参数:
  - data (numpy.ndarray): 数据集（将根据数据集的形状推断数据维度，目前支持 2维 和 3维数据）
  - describe (List): 数据集的描述信息（长度为3）
    - 时间戳 (Iterable[datetime])
    - 字段列表 (Iterable[str] 或 str)
    - 代码列表 (Iterable[str] 或 str)
  
---

<b> from_dataframes </b>

将多个 dataframe 拼接成一个 3d 数据集

- 参数: 
  - dataframes: dict
    - key: 字段名
    - value: dataframe 数据 (列为标的代码)
- 返回值：Data3d

---

<b> to_dataframes </b>

将 Data3d 转化为 dataframe

- <b> 参数 </b>: 
  - col (str): 传入 code 或 field, 分别表示以标的代码或字段名作为列名。
- <b> 返回值 </b> : dataframes: dict
  - key: 当 col = 'code' 时为字段名 , 当 col = 'field' 时列为股票代码
  - value: dataframe 数据 (当 col = 'code' 时列为股票代码 , 当 col = 'field' 时列为字段明)

---
<b> from_csv </b>

读取csv数据并转化成 Ndarray 数据模型

- <b> 参数 </b> :
  - file_path (str): 数据路径
  - start, end: 起止时间.
  - codes (List[str]): 标的代码列表
  - fields: (List[str]) : 字段列表
  
- <b> 返回值: </b> Data3d
  
- <b> csv格式要求 </b> :
  - df.index 必须为时间戳格式 (pd.DatetimeIndex)。
  - df 中必须存在名为 code 的列 
  - df.index * code 维度下数据必须唯一

- <b>  start, end 处理逻辑 </b> :
  - start, end 接受  str / datetime / date 类型的输入
  - 若输入的 end 为日期，则将时间修改为当日 16:00。

---

<b> from_db </b>

读取 db 数据并转化成 Data3d 数据模型

- <b> 参数 </b>
  - table_name (str): 数据表名
  - db_name (str): 数据库名
  - start, end: 起止时间.
  - codes (List[str]): 标的代码列表
  - fields: (List[str]) : 字段列表
  - padding_codes (bool): 是否按照 codes填充确实标的的数据(整列数据为 nan), 默认为 True。
  - datetime_checker: 按照 checker 剔除无效数据, 默认为 None (不剔除)。
  
- <b> 返回值 </b>: Data3d

- <b> start, end 处理逻辑 </b> :
  - start, end 接受  str / datetime / date 类型的输入
  - 若输入的 end 为日期，则将时间修改为当日 16:00


---
<b> query </b>

对给定的时间点，返回该时间（之前）的数据 (窗口)

- <b> 参数 </b>
  - time (datetime): 查询时间点
  - periods (int): 查询的最近 N 条数据
  - start_time (datetime): 查询 start_time 到 time 之间的数据
  - window (timedelta): 查询 time - window 到 time 之间的数据

- <b> 返回值 </b>
  - Dict[str, pd.DataFrame] : 
    - key: 字段名
    - value: dataframe 数据 (列为标的代码)


---
---

#### Data2d

存储一个二维数据集合，底层为 numpy.ndarray。

---

<b> from_csv </b>

读取csv数据并转化成 Data2d 数据模型

- <b> 参数 </b> : 
  - file_path (str): 数据路径
  - start, end: 起止时间.
  - cols: (List[str]): 字段列表
  
- <b> 返回值 </b> : Data2d

- <b> csv格式要求 </b> 
  - 必须存在名为 datetime 的时间戳列
  - 返回的结果数据只包含一个标的 (2维面板数据)。 此时要求 datetime 列中不包含重复时间戳。

- <b> start, end 处理逻辑 </b> :
  - start, end 接受  str / datetime / date 类型的输入
  - 若输入的 end 为日期，则将时间修改为当日 16:00

---

<b> _from_dataframe </b>

将dataframe数据转化成 Data2d 数据模型

- <b> 参数 </b> : 
  - df (Dataframe): 数据路径
  - start, end: 起止时间.
  - cols: (List[str]): 字段列表
  
- <b> 返回值 </b> : Data2d

- <b> csv格式要求 </b> 
  - 必须存在名为 datetime 的时间戳列
  - 返回的结果数据只包含一个标的 (2维面板数据)。 此时要求 datetime 列中不包含重复时间戳。

- <b> start, end 处理逻辑 </b> :
  - start, end 接受  str / datetime / date 类型的输入
  - 若输入的 end 为日期，则将时间修改为当日 16:00

---

<b> from_db </b>

读取 db 数据并转化成 Data2d 数据模型

- <b> 参数 </b>:
  - table_name (str): 数据表名
  - db_name (str): 数据库名
  - src (str): 数据路径
  - start, end: 起止时间.
  - code (str): 标的代码
  - fields: (List[str]) : 字段列表

- <b> start, end 处理逻辑 </b> :
  - start, end 接受  str / datetime / date 类型的输入
  - 若输入的 end 为日期，则将时间修改为当日 16:00

---

<b> query </b>

对给定的时间点，返回该时间（之前）的数据 (窗口)

- <b> 参数 </b>
  - time (datetime): 查询时间点
  - periods (int): 查询的最近 N 条数据
  - start_time (datetime): 查询 start_time 到 time 之间的数据
  - window (timedelta): 查询 time - window 到 time 之间的数据

- <b> 返回值 </b>
  - DataFrame
    - index: 目标时间段
    - columns: 字段名

<b> to_dataframe </b>

将 Data2d 数据转化成 dataframe

- <b> 参数 </b>: 无
- <b> 返回值 </b>: 
  - Dataframe
    - index: 时间戳
    - columns: 字段集合



---
---

#### FinanceReportData
财务数据模型基类，用于存放财务数据

---
---

#### FinanceReportPanelData
- 财务面板数据，*通过Dataset构造*
- 底层为 multi-index dataframe

<b> \__init__ </b>

- 参数:
  - data (pd.DataFrame): 财务面板数据（multi-index dataframe)
  - report_period_dict: 报告期字典
  
---

<b> copy </b>

复制当前的财务面板数据

- 参数: 无
- FinanceReportPanelData

---

<b> query </b>
- 查询规则: 
    - 返回按照财报期对齐的数据
    - 给定查询时间点，返回该时间之前
- args: 
    - time: *datetime* 
    - 1 of：
        - periods (int) 返回N条数据
        - start_time (detetime) 返回某时刻**对应的报告期**及其之后的数据
        - window (timedelta) 返回一段时间的数据
        - shift (int) 返回前数第N条数据 
---
---

#### FinanceReportSectionData
- 财报截面数据，通过Dataset构造
- 指定data_model为'finance-report'，lag参数格式为'nQ'或'nY'的格式。例如当lag为'8Q'时，表示取当前最新可用的财务数据，并取过去连续8个季度的财务数据；当lag为'8Y'时，表示取当前最新可用的财务数据，并取过去8年同一季度的财务数据
- 继承自NdarrayData，**NdarrayData支持的属性方法，它都支持**。同时也支持创建数据视图。

<b> \__init__ </b>

- 参数:
  - data (numpy.ndarray): 财务截面数据
  - describe: : 数据集的描述信息（长度为3）
    - 时间戳 (Iterable[datetime])
    - 字段列表 (Iterable[str] 或 str)
    - 代码列表 (Iterable[str] 或 str)
  
---
---

### DataView

数据视图基类，系统默认使用 3d 数据视图。

数据视图的时间状态随着回测进行更新。

数据视图对外提供丰富的查询接口，保证用户获取最新数据。

多个数据视图可以共享一份数据。

时间轴相同的数据视图之间可以实现状态同步。


---
---

#### DataView2d

---

<b> \__init__ </b>
- 参数: data (Data3d): 数据集


---

<b> get </b>

- <b>功能</b>: 获取最新一条数据
- <b>参数</b>: 无
- <b>返回值</b>: np.array, shape = (len(cols),) 

---

<b> get_dict </b>

- <b>功能</b>: 获取最新一条数据, 返回字典
- <b>参数</b>: 无
- <b> 返回值 </b>: Dict[str, np.float]

---

<b> get_window </b>

- <b>功能</b>: 获取指定时间窗口的数据
- <b>参数</b>: length (int): 窗口长度
- <b>返回值></b>: np.array, shape = (length, len(cols))


---
<b> to_dataframe </b>

- <b>功能</b>: 将数据转化为 dataframe
- <b>参数</b>: 无


---
---
#### DataView3d

3d数据视图，对外提供数据查询接口，用于获取最新数据。

---
<b> \__init__ </b>

- 参数: data (Data3d): 数据集

---

<b> get </b>
  - <b>功能</b>: 获取指定字段的最新一条数据
  - <b>参数</b>:
    - field (str): 字段名
    - codes (Union[list, str], optional): 标的代码集合. Defaults to '*' (返回所有标的数据)。
  - <b>返回值</b>: 
    - np.array (shape = (len(codes), )): 返回指定字段的数据 

---

<b> get_dict </b>
  - <b>功能</b>: 获取指定字段的最新一条数据, 返回字典
  - <b>参数</b>:
    - field (str): 字段名
    - codes (Union[list, str], optional): 标的代码集合. Defaults to '*' (返回所有标的数据).
  - <b>返回值</b>: 
    - dict: key: 标的代码, value: 指定字段的数据

---

<b> get_code </b>
  - <b>功能</b>: 获取指定标的最新一条数据
  - <b>参数</b>:
    - code (str): 标的代码
    - fields (Union[list, str], optional): 字段集合. Defaults to '*' (返回所有字段数据).
  - <b>返回值</b>: 
    - np.array (shape = (len(fields), )): 返回指定标的数据

---

<b> get_code_dict </b>
  - <b>功能</b>: 获取指定标的最新一条数据, 返回字典
  - <b>参数</b>:
    - code (str): 标的代码
    - fields (Union[list, str], optional): 字段集合. Defaults to '*' (返回所有字段数据).
  - <b>返回值</b>: 
    - dict, key: 字段名, value: 指定标的数据。

---

<b> get_window </b>
  - <b>功能</b>: 获取指定字段的最新 N 条数据
  - <b>参数</b>:
    - field (str): 字段名
    - length (int): 数据长度
    - codes (Union[list, str], optional): 标的代码集合. Defaults to '*' (返回所有标的数据).
  - <b>返回值</b>: 
    - np.array (shape = (length, len(codes))): 指定字段的数据

---

<b> get_window_df </b>
  - <b>功能</b>:获取指定字段的最新 N 条数据, 返回 DataFrame
  - <b>参数</b>:
    - field (str): 字段名
    - length (int): 数据长度
    - codes (Union[list, str], optional): 标的代码集合. Defaults to '*' (返回所有标的数据).
  - <b>返回值</b>: 
    - pd.DataFrame: 指定字段的数据


---

<b> get_window_code </b>
  - <b>功能</b>:获取指定字段的最新 N 条数据
  - <b>参数</b>:
    - code (str): 标的代码
    - length (int): 数据长度
    - fields (Union[list, str], optional):  字段集合. Defaults to '*' (返回所有字段数据).
  - <b>返回值</b>: 
    - np.array (shape = (length, len(fields))): 返回指定标的数据

---

<b> get_window_code_df </b>
  - <b>功能</b>: 获取指定标的最新 N 条数据, 返回 DataFrame
  - <b>参数</b>:
    - code (str): 标的代码
    - length (int): 数据长度
    - fields (Union[list, str], optional):  字段集合. Defaults to '*' (返回所有字段数据).
  - <b>返回值</b>: 
    - pd.DataFrame: 指定标的数据

---

<b> query </b>
  - <b>功能</b>: 根据指定时间查询数据
  - <b>参数</b>:
    - time (datetime): 指定时间
    - periods (int, optional): 返回N条数据. Defaults to None.
    - start_time (datetime, optional): 返回从指定时间开始的数据. Defaults to None.
    - window (timedelta, optional): 返回指定时间窗口内的数据. Defaults to None.
  - <b>返回值</b>: 
    - dict: 
      - key: 字段名
      - value: pd.dataframe, index 为时间, columns 为标的代码

---
