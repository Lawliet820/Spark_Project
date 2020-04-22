from pyspark import SparkConf, SparkContext
from mod.decodeReport import report_decode
from mod.summaryAnalyse_v4 import summary_analyse
import pandas as pd
import time

spark_conf = SparkConf().setMaster("local[*]").setAppName("spark_project")
spark_context = SparkContext(conf=spark_conf)
# from pyspark.sql import SparkSession
# spark_session = SparkSession(spark_context)

hbase_host = "192.168.1.150"
hbase_table = "TEST_RPT"


def read_hbase(report_id_start, report_id_stop):
    hbase_conf = {
        "hbase.zookeeper.quorum": hbase_host,
        "hbase.mapreduce.inputtable": hbase_table,
        "hbase.mapreduce.scan.row.start": report_id_start,
        "hbase.mapreduce.scan.row.stop": report_id_stop,
        "hbase.mapreduce.scan.columns": "info:cont"
    }

    keyConv = "org.apache.spark.examples.pythonconverters.ImmutableBytesWritableToStringConverter"
    valueConv = "org.apache.spark.examples.pythonconverters.HBaseResultToStringConverter"

    hbase_rdd = spark_context.newAPIHadoopRDD(
        "org.apache.hadoop.hbase.mapreduce.TableInputFormat",
        "org.apache.hadoop.hbase.io.ImmutableBytesWritable",
        "org.apache.hadoop.hbase.client.Result",
        keyConverter=keyConv,
        valueConverter=valueConv,
        conf=hbase_conf,
        batchSize=0,
    )
    return hbase_rdd


def main():
    t0 = time.time()
    report_id_start = "18589802"
    report_id_stop  = "18689802"
    hbase_rdd = read_hbase(report_id_start, report_id_stop)
    report_counts = hbase_rdd.count()
    print(report_counts)
    decode_rdd = hbase_rdd.map(lambda xxx: xxx[1])
    decode_rdd = decode_rdd.map(lambda xxx: report_decode(xxx))
    decode_rdd.cache()
    # generalSummarys_rdd = decode_rdd.map(lambda xxx: xxx['generalSummarys'])
    abnormals_rdd = decode_rdd.map(lambda xxx: summary_analyse(xxx))
    abnormals_rdd = abnormals_rdd.map(lambda xxx: {"abnormals": xxx})
    result_list = abnormals_rdd.collect()
    result_df = pd.DataFrame.from_dict(result_list)
    result_df.to_csv("../01output/result_df.csv")
    t1 = time.time()
    print('总耗时：', t1-t0)
    
if __name__ == '__main__':
    main()