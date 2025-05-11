"""
Ce script permet de lancer un tournoi automatique de parties de Hasami Shogi entre différentes IA de niveaux différents, sans interface graphique.

Fonctionnalités principales :
- Utilisation d'une table de transpositions partagée pour optimiser les recherches des IA.
- Empêche l'ouverture de toute fenêtre graphique ou audio grâce à la configuration de Pygame en mode "dummy".
- Génère un fichier CSV détaillant le résultat du tournoi.

Le fichier de sortie est 'match_results.csv'. Il a la forme suivante :
    - Colonnes : ia_white, ia_black, winner
    - Chaque ligne correspond à une partie :
        - ia_white : niveau de l'IA qui joue blanc
        - ia_black : niveau de l'IA qui joue noir
        - winner : 1 si blanc gagne, 2 si noir gagne, 0 pour une partie nulle

Déroulement du tournoi :
- Pour chaque paire de niveaux d'IA, on réalise 50 parties jouées avec la première IA en blanc et la seconde en noir, puis 50 parties avec les couleurs inversées (donc 100 au total par duel).
- Les résultats sont enregistrés dans le fichier CSV.

Utilisation :
    python selfplay_tournoi.py

Dépendances :
- Python 3.x
- Les modules 'ia_shogi' et 'hasami_shogi' doivent être présents dans le même dossier.

"""

from __future__ import annotations

import os
import csv
import time
from typing import Dict, Tuple

os.environ["SDL_VIDEODRIVER"] = "dummy" #évite l'ouverture de fenêtres
os.environ["SDL_AUDIODRIVER"] = "dummy"
from ia_shogi import IA  
from hasami_shogi import HasamiShogi  


# table de transpositions partagée entre les IA pour accélérer les recherches

class SharedTT(dict):
    """Permet de partager la même table de transpositions entre toutes les IA."""
    pass

SHARED_TT = SharedTT()

# Fonction utilitaire pour créer une IA avec la table de transpositions partagée

def make_ia(level: int) -> IA:
    """
    Crée une instance d'IA avec le niveau donné et lui assigne la table de transpositions partagée.
    """
    ia = IA(str(level))
    ia.TT = SHARED_TT
    return ia


# Fonction qui joue une partie entre deux IA et retourne le gagnant

def jouer_match(
    ia_noir: IA,
    ia_blanc: IA,
    noir_commence: bool = True,
) -> int:
    """
    Joue une partie entre deux IA et retourne le gagnant.

    Paramètres :
        ia_noir (IA) : IA qui joue les noirs.
        ia_blanc (IA) : IA qui joue les blancs.
        noir_commence (bool) : True si les noirs commencent.

    Retourne :
        int : 1 si les blancs gagnent, 2 si les noirs gagnent, 0 si nul.
    """
    # Initialisation du jeu
    jeu = HasamiShogi(mode_jeu="ia_vs_ia")
    jeu.memo_positions = {}  # Pour la détection des répétitions de positions
    jeu.ia1 = ia_noir
    jeu.ia2 = ia_blanc
    jeu.joueur_actuel = 1 if noir_commence else 2
    compteur_sterile = 0   # Compte les coups sans capture(nullité)
    max_coups = 400
    nb_coups = 0

    # Boucle principale de la partie
    while not jeu.partie_terminee and nb_coups < max_coups:
        joueur = jeu.joueur_actuel
        ia = ia_noir if joueur == 1 else ia_blanc
        coup = ia.choisir_coup(jeu.plateau, joueur, jeu)
        if coup:
            depart, arrivee = coup
            jeu.coups_valides = jeu.obtenir_coups_valides(depart)
            jeu.deplacer_pion(depart, arrivee)
            jeu.gagnant = jeu.verifier_victoire()
            if not jeu.gagnant:
                jeu.joueur_actuel = 3 - joueur  # Changement de joueur
            else:
                jeu.partie_terminee = True
        else:
            # Aucun coup possible : l'adversaire gagne
            jeu.partie_terminee = True
            jeu.gagnant = 3 - joueur
        nb_coups += 1
        prise = jeu.deplacer_pion(depart, arrivee)
    # Gestion de la nullité par stérilité
    if prise:
        compteur_sterile = 0
    else:
        compteur_sterile += 1
    if compteur_sterile >= 100:
        jeu.partie_terminee = True
        jeu.gagnant = None
    # Gestion de la nullité par triple répétition
    cle = jeu.cle_position()
    jeu.memo_positions[cle] = jeu.memo_positions.get(cle, 0) + 1
    if jeu.memo_positions[cle] == 3:
        jeu.partie_terminee = True
        jeu.gagnant = None
    # Retourner le gagnant 
    if jeu.gagnant == 1:
        return 2  # Noir gagne
    elif jeu.gagnant == 2:
        return 1  # Blanc gagne
    else:
        return 0  # Nul


DUELS = [(1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]
GAMES_PER_COLOR = 50

# Boucle principale du tournoi IA vs IA

def tournoi_ia_vs_ia():
    """
    Lance un tournoi complet(100 parties) entre toutes les paires d'IA définies dans DUELS (on a 4 niveaux d'IA donc 6 duels).
    Génère le fichier match_results.csv avec les détails de chaque partie.
    """
    csv_path = "match_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["ia_white", "ia_black", "winner"])
        for a, b in DUELS:
            # 50 parties avec a blanc et b noir
            for _ in range(GAMES_PER_COLOR):
                gagnant = jouer_match(make_ia(b), make_ia(a), noir_commence=True)
                writer.writerow([a, b, gagnant])
            # 50 parties avec b blanc et a noir
            for _ in range(GAMES_PER_COLOR):
                gagnant = jouer_match(make_ia(a), make_ia(b), noir_commence=True)
                writer.writerow([b, a, gagnant])
    print("\nLe tournoi est terminé et les résultats sont sauvegardés dans", csv_path)


if __name__ == "__main__":
    tournoi_ia_vs_ia()