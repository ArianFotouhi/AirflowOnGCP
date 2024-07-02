# Continuous Training by Airflow on GCP
This repository contains an Apache Airflow DAG designed to continuously train a machine learning model for detecting spam messages (HamSpam) using Google Cloud Composer. The DAG extracts data from Google Cloud Storage, preprocesses it, trains a model, and logs the results.


## Overview

- The HamSpam Detection Continuous Training DAG performs the following steps:
- Extracts and preprocesses data from Google Cloud Storage.
- Trains a RandomForestClassifier model using scikit-learn.
- Saves the trained model back to Google Cloud Storage.
- Logs training metrics to Google Cloud Logging and BigQuery.

## Prerequisites

- **Google Cloud Platform Account**: Ensure you have a GCP account with appropriate permissions.
- **Google Cloud Composer**: An environment set up with Airflow.
- **Google Cloud Storage**: A bucket to store data and model files.
- **Google BigQuery**: A dataset and table for logging model metrics.
- **Service Account**: A service account with the following permissions:
  - Storage Admin
  - BigQuery Admin
  - Logging Admin

## Set Up
bigquery_table_creation.sql file contains queries that should be run in Big Query UI where it creates the schema and table. Plus, the file dags_airflow.py, is ought to be uploaded to Airflow working directory of the created cloud composer instance (airflow) where it automatically creates the dags and pipeline.


Airflow in Cloud Composer:
![CC Image]([https://github.com/ArianFotouhi/AirflowOnGCP/blob/main/assets/CloudComposer.png?raw=true))

Created files in Google Storage:
![GS Image]([https://github.com/ArianFotouhi/AirflowOnGCP/blob/main/assets/GoogleStorage.png?raw=true))

Created Pipeline for Continuous Training:
![AF Image]([(https://github.com/ArianFotouhi/AirflowOnGCP/blob/main/assets/airflow-1.png?raw=true)))

Result insertion to Big Query:
![BQ Image]([https://github.com/example-user/example-repo/raw/main/assets/example.png](https://github.com/ArianFotouhi/AirflowOnGCP/blob/main/assets/BigQuery.png?raw=true))





## DAG Overview

The DAG is defined in `dag_hamspam_continuous_training.py` and consists of two main tasks: `extract_and_preprocess` and `train_model`.

### Tasks

#### extract_and_preprocess

- Extracts data from the specified Cloud Storage bucket.
- Preprocesses the data by adding features and saves the preprocessed data back to Cloud Storage.
- Logs the preprocessing status to Cloud Logging.

#### train_model

- Reads the preprocessed data from Cloud Storage.
- Trains a RandomForestClassifier model using scikit-learn.
- Saves the trained model to Cloud Storage.
- Logs training metrics (confusion matrix, classification report, accuracy) to Cloud Logging and BigQuery.

## Logging and Monitoring

The DAG uses Google Cloud Logging to log messages and Google BigQuery to store model metrics.

- **Google Cloud Logging**: Logs information about preprocessing and training steps, including timestamps and descriptions.
- **Google BigQuery**: Stores model metrics (e.g., classification report) in a specified table for further analysis.

### Example Log Entry

```json
{
  "keyword": "HamSpam_Detector",
  "description": "Training done!",
  "training_timestamp": "2023-07-01T12:34:56.789Z",
  "model_output_msg": "READY!"
}
