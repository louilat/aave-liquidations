import pandas as pd
from pandas import DataFrame
from datetime import date, timedelta


def get_emodes(client_s3, snapshot_date: date) -> DataFrame:
    output = DataFrame()
    day = date(2023, 1, 27)
    while day <= snapshot_date:
        day_str = day.strftime("%Y-%m-%d")
        # print(day_str)
        daily_emodes = pd.read_csv(
            client_s3.get_object(
                Bucket="projet-datalab-group-jprat",
                Key=f"aave-raw-datasource/daily-users-balances/users_balances_snapshot_date={day_str}/active_users_emodes.csv",
            )["Body"]
        )
        output = pd.concat((output, daily_emodes))
        output = output.sort_values("snapshot_block").drop_duplicates(
            subset=["active_user_address"], keep="last"
        )
        day += timedelta(days=1)
    return output
