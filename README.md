# Système intelligent d'appariement Demandeurs / Offres d'emploi — ACPE

**Hackathon IndabaX Congo 2026** — Prototype de moteur d'appariement, recommandation et
tableau de bord décisionnel pour l'Agence Congolaise pour l'Emploi (ACPE).

## 🎯 Objectif

Mettre automatiquement en relation les demandeurs d'emploi et les offres disponibles à
l'aide de techniques de Data Science / NLP, produire un score de compatibilité explicable,
des recommandations Top-5 / Top-10, et un tableau de bord pour les conseillers ACPE.

## 📁 Structure du projet

```
.
├── data/                          # Jeux de données fournis (Excel)
│   ├── demandeurs.xlsx
│   ├── offres_acpe.xlsx
│   ├── offres_extensions.xlsx
│   └── appariement.xlsx           # Ground truth (évaluation uniquement)
├── src/
│   ├── data_prep.py                # Chargement, nettoyage, unification des données
│   ├── matching_engine.py          # Cœur du moteur (TF-IDF + règles métier)
│   ├── run_matching.py             # Génère les recommandations Top-10 pour tous les candidats
│   ├── evaluate.py                 # Precision@K / Recall@K / NDCG@K vs ground truth
│   ├── explain.py                  # Explique un score (termes contributeurs)
│   ├── search.py                   # Bonus 1 — recherche en langage naturel
│   └── skill_gap.py                # Bonus 2 — écarts de compétences
├── notebooks/
│   └── 01_exploration_nettoyage.ipynb   # EDA + documentation des traitements
├── dashboard/
│   └── app.py                      # Tableau de bord décisionnel (Streamlit)
├── outputs/
│   ├── recommandations_top10.csv   # candidate_id, rank, job_id, score
│   ├── recommandations_top5.csv
│   ├── evaluation_metrics.csv
│   └── eda_*.png                   # Graphiques d'exploration
├── reports/
│   ├── METHODOLOGIE_moteur_appariement.md
│   └── Rapport_Hackathon_IndabaX2026.docx
├── requirements.txt
└── README.md
```

## 🚀 Installation

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Utilisation

### 1. Préparer et vérifier les données
```bash
cd src
python data_prep.py
```

### 2. Générer les recommandations (moteur d'appariement)
```bash
python run_matching.py
# -> outputs/recommandations_top10.csv et recommandations_top5.csv
```

### 3. Évaluer les performances (vs ground truth)
```bash
python evaluate.py
```

### 4. Expliquer une recommandation
```bash
python explain.py <id_demandeur>
```

### 5. Bonus 1 — Recherche en langage naturel
```bash
python search.py offres "développeur Python à Brazzaville"
python search.py candidats "comptable avec mobilité nationale"
```

### 6. Bonus 2 — Écarts de compétences
```bash
python skill_gap.py <id_demandeur> <id_offre>
```

### 7. Lancer le tableau de bord
```bash
cd ..
streamlit run dashboard/app.py
```

### 8. Explorer le notebook d'analyse
```bash
jupyter notebook notebooks/01_exploration_nettoyage.ipynb
```

## 🧠 Méthodologie (résumé)

Le moteur combine :
- **Similarité textuelle TF-IDF + cosinus** (93%) entre le profil du candidat et l'offre
  (intitulé, secteur, profil recherché, compétences)
- **Bonus de correspondance sectorielle** (7%) pour renforcer l'explicabilité métier

Les poids ont été choisis après une **étude d'ablation** comparant plusieurs configurations
sur le ground truth fourni — voir `reports/METHODOLOGIE_moteur_appariement.md` pour le détail
et la justification complète.

## 📊 Résultats (évaluation sur les 41 298 candidats)

| Métrique | @5 | @10 |
|---|---|---|
| Precision | 0.333 | 0.201 |
| Recall | 0.556 | 0.669 |
| NDCG | 0.544 | 0.596 |

## ✨ Fonctionnalités bonus

- **Bonus 1 — Recherche intelligente** (`src/search.py`, onglet dashboard) : recherche
  d'offres ou de candidats à partir d'une requête libre en français, sans correspondance
  exacte de mots-clés.
- **Bonus 2 — Analyse des écarts de compétences** (`src/skill_gap.py`, onglet dashboard) :
  pour une paire candidat/offre, liste les compétences requises non couvertes par le profil
  du candidat.

## ⚠️ Limites connues

- Le fichier d'offres principal (2 388 offres) ne contient pas de champ "compétences"
  détaillé — le Bonus 2 n'est pleinement exploitable que sur les 143 offres de l'extension
  (45 avec compétences renseignées).
- La mobilité géographique des candidats est déclarative (Oui/Non/Non déclaré), sans ville
  précise, ce qui limite le raisonnement géographique fin.
- Les taxonomies de secteur diffèrent partiellement entre les deux tables (61% de
  recouvrement exact), d'où le choix de la similarité textuelle comme signal principal.

## 👥 Équipe

LIKIBI NGOMA Daniel Archange

## 📧 Contact

indabax.congo@gmail.com (organisateurs du hackathon)
