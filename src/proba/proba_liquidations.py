from pandas import DataFrame
import numpy as np


def compute_user_variance(
    users: DataFrame,
    # prices_values: DataFrame,
    prices_correlations: DataFrame,
    delta_time: float,
):
    users_ = users.copy()

    # users_ = users_.merge(
    #     prices_values,
    #     how="left",
    #     left_on="underlyingAsset",
    #     right_on="UnderlyingToken"
    # )
    # users_.Price = users_.Price / 1e8

    tokens_pairs = np.array(list(prices_correlations.index))
    volatility_mask = tokens_pairs[:, 0] == tokens_pairs[:, 1]

    prices_volatility = prices_correlations.reset_index()[volatility_mask][
        ["pair1", "rho"]
    ]
    users_ = users_.merge(
        prices_volatility, how="left", left_on="underlyingAsset", right_on="pair1"
    ).rename(columns={"rho": "sigma"})

    users_["a_price_sigma"] = users_.a * users_.sigma  # * users_.Price

    users_list = users_.user_address.unique().tolist()
    users_variance = DataFrame(
        {"user_address": users_list, "user_variance": None}
    ).set_index("user_address")

    for user in users_list:
        user_balance = users_[users_.user_address == user]
        users_variance.loc[user, "user_variance"] = (
            _get_user_var(user_balance, prices_correlations) * delta_time
        )

    return users_, users_variance


def _get_user_var(user_balance: DataFrame, prices_correlations: DataFrame) -> float:
    user_var = 0
    for i, row_i in user_balance.iterrows():
        for j, row_j in user_balance.iterrows():
            if row_i["underlyingAsset"] == row_j["underlyingAsset"]:
                rho_ij = 1
            else:
                rho_ij = prices_correlations.loc[
                    (row_i["underlyingAsset"], row_j["underlyingAsset"]), "rho"
                ]
            user_var += row_i["a_price_sigma"] * row_j["a_price_sigma"] * rho_ij
    return user_var


def compute_default_proba(
    users_balances: DataFrame, users_variances: DataFrame
) -> DataFrame:
    users_proba = users_balances[["user_address", "a"]].copy()
    users_proba = users_proba.groupby("user_address").agg({"a": "sum"})
    users_proba = users_proba.merge(
        users_variances,
        how="left",
        on="user_address",
    )
    users_proba["proba"] = users_proba.a / np.sqrt(users_proba.user_variance)

    return users_proba
