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

DATA_RAW_DIRECTORY = 'podatki_raw'  # mapa, v katero bomo shranili podatke
VSILI_PRENOS_SPLETNE_STRANI = False  # True, če želimo na novo downloadati raw podatke; False sicer
STEVILO_STRANI = 19  # Preveril ročno

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

# ?P<Username>
vzorec_nuca_s_ceno = re.compile(
    r'<span class="a-size-medium a-color-base a-text-normal">(?P<opis>.*?)</span>'
    r'.*?<span class="a-offscreen">€(?P<cena>.*?)</span>'
)

vzorec_nuca_brez_cene = re.compile(
    r'<span class="a-size-medium a-color-base a-text-normal">(?P<opis>.*?)</span>'
)

vzorec_kupona = re.compile(
    r'<span class="a-size-base s-highlighted-text-padding aok-inline-block s-coupon-highlight-color">'
    r'Save €(?P<vrednost_kupona>.*?)'
    r'</span>'
)

vzorec_ocene = re.compile(
    r'<span class="a-icon-alt">(?P<ocena>.*?) out of 5 stars</span>'
)


def _url_spletne_strani(st_strani):
    return (
        "https://www.amazon.de/-/en/"
        f"s?k=nuc&page={st_strani}&language=en"
        "&crid=3VIZDYTXC6EN7&qid=1667900250&sprefix=n%2Caps%2C187&"
        f"ref=sr_pg_{st_strani}"
    )


def _ime_raw_strani(st_strani):
    return os.path.join(DATA_RAW_DIRECTORY, f"nuc{st_strani}.html")


def izloci_podatke_nuca(blok):
    # opis = vzorec_imena.search(blok)
    # print(opis)
    # print(nuc['cena'])
    try:
        nuc = vzorec_nuca_s_ceno.search(blok).groupdict()
    except AttributeError:
        # Empirično sem ugotovil, da nekateri NUC-i nimajo predpisane cene. To razrešim z try/except blokom
        nuc = vzorec_nuca_brez_cene.search(blok).groupdict()
        nuc.setdefault("cena", -1)
    if re.search(vzorec_kupona, blok):
        # print("Našel vzorec kupona!")
        nuc = dict(nuc, **vzorec_kupona.search(blok).groupdict())
    nuc.setdefault("vrednost_kupona", 0)  # NUC-om brez kupona pripišem, da ima kupon vrednost 0
    if re.search(vzorec_ocene, blok):
        nuc = dict(nuc, **vzorec_ocene.search(blok).groupdict())
    nuc.setdefault("ocena", -1)
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
        # print(type(blok.group(0)))
        # print(blok.span()[0], blok.span()[1])
        # print(vsebina[blok.span()[0]: blok.span()[1]])
        yield izloci_podatke_nuca(blok.group(0))


def main():
    """Funkcija izvede celoten del pridobivanja podatkov:
    1. Oglase prenese iz amazona
    2. Lokalno html datoteko pretvori v lepšo predstavitev podatkov
    3. Podatke shrani v csv datoteko
    """
    nuci = []
    STEVILO_STRANI_TEMP = 1
    for st_strani in range(1, STEVILO_STRANI + 1):
        for nuc in nuci_na_strani(st_strani):
            nuci.append(nuc)


if __name__ == '__main__':
    main()
