import sys

from rain_prediction.cloud_storage.aws_storage import SimpleStorageService
from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging
from rain_prediction.entity.artifact_entity import ModelPushingArtifact, ModelEvaluationArtifact
from rain_prediction.entity.config_entity import ModelPushingConfig
from rain_prediction.entity.s3_estimator import RainEstimator


class ModelPushing:
    def __init__(self, model_evaluation_artifact: ModelEvaluationArtifact,
                 model_pushing_config: ModelPushingConfig):
        self.s3 = SimpleStorageService()
        self.model_evaluation_artifact = model_evaluation_artifact
        self.model_pushing_config = model_pushing_config
        self.rain_estimator = RainEstimator(bucket_name=model_pushing_config.bucket_name,
                                            model_path=model_pushing_config.s3_model_key_path)
    
    def initiate_model_pushing(self) -> ModelPushingArtifact:
        """_summary_

        Returns:
            ModelPushingArtifact: _description_
        """
        logging.info("Entered initiate_model_pushing method of ModelPushing class.")
        
        try:
            logging.info("Uploading artifacts folder to s3 bucket.")
            
            self.rain_estimator.save_model(from_file=self.model_evaluation_artifact.trained_model_path)
            
            model_pushing_artifact = ModelPushingArtifact(bucket_name=self.model_pushing_config.bucket_name,
                                                          s3_model_key_path=self.model_pushing_config.s3_model_key_path)
            
            logging.info("Artifact folder has been uploaded to s3 bucket.")
            logging.info(f"Model pushing artifact: {model_pushing_artifact}")
            logging.info("Exited initiate_model_pushing method of ModelPushing class.")
            return model_pushing_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e