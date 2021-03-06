from backtest_base import *

class backtest_strategy(backtest_base):

    def go_long(self, date, units):
        self.open_long_trade(units, date=date)
            
    def go_short(self, date, units):
        self.open_short_trade(units, date=date)

    def add_indicators(self, WindowLenght):
        
        for e_granularity in self.data_granularity:
            self.data[e_granularity].loc[:, 'H-L'] = self.data[e_granularity].loc[:,'bid_h'] - self.data[e_granularity].loc[:,'bid_l']
            self.data[e_granularity].loc[:, 'cum-move'] = self.data[e_granularity].loc[:,'H-L'].rolling(WindowLenght+1).sum()
            self.data[e_granularity].loc[:, 'net-move'] = np.abs( self.data[e_granularity].loc[:,'bid_c'] - self.data[e_granularity].loc[:,'bid_c'].shift(WindowLenght))
            self.data[e_granularity].loc[:, 'ratio-move'] = self.data[e_granularity].loc[:, 'net-move'] / self.data[e_granularity].loc[:, 'cum-move']
            self.data[e_granularity] = self.data[e_granularity].dropna()
                
    def run_strategy(self,window_lenght):

        self.add_indicators(window_lenght)
            
        for e_granularity in self.data_granularity:
            self.data[e_granularity] = self.data[e_granularity].loc[(self.data[e_granularity].index >= self.start_date) & (self.data[e_granularity].index <= self.end_date),:]

        print('-' * 55)
        msg = 'Running strategy v.2.0'
        msg += '\nFixed costs %.2f | ' % self.ftc
        msg += 'proportional costs %.4f' % self.ptc
        print(msg)
        
        for date, _ in self.data[self.decision_frequency].iterrows():
            
            if date >=self.date_to_start_trading:

                ''' 
                Get signal
                Create buy/sell order
                -	Calculate PL
                -	Calculate required margin
                Check all open orders
                - 	Either add to the list
                -	Or eliminate some from list, move to ListofClosedOrders
                '''

                if self.units_net != 0:

                    for etrade in self.listofOpenTrades:
                        
                        if(etrade.unrealizedprofitloss) > 1:
                            
                            self.close_all_trades(date)

                        if(etrade.unrealizedprofitloss) <= -10:

                            self.close_all_trades(date)
                            
                elif self.units_net == 0:
                 
                    #if self.data[self.decision_frequency].loc[date, 'cum-move'] / self.data[self.decision_frequency].loc[date, 'net-move'] < 5: 
                    #if self.data[self.decision_frequency].loc[date, 'cum-move'] / self.data[self.decision_frequency].loc[date, 'net-move'] > 20:
                    #if self.data[self.decision_frequency].loc[date, 'net-move'] < 0.001 and self.data[self.decision_frequency].loc[date, 'cum-move'] > 0.02:
                    #if self.data[e_granularity].loc[date, 'ratio-move'] > 0.20: #>20   
                    if ( self.data[self.decision_frequency].loc[date, 'net-move'] < 0.005 ) and ( self.data[self.decision_frequency].loc[date, 'cum-move'] / self.data[self.decision_frequency].loc[date, 'net-move'] > 20 ):
                        
                        if np.random.random() >= 0.5:
                             
                            self.open_long_trade(1000, date)
                                                         
                        else:
                            
                            self.open_short_trade(1000, date)
                

                self.update(date)
                    
        filename = os.path.join( self.backtest_folder, 'data.xlsx')
        self.data[self.decision_frequency].to_excel(filename)
            
        self.close_all_trades(date)
        self.update(date)
        self.close_out()

        self.calculate_stats()
            
if __name__ == '__main__':
    
     cwd = os.path.dirname(__file__)
     os.chdir(cwd)

     strategy_name = 'strategy v.2.0'
     symbol = 'EUR_USD'
     account_type = 'backtest'
     data_granularity = ['1M']
     decision_frequency = '1M'
     data_granularity.append(decision_frequency)
     data_granularity = list(np.unique(data_granularity))
     start_datetime = datetime.datetime(2020,1,1,0,0,0)
     end_datetime = datetime.datetime(2021,1,1,0,0,0)
     idle_duration_before_start_trading = datetime.timedelta(days=0, hours=1, minutes=0)
     initial_equity = 10000
     marginpercent = 100
     ftc=0.0
     ptc=0.0
     verbose=True
     create_data=False
     window_lenght = 60
     
     # A standard lot = 100,000 units of base currency. 
     # A mini lot = 10,000 units of base currency.
     # A micro lot = 1,000 units of base currency.

     bb = backtest_strategy(strategy_name, symbol, account_type, data_granularity, decision_frequency, start_datetime, end_datetime, idle_duration_before_start_trading, initial_equity, marginpercent, ftc, ptc, verbose, create_data)
     #bb.check_data_quality()
     
     bb.run_strategy(window_lenght)
     
     #bb.plot()

     filename = '{}_data.xlsx'.format(bb.symbol)
     uf.write_df_to_excel(bb.data[bb.decision_frequency], bb.backtest_folder, filename)
     
     filename = '{}_data.pkl'.format(bb.symbol)
     uf.pickle_df(bb.data[bb.decision_frequency], bb.backtest_folder, filename)
             
     bb.write_all_trades_to_excel()
     
     bb.monte_carlo_simulator(250)
 
     #viz.visualize(bb.symbol, bb.data[bb.decision_frequency], bb.listofClosedTrades)
     
     bb.analyze_trades()
     
     bb.calculate_average_number_of_bars_before_profitability()
     