import sys

import pandas as pd
from sklearn.pipeline import Pipeline

from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging


class TargetValueMapping:
    def __init__(self):
        self.Yes: int = 1
        self.No: int = 0
        
    def _asdict(self):
        return self.__dict__
    
    def reverse_mapping(self):
        mapping_response = self._asdict()
        return dict(zip(mapping_response.values(), mapping_response.keys()))

class WindDirValueMapping:
    def __init__(self):
        self.N = 0
        self.NNE = 22.5
        self.NE = 45
        self.ENE = 67.5
        self.E = 90
        self.ESE = 112.5
        self.SE = 135
        self.SSE = 157.5
        self.S = 180
        self.SSW = 202.5
        self.SW = 225
        self.WSW = 247.5
        self.W = 270
        self.WNW = 292.5
        self.NW = 315
        self.NNW = 337.5
        
    def _asdict(self):
        return self.__dict__
    
    def reverse_mapping(self):
        mapping_response = self._asdict()
        return dict(zip(mapping_response.values(), mapping_response.keys()))

class RainModel:
    def __init__(self, preprocessing_object: Pipeline, trained_model_object: object):
        """_summary_

        Args:
            preprocessing_objecy (Pipeline): _description_
            trained_model_object (object): _description_
        """
        self.preprocessing_object = preprocessing_object
        self.trained_model_object = trained_model_object
    
    def predict(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """_summary_

        Args:
            dataframe (pd.DataFrame): _description_

        Returns:
            pd.DataFrame: _description_
        """
        logging.info("Entered predict method of RainModel class.")
        
        try:
            logging.info("Using the trained model to get predictions.")
            
            transformed_features = self.preprocessing_object.transform(dataframe)
            
            logging.info("Used the trained model to get predictions.")
            return self.trained_model_object.predict(transformed_features)
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def __repr__(self):
        return f"{type(self.trained_model_object).__name__}()"
    
    def __str__(self):
        return f"{type(self. trained_model_object).__name__}()"