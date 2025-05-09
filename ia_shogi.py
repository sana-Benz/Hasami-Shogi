import numpy as np
from typing import List, Tuple, Optional
from hasami_shogi import HasamiShogi
import pygame
import random
class IA:
    def __init__(self, niveau: str = "minimax"):
        self.niveau = niveau
        self.profondeur_max = 2  # Réduit la profondeur pour plus de rapidité
        
    def evaluer_position(self, plateau: np.ndarray, joueur: int) -> float:
        """Évalue la position actuelle du plateau."""
        pions_joueur = np.sum(plateau == joueur)
        pions_adverse = np.sum(plateau == (3 - joueur))
        return float(pions_joueur - pions_adverse)
    
    def obtenir_tous_coups_possibles(self, plateau: np.ndarray, joueur: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Retourne tous les coups possibles pour un joueur."""
        coups = []
        for i in range(9):
            for j in range(9):
                if plateau[i][j] == joueur:
                    # Vérifier les mouvements horizontaux
                    for direction in [-1, 1]:
                        k = j + direction
                        while 0 <= k < 9:
                            if plateau[i][k] == 0:
                                coups.append(((i, j), (i, k)))
                            else:
                                break
                            k += direction
                    
                    # Vérifier les mouvements verticaux
                    for direction in [-1, 1]:
                        k = i + direction
                        while 0 <= k < 9:
                            if plateau[k][j] == 0:
                                coups.append(((i, j), (k, j)))
                            else:
                                break
                            k += direction
                    
                    # Vérifier les mouvements diagonaux si l'option est activée
                    if hasattr(self, 'capture_diagonale') and self.capture_diagonale:
                        for di, dj in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                            k, l = i + di, j + dj
                            while 0 <= k < 9 and 0 <= l < 9:
                                if plateau[k][l] == 0:
                                    coups.append(((i, j), (k, l)))
                                else:
                                    break
                                k += di
                                l += dj
        return coups
    
    def simuler_coup(self, plateau: np.ndarray, depart: Tuple[int, int], arrivee: Tuple[int, int], joueur: int) -> np.ndarray:
        """Simule un coup et retourne le nouveau plateau."""
        nouveau_plateau = plateau.copy()
        i_dep, j_dep = depart
        i_arr, j_arr = arrivee
        nouveau_plateau[i_arr][j_arr] = nouveau_plateau[i_dep][j_dep]
        nouveau_plateau[i_dep][j_dep] = 0
        
        # Simuler les captures
        captures = []
        # Vérifier les captures horizontales
        for direction in [-1, 1]:
            k = j_arr + direction
            pions_adverses = []
            while 0 <= k < 9:
                if nouveau_plateau[i_arr][k] == 0:
                    break
                if nouveau_plateau[i_arr][k] == joueur:
                    captures.extend(pions_adverses)
                    break
                if nouveau_plateau[i_arr][k] == 3 - joueur:
                    pions_adverses.append((i_arr, k))
                k += direction
        
        # Vérifier les captures verticales
        for direction in [-1, 1]:
            k = i_arr + direction
            pions_adverses = []
            while 0 <= k < 9:
                if nouveau_plateau[k][j_arr] == 0:
                    break
                if nouveau_plateau[k][j_arr] == joueur:
                    captures.extend(pions_adverses)
                    break
                if nouveau_plateau[k][j_arr] == 3 - joueur:
                    pions_adverses.append((k, j_arr))
                k += direction
        
        # Effectuer les captures
        for i, j in captures:
            nouveau_plateau[i][j] = 0
            
        return nouveau_plateau
    
    def minimax(self, plateau: np.ndarray, profondeur: int, est_maximisant: bool, joueur: int) -> Tuple[float, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """Implémente l'algorithme minimax."""
        if profondeur == 0:
            return self.evaluer_position(plateau, joueur), None
            
        coups_possibles = self.obtenir_tous_coups_possibles(plateau, joueur if est_maximisant else 3 - joueur)
        if not coups_possibles:
            return self.evaluer_position(plateau, joueur), None
            
        if est_maximisant:
            meilleur_score = float('-inf')
            meilleur_coup = None
            for depart, arrivee in coups_possibles:
                nouveau_plateau = self.simuler_coup(plateau, depart, arrivee, joueur)
                score, _ = self.minimax(nouveau_plateau, profondeur - 1, False, joueur)
                if score > meilleur_score:
                    meilleur_score = score
                    meilleur_coup = (depart, arrivee)
            return meilleur_score, meilleur_coup
        else:
            meilleur_score = float('inf')
            meilleur_coup = None
            for depart, arrivee in coups_possibles:
                nouveau_plateau = self.simuler_coup(plateau, depart, arrivee, 3 - joueur)
                score, _ = self.minimax(nouveau_plateau, profondeur - 1, True, joueur)
                if score < meilleur_score:
                    meilleur_score = score
                    meilleur_coup = (depart, arrivee)
            return meilleur_score, meilleur_coup
    
    def alpha_beta(self, plateau: np.ndarray, profondeur: int, est_maximisant: bool,
                   joueur: int, alpha: float = float('-inf'),
                   beta: float = float('inf')) -> Tuple[float, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """Implémente l'algorithme alpha-beta."""
        if profondeur == 0:
            return self.evaluer_position(plateau, joueur), None
            
        coups_possibles = self.obtenir_tous_coups_possibles(plateau, joueur if est_maximisant else 3 - joueur)
        if not coups_possibles:
            return self.evaluer_position(plateau, joueur), None
            
        if est_maximisant:
            meilleur_score = float('-inf')
            meilleur_coup = None
            for depart, arrivee in coups_possibles:
                nouveau_plateau = self.simuler_coup(plateau, depart, arrivee, joueur)
                score, _ = self.alpha_beta(nouveau_plateau, profondeur - 1, False, joueur, alpha, beta)
                if score > meilleur_score:
                    meilleur_score = score
                    meilleur_coup = (depart, arrivee)
                alpha = max(alpha, meilleur_score)
                if beta <= alpha:
                    break
            return meilleur_score, meilleur_coup
        else:
            meilleur_score = float('inf')
            meilleur_coup = None
            for depart, arrivee in coups_possibles:
                nouveau_plateau = self.simuler_coup(plateau, depart, arrivee, 3 - joueur)
                score, _ = self.alpha_beta(nouveau_plateau, profondeur - 1, True, joueur, alpha, beta)
                if score < meilleur_score:
                    meilleur_score = score
                    meilleur_coup = (depart, arrivee)
                beta = min(beta, meilleur_score)
                if beta <= alpha:
                    break
            return meilleur_score, meilleur_coup
    def choisir_coup(self,
                 plateau: np.ndarray,
                 joueur: int,
                 jeu: HasamiShogi
                 ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Choisit un coup :
            • mélange la liste de coups pour éviter toujours le même ordre
            • si plusieurs coups ont le même score, en prend un au hasard
        """
        try:
            # 1️⃣ Tous les coups possibles mélangés
            coups_possibles = self.obtenir_tous_coups_possibles(plateau, joueur)
            if not coups_possibles:
                return None
            random.shuffle(coups_possibles)

            # 2️⃣ Début de partie : privilégier le centre
            if np.sum(plateau == 0) > 70:
                centraux = [c for c in coups_possibles
                            if 2 <= c[1][0] <= 6 and 2 <= c[1][1] <= 6]
                if centraux:
                    return random.choice(centraux)

            # 3️⃣ Minimax ou Alpha‑Beta
            if self.niveau == "minimax":
                meilleur_score = float('-inf')
                meilleurs = []
                for depart, arrivee in coups_possibles:
                    score, _ = self.minimax(
                        self.simuler_coup(plateau, depart, arrivee, joueur),
                        self.profondeur_max - 1, False, joueur)
                    if score > meilleur_score:
                        meilleur_score = score
                        meilleurs = [(depart, arrivee)]
                    elif score == meilleur_score:
                        meilleurs.append((depart, arrivee))
                return random.choice(meilleurs)
            else:  # "alpha_beta"
                meilleur_score = float('-inf')
                meilleurs = []
                for depart, arrivee in coups_possibles:
                    score, _ = self.alpha_beta(
                        self.simuler_coup(plateau, depart, arrivee, joueur),
                        self.profondeur_max - 1, False, joueur,
                        alpha=float('-inf'), beta=float('inf'))
                    if score > meilleur_score:
                        meilleur_score = score
                        meilleurs = [(depart, arrivee)]
                    elif score == meilleur_score:
                        meilleurs.append((depart, arrivee))
                return random.choice(meilleurs)

        except Exception as e:
            print(f"Erreur choisir_coup : {e}")
            return None

    def jouer_partie(niveau_ia1, niveau_ia2, afficher=False):
            jeu = HasamiShogi(mode_jeu="ia_vs_ia")
            ia1 = IA(niveau_ia1)
            ia2 = IA(niveau_ia2)
            jeu.ia = ia1
            jeu.joueur_actuel = 1
            max_coups = 200
            coups_joués = 0

            while not jeu.partie_terminee and coups_joués < max_coups:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                joueur = jeu.joueur_actuel
                ia = ia1 if joueur == 1 else ia2
                coup = ia.choisir_coup(jeu.plateau, joueur, jeu)
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

                if afficher:
                    jeu.dessiner_plateau()
                    pygame.time.delay(200)
                coups_joués += 1

            return jeu.gagnant, coups_joués   
        
    def evaluer_position(self, plateau: np.ndarray, joueur: int) -> float:
        adv = 3 - joueur
        score = 0.0

        # 1️⃣ Matériel simple
        nbr_j = np.sum(plateau == joueur)
        nbr_a = np.sum(plateau == adv)
        score += 1.0 * (nbr_j - nbr_a)

        # 2️⃣ Centre (cases 3..5)
        score += 0.5 * np.sum(plateau[3:6, 3:6] == joueur)
        score -= 0.5 * np.sum(plateau[3:6, 3:6] == adv)

        # 3️⃣ Mobilité
        coups_j = len(self.obtenir_tous_coups_possibles(plateau, joueur))
        coups_a = len(self.obtenir_tous_coups_possibles(plateau, adv))
        score += 0.1 * (coups_j - coups_a)

        # 4️⃣ Captures imminentes et pions menacés
        def menaces(plateau, attaquant, cible):
            m, c = 0, 0
            for i in range(9):
                for j in range(9):
                    if plateau[i][j] == cible:
                        # test horizontal
                        if j > 0 and plateau[i][j-1] == attaquant:
                            m += 1
                        if j < 8 and plateau[i][j+1] == attaquant:
                            m += 1
                        # test vertical
                        if i > 0 and plateau[i-1][j] == attaquant:
                            m += 1
                        if i < 8 and plateau[i+1][j] == attaquant:
                            m += 1
            return m

        score += 1.0 * menaces(plateau, joueur, adv)    # pions adverses capturables
        score -= 1.0 * menaces(plateau, adv, joueur)    # nos pions menacés

        # 5️⃣ Groupes adjacents
        def groupes(plateau, couleur):
            g = 0
            for i in range(9):
                for j in range(9):
                    if plateau[i][j] == couleur:
                        if j < 8 and plateau[i][j+1] == couleur:
                            g += 1
                        if i < 8 and plateau[i+1][j] == couleur:
                            g += 1
            return g

        score += 0.2 * (groupes(plateau, joueur) - groupes(plateau, adv))

        # 6️⃣ Coins
        coins = [(0,0),(0,8),(8,0),(8,8)]
        for i,j in coins:
            if plateau[i][j] == joueur:
                score += 0.3
            elif plateau[i][j] == adv:
                score -= 0.3

        return score