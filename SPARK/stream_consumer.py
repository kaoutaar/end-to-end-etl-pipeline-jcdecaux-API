from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructField, StructType, StringType, IntegerType, BooleanType, TimestampType, LongType


topic = "velib_data"
client = "JCDecaux API"
print("data stream from %s" %client)
print("Receiving orders data from Kafka topic %s" %topic)


spark = SparkSession\
    .builder\
    .master('local[*]')\
    .appName('velib_stream_consumer')\
    .config("spark.dynamicAllocation.enabled", True)\
    .config("spark.dynamicAllocation.shuffleTracking.enabled", True)\
    .config("spark.sql.shuffle.partitions", 1)\
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

df = spark.readStream\
    .format("kafka")\
    .option("kafka.group.id", "streamspark")\
    .option("kafka.bootstrap.servers", "kafka:9092")\
    .option("subscribe", topic)\
    .option("startingOffsets", "earliest")\
    .option("failOnDataLoss", False)\
    .load()
    
schema = StructType(
    [StructField("number",IntegerType(),True),
     StructField("contract_name",StringType(),True),
     StructField("name",StringType(),True),
     StructField("address",StringType(),True),
     StructField("position",StringType(),True),
     StructField("banking",BooleanType(),True),
     StructField("bonus",BooleanType(),True),
     StructField("bike_stands",IntegerType(),True),
     StructField("available_bike_stands",IntegerType(),True),
     StructField("available_bikes",IntegerType(),True),
     StructField("status",StringType(),True),
     StructField("last_update",LongType(),True)])

df = df.select(df.timestamp, F.from_json(F.decode(df.value, "UTF-8"), "ARRAY<STRING>").alias("val"))


file = "/opt/bitnami/spark/streampool/bruxelles.parquet"
def write_2_loc(batchdata, batchId):
    print(batchdata.count())
    if batchdata.isEmpty():
        batchdata.write.format("console").mode("append").save()
    else:
        batchdata = batchdata.tail(1)
        batchdata = spark.createDataFrame(batchdata, )
        batchdata = batchdata.select(batchdata.timestamp, F.explode(batchdata.val).alias("val"))
        batchdata = batchdata.select(batchdata.timestamp, F.from_json(batchdata.val, schema=schema).alias("val"))
        batchdata = batchdata.select(batchdata.timestamp, F.col("val.*"))
        batchdata = batchdata.filter(batchdata.contract_name=="bruxelles")\
            .withColumn("last_update", (batchdata.last_update/F.lit(1000)).cast(TimestampType()))
        batchdata.write.format("parquet").mode("overwrite").save(file)

q = df.writeStream.foreachBatch(write_2_loc).trigger(processingTime="40 seconds").start()

try:
    q.awaitTermination()
except KeyboardInterrupt:
    print("test terminating...")