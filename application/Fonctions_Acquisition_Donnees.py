import praw
import json
import xmltodict
import urllib.request as libreq
from urllib.parse import quote_plus
from datetime import datetime as dt
import os
import pandas as pd
from Classes import *



def charger_config_json(chemin):
    with open(chemin, 'r') as file:
        return json.load(file)


def initialiser_reddit(config):
    return praw.Reddit(client_id=config['REDDIT']['client_id'],
                       client_secret=config['REDDIT']['client_secret'],
                       user_agent=config['REDDIT']['user_agent'])


def recuperer_posts_reddit(reddit, mot_de_recherche, taille):
    return reddit.subreddit('all').search(query=mot_de_recherche, limit=taille)


def creer_dataframe_reddit(posts):
    data_reddit = [{
        'id_post_reddit': post.id,
        'titre': post.title,
        'auteur': post.author.name if post.author else 'N/A',
        'date': dt.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
        'texte': post.selftext,
        'url': post.url,
        'subreddit': post.subreddit.display_name,
        'upvotes': post.ups,
        'score': post.score,
        'nombre_commentaires': post.num_comments,
        'flairs': post.link_flair_text,
        'source': "reddit"
    } for post in posts]
    return pd.DataFrame(data_reddit)


def recuperer_articles_arxiv(sequence_de_recherche, taille):
    contenu = quote_plus(sequence_de_recherche) # contrairement à praw, dans xreddit il faut formater la sequence afin qu'il n'y ait pas d'espaces
    cible = 'all'
    cible_exclusion = 'ti'
    contenu_exclusion = 'monkey' # exemple insignifiant, juste pour tester la variable exclusion
    requete_arxiv = f"http://export.arxiv.org/api/query?search_query={cible}:{contenu}+ANDNOT+%28{cible_exclusion}:{contenu_exclusion}%29&start=0&max_results={taille}"
    with libreq.urlopen(requete_arxiv) as url:
        return xmltodict.parse(url.read())


def creer_dataframe_arxiv(parsed_xml):
    entries = parsed_xml['feed'].get('entry', [])
    if not isinstance(entries, list):  # Si un seul article, il ne sera pas sous forme de liste
        entries = [entries]

    data_arxiv = [{
        'titre': entry['title'],
        'auteur': entry['author']['name'] if isinstance(entry['author'], dict) else entry['author'][0]['name'],
        'co_auteurs': ', '.join([author['name'] for author in entry['author'][1:]]) if isinstance(entry['author'],
                                                                                                  list) and len(
            entry['author']) > 1 else None,
        'date': dt.strptime(entry['published'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
        'texte': entry['summary'],
        'url': entry['link'][0]['@href'] if isinstance(entry['link'], list) else entry['link']['@href'],
        'catégorie': 'cs',
        'source': 'arxiv'
    } for entry in entries]
    return pd.DataFrame(data_arxiv)


def appliquer_recherche(nom_corpus, mot_de_recherche, taille_par_source):
    config = charger_config_json('config.json')
    reddit = initialiser_reddit(config)

    posts_reddit = recuperer_posts_reddit(reddit, mot_de_recherche, taille_par_source)
    df_reddit = creer_dataframe_reddit(posts_reddit)

    parsed_xml = recuperer_articles_arxiv(mot_de_recherche, taille_par_source)
    df_arxiv = creer_dataframe_arxiv(parsed_xml)

    df_unified = pd.concat([df_arxiv, df_reddit], ignore_index=True, sort=False)
    df_unified['nombre_commentaires'] = df_unified['nombre_commentaires'].fillna(0)
    df_unified['co_auteurs'] = df_unified['co_auteurs'].fillna('Aucun')
    df_unified['texte'] = df_unified['texte'].str.replace('\n', ' ').str.strip()

    fichier_corpus = f"data/{nom_corpus}.csv"
    df_unified.to_csv(fichier_corpus, index=False, encoding='utf-8', sep='\t')

    corpus_articles = DocumentFactory.create_corpus(fichier_corpus, nom_corpus)
    corpus_articles.save(f"data/{nom_corpus}.pkl")

    return corpus_articles


# Exemple d'appel de la fonction
if __name__ == "__main__":
    nom_corpus = "python"
    mot_de_recherche = "python"
    taille_par_source = 100
    corpus_articles = appliquer_recherche(nom_corpus, mot_de_recherche, taille_par_source)


    ex = Corpus.load('data/python.pkl')


