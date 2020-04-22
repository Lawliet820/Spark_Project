import json
import csv
import re
import os
import pandas as pd


def re_match(key_word, raw_string):
    try:
        aaa = re.match(key_word, raw_string, flags=0)
        if str(aaa) == 'None':
            flag = 0
        else:
            flag = 1
        return flag
    except Exception:
        return 0


# 石澳代码v0.4
# 判断范围是否符合要求 ,3个参数，范围,范围开头的范围，范围末尾的范围
def result_textRef_fw(result_value, fw1, fw2):
    try:
        non_decimal = re.compile(r'[^\d.]+')
        result_value = non_decimal.sub('_', result_value)

        if (float(result_value.split('_')[0]) >= float(fw1.split('-')[0]) and float(
                result_value.split('_')[0]) <= float(fw1.split('-')[1])) and \
                (float(result_value.split('_')[1]) >= float(fw2.split('-')[0]) and float(
                    result_value.split('_')[1]) <= float(fw2.split('-')[1])):
            return 1
        else:
            return 0
    except Exception as e:
        return 0


def result_value_replace_fw(result_value, fw):
    try:
        non_decimal = re.compile(r'[^\d.]+')
        result_value = non_decimal.sub('_', result_value)

        if (float(result_value.split('_')[0]) > float(fw.split('-')[0]) and float(result_value.split('_')[0]) < float(
                fw.split('-')[1])) and (float(result_value.split('_')[1]) > float(fw.split('-')[0]) and float(
                result_value.split('_')[1]) < float(fw.split('-')[1])):
            return 1
        else:
            return 0
    except Exception as e:
        return 0


def result_value_replace(result_value):
    # 数字匹配不上返回-1
    try:
        non_decimal = re.compile(r'[^\d.]+')
        result_value = non_decimal.sub('', result_value)
        return float(result_value)
    except Exception:
        return -1


def is_number(n):
    is_number = True
    try:
        num = float(n)
        is_number = (num == num)
    except ValueError:
        is_number = False
    return is_number


def CEA_disambiguation(data):
    # 定性
    blood_index_key = ".*?(阴|阳).*"

    # 定量
    urine_index_key = ".*?(mmol/L).*"

    data['disambiguation'] = 'other'

    if re_match(blood_index_key, data['resultValue']) == 1:
        data['disambiguation'] = 'cea_qualit'

    if re_match(blood_index_key, data['textRef']) == 0 \
            and re_match(blood_index_key, data['resultValue']) == 0:
        data['disambiguation'] = 'cea_ration'
    return data

def herpes_disambiguation(data):
    # I型IgG
    blood_index_key = ".*?((I|Ⅰ)型).*?"
    blood_index_key2 = ".*?(IgG).*?"

    # I型IgM
    blood1_index_key = ".*?((I|Ⅰ)型).*?"
    blood1_index_key2 = ".*?(IgM).*?"

    # II型IgG
    urine1_index_key = ".*?((II|ⅠⅠ)型).*?"
    urine1_index_key2 = ".*?(IgG).*?"

    # II型IgM
    urine2_index_key = ".*?((II|ⅠⅠ)型).*?"
    urine2_index_key2 = ".*?(IgM).*?"

    data['disambiguation'] = 'other'

    if re_match(blood_index_key2, data['checkIndexName']) == 1 and \
            re_match(blood_index_key, data['checkItemName']) == 1 and \
            re_match(urine1_index_key, data['checkItemName']) == 0:
        data['disambiguation'] = 'I_IgG'

    if re_match(blood1_index_key2, data['checkIndexName']) == 1 and \
            re_match(blood1_index_key, data['checkItemName']) == 1 and \
            re_match(urine1_index_key, data['checkItemName']) == 0:
        data['disambiguation'] = 'I_IgM'

    if re_match(urine1_index_key2, data['checkIndexName']) == 1 and \
            re_match(urine1_index_key, data['checkItemName']) == 1:
        data['disambiguation'] = 'II_IgG'

    if re_match(urine2_index_key2, data['checkIndexName']) == 1 and \
            re_match(urine2_index_key, data['checkItemName']) == 1:
        data['disambiguation'] = 'II_IgM'
    return data

def starch_disambiguation(data):
    # I型IgG
    blood_index_key = ".*?(血).*?"
    #     blood_index_key2 = ".*?(IgG).*?"

    # I型IgM
    blood1_index_key = ".*?(胰).*?"
    #     blood1_index_key2 = ".*?(IgM).*?"

    data['disambiguation'] = 'other'

    if re_match(blood_index_key, data['checkItemName']) == 1:
        data['disambiguation'] = 'blood_strach'

    if re_match(blood1_index_key, data['checkItemName']) == 1:
        data['disambiguation'] = 'pancreas_strach'
    return data

# 分析数据后只能区分丁肝
def HDV_disambiguation(data):
    # 丁型肝炎IgM
    blood_index_key = ".*?(gM).*?"

    data['disambiguation'] = 'other'

    if re_match(blood_index_key, data['checkItemName']) == 1:
        data['disambiguation'] = 'HDV_IgM'
    return data

def Tox_disambiguation(data):
    # 弓形虫IgM
    blood_index_key = ".*?(gM).*?"
    blood_index_key2 = ".*?(IgG).*?"

    # 弓形虫IgG
    blood1_index_key = ".*?(gG).*?"
    blood1_index_key2 = ".*?(gM).*?"

    data['disambiguation'] = 'other'

    if re_match(blood_index_key, data['checkItemName']) == 1 and \
            re_match(blood_index_key2, data['checkItemName']) == 0:
        data['disambiguation'] = 'Tox_IgM'

    if re_match(blood1_index_key, data['checkItemName']) == 1 and \
            re_match(blood1_index_key2, data['checkItemName']) == 0:
        data['disambiguation'] = 'Tox_IgG'
    return data

def HAV_disambiguation(data):
    # 甲肝IgM
    blood_index_key = ".*?(gM|GM|gm).*?"
    blood_index_key2 = ".*?(IgG|GG|gg).*?"

    # 甲肝IgG
    blood1_index_key = ".*?(gG|gg|GG).*?"
    blood1_index_key2 = ".*?(gM|GM|gm).*?"

    data['disambiguation'] = 'other'

    if re_match(blood_index_key, data['checkItemName']) == 1 and \
            re_match(blood_index_key2, data['checkItemName']) == 0:
        data['disambiguation'] = 'HAV_IgM'

    if re_match(blood1_index_key, data['checkItemName']) == 1 and \
            re_match(blood1_index_key2, data['checkItemName']) == 0:
        data['disambiguation'] = 'HAV_IgG'
    return data

def K_disambiguation(data):
    # 血清钾
    blood_index_key = ".*?(血清).*?"
    blood_index_key2 = ".*?(全血).*?"

    # 全血钾
    blood1_index_key = ".*?(全血).*?"
    blood1_index_key2 = ".*?(血清).*?"

    data['disambiguation'] = 'other'

    if re_match(blood_index_key, data['checkItemName']) == 1 and \
            re_match(blood_index_key2, data['checkItemName']) == 0:
        data['disambiguation'] = 'K_serum'

    if re_match(blood1_index_key, data['checkItemName']) == 1 and \
            re_match(blood1_index_key2, data['checkItemName']) == 0:
        data['disambiguation'] = 'K_blood'
    return data

def Na_disambiguation(data):
    # 血清钠
    blood_index_key = ".*?(血清).*?"
    blood_index_key2 = ".*?(全血).*?"

    # 全血钠
    blood1_index_key = ".*?(全血).*?"
    blood1_index_key2 = ".*?(血清).*?"

    data['disambiguation'] = 'other'

    if re_match(blood_index_key, data['checkItemName']) == 1 and \
            re_match(blood_index_key2, data['checkItemName']) == 0:
        data['disambiguation'] = 'Na_serum'

    if (re_match(blood1_index_key, data['checkItemName']) == 1 and \
        re_match(blood1_index_key2, data['checkItemName']) == 0) or \
            result_value_replace_fw(data['textRef'], '63-97') == 1:
        data['disambiguation'] = 'Na_blood'
    return data

def HEV_disambiguation(data):
    # 戊型肝炎IgM
    blood_index_key = ".*?(gM).*?"
    blood_index_key2 = ".*?(IgG).*?"

    # 戊型肝炎IgG
    blood1_index_key = ".*?(gG).*?"
    blood1_index_key2 = ".*?(gM).*?"

    data['disambiguation'] = 'other'

    if re_match(blood_index_key, data['checkItemName']) == 1 and \
            re_match(blood_index_key2, data['checkItemName']) == 0:
        data['disambiguation'] = 'HEV_IgM'

    if re_match(blood1_index_key, data['checkItemName']) == 1 and \
            re_match(blood1_index_key2, data['checkItemName']) == 0:
        data['disambiguation'] = 'HEV_IgG'
    return data

def HBV_eAntibody_disambiguation(data):
    # 戊型肝炎IgM
    blood_index_key = ".*?([0-9]).*?"

    blood1_index_key2 = ".*?(阴|阳).*?"
    # 戊型肝炎IgG
    blood1_index_key = ".*?(阴|阳).*?"
    blood1_index_key3 = ".*?(\+|-).*?"

    data['disambiguation'] = 'other'

    # 以rs为准,rs为数值，则为定量
    if re_match(blood_index_key, data['resultValue']) == 1 and \
            re_match(blood1_index_key2, data['resultValue']) == 0:
        data['disambiguation'] = 'HBV_eAntibody_ration'

    # 颖哥代码逻辑rs含阴阳则是阴阳，故只选择rs等于阴阳
    if re_match(blood1_index_key, data['resultValue']) == 1 or \
            re_match(blood1_index_key3, data['resultValue']) == 1 and \
            re_match(blood_index_key, data['resultValue']) == 0:
        data['disambiguation'] = 'HBV_eAntibody_stable'
    return data

def HBV_eAntigen_disambiguation(data):
    # 戊型肝炎IgM
    blood_index_key = ".*?([0-9]).*?"

    blood1_index_key2 = ".*?(阴|阳).*?"
    # 戊型肝炎IgG
    blood1_index_key = ".*?(阴|阳).*?"
    blood1_index_key3 = ".*?(\+|-).*?"

    data['disambiguation'] = 'other'

    # 以rs为准,rs为数值，则为定量
    if re_match(blood_index_key, data['resultValue']) == 1 and \
            re_match(blood1_index_key2, data['resultValue']) == 0:
        data['disambiguation'] = 'HBV_eAntigen_ration'

    # 颖哥代码逻辑rs含阴阳则是阴阳，故只选择rs等于阴阳
    if re_match(blood1_index_key, data['resultValue']) == 1 or \
            re_match(blood1_index_key3, data['resultValue']) == 1 and \
            re_match(blood_index_key, data['resultValue']) == 0:
        data['disambiguation'] = 'HBV_eAntigen_stable'
    return data

def HBV_surface_Antibody_disambiguation(data):
    # 戊型肝炎IgM
    blood_index_key = ".*?([0-9]).*?"

    blood1_index_key2 = ".*?(阴|阳).*?"
    # 戊型肝炎IgG
    blood1_index_key = ".*?(阴|阳).*?"
    blood1_index_key3 = ".*?(\+|-).*?"

    data['disambiguation'] = 'other'

    # 以rs为准,rs为数值，则为定量
    if re_match(blood_index_key, data['resultValue']) == 1 and \
            re_match(blood1_index_key2, data['resultValue']) == 0:
        data['disambiguation'] = 'HBV_surface_Antibody_ration'

    # 颖哥代码逻辑rs含阴阳则是阴阳，故只选择rs等于阴阳
    if re_match(blood1_index_key, data['resultValue']) == 1 or \
            re_match(blood1_index_key3, data['resultValue']) == 1 and \
            re_match(blood_index_key, data['resultValue']) == 0:
        data['disambiguation'] = 'HBV_surface_Antibody_stable'
    return data

def HBV_surface_Antigen_disambiguation(data):
    # 戊型肝炎IgM
    blood_index_key = ".*?([0-9]).*?"

    blood1_index_key2 = ".*?(阴|阳).*?"
    # 戊型肝炎IgG
    blood1_index_key = ".*?(阴|阳).*?"
    blood1_index_key3 = ".*?(\+|-).*?"

    data['disambiguation'] = 'other'

    # 以rs为准,rs为数值，则为定量
    if re_match(blood_index_key, data['resultValue']) == 1 and \
            re_match(blood1_index_key2, data['resultValue']) == 0:
        data['disambiguation'] = 'HBV_surface_Antigen_ration'

    # 颖哥代码逻辑rs含阴阳则是阴阳，故只选择rs等于阴阳
    if re_match(blood1_index_key, data['resultValue']) == 1 or \
            re_match(blood1_index_key3, data['resultValue']) == 1 and \
            re_match(blood_index_key, data['resultValue']) == 0:
        data['disambiguation'] = 'HBV_surface_Antigen_stable'
    return data

def HBV_core_antibody_disambiguation(data):
    # 戊型肝炎IgM
    blood_index_key = ".*?([0-9]).*?"

    blood1_index_key2 = ".*?(阴|阳).*?"
    # 戊型肝炎IgG
    blood1_index_key = ".*?(阴|阳).*?"
    blood1_index_key3 = ".*?(\+|-).*?"

    data['disambiguation'] = 'other'

    # 以rs为准,rs为数值，则为定量
    if re_match(blood_index_key, data['resultValue']) == 1 and \
            re_match(blood1_index_key2, data['resultValue']) == 0:
        data['disambiguation'] = 'HBV_core_antibody_ration'

    # 颖哥代码逻辑rs含阴阳则是阴阳，故只选择rs等于阴阳
    if re_match(blood1_index_key, data['resultValue']) == 1 or \
            re_match(blood1_index_key3, data['resultValue']) == 1 and \
            re_match(blood_index_key, data['resultValue']) == 0:
        data['disambiguation'] = 'HBV_core_antibody_stable'
    return data

def pylorus_disambiguation(data):
    # 戊型肝炎IgM
    blood_index_key = ".*?([0-9]).*?"

    blood1_index_key2 = ".*?(阴|阳).*?"
    # 戊型肝炎IgG
    blood1_index_key = ".*?(阴|阳).*?"
    blood1_index_key3 = ".*?(\+|-).*?"

    data['disambiguation'] = 'other'

    # 以rs为准,rs为数值，则为定量
    if re_match(blood_index_key, data['resultValue']) == 1 and \
            re_match(blood1_index_key2, data['resultValue']) == 0:
        data['disambiguation'] = 'pylorus_ration'

    # 颖哥代码逻辑rs含阴阳则是阴阳，故只选择rs等于阴阳
    if re_match(blood1_index_key, data['resultValue']) == 1 or \
            re_match(blood1_index_key3, data['resultValue']) == 1 and \
            re_match(blood_index_key, data['resultValue']) == 0:
        data['disambiguation'] = 'pylorus_stable'
    return data

def EBV_disambiguation(data):
    # 定量
    blood_index_key = ".*?([0-9]).*?"

    blood1_index_key2 = ".*?(阴|阳).*?"
    # 定性
    blood1_index_key = ".*?(阴|阳).*?"
    blood1_index_key3 = ".*?(\+|-).*?"

    flag_dna = ".*?DNA.*?"

    data['disambiguation'] = 'other'

    # 以rs为准,rs为数值，则为定量
    if re_match(blood_index_key, data['resultValue']) == 1 and \
            re_match(blood1_index_key2, data['resultValue']) == 0 and \
            re_match(flag_dna, data['checkItemName']) == 1:
        data['disambiguation'] = 'EB_DNA_ration'

    # 颖哥代码逻辑rs含阴阳则是阴阳，故只选择rs等于阴阳
    if re_match(blood1_index_key, data['resultValue']) == 1 and \
            re_match(flag_dna, data['checkItemName']) == 1 or \
            re_match(blood1_index_key3, data['resultValue']) == 1 and \
            re_match(blood_index_key, data['resultValue']) == 0 and \
            re_match(flag_dna, data['checkItemName']) == 1:
        data['disambiguation'] = 'EB_DNA_stable'
        # CA,EA
    if re_match('.*?(gA|GA).*?', data['checkItemName']) == 1 and \
            re_match('.*?CA.*?', data['checkItemName']) == 1:
        data['disambiguation'] = 'EB_CA_IgA'

    if re_match('.*?(gA|GA).*?', data['checkItemName']) == 1 and \
            re_match('.*?EA.*?', data['checkItemName']) == 1:
        data['disambiguation'] = 'EB_EA_IgA'

    # IGM,IGG
    if re_match('.*?(GG|gG).*?', data['checkItemName']) == 0 and \
            re_match('.*?(gM|GM).*?', data['checkItemName']) == 1:
        data['disambiguation'] = 'EB_IgM'

    if re_match('.*?(GG|gG).*?', data['checkItemName']) == 1 and \
            re_match('.*?(gM|GM).*?', data['checkItemName']) == 0:
        data['disambiguation'] = 'EB_IgG'
    return data

def troponin_disambiguation(data):
    data['disambiguation'] = 'other'

    # TNT checkItem
    blood_index_key = ".*?(TNT).*?"
    blood_index_key1 = ".*?(阴|阳).*?"

    # I checkItem
    blood1_index_key = ".*?(I).*?"

    #     if re_match(blood_index_key, data['checkItemName']) == 1 and \
    #     re_match(blood1_index_key, data['checkItemName']) == 0 or \
    if re_match(blood_index_key1, data['resultValue']) == 1 or \
            result_value_replace(data['resultValue']) > 0.2 and \
            data['textRef'] != '0-15.6':
        data['disambiguation'] = 'troponin_T'

    #     if re_match(blood_index_key, data['checkItemName']) == 0 and \
    #     re_match(blood1_index_key, data['checkItemName']) == 1 or \
    if result_value_replace(data['resultValue']) < 0.2 and \
            result_value_replace(data['resultValue']) != -1 or \
            data['textRef'] == '0-15.4' or data['textRef'] == '0-15.6':
        #     re_match(blood_index_key, data['checkItemName']) == 0 or \

        data['disambiguation'] = 'troponin_I'
    return data

def fee_egg_disambiguation(data):
    # 尿转铁蛋白 范围从0开始，#indexName含尿
    data['disambiguation'] = 'other'

    # TNT checkItem
    blood_index_key = ".*?(尿).*?"
    blood_index_key1 = ".*?(阴).*?"

    # 血清转铁蛋白不含mg indexName含血清 范围从2开始
    # I checkItem
    blood1_index_key = ".*?(血).*?"
    blood1_index_key1 = ".*?(mg).*?"

    #     if re_match(blood_index_key, data['checkItemName']) == 1 and \
    #     re_match(blood1_index_key, data['checkItemName']) == 0 or \
    if re_match(blood_index_key, data['checkIndexName']) == 1 or \
            result_value_replace_fw(data['textRef'], '0-2') == 1 or \
            re_match(blood_index_key1, data['textRef']) == 1:
        data['disambiguation'] = 'fe_egg_urine'

    #     if re_match(blood_index_key, data['checkItemName']) == 0 and \
    #     re_match(blood1_index_key, data['checkItemName']) == 1 or \
    if re_match(blood1_index_key, data['checkIndexName']) == 1 or \
            result_value_replace_fw(data['textRef'], '2-500'):
        data['disambiguation'] = 'fe_egg_blood'
    return data

def mg_disambiguation(data):
    # 血清酶，item为电解质6项 index为血清
    data['disambiguation'] = 'other'

    # TNT checkItem
    blood_index_key = ".*?(电解质(6|六)项).*?"
    blood_index_key1 = ".*?(血清).*?"

    # index全血 or item为全血 index不为血清 全血大
    # I checkItem
    blood1_index_key = ".*?(全血).*?"
    blood1_index_key1 = ".*?(血清).*?"

    if re_match(blood_index_key, data['checkItemName']) == 1 or \
            re_match(blood_index_key1, data['checkIndexName']) == 1 or \
            re_match(blood_index_key1, data['checkItemName']) == 1 and re_match(blood1_index_key,
                                                                                data['checkItemName']) == 0:
        data['disambiguation'] = 'mg_serum'

    if re_match(blood1_index_key, data['checkIndexName']) == 1 or \
            re_match(blood1_index_key, data['checkItemName']) == 1 and re_match(blood1_index_key1,
                                                                                data['checkIndexName']) == 0:
        data['disambiguation'] = 'mg_blood'
    return data

def zn_disambiguation(data):
    # 血清酶，item为电解质6项 index为血清
    data['disambiguation'] = 'other'

    # TNT checkItem
    blood_index_key1 = ".*?(血清).*?"

    # index全血 or item为全血 index不为血清
    # I checkItem
    blood1_index_key = ".*?(全血).*?"
    blood1_index_key1 = ".*?(血清).*?"

    if re_match(blood_index_key1, data['checkIndexName']) == 1 or \
            re_match(blood_index_key1, data['checkItemName']) == 1 and re_match(blood1_index_key,
                                                                                data['checkItemName']) == 0:
        data['disambiguation'] = 'zn_serum'

    if re_match(blood1_index_key, data['checkIndexName']) == 1 or \
            re_match(blood1_index_key, data['checkItemName']) == 1 and re_match(blood1_index_key1,
                                                                                data['checkIndexName']) == 0:
        data['disambiguation'] = 'zn_blood'
    return data

def cu_disambiguation(data):
    # 血清酶，item为电解质6项 index为血清
    data['disambiguation'] = 'other'

    # TNT checkItem
    blood_index_key1 = ".*?(血清).*?"

    # index全血 or item为全血 index不为血清
    # I checkItem
    blood1_index_key = ".*?(全血).*?"
    blood1_index_key1 = ".*?(血清).*?"

    if re_match(blood_index_key1, data['checkIndexName']) == 1 or \
            re_match(blood_index_key1, data['checkItemName']) == 1 and re_match(blood1_index_key,
                                                                                data['checkItemName']) == 0:
        data['disambiguation'] = 'cu_serum'

    if re_match(blood1_index_key, data['checkIndexName']) == 1 or \
            re_match(blood1_index_key, data['checkItemName']) == 1 and re_match(blood1_index_key1,
                                                                                data['checkIndexName']) == 0:
        data['disambiguation'] = 'cu_blood'
    return data

def BMG_disambiguation(data):
    data['disambiguation'] = 'other'

    blood_index_key1 = ".*?(血).*?"

    # index全血 or item为全血 index不为血清
    # I checkItem
    blood1_index_key = ".*?(尿).*?"
    blood1_index_key1 = ".*?(血).*?"

    if re_match(blood_index_key1, data['checkIndexName']) == 1 or \
            re_match(blood_index_key1, data['checkItemName']) == 1 and re_match(blood1_index_key,
                                                                                data['checkItemName']) == 0:
        data['disambiguation'] = 'BMG_blood'

    if re_match(blood1_index_key, data['checkIndexName']) == 1 or \
            re_match(blood1_index_key, data['checkItemName']) == 1 and re_match(blood1_index_key1,
                                                                                data['checkIndexName']) == 0:
        data['disambiguation'] = 'BMG_urine'
    return data

def fe_disambiguation(data):
    # 血清酶，item为电解质6项 index为血清
    data['disambiguation'] = 'other'

    # TNT checkItem
    blood_index_key1 = ".*?(血清).*?"

    # index全血 or item为全血 index不为血清
    # I checkItem
    blood1_index_key = ".*?(全血).*?"
    blood1_index_key1 = ".*?(血清).*?"

    if re_match(blood_index_key1, data['checkIndexName']) == 1 or \
            re_match(blood_index_key1, data['checkItemName']) == 1 and re_match(blood1_index_key,
                                                                                data['checkItemName']) == 0:
        data['disambiguation'] = 'fe_serum'

    if re_match(blood1_index_key, data['checkIndexName']) == 1 or \
            re_match(blood1_index_key, data['checkItemName']) == 1 and re_match(blood1_index_key1,
                                                                                data['checkIndexName']) == 0:
        data['disambiguation'] = 'fe_blood'
    return data

def ins_disambiguation(data):
    data['disambiguation'] = 'other'

    # 抗胰岛素抗体IAA index含抗胰岛素 含阴阳的一定是抗胰岛素rs和text 单位为NaN的一定是抗胰岛素
    blood_index_key1 = ".*?(抗胰岛素|抗体).*?"
    blood_index_key2 = ".*?(阴|阳).*?"
    blood_index_key3 = ".*?(NaN).*?"

    # 空腹胰岛素测定 index含空腹 index 和 item含抗体的一定是抗胰岛素 不含ng    含pmol 但是不含抗体 不含 阴阳
    # I checkItem
    blood1_index_key = ".*?(空腹).*?"
    blood1_index_key1 = ".*?(pmol|uU/ml|Pmol|uIU/ml|mIU/L).*?"

    if re_match(blood_index_key1, data['checkIndexName']) == 1 or \
            re_match(blood_index_key2, data['resultValue']) == 1 or \
            re_match(blood_index_key2, data['textRef']) == 1 or \
            re_match(blood_index_key3, data['unit']) == 1 or \
            re_match(blood_index_key1, data['checkItemName']) == 1 and re_match(blood1_index_key,
                                                                                data['checkIndexName']) == 0:
        data['disambiguation'] = 'ins_IAA'

    if re_match(blood1_index_key, data['checkIndexName']) == 1 or \
            re_match(blood1_index_key, data['checkItemName']) == 1 and re_match(blood_index_key1,
                                                                                data['checkIndexName']) == 0 or \
            re_match(blood1_index_key1, data['unit']) == 1 and re_match(blood_index_key1,
                                                                        data['checkIndexName']) == 0 and \
            re_match(blood_index_key1, data['checkItemName']) == 0 and re_match(blood_index_key2,
                                                                                data['textRef']) == 0 and \
            re_match(blood_index_key2, data['resultValue']) == 0:
        data['disambiguation'] = 'ins_limosis'
    return data

def HCT_disambiguation(data):
    data['disambiguation'] = 'other'

    # 血粘度
    blood_index_key1 = ".*?(血粘度|流变).*?"

    # 血粘度压积
    if re_match(blood_index_key1, data['checkItemName']) == 1:
        data['disambiguation'] = 'HCT_viscosity'

    # 红细胞压积
    if re_match(blood_index_key1, data['checkItemName']) == 0 and \
            result_textRef_fw(data['textRef'], '10-50', '10-80'):
        data['disambiguation'] = 'HCT_red'

    # 血小板
    if re_match(blood_index_key1, data['checkItemName']) == 0 and \
            result_textRef_fw(data['textRef'], '0-1', '0-1'):
        data['disambiguation'] = 'HCT_palate'
    return data

def glu_disambiguation(data):
    data['disambiguation'] = 'other'

    # 尿葡萄糖
    blood_index_key1 = ".*?(阳|阴).*?"
    blood_index_key2 = ".*?(尿常规|尿液).*?"

    # 空腹血糖
    blood1_index_key1 = ".*?(空腹).*?"
    # 餐后2小时血糖
    blood1_index_key2 = ".*?(2h|2小时).*?"

    # 尿葡萄糖
    if re_match(blood_index_key2, data['checkItemName']) == 1 or \
            re_match(blood_index_key1, data['textRef']) == 1 or re_match(blood_index_key1, data['resultValue']) == 1:
        data['disambiguation'] = 'glucose_urine'

    # 空腹葡萄糖
    if re_match(blood_index_key2, data['checkItemName']) == 0 and \
            re_match(blood_index_key1, data['textRef']) == 0 and re_match(blood_index_key1,
                                                                          data['resultValue']) == 0 and \
            result_textRef_fw(data['textRef'], '0-5', '3-7') or re_match(blood1_index_key1, data['checkItemName']) == 1:
        data['disambiguation'] = 'glucose_blood_empty'

    # 餐后2小时血糖
    if re_match(blood_index_key2, data['checkItemName']) == 0 and \
            re_match(blood_index_key1, data['textRef']) == 0 and re_match(blood_index_key1,
                                                                          data['resultValue']) == 0 and \
            result_textRef_fw(data['textRef'], '0-5', '7-12') or re_match(blood1_index_key2,
                                                                          data['checkItemName']) == 1:
        data['disambiguation'] = 'glucose_blood_2hour'
    return data

# 石澳代码

"""
def glu_disambiguation(data):
    #将葡萄糖分为空腹血糖、尿葡萄糖、其他
    
    blood_index_key   = ".*?(尿|快速|餐后|随机).*"
    blood_item_key    = ".*?(尿常规|尿液|耐量|随机).*"
    blood_textref_key = ".*?(阴|阳|正常).*"

    urine_index_key   = ".*?(空腹|餐后|血).*"
    urine_value_key   = ".*?(阴|阳|Neg|- 0).*"
    urine_textref_key = ".*?(阴|阳|正常).*"
    
    data['disambiguation'] = 'other'
    
    if re_match(blood_index_key, data['checkIndexName']) == 0 and \
    re_match(blood_item_key, data['checkItemName']) == 0 and \
    re_match(blood_textref_key, data['textRef']) == 0 and \
    is_number(result_value_replace(data['resultValue'])):
        data['disambiguation'] = 'blood'
        #空腹血糖
                
    if re_match(urine_index_key, data['checkIndexName']) == 0 and \
    re_match(urine_value_key, data['resultValue']) == 1 and \
    re_match(urine_textref_key, data['textRef']) == 1:
        data['disambiguation'] = 'urine'
        #尿葡萄糖
"""


def wbc_disambiguation(data):
    # 将白细胞分为血白细和尿白细胞

    blood_index_key = ".*?(镜).*"
    blood_item_key = ".*?(尿常规|尿沉|白带|阴道).*"
    blood_value_key = ".*?(阴|阳|正常).*"
    blood_textref_key = ".*?(阴|阳|正常|少|多).*"
    blood_unit_key = ".*?(HP).*"

    data['disambiguation'] = 'NA'

    if re_match(blood_index_key, data['checkIndexName']) == 0 and \
            re_match(blood_item_key, data['checkItemName']) == 0 and \
            re_match(blood_value_key, data['resultValue']) == 0 and \
            re_match(blood_textref_key, data['textRef']) == 0:
        data['disambiguation'] = 'blood'
        # 血白细胞

    if re_match(blood_index_key, data['checkIndexName']) == 1 or \
            re_match(blood_item_key, data['checkItemName']) == 1 or \
            re_match(blood_value_key, data['resultValue']) == 1 or \
            re_match(blood_textref_key, data['textRef']) == 1:
        data['disambiguation'] = 'urine'
        # 尿白细胞
    return data

def bilirubin_disambiguation(data):
    # 将胆红素分为血胆红素和尿胆红素

    blood_index_key = ".*?(尿).*"
    blood_textref_key = ".*?(阴|阳).*"
    blood_value_key = ".*?(阴|阳).*"

    urine_index_key = ".*?(尿).*"
    urine_item_key = ".*?(尿).*"
    urine_value_key = ".*?([0-9]).*"
    urine_textref_key = ".*?([0-9]).*"

    data['disambiguation'] = 'NA'

    if re_match(blood_index_key, data['checkIndexName']) == 0 and \
            re_match(blood_textref_key, data['textRef']) == 0 and \
            re_match(blood_value_key, data['resultValue']) == 0:
        data['disambiguation'] = 'blood'

    if (re_match(urine_value_key, data['resultValue']) == 0 and re_match(urine_textref_key, data['textRef']) == 1) or \
            (re_match(urine_value_key, data['resultValue']) == 1 and re_match(urine_textref_key,
                                                                              data['textRef']) == 0) or \
            (re_match(urine_value_key, data['resultValue']) == 0 and re_match(urine_textref_key,
                                                                              data['textRef']) == 0) or \
            (re_match(urine_index_key, data['checkIndexName']) == 1 or re_match(urine_item_key,
                                                                                data['checkIndexName']) == 1):
        data['disambiguation'] = 'urine'
    return data

ratio_match_pattern = re.compile(r'.*?(比率|比值|百分数|百分比|百分率|CR|微核率)')
amount_match_pattern = re.compile(r'.*?(绝对值|数目|细胞数|细胞值|血小板数|血小板值|计数|CC|总数)')


def number_and_ratio_discrimination(data):
    """
    指标项名称中数目及比率区分
    
    amount: 数目
    ratio: 比率
    """
    index_name = data["checkIndexName"]
    data_type = 'other'
    if "%" in index_name or ratio_match_pattern.findall(index_name):
        data_type = 'ratio'

    if data_type == 'other' and ("#" in index_name or amount_match_pattern.findall(index_name)):
        data_type = 'amount'

    unit = data['unit'].strip().upper()
    if data_type == 'other' and unit:
        if unit in ["%"]:
            data_type = 'ratio'
        elif unit in ['10`9/L', '10^9/L', 'E+9/L', '10E9/L', '*10^9/L', '10*9/L', '10^3/UL', '10~9/L', '/L', 'M/L']:
            data_type = 'amount'

    text_ref = data['textRef'].strip().upper()
    if data_type == 'other':
        if "嗜酸性粒细胞" in index_name and text_ref in ['0.4-8.0']:
            data_type = 'ratio'
        else:
            data_type = 'amount'

    data['disambiguation'] = data_type

    return data


def erythrocyte_disambiguation(data):
    """
    红细胞细分类别判定
    
    leucorrhea: 白带红细胞
    semen: 精液红细胞
    feces: 粪便红细胞
    urine_mic_exam: 尿镜检红细胞
    urine_arena: 尿沉渣红细胞
    urine: 尿红细胞
    blood: 血红细胞
    """
    data_type = 'other'
    index_name = data["checkIndexName"]
    item_name = data["checkItemName"]
    if "白带" in index_name or "白带" in item_name or "四联" in item_name:
        # 白带红细胞
        data_type = 'leucorrhea'

    if data_type == 'other' and ("精液" in index_name or "精液" in item_name):
        # 精液红细胞
        data_type = 'semen'

    if data_type == 'other' and ("粪便" in item_name or "大便" in item_name or item_name == "便常规"):
        # 粪便红细胞
        data_type = 'feces'

    if data_type == 'other' and (
            "尿" in index_name or "尿" in item_name or "小便" in item_name or "阴道" in item_name or "肾病" in item_name):
        if "镜检" in index_name:
            # 尿镜检红细胞
            data_type = 'urine_mic_exam'
        elif "沉渣" in index_name or 'μL' in data["unit"] or 'uL' in data["unit"]:
            # 尿沉渣红细胞
            data_type = 'urine_arena'
        else:
            # 尿红细胞
            data_type = 'urine'

    if data_type == 'other' and ("血" in index_name or "血" in item_name or "地贫" in item_name):
        # 血红细胞
        data_type = 'blood'

    data['disambiguation'] = data_type

    return data


occult_blood_urine_match_pattern = re.compile(r'尿|肾病|干化学|小便常规')
occult_blood_feces_match_pattern = re.compile(r'粪便|大便|便隐血|便潜血|便常规')


def occult_blood_disambiguation(data):
    """
    隐血分类别判定
    
    urine: 尿隐血
    feces: 便隐血
    """
    data_type = 'other'
    index_name = data["checkIndexName"].strip().replace(" ", "")
    item_name = data["checkItemName"].strip().replace(" ", "")
    if "尿" in index_name or occult_blood_urine_match_pattern.findall(item_name):
        data_type = 'urine'

    if data_type == 'other' and (
            occult_blood_feces_match_pattern.findall(index_name) or occult_blood_feces_match_pattern.findall(
            item_name)):
        data_type = 'feces'

    data['disambiguation'] = data_type

    return data


color_feces_match_pattern = re.compile(r'粪便|大便|便常规|便(潜|隐)血')
color_skin_match_pattern = re.compile(r'皮肤|外科')


def color_disambiguation(data):
    """
    颜色分类别判定
    
    urine: 尿颜色
    feces: 便颜色
    skin: 皮肤颜色
    semen: 精液颜色
    """
    data_type = 'other'
    index_name = data["checkIndexName"].strip().replace(" ", "")
    item_name = data["checkItemName"].strip().replace(" ", "")
    if "尿" in index_name or "尿" in item_name:
        data_type = 'urine'

    if data_type == 'other' and (
            color_feces_match_pattern.findall(index_name) or color_feces_match_pattern.findall(item_name)):
        data_type = 'feces'

    if data_type == 'other' and (
            color_skin_match_pattern.findall(index_name) or color_skin_match_pattern.findall(item_name)):
        data_type = 'skin'

    if data_type == 'other' and ("精液" in index_name or "精液" in item_name):
        data_type = 'semen'

    data['disambiguation'] = data_type

    return data


ph_urine_match_pattern = re.compile(r'尿|干化学|肾病|大生化|小便常规')
ph_vagina_match_pattern = re.compile(r'阴道|妇科|白带')


def ph_disambiguation(data):
    """
    酸碱度分类别判定
    
    urine: 尿酸碱度
    vagina: 阴道酸碱度
    """
    data_type = 'other'
    index_name = data["checkIndexName"].strip().replace(" ", "")
    item_name = data["checkItemName"].strip().replace(" ", "")
    if "尿" in index_name or ph_urine_match_pattern.findall(item_name):
        data_type = 'urine'

    if data_type == 'other' and ("阴道" in index_name or ph_vagina_match_pattern.findall(item_name)):
        data_type = 'vagina'

    data['disambiguation'] = data_type

    return data


creatinine_urine_match_pattern = re.compile(r'尿|肾(功能)?损伤|肾病|肾功能筛查')
creatinine_blood_match_pattern = re.compile(r'肾功|生化|血清')


def creatinine_disambiguation(data):
    """
    肌酐分类别判定
    
    urine: 尿肌酐
    blood: 血肌酐
    """
    data_type = 'other'
    index_name = data["checkIndexName"].strip().replace(" ", "")
    item_name = data["checkItemName"].strip().replace(" ", "")
    if "尿肌酐" in index_name or ph_urine_match_pattern.findall(item_name):
        data_type = 'urine'

    if data_type == 'other' and ("血清肌酐" in index_name or creatinine_blood_match_pattern.findall(item_name)):
        data_type = 'blood'

    data['disambiguation'] = data_type

    return data


rdw_cv_match_pattern = re.compile(r'cv|变异')
rdw_sd_match_pattern = re.compile(r'sd|标准差')
rdw_text_ref_match_pattern = re.compile(r'([\d.]*)-{1,2}([\d.]*)')


def rdw_disambiguation(data):
    """
    红细胞分布宽度分类别判定
    
    cv: 变异系数
    sd: 标准差
    """
    data_type = 'other'
    index_name = data["checkIndexName"].strip().replace(" ", "").lower()
    if rdw_cv_match_pattern.findall(index_name):
        data_type = 'cv'

    if data_type == 'other' and (rdw_sd_match_pattern.findall(index_name)):
        data_type = 'sd'

    text_ref = data["textRef"]
    if data_type == 'other' and text_ref:
        ret = rdw_text_ref_match_pattern.findall(text_ref)
        if ret and float(ret[0][1]) < 30:
            data_type = 'cv'
        else:
            data_type = 'sd'

    data['disambiguation'] = data_type

    return data


mch_amount_match_pattern = re.compile(r'蛋白量|含量')


def mch_disambiguation(data):
    """
    平均红细胞血红蛋白分类别判定
    
    amount: 含量
    consistence: 浓度
    """
    data_type = 'other'
    index_name = data["checkIndexName"].strip().replace(" ", "").lower()
    if mch_amount_match_pattern.findall(index_name):
        data_type = 'amount'

    if data_type == 'other' and "浓度" in index_name:
        data_type = 'consistence'

    data['disambiguation'] = data_type

    return data


def erythrocyte_sedimentation_disambiguation(data):
    """
    血沉分类别判定
    
    k_value: 血沉k值
    esr: 血沉
    """
    data_type = 'other'
    index_name = data["checkIndexName"].replace(" ", "").lower()
    unit = data["unit"].lower()
    if "k值" in index_name or "esr.k" in index_name or "方程值" in index_name or "esr.k" in unit:
        data_type = 'k_value'

    if data_type == 'other' and ("mm/h" in index_name or "mm/h" in unit or "mm-h" in unit):
        data_type = 'esr'

    if data_type == 'other':
        data_type = 'esr'

    data['disambiguation'] = data_type

    return data
