from dotenv import load_dotenv
import os
import boto3


def get_minio_s3_client():
    load_dotenv()
    ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
    SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
    SESSION_TOKEN = os.getenv("SESSION_TOKEN")

    client_s3 = boto3.client(
        "s3",
        endpoint_url="https://" + "minio-simple.lab.groupe-genes.fr",
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        aws_session_token=SESSION_TOKEN,
        verify=False,
    )
    return client_s3
