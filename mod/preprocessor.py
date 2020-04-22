from struc.Report import (
    Indicator,
    User,
)
from struc.Enum import GenderEnum


def pre_process(report_data: dict):
    """
    报告预处理
    """
    brithday = report_data["brithday"]
    gender = report_data["gender"]
    report_id = report_data["report_id"]

    # 性别
    if "男" in gender:
        gender = GenderEnum.male
    elif "女" in gender:
        gender = GenderEnum.female
    else:
        gender = None

    # 年龄
    if brithday:
        age = 2019 - int(brithday[:4])
    else:
        age = 0

    user = User(**{
            "report_id": report_id,
            "gender": gender,
            "age": age,
        })

    indicators = []
    for item in report_data["checkItems"]:
        chk_item_name = item["checkItemName"]
        if "checkResults" not in item:
            continue
        for child in item["checkResults"]:
            index_name = child["checkIndexName"]
            if index_name in ["总检"]:
                continue
            child["checkItemName"] = chk_item_name
            indicators.append(Indicator(**{
                "name": "",
                "checkIndexName": child["checkIndexName"],
                "checkItemName": child["checkItemName"],
                "resultValue": child["resultValue"],
                "resultFlagId": child["resultFlagId"],
                "textRef": child["textRef"],
                "unit": child["unit"],
            }))

    summarys2 = report_data["generalSummarys2"]

    return indicators, summarys2, user
