### 测例说明
本测例展示了一个ETF基金T0策略，包括特征工程、模型构建、交易信号生成、策略回测。

### 特征工程

- 确定参考标的
```python
In:
    desc = {"table_name": 'stock_fund', "start": START, "end": END, "fields": 'is_hs300', "codes": "*"}
    basket = Dataset(
        data_model = 'ndarray', describe=desc
    ).load_data()
    basket = basket.to_dataframe()['is_hs300']
    basket = [k for k,v in basket.sum().to_dict().items() if v > 0]

    desc2 = {"table_name": 'stock_bar_daily', "start": '20201001', "end": START, "fields": 'turnover', "codes": basket}
    trade_vol = Dataset(
        data_model='ndarray', describe=desc2
    ).load_data()

    trade_vol = trade_vol.to_dataframe()['turnover'].sum()
    trade_vol.sort_values(ascending = False)
    ref_codes = list(trade_vol.sort_values(ascending = False).index[:10])
    ref_codes
```
```text
Out:
    loading data None__stock_fund__is_hs300 from database.

    loading data None__stock_bar_daily__turnover from database.

    ['002594.SZ',
    '300059.SZ',
    '601318.SH',
    '600519.SH',
    '601012.SH',
    '000725.SZ',
    '000858.SZ',
    '002475.SZ',
    '600196.SH',
    '002241.SZ']
```

- 查询数据
```python
In:
    engine = DataEngine()

    desc = {"db_name": 'common2', "table_name": 'stock_snapshot', "start": START, "end": END, "fields": DEPTH_COLS, "codes": [ETF]}
    etf_depth = Dataset(
        data_model = 'ndarray', describe=desc
    )

    desc2 = {"db_name": 'common2', "table_name": 'stock_snapshot', "start": START, "end": END, "fields": DEPTH_COLS, "codes": ref_codes}
    ref_depth = Dataset(
        data_model = 'ndarray', describe=desc2
    )

    engine.regist(etf_depth)
    engine.regist(ref_depth)
    engine.load_data()
    engine.cache()

    ref_depth = ref_depth.data.to_dataframe()
    etf_depth = etf_depth.data.to_dataframe()
```

```text
Out:
    loading data common2__stock_snapshot__datetime,code,volume,turnover,bid_price_1,ask_price_1 from database.

    loading data common2__stock_snapshot__datetime,code,volume,turnover,bid_price_1,ask_price_1 from database.

    Cashing common2__stock_snapshot__datetime,code,volume,turnover,bid_price_1,ask_price_1 to pickle file: dataset_02338ce7-5e4b-4176-ae55-6bcd3f94472a ....Cashing common2__stock_snapshot__datetime,code,volume,turnover,bid_price_1,ask_price_1 to pickle file: dataset_a9ccae75-83cb-48ce-88c3-0835acddbd4f ....
```

- 特征加工
```python
In:
    # 参考股票 features
    ref_mid = ((ref_depth['ask_price_1'] + ref_depth['bid_price_1']) / 2).ffill()
    ref_fhp = cal_fhp(ref_mid)

    # etf features
    vol = etf_depth['volume'].rename(columns = {ETF:'volume'})
    vol['date'] = vol.index.date
    vol = vol.groupby('date').diff().fillna(0)
    vol['date'] = vol.index.date
    vol = vol.groupby('date').rolling(100, min_periods = 1).mean()
    vol.index.names = ['date', 'datetime']
    vol.index = vol.reset_index()['datetime']

    mid = ((etf_depth['ask_price_1'] + etf_depth['bid_price_1']) / 2).ffill()
    fhp = cal_fhp(mid).rename(columns = {ETF: 'fhp'})
    zscore = cal_zscore(mid).rename(columns = {ETF:'zscore'})

    features = pd.concat([ref_fhp, vol, fhp, zscore, mid.rename(columns = {ETF:'mid'})], axis = 1).ffill().dropna()
    features['date'] = features.index.date
    features.index.names = ['datetime']
    features = features.groupby('date').apply(cut_tail).drop('date', axis = 1).reset_index().set_index('datetime').drop('date',axis = 1)
    mid = features['mid']
    features.drop('mid',axis = 1, inplace = True)

    labels = pd.DataFrame()
    for span in [5,10,15,20]:
        ret = 1000 * (-mid.diff(-span) / mid).fillna(0).rename(f'ret_{span}')
        labels = pd.concat([labels, ret], axis = 1)
```
```python
In:
    labels.describe()
```
<div align=center>
<img width="1000" src="8_测例代码\pics\ETF基金fe1.png"/>
</div>
<div align=center style="font-size:12px">labels</div>
<br />

```python
In:
    features.describe()
```
<div align=center>
<img width="1000" src="8_测例代码\pics\ETF基金fe2.png"/>
</div>
<div align=center style="font-size:12px">features</div>
<br />

- 数据保存
```python
In:
    import pickle, os
    data_path = 'data'
    os.makedirs(data_path, exist_ok = True)

    with open(os.path.join(data_path, 'labels.pkl'), 'wb') as f:
        pickle.dump(labels, f)
        
    with open(os.path.join(data_path, 'features.pkl'), 'wb') as f:
        pickle.dump(features, f)
```

### 模型构建
- 加载数据
```python
In:
    import os, pickle
    data_path = 'projects/演示案例/策略服务-回测场景支持/ETF基金T0/data'
    with open(os.path.join(data_path, 'features.pkl'), 'rb') as f:
        _features = pickle.load(f)
    with open(os.path.join(data_path, 'labels.pkl'), 'rb') as f:
        _labels = pickle.load(f)
```
- 选取训练/训练集
```python
In:
    import pandas as pd
    start = pd.to_datetime('20210101')
    end = pd.to_datetime('20210601')
    features = _features[(_features.index > start) & (_features.index < end)]
    labels = _labels[(_labels.index > start) & (_labels.index < end)]
```
- 导入模型
```python
In:
    from sklearn.linear_model import Lasso, Ridge, LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import r2_score, mean_squared_error
```
```python
In:
    split = int(0.8 * len(features))
    train_x = features[:split]
    test_x = features[split:]
    train_y = labels[:split]
    test_y = labels[split:] 
```
- 备选模型池模型
```python
In:
    lasso = Lasso(); lasso.name = 'lasso'
    ridge = Ridge(); ridge.name = 'ridge'
    ols = LinearRegression(); ols.name = 'ols'

    for model in lasso, ridge, ols:
        print(model.name)
        print('_'*100)
        for label in train_y.columns:
            model.fit(train_x, train_y[label])
            pred_y = model.predict(test_x)
            print(label, r2_score(test_y[label], pred_y), mean_squared_error(test_y[label], pred_y))
        print('_'*100)
        print(' '*100)
```
```text
Out:
    lasso
    ____________________________________________________________________________________________________
    ret_5 -0.00020464356887206492 0.019763796810821733
    ret_10 -0.00043741559966670174 0.0369777098777261
    ret_15 -0.0006855888095866902 0.05338197946499039
    ret_20 -0.0009402616712490541 0.06998329899155226
    ____________________________________________________________________________________________________
                                                                                                        
    ridge
    ____________________________________________________________________________________________________
    ret_5 0.008082603987668135 0.01960004284518924
    ret_10 0.005393780192949116 0.03676217988764639
    ret_15 0.002509108540690752 0.053211557036351005
    ret_20 3.6216858570692345e-05 0.0699150259971209
    ____________________________________________________________________________________________________
                                                                                                        
    ols
    ____________________________________________________________________________________________________
    ret_5 0.008081791943687633 0.019600058890977805
    ret_10 0.005392808735381616 0.03676221579421639
    ret_15 0.0025077068908156974 0.05321163180793329
    ret_20 3.407949205280758e-05 0.06991517543656879
    ____________________________________________________________________________________________________
```
- 模型保存
```python
In:
    import pickle
    lasso = Lasso(); lasso.name = 'lasso'
    ridge = Ridge(); ridge.name = 'ridge'
    ols = LinearRegression(); ols.name = 'ols'

    os.makedirs('models', exist_ok = True)
    for model in lasso, ridge, ols:
        for label in train_y.columns:
            model.fit(features, labels[label])
            path = f'models/{model.name}_{label}.model'
            print(f'saving {path}')
            with open(path,'wb') as f:
                pickle.dump(model, f)
```
```text
Out:
    saving models/lasso_ret_5.model
    saving models/lasso_ret_10.model
    saving models/lasso_ret_15.model
    saving models/lasso_ret_20.model
    saving models/ridge_ret_5.model
    saving models/ridge_ret_10.model
    saving models/ridge_ret_15.model
    saving models/ridge_ret_20.model
    saving models/ols_ret_5.model
    saving models/ols_ret_10.model
    saving models/ols_ret_15.model
    saving models/ols_ret_20.model
```

### 交易信号生成
- 加载数据
```python
In:
    import os, pickle, sys
    data_path = 'data'

    with open(os.path.join(data_path, 'features.pkl'), 'rb') as f:
        _features = pickle.load(f)
        
    import pandas as pd

    from transmatrix.data_api import Dataset

    from helpers import DEPTH_COLS
    ETF = '510300.SH'
    START = '20210601'
    END = '20210701'

    start = pd.to_datetime('20210601')
    end = pd.to_datetime('20210701')
    features = _features[(_features.index > start) & (_features.index < end)]

    desc = {"db_name": 'common2', "table_name": 'stock_snapshot', "start": START, "end": END, "fields": DEPTH_COLS, "codes": [ETF]}
    etf_depth = Dataset(
        data_model = 'ndarray', describe=desc
    ).load_data().to_dataframe()
```
```text
Out:
    loading data common2__stock_snapshot__datetime,code,volume,turnover,bid_price_1,ask_price_1 from database.
```

- 加载模型
```python
In:
    import os, pickle
    path = 'models'
    files = [os.path.join(path, x) for x in os.listdir(path)]
    models = {}

    for file in files:
        if 'ipynb_checkpoints' in file:
            continue
        with open(file,'rb') as f:
            models[file.split('/')[-1].split('.')[0]] = pickle.load(f)
            
    models
```
```text
Out:
    {'lasso_ret_5': Lasso(),
    'lasso_ret_10': Lasso(),
    'lasso_ret_15': Lasso(),
    'lasso_ret_20': Lasso(),
    'ridge_ret_5': Ridge(),
    'ridge_ret_10': Ridge(),
    'ridge_ret_15': Ridge(),
    'ridge_ret_20': Ridge(),
    'ols_ret_5': LinearRegression(),
    'ols_ret_10': LinearRegression(),
    'ols_ret_15': LinearRegression(),
    'ols_ret_20': LinearRegression()}
```
```python
In:
    import pandas as pd
    signal = pd.DataFrame(index = features.index)

    for name, model in models.items():
        ser = pd.Series(model.predict(features), index = features.index, name = name) / 1000
        signal = pd.concat([signal, ser], axis = 1)

    mid = 0.5 * (etf_depth['bid_price_1'] + etf_depth['ask_price_1'])[ETF].rename('mid')
    idx = list(set(mid.index) & set(signal.index))
    idx.sort()
    signal = pd.concat([signal, mid], axis = 1)
    signal.ffill(inplace = True)

    for col in signal.columns: 
        if col != 'mid': signal[col] = signal['mid'] * (signal[col] + 1)  
        
    signal['reverse_20'] = signal['mid'].shift(20)
    signal['reverse_40'] = signal['mid'].shift(40)
    signal['reverse_60'] = signal['mid'].shift(60)

    signal = signal.loc[idx]
    signal.drop('mid', axis = 1, inplace = True)

    signal['code'] = ETF
    signal.index.name = 'datetime'
    signal.reset_index(inplace = True)
    signal
```
<div align=center>
<img width="1000" src="8_测例代码\pics\ETF基金ms1.png"/>
</div>
<div align=center style="font-size:12px">signal</div>
<br />

- 保存推理结果（因子）
```python
In:
    from transmatrix.data_api import create_factor_table, save_factor
    from transmatrix.data_api import Database
    from transmatrix.setting import PRIVATE_DB_NAME
    db = Database(PRIVATE_DB_NAME)
    db.delete_table('factor_hft_demo')
    create_factor_table('factor_hft_demo')
    save_factor('factor_hft_demo',signal, freq = 'tick')
```
```text
Out:
    表factor_hft_demo已删除
    created factor_hft_demo in private_db.
    因子库数据更新: common2 factor_hft_demo : ['lasso_ret_5', 'lasso_ret_10', 'lasso_ret_15', 'lasso_ret_20', 'ridge_ret_5', 'ridge_ret_10', 'ridge_ret_15', 'ridge_ret_20', 'ols_ret_5', 'ols_ret_10', 'ols_ret_15', 'ols_ret_20', 'lgbm_ret_5', 'lgbm_ret_10', 'lgbm_ret_15', 'lgbm_ret_20', 'reverse_20', 'reverse_40', 'reverse_60']
    更新完毕.
```

### 策略回测
- 初始化组件
```python
In:
    from transmatrix.workflow.configer import Configer
    from transmatrix.workflow.run_yaml import build_matrix
    cfg = Configer('config.yaml')
    mat = build_matrix(cfg)
    %time mat.init()
```
```text
Out:
    loading data xwq1_private__factor_hft_demo__* from database.

    loading data common2__stock_snapshot__* from database.

    loading data common2__stock_bar_1day__close from database.

    Cashing xwq1_private__factor_hft_demo__* to pickle file: dataset_b25351f3-3675-4403-9833-8ff1c24f08f8 ....Cashing common2__stock_snapshot__* to pickle file: dataset_09dc71f4-480a-44a3-acf3-c2e1c0b5cc04 ....
    Cashing common2__stock_bar_1day__close to pickle file: dataset_615456ae-3b27-4ffc-99b9-a6ac1a770239 ....

    CPU times: user 6.59 s, sys: 2.09 s, total: 8.68 s
    Wall time: 11.9 s
```
- 运行回测
```python
In:
    %time mat.run()
```
```text
Out:
    CPU times: user 3.52 s, sys: 31.4 ms, total: 3.55 s
    Wall time: 3.56 s
```
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