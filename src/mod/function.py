import re
import os
from structures.Enum import TagIndictorResultValueEnum


def is_number(n: str):
    """
    是否为数字
    """
    # TODO 此处数值判断需要优化
    try:
        num = float(n)
        return True
    except Exception:
        return False


# 数字表达式匹配模式
numberic_string_pattern = re.compile(
    r"^(\d+\.?\d*?)([↓↑]?(\([\u4e00-\u9fa5].*?\))?|次/分|(mmol|umol|CELL|g)/u?L)?$"
)


def is_numberic_string(value: str):
    value = value.replace(' ', '')
    if len(value) < 10:
        ret = numberic_string_pattern.findall(value)
        if ret and is_number(ret[0][0]):
            return float(ret[0][0])
    return None


# 强阳判断模式
strong_positive_pattern = re.compile(r"^\+{3,}(/(HP|Hp|hp))?$")
# 弱阳判断模式
weak_positive_pattern = re.compile(r"^\+\-(/(HP|Hp|hp))?$")
# 阳性判断模式
positive_pattern = re.compile(r"^\+(/(HP|Hp|hp))?$")


def is_positive_or_negative(value: str):
    """
    是否为阴阳性
    """
    if value == "-" or "阴性" in value:
        return TagIndictorResultValueEnum.negative
    if "强阳性" in value or strong_positive_pattern.findall(value):
        return TagIndictorResultValueEnum.strong_positive
    if "弱阳性" in value or weak_positive_pattern.findall(value):
        return TagIndictorResultValueEnum.weak_positive
    if "阳性" in value or positive_pattern.findall(value):
        return TagIndictorResultValueEnum.positive
    return None


# 清洗范围，将单限制改为上下限
def get_textref_up_low(text_ref):
    raw_text_ref = text_ref
    text_ref = text_ref.replace("-<=", "0.00-")
    text_ref = text_ref.replace("-＜=", "0.00-")

    text_ref = text_ref.replace("-<", "0.00-")
    text_ref = text_ref.replace("-＜", "0.00-")

    text_ref = text_ref.replace("<=", "0.00-")
    text_ref = text_ref.replace("＜=", "0.00-")

    text_ref = text_ref.replace("<", "0.00-")
    text_ref = text_ref.replace("＜", "0.00-")
    text_ref = text_ref.replace("〈", "0.00-")
    text_ref = text_ref.replace("-≤", "0.00-")
    text_ref = text_ref.replace("〈", "0.00-")

    if "〉" in text_ref:
        text_ref = text_ref.replace("〉", "")
        text_ref = text_ref + "-Inf"
    if ">" in text_ref:
        text_ref = text_ref.replace(">", "")
        text_ref = text_ref + "-Inf"
    if "﹥" in text_ref:
        text_ref = text_ref.replace("﹥", "")
        text_ref = text_ref + "-Inf"
    if "＞" in text_ref:
        text_ref = text_ref.replace("＞", "")
        text_ref = text_ref + "-Inf"

    if "--" in text_ref:
        text_ref = text_ref.replace("--", "-")

    if "-" in text_ref:
        text_ref_lower = text_ref.split("-")[0]
        text_ref_upper = text_ref.split("-")[1]
        if is_number(text_ref_lower) and is_number(text_ref_upper):
            text_ref_lower = float(text_ref_lower)
            text_ref_upper = float(text_ref_upper)
            if text_ref_lower >= text_ref_upper:
                exchange = text_ref_lower
                text_ref_lower = text_ref_upper
                text_ref_upper = exchange
            return text_ref_lower, text_ref_upper
        else:
            text_ref = raw_text_ref + "(数据错误)"
    else:
        text_ref = raw_text_ref + "(数据错误)"
    return text_ref, text_ref


""" 以下为暂无用处方法
def re_match(key_word, raw_string):
    aaa = re.match(key_word, raw_string, flags=0)
    if aaa:
        flag = 1
    else:
        flag = 0
    return flag


# 清洗指标值，去除非数值非小数点部分
non_decimal = re.compile(r"[^\d.]+")


def result_value_replace(result_value):
    result_value = non_decimal.sub("", result_value)
    if result_value.endswith("."):
        result_value = result_value[:-1]
    try:
        result_value = format(float(result_value), ".2f")
    except Exception as e:
        return result_value
    return result_value


# 指标项名称特殊符号处理
def index_name_replace(index_name):
    index_name = index_name.replace(" ", "").upper()
    index_name = index_name.replace("*", "")
    index_name = index_name.replace("【", "[").replace("】", "]")
    index_name = index_name.replace("（", "(").replace("）", ")")
    index_name = index_name.replace("[", "(").replace("]", ")")
    index_name = index_name.replace("—", "-").replace("－", "-").replace("--", "-")
    index_name = index_name.replace("_", "-")
    index_name = index_name.replace("★", "")
    index_name = index_name.replace("Ⅰ", "I")
    index_name = index_name.replace("Ⅱ", "II")
    if index_name.startswith("-"):
        index_name = index_name[1:]
    if index_name.endswith("."):
        index_name = index_name[:-1]
    return index_name


# 清洗范围，将单限制改为上下限
def text_ref_replace(text_ref):
    raw_text_ref = text_ref
    # print(raw_text_ref)
    text_ref = text_ref.replace("-<=", "0.00-")
    text_ref = text_ref.replace("-＜=", "0.00-")

    text_ref = text_ref.replace("-<", "0.00-")
    text_ref = text_ref.replace("-＜", "0.00-")

    text_ref = text_ref.replace("<=", "0.00-")
    text_ref = text_ref.replace("＜=", "0.00-")

    text_ref = text_ref.replace("<", "0.00-")
    text_ref = text_ref.replace("＜", "0.00-")
    text_ref = text_ref.replace("〈", "0.00-")
    text_ref = text_ref.replace("-≤", "0.00-")
    text_ref = text_ref.replace("〈", "0.00-")

    if "〉" in text_ref:
        text_ref = text_ref.replace("〉", "")
        text_ref = text_ref + "-Inf"
    if ">" in text_ref:
        text_ref = text_ref.replace(">", "")
        text_ref = text_ref + "-Inf"
    if "﹥" in text_ref:
        text_ref = text_ref.replace("﹥", "")
        text_ref = text_ref + "-Inf"
    if "＞" in text_ref:
        text_ref = text_ref.replace("＞", "")
        text_ref = text_ref + "-Inf"

    if "--" in text_ref:
        text_ref = text_ref.replace("--", "-")

    if "-" in text_ref:
        # print(text_ref)
        text_ref_lower = text_ref.split("-")[0]
        text_ref_upper = text_ref.split("-")[1]
        if is_number(text_ref_lower) and is_number(text_ref_upper):
            text_ref_lower = str(float(text_ref_lower))
            text_ref_upper = str(float(text_ref_upper))
            text_ref = text_ref_lower + "-" + text_ref_upper
        else:
            text_ref = raw_text_ref + "(数据错误)"
    else:
        text_ref = raw_text_ref + "(数据错误)"
    return text_ref
"""
