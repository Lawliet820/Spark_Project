import pandas as pd

level_map_df = pd.read_excel("./datas/909标准名称表v0.3.xlsx")
index_name_list = level_map_df["U健康标准名称"]
levelOne_list = level_map_df["大项"]
level_map_dict = {}
for i in range(len(index_name_list)):
    level_map_dict[index_name_list[i]] = levelOne_list[i]


def getLevelOne(indicators, user):
    # 大项目结果初始化
    levelOne_result = {
        "report_id": user.report_id,
        "gender": user.gender.value,
        "age": user.age,
    }
    for levelOne in levelOne_list:
        levelOne_result[levelOne] = 0

    for ind in indicators:
        name = ind.name
        flag = ind.resultFlagId
        if name in level_map_dict:
            if flag > 1:
                levelOne_result[level_map_dict[name]] = 2
            else:
                if levelOne_result[level_map_dict[name]] == 2:
                    continue
                else:
                    levelOne_result[level_map_dict[name]] = 1
        else:
            pass
    return levelOne_result

