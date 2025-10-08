import sys
from typing import Tuple

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from rain_prediction.exception import RainPredictionException
from rain_prediction.logger import logging
from rain_prediction.utils.main_utils import (load_numpy_array_data,
                                              read_yaml_file, load_object, save_obj)
from rain_prediction.entity.config_entity import ModelTrainingConfig
from rain_prediction.entity.artifact_entity import (DataTransformationArtifact,
                                                    ModelTrainingArtifact,
                                                    ClassificationMetricArtifact)
from rain_prediction.entity.estimator import RainModel

class ModelTraining:
    def __init__(self, data_transformation_artifact: DataTransformationArtifact,
                 model_training_config: ModelTrainingConfig):
        """_summary_

        Args:
            data_transformation_artifact (DataTransformationArtifact): _description_
            model_training_config (ModelTrainingConfig): _description_
        """
        self.data_transformation_artifact = data_transformation_artifact
        self.model_training_config = model_training_config
    
    def get_model_object_and_report(self, train: np.array, test: np.array) -> Tuple[object, object]:
        """_summary_

        Args:
            train (np.array): _description_
            test (np.array): _description_

        Returns:
            Tuple[object, object]: _description_
        """
        try:
            
            logging.info("Using neuro-mf to get best model object and report.")
             
            X_train, y_train, X_test, y_test = train[:, :-1], train[:, -1], test[:, :-1], test[:, -1]
            
            model_object = KNeighborsClassifier(weights = 'distance', 
                                                p = 1,
                                                n_neighbors = 4,
                                                leaf_size = 20,
                                                algorithm = 'kd_tree')
            model_object.fit(X_train, y_train)
            
            y_pred = model_object.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            metric_artifact = ClassificationMetricArtifact(accuracy = accuracy,
                                                           f1_score = f1,
                                                           precision_score = precision,
                                                           recall_score = recall)
            
            return model_object, metric_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e
    
    def initiate_model_training(self, ) -> ModelTrainingArtifact:
        """_summary_

        Returns:
            ModelTrainingArtifact: _description_
        """
        logging.info("Entered initiate_model_training method of ModelTrainer class.")
        
        try:
            train_arr = load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_train_file_path)
            test_arr = load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_test_file_path)
            
            model_object, metric_artifact = self.get_model_object_and_report(train=train_arr,
                                                                             test=test_arr)
            
            preprocessing_object = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            
            if metric_artifact.accuracy < self.model_training_config.expected_accuracy:
                logging.info("No best model found with score more than base score.")
                raise Exception("No base model found with score more than base score.")
            
            rain_model = RainModel(preprocessing_object=preprocessing_object,
                                   trained_model_object=model_object)
            logging.info("Created rain model object with preprocessor and model.")
            logging.info("Created best model file path.")
            save_obj(self.model_training_config.trained_model_file_path, rain_model)
            
            model_trainer_artifact = ModelTrainingArtifact(
                trained_model_file_path=self.model_training_config.trained_model_file_path,
                metric_artifact=metric_artifact
            )
            logging.info(f"Model training artifact: {model_trainer_artifact}")
            return model_trainer_artifact
        
        except Exception as e:
            raise RainPredictionException(e, sys) from e