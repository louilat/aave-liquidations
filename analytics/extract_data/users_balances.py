import pandas as pd
from pandas import DataFrame
from datetime import datetime, timedelta
import requests


def get_user_balances_history(user: str, start: datetime, stop: datetime):
    day = start
    user_history = DataFrame()
    while day <= stop:
        month = day.ctime()[4:7]
        day_str = "-".join([day.strftime("%Y"), month, day.strftime("%d")])
        # day_str = day.strftime("%Y-%b-%d")
        # print(day_str)
        resp = requests.get(
            "https://aavedata.lab.groupe-genes.fr/user-selec-balances",
            params={"date": day_str, "user": user},
            verify=False,
        )
        day_users_balances = pd.json_normalize(resp.json())
        if user in day_users_balances.user_address.unique().tolist():
            print("Day = ", day)
            day_users_balances["day"] = day
            resp = requests.get(
                "https://aavedata.lab.groupe-genes.fr/reserves",
                params={"date": day_str},
                verify=False,
            )
            day_reserves = pd.json_normalize(resp.json())
            day_users_balances = day_users_balances[
                [
                    "user_address",
                    "underlyingAsset",
                    "scaledATokenBalance",
                    "scaledVariableDebt",
                    "day",
                ]
            ].merge(
                day_reserves[
                    [
                        "underlyingAsset",
                        "name",
                        "decimals",
                        "underlyingTokenPriceUSD",
                        "liquidityIndex",
                        "variableBorrowIndex",
                        "reserveLiquidationThreshold",
                    ]
                ],
                how="left",
                on="underlyingAsset",
            )
            user_history = pd.concat((user_history, day_users_balances))
        day += timedelta(days=1)
    return user_history
