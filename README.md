# Projet Hasami Shogi – Intelligence Artificielle

Ce projet implémente le jeu **Hasami Shogi** avec plusieurs niveaux d'intelligence artificielle (IA) basés sur l'algorithme Minimax, avec ou sans élagage Alpha–Beta.

---

## 🎮 Lancement de l'interface

Le fichier principal est `interface.py`. Il permet de :

- Jouer en mode 2 joueurs humains.
- Jouer contre une IA (avec choix du niveau).
- Lancer un match entre deux IA pour observer (mode spectateur).

### ▶️ Exécution :

Assurez-vous d'avoir `pygame` installé :

```bash
pip install pygame
```

Puis lancez simplement :

```bash
python interface.py
```

Un menu graphique apparaîtra. Depuis ce menu, vous pouvez :
- Choisir le mode de jeu (2 joueurs, joueur vs IA, IA vs IA),
- Configurer les niveaux des IA,
- Lancer une partie,
- Regarder une simulation entre deux IA.

---

## 🤖 Lancement d'un tournoi automatisé (IA vs IA)

Pour exécuter un tournoi complet entre les IA sans interface graphique, utilisez :

```bash
python selfplay_tournoi.py
```

Cela lancera 100 parties pour chaque duel entre IA de niveaux différents (6 duels en tout).

Un fichier `match_results.csv` sera généré contenant :
- `ia_white` : niveau de l'IA qui joue blanc,
- `ia_black` : niveau de l'IA qui joue noir,
- `winner` : 1 = blanc gagne, 2 = noir gagne, 0 = nul.

---

## 📁 Organisation des fichiers

| Fichier                  | Rôle                                                                 |
|--------------------------|----------------------------------------------------------------------|
| `interface.py`           | Interface utilisateur graphique (menu, parties, options)             |
| `hasami_shogi.py`        | Logique du jeu Hasami Shogi (plateau, règles, captures, affichage)   |
| `ia_shogi.py`            | Algorithmes IA (Minimax, Alpha–Beta, fonctions d'évaluation, etc.)   |
| `selfplay_tournoi.py`    | Simulation automatique de parties IA vs IA pour analyse statistique  |
| `match_results.csv`      | Résultats générés par les duels IA (créé après exécution du tournoi) |

---

## 🧠 Niveaux d’IA

| Niveau | Évaluation            | Profondeur | Optimisation IA                  |
|--------|------------------------|------------|----------------------------------|
| 1      | Simple (naïve)         | 2-3        | Minimax sans élagage             |
| 2      | Simple (naïve)         | 4          | Alpha–Beta + mémoïsation         |
| 3      | Avancée                | 4          | Alpha–Beta + move ordering       |
| 4      | Avancée dynamique      | 3 à 5      | Alpha–Beta + pruneurs + heuristique d’ouverture |

---

## ❓ Dépendances

- Python 3.x
- `pygame` (interface graphique)

---

## 📌 Auteurs

Projet réalisé par **Omar Amaraa** et **Ben Slama Sana**  
Encadré par **Mme Élise Bonzon**
