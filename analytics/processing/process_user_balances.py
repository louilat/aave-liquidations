from pandas import DataFrame
import numpy as np


def process_user_balance_history(user_balances_history: DataFrame) -> DataFrame:
    user_balances_history_ = user_balances_history.copy()
    user_balances_history_["currentATokenBalance"] = (
        user_balances_history_.scaledATokenBalance.apply(int)
        / 10 ** user_balances_history_.decimals.apply(int)
        * user_balances_history_.liquidityIndex.apply(int)
        * 1e-27
        * user_balances_history_.underlyingTokenPriceUSD
    )

    user_balances_history_["currentVariableDebt"] = (
        user_balances_history_.scaledVariableDebt.apply(int)
        / 10 ** user_balances_history_.decimals.apply(int)
        * user_balances_history_.variableBorrowIndex.apply(int)
        * 1e-27
        * user_balances_history_.underlyingTokenPriceUSD
    )

    user_balances_history_["hf_numerator"] = (
        user_balances_history_.currentATokenBalance
        * user_balances_history_.reserveLiquidationThreshold
        * 1e-4
    )

    user_balances_history_ = user_balances_history_.groupby(
        by=["user_address", "day"], as_index=False
    ).agg(
        {
            "currentATokenBalance": "sum",
            "currentVariableDebt": "sum",
            "hf_numerator": "sum",
        }
    )

    user_balances_history_["hf"] = np.where(
        user_balances_history_.currentVariableDebt == 0,
        np.inf,
        user_balances_history_.hf_numerator
        / np.where(
            user_balances_history_.currentVariableDebt == 0,
            np.nan,
            user_balances_history_.currentVariableDebt,
        ),
    )
    # user_balances_history_.day = user_balances_history_.day + timedelta(days=1)
    return user_balances_history_
