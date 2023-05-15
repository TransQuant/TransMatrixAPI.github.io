#  一、数据库API

TransMatrix 的默认使用 Timelyre 分布式时序数据库。

- <b>数据库链接类</b>
#### 属性
    > 名称|类型|说明
    > ---------------|----|----
    db_name        |String|数据库名称
#### 实例方法
  - <b>show_databases </b>
    - <b>功能</b>: 显示全部数据库名称
    - <b>参数</b>：无

    - <b>返回值</b>：数据库名称列表

      ```python
      In:
        from transmatrix.data_api import Database
        db = Database()
        db.show_databases()
      ```
      ```text
      Out:
       ['team2_public',
       'team2_team_meta',
       'test3',
       'test_team_public',
       'test_team_team_meta',
       'test_user2_meta',
       'test_user2_private',
       'test_user_meta',
       'test_user_private',
       'testaaa_meta',
       'testaaa_private']
      ```
  - <b> show_properties </b>
    - <b>功能</b>：显示表属性
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
        table_name|String|数据表名|
    - <b>返回值</b>：表属性字典

      ```python
      In:
        from transmatrix.data_api import Database
        db = Database('common')
        prp = db.show_properties('stock_bar_1day')
      ```
      ```text
      Out:
      {'# Category': 'Attribute',
      'code': 'string',
      'datetime': 'timestamp',
      'trade_day': 'string',
      'open': 'double',
      'high': 'double',
      'low': 'double',
      'close': 'double',
      'volume': 'bigint',
      'turnover': 'double',
      'vwap': 'double',
      'factor': 'double',
      '# Detailed Table Information': '#',
      'Database:': 'common',
      'Owner:': 'hive',
      'CreateTime:': 'Wed Mar 15 14:57:44 CST 2023',
      'LastAccessTime:': 'UNKNOWN',
      'Protect Mode:': 'None',
      'Retention:': '0',
      'Location:': 'hdfs://nameservice1/quark1/user/hive/warehouse/common.db/hive/stock_bar_1day',
      'Table Type:': 'MANAGED_TABLE',
      'Table Parameters:': '#',
      'COLUMN_STATS_ACCURATE': 'false',
      'epoch.engine.enabled': 'true',
      'last_load_time': '1678868512',
      'partition.size': '0',
      'shard.group.duration.seconds': '63072000',
      'storage_handler': 'io.transwarp.timelyre.TimeLyreStorageHandler',
      'timelyre.shiva.cols': 'code,datetime,trade_day,open,high,low,close,volume,turnover,vwap,factor',
      'timelyre.shiva.data.types': 'Tag,Timestamp,String,Float,Float,Float,Float,Integer,Float,Float,Float',
      'timelyre.tag.cols': 'code',
      'timelyre.time.sharding.policy': 'years',
      'timelyre.timestamp.col': 'datetime',
      'transient_lastDdlTime': '1678863464',
      '# Storage Information': '#',
      'SerDe Library:': 'io.transwarp.timelyre.TimeLyreSerde',
      'InputFormat:': 'io.transwarp.timelyre.TimeLyreInputFormat',
      'OutputFormat:': 'io.transwarp.timelyre.TimeLyreOutputFormat',
      'Compressed:': 'No',
      'Num Buckets:': '-1',
      'Bucket Columns:': '[]',
      'Sort Columns:': '[]',
      'Storage Desc Params:': '#',
      'serialization.format': '1'}

  - <b>show_table_type</b> 
    - <b>功能</b>：显示表类型
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
        table_name|String|数据表名|
    - <b>返回值</b>：表类型

      ```python
      In:
        from transmatrix.data_api import Database
        db = Database('common')
        db.show_table_type('stock_bar_1day')
      ```
      ```text
      Out:
        'timelyre'
    
  - <b>clear_mapping_table</b> 
    - <b>功能</b>：删除对应映射表
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
        table_name|String|数据表名|
    - <b>返回值</b>：无

    timelyre数据库配置的dataframeAPI支持修改表结构，可以调用add_columns,drop_columns增加或者删除列，生成原表的映射表。使用query时会指向最新的映射表，查询到修改之后的结果。
    调用clear_mapping_table会删除原表对应的全部映射表，再次查询会显示原表结构和数据。
      
      ```python
      In:
      import pandas as pd
      import numpy as np
      import datetime as dt

      #生成随机行情
      def gen_sample_market(row, column, start, freq, code_num):
          start = pd.to_datetime(start)
          data = np.random.rand(row, column)
          code = [str(i).rjust(6, '0') for i in range(code_num)]
          repeats = row // code_num
          res = row % code_num
          codes = code * repeats + code[:res]
          
          idx = [start + i * freq for i in range(row)]
          df = pd.DataFrame(data)
          df.columns = ['c'+str(i) for i in df.columns]
          df['code'] = codes
          df['datetime'] = idx
          df = df[['code','datetime']+['c'+str(i) for i in range(len(df.columns)-2)]]
          return df
      #建表并插入数据
      db.create_table(table_name='test_insert',
                column_info={'code':'string',
                            'datetime':'timestamp',
                            'c0':'double',
                            'c1':'double'},
                freq='tick')
      df = gen_sample_market(1000000, 2, '2023-01-01', dt.timedelta(seconds=3), 3000)
      db.insert_values('test_insert', df)
      db.query('test_insert')
      ```
      ```text
      Out:
                code            datetime        c0        c1
      0       000109 2023-01-01 00:05:27  0.154508  0.557445
      1       000109 2023-01-01 02:35:27  0.719645  0.004533
      2       000109 2023-01-01 05:05:27  0.236844  0.557391
      3       000109 2023-01-01 07:35:27  0.059960  0.011983
      4       000109 2023-01-01 10:05:27  0.095141  0.055906
      ...        ...                 ...       ...       ...
      999995  002981 2023-02-04 06:29:03  0.535707  0.285430
      999996  002981 2023-02-04 08:59:03  0.546874  0.048224
      999997  002981 2023-02-04 11:29:03  0.991744  0.079193
      999998  002981 2023-02-04 13:59:03  0.053348  0.102120
      999999  002981 2023-02-04 16:29:03  0.622577  0.430500

      [1000000 rows x 4 columns]
      ```
      ```python
      In:
      #使用timelyre数据库dataframeAPI删除列
      from transwarp.timelyre import dataframe as tw
      left_df = tw.DataFrame(table='test_insert', db=db.db_name, conn=db._conn, schema=['code','datetime'])
      left_df.drop_columns(['c1'])
      db.query('test_insert')
      ```
      ```text
      显示已删除c1列
      Out:
      
                code            datetime        c0
      0       000109 2023-01-01 00:05:27  0.154508
      1       000109 2023-01-01 02:35:27  0.719645
      2       000109 2023-01-01 05:05:27  0.236844
      3       000109 2023-01-01 07:35:27  0.059960
      4       000109 2023-01-01 10:05:27  0.095141
      ...        ...                 ...       ...
      999995  002981 2023-02-04 06:29:03  0.535707
      999996  002981 2023-02-04 08:59:03  0.546874
      999997  002981 2023-02-04 11:29:03  0.991744
      999998  002981 2023-02-04 13:59:03  0.053348
      999999  002981 2023-02-04 16:29:03  0.622577

      [1000000 rows x 3 columns]
      ```
      ```python
      In:
      db.clear_mapping_table('test_insert')
      db.query('test_insert')
      ```
      ```text
      显示原表
      Out:
                code            datetime        c0        c1
      0       000109 2023-01-01 00:05:27  0.154508  0.557445
      1       000109 2023-01-01 02:35:27  0.719645  0.004533
      2       000109 2023-01-01 05:05:27  0.236844  0.557391
      3       000109 2023-01-01 07:35:27  0.059960  0.011983
      4       000109 2023-01-01 10:05:27  0.095141  0.055906
      ...        ...                 ...       ...       ...
      999995  002981 2023-02-04 06:29:03  0.535707  0.285430
      999996  002981 2023-02-04 08:59:03  0.546874  0.048224
      999997  002981 2023-02-04 11:29:03  0.991744  0.079193
      999998  002981 2023-02-04 13:59:03  0.053348  0.102120
      999999  002981 2023-02-04 16:29:03  0.622577  0.430500

      [1000000 rows x 4 columns]
      ```

  - <b>remove_cache</b> 
    - <b>功能</b>：删除数据库内缓存表
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
        dropNum|Int|删除缓存表数量|
    - <b>返回值</b>：无

    数据库查询支持缓存功能，如果在配置里打开缓存功能会在每次查询后形成缓存表，下次调用同样的查询语句会返回缓存表的结果提高查询效率。缓存表存在生命周期，可以在配置文件里修改，默认为1小时。如果在缓存表存续期间进行数据增加删除或修改，但仍使用相同的查询语句，那么修改结果不会显示在这次查询里，remove_cache函数可以手动清空全部缓存表，查询到最新修改结果。
    ```python
    In:
      from transmatrix.data_api import Database
      db = Database('common')
      db.remove_cache(5)
    ```

  - <b>show_tables</b> 
    - <b>功能</b>：显示数据库全部表名
    - <b>参数</b>：
      无

    - <b>返回值</b>：
      数据表名称列表

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

  - <b>show_columns</b> 
    - <b>功能</b>：显示表列名
    - <b>参数</b>:
      > 名称|类型|说明
      > ----|----|----
        table_name |String|数据表名|

    - <b>返回值</b>：
      字段名称列表

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

  - <b>get_column_info</b> 
    - <b>功能</b>：返回数据表字段数据类型
    - <b>参数</b>：
    > 名称|类型|说明 
    > ----|----|----
      table_name|String|数据表名 

    - <b>返回值</b>：
      形如 {field_name : field_type}的字典

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

  - <b>execute_sql</b> 
    - <b>功能</b>：执行SQL语句
    - <b>参数</b>：
    > 名称|类型|说明
    > ----|----|----
      sql|String|SQL语句
    
    - <b>返回值</b>：
      执行结果

    可以执行任何sql语句,但做查询操作时需要注意返回结果数据量很大时性能较差问题。建议对于简单查询语句使用query,query_raw接口，复杂查询语句可以用execute_sql函数先生成视图，再使用query,query_raw接口查询结果。
      ```python
      In:
        #查询数据库
        db.execute_sql('show database')
      ```
      ```text
      Out:
        [['common'], ['common2'], ['coral_meta'], ['coral_private'], ['cpp1_meta'], ['cpp1_private'], ['default'], ['discover'], ['global_meta'], ['pandas_test'], ['system'], ['tc11_meta'], ['tc11_private'], ['team2_public'], ['team2_team_meta'], ['test3'], ['test_team_public'], ['test_team_team_meta'], ['test_user2_meta'], ['test_user2_private'], ['test_user_meta'], ['test_user_private'], ['testaaa_meta'], ['testaaa_private'], ['wht1_meta'], ['wht1_private'], ['wyp1_meta'], ['wyp1_private']]
      ```
      ```python
      In:
        #执行插入数据
        db.execute_sql('insert into stock_bar_daily_test select * from stock_bar_daily limit 10')
      ```
      ```text
      Out:
        []
      ```
      ```python
      In:
        #联表查询
        sql = '''
        select 
        a.code,
        a.name,
        a.area,
        a.industry,
        b.`close`
        from stock_code a
        join stock_bar_1day b
        on a.code = b.code
        where (b.trade_day > '2023-03-01' and b.trade_day < '2023-03-05');
        '''
        db.execute_sql(sql)
      ```
      ```text
      Out:
        [['000001.SZ', '平安银行', '深圳', '银行', '14.24'],
        ['000001.SZ', '平安银行', '深圳', '银行', '14.29'],
        ['000002.SZ', '万科A', '深圳', '全国地产', '16.73'],
        ['000002.SZ', '万科A', '深圳', '全国地产', '16.81'],
        ['000004.SZ', 'ST国华', '深圳', '软件服务', '9.95'],
        ['000004.SZ', 'ST国华', '深圳', '软件服务', '9.9'],
        ['000005.SZ', 'ST星源', '深圳', '环境保护', '1.81'],
        ['000005.SZ', 'ST星源', '深圳', '环境保护', '1.81'],
        ['000006.SZ', '深振业A', '深圳', '区域地产', '5.71'],
        ['000006.SZ', '深振业A', '深圳', '区域地产', '5.87'],
        ['000007.SZ', '*ST全新', '深圳', '其他商业', '7.75'],
        ['000007.SZ', '*ST全新', '深圳', '其他商业', '7.76'],
        ['000008.SZ', '神州高铁', '北京', '运输设备', '2.6'],
        ['000008.SZ', '神州高铁', '北京', '运输设备', '2.59'],
        ['000009.SZ', '中国宝安', '深圳', '电气设备', '12.58'],
        ['000009.SZ', '中国宝安', '深圳', '电气设备', '12.52'],
        ['000010.SZ', '美丽生态', '深圳', '建筑工程', '3.34'],
        ['000010.SZ', '美丽生态', '深圳', '建筑工程', '3.34'],
        ['000011.SZ', '深物业A', '深圳', '区域地产', '11.54'],
        ['000011.SZ', '深物业A', '深圳', '区域地产', '11.64'],
      ...
        ['001322.SZ', '箭牌家居', '广东', '家居用品', '24.1'],
        ['001322.SZ', '箭牌家居', '广东', '家居用品', '23.7'],
        ['001323.SZ', '慕思股份', '广东', '家居用品', '46.42'],
        ['001323.SZ', '慕思股份', '广东', '家居用品', '46.32'],
        ...]
      ```
      ```python
      #生成视图
      sql = '''
      create view test_join as
      select l.code as code,name,area,industry,`open`,high,low,`close` from
      (
          select code,name,area,industry
          from stock_code where industry = '银行'
      ) l
      inner join
      (
          select code,`open`,high,low,`close`
          from stock_bar_1day where trade_day > '2023-03-01' and trade_day < '2023-03-05'
      ) r
      on l.code = r.code
      '''
      db.execute_sql(sql)
      db.query('test_join')
      ```
      ```text
      Out:
                      code  name area industry   open   high    low  close
      0   000001.SZ  平安银行   深圳       银行  14.13  14.44  14.06  14.24
      1   000001.SZ  平安银行   深圳       银行  14.35  14.37  14.14  14.29
      2   001227.SZ  兰州银行   甘肃       银行   3.60   3.61   3.59   3.60
      3   001227.SZ  兰州银行   甘肃       银行   3.60   3.63   3.58   3.63
      4   002142.SZ  宁波银行   浙江       银行  30.38  31.38  30.15  30.66
      ..        ...   ...  ...      ...    ...    ...    ...    ...
      79  601997.SH  贵阳银行   贵州       银行   5.65   5.72   5.64   5.71
      80  601998.SH  中信银行   北京       银行   4.97   5.09   4.95   5.08
      81  601998.SH  中信银行   北京       银行   5.09   5.15   5.06   5.14
      82  603323.SH  苏农银行   江苏       银行   4.98   5.09   4.96   5.00
      83  603323.SH  苏农银行   江苏       银行   5.01   5.05   4.97   5.04

      [84 rows x 8 columns]
      ```

  - <b>create_table</b> 
    - <b>功能</b>：创建因子表（因子表用来储存多个同频因子）
    - <b>参数</b>:
      >  名称|类型|说明
      >  ----|----|----
        table_name|String|数据表名
        column_info|Dict|表头信息 {列名:属性} 默认值: {'datetime':'timestamp','code':'string','seqnum':'double'}
        freq|String|频率信息，包括：快照数据：['tick','level1','level2']，分钟数据：['m','min','minute']，小时数据：['h','hour']，日频数据：['d','daily','day']

    - <b>返回值</b>：
      无

      ```python
      In:
        db.create_table('stock_bar_daily_test',
                        column_info={'code':'string','datetime':'timestamp',
                        'trade_day':'string','open':'double','high':'double',
                        'low':'double','close':'double','volume':'int',
                        'turnover':'double','vwap':'double','factor':'double'},
                        freq='daily')
      ```

  - <b>_create_table</b>
    - <b>功能</b>：创建数据表
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
        table_name|String|数据表名
        column_info|Dict|表头信息 {列名:属性}
        table_type|String|数据表类型 默认值:timelyre 可选类型:orc,text
        bucketcolumn|String|分桶用字段
        bucketquantity|Int|分桶数量
        timecol|String|时序列列名
        tags|String|索引列列名,一般为标的代码
        uniqcols|String|主键字段,str,联合主键写在同一字符串中用,号隔开
        shard_group_duration|Int|分片时间长度
        isExternal|Bool|是否是外表
        location|String|外表所在hdfs路径
        col_delimiter|String|外表文件分隔符
    - <b>返回值</b>：无
      
      create_table函数的底层调用，支持3种表类型：timelyre,orc,text外表。对于timelyre表需要指定：table_name,column_info,table_type选择'timelyre',timecol,tags,shard_group_duration,如果timecol和tags并不是唯一索引需要另外指定uniqcols作为区分，比如高频委托和成交数据可以另外指定biz_index作为联合主键。对于orc表需要指定：table_name,column_info,table_type选择'orc'，如果需要orc表支持事务操作必须指定bucketcolumn和bucketquantity。对于text外表需要指定：table_name,column_info,table_type选择'text',isExternal选择True,location,col_delimiter。
    
      ```python
      In:
        #创建timelyre表
        db._create_table(table_name='timelyre_test',
                         column_info={'code':'string',
                                      'datetime':'timestamp',
                                      'open':'double',
                                      'high':'double',
                                      'low':'double',
                                      'close':'double'},
                         table_type='timelyre',
                         timecol='datetime',
                         tags='code',
                         shard_group_duration=63072000)
        #创建orc表
        db._create_table(table_name='orc_test',
                         column_info={'code':'string',
                                      'industry':'string',
                                      'area':'string'},
                         table_type='orc',
                         bucketcolumn='code',
                         bucketquantity=10)
        #创建text外表
        db._create_table(table_name='text_test',
                         column_info={'code':'string',
                                      'industry':'string',
                                      'area':'string'},
                         table_type='text',
                         isExternal=True,
                         location='/tmp/out_tables/text_test.txt',
                         col_delimiter=',')
      ```

  - <b>delete_table</b>
    - <b>功能</b>：删除数据表
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
      table_name|String|数据表名

    - <b>返回值</b>：
      无

      ```python
      In:
        db.delete_table('db_test')
      ```
  - <b>delete_view</b> 
    - <b>功能</b>：删除视图
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
      view_name|String|视图名
    - <b>返回值</b>：无

  - <b>truncate_table</b> 
    - <b>功能</b>：清空数据表内容(只用于orc事务表)
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
        table_name|String|数据表名
    - <b>返回值</b>：
    无

    ```python
    In:
      db.truncate_table('orc_test')
    ```

  - <b>delete_row</b> 
    - <b>功能</b>：删除记录
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
        table_name|String|数据表名
        condition|Dict|筛选条件,{<字段>:<条件>}<br>条件可以为单值,tuple,list<br>分别表示取单值,取值范围(闭区间),取多值

    - <b>返回值</b>：
    无

    ```python
    In:
      db.delete_row('orc_test',condition={'field':'code'})
    ```

  - <b>update_row</b> 
    - <b>功能</b>：更新记录
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
        table_name|String|数据表名
        column_map|Dict|更改内容,{<字段>:<值>}
        condition|Dict|筛选条件,{<字段>:<条件>}<br>条件可以为单值,tuple,list<br>分别表示取单值,取值范围(闭区间),取多值

    - <b>返回值</b>:
    无

    ```python
    In:
      db.update_row('orc_test',column_map={'explain':'test update'},condition={'field':'datetime'})
    ```

  - <b>insert_values</b> 
    - <b>功能</b>：批量插入数据
    - <b>参数</b>：
      > 名称|类型|说明
      > ----|----|----
      table_name|String|数据表名
      values|List/tuple/dict/pandas.DataFrame|插入数据
      if_file|Bool|是否以文件形式传输, 默认值True
      batch|Int|非文件传输时每批次记录条数
      parallelism|Int|并行进程数
    - <b>返回值</b>：
      无

    ```python
    In:
      import pandas as pd
      data = pd.DataFrame(data, columns=['datetime','high','low','open','close','code'])
      db.insert_values('stock_data', data)
    ```

  - <b>query</b> 
    - <b>功能</b>：查询数据表
    - <b>参数</b>：
      >名称|类型|说明
      >----|----|----
      table_name|String|数据表名
      query|String|sql查询语句，使用query传入sql查询语句默认返回Dataframe。
      fields|List/String|字段名
      start|String/date/datetime|查询起始时间
      end|String/date/datetime|查询截止时间
      universe|String/List|查询代码
      raw|bool|默认为False,raw为True时使用HTTP接口传输数据,不建议选择
      other_condition|Dict|其他筛选条件,{<字段>:<条件>}<br>条件可以为单值,tuple,list<br>分别表示取单值,取值范围(闭区间),取多值
      size|Integer|返回记录条数
      return_type|String|取值为 "list"(返回列表) 或 "dataframe"(返回pandas.DataFrame),该参数只在raw为True时有效,否则默认返回Dataframe

    - <b>返回值</b>：
      用列表或DataFrame盛放的数据
    
    可以直接传入sql查询语句，但是不支持较复杂的联表查询。

    ```python
    In:
      db.query(query='select * from stock_bar_1day where trade_day > "2022-03-01" and trade_day < "2022-03-05"')
    ```
    ```text
    Out:
                  code            datetime   trade_day   open   high    low  close  \
    0      000001.SZ 2022-03-02 15:00:00  2022-03-02  15.79  15.87  15.66  15.68   
    1      000001.SZ 2022-03-03 15:00:00  2022-03-03  15.73  15.81  15.63  15.71   
    2      000001.SZ 2022-03-04 15:00:00  2022-03-04  15.62  15.63  15.28  15.33   
    3      000002.SZ 2022-03-02 15:00:00  2022-03-02  19.41  19.67  19.11  19.32   
    4      000002.SZ 2022-03-03 15:00:00  2022-03-03  19.35  19.73  19.34  19.49   
    ...          ...                 ...         ...    ...    ...    ...    ...   
    15829  688981.SH 2022-03-03 15:00:00  2022-03-03  50.85  51.47  50.71  51.06   
    15830  688981.SH 2022-03-04 15:00:00  2022-03-04  50.80  51.46  50.58  50.88   
    15831  689009.SH 2022-03-02 15:00:00  2022-03-02  57.60  57.98  56.86  57.02   
    15832  689009.SH 2022-03-03 15:00:00  2022-03-03  57.03  57.39  55.60  55.66   
    15833  689009.SH 2022-03-04 15:00:00  2022-03-04  55.01  55.55  54.30  54.75   

              volume      turnover    vwap      factor  limit_up  limit_down  
    0       76076086  1.196322e+09  15.725  121.719130   2131.30     1744.24  
    1       57828505  9.081716e+08  15.705  121.719130   2099.65     1717.46  
    2       99093566  1.523794e+09  15.377  121.719130   2103.31     1721.11  
    3       89209507  1.727309e+09  19.362  151.248576   3224.62     2637.78  
    4      131903840  2.574130e+09  19.515  151.248576   3214.03     2630.21  
    ...          ...           ...     ...         ...       ...         ...  
    15829   13889190  7.100505e+08  51.123    1.000000     60.70       40.46  
    15830   12120290  6.183616e+08  51.019    1.000000     61.27       40.85  
    15831     519105  2.965435e+07  57.126    1.000000     69.56       46.38  
    15832     835262  4.713651e+07  56.433    1.000000     68.42       45.62  
    15833    1323586  7.276419e+07  54.975    1.000000     66.79       44.53  

    [15834 rows x 13 columns]
    ```
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

  - <b>query_raw</b> 
    - <b>功能</b>：普通查询
    - <b>参数</b>：
    > 名称|类型|说明
    > ----|-----|----
    table_name|String|查询表名
    fields|List/String|查询字段
    condition|Dict|查询条件，{<字段>:<条件>}，方式同query方法
    raw|bool|默认为False，使用query_as_df函数，否则用query_raw函数

    - <b>返回值</b>：
      用列表或DataFrame盛放的数据

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

  - <b>query_calendar</b> 
    - <b>功能</b>：查询交易日
    - <b>参数</b>：
    > 名称|类型|说明
    >----|----|----
    start|String|查询起始日期
    end|String|查询截止日期
    exchange|String|交易所名称
    table_name|String|交易日存储表名

    - <b>返回值</b>：
      日期列表

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
  - <b>create_factor_table</b>
    - <b>功能</b>：创建因子表
    - <b>参数</b>：
    > 名称|类型|说明
    >----|----|----
    table_name|String|因子表名
    freq|String|因子频率: <br>快照数据 :['tick','level1','level2'] <br>分钟数据 : ['m','min','minute'] <br>小时数据 : ['h','hour'] <br>日频数据 : ['d','daily','day']
    description|String|因子描述

    ```python
    In:
      from transmatrix.data_api import create_factor_table
      create_factor_table('factor_test_table',freq='daily',description='this is a test')
    ```

  - save_factor 
    - <b>功能</b>：保存因子
    - <b>参数</b>
    > 名称|类型|说明
    >----|----|----
    table_name|String|因子表名
    data|dataframe|因子数据
    freq|String|因子频率

    ```python
    In:
      import pandas as pd
      from transmatrix.data_api import save_factor
      df = pd.DataFrame(data=[['2022-01-01','000001.SZ',0.1],['2022-01-02','000001.SZ',0.2]],columns=['datetime','code','value'])
      save_factor('factor_test_table', data=df)
    ```

  - get_column_info_from_df 
    - <b>功能</b>：从dataframe中获取列信息
    - <b>参数</b>：
    > 名称|类型|说明
    >----|----|----
    df|pandas.Dataframe|因子数据

    - 返回
      - Dict 数据每列对应类型

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

  - clear_private_datacache 
    - <b>功能</b>：清理个人数据库缓存
    - <b>参数</b>：
        无
    - <b>返回值</b>：
        无