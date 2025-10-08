import os,sys
import boto3
import pandas as pd

from io import StringIO
from typing import Union, List

from rain_prediction.configuration.aws_connection import S3Client
from rain_prediction.logger import logging
from rain_prediction.exception import RainPredictionException
from mypy_boto3_s3.service_resource import Bucket
from botocore.exceptions import ClientError
import pickle


class SimpleStorageService:
    def __init__(self):
        s3_client = S3Client()
        self.s3_resource = s3_client.s3_resource
        self.s3_client = s3_client.s3_client
    
    def s3_key_path_available(self, bucket_name, s3_key) -> bool:
        try:
            bucket = self.get_bucket(bucket_name)
            file_objects = [file_object for file_object in bucket.objects.filter(Prefix=s3_key)]
            if len(file_objects) > 0:
                return True
            else:
                return False
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    @staticmethod
    def read_object(object_name: str, decode: bool = True, make_readable: bool = False) -> Union[StringIO, str]:
        """_summary_

        Args:
            object_name (str): _description_
            decode (bool, optional): _description_. Defaults to True.
            make_readable (bool, optional): _description_. Defaults to False.

        Returns:
            Union[StringIO, str]: _description_
        """
        logging.info("Entered the read_object method of S3Operations class.")
        
        try:
            func = {
                lambda: object_name.get()["Body"].read().decode()
                if decode is True
                else object_name.get()["Body"].read()
            }
            conv_func = lambda: StringIO(func()) if make_readable is True else func()
            logging.info("Exited the read_object method od S3Operation class.")
            return conv_func
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def get_bucket(self, bucket_name: str) -> Bucket:
        """_summary_

        Args:
            bucket_name (str): _description_

        Returns:
            Bucket: _description_
        """
        logging.info("Entered the get_bucket method of S3Operation class.")
        
        try:
            bucket = self.s3_resource.Bucket(bucket_name)
            logging.info("Exited the get_bucket method of S3Opereation class.")
            return bucket
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def get_file_object(self, filename: str, bucket_name: str) -> Union[list[object], object]:
        """_summary_

        Args:
            filename (str): _description_
            bucket_name (str): _description_

        Returns:
            Union[list[object], object]: _description_
        """
        logging.info("Entered the get_file_object method of S3Operation class.")
        
        try:
            bucket = self.get_bucket(bucket_name)
            
            file_objects = [file_object for file_object in bucket.objects.filter(Prefix=filename)]
            
            func = lambda x: x[0] if len(x) == 1 else x
            
            file_objs = func(file_objects)
            logging.info("Exited the get_file_object method of S3Operation class.")
            
            return file_objs
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def load_model(self, model_name: str, bucket_name: str, model_dir: str =None) -> object:
        """_summary_

        Args:
            model_name (str): _description_
            bucket_name (str): _description_
            model_dir (str, optional): _description_. Defaults to None.

        Returns:
            object: _description_
        """
        logging.info("Entered the load_model method of S3Operation class.")
        
        try:
            func = (
                lambda: model_name
                if model_dir is None
                else model_dir + "/" + model_name
            )
            model_file = func()
            file_object = self.get_file_object(model_file, bucket_name)
            model_object = self.read_object(file_object, decode=False)
            model = pickle.loads(model_object)
            logging.info("Exited the load_model method of S3Operation class.")
            return model
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def create_folder(self, folder_name: str, bucket_name: str) -> None:
        """_summary_

        Args:
            folder_name (str): _description_
            bucket_name (str): _description_
        """
        logging.info("Entered teh create_folder method of S3Operation class.")
        
        try:
            self.s3_resource.Object(bucket_name, folder_name).load()
        
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                folder_object = folder_name + "/"
                self.s3_client.put_object(Bucket=bucket_name, Key=folder_object)
            else:
                pass
            logging.info("Exited the create_folder method of S3Operation class.")
    
    def upload_file(self, from_filename: str, to_filename: str, bucket_name: str, remove: bool = True):
        """_summary_

        Args:
            from_filename (str): _description_
            to_filename (str): _description_
            bucket_name (str): _description_
            remove (bool, optional): _description_. Defaults to True.
        """
        logging.info("Entered the upload_file method of S3Operation class.")
        
        try:
            logging.info(
                f"Uploading {from_filename} file to {to_filename} file in {bucket_name} bucket."
            )
            
            self.s3_resource.meta.client.upload_file(
                from_filename, bucket_name, to_filename.replace("\\", "/")
            )
            
            logging.info(
                f"Uploaded {from_filename} file to {to_filename} file in {bucket_name} bucket."
            )
            
            if remove is True:
                os.remove(from_filename)
                
                logging.info(f"Remove is set to {remove}, deleted the file.")
            
            else:
                logging.info(f"Remove is set to {remove}, not deleted the file.")
            
            logging.info("Exited the upload_file method of S3Operation class.")
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def upload_df_as_csv(self, dataframe: pd.DataFrame, local_filename: str,
                         bucket_filename: str, bucket_name: str) -> None:
        """_summary_

        Args:
            dataframe (pd.DataFrame): _description_
            local_filename (str): _description_
            bucket_filename (str): _description_
            bucket_name (str): _description_
        """
        logging.info("Entered the upload_df_as_csv method of S3Operation class.")
        
        try:
            dataframe.to_csv(local_filename, index=None, header=True)
            
            self.upload_file(local_filename, bucket_filename, bucket_name)
            
            logging.info("Exited the upload_df_to_csv method of S3Operation class.")
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def get_df_from_object(self, object_: object) -> pd.DataFrame:
        """_summary_

        Args:
            object_ (object): _description_

        Returns:
            pd.DataFrame: _description_
        """
        logging.info("Entered the get_df_from_object method of S3Operation class.")
        
        try:
            content = self.read_object(object_, make_readable=True)
            df = pd.read_csv(content, na_values="na")
            logging.info("Exited the get_df_from_object method of S3Operation class.")
            return df
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def read_csv(self, filename: str, bucket_name: str) -> pd.DataFrame:
        """_summary_

        Args:
            filename (str): _description_
            bucket_name (str): _description_

        Returns:
            pd.DataFrame: _description_
        """
        logging.info("Entered the read_csv method of S3Operation class.")
        
        try:
            csv_object = self.get_file_object(filename, bucket_name)
            df = self.get_df_from_object(csv_object)
            logging.info("Exited the read_csv method of S3Operation class.")
            return df
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e