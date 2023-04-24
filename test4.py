from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import Normalizer, StandardScaler
import random
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 pyspark-shell'
import time

kafka_topic_name = "testing"
kafka_bootstrap_servers = '127.0.1.1:9092'

spark = SparkSession \
        .builder \
        .appName("Structured Streaming ") \
        .master("local[*]") \
        .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Construct a streaming DataFrame that reads from topic
flower_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic_name) \
        .option("startingOffsets", "latest") \
        .load()

flower_df1 = flower_df.selectExpr("CAST(value AS STRING)", "timestamp")


flower_schema_string = "order_id INT,sepal_length DOUBLE,sepal_length DOUBLE,sepal_length DOUBLE,sepal_length DOUBLE,species STRING"



flower_df2 = flower_df1 \
        .select(from_csv(col("value"), flower_schema_string) \
                .alias("flower"), "timestamp")


flower_df3 = flower_df2.select("flower.*", "timestamp")

    
flower_df3.createOrReplaceTempView("flower_find");
song_find_text = spark.sql("SELECT * FROM flower_find")
flower_agg_write_stream = song_find_text \
        .writeStream \
        .trigger(processingTime='5 seconds') \
        .outputMode("append") \
        .option("truncate", "false") \
        .format("memory") \
        .queryName("testedTable") \
        .start()

flower_agg_write_stream.awaitTermination(1)
df = spark.sql("SELECT * FROM testedTable")
df.show(3)