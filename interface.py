import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys
from typing import Dict, Any, List, Tuple
from hasami_shogi import HasamiShogi

class Interface:
    def __init__(self):
        try:
            # Initialisation de Pygame
            pygame.init()
            
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
            
            # Options de jeu
            self.options = {
                "mode_jeu": "2_joueurs",  # "2_joueurs", "ia_minimax", "ia_alpha_beta"
                "capture_diagonale": False,
                "capture_multiple_corners": True,
                "seuil_defaite": 2,
                "seuil_ecart_victoire": 3
            }
            
            # Boutons du menu principal
            self.boutons = {
                "jouer": pygame.Rect(300, 200, 200, 50),
                "options": pygame.Rect(300, 300, 200, 50),
                "quitter": pygame.Rect(300, 400, 200, 50)
            }
            
            # Boutons du mode de jeu
            self.boutons_mode = [
                ("2 joueurs", pygame.Rect(50, 150, 200, 40)),
                ("IA (Minimax)", pygame.Rect(300, 150, 200, 40)),
                ("IA (Alpha-Beta)", pygame.Rect(550, 150, 200, 40))
            ]
            
            # État du menu
            self.menu_actuel = "principal"  # "principal" ou "options"
        except Exception as e:
            print(f"Erreur lors de l'initialisation : {e}")
            sys.exit(1)
    
    def dessiner_menu_principal(self):
        """Dessine le menu principal."""
        try:
            self.fenetre.fill(self.BLANC)
            
            # Titre
            titre = self.police.render("Hasami Shogi", True, self.NOIR)
            self.fenetre.blit(titre, (self.largeur//2 - titre.get_width()//2, 100))
            
            # Boutons
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
        """Dessine le menu des options."""
        try:
            self.fenetre.fill(self.BLANC)
            
            # Titre
            titre = self.police.render("Options", True, self.NOIR)
            self.fenetre.blit(titre, (self.largeur//2 - titre.get_width()//2, 50))
            
            # Mode de jeu
            texte = self.police.render("Mode de jeu:", True, self.NOIR)
            self.fenetre.blit(texte, (50, 100))
            
            # Boutons du mode de jeu
            for nom, rect in self.boutons_mode:
                mode_correspondant = "2_joueurs" if nom == "2 joueurs" else f"ia_{nom.lower().split('(')[1].split(')')[0]}"
                couleur = self.VERT if self.options["mode_jeu"] == mode_correspondant else self.BLEU
                pygame.draw.rect(self.fenetre, couleur, rect)
                texte = self.police.render(nom, True, self.BLANC)
                self.fenetre.blit(texte, (rect.centerx - texte.get_width()//2,
                                        rect.centery - texte.get_height()//2))
            
            # Autres options
            y = 250
            for option, valeur in self.options.items():
                if option != "mode_jeu":
                    # Texte de l'option
                    texte = self.police.render(option.replace("_", " ").capitalize(), True, self.NOIR)
                    self.fenetre.blit(texte, (50, y))
                    
                    # Bouton pour modifier
                    if isinstance(valeur, bool):
                        couleur = self.VERT if valeur else self.ROUGE
                        pygame.draw.rect(self.fenetre, couleur, (400, y, 100, 30))
                        texte_valeur = self.police.render(str(valeur), True, self.BLANC)
                    else:
                        pygame.draw.rect(self.fenetre, self.GRIS, (400, y, 100, 30))
                        texte_valeur = self.police.render(str(valeur), True, self.NOIR)
                    
                    self.fenetre.blit(texte_valeur, (420, y))
                    y += 50
            
            # Bouton retour
            pygame.draw.rect(self.fenetre, self.BLEU, (300, 500, 200, 50))
            texte = self.police.render("Retour", True, self.BLANC)
            self.fenetre.blit(texte, (350, 515))
            
            pygame.display.flip()
            return True
        except Exception as e:
            print(f"Erreur lors du dessin du menu options : {e}")
            return False
    
    def executer(self):
        """Boucle principale de l'interface."""
        try:
            en_cours = True
            while en_cours:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        en_cours = False
                        break
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos
                        
                        if self.menu_actuel == "principal":
                            # Vérifier les clics sur les boutons du menu principal
                            for nom, rect in self.boutons.items():
                                if rect.collidepoint(x, y):
                                    if nom == "jouer":
                                        # Lancer le jeu avec les options actuelles
                                        mode_jeu = self.options["mode_jeu"]
                                        niveau_ia = mode_jeu.split("_")[1] if mode_jeu != "2_joueurs" else "minimax"
                                        jeu = HasamiShogi(mode_jeu=mode_jeu, niveau_ia=niveau_ia)
                                        for option, valeur in self.options.items():
                                            if option not in ["mode_jeu"]:
                                                setattr(jeu, option, valeur)
                                        jeu.executer()
                                        # Réinitialiser l'affichage après le jeu
                                        self.fenetre = pygame.display.set_mode((self.largeur, self.hauteur))
                                    elif nom == "options":
                                        self.menu_actuel = "options"
                                    elif nom == "quitter":
                                        en_cours = False
                                        break
                        
                        elif self.menu_actuel == "options":
                            # Vérifier les clics sur les boutons de mode de jeu
                            for nom, rect in self.boutons_mode:
                                if rect.collidepoint(x, y):
                                    mode_correspondant = "2_joueurs" if nom == "2 joueurs" else f"ia_{nom.lower().split('(')[1].split(')')[0]}"
                                    self.options["mode_jeu"] = mode_correspondant
                                    break
                            
                            # Vérifier les autres options
                            y_pos = 250
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
                            
                            # Vérifier le bouton retour
                            if 300 <= x <= 500 and 500 <= y <= 550:
                                self.menu_actuel = "principal"
                
                # Dessiner le menu approprié
                if self.menu_actuel == "principal":
                    if not self.dessiner_menu_principal():
                        break
                else:
                    if not self.dessiner_menu_options():
                        break
                
                # Petit délai pour éviter une utilisation excessive du CPU
                pygame.time.delay(10)
        
        finally:
            # Nettoyage propre de Pygame
            pygame.quit()

if __name__ == "__main__":
    interface = Interface()
    interface.executer() 