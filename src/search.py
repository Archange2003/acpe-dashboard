"""
Bonus 1 — Recherche intelligente en langage naturel
=====================================================
Permet de rechercher des offres ou des candidats à partir d'une requête libre,
sans correspondance exacte de mots-clés, en réutilisant la même logique TF-IDF
que le moteur d'appariement (cohérence de méthode, explicabilité commune).

Important (robustesse mémoire) : les deux index (offres / candidats) sont
construits paresseusement — un côté n'est jamais construit si l'utilisateur ne
recherche que dans l'autre. Sur un serveur à ressources limitées, construire
les deux index d'un coup (comme dans une version précédente) provoquait un
plantage mémoire (segmentation fault) dès la première recherche.

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

# Vocabulaire volontairement compact (unigrammes uniquement, pas de bigrammes,
# max_features réduit) pour rester léger en mémoire sur un serveur gratuit.
_VEC_KWARGS = dict(
    lowercase=True, stop_words=FRENCH_STOPWORDS, ngram_range=(1, 1),
    min_df=2, max_df=0.7, max_features=6000, sublinear_tf=True, dtype=np.float32,
)


class OffresSearchIndex:
    """Index de recherche pour les offres uniquement (construit à la demande)."""

    def __init__(self, off: pd.DataFrame = None):
        self.off = off if off is not None else load_offres()
        self.vec = TfidfVectorizer(**_VEC_KWARGS)
        self.X = self.vec.fit_transform(self.off["texte_offre"])

    def search(self, query: str, top_k: int = 10) -> pd.DataFrame:
        q = self.vec.transform([query])
        sim = (q @ self.X.T).toarray().ravel()
        order = np.argsort(-sim)[:top_k]
        res = self.off.iloc[order][["id_offre", "intitule", "entreprise", "secteur", "lieu", "type_contrat"]].copy()
        res.insert(0, "score", sim[order].round(4))
        return res.reset_index(drop=True)


class CandidatsSearchIndex:
    """Index de recherche pour les candidats uniquement (construit à la demande)."""

    def __init__(self, dem: pd.DataFrame = None):
        self.dem = dem if dem is not None else load_demandeurs()
        self.vec = TfidfVectorizer(**_VEC_KWARGS)
        self.X = self.vec.fit_transform(self.dem["texte_profil"])

    def search(self, query: str, top_k: int = 10) -> pd.DataFrame:
        q = self.vec.transform([query])
        sim = (q @ self.X.T).toarray().ravel()
        order = np.argsort(-sim)[:top_k]
        cols = ["id_demandeur", "Métier visé / Qualification visée", "Secteur demandé",
                "niveau_etude", "Mobilité géographique"]
        res = self.dem.iloc[order][cols].copy()
        res.insert(0, "score", sim[order].round(4))
        return res.reset_index(drop=True)


class SearchEngine:
    """Conservé pour compatibilité (usage en ligne de commande / notebooks) —
    construit les deux index à la demande (propriétés paresseuses). Le dashboard,
    lui, utilise directement OffresSearchIndex / CandidatsSearchIndex séparément
    pour rester le plus léger possible en mémoire sur un serveur gratuit."""

    def __init__(self, dem: pd.DataFrame = None, off: pd.DataFrame = None):
        self.dem = dem if dem is not None else load_demandeurs()
        self.off = off if off is not None else load_offres()
        self._off_index = None
        self._dem_index = None

    @property
    def off_index(self) -> OffresSearchIndex:
        if self._off_index is None:
            self._off_index = OffresSearchIndex(self.off)
        return self._off_index

    @property
    def dem_index(self) -> CandidatsSearchIndex:
        if self._dem_index is None:
            self._dem_index = CandidatsSearchIndex(self.dem)
        return self._dem_index

    def search_offres(self, query: str, top_k: int = 10) -> pd.DataFrame:
        return self.off_index.search(query, top_k)

    def search_candidats(self, query: str, top_k: int = 10) -> pd.DataFrame:
        return self.dem_index.search(query, top_k)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python search.py [offres|candidats] \"requête en langage naturel\"")
        sys.exit(1)

    mode, query = sys.argv[1], sys.argv[2]

    if mode == "offres":
        print(OffresSearchIndex().search(query).to_string(index=False))
    elif mode == "candidats":
        print(CandidatsSearchIndex().search(query).to_string(index=False))
    else:
        print("Mode inconnu : utiliser 'offres' ou 'candidats'")
