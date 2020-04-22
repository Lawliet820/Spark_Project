import re


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


def judge_access(stdIndicators, user_dict):

    # 初始化代谢指标相关值
    kg_value = 0  # 体重
    cm_value = 0  # 身高
    tc_value = 0  # 总胆固醇
    tg_value = 0  # 甘油三酯
    hdlc_value = 0  # 高密度脂蛋白
    glu_value = 0  # 空腹血糖
    dbp_value = 0  # 舒张压
    sbp_value = 0  # 收缩压
    gender_value = user_dict["gender"]
    age_value = user_dict["age"]
    # 读取代谢指标相关值
    for ind in stdIndicators:
        val = is_numberic_string(ind.resultValue)
        if ind.name == "体重" and val:
            kg_value = val
        if ind.name == "身高" and val:
            cm_value = val
        if ind.name == "总胆固醇" and val:
            tc_value = val
        if ind.name == "甘油三酯" and val:
            tg_value = val
        if ind.name == "高密度脂蛋白胆固醇" and val:
            hdlc_value = val
        if ind.name == "空腹血糖" and val:
            glu_value = val
        if ind.name == "舒张压" and val:
            dbp_value = val
        if ind.name == "收缩压" and val:
            sbp_value = val

    # 深度报告准入判断
    if (
            kg_value
            and cm_value
            and tc_value
            and tg_value
            and hdlc_value
            and glu_value
            and dbp_value
            and sbp_value
            and gender_value
            and age_value
            and 18 <= age_value < 65
    ):
        access = "准入"
    else:
        access = "不准入"

    # 函数返回
    return_dict = {
        "gender_value": gender_value,
        "age_value": age_value,
        "kg_value": kg_value,
        "cm_value": cm_value,
        "tc_value": tc_value,
        "tg_value": tg_value,
        "hdlc_value": hdlc_value,
        "glu_value": glu_value,
        "dbp_value": dbp_value,
        "sbp_value": sbp_value,
        "access": access,
    }
    return return_dict
