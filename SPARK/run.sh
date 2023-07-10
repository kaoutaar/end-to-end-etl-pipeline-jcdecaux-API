#!/bin/sh

(/opt/bitnami/spark/sbin/start-connect-server.sh --packages org.apache.spark:spark-connect_2.12:3.4.0 &
sleep 200) &&
python /opt/bitnami/spark/mycode/stream_consumer.py &
(sleep 100 &&
streamlit run /opt/bitnami/spark/mycode/velib_app.py)