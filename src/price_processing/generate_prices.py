"""Function for getting price values at given snapshot"""

# from pandas import DataFrame
# from datetime import datetime

# def generate_prices_values(prices: DataFrame, snapshot_date: datetime):
#     prices_ = prices.sort_values(["Timestamp"]).reset_index(drop=True)
#     prices_[prices_.Timestamp <= snapshot_date.timestamp()]
#     prices_ = prices_.groupby(
#         by=["UnderlyingToken"],
#         as_index=False,
#     ).agg({"Price": "last"})
#     return prices_
