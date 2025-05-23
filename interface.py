"""
Ce module gère l'interface graphique du jeu Hasami Shogi avec de Pygame.

Fonctionnalités principales :
- Affichage du menu principal, des options et du plateau de jeu.
- Gestion des interactions utilisateur (clics sur les boutons, choix des options, lancement des parties).
- Prise en charge de 3 modes de jeu : 2 joueurs, Joueur vs IA, IA vs IA.
- Configuration des options de jeu (règles spéciales, niveaux d'IA, etc.).

Dépendances :
- Pygame
- Les modules 'ia_shogi' et 'hasami_shogi' doivent être présents dans le même dossier.

"""
import os
import pygame
import sys
from typing import Dict, Any, List, Tuple
from hasami_shogi import HasamiShogi
import numpy as np
from ia_shogi import IA

class Interface:
    """
    Classe principale pour l'interface graphique.
    Gère l'affichage, les menus, les options et la boucle principale du jeu.
    """
    def __init__(self):
        """
        Initialise l'interface graphique, les couleurs, les polices, les boutons et les options de jeu.
        """
        try:
            # Initialisation de la fenêtre principale
            pygame.init()
            self.tournoi_en_cours = False
            self.tournoi_parties = 0
            self.tournoi_max = 50
            self.jeu_en_cours = None
            self.afficher_tournoi = False
            self.largeur = 800
            self.hauteur = 600
            self.fenetre = pygame.display.set_mode((self.largeur, self.hauteur))
            pygame.display.set_caption("Hasami Shogi - Menu")
            
            # Couleurs
            self.BLANC = (255, 255, 255)
            self.NOIR = (0, 0, 0)
            self.GRIS = (128, 128, 128)
            self.BLEU = (0, 0, 255)
            self.ROUGE = (255, 0, 0)
            self.VERT = (0, 255, 0)
            
            # Police
            self.police = pygame.font.Font(None, 36)
            
            # Options de jeu par défaut
            self.options = {
                "mode_jeu": "2_joueurs", 
                "capture_diagonale": False,
                "capture_multiple_corners": True,
                "seuil_defaite": 2,
                "seuil_ecart_victoire": 3
            }
            
            # Boutons du menu principal
            self.boutons = {
                "Jouer": pygame.Rect(300, 200, 200, 50),
                "Options": pygame.Rect(300, 300, 200, 50),
                "Quitter": pygame.Rect(300, 400, 200, 50),
                "IA vs IA": pygame.Rect(300, 500, 200, 50)
            }
            
            # Boutons pour le choix du mode de jeu
            self.boutons_mode = [
                ("2 joueurs", pygame.Rect(50, 150, 200, 40)),
                ("Joueur vs IA", pygame.Rect(300, 150, 200, 40)),
                ("IA vs IA", pygame.Rect(550, 150, 200, 40))
            ]
            
            # Niveaux d'IA
            self.niveaux_ia = [1, 2, 3, 4]
            self.niveau_ia_joueur = 1  
            self.niveau_ia_noir = 1    
            self.niveau_ia_blanc = 1   
            
            # État du menu actuel
            self.menu_actuel = "principal"  # "principal" ou "options"
        except Exception as e:
            print(f"Erreur lors de l'initialisation : {e}")
            sys.exit(1)
    
    def dessiner_menu_principal(self):
        """
        Affiche le menu principal avec les boutons pour jouer, options, quitter ou lancer une partie IA vs IA.
        """
        try:
            self.fenetre.fill(self.BLANC)
            
            
            titre = self.police.render("Hasami Shogi", True, self.NOIR)
            self.fenetre.blit(titre, (self.largeur//2 - titre.get_width()//2, 100))
            # Affichage des boutons du menu principal
            for nom, rect in self.boutons.items():
                pygame.draw.rect(self.fenetre, self.BLEU, rect)
                texte = self.police.render(nom.capitalize(), True, self.BLANC)
                self.fenetre.blit(texte, (rect.centerx - texte.get_width()//2,
                                        rect.centery - texte.get_height()//2))
            
            pygame.display.flip()
            return True
        except Exception as e:
            print(f"Erreur lors du dessin du menu principal : {e}")
            return False
    
    def dessiner_menu_options(self):
        """
        Affiche le menu des options qui permet de choisir le mode de jeu, les niveaux d'IA et les règles facultatives.
        """
        try:
            self.fenetre.fill(self.BLANC)
            
            # Titre du menu options
            titre = self.police.render("Options", True, self.NOIR)
            self.fenetre.blit(titre, (self.largeur//2 - titre.get_width()//2, 50))
            
            # Affichage du choix du mode de jeu
            texte = self.police.render("Mode de jeu:", True, self.NOIR)
            self.fenetre.blit(texte, (50, 100))
            
            # Boutons pour le mode de jeu
            for nom, rect in self.boutons_mode:
                if nom == "2 joueurs":
                    mode_correspondant = "2_joueurs"
                elif nom == "Joueur vs IA":
                    mode_correspondant = "joueur_vs_ia"
                else:
                    mode_correspondant = "ia_vs_ia"
                couleur = self.VERT if self.options["mode_jeu"] == mode_correspondant else self.BLEU
                pygame.draw.rect(self.fenetre, couleur, rect)
                texte = self.police.render(nom, True, self.BLANC)
                self.fenetre.blit(texte, (rect.centerx - texte.get_width()//2,
                                        rect.centery - texte.get_height()//2))
            
            # Sélecteurs de niveau IA 
            y_ia = 210
            if self.options["mode_jeu"] == "joueur_vs_ia":
                texte = self.police.render("Niveau IA:", True, self.NOIR)
                self.fenetre.blit(texte, (50, y_ia))
                for idx, niveau in enumerate(self.niveaux_ia):
                    rect = pygame.Rect(220 + idx*60, y_ia, 50, 40)
                    couleur = self.VERT if self.niveau_ia_joueur == niveau else self.BLEU
                    pygame.draw.rect(self.fenetre, couleur, rect)
                    txt = self.police.render(str(niveau), True, self.BLANC)
                    self.fenetre.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
            elif self.options["mode_jeu"] == "ia_vs_ia":
                texteN = self.police.render("Niveau IA Noir:", True, self.NOIR)
                texteB = self.police.render("Niveau IA Blanc:", True, self.NOIR)
                self.fenetre.blit(texteN, (50, y_ia))
                self.fenetre.blit(texteB, (50, y_ia+50))
                for idx, niveau in enumerate(self.niveaux_ia):
                    rectN = pygame.Rect(250 + idx*60, y_ia, 50, 40)
                    rectB = pygame.Rect(250 + idx*60, y_ia+50, 50, 40)
                    couleurN = self.VERT if self.niveau_ia_noir == niveau else self.BLEU
                    couleurB = self.VERT if self.niveau_ia_blanc == niveau else self.BLEU
                    pygame.draw.rect(self.fenetre, couleurN, rectN)
                    pygame.draw.rect(self.fenetre, couleurB, rectB)
                    txtN = self.police.render(str(niveau), True, self.BLANC)
                    txtB = self.police.render(str(niveau), True, self.BLANC)
                    self.fenetre.blit(txtN, (rectN.centerx - txtN.get_width()//2, rectN.centery - txtN.get_height()//2))
                    self.fenetre.blit(txtB, (rectB.centerx - txtB.get_width()//2, rectB.centery - txtB.get_height()//2))
            
            # Affichage des autres options
            y = 310
            for option, valeur in self.options.items():
                if option != "mode_jeu":
                    texte = self.police.render(option.replace("_", " ").capitalize(), True, self.NOIR)
                    self.fenetre.blit(texte, (50, y))
                    
                    
                    if isinstance(valeur, bool):
                        couleur = self.VERT if valeur else self.ROUGE
                        pygame.draw.rect(self.fenetre, couleur, (400, y, 100, 30))
                        texte_valeur = self.police.render(str(valeur), True, self.BLANC)
                    else:
                        pygame.draw.rect(self.fenetre, self.GRIS, (400, y, 100, 30))
                        texte_valeur = self.police.render(str(valeur), True, self.NOIR)
                    
                    self.fenetre.blit(texte_valeur, (420, y))
                    y += 50
            
            # Bouton retour au menu principal
            pygame.draw.rect(self.fenetre, self.BLEU, (300, 500, 200, 50))
            texte = self.police.render("Retour", True, self.BLANC)
            self.fenetre.blit(texte, (350, 515))
            
            pygame.display.flip()
            return True
        except Exception as e:
            print(f"Erreur lors du dessin du menu options : {e}")
            return False
    
    def executer(self):
        """
        Boucle principale de l'interface graphique.
        Gère les événements utilisateur, l'affichage des menus, le lancement des parties et des tournois IA vs IA.
        """
        try:
            en_cours = True
            while en_cours:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        en_cours = False
                        break

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos

                        # Gestion de clics dans le menu principal
                        if self.menu_actuel == "principal":
                            for nom, rect in self.boutons.items():
                                if rect.collidepoint(x, y):
                                    if nom == "Jouer":
                                        # Lancement d'une partie selon le mode de jeu sélectionné
                                        from hasami_shogi import HasamiShogi
                                        mode_jeu = self.options["mode_jeu"]
                                        if mode_jeu == "2_joueurs":
                                            jeu = HasamiShogi(mode_jeu=mode_jeu)
                                        elif mode_jeu == "joueur_vs_ia":
                                            from ia_shogi import IA
                                            jeu = HasamiShogi(mode_jeu=mode_jeu, niveau_ia=str(self.niveau_ia_joueur))
                                            jeu.ia = IA(str(self.niveau_ia_joueur))
                                        else:  
                                            from ia_shogi import IA
                                            jeu = HasamiShogi(mode_jeu=mode_jeu)
                                            jeu.ia1 = IA(str(self.niveau_ia_noir))
                                            jeu.ia2 = IA(str(self.niveau_ia_blanc))
                                            jeu.joueur_actuel = 1
                                        for option, valeur in self.options.items():
                                            if option != "mode_jeu":
                                                setattr(jeu, option, valeur)
                                        jeu.executer()
                                        self.fenetre = pygame.display.set_mode((self.largeur, self.hauteur))
                                    elif nom == "Options":
                                        self.menu_actuel = "options"
                                    elif nom == "Quitter":
                                        en_cours = False
                                        break
                                    elif nom == "IA vs IA":
                                        # Lancement d'une partie IA vs IA
                                        from hasami_shogi import HasamiShogi
                                        from ia_shogi import IA
                                        self.jeu_en_cours = HasamiShogi(mode_jeu="ia_vs_ia")
                                        self.jeu_en_cours.ia1 = IA(str(self.niveau_ia_noir))
                                        self.jeu_en_cours.ia2 = IA(str(self.niveau_ia_blanc))
                                        self.jeu_en_cours.joueur_actuel = 1
                                        self.jeu_en_cours.niveau_ia_noir = self.niveau_ia_noir
                                        self.jeu_en_cours.niveau_ia_blanc = self.niveau_ia_blanc
                                        self.tournoi_en_cours = True

                        # Gestion des clics dans le menu des options
                        elif self.menu_actuel == "options":
                            for nom, rect in self.boutons_mode:
                                if rect.collidepoint(x, y):
                                    if nom == "2 joueurs":
                                        self.options["mode_jeu"] = "2_joueurs"
                                    elif nom == "Joueur vs IA":
                                        self.options["mode_jeu"] = "joueur_vs_ia"
                                    else:
                                        self.options["mode_jeu"] = "ia_vs_ia"
                                    break

                            # Sélection des niveaux IA
                            y_ia = 210
                            if self.options["mode_jeu"] == "joueur_vs_ia":
                                for idx, niveau in enumerate(self.niveaux_ia):
                                    rect = pygame.Rect(220 + idx*60, y_ia, 50, 40)
                                    if rect.collidepoint(x, y):
                                        self.niveau_ia_joueur = niveau
                            elif self.options["mode_jeu"] == "ia_vs_ia":
                                for idx, niveau in enumerate(self.niveaux_ia):
                                    rectN = pygame.Rect(250 + idx*60, y_ia, 50, 40)
                                    rectB = pygame.Rect(250 + idx*60, y_ia+50, 50, 40)
                                    if rectN.collidepoint(x, y):
                                        self.niveau_ia_noir = niveau
                                    if rectB.collidepoint(x, y):
                                        self.niveau_ia_blanc = niveau
                            y_pos = 310

                            # Gestion des options de fin de partie
                            for option, valeur in self.options.items():
                                if option != "mode_jeu":
                                    if 400 <= x <= 500 and y_pos <= y <= y_pos + 30:
                                        if isinstance(valeur, bool):
                                            self.options[option] = not valeur
                                        elif option == "seuil_defaite":
                                            self.options[option] = (valeur % 4) + 1
                                        elif option == "seuil_ecart_victoire":
                                            self.options[option] = (valeur % 5) + 2
                                    y_pos += 50

                            # Bouton retour au menu principal
                            if 300 <= x <= 500 and 500 <= y <= 550:
                                self.menu_actuel = "principal"

                # Gestion de la partie IA vs IA (simulation automatique/mode téléspectateur)
                if self.tournoi_en_cours and self.jeu_en_cours and not self.jeu_en_cours.partie_terminee:
                    jeu = self.jeu_en_cours
                    joueur = jeu.joueur_actuel
                    ia = jeu.ia1 if joueur == 1 else jeu.ia2
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

                    jeu.dessiner_plateau()
                    pygame.time.delay(200)

                # Affichage du plateau ou menu
                if self.jeu_en_cours:                  
                    self.jeu_en_cours.dessiner_plateau()
                else:                                  
                    if self.menu_actuel == "principal":
                        if not self.dessiner_menu_principal():
                            break
                    else:
                        if not self.dessiner_menu_options():
                            break

                pygame.time.delay(10)

        finally:
            pygame.quit()
    

if __name__ == "__main__":
    interface = Interface()
    interface.executer() 