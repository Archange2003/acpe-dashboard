"""
Bonus 2 — Analyse des écarts de compétences (Skill Gap)
==========================================================
Pour une paire (candidat, offre) recommandée, identifie les compétences ou
qualifications requises par l'offre qui ne trouvent pas d'écho dans le profil
du candidat, afin d'orienter le demandeur d'emploi vers les compétences à
développer (exigence "Bonus 2" du guide).

Limite de données assumée : seules les 143 offres du fichier d'extension
contiennent un champ "Compétences" / "Profil" détaillé ; pour les offres du
fichier principal, l'analyse se limite à l'intitulé et au secteur.
"""

import re
import unicodedata
import pandas as pd

from data_prep import load_demandeurs, load_offres

STOP_TOKENS = {
    "et", "de", "des", "du", "la", "le", "les", "en", "un", "une", "à", "au",
    "aux", "pour", "dans", "sur", "avec", "sans", "ou", "d", "l", "bonne",
    "bon", "bons", "notions", "maitrise", "maîtrise", "connaissance",
    "connaissances", "aisance",
}


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text


def _tokens(text: str) -> set:
    text = _norm(text)
    return {t for t in re.findall(r"[a-z0-9]+", text) if t not in STOP_TOKENS and len(t) > 2}


def split_requirements(raw: str) -> list:
    """Découpe le champ Compétences/Profil en items individuels."""
    if not raw:
        return []
    parts = re.split(r"[;\n]", raw)
    if len(parts) == 1:
        parts = re.split(r",(?=\s*[A-ZÀ-Ü])", raw)  # virgule suivie d'une majuscule = nouvel item
    return [p.strip(" .") for p in parts if p.strip(" .")]


def skill_gap(candidate_id: str, job_id: str, dem: pd.DataFrame = None, off: pd.DataFrame = None,
              overlap_threshold: float = 0.34) -> dict:
    dem = dem if dem is not None else load_demandeurs()
    off = off if off is not None else load_offres()

    cand_row = dem[dem["id_demandeur"] == candidate_id]
    job_row = off[off["id_offre"] == job_id]
    if cand_row.empty or job_row.empty:
        raise ValueError("Candidat ou offre introuvable")
    cand_row, job_row = cand_row.iloc[0], job_row.iloc[0]

    candidate_tokens = _tokens(cand_row["texte_profil"])

    requirements = split_requirements(job_row["competences"]) + split_requirements(job_row["profil"])
    if not requirements:
        requirements = split_requirements(job_row["intitule"])  # repli minimal

    missing, covered = [], []
    for req in requirements:
        req_tokens = _tokens(req)
        if not req_tokens:
            continue
        overlap = len(req_tokens & candidate_tokens) / len(req_tokens)
        (covered if overlap >= overlap_threshold else missing).append(req)

    total = len(covered) + len(missing)
    compat_pct = round(100 * len(covered) / total, 1) if total else None

    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "intitule_offre": job_row["intitule"],
        "compatibilite_competences_pct": compat_pct,
        "competences_couvertes": covered,
        "competences_manquantes": missing,
    }


if __name__ == "__main__":
    import sys
    dem = load_demandeurs()
    off = load_offres()

    # Choisit par défaut la première offre de l'extension (celles avec compétences détaillées)
    default_job = off[off["competences"] != ""]["id_offre"].iloc[0]
    cid = sys.argv[1] if len(sys.argv) > 1 else dem["id_demandeur"].iloc[0]
    jid = sys.argv[2] if len(sys.argv) > 2 else default_job

    result = skill_gap(cid, jid, dem, off)
    print(f"Candidat {result['candidate_id']}  |  Offre {result['job_id']} — {result['intitule_offre']}")
    print(f"Compatibilité compétences : {result['compatibilite_competences_pct']}%")
    print("Compétences couvertes    :", ", ".join(result["competences_couvertes"]) or "(aucune)")
    print("Compétences manquantes   :", ", ".join(result["competences_manquantes"]) or "(aucune)")
