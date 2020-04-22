import pandas as pd


def getItemStatus(stdIndicators):
    sheet = pd.read_excel("./datas/深度报告覆盖逻辑-20200327.xlsx", sheet_name=0)
    item_list = list(sheet.columns)
    ind_to_item_dict = {}
    item_to_status_dict = {}
    for item_ in item_list:
        item_to_status_dict[item_] = 0
        for key_ in sheet[item_]:
            ind_to_item_dict[key_] = item_

    for stdind in stdIndicators:
        if stdind.name in ind_to_item_dict:
            item_to_status_dict[ind_to_item_dict[stdind.name]] = 1

    return item_to_status_dict


def reportCover(item_to_status_dict, user_dict):
    check_counts = 0
    access_2_item = 'no'
    access_3_item = 'no'
    access_4_item = 'no'
    access_5_item = 'no'
    access_6_item = 'no'
    access_7_item = 'no'
    for item_ in item_to_status_dict:
        if item_to_status_dict[item_] == 1:
            check_counts += 1
    if 18 <= user_dict["age"] < 65:
        if check_counts >= 2:
            access_2_item = 'yes'
        if check_counts >= 3:
            access_3_item = 'yes'
        if check_counts >= 4:
            access_4_item = 'yes'
        if check_counts >= 5:
            access_5_item = 'yes'
        if check_counts >= 6:
            access_6_item = 'yes'
        if check_counts >= 7:
            access_7_item = 'yes'
    total_dict = {**item_to_status_dict, **{
        "access_2_item": access_2_item,
        "access_3_item": access_3_item,
        "access_4_item": access_4_item,
        "access_5_item": access_5_item,
        "access_6_item": access_6_item,
        "access_7_item": access_7_item,
        "age": user_dict["age"],
    }}
    return total_dict
