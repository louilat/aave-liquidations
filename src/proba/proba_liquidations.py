from pandas import DataFrame
import numpy as np
from scipy.stats import norm
import concurrent.futures


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

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_get_user_var, users_, u, prices_correlations): u
            for u in users_list
        }

        for future in concurrent.futures.as_completed(futures):
            usr = futures[future]
            user_var = future.result()
            users_variance.loc[usr, "user_variance"] = user_var * delta_time

    # for user in users_list:
    #     user_balance = users_[users_.user_address == user]
    #     users_variance.loc[user, "user_variance"] = (
    #         _get_user_var(user_balance, prices_correlations) * delta_time
    #     )

    return users_, users_variance


def _get_user_var(
    users_data: DataFrame, user: str, prices_correlations: DataFrame
) -> float:
    user_balance = users_data[users_data.user_address == user]
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
    users_proba["q_value"] = users_proba.a / np.sqrt(
        users_proba.user_variance.astype(np.float64)
    )
    users_proba["proba_liquidation"] = norm.cdf(users_proba.q_value)

    return users_proba.sort_values("proba_liquidation", ascending=False).reset_index()
