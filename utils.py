""" Metode, ki pomagajo k parsanju podatkov """

import re
import datetime

DAN_BRANJA_PODATKOV = datetime.date(2022, 11, 8)

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


def get_OS(opis_naprave):
    opis_naprave = opis_naprave.lower()
    if re.search(r'(windows|office|win|w11)', opis_naprave):
        return 'Windows'
    elif re.search(r'apple', opis_naprave):
        return 'OS X'
    elif re.search(r'(linux|ubuntu)', opis_naprave):
        return 'Linux'
    elif re.search(r'barebone', opis_naprave):
        return 'no OS'
    return 'unknown'


def stevilo_dni_od_danasnjega_dneva(seznam_datumov):
    """Izracuna stevilo dni stringa datum do danasnjega dne"""

    # Datum sparsam v formatu "<dan>, <krajsava za mesec> <dan>"
    # Tako imam shranjeno tudi konstanto DAN_BRANJA_PODATKOV
    # Vrne razliko v dnevih med danasnjim dnem ter najdaljsim datumom na seznamu datumov; to je vedno zadnji element.
    def _pretvori_niz_datuma_v_objekt(datum):
        """ '<dan>, <krajsava za mesec> <dan>' -> "<dan><mesec - stevilcno><2022> """
        datum_parsed = datum.split(", ")[-1].split(" ")
        # meseci_mapping[datum_parsed.split(" ")[0]]
        dnevi = datum_parsed[1] if len(datum_parsed[1]) == 2 else f"0{datum_parsed[1]}"
        meseci = MESECI_MAPPING[datum_parsed[0]]
        leto = "2022" if datum_parsed[0] in ("Nov", "Dec") else "2023"
        return datetime.datetime.strptime(f"{dnevi}{meseci}{leto}", "%d%m%Y").date()

    razlika_casa = _pretvori_niz_datuma_v_objekt(seznam_datumov[-1]) - DAN_BRANJA_PODATKOV
    return razlika_casa.days


def get_proizvajalca(opis_naprave):
    opis_naprave = opis_naprave.lower()
    if re.search(r'(intel|ghost.?canyon|mipowcat)', opis_naprave):
        return 'Intel'
    elif re.search(r'geekom', opis_naprave):
        return 'GEEKOM'
    elif re.search(r'minis.?forum', opis_naprave):
        return 'MINIS FORUM'
    elif re.search(r'shinobee', opis_naprave):
        return 'Shinobee'
    elif re.search(r'chuwi', opis_naprave):
        return 'Chuwi'
    elif re.search(r'bmax', opis_naprave):
        return 'BMAX'
    elif re.search(r'lenovo', opis_naprave):
        return 'Lenovo'
    elif re.search(r'hp', opis_naprave):
        return 'HP'
    elif re.search(r'gigabyte', opis_naprave):
        return 'GIGABYTE'
    elif re.search(r'histton', opis_naprave):
        return 'HISTTON'
    elif re.search(r'shuttle', opis_naprave):
        return 'Shuttle'
    elif re.search(r'dilc', opis_naprave):
        return 'DILC'
    elif re.search(r'weidian', opis_naprave):
        return 'WEIDIAN'
    elif re.search(r'akasa', opis_naprave):
        return 'AKASA'
    elif re.search(r'kaby.?lake', opis_naprave):
        return 'Kaby Lake'
    elif re.search(r'strhigp', opis_naprave):
        return 'STRHIGP'
    elif re.search(r'apple', opis_naprave):
        return 'Apple'
    elif re.search(r'zotac', opis_naprave):
        return 'ZOTAC'
    elif re.search(r'beelink', opis_naprave):
        return 'Beelink'
    elif re.search(r'fujitsu', opis_naprave):
        return 'Fujitsu'
    elif re.search(r'mele', opis_naprave):
        return 'MeLE'
    return 'unknown'
