import requests
import re
import os
import csv
from orodja import (
    pripravi_imenik,
    shrani_spletno_stran,
    vsebina_datoteke,
    zapisi_csv,
    zapisi_json
)
from utils import (
    get_OS,
    get_proizvajalca,
    stevilo_dni_od_danasnjega_dneva,
    MOZNE_VREDNOSTI_SSDja
)

DATA_RAW_DIRECTORY = 'podatki_raw'  # mapa, v katero bomo shranili podatke
VSILI_PRENOS_SPLETNE_STRANI = False  # True, če želimo na novo downloadati raw podatke; False sicer
STEVILO_STRANI = 19  # Preveril ročno
# Datum branja podatkov. Potreboval ga bom za računanje, čez približno koliko bi dni bi napravo dostavili
GIGABYTE_TO_TERABYTE = 1024

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


def _ime_raw_strani(st_strani):
    return os.path.join(DATA_RAW_DIRECTORY, f"nuc{st_strani}.html")


def get_ssd(opis_naprave):
    def _convert_digit_to_ssd(ssd_parsed_digit):
        return ssd_parsed_digit*GIGABYTE_TO_TERABYTE if ssd_parsed_digit in (1, 2) else ssd_parsed_digit
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
            ssd = 'unknown'
        return ssd
    return 'unknown'


def get_ram(opis_naprave):
    opis_naprave = opis_naprave.lower()
    if re.search(vzorec_ram_stevilka_pred_besedo, opis_naprave):
        ram_raw = vzorec_ram_stevilka_pred_besedo.search(opis_naprave).groupdict("ram").get("ram")
        return int(re.sub("[^0-9]", "", ram_raw))
    elif re.search(vzorec_ram_stevilka_po_besedi, opis_naprave):
        ram_raw = vzorec_ram_stevilka_po_besedi.search(opis_naprave).groupdict("ram").get("ram")
        try:
            int(re.sub("[^0-9]", "", ram_raw))
        except ValueError:
            return 'unknown'
    else:  # re.search(r'barebone', opis_naprave) or re.search(r'(no ram|without ram)', opis_naprave) or not
        # re.search(r'(ram|ddr4)', opis_naprave)
        return 'unknown'


def izloci_podatke_nuca(blok):
    try:
        nuc = vzorec_nuca_s_ceno.search(blok).groupdict()
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
    nuc["proizvajalec"] = get_proizvajalca(nuc["opis"])
    nuc["OS"] = get_OS(nuc["opis"])
    nuc["ssd"] = get_ssd(nuc["opis"])
    nuc["ram"] = get_ram(nuc["opis"])
    print(nuc)
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


if __name__ == '__main__':
    main()
