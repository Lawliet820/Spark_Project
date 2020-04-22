"""
总检2内容分析
"""
import re
from struc.Enum import GenderEnum
from db.Postgres import Disease as DiseaseDB, ItemNameMap, Session


def get_summary_keywords_table():
    """
    对总检关键字表按照检查类别/方法进行分组
    """
    session = Session()
    diseases = (
        session.query(DiseaseDB)
        .filter(DiseaseDB.tag == 'summary')
        .filter(DiseaseDB.is_disease == 1)
        .all()
    )
    category_results = {}
    for disease in diseases:
        item_name = disease.item_name
        if item_name not in category_results:
            category_results[item_name] = []
        category_results[item_name].append(disease)
    return category_results


# 总检关键词表
keywords_mapping = get_summary_keywords_table()
# print("导入 总检关键词表 ...")


def get_check_dirty_name_rels():
    """
    获取检查项别名表
    """
    session = Session()
    data = session.query(ItemNameMap).filter(ItemNameMap.dirty_name_source == "总检关键词").all()
    results = {}
    for obj in data:
        results[obj.dirty_name] = obj.name
    return results


# 检查项别名表
check_dirty_names_mapping = get_check_dirty_name_rels()
# print("导入 检查项别名表 ...")


# 检查项名称提取分割符号
chk_item_name_split_symbol = "★"
# 检查项名称提取分割符号
chk_item_name_extract_pattern = re.compile(r"[,，:：\n]")
# 分句提取分隔符
clause_extract_pattern = re.compile(r"[,。；]")
# 未见异常/病变
no_abnormal_seen_pattern = re.compile(r"^余?.*?(未见(异常|病变)|未发现(明显)?异常)$")


def matched_results_distinguish(matched_list):
    """
    匹配结果根据 disease_name 去重
    1. 按照疾病名称去重
    2. 采用疾病名称最长匹配原则
    """
    unique_disease_names = []
    unique_diseases = []
    unique_disease_clauses = []
    for clause, disease in matched_list:
        name = disease.name
        if name not in unique_disease_names:
            unique_disease_names.append(name)
            unique_diseases.append(disease)
            unique_disease_clauses.append(clause) 

    if len(unique_diseases) <= 1:
        return list(zip(unique_disease_clauses, unique_diseases))

    # 当结果不唯一时，继续按照疾病名称最长匹配原则获取最佳匹配项
    choices = [len(disease.name) for disease in unique_diseases]
    target_disease_index = choices.index(max(choices))
    target_disease = unique_diseases[target_disease_index]
    target_disease_clause = unique_disease_clauses[target_disease_index]
    target_disease_name = target_disease.name

    unique_name_diseases = [(target_disease_clause, target_disease)]
    for index, disease in enumerate(unique_diseases):
        name = disease.name
        if list(set(name) - set(target_disease_name)):
            unique_name_diseases.append((unique_disease_clauses[index], disease))
    return unique_name_diseases


def is_match(key_word, result_word, clause):
    if result_word and key_word:
        if key_word in clause and result_word in clause:
            return True
    else:
        if key_word:
            if key_word in clause:
                return True
        if result_word:
            if result_word in clause:
                return True
    return False


def get_no_colon_indictor_matched_diseases(line):
    """
    获取不带冒号的总检项匹配结果
    1. 找出分句包含的检查项名称，获取到对应的疾病列表
    2. 从疾病列表中检索关键字，获取匹配疾病
    """

    matched_results = []
    clauses = line.split("\n")
    for clause in clauses:
        for key, diseases in keywords_mapping.items():
            if key in clause:
                for disease in diseases:
                    if is_match(disease.key_word, disease.result_word, clause):
                        matched_results.append([clause, disease])

    if len(matched_results) > 1:
        matched_results = matched_results_distinguish(matched_results)
    return matched_results


def get_declarative_indictor_matched_diseases(clause, list_to_be_matched):
    """
    根据关键字和结果值匹配参检项目及疾病名称
    """
    diseases = []
    # 直接按照疾病名称匹配
    for disease in list_to_be_matched:
        if clause == disease.name:
            diseases.append([clause, disease])
            break
    
    # 按照关键字+结果匹配
    if not diseases:
        for disease in list_to_be_matched:
            if is_match(disease.key_word, disease.result_word, clause):
                diseases.append([clause, disease])
    if len(diseases) > 1:
        diseases = matched_results_distinguish(diseases)
    return diseases


# 建议型文本匹配模式
suggestion_match_pattern = re.compile(r"^(报告可至|您|如|请|是|常由|.*?是.*?)")


def get_clauses_matched_diseases(check_item_name, clauses, list_to_be_matched):
    """
    根据关键字和结果值匹配参检项目及疾病名称
    """
    # 无异常或弃检
    no_abnormal_seens = []
    # 未匹配到关键词
    not_matched_key_words = []
    # 建议型文本
    suggestion_clauses = []
    # 匹配疾病
    matched_diseases = []

    for index, clause in enumerate(clauses):
        clause = re.sub(r"^\d(.|、)", "", clause)
        if clause:
            if suggestion_match_pattern.findall(clause):
                suggestion_clauses.append("{}|{}".format(check_item_name, ",".join(clauses[index:])))
                break

            is_continue = True
            for key in ["视力", "弃检", "弃查", "延期", "病史"]:
                if key in clause:
                    is_continue = False
                    no_abnormal_seens.append(clause)
                    break
            if not is_continue:
                break

            results = get_declarative_indictor_matched_diseases(clause, list_to_be_matched)
            if results:
                matched_diseases.extend(results)
            else:
                not_matched_key_words.append("{}|{}｜{}".format(check_item_name, clause, ",".join(clauses[index:])))
    return (
        matched_diseases,
        no_abnormal_seens,
        not_matched_key_words,
        suggestion_clauses,
    )


def extract_part_measure_and_abnormal(diseases):
    """
    提取疾病对应检查方式及部位和异常
    """
    results = []
    for clause, disease in diseases:
        results.append([disease.item_name, disease.part, disease.key_word, disease.result_word, disease.name, clause])
    return results
    

def summary_analyse(summarys, user):
    """
    报告总检内容处理，提取影像、电生理指标异常分析
    """
    if not summarys:
        return []

    gender = user.gender
    age = user.age
    if not age:
        crowd = "0-150"
    elif age < 18:
        crowd = "0-18"
    elif 20 <= age <= 40:
        crowd = "20-40"
    else:
        crowd = "0-150"

    # 未见异常或弃检等
    no_abnormal_seens = []
    # 未匹配检查项
    no_selected_chk_names = []
    # 未找到匹配关键字
    not_matched_key_words = []
    # 建议型文本
    suggestion_clauses = []
    # 不包含：的句子
    single_clauses = []
    # 匹配结果
    matched_results = []
    for line in summarys:
        line = (
            line.replace("★", "")
            .strip()
            .replace(" ", "")
            .replace("【", "")
            .replace(" 】", "")
            .replace("，", ",")
            .replace("；", ";")
            .replace("：", ":")
        )
        if ":" in line:
            items = line.split(":")
            # 提取检查项名称
            chk_item_origin_name, clauses_string = items[0], ":".join(items[1:])

            # 无用文本
            if "分析报告" in chk_item_origin_name:
                suggestion_clauses.append(line)

            # 检查项别名替换
            if chk_item_origin_name in check_dirty_names_mapping:
                chk_item_name = check_dirty_names_mapping[chk_item_origin_name]
            else:
                chk_item_name = chk_item_origin_name

            # 备选检测类别/方法名称列表
            matched_mpping_key_names = [
                (len(key), key) for key in keywords_mapping if key in chk_item_name
            ]
            if matched_mpping_key_names:
                # 检测类别/方法名称最长项
                target_chk_item_name = max(matched_mpping_key_names)[1]
                # 待匹配关键词及结果形容词
                list_to_be_matched = [
                    obj
                    for obj in keywords_mapping[target_chk_item_name]
                    if obj.gender in [GenderEnum.whole, gender]
                    and obj.crowd in ["0-150", crowd]
                ]
                # 执行分句
                clauses = clauses_string.split("\n")
                matched_result = []
                for clause in clauses:
                    if clause:
                        # 按照规则断句，1. 仅取前50个字，2.抛弃“建议”和“提示”后面的内容
                        if len(clause) > 50:
                            clause = clause[:50]
                        if "建议" in clause:
                            clause = clause.split("建议")[0]
                        if "提示" in clause:
                            clause = clause.split("提示")[0]

                        # 未见异常/病变
                        if no_abnormal_seen_pattern.findall(clause):
                            no_abnormal_seens.append(clause)
                            continue

                        # 分句中包含：，为提升匹配度，补全部位名称
                        if ":" in clause and "," in clause:
                            part_name = clause.split(":")[0]
                            items = clause.split(",")
                            for index, item in enumerate(items[1:]):
                                items[1 + index] = part_name + ":" + item
                        else:
                            items = clause_extract_pattern.split(clause)
                        diseases, no_abnormal_seen, not_matched_key_word, suggestion_clause = get_clauses_matched_diseases(
                            chk_item_name, items, list_to_be_matched
                        )
                        no_abnormal_seens.extend(no_abnormal_seen)
                        not_matched_key_words.extend(not_matched_key_word)
                        suggestion_clauses.extend(suggestion_clause)
                        matched_result.extend(diseases)
                if matched_result:
                    matched_results.extend(matched_result)
            else:
                no_selected_chk_names.append(line)
        else:
            if no_abnormal_seen_pattern.findall(line):
                no_abnormal_seens.append(line)
                continue
            
            # 采用无冒号分句匹配模式
            results = get_no_colon_indictor_matched_diseases(line)
            if results:
                matched_results.extend(results)
            else:
                single_clauses.append(line)

    return extract_part_measure_and_abnormal(matched_results)
