import glob
import os
from google.cloud import bigquery

def get_bigquery_client(bigquery_project_id):

    dags_dir = os.path.dirname(os.path.abspath(__file__))
    path_to_key_file = os.path.join(dags_dir, "secrets", "*.json")
    key_files = glob.glob(path_to_key_file)

    if not key_files or len(key_files) == 0:
        raise FileNotFoundError(f"No Google Cloud key found in {path_to_key_file}")

    key_file = key_files[0]
    client = bigquery.Client.from_service_account_json(
        key_file,
        project= bigquery_project_id
    )
    return client


if __name__ == "__main__":
    get_bigquery_client("staging-udts-01")