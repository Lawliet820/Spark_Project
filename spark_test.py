import time 
from pyspark import SparkConf, SparkContext

conf = SparkConf().setMaster("local").setAppName("My App")
sc = SparkContext(conf = conf)

rawFilePath = "file:///home/hadoop/lawliet/00raw_rdd_files/"
rawRddData = sc.textFile(rawFilePath)

t0 = time.time()
numAs = rawRddData.filter(lambda line: 'a' in line).count()
t1 = time.time()
numBs = rawRddData.filter(lambda line: 'b' in line).count()
t2 = time.time()
numCs = rawRddData.filter(lambda line: 'c' in line).count()
t3 = time.time()

print('Lines with a: %s, Lines with b: %s' % (numAs, numBs))
print(t3-t2, t2-t1, t1-t0)

targetFilePath = "file:///home/hadoop/lawliet/01target_rdd_files/"
rawRddData.saveAsTextFile(targetFilePath)