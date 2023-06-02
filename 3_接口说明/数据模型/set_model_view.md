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

<b> \__init__ </b>

- 参数: 
  - data_model (str): 'ndarray' / 'finance-report'，分别对应普通数据和财报数据。
  - describe (dict):
      - source: 'db' / 'file', (传入db 表示从数据库中读取数据 / 传入 file 表示从文件读取数据)
      - db_name (str): 数据库名 (source 为 db 时)。
      - table_name (str): 数据表名 (source 为 db 时)。
      - file_path (str) : 数据文件路径 (source 为 file 时)。
      - dim (int, optional): 维数 2/3. Defaults to 3.
      - start: 开始时间
      - end: 结束时间
      - codes (List[str]): 标的代码列表
      - fields: (List[str]) : 字段列表
  - use_cache: bool 是否采用[数据缓存]()。Defaults to True.

<b> load_data </b>： 读取数据

- 参数：meta_info (dict), 缓存信息。 Defaults to None（将读取系统默认的缓存信息文件）。
- 返回值： [NdarrayData](#NdarrayData) / [FinanceReportData](#FinanceReportData)

<b> cache </b>： 缓存数据

- 参数：meta_info (dict), 缓存信息。 Defaults to None（将读取系统默认的缓存信息文件）。
- 返回值： 无
---

---
### DataModel

数据模型基类，用于存放一个数据集。

目前系统提供了 NdarrayData 和 FinanceReportData 两个数据模型。 

---

#### NdarrayData

一个多维数据集合，后端为 numpy.ndarray。

系统默认使用 （时间，字段，标的代码）的三维数据结构。

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

- 参数: dataframes: dict
  - key: 字段名
  - value: dataframe 数据 (列为标的代码)
- 返回值：NdarrayData

---

<b> to_dataframe </b>
- 参数: 无
- 返回值: dataframes: dict
  - key: 字段名
  - value: dataframe 数据 (列为标的代码)
---

#### FinanceReportData

待补充

---
---

### DataView

数据视图基类，系统默认使用 3d 数据视图。

---
---
#### DataView3d

3d数据视图，对外提供数据查询接口，用于获取最新数据。

参数: 
    - data (NdarrayData): 数据集

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
