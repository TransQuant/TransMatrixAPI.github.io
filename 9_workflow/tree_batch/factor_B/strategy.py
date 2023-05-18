from transmatrix.strategy import SignalStrategy
from transmatrix.data_api import create_data_view, NdarrayData, DataView3d, DataView2d
from scipy.stats import zscore

class ReverseSignal(SignalStrategy):
    
    def init(self):
        self.add_clock(milestones='09:35:00')
        self.subscribe_data(
            'pv', ['default','stock_bar_1day',self.codes,'open,high,low,close', 10]
        )
        self.pv: DataView3d
        
    def pre_transform(self):
        if 'reverse' not in self.pv.fields:
            pv = self.pv.to_dataframe()
            ret = (pv['close'] / pv['close'].shift(1) - 1).fillna(0)
            reverse = -ret.rolling(window = 5, min_periods = 5).mean().fillna(0)
            reverse = zscore(reverse, axis = 1, nan_policy='omit')
            self.reverse: DataView3d = create_data_view(
                NdarrayData.from_dataframes({'reverse':reverse})
            )
            self.reverse.align_with(self.pv)
            
    def on_clock(self):
        self.update_signal(self.reverse.get('reverse'))