import sys
import pandas as pd

from rain_prediction.cloud_storage.aws_storage import SimpleStorageService
from rain_prediction.exception import RainPredictionException
from rain_prediction.entity.estimator import RainModel


class RainEstimator:
    """
    This class is used to save and retrieve rain_prediction model in s3 bucket and to do prediction.
    """
    def __init__(self, bucket_name: str, model_path: str):
        """_summary_

        Args:
            bucket_name (str): _description_
            model_path (str): _description_
        """
        self.bucket_name = bucket_name
        self.s3 = SimpleStorageService()
        self.model_path = model_path
        self.loaded_model: RainModel = None
    
    def is_model_present(self, model_path):
        try:
            return self.s3.s3_key_path_available(bucket_name=self.bucket_name, s3_key=model_path)
        except RainPredictionException as e:
            print(e)
            return False
    
    def load_model(self) -> RainModel:
        """_summary_

        Returns:
            RainModel: _description_
        """
        return self.s3.load_model(self.model_path, bucket_name=self.bucket_name)
    
    def save_model(self, from_file: str, remove: bool = False) -> None:
        """_summary_

        Args:
            from_file (str): _description_
            remove (bool, optional): _description_. Defaults to False.
        """
        try:
            self.s3.upload_file(from_file,
                                to_filename=self.model_path,
                                bucket_name=self.bucket_name,
                                remove=remove)
        
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def predict(self, dataframe: pd.DataFrame):
        """_summary_

        Args:
            dataframe (pd.DataFrame): _description_
        """
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe=dataframe)
        
        except Exception as e:
            raise RainPredictionException(e, sys)