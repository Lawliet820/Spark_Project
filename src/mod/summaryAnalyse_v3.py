import pandas as pd
import re


def load_chk_item_std_name_rels():
    """
    加载标准化名称映射表
    """
    df = pd.read_csv("./datas/描述型指标名称标准化结果v1.0.6.csv")
    clean_name_list = df["清洗后名称"]
    std_name_list = df["标准名称"]
    check_type_list = df["检查方式"]
    part_name_list = df["部位"]
    text_mapper = {}
    for i in range(len(clean_name_list)):
        text_mapper[clean_name_list[i]] = {
            "std_name": std_name_list[i],
            "check_type": check_type_list[i],
            "part_name": part_name_list[i],
        }
    return text_mapper


chk_item_std_names_mapper = load_chk_item_std_name_rels()
print("加载标准化名称映射表...")


def load_chk_ind_std_name_rels():
    """
    加载子项名称标准化映射表
    """
    df = pd.read_csv("./datas/子项名称标准化v1.0.0.csv")
    clean_name_list = df["清洗后名称"]
    std_name_list = df["标准化名称"]
    ind_type_list = df["结果类型"]
    text_mapper = {}
    for i in range(len(clean_name_list)):
        text_mapper[clean_name_list[i]] = {
            "std_name": std_name_list[i],
            "ind_type": ind_type_list[i],
        }
    return text_mapper


chk_ind_std_names_mapper = load_chk_ind_std_name_rels()
print("加载子项名称标准化映射表...")


def load_generalSummary_std_name_rels():
    """
    加载总检1标准化异常名称映射表
    """
    df = pd.read_csv("./datas/报告异常项标准化结果v1.0.3.csv")
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


def load_join_index_analyse_category_data():
    """
    子宫肌瘤总检1标准化异常名称列表
    """
    mapper = {}
    clean_name_str = "子宫多发实性占位肌瘤,子宫多发性肌瘤,子宫多发肌瘤,子宫实性占位肌瘤,子宫粘膜下肌瘤,子宫肌瘤,子宫肌瘤多发,子宫肌瘤并肌瘤变性,子宫肌瘤伴钙化子宫多发肌瘤部分伴钙化,子宫肌瘤可能,子宫肌瘤待排,子宫粘膜下肌瘤可能,子宫多发性肌瘤可能,子宫腺肌症合并腺肌瘤改变,子宫腺肌症合并腺肌瘤,子宫声像图符合子宫腺肌症合并腺肌瘤改变"
    clean_names = clean_name_str.split(",")
    for clean_name in clean_names:
        mapper[clean_name] = {
            "chk_name": "子宫超声",
            "std_name": "子宫肌瘤"
        }
    return mapper

# 报告异常项对应检查指标
abnormal_to_category_mapper = load_join_index_analyse_category_data()
print(abnormal_to_category_mapper)
print("加载联合指标分析指标分类异常项数据...")


def chk_name_clean(name):
    name = name.replace(" ", "").upper()
    name = name.replace("*", "")
    name = name.replace("【", "[").replace("】", "]")
    name = name.replace("（", "(").replace("）", ")")
    name = name.replace("[", "(").replace("]", ")")
    name = name.replace("—", "-").replace("－", "-").replace("--", "-")
    name = name.replace("_", "-")
    name = name.replace("★", "").replace("☆", "")
    name = name.replace("◆", "").replace("·", "").replace("●", "").replace("▲", "").replace("∈", "")
    name = name.replace('"', "")
    name = name.replace("Ⅰ", "I").replace("Ⅱ", "II")
    name = name.replace("：", ":")
    name = name.replace('"', "")
    name = name.replace("，", ",").replace("、", "|")
    if name.endswith(":") or name.endswith("#"):
        name = name[:-1]
    return name


# 子宫肌瘤检查项目
zgjl_chk_name_pattern = re.compile(r'子宫.*?(彩超|B超|阴超|超声)')
zgjl_chk_name_pattern_2 = re.compile(r'阴超')


def correlation_index_check_status_confirm(correlation_index, chk_name):
    """
    确认指标是否参检
    """
    if zgjl_chk_name_pattern.findall(chk_name):
        correlation_index["子宫超声"]['status'] = 1
    if zgjl_chk_name_pattern_2.findall(chk_name):
        correlation_index["子宫超声"]['status'] = 1


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
    checkItems, generalSummary = report["checkItems"], report["generalSummarys"]
    correlation_index_check_status = {
        "子宫超声": {
            "status": 0,
            "abnormals": [],
        }
    }
    for chk_item in checkItems:
        item_name = chk_item["checkItemName"]
        clean_item_name = chk_name_clean(item_name)
        # 检查指定指标项参检状态
        correlation_index_check_status_confirm(correlation_index_check_status, clean_item_name)
        chk_method = None
        if clean_item_name in chk_item_std_names_mapper:
            chk_method = chk_item_std_names_mapper[clean_item_name]["check_type"]
        children = chk_item["checkResults"]
        for child in children:
            ind_name = child["checkIndexName"]
            clean_ind_name = chk_name_clean(ind_name)
            if chk_method:
                clean_ind_name_ = clean_ind_name + chk_method
            else:
                clean_ind_name_ = clean_ind_name
            correlation_index_check_status_confirm(correlation_index_check_status, clean_ind_name_)

    abnormal_names = generalSummary_standardlize(generalSummary)
    std_abnormal_names = [generalSummary_std_names_mapper.get(name, None) for name in abnormal_names]
    unmatched_abnormals = []
    for index, abnormal in enumerate(std_abnormal_names):
        if not abnormal:
            unmatched_abnormals.append(abnormal_names[index])
        if abnormal and abnormal in abnormal_to_category_mapper:
            abnormal_dict = abnormal_to_category_mapper[abnormal]
            chk_name = abnormal_dict["chk_name"]
            std_name = abnormal_dict["std_name"]
            category_data = correlation_index_check_status[chk_name]
            category_data["status"] = 2
            if std_name not in category_data["abnormals"]:
                category_data["abnormals"].append(std_name)
    return correlation_index_check_status, unmatched_abnormals


def summarysAnalyse(report):
    correlation_index_check_status = summary_analyse(report)
    # print(correlation_index_check_status)
    return correlation_index_check_status


