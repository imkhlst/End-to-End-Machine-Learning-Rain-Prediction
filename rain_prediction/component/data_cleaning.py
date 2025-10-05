import sys
import os

import pandas as pd
import numpy as np

from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging
from rain_prediction.constants import SCHEMA_FILE_PATH
from rain_prediction.entity.config_entity import DataCleaningConfig
from rain_prediction.entity.artifact_entity import (DataIngestionArtifact,
                                                    DataValidationArtifact,
                                                    DataCleaningArtifact)
from rain_prediction.entity.estimator import WindDirValueMapping
from rain_prediction.utils.main_utils import read_yaml_file, drop_columns


class DataCleaning:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact,
                 data_cleaning_config: DataCleaningConfig):
        """_summary_

        Args:
            data_ingestion_artifact (DataIngestionArtifact): _description_
            data_validation_artifact (DataValidationArtifact): _description_
            data_cleaning_config (DataCleaningConfig): _description_
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
            self.data_cleaning_config = data_cleaning_config
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def wind_direction_replace(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        try:
            features = self._schema_config["direction_columns"]
            for feature in features:
                dataframe[feature] = dataframe[feature].replace(WindDirValueMapping()._asdict()).infer_objects(copy=False)
            return dataframe
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def is_value_missing(self, dataframe: pd.DataFrame) -> bool:
        try:
            return dataframe.isnull().any().any()
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def is_duplicated(self, dataframe: pd.DataFrame) -> bool:
        try:
            return dataframe.duplicated().any().any()
        except Exception as e:
            raise RainPredictionException(e, sys)
                
    def is_outliers_detected(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        try:
            dataframe_numerical_features = dataframe[self._schema_config["num_columns"]]
            lower = dataframe_numerical_features.quantile(0.25)
            upper = dataframe_numerical_features.quantile(0.75)
            IQR = upper - lower
            status = (dataframe_numerical_features < (lower - 1.5 * IQR)) | (dataframe_numerical_features > (upper + 1.5 * IQR))
            return status.any().any()
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def initiate_data_cleaning(self, ) -> DataCleaningArtifact:
        """_summary_

        Returns:
            DataCleaningArtifact: _description_
        """
        logging.info("Entered initiate_data_cleaning method of DataCleaning class.")
        
        try:
            if self.data_validation_artifact.validation_status:
                logging.info("Starting data cleaning.")
                numerical_features = self._schema_config["num_columns"]
                
                train_dataframe, test_dataframe = (DataCleaning.read_data(file_path=self.data_ingestion_artifact.trained_file_path),
                                                DataCleaning.read_data(file_path=self.data_ingestion_artifact.tested_file_path))
                
                logging.info("Dropping columns in drop_columns of training dataset.")
                train_dataframe = drop_columns(df=train_dataframe,
                                                            cols= self._schema_config["drop_columns"])
                
                logging.info("Replacing values in direction_columns of training dataset.")
                train_dataframe = self.wind_direction_replace(train_dataframe)
                            
                status = self.is_value_missing(train_dataframe)
                if status:
                    train_dataframe[numerical_features] = train_dataframe[numerical_features].fillna(train_dataframe[numerical_features].mean())
                    train_dataframe = train_dataframe.dropna(how="any")
                
                status = self.is_duplicated(train_dataframe)
                if status:
                    train_dataframe = train_dataframe.drop_duplicates()
                
                status = self.is_outliers_detected(train_dataframe)
                if status:
                    cleaned_train_dataframe = train_dataframe[numerical_features].clip(lower=train_dataframe[numerical_features].quantile(0.01),
                                                                                    upper=train_dataframe[numerical_features].quantile(0.99),
                                                                                    axis=1)
                    non_num_cols = train_dataframe.drop(columns=numerical_features)
                    cleaned_train_dataframe = pd.concat([cleaned_train_dataframe, non_num_cols], axis=1)
                else:
                    cleaned_train_dataframe = train_dataframe.copy()
                    
                logging.info("Dropping columns in drop_columns of training dataset.")
                test_dataframe = drop_columns(df=test_dataframe,
                                            cols= self._schema_config["drop_columns"])
                
                logging.info("Replacing values in direction_columns of training dataset.")
                test_dataframe = self.wind_direction_replace(test_dataframe)
                            
                status = self.is_value_missing(test_dataframe)
                if status:
                    logging.info("Filling and dropping missing values in training dataset.")
                    test_dataframe[numerical_features] = test_dataframe[numerical_features].fillna(test_dataframe[numerical_features].mean())
                    test_dataframe = test_dataframe.dropna(how="any")
                
                status = self.is_duplicated(test_dataframe)
                if status:
                    logging.info("Dropping duplicaed data in training dataset.")
                    test_dataframe = test_dataframe.drop_duplicates()
                
                status = self.is_outliers_detected(test_dataframe)
                if status:
                    logging.info("Capping outliers in training dataset.")
                    cleaned_test_dataframe = test_dataframe[numerical_features].clip(lower=test_dataframe[numerical_features].quantile(0.01),
                                                                                    upper=test_dataframe[numerical_features].quantile(0.99),
                                                                                    axis=1)
                    non_num_cols = test_dataframe.drop(columns=numerical_features)
                    cleaned_test_dataframe = pd.concat([cleaned_test_dataframe, non_num_cols], axis=1)
                else:
                    cleaned_test_dataframe = test_dataframe.copy()
                    
                logging.info(f"Data Cleaning Completed")
                logging.info("Creating training and testing directory path.")
                cleaned_train_dir_path = os.path.dirname(self.data_cleaning_config.cleaned_training_file_path)
                cleaned_test_dir_path = os.path.dirname(self.data_cleaning_config.cleaned_testing_file_path)
                os.makedirs(cleaned_train_dir_path, exist_ok=True)
                os.makedirs(cleaned_test_dir_path, exist_ok=True)
                logging.info("Training and Testing Directory has been created.")
                
                logging.info("Exporting train and test file path.")
                cleaned_train_dataframe.to_csv(self.data_cleaning_config.cleaned_training_file_path, index=False, header=True)
                cleaned_test_dataframe.to_csv(self.data_cleaning_config.cleaned_testing_file_path, index=False, header=True)
                logging.info("Train and test data has been exported.")
                
                data_cleaning_artifact = DataCleaningArtifact(
                    cleaned_train_file_path = self.data_cleaning_config.cleaned_training_file_path,
                    cleaned_test_file_path = self.data_cleaning_config.cleaned_testing_file_path
                )
                
                logging.info(f"Data cleaning artifact: {data_cleaning_artifact}.")
                return data_cleaning_artifact
            else:
                raise Exception(self.data_validation_artifact.message)
            
        except Exception as e:
            raise RainPredictionException(e, sys) from e