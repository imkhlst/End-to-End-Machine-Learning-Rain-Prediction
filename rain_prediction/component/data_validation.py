import json
import sys

import pandas as pd
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection

from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging
from rain_prediction.utils.main_utils import read_yaml_file, write_yaml_file
from rain_prediction.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from rain_prediction.entity.config_entity import DataValidationConfig
from rain_prediction.constants import SCHEMA_FILE_PATH

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        """_summary_

        Args:
            data_ingestion_artifact (DataIngestionArtifact): _description_
            data_validation_artifact (DataValidationArtifact): _description_
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        """_summary_

        Args:
            dataframe (pd.DataFrame): _description_

        Returns:
            bool: _description_
        """
        try:
            status = len(dataframe.columns) ==len(self._schema_config["columns"])
            logging.info(f"Is required column present: [{status}].")
            return status
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def is_column_exist(self, dataframe: pd.DataFrame) -> bool:
        """_summary_

        Args:
            dataframe (pd.DataFrame): _description_

        Returns:
            bool: _description_
        """
        try:
            dataframe_columns = dataframe.columns
            missing_numerical_columns = []
            missing_categorical_columns = []
            
            for column in self._schema_config["numerical_columns"]:
                if column not in dataframe_columns:
                    missing_numerical_columns.append(column)
            if len(missing_numerical_columns) > 0:
                logging.info(f"Missing numerical columns: {missing_numerical_columns}.")
            
            for column in self._schema_config["categorical_columns"]:
                if column not in dataframe_columns:
                    missing_categorical_columns.append(column)
                    
            if len(missing_categorical_columns) > 0:
                logging.info(f"Missing categorical column: {missing_categorical_columns}.")
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def detect_dataset_drift(self, reference_dataframe: pd.DataFrame,
                             current_dataframe: pd.DataFrame) -> bool:
        """_summary_

        Args:
            reference_dataframe (pd.DataFrame): _description_
            current_dataframe (pd.DataFrame): _description_

        Returns:
            bool: _description_
        """
        try:
            data_drift_profile = Profile(sections=[DataDriftProfileSection()])
            
            data_drift_profile.calculate(reference_dataframe, current_dataframe)
            
            report = data_drift_profile.json()
            json_report = json.loads(report)
            
            write_yaml_file(file_path=self.data_validation_config.drift_report_file_path,
                            content=json_report)
            
            n_features = json_report["data_drift"]["data"]["metrics"]["n_features"]
            n_drift_features = json_report["data_drift"]["data"]["metrics"]["n_drifted_features"]
            
            logging.info(f"{n_drift_features}/{n_features} drift detected.")
            drift_status = json_report["data_drift"]["data"]["metrics"]["dataset_drift"]
            return drift_status
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def initiate_data_validation(self) -> DataValidationArtifact:
        """_summary_

        Returns:
            DataValidationArtifact: _description_
        """
        try:
            validation_error_msg = ""
            logging.info("Starting data validation.")
            train_dataframe, test_dataframe = (DataValidation.read_data(file_path=self.data_ingestion_artifact.trained_file_path),
                                               DataValidation.read_data(file_path=self.data_ingestion_artifact.tested_file_path))
            
            status = self.validate_number_of_columns(dataframe=train_dataframe)
            logging.info(f"All required columns present in training DataFrame: {status}.")
            if not status:
                validation_error_msg == f"Columns are missing in training DataFrame."
            
            status = self.validate_number_of_columns(dataframe=test_dataframe)
            logging.info(f"All required columns present in testing DataFrame: {status}.")
            if not status:
                validation_error_msg == f"Columns are missing in testing DataFrame."
            
            status = self.is_column_exist(dataframe=train_dataframe)
            if not status:
                validation_error_msg == f"Columns are missing in training DataFrame."
            
            status = self.is_column_exist(dataframe=test_dataframe)
            if not status:
                validation_error_msg == f"Columns are missing in testing DataFrame."
            
            validation_status = len(validation_error_msg) == 0
            
            if validation_status:
                drift_status = self.detect_dataset_drift(train_dataframe, test_dataframe)
                if drift_status:
                    logging.info("Drift detected.")
                    validation_error_msg = "Drift detected"
                else:
                    validation_error_msg = "Drift not detected"
            else:
                logging.info(f"Validation_error: {validation_error_msg}")
            
            data_validation_artifact = DataValidationArtifact(
                validation_status = validation_status,
                message = validation_error_msg,
                drift_report_file_path = self.data_validation_config.drift_report_file_path
            )
            
            logging.info(f"Data validation artifact: {data_validation_artifact}.")
            return data_validation_artifact
        except Exception as e:
            raise RainPredictionException(e, sys) from e