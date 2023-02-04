UNKNOWN_VALUE = UNKNOWN_VALUE

MESECI_MAPPING = dict(
    Jan="01",
    Feb="02",
    Mar="03",
    Apr="04",
    May="05",
    Jun="06",
    Jul="07",
    Aug="08",
    Sep="09",
    Oct="10",
    Nov="11",
    Dec="12",
)

MOZNE_VREDNOSTI_SSDja = [
    1,
    2,
    16,
    32,
    64,
    128,
    240,
    256,
    500,
    512,
    1000,
    1024,
]

SSD_MAPPING = {
    0: 1,
    1: 2,
    2: 3,
    16: 4,
    32: 5,
    64: 6,
    120: 7,
    128: 8,
    240: 9,
    250: 10,
    256: 11,
    500: 12,
    512: 13,
    1000: 14,
    1024: 15,
    2000: 16,
    2048: 17,
    UNKNOWN_VALUE: 18,
}


RAM_MAPPING = {
    4: 1,
    6: 2,
    8: 3,
    12: 4,
    16: 5,
    32: 6,
    46: 7,
    48: 8,
    58: 9,
    64: 10,
    128: 11,
    UNKNOWN_VALUE: 12,
}

PROIZVAJALEC_MAPPING = {
    "Intel": 1,
    "GEEKOM": 2,
    "MINIS FORUM": 3,
    "Shinobee": 4,
    "Chuwi": 5,
    "BMAX": 6,
    "Lenovo": 7,
    "HP": 8,
    "GIGABYTE": 9,
    "HISTTON": 10,
    "Shuttle": 11,
    "DILC": 12,
    "WEIDIAN": 13,
    "AKASA": 14,
    "Kaby Lake": 15,
    "STRHIGP": 16,
    "Apple": 17,
    "ZOTAC": 18,
    "Beelink": 19,
    "Fujitsu": 20,
    "MeLE": 21,
    UNKNOWN_VALUE: 22,
}

OS_MAPPING = {
    "Windows": 1,
    "OS X": 2,
    "Linux": 3,
    "no OS": 4,
    UNKNOWN_VALUE: 5
}


