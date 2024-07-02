# Continuous Training by Airflow on GCP
This repository contains an Apache Airflow DAG designed to continuously train a machine learning model for detecting spam messages (HamSpam) using Google Cloud Composer. The DAG extracts data from Google Cloud Storage, preprocesses it, trains a model, and logs the results.


## Overview

-The HamSpam Detection Continuous Training DAG performs the following steps:

-Extracts and preprocesses data from Google Cloud Storage.

-Trains a RandomForestClassifier model using scikit-learn.

-Saves the trained model back to Google Cloud Storage.

-Logs training metrics to Google Cloud Logging and BigQuery.

## Prerequisites

- **Google Cloud Platform Account**: Ensure you have a GCP account with appropriate permissions.
- **Google Cloud Composer**: An environment set up with Airflow.
- **Google Cloud Storage**: A bucket to store data and model files.
- **Google BigQuery**: A dataset and table for logging model metrics.
- **Service Account**: A service account with the following permissions:
  - Storage Admin
  - BigQuery Admin
  - Logging Admin
