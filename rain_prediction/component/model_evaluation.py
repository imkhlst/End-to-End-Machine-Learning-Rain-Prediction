import sys
import pandas as pd
from typing import Optional
from dataclasses import dataclass

from sklearn.metrics import f1_score

from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging
from rain_prediction.constants import TARGET_COLUMN
from rain_prediction.entity.s3_estimator import RainEstimator
from rain_prediction.entity.estimator import RainModel
from rain_prediction.entity.estimator import TargetValueMapping
from rain_prediction.entity.config_entity import ModelEvaluationConfig
from rain_prediction.entity.artifact_entity import (DataCleaningArtifact,
                                                    ModelTrainingArtifact,
                                                    ModelEvaluationArtifact)


@dataclass
class EvaluateModelResponse:
    trained_model_f1_score: float
    best_model_f1_score: float
    is_model_accepted: bool
    difference: float


class ModelEvaluation:
    def __init__(self,data_cleaning_artifact: DataCleaningArtifact,
                 model_training_artifact: ModelTrainingArtifact,
                 model_evaluation_config: ModelEvaluationConfig):
        try:
            self.model_evaluation_config = model_evaluation_config
            self.data_cleaning_artifact = data_cleaning_artifact
            self.model_training_artifact = model_training_artifact
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def get_best_model(self) -> Optional[RainEstimator]:
        """_summary_

        Returns:
            Optional[RainEstimator]: _description_
        """
        try:
            bucket_name = self.model_evaluation_config.bucket_name
            model_path = self.model_evaluation_config.s3_model_key_path
            rain_estimator = RainEstimator(bucket_name = bucket_name,
                                           model_path = model_path)
            if rain_estimator.is_model_present(model_path = model_path):
                return rain_estimator
            return None
        
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def evaluate_model(self) -> EvaluateModelResponse:
        """_summary_

        Returns:
            EvaluateModelResponse: _description_
        """
        try:
            test_dataframe = pd.read_csv(self.data_cleaning_artifact.cleaned_test_file_path)
            
            X, y = test_dataframe.drop(TARGET_COLUMN, axis=1), test_dataframe[TARGET_COLUMN]
            y = y.replace(TargetValueMapping()._asdict()).infer_objects(copy=False).squeeze()
            
            trained_model_f1_score = self.model_training_artifact.metric_artifact.f1_score
            
            best_model_f1_score = None
            best_model = self.get_best_model()
            if best_model is not None:
                y_pred_best_model = best_model.predict(X)
                best_model_f1_score = f1_score(y, y_pred_best_model)
            
            tmp_best_model_score = 0 if best_model_f1_score is None else best_model_f1_score
            result = EvaluateModelResponse(trained_model_f1_score=trained_model_f1_score,
                                           best_model_f1_score=best_model_f1_score,
                                           is_model_accepted=trained_model_f1_score>tmp_best_model_score,
                                           difference=trained_model_f1_score - tmp_best_model_score)
            logging.info(f"Result: {result}")
            return result
        
        except Exception as e:
            raise RainPredictionException(e, sys)
    
    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        """_summary_

        Returns:
            ModelEvaluationArtifact: _description_
        """
        logging.info("Entered initiate_model_evaluation method of ModelEvaluation class.")
        
        try:
            evaluate_model_response = self.evaluate_model()
            s3_model_path = self.model_evaluation_config.s3_model_key_path
            
            model_evaluation_artifact = ModelEvaluationArtifact(is_model_accepted=evaluate_model_response.is_model_accepted,
                                                                s3_model_path=s3_model_path,
                                                                trained_model_path=self.model_training_artifact.trained_model_file_path,
                                                                changed_accuracy=evaluate_model_response.difference)
            
            logging.info("Your model has been evaluted.")
            logging.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            logging.info("Exited initiate_model_evaluation method of ModelEvaluation class.")
            return model_evaluation_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e