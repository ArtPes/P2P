# P2P 

## Napster (Directory Centralizzata)

Questa strategia prevede che i file di interesse siano già residenti nei peer e che vi sia un sistema di directory sul quale   ogni peer si registra, ogni peer comunica la lista dei file che pone in condivisione e ogni peer interessato ad un download     effettui una richiesta relativa a chi possiede tale file, ottenendo la lista degli IP dei peer dai quali può ottenere il       file. Il download avviene da parte dell’interessato che si comporta da client nei confronti di un singolo peer selezionato,     contenente il file, che si comporta da server. Il sistema di directory possiede le informazioni di tutti i file presenti nel   sistema distribuito. Considerando che mediante il P2P possono essere scambiati contenuti protetti da copyright, storicamente   questo approccio ha avuto parecchi problemi di natura legale in quanto identifica in modo chiaro chi metteva a disposizione     contenuti, mediante l’IP, e quale tipologia di contenuti venivano messi a disposizione, mediante la relativa descrizione.

### Prerequisites

Nel file _config.py_ impostare proprio IPv4 e IPv6 e della directory a cui connettersi

### Running

Eseguire dal terminale:
```
 cd P2P/Napster
 python3 main.py
```


## Gnutella (Directory Distribuita)
In questo sistema non esiste una directory centralizzata che tiene traccia dei file che i singoli peer mettono a disposizione. Ogni peer conosce un numero limitato di vicini iniziali, ed ha la possibilità di trovarne altri successivamente. Quando un peer decide di cercare un file, invia un messaggio QUER ai suoi vicini che, a seconda del valore del TTL (Time To Live) decideranno di inoltrarlo ai rispettivi vicini e così via, fino a  quando il messaggio non arriverà a un peer che possiede il file. Quest'ultimo provvederà a contattare il peer iniziale,  notificandogli la disponibilità del file in questione.

### Prerequisites

Nel file _config.py_ impostare  il proprio IPv4 e IPv6. Per funzionare il programma richiede che sul pc sia installato e attivo il DBMS MongoDB, inoltre occorre la libreria python _pymongo_ che consente al programma di interfacciarsi con il DB.

### Running

Eseguire dal terminale:
```
 sudo service mongd start
 cd P2P/GNutella
 python3 main2.py
```


## Authors :trollface:

* **ArtPes** - (https://github.com/ArtPes)
* **lovalova91** - (https://github.com/lovalova1991)
* **padovanl** - (https://github.com/padovanl)

See also the list of [contributors](https://github.com/ArtPes/P2P/graphs/contributors) who participated in this project.
