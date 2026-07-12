"""
Explique un score de compatibilité en listant les termes (mots/bi-grammes) qui
contribuent le plus à la similarité cosinus TF-IDF entre un candidat et une offre,
ainsi que le statut du bonus secteur. Répond à l'exigence du guide :
"Les équipes devront expliquer la méthode de calcul utilisée ainsi que les
variables ayant contribué au score."
"""

import numpy as np
import pandas as pd

from data_prep import load_demandeurs, load_offres
from matching_engine import build_tfidf


def explain_candidate(candidate_id: str, top_n_offres: int = 5, top_n_termes: int = 6):
    dem = load_demandeurs()
    off = load_offres()
    vectorizer, X_dem, X_off = build_tfidf(dem["texte_profil"], off["texte_offre"])
    terms = np.array(vectorizer.get_feature_names_out())

    idx = dem.index[dem["id_demandeur"] == candidate_id]
    if len(idx) == 0:
        raise ValueError(f"Candidat {candidate_id} introuvable")
    i = idx[0]

    profil = dem.loc[i]
    print(f"Candidat : {candidate_id}")
    print(f"  Métier visé      : {profil['Métier visé / Qualification visée']}")
    print(f"  Secteur demandé  : {profil['Secteur demandé']}")
    print(f"  Diplôme          : {profil['Diplome']} ({profil['niveau_etude']})")
    print(f"  Mobilité         : {profil['Mobilité géographique']}")
    print()

    sim = (X_dem[i] @ X_off.T).toarray().ravel()
    order = np.argsort(-sim)[:top_n_offres]

    print(f"{'Rang':<5}{'Offre':<15}{'Intitulé':<30}{'Score texte':<12}")
    for rank, j in enumerate(order, 1):
        row_terms = (X_dem[i].multiply(X_off[j])).toarray().ravel()
        top_terms_idx = np.argsort(-row_terms)[:top_n_termes]
        top_terms = [terms[t] for t in top_terms_idx if row_terms[t] > 0]
        print(f"{rank:<5}{off.loc[j, 'id_offre']:<15}{off.loc[j, 'intitule'][:28]:<30}{sim[j]:<12.4f}")
        print(f"      termes contributeurs : {', '.join(top_terms) if top_terms else '(aucun recouvrement direct)'}")
        print(f"      entreprise: {off.loc[j,'entreprise']} | secteur offre: {off.loc[j,'secteur'] or '(non renseigné)'} | lieu: {off.loc[j,'lieu']}")
    print()


if __name__ == "__main__":
    import sys
    cid = sys.argv[1] if len(sys.argv) > 1 else "PPKOU2501080016340"
    explain_candidate(cid)
