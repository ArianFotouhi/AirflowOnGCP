from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from google.cloud import logging
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
import string
from datetime import datetime
import joblib
from google.oauth2 import service_account
from google.cloud import bigquery
from google.cloud import storage
import pandas as pd
from io import BytesIO

#Extract data & Data Preprocessing
def extract_and_preprocess():


    bucket_name = 'mlopsbucket21'
    blob_name = 'spamData/SMSSpamCollection'
    service_account_info = {
    "type": "service_account",

    }
    
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    storage_client = storage.Client(credentials=credentials, project=service_account_info['project_id'])
    
    logging_client = logging.Client(credentials=credentials, project=service_account_info['project_id'])
    logger = logging_client.logger('hamspam-training-logs')

    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    



    with blob.open("r") as f:
        df = pd.read_csv(f, sep='\t', names=["label", "message"], header=None)



    
    # Add 'length' and 'punct' features
    df['length'] = df['message'].apply(len)
    df['punct'] = df['message'].apply(lambda x: sum([1 for char in x if char in string.punctuation]))
    
    # Save the preprocessed data
    csv_data = df.to_csv(index=False)
    output_path = 'spamData/smsspamcollection.csv'

    blob = bucket.blob(output_path)
    
    with blob.open("w") as f:
        f.write(csv_data)

    logger.log_struct({
                'keyword': 'HamSpam_Detector',
                'description': 'Preprocessing done!',
                'training_timestamp': datetime.now().isoformat(),
                'model_output_msg': "READY!",

            })




# Train Model
def train_model():
 
    bucket_name = 'mlopsbucket21'
    blob_name = 'spamData/smsspamcollection.csv'
    service_account_info = {
    "type": "service_account",

    }

    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    storage_client = storage.Client(credentials=credentials, project=service_account_info['project_id'])
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
        
    logging_client = logging.Client(credentials=credentials, project=service_account_info['project_id'])
    logger = logging_client.logger('hamspam-training-logs')


    #Extract the contents of the zip file
    with blob.open("r") as f:
        df = pd.read_csv(f)


    X = df['message']
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=0)

    text_clf = Pipeline([('tfidf', TfidfVectorizer()), ('clf', RandomForestClassifier())])
    text_clf.fit(X_train, y_train)

    predictions = text_clf.predict(X_test)

    df_conf_mat = pd.DataFrame(metrics.confusion_matrix(y_test, predictions), index=['ham', 'spam'], columns=['ham', 'spam'])

    clf_report = metrics.classification_report(y_test, predictions)


    acc = metrics.accuracy_score(y_test, predictions)


    # Save the model to GCP storage
    model_data = BytesIO()
    joblib.dump(text_clf, model_data)
    model_data.seek(0)  # Rewind the BytesIO object
    blob_name = 'spamData/hamspam_model.joblib'
    blob = bucket.blob(blob_name)
    with blob.open("wb") as f:
        f.write(model_data.getbuffer())


    # Write metrics to BigQuery
    
    algo_name = "hamspam_detection"
    training_time = datetime.now()
    client = bigquery.Client(credentials=credentials, project=service_account_info['project_id'])

    table_id = f"{service_account_info['project_id']}.ml_ops.hamspam"
    table = bigquery.Table(table_id)
    
    row = {"algo_name": algo_name, "training_time": training_time.strftime('%Y-%m-%d %H:%M:%S'), "model_metrics": clf_report}
    client.insert_rows_json(table, [row])

    logger.log_struct({
                'keyword': 'HamSpam_Detector',
                'description': 'Training done!',
                'training_timestamp': datetime.now().isoformat(),
                'model_output_msg': "READY!",

            })

    

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

# Instantiate the DAG
dag = DAG(
    'dag_hamspam_continuous_training',
    default_args=default_args,
    description='A Training DAG',
    schedule_interval=None,
)

# Define the tasks/operators
extract_preprocess_task = PythonOperator(
    task_id='extract_and_preprocess',
    python_callable=extract_and_preprocess,
    dag=dag,
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

extract_preprocess_task >> train_task