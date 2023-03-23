# NUC Computer Analysis

I will be studying NUC (Next Unit of Computing) computers on the [amazon.de](https://www.amazon.de/s?k=nuc&page=2&language=en&crid=3VIZDYTXC6EN7&qid=1666151008&sprefix=n%2Caps%2C187&ref=sr_pg_2).
I will be analyzing 400 computers that appear in the search results when searching for the term nuc.

The table **obdelani_podatki/nuci.csv** contains the following information:
* Its ID (string)
* The description with which the NUC is presented on Amazon (`string`)
* The price (`float`)
* The value of the coupon that can be redeemed when purchasing the device (`float`)
* The SSD of the computer (extracted with regular expressions from the description) (`int`)
* The RAM of the computer (extracted with regular expressions from the description) (`int`)
* The rating (`float`)
* Whether the NUC is sponsored (`bool`)
* The manufacturer of the computer (`string`)
* The operating system of the computer (extracted with regular expressions from the description) (`string`)

The data is organized in the following way in the other auxiliary files:

In the file **obdelani_podatki/operacijski_sistem.csv**:
* ID of the operating system
* Name of the operating system

In the file **obdelani_podatki/proizvajalci.csv**:
* ID of the NUC producer
* Name of the NUC producer

In the file **obdelani_podatki/ram.csv** se nahajajo:
* ID of the RAM
* Quantity of RAM under this ID

In the file **obdelani_podatki/ssd.csv** se nahajajo:
* ID of the SSD
* Quantity of SSD under this ID

Working hypotheses:
* At a similar price, are Intel's NUCs (which are supposed to be the leaders in this category) comparable to the others? How many computers does intel sell compared to all other manufacturers?
* How does the price of a NUC increase with increasing RAM and SSD?
* How does delivery time vary between computers? How does delivery time affect its rating?
* How are the various data attributes (price, coupon value, number of ratings, delivery time, ...) correlated with each other?
