import praw
import json
import xmltodict
import urllib.request as libreq
from datetime import datetime as dt
import os
import stat
import pandas as pd
from Corpus import Corpus as Cor
from Document import *
nom_corpus  = 'recherche1'
mot_de_recherche = 'web'
taille_par_source = 100
def appliquer_recherche(nom_corpus, mot_de_recherche, taille_par_source):
    import praw
    import json
    import xmltodict
    import urllib.request as libreq
    from datetime import datetime as dt
    import os
    import stat
    import pandas as pd
    from Corpus import Corpus as Cor
    from Document import DocumentFactory, Document, ArxivDocument, RedditDocument

    with open('config.json', 'r') as file:
        config = json.load(file)

    reddit_client_id = config['REDDIT']['client_id']

    reddit_client_secret = config['REDDIT']['client_secret']

    reddit_user_agent = config['REDDIT']['user_agent']

    with libreq.urlopen('http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1') as url:
        r = url.read()

    # instance reddit
    reddit = praw.Reddit(client_id=reddit_client_id,
                         client_secret=reddit_client_secret,
                         user_agent=reddit_user_agent)


    # ********************************** Acquisition données REDDIT ********************************************************
    reddit_recherche = reddit.subreddit('all').search(query=mot_de_recherche, limit=taille_par_source)


    data_reddit = []
    for post in reddit_recherche:
        data_reddit.append({
            'id_post_reddit': post.id,
            'titre': post.title,
            'auteur': post.author.name if post.author else 'N/A',
            'date': dt.utcfromtimestamp(post.created_utc),
            'texte': post.selftext,
            'url': post.url,
            'subreddit': post.subreddit.display_name,
            'upvotes': post.ups,
            'score': post.score,
            'nombre_commentaires': post.num_comments,
            'flairs': post.link_flair_text,
            'source': "reddit"
        })

    df_reddit = pd.DataFrame(data_reddit)




    # ********************************** Acquisition données ARXIV *********************************************************
    cible = 'all'
    contenu = mot_de_recherche
    cible_exclusion = 'ti'
    contenu_exclusion = 'monkey'
    volume = taille_par_source
    requete_arxiv = f"http://export.arxiv.org/api/query?search_query={cible}:{contenu}+ANDNOT+%28{cible_exclusion}:{contenu_exclusion}%29&start=0&max_results={volume}"

    with libreq.urlopen(requete_arxiv) as url:
        r = url.read()

    parsed = xmltodict.parse(r)

    articles = parsed['feed']['entry']
    data_arxiv = []
    for entry in articles:
        # Gérer les cas où il n'y a qu'un seul auteur
        if isinstance(entry['author'], list):
            authors_list = [author['name'] for author in entry['author']]
        else:
            authors_list = [entry['author']['name']]

        # Séparation de l'auteur principal et des co-auteurs
        auteur_principal = authors_list[0]
        co_auteurs = ', '.join(authors_list[1:]) if len(authors_list) > 1 else None

        # Gérer les liens
        if isinstance(entry['link'], list):
            link_url = entry['link'][0]['@href']
        else:
            link_url = entry['link']['@href']

        data_arxiv.append({
            'titre': entry['title'],
            'auteur': auteur_principal,
            'co_auteurs': co_auteurs,
            'date': dt.strptime(entry['published'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
            'texte': entry['summary'],
            'url': link_url,
            'catégorie': 'cs',
            'source': 'arxiv'
        })

    # Convertir les données en DataFrame
    df_arxiv = pd.DataFrame(data_arxiv)


    # ********************************** Fusion et traitement initial des données des deux sources *************************

    df_unified = pd.concat([df_arxiv, df_reddit], ignore_index=True, sort=False)

    # traitement pour affecter une valeur par defaut à des colonnes utiles

    df_unified['nombre_commentaires'] = df_unified['nombre_commentaires'].fillna(-1)
    df_unified['co_auteurs'] = df_unified['co_auteurs'].fillna('inexistant')

    # traitement pour épurer le texte et rajouter les colonnes nombre de mots et de phrases par contenu:

    df_unified['texte'] = df_unified['texte'].apply(lambda x: x.replace('\n', '') if isinstance(x, str) else x)
    df_unified["nombre_de_mots"] = df_unified['texte'].apply(lambda x: len(x.split(' ')) if isinstance(x, str) else 0)
    df_unified["nombre_de_phrases"] = df_unified['texte'].apply(lambda x: len(x.split('.')) if isinstance(x, str) else 0)
    df_unified = df_unified[df_unified['texte'].str.len() > 20]

    df_unified.to_csv(f"data/{nom_corpus}.csv", index=False, encoding='utf-8', sep='\t')
    st = os.stat(f"data/{nom_corpus}.csv")
    os.chmod(f"data/{nom_corpus}.csv", st.st_mode | stat.S_IWRITE | stat.S_IREAD)

    # récupérer le sac de mots et le stocker :

    sac_de_mots = ''.join(df_unified['texte'])

    with open(f"data/sac_de_mots_{nom_corpus}.txt", 'w', encoding='utf-8') as file:
        file.write(sac_de_mots)

    # récupérer notre enregistrement corpus (l'ensemble de nos docs)
    corpus_articles = DocumentFactory.create_corpus(f"data/{nom_corpus}.csv", nom_corpus)
    corpus_articles.save(f"data/{nom_corpus}.pkl")

    return corpus_articles

appliquer_recherche(nom_corpus, mot_de_recherche, taille_par_source)
corpus = Cor.load('data/recherche1.pkl')

print(len(corpus.id2doc))
