import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os, sys
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from transmatrix.evaluator.signal import SignalEvaluator
from evaluator_tool.evaluator_helper import evaluate_factor, panel_concat_nonstock
from evaluator_tool.plot_utils import plot_heatmap_monthly, plot_heatmap_yearly


class EvalFull(SignalEvaluator):
    def init(self):
        self.subscribe_data(
            'pv', ['*','stock_bar_1day',self.codes,'open,high,low,close', 10]
        )
        self.subscribe_data(
            'meta', ['*','critic_data', self.codes, 'is_hs300,is_zz500,ind', 10]
        )
        self.subscribe_data(
            'benchmark', ['*','stock_index', '000300.SH', 'close', 10]
        )
        
    def regist(self):
        pass
    
    def critic(self):
        critic_data = self.aligned_data['pv'].to_dataframe()
        critic_data.update(self.aligned_data['meta'].to_dataframe())
        critic_data.update({'signal': self.strategy.signal})
        # benchmark_data = self.aligned_data['benchmark'].to_dataframe()[['close']]
        benchmark_data = panel_concat_nonstock(self.aligned_data['benchmark'])
        
        verbose = False
        if not self.matrix.in_batch_mode:
            print('开始因子评价')
            print('--'*50)
            verbose = True
        factor_data = critic_data['signal']
        perf = evaluate_factor(factor_data, critic_data, benchmark_data, verbose = verbose)
        self.perf = perf
        if not self.matrix.in_batch_mode:
            print('完成因子评价')
            print('--'*50)

    def show(self):
        report_path = os.path.join(Path(self.matrix.config_source).parent.absolute(),'report')
        print(f'saving report to {report_path}')
        now = datetime.now()
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']        
        
        n = 11
        fig, axs = plt.subplots(n,1, figsize = (12, 8*n))
        self.perf['cover_count'].plot(title = 'Stock Count with Factor', ax = axs[0])
        self.perf['top_excess_return'].plot(title = 'Excess Return', ax = axs[1])
        self.perf['ma_top_excess_return'].plot(title = 'Avg 20 Period', ax = axs[2])        
        self.perf['rank_ic_ser'].plot(title = 'Rank IC', ax = axs[3])
        self.perf['ma_rank_ic_ser'].plot(title = 'Avg 20 Period', ax = axs[4])
        
        # print('-'*100)
        # print('IC&RankIC')
        # print(self.perf['ic_stats'])
        
        example_string = self.perf['ic_stats'].to_string()
        if not os.path.exists(report_path): os.mkdir(report_path)
        with open(os.path.join(report_path, f'report_{now}.txt'),'w') as f:
            f.write(example_string) 
        
        self.perf['ic_cumsum'].plot(title = 'IC_cumsum', ax = axs[5])
        
        plot_heatmap_monthly(self.perf['monthly_rank_ic_mean'], title='Rank IC by Month', ax=axs[6])
        plot_heatmap_monthly(self.perf['monthly_excess_return'], title='Excess Return by Month', ax=axs[7])
        plot_heatmap_yearly(self.perf['ind_ic_yearly_mean'], title='Ind IC by Year', ax=axs[8])
        
        self.perf['se_ic_lag'].plot(title = 'IC Decay', ax = axs[9])
        self.perf['yearly_top_excess_net'].plot(title = 'Top Yearly Excess Return', ax = axs[10])
        fig.savefig(os.path.join(report_path,f'report_{now}.png'), bbox_inches = 'tight')
        if not self.matrix.in_batch_mode:
            plt.show()
        
        
        
        
        
        
        
        