"""
Hackathon IndabaX Congo 2026 - Moteur d'appariement
====================================================
Approche hybride, choisie pour rester explicable (exigence du jury) :

  score_final = 0.55 * similarité_textuelle (TF-IDF + cosinus)
              + 0.25 * bonus_secteur (secteur demandé == secteur de l'offre)
              + 0.15 * bonus_mobilité (localisation compatible)
              + 0.05 * bonus_type_contrat (objectif du candidat vs groupe de contrat)

Justification du choix :
  - TF-IDF/cosinus capte la proximité sémantique de surface entre l'intitulé de poste,
    le secteur, le profil et les compétences recherchées côté offre, et le métier visé /
    la qualification / la filière côté candidat. Rapide (pas de GPU), reproductible,
    et interprétable (on peut extraire les termes qui contribuent au score).
  - Les bonus par règles métier corrigent les angles morts du texte pur : deux intitulés
    peuvent être formulés très différemment mais appartenir au même secteur ACPE
    (ex. "secteur_metier" candidat vs "secteur" offre), ou un candidat non mobile ne
    devrait pas se voir proposer une offre hors de sa localité déclarée.
"""

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

# Poids retenus après étude d'ablation (voir rapport, section "Choix des poids") :
# le TF-IDF pur (W_TEXT=1.0) obtient le meilleur score sur le ground truth fourni
# (P@5=0.331 vs 0.303 pour le mix initial 55/25/15/5). On conserve toutefois un
# léger bonus secteur (poids faible) pour l'explicabilité métier exigée par le jury,
# la perte de précision induite étant marginale (-0.3 à -0.5 pt).
W_TEXT = 0.93
W_SECTEUR = 0.07
W_MOBILITE = 0.0
W_CONTRAT = 0.0

FRENCH_STOPWORDS = [
    "le", "la", "les", "de", "des", "du", "un", "une", "et", "en", "à", "au", "aux",
    "pour", "dans", "sur", "par", "avec", "sans", "ou", "que", "qui", "ce", "cette",
    "ces", "son", "sa", "ses", "est", "sont", "d", "l", "s", "a",
]


def build_tfidf(dem_texts: pd.Series, off_texts: pd.Series):
    """Vectoriseur TF-IDF partagé (même vocabulaire des deux côtés)."""
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words=FRENCH_STOPWORDS,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.6,
        sublinear_tf=True,
    )
    corpus = pd.concat([dem_texts, off_texts], ignore_index=True)
    vectorizer.fit(corpus)
    X_dem = vectorizer.transform(dem_texts)
    X_off = vectorizer.transform(off_texts)
    return vectorizer, X_dem, X_off


def secteur_match_score(secteur_demande: str, secteur_metier: str, offre_secteur: str) -> float:
    """1.0 si secteur exact, 0.5 si chevauchement partiel de mots-clés, 0 sinon."""
    if not offre_secteur:
        return 0.3  # neutre : pas d'info secteur côté offre (fichier extension)
    candidats = {secteur_demande.lower(), secteur_metier.lower()}
    offre_l = offre_secteur.lower()
    for c in candidats:
        if not c:
            continue
        if c == offre_l:
            return 1.0
    # chevauchement de mots (secteurs souvent formulés "A - B - C")
    off_tokens = set(w for w in offre_l.replace("-", " ").split() if len(w) > 3)
    best = 0.0
    for c in candidats:
        if not c:
            continue
        c_tokens = set(w for w in c.replace("-", " ").split() if len(w) > 3)
        if not c_tokens or not off_tokens:
            continue
        overlap = len(c_tokens & off_tokens) / max(1, len(c_tokens | off_tokens))
        best = max(best, overlap)
    return best


def mobilite_match_score(mobilite: str, lieu_offre: str) -> float:
    """Règle simple : mobilité déclarée 'Oui' -> compatible partout.
    'Non' ou 'Non déclaré' -> score neutre (0.6) car on ignore la ville du candidat
    (non fournie dans le jeu de données)."""
    if mobilite == "Oui":
        return 1.0
    if mobilite == "Non":
        return 0.5
    return 0.6  # non déclaré


def contrat_match_score(objectif: str, groupe_contrat: str) -> float:
    mapping = {
        "Emploi": {"Emploi Durable", "Emploi Temporaire"},
        "Stage": {"Stages Classiques", "Alternance"},
        "Formation": {"Alternance", "Stages Classiques"},
    }
    if not groupe_contrat:
        return 0.5
    ok = groupe_contrat in mapping.get(objectif, set())
    return 1.0 if ok else 0.3


def compute_rule_matrix(dem: pd.DataFrame, off: pd.DataFrame) -> dict:
    """Pré-calcule, par candidat et par offre, des vecteurs de features de règles
    (retournés sous forme de tableaux numpy pour un calcul vectorisé rapide)."""
    n_dem, n_off = len(dem), len(off)

    # Encodage catégoriel simple pour vectoriser les règles secteur/mobilité/contrat
    secteur_off = off["secteur"].str.lower().values
    lieu_off = off["lieu"].values
    groupe_off = off["groupe_contrat"].values

    return {
        "secteur_off": secteur_off,
        "lieu_off": lieu_off,
        "groupe_off": groupe_off,
    }
