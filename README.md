# End-to-end ETL pipeline - jcdecaux API

<br style=“line-height:10;”> 

![image](https://github.com/kaoutaar/end-to-end-etl-pipeline-jcdecaux-API/assets/51215027/ae516d3c-328a-4f7f-8a01-3f037456f125)


<br style=“line-height:10;”> 

The architecture consists of 2 main pipelines:
* Batch pipeline: after data being served to kafka, we use spark analytics engine to transform and process data in batches and send tables into a datawarehouse
* Stream pipeline: we use spark streaming to fetch and filter data that will be served in our web application in ~ realtime.


### Jcdecaux API:
The API provides information about the location of the bike stations in Europe, the availability of bikes and parking spaces in real time, in addition to other details.
A single call of this API returns the most recent information about all the existing stations, "the most recent" could be the last update got 1–2 min ago, 
which doesn't really mean real-time data, we can do nothing to improve it, this is how the API works. 
And to make the API act like a stream source but also avoid to overload the server, a script is scheduled in Airflow to fetch data every 30 seconds, 
this data is then sent to kafka cluster using kafka produder.

### kafka:
kafka receives data and store it in a topic called "velib_data" waiting to be polled, two consumer groups are configured to consume data from kafka broker in parallel:
1) batch-consumer: using spark-connect, a spark client script is in charge of polling data from kafka in batches, is takes care of transforming and creating tables that are sent to the datawarehouse, 
Airflow is configured to run this job every day at 5am,
2) stream-consumer: spark structured streaming is used here to allow consuming data from kafka broker in real time, the transformed data is then served to the web-based application. 
**Note:** spark-connect doesn't support yet streaming operations, which means in our case, the stream-consumer script will live in the same evironment as spark cluster.

### Datawarehouse:
the choice of the right tool for datawarehousing and OLAP system is out of the scope of this project. In our case we use SQLserver.

### web application:
to create a web application, there are a plenty of choices, the easiest one (to learn and implement) IMHO is streamlit, you don't need to be a web developer to use it, 
with a single python script your application is ready to be served.

<br style=“line-height:10;”> 

# Environment

* the whole architecture can be installed locally in one go using dockercompose. you must have at least 8GB ram for it to run.

* for zookeeper, kafka, spark and SQLserver,  each service runs in its own separate container

* Airflow is configured to use local executor to enable parallel tasks, for this we need to set up a postgreSQL database for backend service, for more options read the following link
https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html
* the web application could have been set in its own server, but the whole architecture is already taking enough space and cpu,
  this is why the app will live with spark engine in the same container

<br style=“line-height:20;”> 

# How to run

after cloning the repository, using a terminal, cd to its directory and run

> docker-compose -f dockercompose.yaml up

this is going to take a few minutes because it will install base images and then build the costumized ones.
after all containers are up, using your browser, you can view the airflow UI at 
> localhost:8080


Notes: 
* airflow webserver may take extra time to start, so be patient!
* the credentials to login are admin:admin
* the DAGs are configured to not automatically start when the servers are up, you have to start them manually using the toggle in the left, but you can change this option if needed
* the first DAG to be run is **api-to-kafka**

<br style=“line-height:20;”> 


![Screenshot (47)](https://github.com/kaoutaar/end-to-end-etl-pipeline-jcdecaux-API/assets/51215027/b9ed38f8-3252-4f00-97d0-c03d4749f0fc)

wait at least 2 min to run the web application at 
> localhost:8501


![Screenshot (52)](https://github.com/kaoutaar/end-to-end-etl-pipeline-jcdecaux-API/assets/51215027/0eb62674-0f3c-4014-a5b0-22a2de8576b9)


<br style=“line-height:10;”> 
 
 
Here we go.. the app shows that the station **Gare Centrale** in Brussels has 24 bikes availables. and 11 free docks.

