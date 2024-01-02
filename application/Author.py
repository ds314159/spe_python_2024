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
