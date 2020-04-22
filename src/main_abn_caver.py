import json
import time
import happybase
import os
import csv
import traceback
import pandas as pd
from mod.preprocessor import pre_process
from mod.summaryAnalyse_v4 import summary_analyse
from concurrent.futures import ProcessPoolExecutor, as_completed

table_name = 'TEST_RPT'
database_host = '192.168.1.152'
database_port = 9090


def scanner(database_host, database_port, table_name, start='', end='', *args, **kwrgs):
    """
    链接hbase，获取报告数据
    """
    c = happybase.Connection(database_host, port=database_port)
    t = c.table(table_name)
    return t.scan(*args, **kwrgs, row_start=start, row_stop=end)


def job(start, end):
    count = 1
    dataset = scanner(
        database_host, database_port, table_name, start=start, end=end
    )
    result_list = []
    t0 = time.time()
    for key, row in dataset:
        report_id = key.decode()
        key = report_id
        count += 1
        if row:
            raw_data = json.loads(row[b'info:cont'].decode())
            one_report = {
                # "report_id": report_id,
                # 'brithday': row[b'info:bd'].decode(),
                # 'gender': row[b'info:sex'].decode(),
                # 'checkItems': raw_data['checkItems'],
                'generalSummarys': raw_data['generalSummarys'],
                # 'generalSummarys2': raw_data['generalSummarys2'],
            }
            abnormals = summary_analyse(one_report)
            abnormals_dict = {
                "abnormals": abnormals,
            }
            result_list.append(abnormals_dict)

        if count % 2000 == 0:
            t1 = time.time()
            print(os.getpid(), report_id, count, t1 - t0)
            t0 = time.time()

    if len(result_list) > 0:
        result_df = pd.DataFrame.from_dict(result_list)
        result_df.to_csv("../01output/part_to_{}.csv".format(key))


def main1():
    job("18589801", "18589803")


def main():
    # 31337233 - 39216845 之间无数据
    # start = 18589801
    # end = 58111013
    start = 18589801
    end =   58111013
    gap =      50000
    max_workers = 16

    slices = [[i, i + gap] for i in range(start, end, gap)]
    slices[-1][1] = end

    total = len(slices)
    print("共计", total)
    executor = ProcessPoolExecutor(max_workers=max_workers)
    tasks = []
    for slice_ in slices:
        tasks.append(executor.submit(job, str(slice_[0]), str(slice_[1])))
        # print("slice:", slice_)
    n_count = 0
    for future in as_completed(tasks):
        n_count += 1
        print("{}/{}".format(n_count, total))
        try:
            ret = future.result()
        except Exception as e:
            print("========================")
            raise


if __name__ == '__main__':
    main()

