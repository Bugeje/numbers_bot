from enum import IntEnum

class State(IntEnum):
    ASK_NAME = 0
    ASK_BIRTHDATE = 1
    EXTENDED_ANALYSIS = 2
    ASK_PARTNER_NAME = 3
    ASK_PARTNER_BIRTHDATE = 4
