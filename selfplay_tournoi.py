# -*- coding: utf-8 -*-
"""selfplay_tournoi_opt.py
Headless self‑play tournament with CSV output and live progress
--------------------------------------------------------------
* Shared transposition table (TT) so both AIs reuse the same search data.
* Forces Pygame to use the dummy driver – no window will ever open.
* Prints progress to the terminal so you can see who is playing whom.
* Saves per‑duel aggregate statistics in `resultats_tournoi.csv` with the
  columns:
      duel,wins_black,wins_white,draws,avg_moves,total_games

NOTE – The previous SyntaxError came from using an augmented assignment on
      a conditional expression. This version replaces it with a tiny `if`.
"""

from __future__ import annotations

import os
import csv
import time
from typing import Dict, Tuple

# ---------------------------------------------------------------------------
# Prevent Pygame from opening any window / audio device
# ---------------------------------------------------------------------------
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from ia_shogi import IA  # type: ignore
from hasami_shogi import HasamiShogi  # type: ignore

# ------------------------- SHARED TRANSPOSITION TABLE ----------------------

class SharedTT(dict):
    """Simple wrapper so we can attach the *same* dict to every IA instance."""
    pass

SHARED_TT = SharedTT()


def make_ia(level: int) -> IA:
    """Create an IA instance and plug the shared TT into it."""
    ia = IA(str(level))
    ia.TT = SHARED_TT  # all engines reuse the same table
    return ia

# ----------------------------- SINGLE GAME ---------------------------------

def jouer_match(
    ia_noir: IA,
    ia_blanc: IA,
    noir_commence: bool = True,
) -> Tuple[int | None, int, float, float]:
    """Play one game and return (winner, nb_moves, time_black, time_white)."""
    jeu = HasamiShogi(mode_jeu="ia_vs_ia")
    jeu.ia1 = ia_noir
    jeu.ia2 = ia_blanc
    jeu.joueur_actuel = 1 if noir_commence else 2
    compteur_sterile = 0   
    max_coups = 400
    nb_coups = 0
    temps_noir = 0.0
    temps_blanc = 0.0

    while not jeu.partie_terminee and nb_coups < max_coups:
        
        joueur = jeu.joueur_actuel
        ia = ia_noir if joueur == 1 else ia_blanc

        # Chronométrage de la réflexion
        start = time.perf_counter()
        coup = ia.choisir_coup(jeu.plateau, joueur, jeu)
        dt = time.perf_counter() - start
        if joueur == 1:
            temps_noir += dt
        else:
            temps_blanc += dt

        # Exécuter le coup sélectionné
        if coup:
            depart, arrivee = coup
            jeu.coups_valides = jeu.obtenir_coups_valides(depart)
            jeu.deplacer_pion(depart, arrivee)
            jeu.gagnant = jeu.verifier_victoire()
            if not jeu.gagnant:
                jeu.joueur_actuel = 3 - joueur
            else:
                jeu.partie_terminee = True
        else:  # aucun coup trouvé -> l'adversaire gagne
            jeu.partie_terminee = True
            jeu.gagnant = 3 - joueur

        nb_coups += 1
        prise = jeu.deplacer_pion(depart, arrivee)
    if prise:                     # ta fonction renvoie True si capture
        compteur_sterile = 0
    else:
        compteur_sterile += 1

    # nulle par stérilité
    if compteur_sterile >= 100:
        jeu.partie_terminee = True
        jeu.gagnant = None

    # nulle par triple répétition
    cle = jeu.cle_position()
    jeu.memo_positions[cle] = jeu.memo_positions.get(cle, 0) + 1
    if jeu.memo_positions[cle] == 3:
        jeu.partie_terminee = True
        jeu.gagnant = None
    return jeu.gagnant, nb_coups, temps_noir, temps_blanc

# --------------------------- TOURNAMENT LOOP -------------------------------

DUELS = [(1, 3), (1, 4), (2, 3), (2, 4), (3, 4), (1, 2)]
GAMES_PER_COLOR = 50  # 50 when IA_x is Black + 50 when IA_x is White


def tournoi_ia_vs_ia() -> Dict[Tuple[int, int], dict]:
    """Run the tournament and write `resultats_tournoi.csv`."""
    csv_path = "resultats_tournoi.csv"
    stats: Dict[Tuple[int, int], dict] = {}

    with open(csv_path, "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["duel", "wins_black", "wins_white", "draws", "avg_moves", "total_games"])

        for duel_idx, (n1, n2) in enumerate(DUELS, start=1):
            print("=" * 55)
            print(f"DUEL {duel_idx}/{len(DUELS)} : IA{n1} ↔ IA{n2}")
            print("-" * 55)

            wins_black = wins_white = draws = total_moves = 0
            total_games = GAMES_PER_COLOR * 2

            # ---------- Phase 1 : IA n1 joue Noir, IA n2 joue Blanc ----------
            for g in range(1, GAMES_PER_COLOR + 1):
                gagnant, n_coups, *_ = jouer_match(make_ia(n1), make_ia(n2), noir_commence=True)
                total_moves += n_coups
                if gagnant == 1:
                    wins_black += 1
                elif gagnant == 2:
                    wins_white += 1
                else:
                    draws += 1
                if g % 10 == 0:
                    print(f"  Partie {g}/{GAMES_PER_COLOR} (phase 1) terminée ».")

            # ---------- Phase 2 : couleurs inversées -----------------------
            for g in range(1, GAMES_PER_COLOR + 1):
                gagnant, n_coups, *_ = jouer_match(make_ia(n2), make_ia(n1), noir_commence=True)
                total_moves += n_coups
                if gagnant == 1:
                    wins_black += 1  # IA n2 (Noir) gagne
                elif gagnant == 2:
                    wins_white += 1  # IA n1 (Blanc) gagne
                else:
                    draws += 1
                if g % 10 == 0:
                    print(f"  Partie {g}/{GAMES_PER_COLOR} (phase 2) terminée ».")

            avg_moves = total_moves / total_games

            print(f"   ► Résumé : Noir {wins_black} | Blanc {wins_white} | Nuls {draws} | ⌀ coups {avg_moves:.1f}")

            writer.writerow([f"IA{n1}-IA{n2}", wins_black, wins_white, draws, f"{avg_moves:.1f}", total_games])

            stats[(n1, n2)] = dict(
                wins_black=wins_black,
                wins_white=wins_white,
                draws=draws,
                avg_moves=avg_moves,
                games=total_games,
            )

    print("\nTournoi terminé ✔  Résultats dans", csv_path)
    return stats


if __name__ == "__main__":
    tournoi_ia_vs_ia()