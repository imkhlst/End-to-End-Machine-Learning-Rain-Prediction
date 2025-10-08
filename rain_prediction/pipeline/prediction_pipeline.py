import os
import sys
import pandas as pd
import numpy as np

from rain_prediction.entity.config_entity import RainConfig
from rain_prediction.entity.s3_estimator import RainEstimator
from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging
from rain_prediction.utils.main_utils import read_yaml_file


class RainData:
    def __init__(self, Rainfall, WindGustSpeed, WindSpeed9am, WindSpeed3pm, Humidity9am,
                 Humidity3pm, WindGustDir, WindDir9am, WindDir3pm, Location):
        """_summary_

        Args:
            Rainfall (_type_): _description_
            WindGustSpeed (_type_): _description_
            WindSpeed9am (_type_): _description_
            WindSpeed3pm (_type_): _description_
            Humidity9am (_type_): _description_
            Humidity3pm (_type_): _description_
            WindGustDir (_type_): _description_
            WindDir9am (_type_): _description_
            WindDir3pm (_type_): _description_
            Location (_type_): _description_
        """
        try:
            self.Rainfall = Rainfall
            self.WindGustSpeed = WindGustSpeed
            self.WindSpeed9am = WindSpeed9am
            self.WindSpeed3pm = WindSpeed3pm
            self.Humidity9am = Humidity9am
            self.Humidity3pm = Humidity3pm
            self.WindGustDir = WindGustDir
            self.WindDir9am = WindDir9am
            self.WindDir3pm = WindDir3pm
            self.Location = Location
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def get_rain_input_dataframe(self) -> pd.DataFrame:
        """_summary_

        Returns:
            pd.DataFrame: _description_
        """
        try:
            rain_input_dict = self.get_rain_data_as_dict()
            return pd.DataFrame(rain_input_dict)
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def get_rain_data_as_dict(self):
        """_summary_
        """
        logging.info("Entered get_rain_data_as_dict method as RainData class.")
        
        try:
            input_data = {
                "Rainfall": [self.Rainfall],
                "WindGustSpeed": [self.WindGustSpeed],
                "WindSpeed9am": [self.WindSpeed9am],
                "WindSpeed3pm": [self.WindSpeed3pm],
                "Humidity9am": [self.Humidity9am],
                "Humidity3pm": [self.Humidity3pm],
                "WindGustDir": [self.WindGustDir],
                "WindDir9am": [self.WindDir9am],
                "WindDir3pm": [self.WindDir3pm],
                "Location": [self.Location]
            }
            logging.info("rain data dict has been created.")
            logging.info("Exited get_rain_data_as_dict method of RainData class.")
            return input_data
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
class RainClassifier:
    def __init__(self, prediction_pipeline_config: RainConfig = RainConfig()):
        """_summary_

        Args:
            prediction_pipeline_config (RainConfig, optional): _description_. Defaults to RainConfig.
        """
        try:
            self.prediction_pipeline_config = prediction_pipeline_config
            
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def predict(self, dataframe: pd.DataFrame) -> str:
        """_summary_

        Args:
            dataframe (pd.DataFrame): _description_

        Returns:
            str: _description_
        """
        try:
            logging.info("Entered predict method of RainClassifier class.")
            model = RainEstimator(
                bucket_name=self.prediction_pipeline_config.model_bucket_name,
                model_path=self.prediction_pipeline_config.model_file_path
            )
            result = model.predict(dataframe)
            return result
        
        except Exception as e:
            raise RainPredictionException(e, sys)