from Document import  DocumentFactory
import pickle
class Corpus:

    def __init__(self, nom):
        self.nom = nom
        self.authors = {}  # Dictionnaire des auteurs
        self.id2doc = {}  # Dictionnaire des documents
        self.ndoc = 0  # Comptage des documents
        self.naut = 0  # Comptage des auteurs

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
        return print(f"Corpus '{self.nom}' contenant {self.ndoc} documents et {self.naut} auteurs.")

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
