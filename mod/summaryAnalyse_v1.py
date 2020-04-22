import pandas as pd
import re
from mod.declaration_summary_analyse import summary_analyse

# import pymongo
# import collections
# mongo_client = pymongo.MongoClient("mongodb://{}:{}@{}:{}".format('root', 'example', "192.168.1.152", 27017))
# mongo_db = mongo_client.report_chk_item_standlize
# collections = mongo_db.a20200304


def load_chk_item_std_name_rels():
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


    # with open("../datas/描述型指标名称标准化结果v1.0.6.csv") as f:
    #     reader = csv.reader(f.readlines())
    #     next(reader)
    #     text_mapper = {}
    #     for line in reader:
    #         clean_name, std_name, level_1, level_2, part_name, check_type, attrs, gender = line
    #         text_mapper[clean_name] = {
    #             "std_name": std_name,
    #             "check_type": check_type,
    #             "part_name": part_name
    #         }
    # return text_mapper

chk_item_std_names_mapper = load_chk_item_std_name_rels()


def load_chk_ind_std_name_rels():
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


    # with open("../datas/子项名称标准化v1.0.0.csv") as f:
    #     reader = csv.reader(f.readlines())
    #     next(reader)
    #     text_mapper = {}
    #     for line in reader:
    #         clean_name, item_names, std_name, ind_type, *_ = line
    #         text_mapper[clean_name] = {
    #             "std_name": std_name,
    #             "ind_type": ind_type,
    #         }
    # return text_mapper

chk_ind_std_names_mapper = load_chk_ind_std_name_rels()


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


# 1. 各种组合
# 1.1 脂肪肝可检出指标
zfg_chk_item_name_pattern = re.compile(r'(数字化肝超|肝.*(超声|彩超|B超|E超|MRI|CT))')
# 1.2 心电图
# 1.3 心脏听诊
xztz_chk_item_name_pattern = re.compile(r'心.*听诊')
# 2. 大组合
# 2.1 颈动脉超声
jdmcs_chk_item_pattern = re.compile(r'颈动脉.*(超声|彩超|B超|E超)')
# 2.2 眼底检查
# 2.3 肾超声
scs_chk_item_pattern = re.compile(r'肾.*(超声|彩超|B超|E超)')
# 2.4 心脏超声
xzcs_chk_item_pattern = re.compile(r'肾.*(超声|彩超|B超|E超)')
# 2.5 肝B超-肝硬化/肝纤维化
gbc_chk_item_pattern = re.compile(r'肝.*(超声|彩超|B超|E超|纤维)')


def correlation_index_check_status_confirm(correlation_index, chk_name, confirm_type):
    """
    确认指标是否参检或是否异常
    confirm_type = 1 确认指标是否参检
    confirm_type = 2 确认指标是否异常
    """
    if zfg_chk_item_name_pattern.findall(chk_name):
        correlation_index["脂肪肝"] = 1 if confirm_type == 1 else 2
    if "心电图" in chk_name:
        correlation_index["心电图"] = 1 if confirm_type == 1 else 2
    if xztz_chk_item_name_pattern.findall(chk_name):
        correlation_index["心脏听诊"] = 1 if confirm_type == 1 else 2
    if jdmcs_chk_item_pattern.findall(chk_name):
        correlation_index["颈动脉超声"] = 1 if confirm_type == 1 else 2
    if "眼底" in chk_name:
        correlation_index["眼底检查"] = 1 if confirm_type == 1 else 2
    if scs_chk_item_pattern.findall(chk_name):
        correlation_index["肾超声"] = 1 if confirm_type == 1 else 2
    if xzcs_chk_item_pattern.findall(chk_name):
        correlation_index["心脏超声"] = 1 if confirm_type == 1 else 2
    if gbc_chk_item_pattern.findall(chk_name):
        correlation_index["肝B超"] = 1 if confirm_type == 1 else 2


# 1. 判断名称是否可以被标准化，分 chk_item_name 和 chk_ind_name
# 2. 记录标准化名称
# 3. 记录关联指标分析-组合逻辑中的描述型指标是否参检
def chk_item_and_ind_standlize(checkItems):
    correlation_index_check_status = {
        "脂肪肝": 0,
        "心电图": 0,
        "心脏听诊": 0,
        "颈动脉超声": 0,
        "眼底检查": 0,
        "肾超声": 0,
        "心脏超声": 0,
        "肝B超": 0
    }
    objs = []
    for chk_item in checkItems:
        obj = {}
        item_name = chk_item["checkItemName"]
        clean_item_name = chk_name_clean(item_name)
        # 检查指定指标项参检状态
        correlation_index_check_status_confirm(correlation_index_check_status, clean_item_name, 1)
        chk_method = None
        if clean_item_name in chk_item_std_names_mapper:
            chk_method = chk_item_std_names_mapper[clean_item_name]["check_type"]
            obj.update({
                "checkItemName": item_name,
                "clean_name": clean_item_name,
                "std_name": chk_item_std_names_mapper[clean_item_name]["std_name"],
                "standlized": True
            })

        else:
            obj.update({
                "checkItemName": item_name,
                "clean_name": clean_item_name,
                "std_name": None,
                "standlized": False
            })
        obj.update({
            "chk_method": chk_method
        })
        children = chk_item["checkResults"]
        std_children = []
        for child in children:
            std_child = {}
            ind_name = child["checkIndexName"]
            clean_ind_name = chk_name_clean(ind_name)
            if chk_method:
                clean_ind_name_ = clean_ind_name + chk_method
            else:
                clean_ind_name_ = clean_ind_name
            correlation_index_check_status_confirm(correlation_index_check_status, clean_ind_name_, 1)
            if clean_ind_name in chk_ind_std_names_mapper:
                std_child.update({
                    "checkIndexName": ind_name,
                    "clean_name": clean_ind_name,
                    "std_name": chk_ind_std_names_mapper[clean_ind_name]["std_name"],
                    "standlized": True
                })
            else:
                std_child.update({
                    "checkIndexName": ind_name,
                    "clean_name": clean_ind_name,
                    "std_name": None,
                    "standlized": False
                })
            std_children.append(std_child)
        obj["children"] = std_children
        objs.append(obj)
    return correlation_index_check_status, objs


def summarysAnalyse(summarys2, user, one_report):
    abnormal_chk_info = summary_analyse(summarys2, user)
    correlation_index_check_status, chk_items = chk_item_and_ind_standlize(one_report["checkItems"])
    for item in abnormal_chk_info:
        chk_name = item[1] + item[0]
        correlation_index_check_status_confirm(correlation_index_check_status, chk_name, 2)

    # data = {
    #     "rpt_id": user.report_id,
    #     "chk_item_info": chk_items,
    #     "correlation_index_check_status": correlation_index_check_status
    # }
    # collections.insert_one(data)
    return correlation_index_check_status


