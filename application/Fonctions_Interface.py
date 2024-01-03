import ipywidgets as widgets
from IPython.display import display, clear_output
from Fonctions_Acquisition_Donnees import *
import os



def charger_corpus(fichier):
    # Utilisez ici votre méthode de chargement
    return Corpus.load(fichier)

def lister_noms_corpus(directory="data"):
    return [f for f in os.listdir(directory) if f.endswith('.pkl')]


def creer_interface_recherche_corpus():
    # Style pour les descriptions des widgets et layout pour la largeur
    style = {'description_width': 'initial'}
    layout = widgets.Layout(width='500px')  # Définir une largeur de 500px

    def on_bouton_executer_clicked(b):
        with output:
            clear_output(wait=True)
            try:
                if mot_cle_widget.value.strip() == '' or nom_corpus_widget.value.strip() == '':
                    print("Veuillez entrer un mot-clé de recherche et attribuer un nom au résultat de la recherche.")
                    return
                print(f"Recherche avec le mot-clé: '{mot_cle_widget.value}' pour {nombre_articles_widget.value} articles")
                resultat = appliquer_recherche(nom_corpus_widget.value, mot_cle_widget.value, nombre_articles_widget.value)
                display(resultat)
            except Exception as e:
                print(f"Une erreur s'est produite: {e}")



    nom_corpus_widget = widgets.Text(
        value='',
        description='Nom de la recherche:    ',
        disabled=False,
        style=style,
        layout=layout
    )

    mot_cle_widget = widgets.Text(
        value='',
        description='Séquence de recherche:',
        disabled=False,
        style=style,
        layout=layout
    )

    nombre_articles_widget = widgets.IntSlider(
        value=100,
        min=0,
        max=200,
        step=10,
        description='Volume extraction:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d',
        style=style,
        layout=layout
    )

    bouton_executer = widgets.Button(
        description='Exécuter',
        disabled=False,
        button_style='info',
        tooltip='Cliquer ici pour lancer la recherche',
        icon='search'
    )

    # Zone d'affichage des résultats
    output = widgets.Output()

    # Configuration des événements
    bouton_executer.on_click(on_bouton_executer_clicked)


    # Mise en page et affichage
    return widgets.VBox([nom_corpus_widget, mot_cle_widget, nombre_articles_widget, bouton_executer, output])


def creer_interface_chargement_corpus():
    # Définition de la fonction appelée lorsque le bouton est cliqué
    def on_bouton_charger_clicked(b):
        with output:
            clear_output(wait=True)
            try:
                nom_corpus = liste_corpus_widget.value
                chemin_complet = os.path.join("data", nom_corpus)
                corpus = charger_corpus(chemin_complet)
                print(f"Corpus '{nom_corpus}' chargé avec succès.")
                return corpus
            except Exception as e:
                print(f"Une erreur s'est produite lors du chargement: {e}")

    # Création des widgets
    liste_corpus_widget = widgets.Select(
        options=lister_noms_corpus(),
        description='Choisir un corpus:',
        disabled=False
    )

    bouton_charger = widgets.Button(
        description='Charger le Corpus',
        disabled=False
    )

    # Configuration de l'événement du bouton
    bouton_charger.on_click(on_bouton_charger_clicked)

    # Zone d'affichage des résultats et messages
    output = widgets.Output()

    # Affichage de l'interface

    return widgets.VBox([liste_corpus_widget, bouton_charger, output])