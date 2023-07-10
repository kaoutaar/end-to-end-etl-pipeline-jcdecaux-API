from airflow.models import DAG
from airflow.operators.python import PythonOperator
import datetime as dt
from datetime import timedelta
import pendulum
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from appscripts import producer, batch_consumer, static_data


default_args={'owner':'velib',
              'retries':2,
              'retry_delay':timedelta(seconds=300)}


with DAG(dag_id="api_to_kafka",
         default_args = default_args,
        #  is_paused_upon_creation=False,
         catchup = False,
         max_active_runs=1,
         start_date=pendulum.datetime(2023,7,8, tz="Europe/Paris"),
         schedule=dt.timedelta(seconds=30)) as dag:
    task1 = PythonOperator(task_id="api_to_kafka", python_callable=producer.send_api_data)


with DAG(dag_id="kafka_to_mssql",
         default_args = default_args,
         catchup = False,
         start_date=pendulum.datetime(2023,7,8, tz="Europe/Paris"),
         schedule="0 5 * * *") as dag:
    task1 = PythonOperator(task_id="kafka_to_mssql", python_callable=batch_consumer.batch_send_mssql)


with DAG(dag_id="static_data_to_DW",
         default_args = default_args,
         catchup = False,
         start_date=pendulum.datetime(2023,7,8, tz="Europe/Paris"),
         schedule="@once") as dag:
    task1 = PythonOperator(task_id="static_data_to_DW", python_callable=static_data.send_static_data)