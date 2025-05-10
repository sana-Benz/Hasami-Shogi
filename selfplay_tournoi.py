import time
import numpy as np
from ia_shogi import IA
from hasami_shogi import HasamiShogi
import pygame

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
        # Debug : coups possibles
        coups_possibles = []
        for i in range(9):
            for j in range(9):
                if jeu.plateau[i][j] == joueur:
                    coups_possibles.extend(jeu.obtenir_coups_valides((i, j)))
        
        score_n = ia_noir.evaluer_position(jeu.plateau, 1)
        score_b = ia_blanc.evaluer_position(jeu.plateau, 2)
        #print(f"Score IA Noir: {score_n:.2f} | Score IA Blanc: {score_b:.2f}")

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
        if score_n > score_b:
            avantage_noir += 1
        elif score_b > score_n:
            avantage_blanc += 1

        coups_joués += 1

    # Affichage fin de partie
    if jeu.gagnant == 1:
        print("Victoire Noir")
    elif jeu.gagnant == 2:
        print("Victoire Blanc")
    elif jeu.gagnant is None:
        print("Match nul (répétition ou blocage)")
    print(f"Partie terminée en {coups_joués} coups\n")

    return jeu.gagnant, temps_noir, temps_blanc, avantage_noir, avantage_blanc

def tournoi_ia_vs_ia():
    niveaux = [1, 2, 3, 4]
    duels = [(1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]
    stats = {}
    duel_total = len(duels)
    duel_num = 1
    for n1, n2 in duels:
        print("="*40)
        print(f"DUEL {duel_num}/{duel_total} : IA{n1} (Noir) vs IA{n2} (Blanc)")
        print("="*40)
        duel_num += 1
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
    # Affichage récapitulatif final
    print("\nRÉCAPITULATIF FINAL DU TOURNOI :")
    print("="*60)
    print(f"{'Duel':<15}{'Victoires N':<12}{'Victoires B':<12}{'Nuls':<8}{'Temps N (s)':<12}{'Temps B (s)':<12}{'Avantage N':<12}{'Avantage B':<12}")
    print("-"*60)
    for (n1, n2), res in stats.items():
        print(f"IA{n1} vs IA{n2}  {res['victoires_noir']:<12}{res['victoires_blanc']:<12}{res['nuls']:<8}{res['temps_noir']:<12.2f}{res['temps_blanc']:<12.2f}{res['avantage_noir']:<12}{res['avantage_blanc']:<12}")
    print("="*60)
    return stats

if __name__ == "__main__":
    tournoi_ia_vs_ia()