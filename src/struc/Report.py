from struc.Base import Structure, noDefault, dataclass
from struc.Enum import GenderEnum

@dataclass
class Indicator(Structure):
    """
    原始指标项
    """
    name: str = noDefault
    checkIndexName: str = noDefault
    checkItemName: str = noDefault
    resultValue: str = noDefault
    resultFlagId: int = 1
    textRef: str = ""
    unit: str = ""

@dataclass
class User(Structure):
    report_id: str = noDefault
    gender: GenderEnum = GenderEnum.whole  # 性别
    age: int = noDefault  # 年龄

@dataclass
class SummaryContent(Structure):
    """
    总检内容
    """
    content: str = noDefault  # 总检项



