"""Functions for extracting price data from datalab"""

import pandas as pd
from pandas import DataFrame
from datetime import date, timedelta
import json


def extract_price_data(client_s3, start: date, end: date) -> DataFrame:
    prices = DataFrame()
    day = start
    while day < end:
        day_str = day.strftime("%Y-%m-%d")
        day_prices = pd.json_normalize(
            json.loads(
                client_s3.get_object(
                    Bucket="projet-datalab-group-jprat",
                    Key=f"aave-raw-datasource/hourly-prices/hourly_prices_snapshot_date={day_str}/hourly_prices.json",
                )["Body"]
                .read()
                .decode()
            )
        )
        prices = pd.concat((prices, day_prices))
        day += timedelta(days=1)
    return prices
