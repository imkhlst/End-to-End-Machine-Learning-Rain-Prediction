import os
import sys

import pandas as pd
from imblearn.combine import SMOTEENN
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging
from rain_prediction.constants import TARGET_COLUMN, SCHEMA_FILE_PATH
from rain_prediction.entity.estimator import TargetValueMapping
from rain_prediction.entity.config_entity import DataTransformationConfig
from rain_prediction.entity.artifact_entity import (DataIngestionArtifact,
                                                    DataValidationArtifact,
                                                    DataCleaningArtifact,
                                                    DataTransformationArtifact)
from rain_prediction.utils.main_utils import (save_obj, save_numpy_array_data,
                                              read_yaml_file, drop_columns)


class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact,
                 data_cleaning_artifact: DataCleaningArtifact,
                 data_transformation_config: DataTransformationConfig):
        """_summary_

        Args:
            data_ingestion_artifact (DataIngestionArtifact): _description_
            data_validation_artifact (DataValidationArtifact): _description_
            data_tranformation_config (DataTransformationConfig): _description_
        """
        try:
            self.data_inegstion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
            self.data_cleaning_artifact = data_cleaning_artifact
            self.data_transformation_config = data_transformation_config
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    @staticmethod
    def read_file(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def get_data_transformer_object(self) -> Pipeline:
        """_summary_

        Returns:
            Pipeline: _description_
        """
        logging.info("Entered et_data_transformer_object method of DataTransformation class.")
        
        try:
            logging.info("Get numerical cols from schema config.")
            
            numeric_transformer = StandardScaler()
            one_hot_transformer = OneHotEncoder()
            
            logging.info("Initialized StanderScaler and OneHotEncoder.")
            
            num_features = self._schema_config["num_columns"]
            one_hot_columns = self._schema_config["one_hot_columns"]
            
            preprocessor = ColumnTransformer(
                [
                    ("OneHotEncoder", one_hot_transformer, one_hot_columns),
                    ("StandarScaler", numeric_transformer, num_features)
                ]
            )
            
            logging.info("Created preprocessor object from ColumnTransformer.")
            
            logging.info("Exited get_data_tranformer_object method of DataTransformation class.")
            return preprocessor
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def initiate_data_transformation(self, ) -> DataTransformationArtifact:
        """
        """
        try:
            logging.info("Starting data transformation.")
            preprocessor = self.get_data_transformer_object()
            logging.info("Got the processor object.")
            
            train_dataframe = DataTransformation.read_file(file_path=self.data_cleaning_artifact.cleaned_train_file_path)
            test_dataframe = DataTransformation.read_file(file_path=self.data_cleaning_artifact.cleaned_test_file_path)
            