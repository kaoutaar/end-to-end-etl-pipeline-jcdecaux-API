#!/bin/sh

airflow db init &&
airflow users create --username admin --password admin --firstname kaou --lastname tar --role Admin --email admin@example.com ;
airflow webserver &
airflow scheduler