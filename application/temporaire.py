import ipywidgets as widgets
from IPython.display import display, clear_output
from Fonctions_Acquisition_Donnees import *
import os

def charger_corpus(fichier):
    """
    Charge un corpus depuis un fichier.

    :param fichier: Chemin du fichier contenant le corpus.
    :return: Un objet Corpus chargé.
    """
    return Corpus.load(fichier)

def lister_noms_corpus(directory="data"):
    """
    Liste les noms des corpus disponibles dans un répertoire.

    :param directory: Chemin du répertoire contenant les corpus.
    :return: Une liste de noms de corpus.
    """
    return [f for f in os.listdir(directory) if f.endswith('.pkl')]

def creer_interface_recherche_corpus():
    """
    Crée une interface utilisateur pour la recherche dans un corpus.

    Cette interface comprend des champs pour entrer le nom de la recherche, le mot-clé,
    et le nombre d'articles, ainsi qu'un bouton pour exécuter la recherche.
    """

    style = {'description_width': 'initial'}
    layout = widgets.Layout(width='500px')  # Définir une largeur fixe pour les widgets

    def on_bouton_executer_clicked(b):
        """
        Gère l'événement de clic sur le bouton d'exécution.

        :param b: Objet bouton (non utilisé dans la fonction).
        """
        with output:
            clear_output(wait=True)
            try:
                # Vérification des entrées et exécution de la recherche
                # ...
            except Exception as e:
                print(f"Une erreur s'est produite: {e}")

    # Définition des widgets pour l'interface
    nom_corpus_widget = widgets.Text(description='Nom de la recherche:', style=style, layout=layout)
    mot_cle_widget = widgets.Text(description='Séquence de recherche:', style=style, layout=layout)
    nombre_articles_widget = widgets.IntSlider(description='Volume extraction:', style=style, layout=layout, min=0, max=200, step=10)
    bouton_executer = widgets.Button(description='Exécuter', button_style='info', tooltip='Cliquer ici pour lancer la recherche', icon='search')
    output = widgets.Output()

    bouton_executer.on_click(on_bouton_executer_clicked)

    return widgets.VBox([nom_corpus_widget, mot_cle_widget, nombre_articles_widget, bouton_executer, output])

def creer_interface_chargement_corpus():
    """
    Crée une interface utilisateur pour charger un corpus existant.

    Cette interface comprend un menu déroulant pour sélectionner un corpus et un bouton pour charger le corpus sélectionné.
    """

    def on_bouton_charger_clicked(b):
        """
        Gère l'événement de clic sur le bouton de chargement.

        :param b: Objet bouton (non utilisé dans la fonction).
        """
        with output:
            clear_output(wait=True)
            try:
                # Chargement du corpus sélectionné
                # ...
            except Exception as e:
                print(f"Une erreur s'est produite lors du chargement: {e}")

    liste_corpus_widget = widgets.Select(options=lister_noms_corpus(), description='Choisir un corpus:')
    bouton_charger = widgets.Button(description='Charger le Corpus')
    output = widgets.Output()

    bouton_charger.on_click(on_bouton_charger_clicked)

    return widgets.VBox([liste_corpus_widget, bouton_charger, output])
