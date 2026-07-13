"""
Hackathon IndabaX Congo 2026 - Génération des recommandations
================================================================
Calcule, pour chaque candidat, un score de compatibilité avec toutes les offres,
puis exporte le Top-10 (qui contient le Top-5) au format demandé :
    candidate_id, rank, job_id, score

Traitement par lots (chunks) de candidats pour rester raisonnable en mémoire
(41 298 candidats x 2 531 offres ~ 104M paires).
"""

import re
import time
import numpy as np
import pandas as pd
from scipy import sparse

from data_prep import load_demandeurs, load_offres, load_ground_truth
from matching_engine import build_tfidf, W_TEXT, W_SECTEUR, W_MOBILITE, W_CONTRAT

import os
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
CHUNK = 500  # réduit (au lieu de 2000) pour limiter le pic mémoire sur serveurs à ressources limitées
TOP_K = 10


def normalize_secteur(x: str) -> str:
    if not x:
        return ""
    x = x.lower()
    x = re.sub(r"[-–,&/]", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def secteur_bonus_chunk(dem_codes_chunk: np.ndarray, dem_missing_chunk: np.ndarray,
                         off_codes: np.ndarray, off_missing: np.ndarray) -> np.ndarray:
    """Matrice (chunk x n_off) de bonus secteur, entièrement vectorisée (codes entiers) :
      - 1.0  si secteur candidat == secteur offre (même catégorie normalisée)
      - 0.3  si l'un des deux côtés n'a pas de secteur renseigné (neutre)
      - 0.15 si les deux sont renseignés mais différents (léger malus)
    """
    exact = dem_codes_chunk[:, None] == off_codes[None, :]
    missing = dem_missing_chunk[:, None] | off_missing[None, :]
    out = np.where(exact, 1.0, np.where(missing, 0.3, 0.15)).astype(np.float32)
    return out


def generate_recommendations(dem: pd.DataFrame, off: pd.DataFrame, top_k: int = TOP_K,
                              progress_callback=None) -> pd.DataFrame:
    """Calcule le Top-K de recommandations pour tous les candidats. Réutilisée par
    le script CLI (main) et par le dashboard (calcul à la volée si le CSV est absent)."""
    vectorizer, X_dem, X_off = build_tfidf(dem["texte_profil"], off["texte_offre"])

    dem_secteur_norm = pd.Series([
        normalize_secteur(a) or normalize_secteur(b)
        for a, b in zip(dem["Secteur demandé"], dem["secteur_metier"])
    ])
    off_secteur_norm = pd.Series([normalize_secteur(s) for s in off["secteur"]])

    all_secteurs = pd.concat([dem_secteur_norm, off_secteur_norm], ignore_index=True)
    codes, _ = pd.factorize(all_secteurs)
    dem_sect_codes = codes[: len(dem_secteur_norm)]
    off_sect_codes = codes[len(dem_secteur_norm):]
    dem_sect_missing = (dem_secteur_norm.values == "")
    off_sect_missing = (off_secteur_norm.values == "")

    n_dem, n_off = len(dem), len(off)
    off_ids = off["id_offre"].values
    dem_ids = dem["id_demandeur"].values

    rows = []
    for start in range(0, n_dem, CHUNK):
        end = min(start + CHUNK, n_dem)
        sim = (X_dem[start:end] @ X_off.T).toarray().astype(np.float32)

        sect_bonus = secteur_bonus_chunk(
            dem_sect_codes[start:end], dem_sect_missing[start:end],
            off_sect_codes, off_sect_missing,
        )

        score = W_TEXT * sim + W_SECTEUR * sect_bonus
        score = np.clip(score, 0, 1)

        k = min(top_k, n_off)
        part = np.argpartition(-score, k - 1, axis=1)[:, :k]
        for local_i in range(end - start):
            idxs = part[local_i]
            sc = score[local_i, idxs]
            order = np.argsort(-sc)
            idxs_sorted = idxs[order]
            sc_sorted = sc[order]
            cid = dem_ids[start + local_i]
            for rank, (idx, s) in enumerate(zip(idxs_sorted, sc_sorted), start=1):
                rows.append((cid, rank, off_ids[idx], round(float(s), 4)))

        if progress_callback:
            progress_callback(end, n_dem)

    return pd.DataFrame(rows, columns=["candidate_id", "rank", "job_id", "score"])


def main():
    t0 = time.time()
    print("Chargement des données...")
    dem = load_demandeurs()
    off = load_offres()
    gt = load_ground_truth()
    print(f"  {len(dem)} demandeurs, {len(off)} offres  ({time.time()-t0:.1f}s)")

    print("Calcul des scores par lots + extraction Top-10...")

    def _log(end, n_dem):
        if (end // CHUNK) % 5 == 0 or end == n_dem:
            print(f"  {end}/{n_dem} candidats traités  ({time.time()-t0:.1f}s)")

    reco = generate_recommendations(dem, off, top_k=TOP_K, progress_callback=_log)
    reco.to_csv(f"{OUT_DIR}/recommandations_top10.csv", index=False)
    reco[reco["rank"] <= 5].to_csv(f"{OUT_DIR}/recommandations_top5.csv", index=False)
    print(f"Terminé en {time.time()-t0:.1f}s. Fichiers écrits dans {OUT_DIR}/")
    print(reco.head(15))


if __name__ == "__main__":
    main()
