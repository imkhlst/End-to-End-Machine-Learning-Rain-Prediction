import os
from datetime import date

DATABASE_NAME = "Rain-Prediction"

COLLECTION_NAME = "weatherdata"

MONGODB_URL_KEY = "MONGODB_URL"

PIPELINE_NAME: str = "rainpredition"

ARTIFACT_DIR: str = "artifact"

FILE_NAME: str = "weatherAUS.csv"
TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"
CLEANED_TRAIN_FILE_NAME: str = "cleaned_train.csv"
CLEANED_TEST_FILE_NAME: str = "cleaned_test.csv"

MODEL_FILE_NAME = "model.pkl"

TARGET_COLUMN = "RainTomorrow"
PREPROCESSING_OBJECT_FILE_NAME = "preprocessing.pkl"
SCHEMA_FILE_PATH = os.path.join("config", "schema.yaml")

"""
Data Ingestion related constant start with DATA_INGESTION VAR NAME
"""
DATA_INGESTION_COLLECTION_NAME: str = "weatherdata"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2

"""
Data Validation related constant start with DATA_VALIDATION VAR NAME
"""
DATA_VALIDATION_DIR_NAME: str = "data_validation"
DATA_VALIDATION_DRIFT_REPORT_DIR: str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "report.ymal"

"""
Data Cleaning related constant start with DATA_CLEANING VAR NAME
"""
DATA_CLEANING_DIR_NAME: str = "data_cleaning"
DATA_CLEANING_CLEANED_DATA_DIR: str = "cleaned"

"""
Data Transformation related constant start with DATA_TRANSFORMATION VAR NAME
"""
DATA_TRANSFORMATION_DIR_NAME: str = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR: str = "transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR: str = "transformed_object"