import enum


class ReviewCycleEnum(enum.Enum):
    """
    复检周期
    """

    one_year = "一年后"
    half_a_year = "半年后"
    thress_months = "三个月后"
    two_months = "两个月后"
    one_month = "一个月后"
    half_a_month = "半个月后"
    two_weeks = "两周后"
    one_week = "一周后"
    one_day = "一天后"


class GenderEnum(enum.Enum):
    """
    性别类型
    """

    male = "男"
    female = "女"
    whole = "所有人"


class AbnormalDirectionEnum(enum.Enum):
    """
    异常方向
    """

    unknow = 0
    inner = 1
    upper = 2
    lower = 3


class DiseaseTagEnum(enum.Enum):
    # the value here is used for ordering
    unknow = 1  # 未知
    week = 2  # 弱
    strong = 3  # 强
    summary = 4  # 总检
    highest = 5  # 最高优先级

    def __lt__(self, obj):
        return self.value > obj.value