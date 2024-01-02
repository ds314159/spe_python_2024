from Classes import Corpus

ex = Corpus.load('data/python.pkl')

for _, doc in ex.id2doc.items():
    doc.afficher_infos()

print(len(ex.id2doc))