#pick up notes

"""
add stopped out bull and bear

format the printing out of data frame at the end if possible. make it wider
"""
import pandas as pd
import ccxt
import pandas_ta as ta
import numpy as np
import datetime
import time
import sys
#changeable variables
ticker = "BTC/USDT"
timeframe = "4h"

#how many sets of 100 candles do you want?
batches = 10

#distiguish the borders of a trade and a strong trade
#threshold = 500

#target candle ##WARNING IF BELOW 15 TOP CELLS WON'T POPULATE ALL INDICATORS
target_candle = 30

#new file save name
new_file_name = "prepared_data"
# keys are the acceptable time frames, vals are amount of msecs
timeframe_options = {
    "1s":1000000,
    "1m":60000000,
    "3m":180000000,
    "5m":300000000,
    "10m":600000000,
    "15m":900000000,
    "30m":1800000000,
    "1h":3600000000,
    "2h":7200000000,
    "4h":14400000000,
    "6h":21600000000,
    "8h":28800000000,
    "12h":43200000000,
    "1d":86400000000,
    "3d":259200000000,
    "1w":604800000000,
    "1M":2592000000000,
}
#Exchange
exchange = ccxt.binance()

#set a list to capture all the df's
master_df = []

#get the current time
current_time=int(time.mktime(datetime.datetime.now().timetuple()) * 1000)
try:
    #get the most recent 1000 candles
    candles = exchange.fetch_ohlcv(ticker,timeframe,limit =1000)
except Exception as e:
    print(f"Error : {e}")
    sys.exit(1)
    
#add each batch to master df
master_df.extend(candles)

#set the current time to the value of the earliest candles in the  batch
current_time=candles[0][0]



#for as many times as 1 less than batches as one is already made
for i in range(batches-1):
    #fetch 1000 candles from (current_time)-(numberofmillisecondsin1000) this is the beggining time 1000 candles earlier
    candles = exchange.fetch_ohlcv(ticker,timeframe,limit =1000, since=(current_time - (timeframe_options[timeframe])))
    master_df.extend(candles)
    #update current_time
    current_time=candles[0][0]
    
#put all candle data into a df
master_df = pd.DataFrame(master_df, columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
#format df
df = master_df.sort_values(by="Timestamp",ascending =True)
df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
df = df.drop_duplicates()

'''
#add indicators to df
df["RSI 10"] = df.ta.rsi(10)
df["RSI 14"] = df.ta.rsi()
df["RSI 20"] = df.ta.rsi(20)
df["RSI 30"] = df.ta.rsi(30)

df["OBV"] = df.ta.obv()
df["ATR"] = df.ta.atr()


#add incdicators at previous times
df["rsi -1 change"] = df["rsi"] - df["rsi"].shift(1) 
df["rsi -2 change"] = df["rsi"] - df["rsi"].shift(2) 
df["rsi -3 change"] = df["rsi"] - df["rsi"].shift(3) 
df["rsi -4 change"] = df["rsi"] - df["rsi"].shift(4) 
df["rsi -5 change"] = df["rsi"] - df["rsi"].shift(5) 

df["obv -1 change"] = df["obv"] - df["obv"].shift(1)
df["obv -2 change"] = df["obv"] - df["obv"].shift(2) 
df["obv -3 change"] = df["obv"] - df["obv"].shift(3) 
df["obv -4 change"] = df["obv"] - df["obv"].shift(4) 
df["obv -5 change"] = df["obv"] - df["obv"].shift(5) 

df["atr -1 change"] = df["obv"] - df["obv"].shift(1)
df["atr -2 change"] = df["obv"] - df["obv"].shift(2) 
df["atr -3 change"] = df["obv"] - df["obv"].shift(3) 
df["atr -4 change"] = df["obv"] - df["obv"].shift(4) 
df["atr -5 change"] = df["obv"] - df["obv"].shift(5) 



#calculate the lowest low in the trading period

list_of_lows =  list(df["low"])

new_lows = []
for low in range(len(list_of_lows) - target_candle):
    temp_list = list_of_lows[low + 1:low + 1+ target_candle]
    lowest = min(temp_list)
    new_lows.append(lowest)

for i in range(target_candle):
    new_lows.append(0)
df["lowest"] = new_lows


#calculate the highest high in the trading period

list_of_highs =  list(df["high"])

new_highs = []
for high in range(len(list_of_highs) - target_candle):
    temp_list = list_of_highs[high + 1:high + 1+ target_candle]
    highest = max(temp_list)
    new_highs.append(highest)

for i in range(target_candle):
    new_highs.append(0)
df["highest"] = new_highs

'''

#Remove the first x rows because the indicators have not populated.
df = df.drop(df.index[:target_candle])
#-1 after target candle
#add column that calculates closing price in 20 candles
#df["outcome"] = df["close"].shift(-target_candle)

#net_change column
#df["net_change"] = df["outcome"] - df["close"]

#remove last x rows as has no outcome yet   ####THIS ISNT REMOVING THE LAST ONCE WHOS HIGHEST AND LOWEST POPULATE WRONG.
#df = df.drop(df.index[-target_candle:])

#adding y value to df
#df["y"] = np.where(df["net_change"] < -threshold, 0,
                 #  np.where((df["net_change"] >= -threshold) & (df["net_change"] < 0), 1,
                           # np.where((df["net_change"] >= 0) & (df["net_change"] <= threshold), 2, 3)))
#df["y"] = np.where(df["net_change"] > 0,1,0)

#remove unnessesary columns
clean_df = df#.drop(columns=["outcome"])

#reset the indexes
clean_df.reset_index(drop=True,inplace=True)
print(clean_df)
#check for missing vals and replace with mean
missing_val_count = df.isnull().sum()
print(missing_val_count)

missing_values_index = df[df.isna().any(axis=1)].index
print(missing_values_index)

if missing_val_count.any():

    #df.fillna(df.median(), inplace=True)
    print(f"{len(missing_val_count)} values replaced with median values of their column.")
# write the new clean file to csv
clean_df.to_csv(f"{new_file_name}.csv", index=False)

print(clean_df.head())


print(f"Program Complete.....prepared_data.csv has been saved. Df shape:{df.shape}")