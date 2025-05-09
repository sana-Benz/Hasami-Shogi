import numpy as np
from typing import List, Tuple, Optional
from hasami_shogi import HasamiShogi

class IA:
    def __init__(self, niveau: str = "minimax"):
        self.niveau = niveau
        self.profondeur_max = 3 # profondeur de l'arbre de recherche par défaut (2 coups à l'avance)
        
    def evaluer_position(self, plateau: np.ndarray, joueur: int) -> float:
        #il faut enrichir
        """Fonction d'évaluation qui évalue la position actuelle du plateau. Sert à donner une valeur numérique à 
        une position pour que l’IA puisse comparer les positions et choisir la meilleure."""
        pions_joueur = np.sum(plateau == joueur)
        pions_adverse = np.sum(plateau == (3 - joueur))
        return float(pions_joueur - pions_adverse)
    
    def obtenir_tous_coups_possibles(self, plateau: np.ndarray, joueur: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Générateur d'actions (successeurs dans l’arbre de recherche). Pour chaque pion du joueur, génère tous les déplacements possibles.
        Permet à l’IA de savoir quels coups sont légaux à chaque étape de l’arbre."""
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
        """Générateur d’états fils (noeuds enfants dans l’arbre). Simule un coup et retourne le nouveau plateau.
         Applique un coup sur une copie du plateau, effectue les captures éventuelles, et retourne le nouveau plateau résultant."""
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
    
    # --- MINIMAX ---
    def MINIMAX_DECISION(self, plateau: np.ndarray, joueur: int, profondeur: int) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """C’est la fonction qui choisit le coup optimal pour l’IA selon Minimax.
        Pour chaque coup possible, simule le coup et appelle MIN_VALUE pour évaluer la réponse de l’adversaire. Retourne le coup qui maximise la valeur."""
        actions = self.obtenir_tous_coups_possibles(plateau, joueur)
        if not actions:
            return None
        best_action = None
        best_value = float('-inf')
        for action in actions:
            value = self.MIN_VALUE(self.simuler_coup(plateau, action[0], action[1], joueur), joueur, profondeur-1)
            if value > best_value:
                best_value = value
                best_action = action
        return best_action

    def MIN_VALUE(self, plateau: np.ndarray, joueur: int, profondeur: int) -> float:
        """Noeud adversaire dans Minimax (minimise la valeur)."""
        if profondeur == 0 or not self.obtenir_tous_coups_possibles(plateau, 3-joueur):
            return self.evaluer_position(plateau, joueur)
        v = float('inf')
        actions = self.obtenir_tous_coups_possibles(plateau, 3-joueur)
        for action in actions:
            v = min(v, self.MAX_VALUE(self.simuler_coup(plateau, action[0], action[1], 3-joueur), joueur, profondeur-1))
        return v

    def MAX_VALUE(self, plateau: np.ndarray, joueur: int, profondeur: int) -> float:
        """Noeud IA/MAX dans Minimax (maximise la valeur)."""
        if profondeur == 0 or not self.obtenir_tous_coups_possibles(plateau, joueur):
            return self.evaluer_position(plateau, joueur)
        v = float('-inf')
        actions = self.obtenir_tous_coups_possibles(plateau, joueur)
        for action in actions:
            v = max(v, self.MIN_VALUE(self.simuler_coup(plateau, action[0], action[1], joueur), joueur, profondeur-1))
        return v

    # --- ALPHA-BETA ---
    def ALPHA_BETA(self, plateau: np.ndarray, joueur: int, profondeur: int) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Utilise l’élagage alpha-bêta pour ignorer les branches inutiles."""
        actions = self.obtenir_tous_coups_possibles(plateau, joueur)
        if not actions:
            return None
        best_action = None
        v = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        for action in actions:
            value = self.AB_MIN_VALUE(self.simuler_coup(plateau, action[0], action[1], joueur), joueur, profondeur-1, alpha, beta)
            if value > v:
                v = value
                best_action = action
            alpha = max(alpha, v)
        return best_action

    def AB_MAX_VALUE(self, plateau: np.ndarray, joueur: int, profondeur: int, alpha: float, beta: float) -> float:
        """Coupe l’exploration si la valeur courante de la fonction Eval dépasse beta (élagage)."""
        if profondeur == 0 or not self.obtenir_tous_coups_possibles(plateau, joueur):
            return self.evaluer_position(plateau, joueur)
        v = float('-inf')
        actions = self.obtenir_tous_coups_possibles(plateau, joueur)
        for action in actions:
            v = max(v, self.AB_MIN_VALUE(self.simuler_coup(plateau, action[0], action[1], joueur), joueur, profondeur-1, alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def AB_MIN_VALUE(self, plateau: np.ndarray, joueur: int, profondeur: int, alpha: float, beta: float) -> float:
        """Coupe l’exploration si la valeur courante de la fonction Eval descend sous alpha (élagage)."""
        if profondeur == 0 or not self.obtenir_tous_coups_possibles(plateau, 3-joueur):
            return self.evaluer_position(plateau, joueur)
        v = float('inf')
        actions = self.obtenir_tous_coups_possibles(plateau, 3-joueur)
        for action in actions:
            v = min(v, self.AB_MAX_VALUE(self.simuler_coup(plateau, action[0], action[1], 3-joueur), joueur, profondeur-1, alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def choisir_coup(self, plateau: np.ndarray, joueur: int, jeu: HasamiShogi) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Choisit le meilleur coup selon le niveau de difficulté."""
        try:
            coups_possibles = self.obtenir_tous_coups_possibles(plateau, joueur)
            if not coups_possibles:
                return None
            if self.niveau == "minimax":
                return self.MINIMAX_DECISION(plateau, joueur, self.profondeur_max)
            else:
                return self.ALPHA_BETA(plateau, joueur, self.profondeur_max)
        except Exception as e:
            print(f"Erreur lors du choix du coup : {e}")
            return None 