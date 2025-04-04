import pandas as pd
from pandas import DataFrame
from datetime import datetime, timedelta
import requests


def get_prices_history(start: datetime, stop: datetime):
    prices_history = DataFrame()
    day = start
    while day <= stop:
        month = day.ctime()[4:7]
        day_str = "-".join([day.strftime("%Y"), month, day.strftime("%d")])
        resp = requests.get(
            "https://aavedata.lab.groupe-genes.fr/prices",
            params={"date": day_str},
            verify=False,
        )
        day_prices = pd.json_normalize(resp.json())
        prices_history = pd.concat((prices_history, day_prices))
        day += timedelta(days=1)
    return prices_history
