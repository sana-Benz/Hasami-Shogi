"""
Ce module implémente une version complète du jeu Hasami Shogi.
Il gère à la fois la logique du jeu et l'interface graphique en utilisant Pygame.

Caractéristiques principales :
- Plateau de 9x9 avec pions noirs et blancs

- Modes de jeu : 2 joueurs, joueur vs IA, IA vs IA

- Système de capture avancé :
  * Capture horizontale et verticale
  * Capture diagonale (optionnelle)
  * Capture aux coins (optionnelle)
  
- Conditions de victoire multiples :
  * Seuil de défaite (nombre minimum de pions)
  * Écart de victoire (différence de pions)
  * Répétition de position (match nul)
  
- Interface graphique complète :
  * Affichage du plateau et des pions
  * Mise en évidence des coups valides
  * Barre d'évaluation de position
  * Messages de fin de partie
  
- Système anti-répétition :
  * Détection des positions répétées
  * Limite de 60 demi-coups sans capture

Dépendances :
- Pygame pour l'interface graphique
- Numpy pour la gestion du plateau de jeu
- ia_shogi pour l'ia

Classes:
    HasamiShogi: Classe principale gérant le jeu et l'interface graphique
"""

import pygame
import numpy as np
from typing import List, Tuple, Optional

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (128, 128, 128)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 0, 255)
#barre de score
BAR_NOIR  = ( 20,  20,  20)   # haut de la barre (avantage noir)
BAR_BLANC = (230, 230, 230)   # bas  de la barre (avantage blanc)

class HasamiShogi:
    """
    Classe principale du jeu Hasami Shogi.
    
    Cette classe gère l'ensemble du jeu, incluant :
    - L'initialisation du plateau
    - La logique de jeu (déplacements, captures)
    - L'interface graphique
    - Les différents modes de jeu
    - Le système de score et de victoire
    
    Attributes:
        taille_case (int): Taille en pixels d'une case du plateau
        taille_plateau (int): Nombre de cases par côté (9)
        mode_jeu (str): Mode de jeu ("2_joueurs", "joueur_vs_ia", "ia_vs_ia")
        capture_diagonale (bool): Captures en diagonale (optionnelles)
        capture_multiple_corners (bool): Captures aux coins (optionnelles)
        seuil_defaite (int): Nombre minimum de pions pour continuer
        seuil_ecart_victoire (int): Écart de pions nécessaire pour gagner
    """
    
    def __init__(self, taille_case: int = 60, mode_jeu: str = "2_joueurs", niveau_ia: str = "minimax"):
        """
        Initialise une nouvelle partie de Hasami Shogi.
        
        Args:
            taille_case: Taille en pixels d'une case du plateau
            mode_jeu: Mode de jeu ("2_joueurs", "joueur_vs_ia", "ia_vs_ia")
            niveau_ia: Niveau de l'IA
        """
    
        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_init():
            pygame.display.init()
        if not pygame.font.get_init():
            pygame.font.init()
        self.derniere_capture   = 0     
        self.capture_effectuee  = False
        self.taille_case     = taille_case
        self.taille_plateau  = 9
        self.taille_fenetre  = self.taille_case * self.taille_plateau
        self.largeur_fenetre = self.taille_fenetre + 200   
        
        # Création de la fenêtre
        self.fenetre = pygame.display.set_mode((self.largeur_fenetre, self.taille_fenetre))
        pygame.display.set_caption("Hasami Shogi")
        
        # Mode de jeu et IA
        self.mode_jeu = mode_jeu
        self.ia = None
        if mode_jeu != "2_joueurs":
            from ia_shogi import IA
            self.ia = IA(niveau_ia)
        
        # Initialisation du plateau
        self.plateau = np.zeros((self.taille_plateau, self.taille_plateau), dtype=int)
        self.initialiser_plateau()
        
        # Variables de jeu
        self.joueur_actuel = 1  # 1 pour noir, 2 pour blanc
        self.positions_occurrence = {self.cle_position(): 1}
        self.pion_selectionne = None
        self.coups_valides = []
        self.partie_terminee = False
        self.gagnant = None
        
        # Options de jeu
        self.capture_diagonale = False
        self.capture_multiple_corners = True
        self.seuil_defaite = 2
        self.seuil_ecart_victoire = 3
        
        # Boutons de fin de partie
        self.boutons = {
            "recommencer": pygame.Rect(self.taille_fenetre + 20, self.taille_fenetre - 100, 160, 40),
            "quitter": pygame.Rect(self.taille_fenetre + 20, self.taille_fenetre - 50, 160, 40)
        }
        
    def initialiser_plateau(self):
        """
        Initialise le plateau de jeu avec la position de départ.
        
        Place les pions noirs sur la première ligne (index 0)
        et les pions blancs sur la dernière ligne (index 8).
        Le reste du plateau est vide (valeur 0).
        """
        # Pions noirs (1) en haut
        self.plateau[0] = [1] * 9
        # Pions blancs (2) en bas
        self.plateau[-1] = [2] * 9
        
    def dessiner_plateau(self):
        """
        Dessine l'interface graphique complète du jeu.
        
        Cette méthode gère l'affichage de :
        - La grille du plateau
        - Les pions (noirs et blancs)
        - Les coups valides en surbrillance
        - Le pion sélectionné en surbrillance
        - Les options de jeu actives
        - L'interface utilisateur (boutons, scores)
        - Les messages de fin de partie
        """
        try:
            self.fenetre.fill(BLANC)
            
            # Dessiner les lignes du plateau
            for i in range(self.taille_plateau):
                # Lignes horizontales
                pygame.draw.line(self.fenetre, NOIR,
                               (0, i * self.taille_case),
                               (self.taille_fenetre, i * self.taille_case))
                # Lignes verticales
                pygame.draw.line(self.fenetre, NOIR,
                               (i * self.taille_case, 0),
                               (i * self.taille_case, self.taille_fenetre))
            
            # Dessiner les pions
            for i in range(self.taille_plateau):
                for j in range(self.taille_plateau):
                    if self.plateau[i][j] != 0:
                        couleur = NOIR if self.plateau[i][j] == 1 else BLANC
                        centre = (j * self.taille_case + self.taille_case // 2,
                                i * self.taille_case + self.taille_case // 2)
                        pygame.draw.circle(self.fenetre, couleur, centre, self.taille_case // 3)
                        if self.plateau[i][j] == 2:  # Contour pour les pions blancs
                            pygame.draw.circle(self.fenetre, NOIR, centre, self.taille_case // 3, 2)
            
            # Mettre en surbrillance le pion sélectionné
            if self.pion_selectionne:
                i, j = self.pion_selectionne
                rect = pygame.Rect(j * self.taille_case, i * self.taille_case,
                                 self.taille_case, self.taille_case)
                pygame.draw.rect(self.fenetre, VERT, rect, 3)
            
            # Mettre en surbrillance les coups valides
            for i, j in self.coups_valides:
                rect = pygame.Rect(j * self.taille_case, i * self.taille_case,
                                 self.taille_case, self.taille_case)
                pygame.draw.rect(self.fenetre, ROUGE, rect, 2)
            
            # Afficher les options actives
            police = pygame.font.Font(None, 24)
            x_options = self.taille_fenetre + 20
            y_options = 20
            
            # Titre des options
            titre = police.render("Options actives:", True, NOIR)
            self.fenetre.blit(titre, (x_options, y_options))
            y_options += 30
            
            # Afficher les options
            options = [
                ("Capture diagonale", self.capture_diagonale),
                ("Capture coin", self.capture_multiple_corners),
                (f"Seuil défaite: {self.seuil_defaite}", True),
                (f"Seuil victoire: {self.seuil_ecart_victoire}", True)
            ]
            
            for option, active in options:
                couleur = VERT if active else ROUGE
                texte = police.render(option, True, couleur)
                self.fenetre.blit(texte, (x_options, y_options))
                y_options += 25
            
            # Afficher le joueur actuel et le mode de jeu
            if self.mode_jeu == "ia_vs_ia":
                niveau_noir = getattr(self, 'niveau_ia_noir', 1)
                niveau_blanc = getattr(self, 'niveau_ia_blanc', 1)
                if self.joueur_actuel == 1:
                    texte_joueur = police.render(f"IA niv {niveau_noir} (Noir)", True, NOIR)
                else:
                    texte_joueur = police.render(f"IA niv {niveau_blanc} (Blanc)", True, NOIR)
                texte_mode = police.render("Mode : IA vs IA", True, NOIR)
                self.fenetre.blit(texte_joueur, (x_options, y_options + 20))
                self.fenetre.blit(texte_mode, (x_options, y_options + 45))
            else:
                joueur = "Noir" if self.joueur_actuel == 1 else "Blanc"
                mode = "2 joueurs" if self.mode_jeu == "2_joueurs" else f"IA ({self.ia.niveau})"
                texte_joueur = police.render(f"Joueur actuel: {joueur}", True, NOIR)
                texte_mode = police.render(f"Mode: {mode}", True, NOIR)
                self.fenetre.blit(texte_joueur, (x_options, y_options + 20))
                self.fenetre.blit(texte_mode, (x_options, y_options + 45))
            
            # Afficher un message spécial pour le tour de l'IA
            if self.mode_jeu != "2_joueurs" and self.mode_jeu != "ia_vs_ia" and self.joueur_actuel == 2:
                texte_ia = police.render("C'est le tour de l'IA", True, ROUGE)
                self.fenetre.blit(texte_ia, (x_options, y_options + 70))
            
            # Dessiner les boutons de contrôle
            for nom, rect in self.boutons.items():
                pygame.draw.rect(self.fenetre, BLEU, rect)
                texte = police.render(nom.capitalize(), True, BLANC)
                self.fenetre.blit(texte, (rect.centerx - texte.get_width()//2,
                                        rect.centery - texte.get_height()//2))
            
            # Afficher le message de fin de partie si la partie est terminée
            if self.partie_terminee:
                overlay = pygame.Surface((self.largeur_fenetre, self.taille_fenetre))
                overlay.fill(BLANC)
                overlay.set_alpha(128)
                self.fenetre.blit(overlay, (0, 0))

                police_grande = pygame.font.Font(None, 48)
                if self.gagnant in (1, 2):
                    message = f"Le joueur {'Noir' if self.gagnant == 1 else 'Blanc'} a gagné !"
                else:
                    message = "Match nul par répétition"

                texte_message = police_grande.render(message, True, NOIR)
                self.fenetre.blit(
                    texte_message,
                    (self.largeur_fenetre//2 - texte_message.get_width()//2,
                    self.taille_fenetre//2 - 50)
    )

                

            if self.ia:                        
                # score positif donc avantage Noir, négatif donc avantage Blanc
                        score_n = self.ia.evaluer_position(self.plateau, 1)
                        score_b = self.ia.evaluer_position(self.plateau, 2)
                        eval_global = score_n - score_b       # ∈ [-inf, +inf]

                        # On borne pour éviter une barre démesurée
                        eval_global = max(-10.0, min(10.0, eval_global))

                        # Convertir en pourcentage (‑10 devient 0 %,   0 devient 50 %,  +10 devient 100 %)
                        pct_noir = (eval_global + 10) / 20

                        # Dimensions
                        x_bar   = self.taille_fenetre + 170   
                        w_bar   = 20
                        h_total = self.taille_fenetre
                        h_noir  = int(pct_noir * h_total)

                        # Dessine la moitié supérieure (Noir) et inférieure (Blanc)
                        pygame.draw.rect(self.fenetre, BAR_BLANC,
                                        (x_bar, 0, w_bar, h_total - h_noir))     # bas
                        pygame.draw.rect(self.fenetre, BAR_NOIR,
                                        (x_bar, h_total - h_noir, w_bar, h_noir)) # haut

                        # bordure
                        pygame.draw.rect(self.fenetre, NOIR,
                                        (x_bar, 0, w_bar, h_total), 1)

                        # Labels N/B
                        police_bar = pygame.font.Font(None, 20)
                        txtN = police_bar.render("N", True, NOIR)
                        txtB = police_bar.render("B", True, NOIR)
                        self.fenetre.blit(txtN, (x_bar - 12, 2))
                        self.fenetre.blit(txtB, (x_bar - 12, h_total - txtB.get_height() - 2))
                    
            pygame.display.flip()
            return True
        except pygame.error as e:
            print(f"Erreur lors du dessin du plateau : {e}")
            return False
    
    def obtenir_coups_valides(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Détermine tous les coups valides possibles pour un pion donné.
        
        Un coup est valide si :
        - Le déplacement est horizontal ou vertical
        - Le chemin est libre (pas de pions sur le trajet)
        - La position d'arrivée est sur le plateau
        
        Args:
            position: Tuple (ligne, colonne) de la position du pion
        
        Returns:
            Liste de tuples (ligne, colonne) des positions valides
        """
        i, j = position
        coups = []
        
        # Vérifier les mouvements horizontaux
        for direction in [-1, 1]:
            k = j + direction
            while 0 <= k < self.taille_plateau:
                if self.plateau[i][k] == 0:
                    coups.append((i, k))
                else:
                    break
                k += direction
        
        # Vérifier les mouvements verticaux
        for direction in [-1, 1]:
            k = i + direction
            while 0 <= k < self.taille_plateau:
                if self.plateau[k][j] == 0:
                    coups.append((k, j))
                else:
                    break
                k += direction
        
        return coups
    
    def verifier_capture(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Vérifie et retourne les pions capturés après un mouvement.
        
        Les captures peuvent se faire de plusieurs façons :
        - En encadrant les pions adverses horizontalement ou verticalement
        - En diagonale si l'option capture_diagonale est activée
        - Aux coins si l'option capture_multiple_corners est activée
        
        Args:
            position: Tuple (ligne, colonne) de la position du dernier pion déplacé
        
        Returns:
            Liste des positions (ligne, colonne) des pions capturés
        """
        i, j = position
        captures = []

        # Captures classiques (horizontale, verticale)
        for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            pions_adverses = []
            k, l = i + di, j + dj
            while 0 <= k < self.taille_plateau and 0 <= l < self.taille_plateau:
                if self.plateau[k][l] == 0:
                    break
                if self.plateau[k][l] == self.joueur_actuel:
                    if pions_adverses:
                        captures.extend(pions_adverses)
                    break
                if self.plateau[k][l] == 3 - self.joueur_actuel:
                    pions_adverses.append((k, l))
                k += di
                l += dj

        # Capture diagonale si activée
        if self.capture_diagonale:
            for di, dj in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                pions_adverses = []
                k, l = i + di, j + dj
                while 0 <= k < self.taille_plateau and 0 <= l < self.taille_plateau:
                    if self.plateau[k][l] == 0:
                        break
                    if self.plateau[k][l] == self.joueur_actuel:
                        if pions_adverses:
                            captures.extend(pions_adverses)
                        break
                    if self.plateau[k][l] == 3 - self.joueur_actuel:
                        pions_adverses.append((k, l))
                    k += di
                    l += dj

        # Capture coin
        coin_capture = None
        coins = [ (0, 0), (0, self.taille_plateau - 1), (self.taille_plateau - 1, 0), (self.taille_plateau - 1, self.taille_plateau - 1) ]
        for ci, cj in coins:
            if self.plateau[ci][cj] == 3 - self.joueur_actuel:
                # Coin en haut à gauche
                if ci == 0 and cj == 0:
                    if self.plateau[0][1] == self.joueur_actuel and self.plateau[1][0] == self.joueur_actuel:
                        coin_capture = (0, 0)
                        break
                # Coin en haut à droite
                elif ci == 0 and cj == self.taille_plateau - 1:
                    if self.plateau[0][self.taille_plateau - 2] == self.joueur_actuel and self.plateau[1][self.taille_plateau - 1] == self.joueur_actuel:
                        coin_capture = (0, self.taille_plateau - 1)
                        break
                # Coin en bas à gauche
                elif ci == self.taille_plateau - 1 and cj == 0:
                    if self.plateau[self.taille_plateau - 2][0] == self.joueur_actuel and self.plateau[self.taille_plateau - 1][1] == self.joueur_actuel:
                        coin_capture = (self.taille_plateau - 1, 0)
                        break
                # Coin en bas à droite
                elif ci == self.taille_plateau - 1 and cj == self.taille_plateau - 1:
                    if self.plateau[self.taille_plateau - 2][self.taille_plateau - 1] == self.joueur_actuel and self.plateau[self.taille_plateau - 1][self.taille_plateau - 2] == self.joueur_actuel:
                        coin_capture = (self.taille_plateau - 1, self.taille_plateau - 1)
                        break
        if coin_capture:
            captures.append(coin_capture)

        return captures
    
    def deplacer_pion(self, depart: Tuple[int, int], arrivee: Tuple[int, int]) -> bool:
        """
        Déplace un pion et gère les captures qui en résultent.
        
        Cette méthode :
        1. Vérifie si le déplacement est valide
        2. Effectue le déplacement
        3. Vérifie et applique les captures
        4. Met à jour le compteur de coups sans capture
        5. Vérifie les conditions de victoire
        
        Args:
            depart: Tuple (ligne, colonne) de la position initiale
            arrivee: Tuple (ligne, colonne) de la position finale
        
        Returns:
            bool: True si le déplacement a été effectué avec succès
        """
        if arrivee not in self.coups_valides:
            return False
        
        i_dep, j_dep = depart
        i_arr, j_arr = arrivee
        
        # Déplacement du pion
        self.plateau[i_arr][j_arr] = self.plateau[i_dep][j_dep]
        self.plateau[i_dep][j_dep] = 0
        
        # Effectuer les captures
        captures = self.verifier_capture(arrivee)
        for i, j in captures:
            self.plateau[i][j] = 0
        self.capture_effectuee = bool(captures)
        if self.capture_effectuee:
            self.derniere_capture = 0        # reset
        else:
            self.derniere_capture += 1

        # si 60 coups sans capture alors match nul
        if self.derniere_capture >= 60:
            self.partie_terminee = True
            self.gagnant = None              
            print("Match nul : 60 demi‑coups sans capture")
            return True                      
        cle = self.cle_position(3 - self.joueur_actuel)   
        self.positions_occurrence[cle] = \
                self.positions_occurrence.get(cle, 0) + 1
        # match nul par répétition de coups
        if self.positions_occurrence[cle] >= 3:
            self.partie_terminee = True
            self.gagnant = None          
            print("Match nul : position répétée 3 fois")
            return True                 

        return True
    
    def verifier_victoire(self) -> Optional[int]:
        """
        Vérifie si la partie est terminée et détermine le vainqueur.
        
        La victoire peut être obtenue de plusieurs façons :
        - Un joueur a moins de pions que le seuil_defaite
        - L'écart de pions entre les joueurs dépasse seuil_ecart_victoire
        - Une position se répète trois fois (match nul)
        
        Returns:
            Optional[int]: 
                - 1 si les Noirs gagnent
                - 2 si les Blancs gagnent
                - None si la partie continue
                - 0 en cas de match nul
        """
        # Compter les pions restants
        pions_noirs = np.sum(self.plateau == 1)
        pions_blancs = np.sum(self.plateau == 2)
        
        # Vérifier le seuil de défaite
        if pions_noirs <= self.seuil_defaite:
            return 2  # Blanc gagne
        if pions_blancs <= self.seuil_defaite:
            return 1  # Noir gagne
        
        # Vérifier le seuil d'écart
        ecart = abs(pions_noirs - pions_blancs)
        if ecart >= self.seuil_ecart_victoire:
            if pions_noirs > pions_blancs:
                return 1  # Noir gagne
            else:
                return 2  # Blanc gagne
        
        return None
    
    def executer(self):
        """
        Boucle principale du jeu gérant les événements et l'affichage.
        
        Cette méthode :
        - Gère les événements de la souris et du clavier
        - Met à jour l'affichage du plateau
        - Gère les tours des joueurs et de l'IA
        - Contrôle le déroulement de la partie
        - Gère les actions de fin de partie (recommencer/quitter)
        
        Fonctionnement détaillé :
        1. Boucle principale :
           - Traite les événements Pygame (clics, fermeture)
           - Gère les interactions avec les boutons de contrôle
           - Met à jour l'affichage du plateau
        
        2. Gestion des coups :
           - Permet la sélection d'un pion
           - Affiche les coups valides
           - Effectue le déplacement si valide
           - Gère les captures
           - Vérifie les conditions de victoire
        
        3. Mode IA :
           - Active l'IA au tour approprié
           - Applique les coups de l'IA
           - Gère la transition entre joueur et IA
        
        4. Fin de partie :
           - Affiche le message de victoire
           - Permet de recommencer ou quitter
        """
        en_cours = True
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                    break
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    
                    # Vérifier les clics sur les boutons de contrôle
                    for nom, rect in self.boutons.items():
                        if rect.collidepoint(x, y):
                            if nom == "recommencer":
                                # Réinitialiser complètement le jeu
                                self.__init__(self.taille_case, self.mode_jeu, self.ia.niveau if self.ia else "minimax")
                            elif nom == "quitter":
                                en_cours = False
                            continue
                    
                    # Gestion des coups pendant la partie
                    if not self.partie_terminee:
                        i = y // self.taille_case
                        j = x // self.taille_case
                        
                        if 0 <= i < self.taille_plateau and 0 <= j < self.taille_plateau:
                            # Ne permettre les coups que si c'est le tour du joueur humain
                            if self.mode_jeu == "2_joueurs" or self.joueur_actuel == 1:
                                if self.pion_selectionne is None:
                                    # Sélectionner un pion
                                    if self.plateau[i][j] == self.joueur_actuel:
                                        self.pion_selectionne = (i, j)
                                        self.coups_valides = self.obtenir_coups_valides((i, j))
                                else:
                                    # Déplacer le pion sélectionné
                                    if self.deplacer_pion(self.pion_selectionne, (i, j)):
                                        # Vérifier la victoire
                                        self.gagnant = self.verifier_victoire()
                                        if self.gagnant:
                                            self.partie_terminee = True
                                        else:
                                            # Changer de joueur
                                            self.joueur_actuel = 3 - self.joueur_actuel
                                    
                                    # Réinitialiser la sélection
                                    self.pion_selectionne = None
                                    self.coups_valides = []
            
            # Tour de l'IA si nécessaire
            if not self.partie_terminee and self.mode_jeu != "2_joueurs" and self.joueur_actuel == 2:
                # L'IA joue avec les pions blancs (joueur 2)
                coup = self.ia.choisir_coup(self.plateau, self.joueur_actuel, self)
                if coup:
                    depart, arrivee = coup
                    # Vérifier si le coup est valide
                    self.coups_valides = self.obtenir_coups_valides(depart)
                    if arrivee in self.coups_valides:
                        if self.deplacer_pion(depart, arrivee):
                            self.gagnant = self.verifier_victoire()
                            if self.gagnant:
                                self.partie_terminee = True
                            else:
                                self.joueur_actuel = 1  # Retour au joueur humain
            
            self.dessiner_plateau()
            pygame.time.delay(10)  # Ajouter un petit délai pour ne pas surcharger le CPU
        
        pygame.quit()

    def cle_position(self, joueur: int | None = None) -> str:
        """
        Génère une clé unique représentant l'état actuel du plateau.
        
        Cette clé est utilisée pour :
        - Détecter les répétitions de position
        - Identifier les positions déjà évaluées par l'IA
        
        Args:
            joueur: Optionnel, le joueur actuel (1 pour noir, 2 pour blanc)
                   Si None, utilise self.joueur_actuel
        
        Returns:
            str: Une chaîne unique représentant l'état du plateau et le joueur actif
        """
        if joueur is None:         
            joueur = self.joueur_actuel
        board_str = ''.join(map(str, self.plateau.flatten()))
        return board_str + str(joueur)

if __name__ == "__main__":
    jeu = HasamiShogi()
    jeu.executer() 