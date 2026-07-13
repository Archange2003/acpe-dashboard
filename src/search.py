"""
Bonus 1 — Recherche intelligente en langage naturel
=====================================================
Permet de rechercher des offres ou des candidats à partir d'une requête libre,
sans correspondance exacte de mots-clés, en réutilisant le même vectoriseur
TF-IDF que le moteur d'appariement (cohérence de méthode, explicabilité commune).

Exemples :
    python search.py offres "développeur Python à Brazzaville"
    python search.py candidats "comptable avec mobilité nationale"
"""

import sys
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from data_prep import load_demandeurs, load_offres
from matching_engine import FRENCH_STOPWORDS


class SearchEngine:
    """Index TF-IDF réutilisable pour rechercher dans les offres ou les candidats.

    Accepte des DataFrames déjà chargés (dem, off) pour éviter de dupliquer les
    données en mémoire — important sur un serveur à ressources limitées, où
    charger une seconde copie complète des 41 298 candidats a été identifié
    comme cause de plantage mémoire (segmentation fault)."""

    def __init__(self, dem: pd.DataFrame = None, off: pd.DataFrame = None):
        self.dem = dem if dem is not None else load_demandeurs()
        self.off = off if off is not None else load_offres()

        # min_df=2 et max_features bornent la taille du vocabulaire (donc la mémoire),
        # cohérent avec le moteur d'appariement principal (matching_engine.build_tfidf)
        self.vec_off = TfidfVectorizer(
            lowercase=True, stop_words=FRENCH_STOPWORDS, ngram_range=(1, 2),
            min_df=2, max_df=0.7, max_features=20000, sublinear_tf=True, dtype=np.float32,
        )
        self.X_off = self.vec_off.fit_transform(self.off["texte_offre"])

        self.vec_dem = TfidfVectorizer(
            lowercase=True, stop_words=FRENCH_STOPWORDS, ngram_range=(1, 2),
            min_df=2, max_df=0.7, max_features=20000, sublinear_tf=True, dtype=np.float32,
        )
        self.X_dem = self.vec_dem.fit_transform(self.dem["texte_profil"])

    def search_offres(self, query: str, top_k: int = 10) -> pd.DataFrame:
        q = self.vec_off.transform([query])
        sim = (q @ self.X_off.T).toarray().ravel()
        order = np.argsort(-sim)[:top_k]
        res = self.off.iloc[order][["id_offre", "intitule", "entreprise", "secteur", "lieu", "type_contrat"]].copy()
        res.insert(0, "score", sim[order].round(4))
        return res.reset_index(drop=True)

    def search_candidats(self, query: str, top_k: int = 10) -> pd.DataFrame:
        q = self.vec_dem.transform([query])
        sim = (q @ self.X_dem.T).toarray().ravel()
        order = np.argsort(-sim)[:top_k]
        cols = ["id_demandeur", "Métier visé / Qualification visée", "Secteur demandé",
                "niveau_etude", "Mobilité géographique"]
        res = self.dem.iloc[order][cols].copy()
        res.insert(0, "score", sim[order].round(4))
        return res.reset_index(drop=True)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python search.py [offres|candidats] \"requête en langage naturel\"")
        sys.exit(1)

    mode, query = sys.argv[1], sys.argv[2]
    engine = SearchEngine()

    if mode == "offres":
        print(engine.search_offres(query).to_string(index=False))
    elif mode == "candidats":
        print(engine.search_candidats(query).to_string(index=False))
    else:
        print("Mode inconnu : utiliser 'offres' ou 'candidats'")
