# ds-network-analysis

## File organization
1. report files, written in markdown, are in report-source/
2. the python ETL package is in src/
3. the python network analysis files are in py/
4. the data itself is in xxx?

## todo

1. decidere hashtag per ciascun gruppo (prima fase con valutazione umana seconda fase con correlazione e se hashtag correlato con >1 categoria, escluso) -> abbiamo gli hashtag per ciascun gruppo
    - esludere hashtags che compaiono una volta
    - ripetere algoritmo per i primi k figli di ogni categoria
Problemi: scaricare i tweet una volta sola. trovare migliore metodo di memorizzarli (csv) scrivere query corretta
2. Scaricare i tweet in un dataframe
3. classificarli per ciascuna delle 3 categorie
4. (quarta categoria)
5. allo stesso modo del numero 3, classificare gli utenti in ciascuna delle 3 categorie
6. da dataframe, costruire rete networkx (decidere cosa sono i link - retweet mentions follows)

### network
1. decidere quali dei 72 attributi di Twarc tenerci come proprietà dei nodi (o dei link)


### quarta categoria
1. usare hashtag di eventi o altri di tendenza per trovare utenti molto attivi (con *author.public_metrics.tweet_count*)
2. accedere ai loro hashtag usando *author.entities.description.hashtags*
3. tenerci solo gli utenti per cui non appare hashtag delle 3 categorie (già tutti trovati)
questi sono i **"Don't care"**
N.B. potremmo trovare altri campi per fare lo stesso lavoro.

15/06 
### algoritmo per categorizzare i tweets 
- query per hashtags-padre: fatto
- ricorsione sui k-figli: da fare 
- eliminare hashatgs da liste che hanno pochi count: da fare (elminare hashtags che hanno poco supporto)
- score alla lista per figli ripetuti su più liste: da fare  (calcolare score su quelli che hanno più supporto)

