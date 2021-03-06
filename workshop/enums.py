from enum import Enum


class Element_type():
    # 便签
    STICKY = 'sticky'
    # 卡
    CARD = 'card'


class Card_type():
    # 工具卡,有子类
    TOOL = 'tool'
    # 愿景卡
    VISION = 'vision'
    # 数据卡
    DATA = 'data'
    # 业务价值痛点卡
    VALUE = 'value'
    # 场景卡
    SCENE = 'scene'


class ToolCardTypes(Enum):
    # 变现卡
    MONETIZING = 'monetizing'
    # 技能卡
    TECH = 'tech'
    # 类别卡
    CLASS = 'class'
    # 主题卡
    SUBJECT = 'subject'

    @classmethod
    def getMemberValues(cls):
        return map(lambda a: a.value, ToolCardTypes.__members__.values())


class StepTypes:
    BUSINESS_VISION = 'businessVision'
    DATA_PANORAMA = 'dataPanorama'
    TECHNOLOGY_CARD = 'technologyCard'
    DIVERGENCE_SCENE = 'divergenceScene'
    CONVERGENCE_SCENE = 'convergenceScene'
    GENERATE_REPORT = 'generateReport'


class RoleTypes:
    CREATOR = 'creator'
    MEMBER = 'member'
