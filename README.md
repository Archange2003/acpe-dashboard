# Système intelligent d'appariement — ACPE (Hackathon IndabaX Congo 2026)

Tableau de bord décisionnel pour l'appariement demandeurs d'emploi / offres d'emploi.

## Déploiement

Ce dépôt est prêt pour Streamlit Community Cloud :
- **Fichier principal** : `dashboard/app.py`
- **Dépendances** : `requirements.txt`

Le dashboard calcule automatiquement les recommandations au premier chargement
(~30-60 secondes selon les ressources), aucun fichier pré-calculé n'est requis.

## Structure

```
data/         # Jeux de données (demandeurs, offres, ground truth)
src/          # Moteur d'appariement, recherche, skill gap
dashboard/    # Application Streamlit
requirements.txt
```

## Exécution locale

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```
