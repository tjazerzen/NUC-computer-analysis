# analiza NUC računalnikov

V okviru predmeta Programiranje 1 bom preučil računalnike NUC (Next Unit of Computing) na [nemškem Amazonu](https://www.amazon.de/-/en/s?k=nuc&page=2&crid=3VIZDYTXC6EN7&qid=1666151008&sprefix=n%2Caps%2C187&ref=sr_pg_2).
Zajel bom 400 računalnikov, ki se mi ob iskanju besede *nuc* pojavijo pod iskalnimi rezultati.

V tabeli **obdelani_podatki/nuci.csv** se nahajajo:
* Njegov ID (`string`)
* Opis, s katerim je NUC na amazonu predstavljen (`string`)
* Cena (`float`)
* Vrednost kupona, ki ga lahko unovčimo ob nakupu naprave (`float`)
* SSD računalnika (prebran z regularnimi izrazi iz opisa) (`int`)
* RAM računalnika (prebran z regularnimi izrazi iz opisa) (`int`)
* Ocena (`float`)
* Če je nuc sponzoriran `(bool)`
* Proizvajalec računalnika (`string`)
* Operacijski sistem računalnika (prebran z regularnimi izrazi iz opisa) (`string`)

Potem so v ostalih pomožnih datotekah podatki razporejeni na naslednji način. 

V datoteki **obdelani_podatki/operacijski_sistem.csv** se nahajajo:
* ID operacijskega sistema
* Ime operacijskega sistema

V datoteki **obdelani_podatki/proizvajalci.csv** se nahajajo:
* ID proizvajalca
* Ime proizvajalca

V datoteki **obdelani_podatki/ram.csv** se nahajajo:
* ID RAM-a
* Količina RAM-a pod tem ID-jem

V datoteki **obdelani_podatki/ssd.csv** se nahajajo:
* ID SSD-ja
* Količina SSD-ja pod tem ID-jem

Delovne hipoteze:
* So ob podobni ceni Intelovi NUC-i (ki naj bi bili vodilni znotraj te kategorije) primerljivi z ostalimi? 
  Koliko računalnikov proda intel na pram vsem ostalim proizvajalcem?
* Kako raste cena NUC-a ob večanju RAM-a in SSD-ja?
* Kako se čas dostave spreminja med računalniki? Kako čas dostave vpliva na njegovo oceno?
* Kako so razni podatkovni atributi (cena, vrednost kupona, število ocen, čas dostave, ...) med sabo korelirani?
