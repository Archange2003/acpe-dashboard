# Logos officiels (optionnel)

Le tableau de bord affiche par défaut des versions **stylisées** du logo ACPE et
des armoiries de la République du Congo (dessinées en SVG dans `branding.py`).

Pour utiliser les **vrais fichiers officiels**, ajoutez simplement ici deux images :

| Fichier attendu | Contenu | Où le trouver |
|---|---|---|
| `acpe_logo.png` | Logo officiel de l'ACPE | En haut de https://www.acpe.cg |
| `armoiries_congo.png` | Armoiries de la République du Congo | Page Wikipédia « Armoiries de la République du Congo » (image libre de droits, domaine des emblèmes d'État) |

Dès que ces deux fichiers sont présents dans ce dossier (mêmes noms exacts,
sensible à la casse), le tableau de bord les détecte automatiquement au
prochain chargement — aucune modification de code nécessaire.

Formats acceptés : `.png`, `.jpg` (renommez simplement l'extension dans le nom
de fichier ci-dessus si besoin, ex. `acpe_logo.jpg`, et ajustez la ligne
correspondante dans `branding.py` si vous changez le format).
