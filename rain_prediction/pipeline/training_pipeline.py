import sys
from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging
from rain_prediction.component.data_ingestion import DataIngestion
from rain_prediction.component.data_validation import DataValidation
from rain_prediction.component.data_cleaning import DataCleaning
from rain_prediction.component.data_transformation import DataTransformation
from rain_prediction.component.model_training import ModelTraining
from rain_prediction.component.model_evaluation import ModelEvaluation
from rain_prediction.component.model_pushing import ModelPushing

from rain_prediction.entity.config_entity import (DataIngestionConfig,
                                                  DataCleaningConfig,
                                                  DataValidationConfig,
                                                  DataTransformationConfig,
                                                  ModelTrainingConfig,
                                                  ModelEvaluationConfig,
                                                  ModelPushingConfig)

from rain_prediction.entity.artifact_entity import (DataIngestionArtifact,
                                                    DataCleaningArtifact,
                                                    DataValidationArtifact,
                                                    DataTransformationArtifact,
                                                    ModelTrainingArtifact,
                                                    ModelEvaluationArtifact,
                                                    ModelPushingArtifact)


class TrainPipeline:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()
        self.data_validation_config = DataValidationConfig()
        self.data_cleaning_config = DataCleaningConfig()
        self.data_transformation_config = DataTransformationConfig()
        self.model_training_config = ModelTrainingConfig()
        self.model_evaluation_config = ModelEvaluationConfig()
        self.model_pushing_config = ModelPushingConfig()
    
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
            logging.info("Entered the start_data_transformation method of TrainPipeline class.")
            data_transformation = DataTransformation(data_cleaning_artifact=data_cleaning_artifact,
                                                     data_transformation_config=self.data_transformation_config)
            
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info("Data transformation completed.")
            logging.info("Exited the start_data_transformation method of TrainPipeline class.")
            return data_transformation_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def start_model_training(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainingArtifact:
        try:
            logging.info("Entered the start_model_training method of TrainPipeline class.")
            model_training = ModelTraining(data_transformation_artifact=data_transformation_artifact,
                                           model_training_config=self.model_training_config)
            
            model_training_artifact = model_training.initiate_model_training()
            logging.info("Model Training completed.")
            logging.info("Exited the start_model_training method of TrainPipeline class.")
            return model_training_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def start_model_evaluation(self, data_cleaning_artifact: DataCleaningArtifact,
                               model_training_artifact: ModelTrainingArtifact) -> ModelEvaluationArtifact:
        try:
            logging.info("Entered the start_model_evaluation method of TrainPipeline class.")
            model_evaluation = ModelEvaluation(data_cleaning_artifact=data_cleaning_artifact,
                                              model_training_artifact=model_training_artifact,
                                              model_evaluation_config=self.model_evaluation_config)
            
            model_evaluation_artifact = model_evaluation.initiate_model_evaluation()
            logging.info("Model Evaluation completed.")
            logging.info("Exited the start_model_evaluation method of TrainPipeline class.")
            return model_evaluation_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
        
    def start_model_pushing(self, model_evaluation_artifact: ModelEvaluationArtifact) -> ModelPushingArtifact:
        try:
            logging.info("Entered the start_model_pushing method of TrainPipeline class.")
            model_pushing = ModelPushing(model_evaluation_artifact=model_evaluation_artifact,
                                         model_pushing_config=self.model_pushing_config)
            
            model_pushing_artifact = model_pushing.initiate_model_pushing()
            logging.info("Model Training completed.")
            logging.info("Exited the start_model_pushing method of TrainPipeline class.")
            return model_pushing_artifact
        
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
            model_training_artifact = self.start_model_training(data_transformation_artifact=data_transformation_artifact)
            model_evaluation_artifact = self.start_model_evaluation(data_cleaning_artifact=data_cleaning_artifact,
                                                                    model_training_artifact=model_training_artifact)
            
            if not model_evaluation_artifact.is_model_accepted:
                logging.info(f"Model not accepted.")
                return None
            
            model_pushing_artifact = self.start_model_pushing(model_evaluation_artifact=model_evaluation_artifact)
            
        except Exception as e:
            raise RainPredictionException(e, sys) from e