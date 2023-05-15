#  一、数据库API
- 数据库链接类
  - 属性
    > 名称|类型|说明
    > ---------------|----|----
    db_name        |String|数据库名称

  - show_tables 显示数据库全部表名
    - 参数：
      无

    - 返回：
      - 数据库表名称组成的列表

      代码样例
      ```python
      In:
        from transmatrix.data_api import Database
        db = Database('test3')
        db.show_tables()
      ```
      ```text
      Out:
        ['capital',
        'factor_data__stock_cn__tech__1day__macd',
        'stock_bar_daily',
        'stock_code',
        'stock_data',
        'stock_fund',
        'stock_index',
        'stock_meta_temp',
        'trade_calendar']
      ```

  - show_columns 显示表列名
    - 参数:
      > 名称|类型|说明
      > ----|----|----
        table_name |String|数据表名|

    - 返回：
      - 字段名称组成的列表

      代码样例
      ```python
      In:
        db.show_columns('db_test')
      ```
      ```text
      Out:
        ['code',
        'datetime',
        'trade_day',
        'open',
        'high',
        'low',
        'close',
        'volume',
        'turnover',
        'vwap']
      ```

  - get_column_info 返回数据表字段数据类型
    - 参数:
    > 名称|类型|说明 
    > ----|----|----
      table_name|String|数据表名 

    - 返回：
      - 形如 {field_name : field_type}的字典

      代码样例
      ```python
      In:
        db.get_column_info('db_test')
      ```
      ```text
      Out:
        {'code': 'string',
        'datetime': 'timestamp',
        'trade_day': 'string',
        'open': 'double',
        'high': 'double',
        'low': 'double',
        'close': 'double',
        'volume': 'bigint',
        'turnover': 'double',
        'vwap': 'double'}
      ```

  - execute_sql 执行SQL语句
    - 参数:
    > 名称|类型|说明
    > ----|----|----
      sql|String|SQL语句
    
    - 返回:
      - 执行结果

      代码样例
      ```python
      In:
        db.execute_sql('insert into stock_bar_daily_test select * from stock_bar_daily limit 10')
      ```
      ```text
      Out:
        []

  - create_table 创建因子表（因子表用来储存多个同频因子）
      - 参数:
      >  名称|类型|说明
      >  ----|----|----
        table_name|String|数据表名
        column_info|Dict|表头信息 {列名:属性} 默认值: {'datetime':'timestamp','code':'string','seqnum':'double'}
        freq|String|频率信息，包括：快照数据：['tick','level1','level2']，分钟数据：['m','min','minute']，小时数据：['h','hour']，日频数据：['d','daily','day']

    - 返回：
      无

      代码样例
      ```python
      In:
        db.create_table('stock_bar_daily_test',
                        column_info={'code':'string','datetime':'timestamp',
                        'trade_day':'string','open':'double','high':'double',
                        'low':'double','close':'double','volume':'int',
                        'turnover':'double','vwap':'double','factor':'double'},
                        freq='daily')
      ```

  - delete_table 删除数据表
    - 参数:
      > 名称|类型|说明
      > ----|----|----
      table_name|String|数据表名

    - 返回：
      无

      代码样例
      ```python
      In:
        db.delete_table('db_test')
      ```

  - truncate_table 清空数据表内容(只用于orc事务表)
    - 参数:
      > 名称|类型|说明
      > ----|----|----
        table_name|String|数据表名
    - 返回：
    无

    代码样例
    ```python
    In:
      db.truncate_table('orc_test')
    ```

  - delete_row 删除记录
    - 参数：
      > 名称|类型|说明
      > ----|----|----
        table_name|String|数据表名
        condition|Dict|筛选条件,{<字段>:<条件>}<br>条件可以为单值,tuple,list<br>分别表示取单值,取值范围(闭区间),取多值

    - 返回:
    无

    代码样例
    ```python
    In:
      db.delete_row('orc_test',condition={'field':'code'})
    ```

  - update_row 更新记录
    - 参数
      > 名称|类型|说明
      > ----|----|----
        table_name|String|数据表名
        column_map|Dict|更改内容,{<字段>:<值>}
        condition|Dict|筛选条件,{<字段>:<条件>}<br>条件可以为单值,tuple,list<br>分别表示取单值,取值范围(闭区间),取多值

    - 返回:
    无

    代码样例
    ```python
    In:
      db.update_row('orc_test',column_map={'explain':'test update'},condition={'field':'datetime'})
    ```

  - insert_values 批量插入数据
      - 参数:
        > 名称|类型|说明
        > ----|----|----
        table_name|String|数据表名
        values|List/tuple/dict/pandas.DataFrame|插入数据
        if_file|Bool|是否以文件形式传输
        batch|Int|非文件传输时每批次记录条数
        parallelism|Int|并行进程数
      - 返回：
      无

      代码样例
      ```python
      In:
        import pandas as pd
        data = pd.DataFrame(data, columns=['datetime','high','low','open','close','code'])
        db.insert_values('stock_data', data)
      ```

  - query 查询数据表
      - 参数
        >名称|类型|说明
        >----|----|----
        table_name|String|数据表名
        fields|List/String|字段名
        start|String/date/datetime|查询起始时间
        end|String/date/datetime|查询截止时间
        universe|String/List|查询代码
        raw|bool|默认为False，使用query_as_df函数，否则用query_raw函数
        other_condition|Dict|其他筛选条件,{<字段>:<条件>}<br>条件可以为单值,tuple,list<br>分别表示取单值,取值范围(闭区间),取多值
        size|Integer|返回记录条数
        return_type|String|取值为 "list"(返回列表) 或 "pandas.DataFrame"(返回DataFrame)

      - 返回：
        - 用列表或DataFrame盛放的数据

      代码样例
      ```python
      In:
        df = db.query('stock_bar_daily',start='2019-10-01',end='2019-10-15',fields='close,vwap',universe='000004.SZ,000065.SZ')
        print(df)
      ```
      ```text
      Out:
            close    vwap       code            datetime
        0   18.83  18.900  000004.SZ 2019-10-08 15:00:00
        1   18.73  18.692  000004.SZ 2019-10-09 15:00:00
        2   18.94  18.881  000004.SZ 2019-10-10 15:00:00
        3   18.87  18.834  000004.SZ 2019-10-11 15:00:00
        4   19.05  19.041  000004.SZ 2019-10-14 15:00:00
        5   18.84  18.864  000004.SZ 2019-10-15 15:00:00
        6    8.53   8.566  000065.SZ 2019-10-08 15:00:00
        7    8.60   8.513  000065.SZ 2019-10-09 15:00:00
        8    8.64   8.639  000065.SZ 2019-10-10 15:00:00
        9    8.61   8.576  000065.SZ 2019-10-11 15:00:00
        10   8.78   8.787  000065.SZ 2019-10-14 15:00:00
        11   8.66   8.691  000065.SZ 2019-10-15 15:00:00
      ```
      ---
      ```python
      In:
        #指定其他查询条件,收盘价在18和19之间
        df = db.query('stock_bar_daily',start='2019-10-01',end='2019-10-15',fields='close,vwap',universe='000004.SZ,000065.SZ',
        other_condition={'close':(18,19)})
      ```
      ```text
      Out:
          close    vwap       code            datetime
        0  18.83  18.900  000004.SZ 2019-10-08 15:00:00
        1  18.73  18.692  000004.SZ 2019-10-09 15:00:00
        2  18.94  18.881  000004.SZ 2019-10-10 15:00:00
        3  18.87  18.834  000004.SZ 2019-10-11 15:00:00
        4  18.84  18.864  000004.SZ 2019-10-15 15:00:00
      ```
      ---
      ```python
      In:
        #指定其他查询条件,收盘价取18.83,8.66,8.64,8.61
        df = db.query('stock_bar_daily',start='2019-10-01',end='2019-10-15',fields='close,vwap',universe='000004.SZ,000065.SZ',
        other_condition={'close':[18.83,8.66,8.64,8.61]})
      ```
      ```text
      Out:
          close    vwap       code            datetime
        0  18.83  18.900  000004.SZ 2019-10-08 15:00:00
        1   8.64   8.639  000065.SZ 2019-10-10 15:00:00
        2   8.61   8.576  000065.SZ 2019-10-11 15:00:00
        3   8.66   8.691  000065.SZ 2019-10-15 15:00:00
      ```
      ---
      ```python
      In:
        #指定其他查询条件,收盘价等于8.60
        df = db.query('stock_bar_daily',start='2019-10-01',end='2019-10-15',fields='close,vwap',universe='000004.SZ,000065.SZ',
        other_condition={'close':8.60})
      ```
      ```text
      Out:
          close   vwap       code            datetime
        0    8.6  8.513  000065.SZ 2019-10-09 15:00:00
      ```  

  - query_raw 普通查询
      - 参数
      > 名称|类型|说明
      > ----|-----|----
      table_name|String|查询表名
      fields|List/String|查询字段
      condition|Dict|查询条件，{<字段>:<条件>}，方式同query方法
      raw|bool|默认为False，使用query_as_df函数，否则用query_raw函数

      - 返回：
        - 用列表或DataFrame盛放的数据

      代码样例
      ```python
      In:
        db.query_raw('stock_code',fields='code,name,industry,list_date',condition={'industry':['软件服务','银行']})
      ```
      ```text
      Out:
              code  name industry   list_date
        0    000001.SZ  平安银行       银行  1991-04-03
        1    000004.SZ  ST国华     软件服务  1991-01-14
        2    000034.SZ  神州数码     软件服务  1994-05-09
        3    000158.SZ  常山北明     软件服务  2000-07-24
        4    000409.SZ  云鼎科技     软件服务  1996-06-27
        ..         ...   ...      ...         ...
        310  688590.SH  新致软件     软件服务  2020-12-07
        311  688619.SH   罗普特     软件服务  2021-02-23
        312  688682.SH   霍莱沃     软件服务  2021-04-20
        313  688777.SH  中控技术     软件服务  2020-11-24
        314  688787.SH  海天瑞声     软件服务  2021-08-13

      [315 rows x 4 columns]
      ```

  - query_calendar 查询交易日
      - 参数
      > 名称|类型|说明
      >----|----|----
      start|String|查询起始日期
      end|String|查询截止日期
      exchange|String|交易所名称
      table_name|String|交易日存储表名

      - 返回：
        - 日期组成的列表

      代码样例

      ```python
      In:
        dates = db.query_calendar('2022-09-01','2022-09-20',exchange='SSE',table_name='trade_calendar')
        print(dates)
      ```
      ```text
      Out:
        [datetime.date(2022, 9, 1), datetime.date(2022, 9, 2), datetime.date(2022, 9, 5),
        datetime.date(2022, 9, 6), datetime.date(2022, 9, 7), datetime.date(2022, 9, 8),
        datetime.date(2022, 9, 9), datetime.date(2022, 9, 13), datetime.date(2022, 9, 14),
        datetime.date(2022, 9, 15), datetime.date(2022, 9, 16), datetime.date(2022, 9, 19),
        datetime.date(2022, 9, 20)]
      ```

  其他函数
  - create_factor_table 创建因子表
    - 参数
    > 名称|类型|说明
    >----|----|----
    table_name|String|因子表名
    freq|String|因子频率: <br>快照数据 :['tick','level1','level2'] <br>分钟数据 : ['m','min','minute'] <br>小时数据 : ['h','hour'] <br>日频数据 : ['d','daily','day']
    description|String|因子描述

    代码样例
    ```python
    In:
      from transmatrix.data_api import create_factor_table
      create_factor_table('factor_test_table',freq='daily',description='this is a test')
    ```

  - save_factor 保存因子
    - 参数
    > 名称|类型|说明
    >----|----|----
    table_name|String|因子表名
    data|dataframe|因子数据
    freq|String|因子频率

    代码样例
    ```python
    In:
      import pandas as pd
      from transmatrix.data_api import save_factor
      df = pd.DataFrame(data=[['2022-01-01','000001.SZ',0.1],['2022-01-02','000001.SZ',0.2]],columns=['datetime','code','value'])
      save_factor('factor_test_table', data=df)
    ```

  - get_column_info_from_df 从dataframe中获取列信息
    - 参数
    > 名称|类型|说明
    >----|----|----
    df|pandas.Dataframe|因子数据

    - 返回
      - Dict 数据每列对应类型

    代码样例
    ```python
    In:
      import pandas as pd
      from transmatrix.data_api import get_column_info_from_df
      df = pd.DataFrame(data=[['2022-01-01','000001.SZ',0.1],['2022-01-02','000001.SZ',0.2]],columns=['datetime','code','value'])
      columns = get_column_info_from_df(df)
      print(columns)
    
    Out:
      {'datetime': 'string', 'code': 'string', 'value': 'double'}
    ```

  - clear_private_datacache 清理个人数据库缓存
    - 参数
        无
    - 返回
        无