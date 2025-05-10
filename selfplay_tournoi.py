import time
import numpy as np
from ia_shogi import IA
from hasami_shogi import HasamiShogi

def jouer_match(ia_noir, ia_blanc, noir_commence=True):
    jeu = HasamiShogi(mode_jeu="ia_vs_ia")
    jeu.ia1 = ia_noir
    jeu.ia2 = ia_blanc
    jeu.joueur_actuel = 1 if noir_commence else 2
    jeu.niveau_ia_noir = int(ia_noir.niveau)
    jeu.niveau_ia_blanc = int(ia_blanc.niveau)
    max_coups = 200
    coups_joués = 0
    temps_noir = 0.0
    temps_blanc = 0.0
    avantage_noir = 0
    avantage_blanc = 0

    while not jeu.partie_terminee and coups_joués < max_coups:
        joueur = jeu.joueur_actuel
        ia = jeu.ia1 if joueur == 1 else jeu.ia2
        t0 = time.perf_counter()
        coup = ia.choisir_coup(jeu.plateau, joueur, jeu)
        t1 = time.perf_counter()
        if joueur == 1:
            temps_noir += t1 - t0
        else:
            temps_blanc += t1 - t0
        if coup:
            depart, arrivee = coup
            jeu.coups_valides = jeu.obtenir_coups_valides(depart)
            jeu.deplacer_pion(depart, arrivee)
            jeu.gagnant = jeu.verifier_victoire()
            if jeu.gagnant:
                jeu.partie_terminee = True
            else:
                jeu.joueur_actuel = 3 - joueur
        else:
            jeu.partie_terminee = True
            jeu.gagnant = 3 - joueur

        # Calcul de l'avantage
        score_n = ia_noir.evaluer_position(jeu.plateau, 1)
        score_b = ia_blanc.evaluer_position(jeu.plateau, 2)
        if score_n > score_b:
            avantage_noir += 1
        elif score_b > score_n:
            avantage_blanc += 1
        # Si égalité, on ne compte pas

        coups_joués += 1

    return jeu.gagnant, temps_noir, temps_blanc, avantage_noir, avantage_blanc

def tournoi_ia_vs_ia():
    niveaux = [1, 2, 3, 4]
    stats = {}
    for n1 in niveaux:
        for n2 in niveaux:
            print(f"Match IA{n1} vs IA{n2}")
            victoires_noir = 0
            victoires_blanc = 0
            nuls = 0
            total_temps_noir = 0.0
            total_temps_blanc = 0.0
            total_avantage_noir = 0
            total_avantage_blanc = 0
            for i in range(50):
                ia1 = IA(str(n1))
                ia2 = IA(str(n2))
                gagnant, t_noir, t_blanc, adv_noir, adv_blanc = jouer_match(ia1, ia2, noir_commence=True)
                if gagnant == 1:
                    victoires_noir += 1
                elif gagnant == 2:
                    victoires_blanc += 1
                else:
                    nuls += 1
                total_temps_noir += t_noir
                total_temps_blanc += t_blanc
                total_avantage_noir += adv_noir
                total_avantage_blanc += adv_blanc
            for i in range(50):
                ia1 = IA(str(n1))
                ia2 = IA(str(n2))
                gagnant, t_noir, t_blanc, adv_noir, adv_blanc = jouer_match(ia1, ia2, noir_commence=False)
                if gagnant == 1:
                    victoires_noir += 1
                elif gagnant == 2:
                    victoires_blanc += 1
                else:
                    nuls += 1
                total_temps_noir += t_noir
                total_temps_blanc += t_blanc
                total_avantage_noir += adv_noir
                total_avantage_blanc += adv_blanc
            stats[(n1, n2)] = {
                "victoires_noir": victoires_noir,
                "victoires_blanc": victoires_blanc,
                "nuls": nuls,
                "temps_noir": total_temps_noir,
                "temps_blanc": total_temps_blanc,
                "avantage_noir": total_avantage_noir,
                "avantage_blanc": total_avantage_blanc
            }
            print(f"Résultats IA{n1} vs IA{n2} : Noir {victoires_noir} victoires, Blanc {victoires_blanc} victoires, Nuls {nuls}")
            print(f"Temps total : Noir {total_temps_noir:.2f}s, Blanc {total_temps_blanc:.2f}s")
            print(f"Avantage le plus long : Noir {total_avantage_noir} coups, Blanc {total_avantage_blanc} coups")
    return stats

if __name__ == "__main__":
    tournoi_ia_vs_ia()