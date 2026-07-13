"""
Hackathon IndabaX Congo 2026 - Préparation des données
=======================================================
Charge, nettoie et unifie les jeux de données :
  - Demandeurs d'emploi
  - Offres d'emploi (fichier principal + extension)
  - Appariement de référence (ground truth)

Produit deux tables propres : demandeurs (41 298 lignes) et offres (2 678 lignes),
chacune avec un champ texte unifié utilisé par le moteur d'appariement.
"""

import re
import unicodedata
import pandas as pd

import os
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def clean_text(x) -> str:
    """Nettoyage léger : minuscule, accents conservés (le français en a besoin),
    espaces multiples supprimés, valeurs vides normalisées."""
    if pd.isna(x):
        return ""
    x = str(x).strip()
    if x.lower() in {"nan", "none", "non déclaré", "non déclaree", "aucun", "aucune", ""}:
        return ""
    x = unicodedata.normalize("NFKC", x)
    x = re.sub(r"\s+", " ", x)
    return x.strip()


def build_texte_profil(r: dict) -> str:
    """Construit le champ texte unifié et pondéré à partir d'un profil candidat
    (dict ou ligne de DataFrame avec les mêmes clés que load_demandeurs())."""
    parts = []
    parts += [r.get("Métier visé / Qualification visée", "")] * 3
    parts += [r.get("qualification_metier", "")] * 3
    parts += [r.get("Secteur demandé", "")] * 2
    parts += [r.get("secteur_metier", "")] * 2
    parts += [r.get("Filière / Spécialité", "")] * 2
    parts += [r.get("Qualification", "")]
    parts += [r.get("Secteur d'activité", "")]
    parts += [r.get("Diplome", "")]
    parts += [r.get("niveau_etude", "")]
    return " ".join(p for p in parts if p)


def build_texte_offre(r: dict) -> str:
    """Construit le champ texte unifié et pondéré à partir d'une offre
    (dict ou ligne de DataFrame avec les mêmes clés que load_offres())."""
    parts = []
    parts += [r.get("intitule", "")] * 3
    parts += [r.get("secteur", "")] * 2
    parts += [r.get("profil", "")] * 2
    parts += [r.get("competences", "")] * 2
    parts += [r.get("description", "")]
    parts += [r.get("type_contrat", "")]
    return " ".join(p for p in parts if p)


def load_demandeurs() -> pd.DataFrame:
    df = pd.read_excel(f"{DATA_DIR}/demandeurs.xlsx")
    df.columns = [c.strip() for c in df.columns]
    df = df.drop(columns=["offre_pertinente"], errors="ignore")  # colonne 100% vide

    text_cols = [
        "Qualification", "Secteur d'activité", "Diplome", "niveau_etude",
        "qualification_metier", "secteur_metier", "Filière / Spécialité",
        "Secteur demandé", "Métier visé / Qualification visée",
    ]
    for c in text_cols:
        df[c] = df[c].apply(clean_text)

    df["Genre"] = df["Genre"].apply(clean_text)
    df["Objectif"] = df["Objectif"].apply(clean_text)
    df["Mobilité géographique"] = df["Mobilité géographique"].apply(clean_text)

    # Age : bornage raisonnable (16-65) contre erreurs de saisie
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df.loc[(df["Age"] < 14) | (df["Age"] > 70), "Age"] = pd.NA

    # Champ texte unifié pour le NLP, avec pondération par répétition
    # des champs les plus discriminants (métier visé, secteur demandé, qualification)
    df["texte_profil"] = df.apply(lambda r: build_texte_profil(r.to_dict()), axis=1)
    df = df.rename(columns={"Matricule": "id_demandeur"})
    return df


def load_offres() -> pd.DataFrame:
    off1 = pd.read_excel(f"{DATA_DIR}/offres_acpe.xlsx")
    off1.columns = [c.strip() for c in off1.columns]
    off1 = off1.rename(columns={
        "Référence offre": "id_offre",
        "Intitule": "intitule",
        "Secteur activité": "secteur",
        "Entreprise": "entreprise",
        "Type d'entreprise": "type_entreprise",
        "Lieu": "lieu",
        "Groupe de contrat": "groupe_contrat",
        "Type contrat": "type_contrat",
        "Date de publication": "date_publication",
    })
    off1 = off1.drop(columns=["Poste"], errors="ignore")
    off1["description"] = ""
    off1["profil"] = ""
    off1["competences"] = ""

    off2 = pd.read_excel(f"{DATA_DIR}/offres_extensions.xlsx")
    off2.columns = [c.strip() for c in off2.columns]
    off2 = off2.rename(columns={
        "Référence": "id_offre",
        "Intitulé": "intitule",
        "Type Contrat": "type_contrat",
        "Entreprise": "entreprise",
        "Description": "description",
        "Profil": "profil",
        "Compétences": "competences",
    })
    for c in ["secteur", "type_entreprise", "lieu", "groupe_contrat", "date_publication"]:
        off2[c] = ""

    cols = ["id_offre", "intitule", "secteur", "entreprise", "type_entreprise",
            "lieu", "groupe_contrat", "type_contrat", "date_publication",
            "description", "profil", "competences"]

    # Les 143 offres de l'extension partagent leur id_offre avec le fichier principal
    # (mêmes références) mais apportent des champs enrichis (description/profil/compétences)
    # absents du fichier principal -> fusion par id_offre plutôt que simple concaténation,
    # pour ne pas perdre cette information.
    off1["date_publication"] = off1["date_publication"].astype(str)
    enrich_cols = ["id_offre", "description", "profil", "competences"]
    offres = off1[cols].merge(
        off2[enrich_cols], on="id_offre", how="left", suffixes=("", "_ext")
    )
    for c in ["description", "profil", "competences"]:
        offres[c] = offres[c].where(offres[c].astype(str).str.len() > 0, offres[f"{c}_ext"])
        offres = offres.drop(columns=[f"{c}_ext"])

    # Offres de l'extension dont l'id_offre n'existe PAS dans le fichier principal (aucune ici,
    # mais on couvre le cas pour rester robuste si les jeux de données évoluent)
    new_off2 = off2[~off2["id_offre"].isin(off1["id_offre"])].copy()
    if len(new_off2):
        for c in ["secteur", "type_entreprise", "lieu", "groupe_contrat", "date_publication"]:
            new_off2[c] = ""
        offres = pd.concat([offres, new_off2[cols]], ignore_index=True)

    offres["date_publication"] = offres["date_publication"].astype(str)

    text_cols = ["intitule", "secteur", "entreprise", "lieu", "type_contrat",
                 "description", "profil", "competences"]
    for c in text_cols:
        offres[c] = offres[c].apply(clean_text)

    offres = offres.drop_duplicates(subset="id_offre").reset_index(drop=True)

    offres["texte_offre"] = offres.apply(lambda r: build_texte_offre(r.to_dict()), axis=1)
    return offres


def load_ground_truth() -> pd.DataFrame:
    gt = pd.read_excel(f"{DATA_DIR}/appariement.xlsx")
    gt.columns = [c.strip() for c in gt.columns]
    return gt


if __name__ == "__main__":
    dem = load_demandeurs()
    off = load_offres()
    gt = load_ground_truth()
    print("Demandeurs :", dem.shape)
    print("Offres     :", off.shape)
    print("Ground truth:", gt.shape)
    dem.to_parquet("../outputs/demandeurs_clean.parquet")
    off.to_parquet("../outputs/offres_clean.parquet")
    gt.to_parquet("../outputs/ground_truth.parquet")
    print("Exemple texte profil:", dem["texte_profil"].iloc[0])
    print("Exemple texte offre :", off["texte_offre"].iloc[0])
