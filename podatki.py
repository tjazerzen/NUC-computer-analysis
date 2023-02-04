import re
import os
import datetime
from orodja import (
    shrani_spletno_stran,
    vsebina_datoteke,
    zapisi_csv,
)

from utils import (
    MESECI_MAPPING,
    MOZNE_VREDNOSTI_SSDja,
    PROIZVAJALEC_MAPPING,
    RAM_MAPPING,
    OS_MAPPING,
    SSD_MAPPING,
    UNKNOWN_VALUE,
)

DATA_RAW_DIRECTORY = 'podatki_raw'  # mapa, v katero bomo shranili podatke
DATA_OBDELANI_DIRECTORY = 'obdelani-podatki'
VSILI_PRENOS_SPLETNE_STRANI = False  # True, če želimo na novo downloadati raw podatke; False sicer
STEVILO_STRANI = 19  # Preveril ročno
# Datum branja podatkov. Potreboval ga bom za računanje, čez približno koliko bi dni bi napravo dostavili
GIGABYTE_TO_TERABYTE = 1024
DAN_BRANJA_PODATKOV = datetime.date(2022, 11, 8)

PODATKI_POMOZNIH_TABEL = [
    (PROIZVAJALEC_MAPPING, "proizvajalec", "proizvajalci"), (RAM_MAPPING, "ram", "ram"),
    (SSD_MAPPING, "ssd", "ssd"), (OS_MAPPING, "operacijski_sistem", "operacijski_sistem")
]

vzorec_bloka = re.compile(
    r'<div data-asin=".*?" '
    r'data-index="[1-9][0-9]?" '
    r'data-uuid=".*?" '
    r'data-component-type=(""|"s-search-result") '
    r'class="s-result-item .*?sg-col-0-of-12 sg-col-16-of-20 .*?'
    r'sg-col .*?s-widget-spacing-(small|large).*?">'
    r'<div class="sg-col-inner">'
    r'(.|\n)*?'
    r'(</div>){7,12}'
)

vzorec_nuca_s_ceno = re.compile(
    r'<span class="a-size-medium a-color-base a-text-normal">(?P<opis>.*?)</span>'
    r'.*?<span class="a-offscreen">€(?P<cena>.*?)</span>'
)

vzorec_nuca_brez_cene = re.compile(
    r'<span class="a-size-medium a-color-base a-text-normal">(?P<opis>.*?)</span>'
)

vzorec_idja = re.compile(
    r'<div data-asin="(?P<id>.*?)" data-index="(.|..)" data-uuid=".*?"'
)

vzorec_kupona = re.compile(
    r'<span class="a-size-base s-highlighted-text-padding aok-inline-block s-coupon-highlight-color">'
    r'Save €(?P<vrednost_kupona>.*?)'
    r'</span>'
)

vzorec_ocene = re.compile(
    r'<span class="a-icon-alt">'
    r'(?P<ocena>.*?)'
    r' out of 5 stars</span>'
    r'.*?'
    r'customerReviews"><span class="a-size-base .*?">'
    r'(?P<stevilo_ocen>.*?)'
    r'</span>'
)

vzorec_dneva_dostave = re.compile(
    r'<span aria-label="Get it (?P<dan_dostave>.*?, .*?)">'
)

vzorec_amazon_choice = re.compile(
    r'<span class="a-badge-label-inner a-text-ellipsis">'
    r'<span class="a-badge-text" data-a-badge-color="sx-cloud">'
    r'Amazon\'s .*?Choice'
    r'</span></span>'
)

vzorec_sponzoriran_produkt = re.compile(
    r'<span class="a-color-base">Sponsored</span>'
)

vzorec_ssd_velikost = f'({"|".join([str(velikost) for velikost in MOZNE_VREDNOSTI_SSDja])})'
vzorec_ssd_stevilka_po_besedi_ssd = re.compile(r'ssd: (?P<ssd>.*?)gb')
vzorec_ssd_stevilka_pred_besedo_ssd = re.compile(r'(?P<ssd>....)( )?(gb|tb) (pcie|nvme|pcle)?( )?ssd')
vzorec_ssd_m2_ssd = re.compile(r'(ddr4|lpddr4,) (?P<ssd>.*?)(gb|tb|g) m.2 .*?ssd')

vzorec_ram_stevilka_pred_besedo = re.compile(r'(?P<ram>...)( )?(gb|g) (ram|ddr4)')
vzorec_ram_stevilka_po_besedi = re.compile(r'(ram|ddr4)(:)?[^ ] (?P<ram>...)')


def _url_spletne_strani(st_strani):
    return (
        "https://www.amazon.de/-/en/"
        f"s?k=nuc&page={st_strani}&language=en"
        "&crid=3VIZDYTXC6EN7&qid=1667900250&sprefix=n%2Caps%2C187&"
        f"ref=sr_pg_{st_strani}"
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
    return UNKNOWN_VALUE


def _ime_raw_strani(st_strani):
    return os.path.join(DATA_RAW_DIRECTORY, f"nuc{st_strani}.html")


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
    return UNKNOWN_VALUE


def get_ssd(opis_naprave):
    def _convert_digit_to_ssd(ssd_parsed_digit):
        return ssd_parsed_digit * GIGABYTE_TO_TERABYTE if ssd_parsed_digit in (1, 2) else ssd_parsed_digit

    opis_naprave = opis_naprave.lower()
    if re.search(r'ssd', opis_naprave) and re.search(vzorec_ssd_velikost, opis_naprave):
        if re.search(vzorec_ssd_stevilka_po_besedi_ssd, opis_naprave):
            ssd_digit = int(vzorec_ssd_stevilka_po_besedi_ssd.search(opis_naprave).groupdict().get("ssd"))
            ssd = _convert_digit_to_ssd(ssd_digit)
        elif re.search(vzorec_ssd_stevilka_pred_besedo_ssd, opis_naprave):
            ssd_raw = vzorec_ssd_stevilka_pred_besedo_ssd.search(opis_naprave).groupdict().get("ssd")
            ssd_digit = int(re.sub("[^0-9]", "", ssd_raw.split(" ")[-1]))
            ssd = _convert_digit_to_ssd(ssd_digit)
        elif re.search(vzorec_ssd_m2_ssd, opis_naprave):
            ssd_digit = int(vzorec_ssd_m2_ssd.search(opis_naprave).groupdict().get("ssd").strip("ram "))
            ssd = _convert_digit_to_ssd(ssd_digit)
        else:
            ssd = UNKNOWN_VALUE
        return ssd
    return UNKNOWN_VALUE


def _id_kolicine(ime_kolicine):
    return f"{ime_kolicine}_id"


def vrni_pomozne_tabele(mapping, ime_kolicine):
    """Uporabljeno na spremenljivkah PROIZVAJALEC_MAPPING, RAM_MAPPING, SSD_MAPPING"""
    return [{_id_kolicine(ime_kolicine): oznaka_kolicine, ime_kolicine: kolicina}
            for kolicina, oznaka_kolicine in mapping.items()]


def get_ram(opis_naprave):
    opis_naprave = opis_naprave.lower()
    if re.search(vzorec_ram_stevilka_pred_besedo, opis_naprave):
        ram_raw = vzorec_ram_stevilka_pred_besedo.search(opis_naprave).groupdict("ram").get("ram")
        return int(re.sub("[^0-9]", "", ram_raw))
    elif re.search(vzorec_ram_stevilka_po_besedi, opis_naprave):
        ram_raw = vzorec_ram_stevilka_po_besedi.search(opis_naprave).groupdict("ram").get("ram")
        try:
            return int(re.sub("[^0-9]", "", ram_raw))
        except ValueError:
            return UNKNOWN_VALUE
    else:  # re.search(r'barebone', opis_naprave) or re.search(r'(no ram|without ram)', opis_naprave) or not
        # re.search(r'(ram|ddr4)', opis_naprave)
        return UNKNOWN_VALUE


def izloci_podatke_nuca(blok):
    try:
        nuc = vzorec_nuca_s_ceno.search(blok).groupdict()
        nuc['cena'] = float(nuc['cena'].replace(",", ""))
    except AttributeError:
        # Empirično sem ugotovil, da nekateri NUC-i nimajo predpisane cene. To razrešim z try/except blokom
        nuc = vzorec_nuca_brez_cene.search(blok).groupdict()
        nuc.setdefault("cena", -1)
    nuc = dict(nuc, **vzorec_idja.search(blok).groupdict())
    if re.search(vzorec_kupona, blok):
        nuc = dict(nuc, **vzorec_kupona.search(blok).groupdict())
    nuc.setdefault("vrednost_kupona", 0)  # NUC-om brez kupona pripišem, da ima kupon vrednost 0
    if re.search(vzorec_ocene, blok):
        nuc = dict(nuc, **vzorec_ocene.search(blok).groupdict())
    nuc.setdefault("ocena", -1)
    nuc.setdefault("stevilo_ocen", 0)
    if re.search(vzorec_dneva_dostave, blok):
        seznam_datumov = vzorec_dneva_dostave.search(blok).groupdict()["dan_dostave"].split(" - ")
        st_dni = stevilo_dni_od_danasnjega_dneva(seznam_datumov)
        nuc["cas_dostave"] = st_dni
    nuc.setdefault("cas_dostave", -1)
    nuc["amazons_choice"] = True if re.search(vzorec_amazon_choice, blok) else False
    nuc["produkt_sponzoriran"] = True if re.search(vzorec_sponzoriran_produkt, blok) else False
    nuc[_id_kolicine("proizvajalec")] = PROIZVAJALEC_MAPPING[get_proizvajalca(nuc["opis"])]
    nuc[_id_kolicine("OS")] = OS_MAPPING[get_OS(nuc["opis"])]
    nuc[_id_kolicine("ssd")] = SSD_MAPPING[get_ssd(nuc["opis"])]
    nuc[_id_kolicine("ram")] = RAM_MAPPING[get_ram(nuc["opis"])]
    return nuc


def nuci_na_strani(st_strani):
    """
    Shrani raw podatke v folder ./data, če je VSILI_PRENOS_SPLETNE_STRANI nastavljen na True, ter vsako stran sparsa
    """
    ime_datoteke = _ime_raw_strani(st_strani)
    if VSILI_PRENOS_SPLETNE_STRANI:
        shrani_spletno_stran(
            url=_url_spletne_strani(st_strani),
            ime_datoteke=ime_datoteke,
            vsili_prenos=VSILI_PRENOS_SPLETNE_STRANI,
        )
    vsebina = vsebina_datoteke(ime_datoteke)
    for blok in vzorec_bloka.finditer(vsebina):
        yield izloci_podatke_nuca(blok.group(0))


def main():
    """Funkcija izvede celoten del pridobivanja podatkov:
    1. Oglase prenese iz amazona
    2. Lokalno html datoteko pretvori v lepšo predstavitev podatkov
    3. Podatke shrani v csv datoteko
    """
    nuci = []
    for st_strani in range(1, STEVILO_STRANI + 1):
        for nuc in nuci_na_strani(st_strani):
            nuci.append(nuc)
    zapisi_csv(
        nuci,
        [
            'opis',
            'cena',
            'id',
            'vrednost_kupona',
            'ocena',
            'stevilo_ocen',
            'cas_dostave',
            'amazons_choice',
            'produkt_sponzoriran',
            'proizvajalec_id',
            'OS_id',
            'ssd_id',
            'ram_id'
        ],
        'obdelani-podatki/nuci.csv'
    )
    for mapping, ime_kolicine, ime_tabele in PODATKI_POMOZNIH_TABEL:
        zapisi_csv(
            vrni_pomozne_tabele(mapping, ime_kolicine),
            [_id_kolicine(ime_kolicine), ime_kolicine],
            f"{DATA_OBDELANI_DIRECTORY}/{ime_tabele}.csv"
        )


if __name__ == '__main__':
    main()
