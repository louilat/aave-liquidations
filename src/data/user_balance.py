"""Function for extracting users' balances snapshot"""

from datetime import date
import pandas as pd
from pandas import DataFrame
import requests


def get_users_snapshot(snapshot_date: date) -> DataFrame:
    day_str = snapshot_date.strftime("%Y-%b-%d")
    response_users = requests.get(
        url="https://aavedata.lab.groupe-genes.fr/users-balances",
        params={"date": day_str},
        verify=False,
    )
    response_reserves = requests.get(
        url="https://aavedata.lab.groupe-genes.fr/reserves",
        params={"date": day_str},
        verify=False,
    )
    try:
        users = pd.json_normalize(response_users.json())
        reserves = pd.json_normalize(response_reserves.json())
    except Exception as e:
        raise e

    users_ = users.drop(columns=["decimals", "name"]).merge(
        reserves, how="left", on="underlyingAsset"
    )
    return users_


# def get_users_snapshot(client_s3, snapshot_date: date) -> DataFrame:
#     day = date(2023, 1, 27)
#     balances_snapshot = DataFrame({"user_address": []})
#     while day <= snapshot_date:
#         day_str = day.strftime("%Y-%m-%d")
#         active_users = pd.read_csv(
#             client_s3.get_object(
#                 Bucket="projet-datalab-group-jprat",
#                 Key=f"aave-raw-datasource/daily-decoded-events/decoded_events_snapshot_date={day_str}/all_active_users.csv",
#             )["Body"]
#         )
#         transfer_users = pd.read_csv(
#             client_s3.get_object(
#                 Bucket="projet-datalab-group-jprat",
#                 Key=f"aave-raw-datasource/daily-decoded-events/decoded_events_snapshot_date={day_str}/all_atoken_transfer_users.csv",
#             )["Body"]
#         )
#         active_users = pd.concat((active_users, transfer_users)).drop_duplicates()
#         active_users_balances = pd.read_csv(
#             client_s3.get_object(
#                 Bucket="projet-datalab-group-jprat",
#                 Key=f"aave-raw-datasource/daily-users-balances/users_balances_snapshot_date={day_str}/active_users_balances.csv",
#             )["Body"]
#         )
#         transfer_users_balances = pd.read_csv(
#             client_s3.get_object(
#                 Bucket="projet-datalab-group-jprat",
#                 Key=f"aave-raw-datasource/daily-users-balances/users_balances_snapshot_date={day_str}/atoken_transfer_users_balances.csv",
#             )["Body"]
#         )
#         active_users_balances = pd.concat(
#             (active_users_balances, transfer_users_balances)
#         ).drop_duplicates(subset=["user_address", "name"])
#         balances_snapshot = balances_snapshot[
#             ~balances_snapshot.user_address.isin(active_users.active_user_address)
#         ]
#         balances_snapshot = pd.concat((balances_snapshot, active_users_balances))
#         day += timedelta(days=1)

#     # Merge with reserves data to get good prices and index
#     snapshot_date_str = snapshot_date.strftime("%Y-%m-%d")
#     reserves_data = pd.read_csv(
#         client_s3.get_object(
#             Bucket="projet-datalab-group-jprat",
#             Key=f"aave-raw-datasource/daily-users-balances/users_balances_snapshot_date={snapshot_date_str}/reserves_data.csv",
#         )["Body"]
#     )

#     balances = balances_snapshot[
#         ["user_address", "underlyingAsset", "scaledATokenBalance", "scaledVariableDebt"]
#     ]

#     balances = balances.merge(
#         reserves_data[
#             [
#                 "reserveLiquidationThreshold",
#                 "decimals",
#                 "underlyingAsset",
#                 "liquidityIndex",
#                 "variableBorrowIndex",
#                 "underlyingTokenPriceUSD",
#             ]
#         ],
#         how="left",
#         on="underlyingAsset",
#     )

#     return balances
