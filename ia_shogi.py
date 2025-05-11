"""
Ce module implémente différents niveaux d'IA pour jouer au Hasami Shogi.
Il utilise plusieurs algorithmes d'exploration d'arbre de jeu et différentes
fonctions d'évaluation selon le niveau choisi.

Caractéristiques principales :
- 4 niveaux d'IA avec des stratégies différentes
- Algorithmes Minimax et Alpha-Beta
- Fonctions d'évaluation 
- Table de transposition pour optimiser les performances
- Système de mise en ordre des coups

Niveaux d'IA :
1. Débutant : Minimax simple, profondeur 3
2. Intermédiaire : Alpha-Beta, profondeur 4
3. Avancé : Alpha-Beta avec évaluation avancée
4. Expert : Profondeur dynamique, évaluation avancée

Dépendances :
- Numpy et HasamiShogi 
"""

import numpy as np
from typing import List, Tuple, Optional
from hasami_shogi import HasamiShogi
import pygame
import random
import functools, hashlib, typing as _t       

@functools.lru_cache(maxsize=None)
def _hash(board_bytes: bytes) -> int:
    """
    Génère un hash pour un plateau 9x9.
    Utilisé comme clé pour la table de transposition.
    
    Args:
        board_bytes: Représentation en bytes du plateau
        
    Returns:
        int: Hash 64-bit du plateau
    """
    return int.from_bytes(hashlib.blake2b(board_bytes, digest_size=8).digest(),
                          'little')

class IA:
    """
    Classe principale pour l'intelligence artificielle du Hasami Shogi.
    
    Cette classe implémente différents niveaux d'IA avec des stratégies
    et des algorithmes adaptés à chaque niveau.
    
    Attributes:
        niveau (str): Niveau de l'IA ("1" à "4")
        profondeur_max (int): Profondeur maximale de l'arbre de recherche
        utilise_alpha_beta (bool): Utilise l'algorithme Alpha-Beta
        eval_fonction (callable): Fonction d'évaluation utilisée
        transpo (dict): Table de transposition pour optimiser la recherche
    """
    
    def __init__(self, niveau: str = "1"):
        """
        Initialise une nouvelle IA avec le niveau spécifié.
        
        Args:
            niveau: Niveau de l'IA ("1" à "4")
                   - 1: Débutant (Minimax simple)
                   - 2: Intermédiaire (Alpha-Beta)
                   - 3: Avancé (Alpha-Beta + évaluation avancée)
                   - 4: Expert (Profondeur dynamique)
        """
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
            self.profondeur_max = 3  # dynamique ajusté dans choisir_coup
            self.utilise_alpha_beta = True
            self.eval_fonction = self.evaluer_position
        else:
            self.profondeur_max = 2
            self.utilise_alpha_beta = False
            self.eval_fonction = self.evaluer_position_naive

    def evaluer_position_naive(self, plateau: np.ndarray, joueur: int) -> float:
        """
        Évalue la position actuelle du plateau de manière simple.
        
        Cette fonction d'évaluation prend en compte :
        1. Le matériel (différence de pions)
        2. Le contrôle du centre 
        3. Les menaces simples (horizontales et verticales)
        
        Args:
            plateau: État actuel du plateau
            joueur: Joueur dont on évalue la position (1 ou 2)
            
        Returns:
            float: Score de la position (positif = avantage pour le joueur)
        """
        adv = 3 - joueur
        score = 0.0

        # Matériel
        pions_joueur = np.sum(plateau == joueur)
        pions_adverse = np.sum(plateau == adv)
        score += 1.0 * (pions_joueur - pions_adverse)

        # Centre avec un poids plus faible
        score += 0.3 * np.sum(plateau[3:6, 3:6] == joueur)
        score -= 0.3 * np.sum(plateau[3:6, 3:6] == adv)

        # Menaces (uniquement horizontales et verticales)
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
    
    def evaluer_position(self, plateau: np.ndarray, joueur: int) -> float:
        """
        Évalue la position actuelle du plateau de manière avancée.
        
        Cette fonction d'évaluation plus sophistiquée prend en compte :
        1. Le matériel (différence de pions)
        2. Le contrôle du centre (cases 3-5)
        3. La mobilité (nombre de coups possibles)
        4. Les menaces et pions menacés
        5. Les groupes de pions adjacents
        6. Le contrôle des coins
        
        Args:
            plateau: État actuel du plateau
            joueur: Joueur dont on évalue la position (1 ou 2)
            
        Returns:
            float: Score de la position (positif = avantage pour le joueur)
        """
        adv = 3 - joueur
        score = 0.0

        # Matériel
        nbr_j = np.sum(plateau == joueur)
        nbr_a = np.sum(plateau == adv)
        score += 1.0 * (nbr_j - nbr_a)

        # Centre
        score += 0.5 * np.sum(plateau[3:6, 3:6] == joueur)
        score -= 0.5 * np.sum(plateau[3:6, 3:6] == adv)

        # Mobilité
        coups_j = len(self.obtenir_tous_coups_possibles(plateau, joueur))
        coups_a = len(self.obtenir_tous_coups_possibles(plateau, adv))
        score += 0.1 * (coups_j - coups_a)

        # Captures imminentes et pions menacés
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

        # Groupes adjacents
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

        # Coins
        coins = [(0,0),(0,8),(8,0),(8,8)]
        for i,j in coins:
            if plateau[i][j] == joueur:
                score += 0.3
            elif plateau[i][j] == adv:
                score -= 0.3

        return score
    
    def obtenir_tous_coups_possibles(self, plateau: np.ndarray, joueur: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Retourne tous les coups possibles pour un joueur.
        
        Un coup est représenté par un tuple ((ligne_dep, col_dep), (ligne_arr, col_arr)).
        Les coups sont valides si :
        - Le déplacement est horizontal ou vertical
        - Le chemin est libre
        - La position d'arrivée est sur le plateau
        
        Args:
            plateau: État actuel du plateau
            joueur: Joueur dont on cherche les coups (1 ou 2)
            
        Returns:
            Liste de tuples représentant les coups valides
        """
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
        """
        Simule un coup et retourne le nouveau plateau.
        
        Cette méthode :
        1. Copie le plateau actuel
        2. Effectue le déplacement
        3. Simule les captures possibles
        4. Retourne le nouveau plateau
        
        Args:
            plateau: État actuel du plateau
            depart: Position de départ (ligne, colonne)
            arrivee: Position d'arrivée (ligne, colonne)
            joueur: Joueur qui effectue le coup (1 ou 2)
            
        Returns:
            np.ndarray: Nouveau plateau après le coup
        """
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
        self.transpo[(h, profondeur)] = v   # cache le resultat
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
        self.transpo[(h, profondeur)] = v   # cache le resultat
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
        self.transpo[(h, profondeur)] = v   # cache le resultat

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
        self.transpo[(h, profondeur)] = v   # cache le resultat
        return v

    def choisir_coup(self, plateau: np.ndarray, joueur: int, jeu: HasamiShogi) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Choisit le meilleur coup à jouer selon le niveau de l'IA.
        
        Cette méthode :
        1. Obtient tous les coups possibles
        2. Les met en ordre selon leur potentiel
        3. Utilise l'algorithme approprié (Minimax ou Alpha-Beta)
        4. Retourne le meilleur coup trouvé
        
        Args:
            plateau: État actuel du plateau
            joueur: Joueur qui doit jouer (1 ou 2)
            jeu: Instance du jeu pour accéder aux règles
            
        Returns:
            Tuple de tuples ((ligne_dep, col_dep), (ligne_arr, col_arr)) ou None si pas de coup possible
        """
        try:
            # Récupération de tous les coups possibles pour le joueur actuel
            coups_possibles = self.obtenir_tous_coups_possibles(plateau, joueur)
            if not coups_possibles:
                return None
            
            # Mélange aléatoire des coups 
            random.shuffle(coups_possibles)

            # Stratégie spéciale pour le niveau 4 (Expert)
            if self.niveau == "4":
                static_eval = self.eval_fonction(plateau, joueur)
                # Si la position est très défavorable, on cherche le meilleur coup immédiat
                if (joueur == 1 and static_eval < -5) or (joueur == 2 and static_eval > 5):
                    meilleur_coup = max(
                        coups_possibles,
                        key=lambda action: self.eval_fonction(
                            self.simuler_coup(plateau, action[0], action[1], joueur),
                            joueur
                        )
                    )
                    return meilleur_coup

            # Stratégie d'ouverture : privilégier le centre
            if np.sum(plateau == 0) > 70:  # Début de partie 
                centraux = [c for c in coups_possibles if 2 <= c[1][0] <= 6 and 2 <= c[1][1] <= 6]
                if centraux:
                    return random.choice(centraux)
  
            # Ajustement de la profondeur de recherche selon le niveau et la phase de jeu
            profondeur = self.profondeur_max
            if self.niveau == "4":
                nb_pions = np.sum(plateau != 0)
                # Profondeur réduite en début de partie pour plus de rapidité
                if nb_pions > 60:
                    profondeur = 3
                else:
                    profondeur = self.profondeur_max
            
            # Limitation de la profondeur selon le niveau
            if self.niveau == "1":
                profondeur = min(profondeur, 2)  
            elif self.niveau == "2":
                profondeur = min(profondeur, 3)  
            elif self.niveau == "3":
                profondeur = min(profondeur, 3)  

            # Algorithme Minimax simple pour le niveau 1
            if self.niveau == "1":
                meilleur_score = float('-inf')
                meilleurs = []
                # Tri des coups pour optimiser la recherche
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
            # Algorithme Alpha-Beta pour les niveaux 2, 3 et 4
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
            print(f"Erreur dans choisir_coup : {e}")
            return None

    def jouer_partie(niveau_ia1, niveau_ia2, afficher=False):
        """
        Joue une partie complète entre deux IA de niveaux différents.
        
        Cette méthode :
        1. Initialise une partie avec deux IA de niveaux spécifiés
        2. Fait jouer les IA à tour de rôle jusqu'à la fin de la partie
        3. Gère l'affichage graphique si demandé
        4. Retourne le résultat de la partie
        
        Args:
            niveau_ia1: Niveau de la première IA ("1" à "4")
            niveau_ia2: Niveau de la deuxième IA ("1" à "4")
            afficher: Si True, affiche la partie en cours avec un délai de 200ms entre les coups
            
        Returns:
            Tuple contenant :
            - Le gagnant (1 ou 2) ou None si partie nulle
            - Le nombre de coups joués
            
        Note:
            La partie s'arrête après 200 coups maximum pour éviter les parties infinies
        """
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
        
    