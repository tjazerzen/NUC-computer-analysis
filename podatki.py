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


NUC_FRONTPAGE_URL = 'https://www.amazon.de/s?k=nuc&page=2&language=en&crid=3VIZDYTXC6EN7&qid=1666151008&sprefix=n%2Caps%2C187&ref=sr_pg_2'
# mapa, v katero bomo shranili podatke
NUC_DIRECTORY = 'data'
# ime datoteke v katero bomo shranili glavno stran
FRONTPAGE_FILENAME = 'index_nuc.html'
# ime CSV datoteke v katero bomo shranili podatke
CSV_FILENAME = 'macki.csv'
VSILI_PRENOS = True


def main():
    """Funkcija izvede celoten del pridobivanja podatkov:
    1. Oglase prenese iz amazona
    2. Lokalno html datoteko pretvori v lepšo predstavitev podatkov
    3. Podatke shrani v csv datoteko
    """
    # Najprej v lokalno datoteko shranimo glavno stran
    shrani_spletno_stran(
        NUC_FRONTPAGE_URL,
        os.path.join(NUC_DIRECTORY, FRONTPAGE_FILENAME),
        vsili_prenos=VSILI_PRENOS,
    )


if __name__ == '__main__':
    main()

