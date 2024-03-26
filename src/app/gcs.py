import os
from google.cloud import storage

# Specify your Google Cloud Storage bucket name
BUCKET_NAME = os.getenv("GCP_BUCKET")

def connect_to_gcs():
    return storage.Client()

def upload_to_gcs(source_file_name, destination_blob_name):
    # Initialize a client
    client = connect_to_gcs()
    # Get the bucket
    bucket = client.bucket(BUCKET_NAME)
    # Upload the file
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name} in {BUCKET_NAME}.")

def download_from_gcs(file):
    # Initialize a client
    client = connect_to_gcs()
    bucket = client.bucket(BUCKET_NAME)
    bucket = client.lookup_bucket(bucket)
    blob = bucket.blob(file)
    blob.download_to_filename(file, start=0)
