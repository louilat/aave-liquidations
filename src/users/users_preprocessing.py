"""Function for preprocessing the users dataframe before computing proba"""

from pandas import DataFrame
import numpy as np


def clean_users(users: DataFrame, emodes: DataFrame, assets_list: list) -> DataFrame:
    users_ = users.copy()
    users_ = users_.merge(
        emodes[["active_user_address", "emode"]],
        how="left",
        left_on="user_address",
        right_on="active_user_address",
    ).drop(columns="active_user_address")

    users_.reserveLiquidationThreshold = np.select(
        condlist=[
            users_.emode == 0,
            users_.emode == 1,
            users_.emode == 2,
            users_.emode == 3,
            users_.emode == 4,
            users_.emode == 5,
            users_.emode == 6,
            users_.emode == 7,
        ],
        choicelist=[
            users_.reserveLiquidationThreshold,
            9500,
            9200,
            9450,
            8600,
            8600,
            8600,
            8500,
        ],
        default=users_.reserveLiquidationThreshold,
    )

    users_["currentATokenBalanceUSD"] = (
        users_.scaledATokenBalance.apply(int)
        / 10**users_.decimals
        * users_.liquidityIndex.apply(int)
        * 1e-27
        * users_.underlyingTokenPriceUSD
    ).astype(float)
    users_["currentVariableDebtUSD"] = (
        users_.scaledVariableDebt.apply(int)
        / 10**users_.decimals
        * users_.variableBorrowIndex.apply(int)
        * 1e-27
        * users_.underlyingTokenPriceUSD
    ).astype(float)

    residual_balances_mask = (
        users_.groupby("user_address")["currentATokenBalanceUSD"].transform("sum") > 100
    )
    borrower_mask = (
        users_.groupby("user_address")["currentVariableDebtUSD"].transform("sum") > 0
    )

    users_["token_not_registered"] = ~users_.underlyingAsset.isin(assets_list)
    is_token_registered_mask = (
        users_.groupby("user_address")["token_not_registered"].transform("sum") == 0
    )

    users_ = users_[
        (residual_balances_mask & borrower_mask & is_token_registered_mask)
    ].drop(columns="token_not_registered")

    users_["a"] = (
        users_.currentVariableDebtUSD
        - users_.currentATokenBalanceUSD
        * users_.reserveLiquidationThreshold.apply(int)
        * 1e-4
    ).astype(float)

    return users_
