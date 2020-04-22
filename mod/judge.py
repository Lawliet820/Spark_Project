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

def judgeMetabolism(stdIndicators):
    tc_flag = 0  # 总胆固醇flag
    tg_flag = 0  # 甘油三酯flag
    hdlc_flag = 0  # 高密度脂蛋白flag
    ldlc_flag = 0  # 低密度脂蛋白flag
    glu_flag = 0  # 空腹血糖flag
    dbp_flag = 0  # 舒张压flag
    dbp_val = 0
    sbp_flag = 0  # 收缩压flag
    sbp_val = 0
    ua_flag = 0  # 尿酸flag
    gly_hem_flag = 0  # 糖化血红蛋白flag
    gly_alb_flag = 0  # 糖化白蛋白flag

    metabolism_status = {
        "血糖状态": 0,
        "血压状态": 0,
        "血脂状态": 0,
        "尿酸状态": 0,
    }

    # 读取代谢指标相关值
    for ind in stdIndicators:
        if ind.name == "总胆固醇":
            tc_flag = ind.resultFlagId
            metabolism_status["血脂状态"] = 1

        if ind.name == "甘油三酯":
            tg_flag = ind.resultFlagId
            metabolism_status["血脂状态"] = 1

        if ind.name == "高密度脂蛋白胆固醇":
            hdlc_flag = ind.resultFlagId
            metabolism_status["血脂状态"] = 1

        if ind.name == "低密度脂蛋白胆固醇":
            ldlc_flag = ind.resultFlagId
            metabolism_status["血脂状态"] = 1

        if ind.name == "空腹血糖":
            glu_flag = ind.resultFlagId
            metabolism_status["血糖状态"] = 1

        if ind.name == "糖化血红蛋白":
            gly_hem_flag = ind.resultFlagId
            metabolism_status["血糖状态"] = 1

        if ind.name == "糖化白蛋白":
            gly_alb_flag = ind.resultFlagId
            metabolism_status["血糖状态"] = 1

        if ind.name == "舒张压":
            # dbp_flag = ind.resultFlagId
            dbp_val = is_numberic_string(ind.resultValue)
            metabolism_status["血压状态"] = 1

        if ind.name == "收缩压":
            # sbp_flag = ind.resultFlagId
            sbp_val = is_numberic_string(ind.resultValue)
            metabolism_status["血压状态"] = 1

        if ind.name == "尿酸":
            ua_flag = ind.resultFlagId
            metabolism_status["尿酸状态"] = 1



    # 高血糖判断
    if glu_flag == 3 or gly_hem_flag == 3 or gly_alb_flag == 3:
        metabolism_status["血糖状态"] = 3

    # 高血脂判断
    if tc_flag == 3 or tg_flag == 3 or hdlc_flag == 2 or ldlc_flag == 3:
        metabolism_status["血脂状态"] = 3

    # 高血压判断
    if (sbp_val and sbp_val >= 140) or (dbp_val and dbp_val >= 90):
        metabolism_status["血压状态"] = 3

    # 高尿酸判断
    if ua_flag == 3:
        metabolism_status["尿酸状态"] = 3

    return metabolism_status
