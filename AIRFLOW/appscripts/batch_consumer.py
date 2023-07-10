from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import StorageLevel
from pyspark.sql.types import StructField, StructType, StringType, IntegerType, TimestampType, DateType
import datetime
import pandas as pd


def batch_send_mssql():
    topic = "velib_data"
    client = "JCDecaux API"
    print("data stream from %s" %client)
    print("Receiving orders data from Kafka topic %s" %topic)

    #connection to remote spark server
    spark = SparkSession\
        .builder\
        .remote("sc://spark:15002")\
        .appName('velib_batch_consumer')\
        .config("spark.dynamicAllocation.enabled", True)\
        .config("spark.dynamicAllocation.shuffleTracking.enabled", True)\
        .config("spark.worker.cleanup.enabled", True)\
        .config("spark.sql.shuffle.partitions", 1)\
        .getOrCreate()


    yesterday = datetime.datetime.now() - datetime.timedelta(1)
    year = yesterday.year
    month = yesterday.month
    day = yesterday.day
    start = datetime.datetime(year, month, day,0,0)
    end = datetime.datetime(year, month, day,23,59,59)
    start_timestamp = int(datetime.datetime.timestamp(start))*1000 #millisecond
    end_timestamp = int(datetime.datetime.timestamp(end))*1000

    df = spark.read\
        .format("kafka")\
        .option("kafka.group.id	", "batchspark")\
        .option("kafka.bootstrap.servers", "kafka:9092")\
        .option("subscribe", topic)\
        .option("failOnDataLoss", False)\
        .option("startingTimestamp",  start_timestamp)\
        .option("endingTimestamp",end_timestamp)\
        .load()


    stations_schema = StructType(
        [StructField("name",StringType(),True),
        StructField("contract_name",StringType(),True),
        StructField("bike_stands",IntegerType(),True),
        StructField("available_bikes",IntegerType(),True),
        StructField("status",StringType(),True)])

    df = df.select(df.timestamp, F.explode(F.from_json(F.decode(df.value, "UTF-8"), "ARRAY<STRING>")).alias("val"))
    df = df.select(df.timestamp, F.from_json(df.val, schema=stations_schema).alias("val"))
    df = df.select(df.timestamp, F.col("val.*")).persist(StorageLevel.MEMORY_ONLY)

    def aggreg(key, df):
        s = df.available_bikes-df.available_bikes.shift()
        return pd.DataFrame([key + (s.where(s<0,0).abs().sum(),
                                    s.where(s>0,0).sum(),
                                    df["status"].mode()[0],
                                    df["bike_stands"].max(),)])

    schema = StructType([StructField("Cont_name", StringType(), True),
                StructField("Station_name", StringType(), True),
                StructField("Date_ID", TimestampType(), True),
                StructField("OUT_Bikes", IntegerType(), True),
                StructField("IN_Bikes", IntegerType(), True),
                StructField("Station_status", StringType(), True),
                StructField("Capacity", IntegerType(), True)])

    df = df.groupby("contract_name","name",F.date_trunc('hour',df.timestamp)).applyInPandas(aggreg,schema=schema)

    date_df = df.select("Date_ID")\
        .withColumns({"Year_":F.year(df.Date_ID), "Month_":F.month(df.Date_ID), "Day_":F.dayofmonth(df.Date_ID), "DayName":F.dayofweek(df.Date_ID), "Hour_":F.hour(df.Date_ID)})\
        .withColumn("Date_ID", F.unix_timestamp(F.date_format(df.Date_ID, "yyyy-MM-dd hh:mm"), "yyyy-MM-dd hh:mm"))\
        .dropDuplicates()


    date_df.printSchema()
    date_df.show()

    #connection
    dbserver = "mssql" 
    db_name = "velib"
    jdbcUrl = f"jdbc:sqlserver://{dbserver}:1433;DatabaseName={db_name}"
    driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"

    station_info = spark.read\
        .format("jdbc")\
        .option("url", jdbcUrl)\
        .option("dbtable", "Stations")\
        .option("user", "sa")\
        .option("password", "MY1password")\
        .load()

    cond = ["Station_name", "Cont_name"]
    bus_df = df.join(station_info, on=cond, how = "left")
    bus_df = bus_df.select(["OUT_Bikes", "IN_Bikes", "Station_status", "Capacity", "Date_ID", "Station_ID", "Cont_name"])
    bus_df = bus_df.withColumn("Date_ID", F.unix_timestamp(F.date_format(bus_df.Date_ID, "yyyy-MM-dd hh:mm"), "yyyy-MM-dd hh:mm"))

    bus_df.printSchema()
    bus_df.show()

    #write to sql server
    bus_df.write.\
        format("jdbc").\
        option("url", jdbcUrl).\
        option("driver", driver).\
        option("dbtable", "BusinessFact").\
        option("user", "sa").\
        option("password", "MY1password").\
        mode("append").\
        save()

    date_df.write.\
        format("jdbc").\
        option("url", jdbcUrl).\
        option("driver", driver).\
        option("dbtable", "ActivityDate").\
        option("user", "sa").\
        option("password", "MY1password").\
        mode("append").\
        save()