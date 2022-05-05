from enum import Enum


class QuestionStatus(str, Enum):
    UNKNOWN = "unknown"
    LEARNING = "learning"
    KNOWN = "known"
