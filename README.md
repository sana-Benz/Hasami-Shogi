# Hasami Shogi

Un jeu de Hasami Shogi implémenté en Python avec Pygame.

## Description

Hasami Shogi est un jeu de stratégie japonais se jouant sur un plateau de 9x9 cases. Chaque joueur commence avec 9 pions alignés sur la première rangée de son côté. Le but est de capturer les pions adverses en les prenant en tenaille horizontalement ou verticalement.

## Installation

1. Assurez-vous d'avoir Python 3.7 ou supérieur installé sur votre système.
2. Clonez ce dépôt ou téléchargez les fichiers.
3. Installez les dépendances requises :
```bash
pip install -r requirements.txt
```

## Comment jouer

1. Lancez le jeu en exécutant :
```bash
python interface.py
```

2. Dans le menu principal, vous pouvez :
   - Cliquer sur "Jouer" pour commencer une partie
   - Cliquer sur "Options" pour modifier les règles du jeu
   - Cliquer sur "Quitter" pour fermer le jeu

3. Pendant la partie :
   - Cliquez sur un pion pour le sélectionner
   - Les cases où vous pouvez déplacer le pion seront mises en surbrillance
   - Cliquez sur une case valide pour déplacer le pion
   - Les pions capturés seront automatiquement retirés du plateau

## Règles du jeu

### Règles de base
- Les pions se déplacent horizontalement ou verticalement comme une tour aux échecs
- Un pion peut capturer un ou plusieurs pions adverses en les prenant en tenaille
- Un joueur perd s'il ne lui reste plus qu'un certain nombre de pions (seuil de défaite)
- Un joueur gagne s'il a un certain nombre de pions de plus que son adversaire (seuil d'écart de victoire)

### Options personnalisables
- Capture en diagonale : active ou désactive la capture des pions en diagonale
- Capture multiple dans les coins : active ou désactive la capture de plusieurs pions coincés dans un coin
- Seuil de défaite : nombre minimum de pions avant la défaite (1-4)
- Seuil d'écart de victoire : différence de pions nécessaire pour gagner (2-6)

## Structure du projet

- `hasami_shogi.py` : Contient la logique principale du jeu
- `interface.py` : Gère l'interface utilisateur et les menus
- `requirements.txt` : Liste des dépendances Python nécessaires

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request 