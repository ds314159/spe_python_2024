from datetime import datetime
import pandas as pd

import Corpus
from Corpus import *



class Document:

    def __init__(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
        self.url = url
        self.texte = texte


    def afficher_infos(self):
        return print(f"Titre: {self.titre}\nAuteur: {self.auteur}\nDate: {self.date}\nURL: {self.url}\nTexte: {self.texte}")

    def __str__(self):
        return self.titre



class RedditDocument(Document):

    def __init__(self, source, titre, auteur, date, url, texte, nb_commentaires):
        super().__init__(titre, auteur, date, url, texte)
        self.nb_commentaires = nb_commentaires
        self.type = source

    def get_nb_commentaires(self):
        return self.nb_commentaires

    def set_nb_commentaires(self, nb_commentaires):
        self.nb_commentaires = nb_commentaires

    def get_type(self):
        return self.type

    def afficher_infos(self):
        print(f"Source: {self.type}")
        super().afficher_infos()
        print(f"Nombre de commentaires: {self.nb_commentaires}")


class ArxivDocument(Document):

    def __init__(self, source, titre, auteur, date, url, texte, co_auteurs):
        super().__init__(titre, auteur, date, url, texte)
        self.co_auteurs = co_auteurs
        self.type = source

    def get_co_auteurs(self):
        return self.co_auteurs

    def set_co_auteurs(self, co_auteurs):
        self.co_auteurs = co_auteurs

    def get_type(self):
        return self.type

    def afficher_infos(self):
        print(f"Source: {self.type}")
        super().afficher_infos()
        print(f"Co-auteurs: {self.co_auteurs}" if self.co_auteurs else "Co_auteurs: aucun")



class DocumentFactory:

    @staticmethod
    def create_document(source,titre, auteur, date, url, texte, co_auteurs, nb_commentaires):
        if source == "reddit":
            return RedditDocument(source, titre, auteur, date, url, texte, nb_commentaires)
        elif source == "arxiv":
            return ArxivDocument(source, titre, auteur, date, url, texte, co_auteurs)
        else:
            raise ValueError(f"Type de document {source} non reconnu")

    def create_corpus(chemin_donnees_acquises, nom_corpus):
        # récupérer notre enregistrement corpus (l'ensemble de nos docs)
        docs = pd.read_csv(chemin_donnees_acquises, sep='\t')

        # instancier un objet Corpus pour y stocker sous forme d'instances d'autres objets les articles acquis
        corpus_articles = Corpus.Corpus(nom_corpus)

        for _, doc in docs.iterrows():
            corpus_articles.add_document(doc['source'],
                                         doc['titre'],
                                         doc['auteur'],
                                         doc['date'],
                                         doc['url'],
                                         doc['texte'],
                                         doc['co_auteurs'],
                                         doc['nombre_commentaires'])
        return corpus_articles


