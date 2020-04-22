import pandas as pd
import re


def load_generalSummary_std_name_rels():
    """
    加载总检1标准化异常名称映射表
    """
    df = pd.read_csv("./datas/abn_std_v1.0.7.csv")
    std_name_list = df["标准化名称"]
    show_name_list = df["检出名称"]
    name_mapper = {}
    for index, name_str in enumerate(show_name_list):
        name_str = str(name_str)
        if name_str and name_str != "nan":
            names = name_str.split(",")
            for name in names:
                if name:
                    name_mapper[name] = std_name_list[index]
    return name_mapper


generalSummary_std_names_mapper = load_generalSummary_std_name_rels()
print("加载总检1标准化异常名称映射表...")


# 不参与分词的特殊符号替换模式
not_needed_symbols_replace_pattern = re.compile(
    r"[\s+`~!@#$%^&*()=|{}'\[\].。<>/?！￥…（）—\-【】‘;；:：”“’,，、？\\]"
)


def clean_abn_name(abn_name):
    """
    报告异常项名称清洗
    """
    new_abn_name = (
        not_needed_symbols_replace_pattern.sub("", abn_name)
        .replace("Ⅰ", "1")
        .replace("Ⅱ", "2")
        .replace("Ⅲ", "3")
        .lower()
    )
    return new_abn_name


def generalSummary_standardlize(summary):
    """
    总检1标准化
    """
    abnormal_names = []
    for item in summary:
        summary_name = item["summaryName"]
        abnormal_names.append(clean_abn_name(summary_name))
    return abnormal_names


# 1. 判断名称是否可以被标准化，分 chk_item_name 和 chk_ind_name
# 2. 记录标准化名称
# 3. 记录关联指标分析-组合逻辑中的描述型指标是否参检
def summary_analyse(report):
    generalSummary = report["generalSummarys"]
    abnormal_names = generalSummary_standardlize(generalSummary)
    std_abnormal_names = [generalSummary_std_names_mapper.get(name, None) for name in abnormal_names]
    # print(std_abnormal_names)
    return std_abnormal_names



