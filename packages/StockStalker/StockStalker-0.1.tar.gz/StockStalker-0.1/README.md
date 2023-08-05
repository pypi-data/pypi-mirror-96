# StockStalker Guide
A easy to use, robust and quick Stocks API.

**WORK IN PROGRESS**

Changelog 2/12/2021:
- improved stocks reliability
- added crypto, doesnt work that well, need to fix
- added Currency module, works 


To install StockStalker, you can use pip:
`pip install stocky`

StockStalker is composed of two main sub-modules:
`present` & `past`

As the name suggests, `present` contains the functions to fetch live, realtime data. 
`past`, is simpler and contains a function to fetch historical data associated with a Symbol.

## Present Data

To operate `present` simply import it:
`import StockStalker.present as present`

Then you can use its two main functions:
 - `getLiveData(ticker, format="Dict")`
 - `getIndex(index)`
 
 `getLiveData()` returns either a Dict (`format="Dict"`), a Panda's Dataframe  (`format="DataFrame"`) or a object  (`format="Object"`). They all hold the same information, so its up to you!

`getLiveData()`returns a ample amount of information about a stock, here is a example:
```python
{
   "Symbol":"AAPL",
   "Price":134.56,
   "Change":[
      {
         "change":-0.83,
         "percentageChange":"-0.61%"
      }
   ],
   "P/E":36.5,
   "Ranges":[
      {
         "Low":133.77,
         "High":136.39
      }
   ],
   "Open":135.9,
   "previousClose":135.39,
   "EPS":3.69,
   "marketCap":"2.259T",
   "volume":50445505.0
}
```


`getIndex(index)` can be supplied currently with 4 inputs: 
- "NASDAQ" - gets all Symbols in the NASDAQ index
- "NASDAQ.OTHER" - gets all Symbols in the OFIN index
- "DOW" - gets all the Symbols in the DOW index
- "NYSE" - gets all Symbols in the NYSE

`getIndex` returns a list that looks like the following:
```python
['MCD', 'TRV', 'UNH', 'WMT', 'DOW', 'JPM', 'AXP'...

```

## Past Data 

`past` contains currently only one function: 

```python
getPastData(ticker, startDate, toDate, interval="d"):
```
dates are in the format: `m/d/Y`
invervals (the amount of time between each column of data) can be set as:
- "d" - having a interval of a day
- "w" - having a inverval of a week
- "mo" - having a interval of a month

An example of this function and what it returns a Dataframe:
```python
#get a years worth of data
df = getPastData("AAPL", "2/11/2021", "2/11/2020", interval="d"):
print(df)
```
```bash
,Date,Open,High,Low,Close,Adj Close,Volume  
0,2020-02-11,80.900002,80.974998,79.677498,79.902496,79.287888,94323200  
1,2020-02-12,80.3675,81.805,80.3675,81.800003,81.170799,113730400  
2,2020-02-13,81.047501,81.555,80.837502,81.217499,80.592773,94747600  
3,2020-02-14,81.184998,81.495003,80.712502,81.237503,80.612625,80113600

```


### Notes
- Gonna add crypto eventually
- Error Handling is alright, will improve
- Sometimes Yahoo Finance doesnt have the Data, if thats so, the entry for the Data thats missing is simply `"N/A"`




