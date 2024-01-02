from datetime import datetime
import pandas as pd
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

########################################################################################################################
class Author:

    def __init__(self, name):
        self.name = name
        self.ndoc = 0  # Nombre de documents publiés par l'auteur
        self.production = {}  # Dictionnaire des documents écrits par l'auteur

    def add(self, doc):
        """
        Ajoute un document à la production de l'auteur
        """
        self.ndoc += 1
        self.production[doc.titre] = doc

    def __str__(self):
        return f"{self.name} - {self.ndoc} document(s) publié(s)"

########################################################################################################################

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


########################################################################################################################
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

########################################################################################################################
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


########################################################################################################################
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
        corpus_articles = Corpus(nom_corpus)

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

########################################################################################################################

class Corpus:

    def __init__(self, nom):
        self.nom = nom
        self.authors = {}  # Dictionnaire des auteurs
        self.id2doc = {}  # Dictionnaire des documents
        self.ndoc = 0  # Comptage des documents
        self.naut = 0  # Comptage des auteurs
        self.texte_concatene = None # sera acquis au premier appel de la fonction search

    def add_document(self,source ,titre, auteur, date, url, texte, co_auteurs, nb_commentaires=0):
        # Créer une nouvelle instance de Document

        doc = DocumentFactory.create_document(source ,titre, auteur, date, url, texte, co_auteurs, nb_commentaires)

        # Ajouter le document à id2doc
        self.id2doc[titre] = doc

        # Incrémenter le comptage des documents
        self.ndoc += 1

        # Vérifier si l'auteur existe déjà dans authors
        if auteur not in self.authors:
            # Si l'auteur n'existe pas, créer une nouvelle instance et l'ajouter au dictionnaire
            current_auteur = Author(auteur)
            self.authors[auteur] = current_auteur
            self.naut += 1
        else:
            # Si l'auteur existe déjà, récupérer l'instance existante
            current_auteur = self.authors[auteur]

        # Utiliser la méthode "add" de l'instance pour ajouter le document à sa production
        current_auteur.add(doc)

    def __repr__(self):
        return f"Corpus '{self.nom}' contenant {self.ndoc} documents et {self.naut} auteurs."

    def __repr__html(self):
        # Commencer par une chaîne de caractères contenant le début de la table HTML
        html = f"<h3>Corpus: {self.nom}</h3>"
        html += "<table border='1'>"
        html += "<tr><th>Titre</th><th>Auteur</th><th>Date</th><th>URL</th><th>Extrait</th></tr>"

        # Pour chaque document, ajouter une ligne au tableau HTML
        for doc in self.id2doc.values():
            html += f"<tr><td>{doc.titre}</td><td>{doc.auteur}</td><td>{doc.date}</td><td><a href='{doc.url}'>Lien</a></td><td>{doc.texte[:100]}...</td></tr>"

        # Terminer la table HTML
        html += "</table>"

        # Retourner la chaîne de caractères HTML
        return html

    def documents_par_date(self, n):
        # Trier les documents par date puis par titre
        sorted_docs = sorted(self.id2doc.values(), key=lambda x: (x.date), reverse = True)

        # Afficher les n premiers documents triés
        for doc in sorted_docs[:n]:
            print(f"Titre: {doc.titre}, Date: {doc.date}, Auteur: {doc.auteur}")

    def documents_par_titre(self, n):
        # Trier les documents par date puis par titre
        sorted_docs = sorted(self.id2doc.values(), key=lambda x: (x.titre))

        # Afficher les n premiers documents triés
        for doc in sorted_docs[:n]:
            print(f"Titre: {doc.titre}, Date: {doc.date}, Auteur: {doc.auteur}")

    def documents_par_date_et_titre(self, n):
        # Trier les documents par date puis par titre
        sorted_docs = sorted(self.id2doc.values(), key=lambda x: (x.date, x.titre))

        # Afficher les n premiers documents triés
        for doc in sorted_docs[:n]:
            print(f"Titre: {doc.titre}, Date: {doc.date}, Auteur: {doc.auteur}")

    def save(self, filename):
        """
        Sauvegarde l'objet Corpus dans un fichier.

        Args:
            filename (str): Le nom du fichier où sauvegarder l'objet.
        """
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls, filename):
        """
        Charge un objet Corpus à partir d'un fichier.

        Args:
            filename (str): Le nom du fichier depuis lequel charger l'objet.

        Returns:
            Corpus: L'objet Corpus chargé.
        """
        with open(filename, 'rb') as file:
            return pickle.load(file)

    def concatener_textes(self):
        if self.texte_concatene is None:
            self.texte_concatene = ' '.join([str(doc.texte) if doc.texte is not None else '' for doc in self.id2doc.values()])

    def search(self, mot_clef):

        self.concatener_textes()

        # Utilisez re.findall pour trouver toutes les occurrences du mot-clé
        return re.findall(mot_clef, self.texte_concatene)

    def concorde(self, expression, taille_contexte):
        # s'ssurez-vous que les textes sont concaténés
        self.concatener_textes()

        # Trouver toutes les occurrences de l'expression
        pattern = re.compile(r'(.{{0,{0}}})({1})(.{{0,{0}}})'.format(taille_contexte, expression))
        matches = pattern.finditer(self.texte_concatene)

        # Créer un DataFrame pour stocker les résultats
        concordances = pd.DataFrame(columns=['contexte gauche', 'motif trouvé', 'contexte droit'])

        # Remplir le DataFrame avec les résultats
        for match in matches:
            concordances = concordances.append({
                'contexte gauche': match.group(1),
                'motif trouvé': match.group(2),
                'contexte droit': match.group(3)
            }, ignore_index=True)

        return concordances

    def nettoyer_texte(self, texte):
        """
        Nettoie le texte en appliquant plusieurs traitements.

        Args:
            texte (str): Le texte à nettoyer.

        Returns:
            str: Le texte nettoyé.
        """
        # s'assurer de bien transmettre une chaine de texte
        if not isinstance(texte, str):
            texte = str(texte)
        # suppression des nombres
        texte = re.sub(r'\d+', '', texte)

        # Conversion en minuscules
        texte = texte.lower()

        # Remplacement des sauts de ligne par des espaces
        texte = texte.replace('\n', ' ')

        # Suppression de la ponctuation
        # tous les caractères qui ne sont ni des lettres, ni des chiffres, ni des caractères de soulignement, ni des espaces (y compris les tabulations et les retours à la ligne). En pratique, cela revient principalement à sélectionner la ponctuation et les symboles spéciaux.
        texte = re.sub(r'[^\w\s]', '', texte)

        return texte

    def construire_vocabulaire(self):
        """
        Construit le vocabulaire à partir des textes de tous les documents du corpus.

        Returns:
            dict: Un dictionnaire avec chaque mot unique et son nombre d'occurrences.
        """
        vocabulaire = set()

        # Boucler sur chaque document et extraire les mots
        for doc in self.id2doc.values():
            # Nettoyer le texte (en utilisant la fonction nettoyer_texte si elle est définie)
            texte_nettoye = self.nettoyer_texte(doc.texte)

            # Séparer les mots en utilisant l'espace, la tabulation, et la ponctuation comme délimiteurs
            mots = re.findall(r'\b\w+\b', texte_nettoye)

            # Ajouter les mots au set vocabulaire
            vocabulaire.update(mots)

        # Convertir le set en dictionnaire avec le compte des occurrences
        vocabulaire_dict = {index: mot for index, mot in enumerate(vocabulaire)}


        return vocabulaire_dict

    def calculer_frequences(self, vocabulaire_dict):
        # Créer un dictionnaire pour stocker les fréquences des termes dans chaque document
        freq_par_doc = {doc.titre: {mot: 0 for mot in vocabulaire_dict.values()} for doc in self.id2doc.values()}

        for doc in self.id2doc.values():
            # Nettoyage et extraction des mots
            texte_nettoye = self.nettoyer_texte(doc.texte)
            mots = re.findall(r'\b\w+\b', texte_nettoye)

            # Compter les fréquences des mots pour ce document
            for mot in mots:
                if mot in freq_par_doc[doc.titre]:
                    freq_par_doc[doc.titre][mot] += 1

        # Transformer le dictionnaire en DataFrame pour une meilleure lisibilité
        freq_df = pd.DataFrame.from_dict(freq_par_doc, orient='index')

        return freq_df

    def calculer_frequences_2(self, vocabulaire_dict):
        # Créer un dictionnaire pour stocker les fréquences des termes dans chaque document
        freq_par_doc = {index: {mot: 0 for mot in vocabulaire_dict.values()} for index, doc in
                        enumerate(self.id2doc.values())}

        for index, doc in enumerate(self.id2doc.values()):
            # Nettoyage et extraction des mots
            texte_nettoye = self.nettoyer_texte(doc.texte)
            mots = re.findall(r'\b\w+\b', texte_nettoye)

            # Compter les fréquences des mots pour ce document spécifique
            for mot in mots:
                if mot in vocabulaire_dict.values():  # Assurez-vous que le mot est dans le vocabulaire
                    freq_par_doc[index][mot] += 1

        # Transformer le dictionnaire en DataFrame pour une meilleure lisibilité
        freq_df = pd.DataFrame.from_dict(freq_par_doc, orient='index')

        return freq_df

    def vectoriser_documents(self):
        """
        Vectorise les documents du corpus en utilisant TF-IDF.
        """
        # Assurez-vous que les textes sont concaténés
        self.concatener_textes()

        # Initialiser le vectoriseur TF-IDF
        self.vectorizer = TfidfVectorizer()

        # Créer une liste de tous les textes des documents
        documents = [str(doc.texte) if doc.texte is not None else '' for doc in self.id2doc.values()]

        # Vectoriser les documents
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

    def rechercher_documents(self, requete):
        """
        Recherche les documents pertinents basés sur une requête multi-mots.

        Args:
            requete (str): La requête de recherche entrée par l'utilisateur.

        Returns:
            DataFrame: Un DataFrame contenant les documents triés par pertinence.
        """
        # Vérifiez si les documents ont été vectorisés
        if not hasattr(self, 'tfidf_matrix'):
            self.vectoriser_documents()

        # Nettoyer et vectoriser la requête
        requete_vectorisee = self.vectorizer.transform([requete])

        # Calculer la similarité cosinus
        cos_similarities = cosine_similarity(requete_vectorisee, self.tfidf_matrix)

        # Récupérer les scores de similarité pour chaque document
        scores = cos_similarities[0]

        # Créer un DataFrame pour les résultats
        resultats = pd.DataFrame({
            'Document': [doc.titre for doc in self.id2doc.values()],
            'Score': scores
        })

        # Trier les résultats par score de similarité
        resultats_ordonnes = resultats.sort_values(by='Score', ascending=False)

        return resultats_ordonnes



