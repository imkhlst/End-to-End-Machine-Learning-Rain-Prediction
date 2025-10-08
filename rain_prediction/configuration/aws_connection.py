import os
import boto3

from rain_prediction.constants import AWS_ACCESS_KEY_ID_ENV_KEY, AWS_SECRET_ACCESS_KEY_ENV_KEY, REGION_NAME

class S3Client:
    s3_client = None
    s3_resource = None
    def __init__(self, region_name=REGION_NAME):
        """_summary_

        Args:
            region_name (_type_, optional): _description_. Defaults to REGION_NAME.
        """
        if S3Client.s3_resource==None or S3Client.s3_client==None:
            __access_key_id = os.getenv(AWS_ACCESS_KEY_ID_ENV_KEY)
            __access_secret_key = os.getenv(AWS_SECRET_ACCESS_KEY_ENV_KEY)
            if __access_key_id is None:
                raise Exception(f"Environment variable: {AWS_ACCESS_KEY_ID_ENV_KEY} is not available.")
            if __access_secret_key is None:
                raise Exception(f"Environment variable: {AWS_SECRET_ACCESS_KEY_ENV_KEY} is not available.")
            
            S3Client.s3_resource = boto3.resource("s3",
                                                  aws_access_key_id = __access_key_id,
                                                  aws_secret_access_key = __access_secret_key,
                                                  region_name = region_name)
            S3Client.s3_client = boto3.client("s3",
                                              aws_access_key_id = __access_key_id,
                                              aws_secret_access_key = __access_secret_key,
                                              region_name = region_name)
            self.s3_resource = S3Client.s3_resource
            self.s3_client = S3Client.s3_client