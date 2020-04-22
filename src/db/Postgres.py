import os
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, Enum, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from struc.Enum import (
    ReviewCycleEnum,
    GenderEnum,
    AbnormalDirectionEnum,
    DiseaseTagEnum,
)


database_host = os.environ.get("database_host", "192.168.1.152")
database_port = os.environ.get("database_port", "5434")
engine_string = "postgres://postgres:postgres@{database_host}:{database_port}".format(
    database_host=database_host, database_port=database_port
)
engine = create_engine(engine_string, echo=False, pool_size=1000, max_overflow=1000)
Session = sessionmaker(bind=engine, autoflush=True)

DBase = declarative_base()


class ItemNameMap(DBase):
    __tablename__ = "ItemNameMap"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    item_id = Column(String) 
    dirty_name = Column(String)
    dirty_name_id = Column(String)  
    coverage = Column(Float)  
    meinian_name = Column(String)  
    ambiguity_determination = Column(String)  
    dirty_name_source = Column(String)


class Disambiguation(DBase):
    __tablename__ = "Disambiguation"

    id = Column(Integer, primary_key=True)
    before_name = Column(String)  # 消歧前项目名
    after_name = Column(String)  # 消歧后项目名
    disambiguation_function_name = Column(String)  # 消岐函数名
    disambiguation_flag = Column(String)  # 消岐函数flag


class Disease(DBase):
    """
    310最优先疾病指标关联表
    311疾病和项目强关联
    312总检关键词表
    313疾病和项目弱关联
    """

    __tablename__ = "Disease"

    id = Column(Integer, primary_key=True)

    item_name = Column(String)  # 项目干净名
    item_name_meinian = Column(String)  # 美年项目脏名
    item_id = Column(String)  # 项目干净名ID
    check_measure = Column(String)  # 检查方法
    unit = Column(String)  # 单位
    part = Column(String)  # 部位
    alias = Column(String)  # 别名
    english_short_name = Column(String)  # 英文简称
    item_category = Column(String)  # 项目类别
    significance = Column(String)  # 意义
    provenance = Column(String)  # 出处
    key_word = Column(String)  # 关键词（名词）
    result_word = Column(String)  # 结果（形容词）
    normal_range = Column(String)  # 正常范围
    normal_range_lower = Column(Float)  # 正常范围下限
    normal_range_upper = Column(Float)  # 正常范围上限
    abnormal_range = Column(String)  # 异常范围
    range_lower = Column(Float)  # 异常范围下限
    range_upper = Column(Float)  # 异常范围上限
    abnormal_direction = Column(Enum(AbnormalDirectionEnum))  # 异常方向
    united_number = Column(Integer)  # 联合编号
    correlation = Column(String)  # 关联度
    gender = Column(Enum(GenderEnum))  # 性别
    review_cycle = Column(Enum(ReviewCycleEnum))  # 复查周期
    crowd = Column(String)  # 人群
    tag = Column(Enum(DiseaseTagEnum))  # 强弱关联Tag
    default_rating = Column(String)  # 默认评级

    name = Column(String)  # 疾病名称
    # disease_id = Column(Integer)  # 疾病ID
    class_1 = Column(String)  # 一级分类
    # class_2 = Column(String)  # 二级分类
    # image_name = Column(String)  # 图片名称?? 图片名称与show_name一致
    show_name = Column(String)  # 显示名称
    img_url = Column(String)  # 图片链接名称
    is_disease = Column(Integer)  # 是否代表疾病
    departments = Column(ARRAY(String))  # 所属科室

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, obj):
        return self.name == obj.name and self.item_name == obj.item_name

    def __hash__(self):
        return hash(self.name)