from struc.Report import Indicator
from db.Postgres import Session
from db.Postgres import ItemNameMap as ItemNameMapDB
from db.Postgres import Disambiguation as DisambiguationDB
from dataclasses import asdict
from copy import deepcopy
from typing import List

# 获取消歧函数，并加载
import importlib

# 获取消歧函数中所有方法及其名称，制成字典
lib = importlib.import_module("mod.disambiguation")
func_name_list = [funcname for funcname in dir(lib) if not funcname.startswith("__")]
disambiguation_func_dict = {}
for funcname in func_name_list:
    disambiguation_func_dict[funcname] = getattr(lib, funcname)


def clean_name_disambiguation(indicator: Indicator, funcname: str):
    """
    调用消歧函数，返回消歧后tag
    """
    indicator_copy = deepcopy(indicator)
    func = disambiguation_func_dict.get(funcname, None)
    if func:
        data = func(asdict(indicator_copy))
        return data["disambiguation"]
    else:
        return "not_match_func"


def load_item_name_db():
    """
    加载指标项数据
    """
    session = Session()
    result = session.query(ItemNameMapDB)
    return result


# 指标项数据
item_name_db = load_item_name_db()


def load_disambiguation_db():
    """
    加载消岐信息表
    """
    session = Session()
    result = session.query(DisambiguationDB)
    return result


# 消岐信息表
disambiguation_info_db = load_disambiguation_db()


def getStdIndicator(indicators: List[Indicator]) -> List[Indicator]:
    # 查询所有指标项关联的“脏名映射表”信息,制成字典
    itemnamemaps_db = (
        item_name_db.filter(
            ItemNameMapDB.dirty_name.in_([indicator.checkIndexName for indicator in indicators])
        ).all()
    )
    itemnamemap_dict = {}
    for itemnamemap_db in itemnamemaps_db:
        itemnamemap_dict[itemnamemap_db.dirty_name] = itemnamemap_db

    # 替换项目名称为干净名
    indicators_copy = []
    for indicator in indicators:
        if indicator.checkIndexName in itemnamemap_dict:
            indicator.name = itemnamemap_dict[indicator.checkIndexName].name
            if indicator.name != "其它":
                indicators_copy.append(indicator)
    indicators = deepcopy(indicators_copy)

    # 查询所有需要消歧的指标对应的“消歧函数表”信息，并制成字典
    disambiguations_db = (
        disambiguation_info_db.filter(
            DisambiguationDB.before_name.in_([indicator.name for indicator in indicators])
        ).distinct().all()
    )
    disambiguation_db_dict = dict(
        zip(
            [disambiguation.before_name for disambiguation in disambiguations_db],
            [disambiguation.disambiguation_function_name for disambiguation in disambiguations_db],
        )
    )

    # 消歧
    indicators_copy = []
    for indicator in indicators:
        if indicator.name in disambiguation_db_dict:
            funcname = disambiguation_db_dict[indicator.name]
            flag = clean_name_disambiguation(indicator, funcname)
            if flag != "not_match_func":
                for disambiguation_db in disambiguations_db:
                    if disambiguation_db.before_name == indicator.name and disambiguation_db.disambiguation_flag == flag:
                        indicator.name = disambiguation_db.after_name
                indicators_copy.append(indicator)
        else:
            indicators_copy.append(indicator)
    indicators = deepcopy(indicators_copy)
    return indicators
