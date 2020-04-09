from pyspark import SparkConf,SparkContext
spark_conf = SparkConf().setMaster("local").setAppName("ReadHbase")
spark_context = SparkContext(conf = spark_conf)
# from pyspark.sql import SparkSession
# spark_session = SparkSession(spark_context)

hbase_host = "localhost"
hbase_port = "2181"
hbase_table = "TEST_RPT"
hbase_conf = {
        "hbase.zookeeper.quorum": hbase_host,
        "hbase.zookeeper.property.clientPort": hbase_port,
        "hbase.mapreduce.inputtable": hbase_table,
        "hbase.mapreduce.scan.row.start": '18589801',
        "hbase.mapreduce.scan.row.stop" : '18589802',
        "hbase.mapreduce.scan.columns"  : "info:cont info:bd info:sex"
    }

keyConv = "org.apache.spark.examples.pythonconverters.ImmutableBytesWritableToStringConverter"
valueConv = "org.apache.spark.examples.pythonconverters.HBaseResultToStringConverter"

hbase_rdd = spark_context.newAPIHadoopRDD("org.apache.hadoop.hbase.mapreduce.TableInputFormat","org.apache.hadoop.hbase.io.ImmutableBytesWritable","org.apache.hadoop.hbase.client.Result",keyConverter=keyConv,valueConverter=valueConv,conf=hbase_conf)

count = hbase_rdd.count()
hbase_rdd.cache()
output = hbase_rdd.collect()
for (k, v) in output[:1]:
    print (k, v)
