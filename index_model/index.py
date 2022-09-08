#Import the package
import datetime as dt
import pandas as pd
from pandas.tseries.offsets import BMonthEnd

class IndexModel:
    def __init__(self) -> pd.DataFrame:
        """
        Import data
        """
        #import the stock price as DataFrame, set date as index
        self.data = pd.read_csv("Assessment-Index-Modelling-master/data_sources/stock_prices.csv", index_col=0)
        #modify the index type to datetime.
        self.data.index = pd.to_datetime(self.data.index, format='%d/%m/%Y')

    def calc_index_level(self, start_date: dt.date, end_date: dt.date) -> pd.DataFrame:
        """
        Calculate the Total return index
        """
        #Generate the first business day of each month in the backtesting period
        self.business_month_start = pd.date_range(start_date, end_date, freq='BMS')
        #Find out the last buiness day of pervious in order to prepare for 
        #selecting the top 3 stocks based on the market capitalization
        self.business_month_end = self.business_month_start - pd.offsets.BDay()
        #Extract the stock data of the last business in each month
        self.month_end_pd = self.data[self.data.index.isin(self.business_month_end)]
        #return the stock name of top 3 stocks at last business day of each month
        self.month_stock =pd.DataFrame(self.month_end_pd.apply(lambda x: x.nlargest(3).index.tolist(), axis=1).tolist(),  columns=['Stock1', 'Stock2', 'Stock3'])
        #In each month in the backtesting period, calculte the wealth of each day based on the rule
        self.index_number = []
        for i in range(len(self.business_month_start)):
            df = self.data[self.business_month_start[i]:self.business_month_start[i]+BMonthEnd()]
            for j in df.index:
                self.index_number.append(0.5*df.loc[j, self.month_stock.iloc[i,0]] + 0.25*df.loc[j, self.month_stock.iloc[i,1]] + 0.25*df.loc[j, self.month_stock.iloc[i,2]])
        #store the information as dataframe
        self.wealth = {'total_wealth':self.index_number}
        self.index_df = pd.DataFrame(self.wealth)
        self.index_df.index = pd.date_range(start_date, end_date, freq='B')
        #calulate the total return of index
        self.index_df["return"] = self.index_df["total_wealth"].pct_change(1)
        #assgin the beginning value of 100, and modify for the other value as well
        self.index_df["Index_number"] = 100
        for i in range(1, len(self.index_df)):
            self.index_df.iloc[i, 2] = self.index_df.iloc[i-1,2]*(1+self.index_df.iloc[i,1])
        #the Final output
        self.df_final = self.index_df[["Index_number"]]

        

    def export_values(self, file_name: str):
        """
        export the result as csv
        """
        self.df_final.to_csv(file_name)