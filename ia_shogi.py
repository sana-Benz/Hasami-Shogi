import numpy as np
from typing import List, Tuple, Optional
from hasami_shogi import HasamiShogi

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
    
    def choisir_coup(self, plateau: np.ndarray, joueur: int, jeu: HasamiShogi) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Choisit le meilleur coup selon le niveau de difficulté."""
        try:
            # Obtenir tous les coups possibles
            coups_possibles = self.obtenir_tous_coups_possibles(plateau, joueur)
            if not coups_possibles:
                return None
            
            # Si c'est le début de la partie, privilégier les coups vers le centre
            if np.sum(plateau == 0) > 70:  # Plus de 70 cases vides
                coups_centraux = []
                for depart, arrivee in coups_possibles:
                    i_arr, j_arr = arrivee
                    if 2 <= i_arr <= 6 and 2 <= j_arr <= 6:
                        coups_centraux.append((depart, arrivee))
                if coups_centraux:
                    return coups_centraux[0]
            
            # Sinon, utiliser l'algorithme choisi
            if self.niveau == "minimax":
                _, coup = self.minimax(plateau, self.profondeur_max, True, joueur)
            else:  # alpha-beta
                _, coup = self.alpha_beta(plateau, self.profondeur_max, True, joueur)
            
            # Si aucun coup n'a été trouvé, prendre le premier coup possible
            if not coup and coups_possibles:
                return coups_possibles[0]
            
            return coup
        except Exception as e:
            print(f"Erreur lors du choix du coup : {e}")
            return None 