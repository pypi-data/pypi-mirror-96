from ejtraderMT import Metatrader



api = Metatrader()

symbol = "EURUSD"
symbols = [symbol,"GBPUSD","AUDUSD"]
timeframe = "M1"


data = api.ShorthistoryDataFrame(symbol,timeframe,3)


print(data)

