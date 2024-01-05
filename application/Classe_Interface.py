import ipywidgets as widgets
from IPython.display import display, clear_output
from Fonctions_Acquisition_Donnees import *
import os

class Interface:
    def __init__(self):
        # Lors du choix d'un corpus de travail, ce choix est affecté à l'attribut corpus_courant de la classe interface
        self.corpus_courant = None
        # Sous corpus si choix de selection par date
        self.sous_corpus_courant_predate = None
        # Sous corpus si choix de selection par date
        self.sous_corpus_courant_postdate = None
        # Lors d'une recherche par séquence, le résultat de la recherche est affecté à l'attribut recherche_courante
        self.recherche_courante = None
        # sortie moteur recherche
        self.output_mr = widgets.Output()

        self.concordances = None
        self.current_page_concordancier = 1
        self.output_concordances = widgets.Output()
        self.bouton_page_suivante_concordances = widgets.Button(description='Page Suivante', button_style='success')
        self.bouton_page_precedente_concordances = widgets.Button(description='Page Précédente', button_style='warning')

    def charger_corpus(self, fichier):
        """
        Charge un corpus depuis un fichier.
        :param fichier: Chemin du fichier contenant le corpus.
        :return: Un objet Corpus chargé.
        """
        return Corpus.load(fichier)

    @property
    def corpus_courant(self):
        """
        Accesseur (getter) pour l'attribut corpus_courant.
        :return: L'objet Corpus actuellement chargé.
        """
        return self._corpus_courant

    @corpus_courant.setter
    def corpus_courant(self, value):
        """
        Modificateur (setter) pour l'attribut corpus_courant.
        :param value: Le nouveau corpus à définir comme corpus courant.
        """
        self._corpus_courant = value

    def lister_noms_corpus(self, directory="data"):
        """
        Liste les noms des corpus disponibles dans un répertoire.
        :param directory: Chemin du répertoire contenant les corpus, par défaut 'data'.
        :return: Une liste de noms de corpus.
        """
        return [f for f in os.listdir(directory) if f.endswith('.pkl')]

    def creer_interface_recherche_corpus(self):
        """
        Crée une interface utilisateur pour construire un corpus à partir d'une séquence de recherche.
        """
        style = {'description_width': 'initial'}
        layout = widgets.Layout(width='500px')

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

        nom_corpus_widget = widgets.Text(description='Nom de la recherche:', style=style, layout=layout)
        mot_cle_widget = widgets.Text(description='Séquence de recherche:', style=style, layout=layout)
        nombre_articles_widget = widgets.IntSlider(description='Volume extraction:', min=0, max=200, step=10, style=style, layout=layout)
        bouton_executer = widgets.Button(description='Exécuter', button_style='info', tooltip='Cliquer ici pour lancer la recherche', icon='search')
        output = widgets.Output()

        bouton_executer.on_click(on_bouton_executer_clicked)

        return widgets.VBox([nom_corpus_widget, mot_cle_widget, nombre_articles_widget, bouton_executer, output])

    def creer_interface_chargement_corpus(self):
        """
        Crée une interface utilisateur pour charger un corpus existant.
        """
        def on_bouton_charger_clicked(b):
            with output:
                clear_output(wait=True)
                try:
                    nom_corpus = liste_corpus_widget.value
                    chemin_complet = os.path.join("data", nom_corpus)
                    self.corpus_courant = self.charger_corpus(chemin_complet)
                    print(f"Corpus '{nom_corpus}' chargé avec succès.")
                except Exception as e:
                    print(f"Une erreur s'est produite lors du chargement: {e}")

        liste_corpus_widget = widgets.Select(options=self.lister_noms_corpus(), description='Choisir un corpus:', disabled=False)
        bouton_charger = widgets.Button(description='Charger le Corpus', disabled=False)
        output = widgets.Output()

        bouton_charger.on_click(on_bouton_charger_clicked)

        return widgets.VBox([liste_corpus_widget, bouton_charger, output])

    def construire_vision_ensemble_corpus(self):
        """
        Crée une interface utilisateur pour configurer et afficher une vision d'ensemble du corpus.
        """
        style = {'description_width': 'initial'}
        layout = widgets.Layout(width='400px')

        max_words_widget = widgets.IntSlider(value=200, min=10, max=500, step=10, description='Choisir le nombre de mots à afficher dans le nuage:', style=style,
                                             layout=layout)
        min_word_length_widget = widgets.IntSlider(value=0, min=0, max=10, step=1, description="Choisir la taille minimale d'un mot:",
                                                   style=style, layout=layout)
        background_color_widget = widgets.ColorPicker(value='pink', description='Choisir la couleur de fond de votre nuage', style=style,
                                                      layout=layout)
        bouton_vision_ensemble = widgets.Button(description='Afficher Vision d\'Ensemble', button_style='info',
                                                tooltip='Cliquer pour visualiser', icon='eye')
        output = widgets.Output()

        def on_bouton_vision_ensemble_clicked(b):
            with output:
                clear_output(wait=True)
                try:
                    if self.corpus_courant:
                        self.corpus_courant.vision_d_ensemble(max_words=max_words_widget.value,
                                                              min_word_length=min_word_length_widget.value,
                                                              background_color=background_color_widget.value)
                    else:
                        print("Aucun corpus n'est chargé actuellement.")
                except Exception as e:
                    print(f"Une erreur s'est produite: {e}")

        bouton_vision_ensemble.on_click(on_bouton_vision_ensemble_clicked)

        return widgets.VBox(
            [max_words_widget, min_word_length_widget, background_color_widget, bouton_vision_ensemble, output])


    def afficher_resultats_recherche(self):
        """Affiche les résultats de la recherche courante."""
        with self.output_mr:
            clear_output(wait=True)
            if self.recherche_courante is not None:
                # Affichage du texte de présentation
                nombre_resultats = len(self.recherche_courante)
                texte_explicatif = f"Les {nombre_resultats} résultats ayant le meilleur score par ordre décroissant de pertinence, appuyer sur le titre pour visualiser l'article:"
                print(texte_explicatif)
                for index, row in self.recherche_courante.iterrows():
                    label = widgets.Label(value=f"\nArticle d'index {index} et intitulé:")
                    bouton_doc = widgets.Button(description=row['Document'], layout=widgets.Layout(width='auto'))
                    bouton_doc.on_click(lambda b, idx=index: self.afficher_texte_document(idx))
                    display(label, bouton_doc)
            else:
                print("Aucun résultat de recherche à afficher.")

    def afficher_texte_document(self, index):
        """Affiche le texte du document à l'index spécifié et un bouton de retour."""
        with self.output_mr:
            clear_output(wait=True)
            try:
                doc = list(self.corpus_courant.id2doc.values())[index]
                print(f"Texte du document: {doc.texte}")
                bouton_retour = widgets.Button(description='Retour aux résultats', layout=widgets.Layout(width='auto'))
                bouton_retour.on_click(lambda b: self.afficher_resultats_recherche())
                display(bouton_retour)
            except Exception as e:
                print(f"Erreur lors de l'affichage du document: {e}")

    def construire_recherche_sequence_dans_corpus(self):
        """Crée une interface utilisateur pour effectuer une recherche dans le corpus courant."""
        style = {'description_width': 'initial'}
        layout = widgets.Layout(width='500px')

        sequence_recherche_widget = widgets.Text(description='Séquence de recherche:', style=style, layout=layout)
        nombre_resultats_widget = widgets.IntSlider(value=5, min=1, max=20, step=1, description='Nombre de résultats:',
                                                    style=style, layout=layout)
        bouton_rechercher = widgets.Button(description='Rechercher', button_style='info',
                                           tooltip='Cliquer pour rechercher', icon='search')

        def on_bouton_rechercher_clicked(b):
            with self.output_mr:
                clear_output(wait=True)
                try:
                    if self.corpus_courant:
                        resultats = self.corpus_courant.rechercher_documents(sequence_recherche_widget.value)
                        self.recherche_courante = resultats.head(nombre_resultats_widget.value)
                        self.afficher_resultats_recherche()
                    else:
                        print("Aucun corpus n'est chargé actuellement.")
                except Exception as e:
                    print(f"Une erreur s'est produite: {e}")

        bouton_rechercher.on_click(on_bouton_rechercher_clicked)

        return widgets.VBox([sequence_recherche_widget, nombre_resultats_widget, bouton_rechercher, self.output_mr])



    def afficher_page_concordances(self, concordances, page_num, results_per_page):
        with self.output_concordances:
            clear_output(wait=True)
            start = (page_num - 1) * results_per_page
            end = start + results_per_page
            page_concordances = concordances.iloc[start:end]
            display(page_concordances)

            # Gérer l'affichage des boutons de pagination
            self.bouton_page_precedente_concordances.disabled = page_num <= 1
            self.bouton_page_suivante_concordances.disabled = end >= len(concordances)

            if page_num > 1:
                display(self.bouton_page_precedente_concordances)

            if end < len(concordances):
                display(self.bouton_page_suivante_concordances)

    def construire_interface_concorde(self):
        style = {'description_width': 'initial'}
        layout = widgets.Layout(width='500px')

        expression_widget = widgets.Text(description='Expression:', style=style, layout=layout)
        contexte_widget = widgets.IntSlider(value=5, min=1, max=20, step=1, description='Taille du contexte:', style=style, layout=layout)
        results_per_page_widget = widgets.IntSlider(value=10, min=1, max=100, step=1, description='Résultats par page:', style=style, layout=layout)
        bouton_concorde = widgets.Button(description='Chercher Concordances', button_style='info', icon='search')

        def update_page(concordances, change):
            new_page = self.current_page_concordancier + change
            max_page = (len(concordances) - 1) // results_per_page_widget.value + 1
            if 1 <= new_page <= max_page:
                self.current_page_concordancier = new_page
                self.afficher_page_concordances(concordances, self.current_page_concordancier, results_per_page_widget.value)

        self.bouton_page_suivante_concordances.on_click(lambda b: update_page(self.concordances, 1))
        self.bouton_page_precedente_concordances.on_click(lambda b: update_page(self.concordances, -1))

        def on_bouton_concorde_clicked(b):
            with self.output_concordances:
                clear_output(wait=True)
                if self.corpus_courant:
                    self.concordances = self.corpus_courant.concorde(expression_widget.value, contexte_widget.value)
                    self.current_page_concordancier = 1
                    self.afficher_page_concordances(self.concordances, self.current_page_concordancier, results_per_page_widget.value)
                else:
                    print("Aucun corpus n'est chargé actuellement.")

        bouton_concorde.on_click(on_bouton_concorde_clicked)

        return widgets.VBox([expression_widget, contexte_widget, results_per_page_widget, bouton_concorde, self.output_concordances])

    def diviser_et_afficher_sous_corpus(self):
        style = {'description_width': 'initial'}
        layout = widgets.Layout(width='500px')

        date_widget = widgets.DatePicker(description='Choisir une date:', style=style, layout=layout)
        bouton_diviser = widgets.Button(description='Diviser Corpus', button_style='info', icon='cut')
        output_division = widgets.Output()

        def on_bouton_diviser_clicked(b):
            with output_division:
                clear_output(wait=True)
                if self.corpus_courant:
                    date_limite = date_widget.value
                    self.sous_corpus_courant_predate = self.corpus_courant.copier_et_filtrer_avant_date(date_limite)
                    self.sous_corpus_courant_postdate = self.corpus_courant.copier_et_filtrer_apres_date(date_limite)

                    # Afficher les deux sous-corpus
                    print("Sous-corpus avant la date limite:")
                    self.sous_corpus_courant_predate.vision_d_ensemble()
                    print("Sous-corpus après la date limite:")
                    self.sous_corpus_courant_postdate.vision_d_ensemble()
                else:
                    print("Aucun corpus n'est chargé actuellement.")

        bouton_diviser.on_click(on_bouton_diviser_clicked)

        return widgets.VBox([date_widget, bouton_diviser, output_division])
