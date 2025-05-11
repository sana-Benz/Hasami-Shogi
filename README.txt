# Projet Hasami Shogi – Intelligence Artificielle

Ce projet implémente le jeu Hasami Shogi avec plusieurs niveaux d'intelligence artificielle (IA) basés sur l'algorithme Minimax, avec ou sans élagage Alpha–Beta.

========================================
LIVRABLE : Ce projet est à remettre sous forme d'une archive ZIP contenant :
- Le rapport au format PDF
- Le code Python du jeu
- Le code R d’analyse statistique
- Le fichier CSV contenant les résultats des tournois
- Les images PNG générées par R (graphiques)
- Ce fichier README.txt
========================================

1. Lancement de l'interface
---------------------------
Le fichier principal est `interface.py`. Il permet de :
- Jouer à deux joueurs humains
- Jouer contre une IA
- Lancer une partie entre deux IA (spectateur)

Exécution :

Assurez-vous d'avoir Python 3 installé. Puis installez la bibliothèque suivante :

    pip install pygame

Lancez l'interface avec :

    python interface.py

Un menu apparaîtra permettant de configurer les niveaux d'IA et de lancer une partie.

2. Tournoi automatique entre IA
-------------------------------
Le fichier `selfplay_tournoi.py` lance un tournoi complet entre les différentes IA sans interface.

    python selfplay_tournoi.py

Ce script génère un fichier `match_results.csv` contenant :
- `ia_white` : niveau de l'IA qui joue blanc
- `ia_black` : niveau de l'IA qui joue noir
- `winner` : 1 = blanc, 2 = noir, 0 = nul

3. Structure des fichiers
-------------------------

- interface.py         : Interface utilisateur graphique
- hasami_shogi.py      : Logique du jeu et du plateau
- ia_shogi.py          : IA Minimax / Alpha–Beta / fonctions d'évaluation
- selfplay_tournoi.py  : Simulation automatique IA vs IA
- match_results.csv    : Résultats du tournoi (généré automatiquement)
- *.png                : Graphiques générés via R
- *.R                  : Script R pour analyse et visualisation
- rapport.pdf          : Rapport de projet complet

4. Niveaux d’IA
---------------

| Niveau | Évaluation        | Profondeur | Optimisation                          |
|--------|-------------------|------------|----------------------------------------|
| 1      | Naïve             | 2-3        | Minimax sans élagage                  |
| 2      | Naïve             | 4          | Alpha–Beta + cache                    |
| 3      | Avancée           | 4          | Alpha–Beta + move ordering            |
| 4      | Dynamique         | 3 à 5      | Alpha–Beta + pruneurs + heuristique  |

5. Dépendances
--------------

- Python 3.x
- pygame

Vous pouvez également utiliser ce fichier :

    pip install -r requirements.txt

6. Auteurs
----------

Projet réalisé par Omar Amaraa et Ben Slama Sana  
Encadré par Mme Élise Bonzon
