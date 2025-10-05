import sys
from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging
from rain_prediction.component.data_ingestion import DataIngestion
from rain_prediction.component.data_validation import DataValidation
from rain_prediction.component.data_cleaning import DataCleaning
from rain_prediction.component.data_transformation import DataTransformation

from rain_prediction.entity.config_entity import (DataIngestionConfig,
                                                  DataCleaningConfig,
                                                  DataValidationConfig,
                                                  DataTransformationConfig)

from rain_prediction.entity.artifact_entity import (DataIngestionArtifact,
                                                    DataCleaningArtifact,
                                                    DataValidationArtifact,
                                                    DataTransformationArtifact)


class TrainPipeline:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()
        self.data_validation_config = DataValidationConfig()
        self.data_cleaning_config = DataCleaningConfig()
        self.data_transformation_config = DataTransformationConfig()
    
    def start_data_ingestion(self) -> DataIngestionArtifact:
        """_summary_

        Returns:
            DataIngestionArtifact: _description_
        """
        try:
            logging.info("Entered the start_data_ingestion method of TrainPipeline class.")
            logging.info("Getting the data from MongoDB.")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info("Got the train_set and test_set from MongoDB")
            logging.info("Exited the start_data_ingestion method of TrainPipeline class.")
            return data_ingestion_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        """_summary_

        Returns:
            DataValidationArtifact: _description_
        """
        try:
            logging.info("Entered the start_data_validation method of TrainPipeline class.")
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
                                             data_validation_config=self.data_validation_config)
            
            data_validation_artifact = data_validation.initiate_data_validation()
            
            logging.info("Data Validation completed.")
            logging.info("Exited the start_data_validation method of TrainPipeline class.")
            return data_validation_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def start_data_cleaning(self, data_ingestion_artifact: DataIngestionArtifact,
                            data_validation_artifact: DataValidationArtifact) -> DataCleaningArtifact:
        """_summary_

        Args:
            data_ingestion_artifact (DataIngestionArtifact): _description_
            data_validation_artifact (DataValidationArtifact): _description_

        Returns:
            DataCleaningArtifact: _description_
        """
        try:
            logging.info("Entered the start_data_cleaning method of TrainPipeline class.")
            data_cleaning = DataCleaning(data_ingestion_artifact=data_ingestion_artifact,
                                         data_validation_artifact=data_validation_artifact,
                                         data_cleaning_config=self.data_cleaning_config)
            
            data_cleaning_artifact = data_cleaning.initiate_data_cleaning()
            logging.info("Data Cleaning completed.")
            logging.info("Exited the start_data_cleaning method of TrainPipeline class.")
            return data_cleaning_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def start_data_transformation(self, data_cleaning_artifact: DataCleaningArtifact) -> DataTransformationArtifact:
        try:
            logging.info("Entered the start_data_cleaning method of TrainPipeline class.")
            data_transformation = DataTransformation(data_cleaning_artifact=data_cleaning_artifact,
                                                     data_transformation_config=self.data_transformation_config)
            
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info("Data transformation completed.")
            logging.info("Exited the start_data_transformation method of TrainPipeline class.")
            return data_transformation_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def run_pipeline(self,) -> None:
        """_summary_
        """
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_cleaning_artifact = self.start_data_cleaning(data_ingestion_artifact=data_ingestion_artifact,
                                                                data_validation_artifact=data_validation_artifact)
            data_transformation_artifact = self.start_data_transformation(data_cleaning_artifact=data_cleaning_artifact)
            
        except Exception as e:
            raise RainPredictionException(e, sys) from e