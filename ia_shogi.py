import numpy as np
from typing import List, Tuple, Optional
from hasami_shogi import HasamiShogi
import pygame
import random
import functools, hashlib, typing as _t       # ← NEW
_ZOBRIST = np.random.randint(0, 2**64, size=(9, 9, 3), dtype=np.uint64)

@functools.lru_cache(maxsize=None)
def _hash(board_bytes: bytes) -> int:
    """Stable 64‑bit hash of a 9×9 board (used as TT key)."""
    return int.from_bytes(hashlib.blake2b(board_bytes, digest_size=8).digest(),
                          'little')
class IA:
    def __init__(self, niveau: str = "1"):
        self.niveau = str(niveau)
        self.transpo: dict[tuple[int, int], float] = {}
        # Configuration selon le niveau
        if self.niveau == "1":
            self.profondeur_max = 3
            self.utilise_alpha_beta = False
            self.eval_fonction = self.evaluer_position_naive
        elif self.niveau == "2":
            self.profondeur_max = 4
            self.utilise_alpha_beta = True
            self.eval_fonction = self.evaluer_position_naive
        elif self.niveau == "3":
            self.profondeur_max = 4
            self.utilise_alpha_beta = True
            self.eval_fonction = self.evaluer_position
        elif self.niveau == "4":
            self.profondeur_max = 3  # dynamique, ajusté dans choisir_coup
            self.utilise_alpha_beta = True
            self.eval_fonction = self.evaluer_position
        else:
            self.profondeur_max = 2
            self.utilise_alpha_beta = False
            self.eval_fonction = self.evaluer_position_naive

    #fct eval naive
    def evaluer_position_naive(self, plateau: np.ndarray, joueur: int) -> float:
        """Évalue la position actuelle du plateau de manière simple mais plus élaborée que la version de base."""
        adv = 3 - joueur
        score = 0.0

        # 1️⃣ Matériel simple (comme avant)
        pions_joueur = np.sum(plateau == joueur)
        pions_adverse = np.sum(plateau == adv)
        score += 1.0 * (pions_joueur - pions_adverse)

        # 2️⃣ Centre (cases 3..5) avec un poids plus faible
        score += 0.3 * np.sum(plateau[3:6, 3:6] == joueur)
        score -= 0.3 * np.sum(plateau[3:6, 3:6] == adv)

        # 3️⃣ Menaces simplifiées (uniquement horizontales et verticales)
        def menaces_simples(plateau, attaquant, cible):
            m = 0
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

        score += 0.5 * menaces_simples(plateau, joueur, adv)    # pions adverses capturables
        score -= 0.5 * menaces_simples(plateau, adv, joueur)    # nos pions menacés

        return score
    
    #fct eval developpée
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
        nouveau_plateau = plateau.view().copy()
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
    
    def is_terminal_state(self, plateau: np.ndarray, joueur: int) -> Optional[int]:
        # On simule la vérification de victoire sur un plateau donné
        pions_noirs = np.sum(plateau == 1)
        pions_blancs = np.sum(plateau == 2)
        if pions_noirs <= 2:
            return 2  # Blanc gagne
        if pions_blancs <= 2:
            return 1  # Noir gagne
        ecart = abs(pions_noirs - pions_blancs)
        if ecart >= 3:
            if pions_noirs > pions_blancs:
                return 1
            else:
                return 2
        return None
    @staticmethod
    def count_captured(b_old: np.ndarray, b_new: np.ndarray) -> int:
        """Return how many pieces disappeared between the two positions."""
        return int((b_old != 0).sum() - (b_new != 0).sum())

    def order_moves(self, actions, plateau, joueur):
        # Met en avant les coups qui capturent un pion, puis ceux au centre
        def score_coup(action):
            depart, arrivee = action
            plateau_apres = self.simuler_coup(plateau, depart, arrivee, joueur)
            captures = self.count_captured(plateau, plateau_apres)   # NEW
            centre = 1 if 2 <= arrivee[0] <= 6 and 2 <= arrivee[1] <= 6 else 0
            return (captures, centre)
        return sorted(actions, key=score_coup, reverse=True)

    def MIN_VALUE(self, plateau: np.ndarray, joueur: int, profondeur: int, eval_fonction) -> float:
        h = _hash(plateau.tobytes())
        cached = self.transpo.get((h, profondeur))
        if cached is not None:
            return cached
        if profondeur == 0 or not self.obtenir_tous_coups_possibles(plateau, 3-joueur):
            return eval_fonction(plateau, joueur)
        v = float('inf')
        actions = self.obtenir_tous_coups_possibles(plateau, 3-joueur)
        for action in actions:
            v = min(v, self.MAX_VALUE(self.simuler_coup(plateau, action[0], action[1], 3-joueur), joueur, profondeur-1, eval_fonction))
        self.transpo[(h, profondeur)] = v   # cache the result
        return v

    def MAX_VALUE(self, plateau: np.ndarray, joueur: int, profondeur: int, eval_fonction) -> float:
        h = _hash(plateau.tobytes())
        cached = self.transpo.get((h, profondeur))
        if cached is not None:
            return cached
        if profondeur == 0 or not self.obtenir_tous_coups_possibles(plateau, joueur):
            return eval_fonction(plateau, joueur)
        v = float('-inf')
        actions = self.obtenir_tous_coups_possibles(plateau, joueur)
        for action in actions:
            v = max(v, self.MIN_VALUE(self.simuler_coup(plateau, action[0], action[1], joueur), joueur, profondeur-1, eval_fonction))
        self.transpo[(h, profondeur)] = v   # cache the result
        return v

    def AB_MIN_VALUE(self, plateau: np.ndarray, joueur: int, profondeur: int, alpha: float, beta: float, eval_fonction) -> float:
        h = _hash(plateau.tobytes())
        cached = self.transpo.get((h, profondeur))
        if cached is not None:
            return cached
        gagnant = self.is_terminal_state(plateau, joueur)
        if gagnant:
            if gagnant == joueur:
                return float('inf')
            else:
                return float('-inf')
        if profondeur == 0 or not self.obtenir_tous_coups_possibles(plateau, 3-joueur):
            return eval_fonction(plateau, joueur)
        v = float('inf')
        actions = self.obtenir_tous_coups_possibles(plateau, 3-joueur)
        actions = self.order_moves(actions, plateau, 3-joueur)
        for action in actions:
            v = min(v, self.AB_MAX_VALUE(self.simuler_coup(plateau, action[0], action[1], 3-joueur), joueur, profondeur-1, alpha, beta, eval_fonction))
            if v <= alpha:
                return v
            beta = min(beta, v)
        self.transpo[(h, profondeur)] = v   # cache the result

        return v

    def AB_MAX_VALUE(self, plateau: np.ndarray, joueur: int, profondeur: int, alpha: float, beta: float, eval_fonction) -> float:
        h = _hash(plateau.tobytes())
        cached = self.transpo.get((h, profondeur))
        if cached is not None:
            return cached
        gagnant = self.is_terminal_state(plateau, joueur)
        if gagnant:
            if gagnant == joueur:
                return float('inf')
            else:
                return float('-inf')
        if profondeur == 0 or not self.obtenir_tous_coups_possibles(plateau, joueur):
            return eval_fonction(plateau, joueur)
        v = float('-inf')
        actions = self.obtenir_tous_coups_possibles(plateau, joueur)
        actions = self.order_moves(actions, plateau, joueur)
        for action in actions:
            v = max(v, self.AB_MIN_VALUE(self.simuler_coup(plateau, action[0], action[1], joueur), joueur, profondeur-1, alpha, beta, eval_fonction))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        self.transpo[(h, profondeur)] = v   # cache the result
        return v

    def choisir_coup(self, plateau: np.ndarray, joueur: int, jeu: HasamiShogi) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        try:
            coups_possibles = self.obtenir_tous_coups_possibles(plateau, joueur)
            if not coups_possibles:
                return None
            random.shuffle(coups_possibles)
            if self.niveau == "4":
                static_eval = self.eval_fonction(plateau, joueur)
                if (joueur == 1 and static_eval < -5) or (joueur == 2 and static_eval > 5):
                    # choisir le coup donnant la meilleure éval statique après exécution
                    meilleur_coup = max(
                        coups_possibles,
                        key=lambda action: self.eval_fonction(
                            self.simuler_coup(plateau, action[0], action[1], joueur),
                            joueur
                        )
                    )
                    return meilleur_coup
            # Début de partie : privilégier le centre
            if np.sum(plateau == 0) > 70:
                centraux = [c for c in coups_possibles if 2 <= c[1][0] <= 6 and 2 <= c[1][1] <= 6]
                if centraux:
                    return random.choice(centraux)
  
            # Détermination de la profondeur dynamique pour le niveau 4
            profondeur = self.profondeur_max
            if self.niveau == "4":
                nb_pions = np.sum(plateau != 0)
                if nb_pions > 60:
                    profondeur = 3
                else:
                    profondeur = self.profondeur_max
            # Optimisation : profondeur réduite pour niveaux faibles
            if self.niveau == "1":
                profondeur = min(profondeur, 2)
            elif self.niveau == "2":
                profondeur = min(profondeur, 3)
            elif self.niveau == "3":
                profondeur = min(profondeur, 3)

            if self.niveau == "1":
                meilleur_score = float('-inf')
                meilleurs = []
                coups_possibles = self.order_moves(coups_possibles, plateau, joueur)
                for depart, arrivee in coups_possibles:
                    nouveau_plateau = self.simuler_coup(plateau, depart, arrivee, joueur)
                    score = self.MIN_VALUE(nouveau_plateau, joueur, profondeur - 1, self.eval_fonction)
                    if score > meilleur_score:
                        meilleur_score = score
                        meilleurs = [(depart, arrivee)]
                    elif score == meilleur_score:
                        meilleurs.append((depart, arrivee))
                return random.choice(meilleurs)
            else:
                meilleur_score = float('-inf')
                meilleurs = []
                coups_possibles = self.order_moves(coups_possibles, plateau, joueur)
                for depart, arrivee in coups_possibles:
                    nouveau_plateau = self.simuler_coup(plateau, depart, arrivee, joueur)
                    score = self.AB_MIN_VALUE(nouveau_plateau, joueur, profondeur - 1, float('-inf'), float('inf'), self.eval_fonction)
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
        
    