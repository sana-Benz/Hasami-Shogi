import time
import csv
from ia_shogi import IA
from hasami_shogi import HasamiShogi

def run_round_robin(levels, games_per_pair=50, afficher=False):
    """
    Pour chaque paire de niveaux distincts (a,b) avec a<b,
    joue `games_per_pair` parties avec a en blanc, then
    games_per_pair parties en inversant.
    Enregistre les résultats dans 'match_results.csv'.
    """
    fieldnames = [
        "ia_white", "ia_black", "winner", "moves", "duration_s"
    ]
    with open("match_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, lvl_a in enumerate(levels):
            for lvl_b in levels[i+1:]:
                # 50 parties lvl_a blanc vs lvl_b noir
                for _ in range(games_per_pair):
                    start = time.time()
                    winner, moves = IA.jouer_partie(
                        niveau_ia1=lvl_a,
                        niveau_ia2=lvl_b,
                        afficher=afficher
                    )
                    duration = time.time() - start
                    writer.writerow({
                        "ia_white": lvl_a,
                        "ia_black": lvl_b,
                        "winner": winner,      # 0=nulle,1=white,2=black
                        "moves": moves,
                        "duration_s": round(duration, 3)
                    })
                # 50 parties inverse
                for _ in range(games_per_pair):
                    start = time.time()
                    winner, moves = IA.jouer_partie(
                        niveau_ia1=lvl_b,
                        niveau_ia2=lvl_a,
                        afficher=afficher
                    )
                    duration = time.time() - start
                    # On transpose les indices de winner pour garder white=lvl_a
                    if winner == 1:
                        winner_transposed = 2
                    elif winner == 2:
                        winner_transposed = 1
                    else:
                        winner_transposed = 0
                    writer.writerow({
                        "ia_white": lvl_a,
                        "ia_black": lvl_b,
                        "winner": winner_transposed,
                        "moves": moves,
                        "duration_s": round(duration, 3)
                    })

if __name__ == "__main__":
    # Les 4 niveaux que tu utilises
    niveaux = ["1", "2", "3", "4"]
    run_round_robin(niveaux, games_per_pair=50, afficher=False)
    print("Terminé : résultats dans match_results.csv")
