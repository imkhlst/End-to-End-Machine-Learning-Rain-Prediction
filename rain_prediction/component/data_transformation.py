import os
import sys

import pandas as pd
import numpy as np
from imblearn.combine import SMOTEENN
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging
from rain_prediction.constants import TARGET_COLUMN, SCHEMA_FILE_PATH
from rain_prediction.entity.estimator import TargetValueMapping
from rain_prediction.entity.config_entity import DataTransformationConfig
from rain_prediction.entity.artifact_entity import (DataCleaningArtifact,
                                                    DataTransformationArtifact)
from rain_prediction.utils.main_utils import (save_obj, save_numpy_array_data,
                                              read_yaml_file, drop_columns)


class DataTransformation:
    def __init__(self, data_cleaning_artifact: DataCleaningArtifact,
                 data_transformation_config: DataTransformationConfig):
        """_summary_

        Args:
            data_ingestion_artifact (DataIngestionArtifact): _description_
            data_validation_artifact (DataValidationArtifact): _description_
            data_tranformation_config (DataTransformationConfig): _description_
        """
        try:
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
            
            input_feature_train_dataframe = train_dataframe.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_dataframe = train_dataframe[TARGET_COLUMN]
            
            target_feature_train_dataframe = target_feature_train_dataframe.replace(
                TargetValueMapping()._asdict()).infer_objects(copy=False).squeeze()
            logging.info(f"target_feature_train_dataframe type: {type(target_feature_train_dataframe)}")
            logging.info(f"target_feature_train_dataframe shape: {getattr(target_feature_train_dataframe, 'shape', None)}")
            logging.info(f"target_feature_train_dataframe sample:\n{target_feature_train_dataframe.head() if hasattr(target_feature_train_dataframe, 'head') else target_feature_train_dataframe}")
            target_feature_train_dataframe = np.array(target_feature_train_dataframe).ravel()
            
            logging.info("Got train features and test features of training dataset.")
            
            input_feature_test_dataframe = test_dataframe.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_dataframe = test_dataframe[TARGET_COLUMN]
            
            target_feature_test_dataframe = target_feature_test_dataframe.replace(
                TargetValueMapping()._asdict()).infer_objects(copy=False).squeeze()
            
            target_feature_test_dataframe = np.array(target_feature_test_dataframe).ravel()

            logging.info("Got train features and test features of testing dataset.")
            
            logging.info("Applying preprocessing object on training dataframe and testing dataframe.")
            
            input_feature_train_arr = preprocessor.fit_transform(input_feature_train_dataframe)
            
            logging.info("Used the preprocessor object to fit transform the train features.")
            
            input_feature_test_arr = preprocessor.transform(input_feature_test_dataframe)
            
            logging.info("Applying SMOTEENN on training dataset and testing dataset.")
            
            smt = SMOTEENN(sampling_strategy="minority")
            input_feature_train_final, target_feature_train_final = smt.fit_resample(
                input_feature_train_arr, target_feature_train_dataframe
            )
            logging.info(f"type(input_feature_train_final): {type(input_feature_train_final)}")
            logging.info(f"type(target_feature_train_final): {type(target_feature_train_final)}")
            logging.info(f"input_feature_train_final shape: {getattr(input_feature_train_final, 'shape', None)}")
            logging.info(f"target_feature_train_final shape: {getattr(target_feature_train_final, 'shape', None)}")
            logging.info(f"Sample of target_feature_train_final: {target_feature_train_final[:5] if hasattr(target_feature_train_final, '__getitem__') else target_feature_train_final}")

            if hasattr(input_feature_train_final, "toarray"):
                input_feature_train_final = input_feature_train_final.toarray()

            if hasattr(input_feature_test_arr, "toarray"):
                input_feature_test_arr = input_feature_test_arr.toarray()
            
            logging.info("Creating train array and test array")
            
            train_arr = np.concatenate(
                [input_feature_train_final, target_feature_train_final.reshape(-1, 1)], axis=1
            )
            test_arr = np.concatenate(
                [input_feature_test_arr, target_feature_test_dataframe.reshape(-1, 1)], axis=1
            )
            
            logging.info("Saving the preprocessor object, train array and test array.")
            save_obj(self.data_transformation_config.transformed_object_file_path, preprocessor)
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            logging.info("Preprocessor object, train array, test array has been saved.")
            
            logging.info("Exited initiate_data_transformation method of DataTransformation class.")
            
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact
        except Exception as e:
            raise RainPredictionException(e, sys) from e