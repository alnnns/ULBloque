"""
Titre : Projet d'année Q1, ULBloqué.

Auteur : Sacha Alinia 

Matricule : 586702

Entrées :   - Un fichier texte contenant la configuration initiale de la grille 
            - Interactions de l'utilisateur via le clavier pour choisir une voiture et une direction (via la librairie getkey).

Sortie :   - Affichage en console de la grille de jeu mise à jour après chaque mouvement.
           - Messages indiquant les étapes du jeu, y compris les mouvements valides, les erreurs, et l'état final (victoire, défaite, abandon).

But :   - Faire sortir la voiture "A" (blanche) de la grille en atteignant la case de sortie dans un nombre limité de mouvements.
"""

import sys                              
from getkey import getkey


# ------------------------------------------------  Fonctions -----------------------------------------------------

def pos_cars(height, grille):
    """
    Entrée : - height (int) -> Hauteur de la grille.         
             - grille (list[str]) -> Représentation textuelle de la grille.
    Sortie : dict -> Dictionnaire avec les caractères des voitures comme clés 
                      et leurs positions sur la grille comme valeurs.
    But : Identifier les positions de chaque voiture dans la grille.
    """
    pos = {}

    for i in range(height):
        line = grille[i]                                 
        for j in range(1, len(line) - 1):  # Ignore les bordures de la grille.
            char = line[j] 
            if char != '.':  # Une voiture est détectée
                if char not in pos:
                    pos[char] = []  
                pos[char].append((j - 1, i))  # Stocke la position relative dans la grille.
    return pos


def sorted_dic(pos):
    """
    Entrée : pos (dict) -> Dictionnaire des positions des voitures.
    Sortie : dict -> Dictionnaire trié par ordre alphabétique des clés.
    But : Trier les clés du dictionnaire pour une représentation ordonnée.
    """
    keys = sorted(pos.keys())
    sorted_pos = {}

    for key in keys:
        sorted_pos[key] = pos[key]
    return sorted_pos

                                    
def cars_info(pos):
    """
    Entrée : pos (dict) -> Dictionnaire trié des positions des voitures.
    Sortie : list -> Liste contenant des informations sur chaque voiture 
                     [position initiale, direction, taille].
    But : Transformer les positions des voitures en informations structurées.
    """
    cars = []
    for car, positions in pos.items():
        positions.sort()

        if positions[0][0] == positions[1][0]:  # Voiture verticale
            direction = "v"
        else:  # Voiture horizontale
            direction = "h"

        cars.append([positions[0], direction, len(positions)])  # Stocke les informations structurées.
    
    return cars


def parse_game(game_file_path: str) -> dict:
    """
    Entrée : game_file_path (str) -> Chemin du fichier de jeu.
    Sortie : dict -> Dictionnaire contenant la largeur, hauteur, mouvements 
                     max, et informations sur les voitures.
    But : Analyser un fichier de jeu et créer une structure de données 
          représentant l'état initial du jeu.
    """
    game = {}

    # Lecture du fichier
    with open(game_file_path) as file:
        f = file.readlines()
    
    grille = []
    for line in f:
        if '+' not in line and '|' in line:  # Ignore les lignes de bordure.
            grille.append(line.strip())

    height = len(grille)  # Nombre de lignes dans la grille
    width = len(grille[0]) - 2  # Largeur sans les bordures verticales
    max_moves = int(f[-1].strip())  # Le dernier élément du fichier est le nombre max de mouvements.

    # Analyse des positions des voitures
    pos = pos_cars(height, grille)
    sorted_pos = sorted_dic(pos)
    cars = cars_info(sorted_pos)

    # Stockage des infos du jeu
    game['width'] = width
    game['height'] = height
    game['max_moves'] = max_moves
    game['cars'] = tuple(cars)
    
    return game


def grille_vide(width, height):
    """
    Entrée : - width (int) -> Largeur de la grille.
             - height (int) -> Hauteur de la grille.
    Sortie : list[list[str]] -> grille vide remplie de '.'.
    But : Créer une grille vide pour le jeu.
    """
    grille = []
    for i in range(height):
        ligne = []
        for j in range(width):
            ligne.append('.')
        grille.append(ligne)
    return grille     


def place_cars(grille, cars, colors, reset):
    """
    Entrée : - grille (list[list[str]]) -> grille vide.
             - cars (list) -> Liste des informations sur les voitures.
             - colors (list[str]) -> Liste des couleurs ANSI pour les voitures.
             - reset (str) -> Code ANSI pour réinitialiser la couleur.
    Sortie : list[list[str]] -> grille mise à jour avec les voitures placées.
    But : Placer les voitures sur la grille.
    """
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'    

    for elem, car_info in enumerate(cars):
        position, direction, size = car_info
        x, y = position
        
        if elem == 0:
            color = colors[0]  
        else:
            color = colors[(elem - 1) % (len(colors) - 1) + 1] 
        
        for i in range(size):
            if direction == 'h':  # Horizontal
                grille[y][x + i] = f"{color}{letters[elem]}{reset}"
            elif direction == 'v':  # Vertical
                grille[y + i][x] = f"{color}{letters[elem]}{reset}"
    return grille


def build_grille_string(grille, cars, width, height):
    """
    Entrée : - grille (list[list[str]]) -> grille avec les voitures placées.
             - cars (list) -> Liste des informations sur les voitures.
             - width (int) -> Largeur de la grille.
             - height (int) -> Hauteur de la grille.
    Sortie : str -> Représentation textuelle de la grille.
    But : Construire une chaîne de caractères représentant la grille de jeu avec des barres continues comme contours.
    """
    largeur = len(grille[0])  # Longueur d'une ligne de la grille
    bordure = "┌" + "─" * largeur + "┐\n"  # Bordure du haut
    grille_str = bordure
    for i, ligne in enumerate(grille):
        if i == cars[0][0][1]:  # Ligne avec la sortie
            grille_str += "│" + ''.join(ligne) + " -> |EXIT|\n"
        else:
            grille_str += "│" + ''.join(ligne) + "│\n"
    grille_str += "└" + "─" * largeur + "┘"  # Bordure du bas
    return grille_str


def get_game_str(game: dict, current_move_number: int) -> str:
    """
    Entrée : - game (dict) -> Dictionnaire contenant l'état actuel du jeu.
             - current_move_number (int) -> Nombre de mouvements effectués jusqu'à présent.
    Sortie : str -> Représentation textuelle complète de l'état du jeu.
    But : Générer une description textuelle de la grille et des informations sur les mouvements restants.
    """
    width = game['width']
    height = game['height']
    max_moves = game['max_moves']
    cars = game['cars']

    grille = grille_vide(width, height)

    # Définir les couleurs des voitures
    colors = [
        "\u001b[47m",  # Blanc
        "\u001b[41m",  # Rouge
        "\u001b[42m",  # Vert
        "\u001b[43m",  # Jaune
        "\u001b[44m",  # Bleu
        "\u001b[45m",  # Magenta
        "\u001b[46m"   # Cyan
    ]
    
    reset = "\u001b[0m"  # Réinitialisation 
    
    grille = place_cars(grille, cars, colors, reset)
    grille_str = build_grille_string(grille, cars, width, height)

    moves_info = (f'\nMouvements maximums : {max_moves}\n'
                  f'Mouvements effectués : {current_move_number}\n'
                  f'Mouvements restants : {max_moves - current_move_number}\n')

    return grille_str + '\n' + moves_info


def car_positions(car: tuple) -> list:
    """
    Entrée : car (tuple) -> Informations sur une voiture (position initiale, direction, taille).
    Sortie : list[tuple] -> Liste des positions occupées par la voiture.
    But : Déterminer les positions exactes sur la grille occupées par une voiture donnée.
    """
    position, direction, size = car
    x, y = position

    if direction == "h":
        return [(x + i, y) for i in range(size)]
    
    elif direction == "v":
        return [(x, y + i) for i in range(size)]


def new_positions(x, y, direction, size):
    """
    Entrée : - x (int), y (int) -> Position initiale de la voiture.
             - direction (str) -> Direction du mouvement ("UP", "DOWN", "LEFT", "RIGHT").
             - size (int) -> Taille de la voiture.
    Sortie : list[tuple] -> Liste des nouvelles positions après le déplacement.
    But : Calculer les nouvelles positions occupées par une voiture après un mouvement donné.
    """
    if direction == "UP":
        return [(x, y - 1 + i) for i in range(size)]
    
    elif direction == "DOWN":
        return [(x, y + 1 + i) for i in range(size)]
    
    elif direction == "LEFT":
        return [(x - 1 + i, y) for i in range(size)]
    
    elif direction == "RIGHT":
        return [(x + 1 + i, y) for i in range(size)]
    return []


def limits_grille(game, new_positions):
    """
    Entrée : - game (dict) -> Dictionnaire contenant les dimensions de la grille.
             - new_positions (list[tuple]) -> Liste des nouvelles positions d'une voiture.
    Sortie : bool -> True si une position est hors de la grille, sinon False.
    But : Vérifier si une voiture dépasse les limites de la grille après un déplacement.
    """
    width, height = game['width'], game['height']
    for x, y in new_positions:
        if x < 0 or x >= width or y < 0 or y >= height:
            return True
    return False


def collision(cars, car_index, new_positions):
    """
    Entrée : - cars (list) -> Liste des informations sur toutes les voitures.
             - car_index (int) -> Index de la voiture en déplacement.
             - new_positions (list[tuple]) -> Nouvelles positions de la voiture.
    Sortie : bool -> True s'il y a une collision avec une autre voiture, sinon False.
    But : Détecter les collisions entre voitures après un déplacement.
    """
    for m, n in enumerate(cars):
        if m != car_index:
            other_positions = car_positions(n)
            for pos in new_positions:
                if pos in other_positions:
                    return True
    return False


def move_car(game: dict, car_index: int, direction: str) -> bool:
    """
    Entrée : - game (dict) -> Dictionnaire contenant l'état actuel du jeu.
             - car_index (int) -> Index de la voiture à déplacer.
             - direction (str) -> Direction du déplacement ("UP", "DOWN", "LEFT", "RIGHT").
    Sortie : bool -> True si le déplacement est réussi, sinon Falsen.
    But : Déplacer une voiture dans une direction donnée en vérifiant les limites et les collisions.
    """
    cars = list(game['cars'])
    car = cars[car_index]
    position, car_direction, size = car
    x, y = position

    if (direction in ["UP", "DOWN"] and car_direction != "v") or \
       (direction in ["LEFT", "RIGHT"] and car_direction != "h"):
        return False  # Mouvement invalide

    new_pos = new_positions(x, y, direction, size)
    
    if limits_grille(game, new_pos):
        return False  # Mouvement hors de la grille

    if collision(cars, car_index, new_pos):
        return False  # Collision détectée

    # Appliquer le mouvement
    cars[car_index] = (new_pos[0], car_direction, size)
    game['cars'] = tuple(cars)  # Mettre à jour les voitures dans le jeu
    return True    


def is_win(game: dict) -> bool:
    """
    Entrée : game (dict) -> Dictionnaire contenant l'état actuel du jeu.
    Sortie : bool -> True si la voiture principale (A) atteint la sortie, False sinon.
    But : Vérifier si le joueur a gagné en atteignant la sortie.
    """
    car_A = game['cars'][0]
    position, direction, size = car_A

    if direction == 'h':
        exit = game['width'] - 1  
        for x, y in car_positions(car_A):
            if x == exit: 
                return True
    return False


def play_game(game: dict) -> int:
    """
    Entrée : game (dict) -> Dictionnaire contenant les données initiales et actuelles du jeu.
    Sortie : int -> Résultat du jeu (0 si victoire, 1 si mouvements épuisés, 2 si le joueur abandonne).
    But : Gérer la boucle principale du jeu en permettant de sélectionner une voiture, enchaîner des mouvements,
          et changer directement de voiture ou direction sans manipulation supplémentaire.
    """
    current_move_number = 0
    selected_car = None  # Voiture actuellement sélectionnée

    print("\n\nSélectionnez une voiture (A-H), puis utilisez les flèches pour la déplacer.\n")

    while current_move_number < game['max_moves']:
        print(get_game_str(game, current_move_number))  # Afficher l'état du jeu

        # Lire la touche de l'utilisateur
        key = getkey().strip().upper()  # Nettoyer l'entrée (supprimer espaces, retours à la ligne, etc.)

        # Si l'utilisateur appuie sur ESCAPE, il quitte le jeu immédiatement
        if key == 'ESCAPE':
            return 2

        # Si l'utilisateur choisit une voiture (A-H)
        if len(key) == 1 and 'A' <= key <= 'H':
            selected_car = key
            car_index = ord(selected_car) - ord('A')  # Calculer l'index de la voiture
            print(f"Voiture {selected_car} sélectionnée. Utilisez les flèches pour la déplacer.")
            continue

        # Si une voiture est sélectionnée et l'utilisateur appuie sur une direction
        if selected_car and key in ["UP", "DOWN", "LEFT", "RIGHT"]:
            direction = key
            while True:
                # Tenter de déplacer la voiture dans la direction spécifiée
                if move_car(game, car_index, direction):
                    current_move_number += 1
                    print(f"Voiture {selected_car} déplacée vers {direction}.")
                    print(get_game_str(game, current_move_number))

                    # Victoire
                    if is_win(game):
                        return 0

                    # Défaite
                    if current_move_number >= game['max_moves']:
                        print(get_game_str(game, current_move_number))
                        return 1

                    # Lire la prochaine touche
                    next_key = getkey().strip().upper()

                    # Abandon
                    if next_key == 'ESCAPE':
                        return 2

                    # Si la prochaine touche est différente, changer immédiatement
                    if next_key != direction:
                        if len(next_key) == 1 and 'A' <= next_key <= 'H':  # Changer de voiture
                            selected_car = next_key
                            car_index = ord(selected_car) - ord('A')
                            print(f"Changement vers la voiture {selected_car}.\n")
                            break
                        elif next_key in ["UP", "DOWN", "LEFT", "RIGHT"]:  # Changer de direction
                            direction = next_key
                            continue
                        else:
                            print("Entrée invalide.")
                            break
                else:
                    print(f"Impossible de déplacer la voiture {selected_car} vers {direction}.")
                    break

        else:
            print("Entrée invalide. Sélectionnez une voiture (A-H) ou utilisez les flèches pour la déplacer.")



# ----------------------------------------------------- Main -------------------------------------------------------

def main():
    game = parse_game(sys.argv[1])

    print('\nBIENVENUE DANS LE JEU ULBLOQUE !\n\n')
    print('Le but est de faire sortir la voiture A (blanche) en atteignant la sortie.')
    print('Vous avez un maximum de 40 mouvements pour y arriver.')

    result = play_game(game)

    if result == 0:
        print('Félicitations, vous avez gagné ! ')
    elif result == 1:
        print('Vous avez perdu, vous avez dépassé le nombre maximum de mouvements.')
    elif result == 2:
        print('Vous avez abandonné la partie.')



# ------------------------------------------------- Corps du code -------------------------------------------------

if __name__ == '__main__':
    main()