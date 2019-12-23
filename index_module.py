import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np


# input_dir = os.getcwd()+'\\Input' # where files from scrape module are stored


class Get_Weights(object):
    
    def __init__(self,
                input_dir):
        self.input_dir = input_dir
        
    def get_coins(self):
        # iteratively read csv files
        csv_list = os.listdir(self.input_dir)
        csv_list = [k for k in csv_list if '.csv' in k]
        coins = [x.split('.')[0] for x in csv_list]
        self.coins = coins
        self.csv_list = csv_list
        
    def make_currency_dict(self):
#         build dictionary from csv list
        df_dict = {}
        for idx, i in enumerate(self.csv_list):
            df_dict.update({f'{self.coins[idx]}' : pd.read_csv(input_dir+f'\\{i}')})
        self.df_dict = df_dict
        
    
    def join_dfs(self):
        # cleaning data
        for i in range(len(self.df_dict)):
            self.df_dict[self.coins[i]].Volume = self.df_dict[self.coins[i]].Volume.replace('-', str(0))
            self.df_dict[self.coins[i]].Market_Cap = self.df_dict[self.coins[i]].Market_Cap.replace('-', str(0))
            self.df_dict[self.coins[i]].Volume = self.df_dict[self.coins[i]].Volume.apply(lambda x : str(x))
            self.df_dict[self.coins[i]].Volume = self.df_dict[self.coins[i]].Volume.apply(lambda x: x.replace(' ', ''))
            self.df_dict[self.coins[i]].Market_Cap = self.df_dict[self.coins[i]].Market_Cap.apply(lambda x : str(x))
            self.df_dict[self.coins[i]].Market_Cap = self.df_dict[self.coins[i]].Market_Cap.apply(lambda x: x.replace(' ',''))
            self.df_dict[self.coins[i]].Volume = pd.to_numeric(self.df_dict[self.coins[i]].Volume)
            self.df_dict[self.coins[i]].Market_Cap = pd.to_numeric(self.df_dict[self.coins[i]].Market_Cap)
        
        joined_df = pd.DataFrame(data = self.df_dict[self.coins[i]].Date , columns = ['Date'])
    
        for i in range(len(self.df_dict)):
            joined_df = pd.merge(joined_df, self.df_dict[self.coins[i]], on='Date', how='left')

            joined_cols_matrix = [[f'{i}_Open', f'{i}_High',
                                    f'{i}_Low', f'{i}_Close',
                                    f'{i}_Volume', f'{i}_Market_Cap'] for i in self.coins]
        joined_df.Date = pd.to_datetime(joined_df['Date'])
        joined_df.set_index(['Date'], inplace=True)
        joined_cols = []
        for sublist in joined_cols_matrix:
            for val in sublist:
                joined_cols.append(val)
        joined_df.columns = joined_cols
        joined_df.dropna(inplace=True)
        
        # adding the `Date` column back in will be helpful for dealing with non-zero mulitples for dynamicly weighting our values
        weighted_df = pd.DataFrame()
        joined_df['Date'] = joined_df.index
        joined_cols = joined_df.columns.tolist()
        joined_cols = joined_cols[-1:] + joined_cols[:-1]
        self.joined_df = joined_df[joined_cols]
        
    def get_weights(self):
        weighted_open = list()
        weighted_high = list()
        weighted_low = list()
        weighted_close = list()
        for i in range(len(self.joined_df)):
            
            # Open
            
            a = 0
            for j in range(len(self.coins)):
                open_val = self.joined_df.loc[self.joined_df.index[i],f'{self.coins[j]}_Open']
                market_cap = self.joined_df.loc[self.joined_df.index[i],f'{self.coins[j]}_Market_Cap']

                a += (open_val*market_cap)
            k = [self.joined_df.iloc[i,(k+1)*6] for k in range(len(self.coins))]

            result = a/np.sum(k)
            weighted_open.append(result)
            
            # High

            a = 0
            for j in range(len(self.coins)):
                high_val = self.joined_df.loc[self.joined_df.index[i],f'{self.coins[j]}_High']
                market_cap = self.joined_df.loc[self.joined_df.index[i],f'{self.coins[j]}_Market_Cap']

                a += (high_val*market_cap)
            k = [self.joined_df.iloc[i,(k+1)*6] for k in range(len(self.coins))]
            result = a/np.sum(k)
            weighted_high.append(result)
            
            # Low

            a = 0
            for j in range(len(self.coins)):
                low_val = self.joined_df.loc[self.joined_df.index[i],f'{self.coins[j]}_Low']
                market_cap = self.joined_df.loc[self.joined_df.index[i],f'{self.coins[j]}_Market_Cap']

                a += (low_val*market_cap)
            k = [self.joined_df.iloc[i,(k+1)*6] for k in range(len(self.coins))]
            result = a/np.sum(k)
            weighted_low.append(result)
            
            # Close

            a = 0
            for j in range(len(self.coins)):
                close_val = self.joined_df.loc[self.joined_df.index[i],f'{self.coins[j]}_Close']

                market_cap = self.joined_df.iloc[i,(j+1)*6]

                a += (close_val*market_cap)
            k = [self.joined_df.iloc[i,(k+1)*6] for k in range(len(self.coins))]
            result = a/np.sum(k)
            weighted_close.append(result)

        weighted_df = pd.DataFrame({'weighted_open':weighted_open, 
                                    'weighted_high':weighted_high, 
                                    'weighted_low':weighted_low, 
                                    'weighted_close':weighted_close}, 
                                    index=self.joined_df.index)
        # save CSV
        weighted_df.to_csv(f'{len(self.coins)}currencies_weighted_index.csv')
        # return the dataframe for exploration
        return weighted_df