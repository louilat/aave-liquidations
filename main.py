"""Main ETL"""

from datetime import date, timedelta
import io
import warnings

warnings.filterwarnings(action="ignore")

from src.utils.minio import get_minio_s3_client
from src.data.user_balance import get_users_snapshot
from src.data.price import extract_price_data
from src.data.emodes import get_emodes
from src.price_processing.fit_normal import (
    preprocess_prices_for_fitting,
    fit_multivariate_normal_distribution,
    generate_prices_correlations,
)

from src.users.users_preprocessing import clean_users
from src.proba.proba_liquidations import compute_user_variance, compute_default_proba

client_s3 = get_minio_s3_client()


## Parameters
snapshot_date = date(2024, 7, 15)
maturity = 1 / 365
bucket = "llatournerie-ensae"
output_path = "aave-liquidations-proba/dev-jobs/"

print("STEP 1: Extract data")


print("   --> Users snapshot")
raw_users = get_users_snapshot(
    # client_s3=client_s3,
    snapshot_date=snapshot_date
)


print("   --> Hourly prices")
start_price_date = snapshot_date - timedelta(days=45)
prices = extract_price_data(
    client_s3=client_s3, start=start_price_date, end=snapshot_date
)

print("   --> Users emodes")
emodes = get_emodes(client_s3=client_s3, snapshot_date=snapshot_date)


print("STEP 2: Estimate prices volatility and correlations")

print("   --> Extract brownian motion values from prices values")
processed_prices = preprocess_prices_for_fitting(prices=prices)

print("   --> Fit multivariate normal")
Sigma = fit_multivariate_normal_distribution(processed_prices.values)

print("   --> Generate correlations dataframe")
correlations = generate_prices_correlations(Sigma, processed_prices.columns.tolist())

print("STEP 3: Compute liquidations probas")

print("   --> Preprocessing users data")
users = clean_users(
    users=raw_users, emodes=emodes, assets_list=processed_prices.columns.tolist()
)

print("   --> Compute users variance coeff")
_, users_variance_coeff = compute_user_variance(
    users=users,
    # prices_values=prices_values,
    prices_correlations=correlations,
    delta_time=maturity,
)

print("   --> Compute users liquidation proba")
users_liquidation_proba = compute_default_proba(
    users_balances=users,
    users_variances=users_variance_coeff,
)

buffer = io.StringIO()
users_liquidation_proba.to_csv(buffer, index=False)
client_s3.put_object(
    Bucket=bucket, Key=output_path + "probas_mlt.csv", Body=buffer.getvalue()
)

buffer = io.StringIO()
correlations.reset_index().to_csv(buffer, index=False)
client_s3.put_object(
    Bucket=bucket, Key=output_path + "correlations.csv", Body=buffer.getvalue()
)

buffer = io.StringIO()
users.reset_index().to_csv(buffer, index=False)
client_s3.put_object(
    Bucket=bucket, Key=output_path + "users.csv", Body=buffer.getvalue()
)

print("Done!")
