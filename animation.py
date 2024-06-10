import pygame
import random
import time
import sys

# Initialiser Pygame
pygame.init()

# Paramètres de la fenêtre
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bomberman")

# Couleurs
WHITE = (200, 200, 200)
BLACK = (0, 128, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GREY = (128, 128, 128)
RED = (0, 0, 0)  # Nouvelle couleur pour les ennemis

# Taille de la grille
grid_size = 40
num_cols = screen_width // grid_size
num_rows = screen_height // grid_size

# Taille du personnage
player_size = 30

# Classe pour les murs
class Wall:
    def __init__(self, x, y, destructible):
        self.rect = pygame.Rect(x, y, grid_size, grid_size)
        self.destructible = destructible

    def draw(self):
        if self.destructible:
            pygame.draw.rect(screen, BLACK, self.rect)
            pygame.draw.line(screen, YELLOW, (self.rect.x, self.rect.y), (self.rect.x + grid_size, self.rect.y), 3)
            pygame.draw.line(screen, YELLOW, (self.rect.x, self.rect.y), (self.rect.x, self.rect.y + grid_size), 3)
            pygame.draw.line(screen, YELLOW, (self.rect.x + grid_size, self.rect.y + grid_size), (self.rect.x + grid_size, self.rect.y), 3)
            pygame.draw.line(screen, YELLOW, (self.rect.x + grid_size, self.rect.y + grid_size), (self.rect.x, self.rect.y + grid_size), 3)
        else:
            pygame.draw.rect(screen, GREY, self.rect)

# Classe pour le joueur
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, player_size, player_size)

    def draw(self):
        pygame.draw.circle(screen, BROWN, (self.rect.x + player_size // 2, self.rect.y + player_size // 2), player_size // 2)
        pygame.draw.circle(screen, GREY, (self.rect.x + player_size // 4, self.rect.y + player_size // 4), player_size // 8)
        pygame.draw.circle(screen, GREY, (self.rect.x + 3 * player_size // 4, self.rect.y + player_size // 4), player_size // 8)

    def move(self, dx, dy, walls):
        
        new_rect = self.rect.move(dx, dy)
        for wall in walls:
            if new_rect.colliderect(wall.rect):
                return  # ne pas effectuer le mouvement si colision avec un mur
        
        # possibilité d'avancer sans rencontre avec un mur
        self.rect.x += dx
        self.rect.y += dy

# Classe pour la bombe
class Bombe:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, grid_size, grid_size)
        self.start_time = time.time()
        self.exploded = False

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.rect.x + grid_size // 2, self.rect.y + grid_size // 2), grid_size // 2)

    def explode(self):
        explosion_group.add(Explosion(self.rect.x, self.rect.y))
        self.exploded = True

    def check_explosion(self):
        if self.exploded:
            bombes.remove(self)

# Classe pour l'explosion
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 5):
            img = pygame.image.load(f"explo{num}.png")
            img = pygame.transform.scale(img, (100, 100))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0
        self.speed = 4

    def update(self, walls, enemies):
        self.counter += 1
        if self.counter > self.speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        if self.index >= len(self.images) - 1 and self.counter >= self.speed:
            # Supprimer les murs destructibles touchés par l'explosion
            for wall in walls:
                if self.rect.colliderect(wall.rect) and wall.destructible:
                    walls.remove(wall)
            # Supprimer les ennemis touchés par l'explosion
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    enemies.remove(enemy)
            self.kill()


# Classe pour les ennemis
class Ennemi:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, player_size, player_size)
        self.direction = "left"

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)
        pygame.draw.circle(screen, BLACK, (self.rect.x + 10, self.rect.y + 10), 4)
        pygame.draw.circle(screen, BLACK, (self.rect.x + 20, self.rect.y + 10), 4)
        
        # Vitesse de l'ennemie programmer par cycle de jeu entant que une 1 unité

    def move(self, player_rect, walls):
        # Suivre le joueur
        if self.rect.x < player_rect.x:
            self.rect.x += 1
        elif self.rect.x > player_rect.x:
            self.rect.x -= 1
        if self.rect.y < player_rect.y:
            self.rect.y += 1
        elif self.rect.y > player_rect.y:
            self.rect.y -= 1

        # Vérifier les collisions avec les murs
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if wall.destructible:
                    
                    self.change_direction()
                else:
                    # ne pas traverser le mur
                    if self.direction == "left":
                        self.rect.x += 1
                    elif self.direction == "right":
                        self.rect.x -= 1
                    elif self.direction == "up":
                        self.rect.y += 1
                    elif self.direction == "down":
                        self.rect.y -= 1
                    break

    def change_direction(self):
        directions = ["left", "right", "up", "down"]
        directions.remove(self.direction)
        self.direction = random.choice(directions)

# Création de la liste des murs
walls = []
for col in range(num_cols):
    for row in range(num_rows):
        if random.random() < 0.2:  
            walls.append(Wall(col * grid_size, row * grid_size, True))
        elif random.random() < 0.1: 
            walls.append(Wall(col * grid_size, row * grid_size, False))

# Création de la liste des bombes
bombes = []

# Création du groupe d'explosions
explosion_group = pygame.sprite.Group()

# Création de la liste des ennemis
ennemis = []

# Afficher la surface
fenetre = pygame.display.set_mode((800, 800))
fenetre.fill(WHITE)

# Demande d'appuyer sur la touche "Entrée" pour démarrer le jeu
font = pygame.font.SysFont('Arial', 20)
start_text = font.render("Appuyez sur Entrée pour commencer", True, BLACK)
fenetre.blit(start_text, (200, 200))
pygame.display.flip()
waiting_for_start = True
while waiting_for_start:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            waiting_for_start = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                waiting_for_start = False

# Création du joueur
player = Player((num_cols // 2) * grid_size, (num_rows // 2) * grid_size)

#  le suivi du temps pour les ennemis
last_enemy_time = pygame.time.get_ticks()


# Boucle principale du jeu
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Création d'une bombe
                bombes.append(Bombe(player.rect.x, player.rect.y))
            elif event.key == pygame.K_o:  # Demander au joueur rejouer en appuyant sur la touche O (oui)
                # Réinitialiser le jeu
                walls = []
                for col in range(num_cols):
                    for row in range(num_rows):
                        if random.random() < 0.2: 
                            walls.append(Wall(col * grid_size, row * grid_size, True))
                        elif random.random() < 0.1:  
                            walls.append(Wall(col * grid_size, row * grid_size, False))
                player = Player((num_cols // 2) * grid_size, (num_rows // 2) * grid_size)
                ennemis = []
                for _ in range(1):
                    group_x = random.randint(0, screen_width - player_size)
                    group_y = random.randint(0, screen_height - player_size)
                    for _ in range(1):  
                        ennemis.append(Ennemi(group_x, group_y))
                last_enemy_time = pygame.time.get_ticks()
            elif event.key == pygame.K_n:  # Quitter le jeu si le joueur appuie sur la touche N (non)
                running = False

    # Déplacement du joueur
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move(-1, 0, walls)
    if keys[pygame.K_RIGHT]:
        player.move(1, 0, walls)
    if keys[pygame.K_UP]:
        player.move(0, -1, walls)
    if keys[pygame.K_DOWN]:
        player.move(0, 1, walls)

    # Limitation du déplacement du joueur aux dimensions de la fenêtre
    player.rect.x = max(0, min(player.rect.x, fenetre.get_width() - player_size))
    player.rect.y = max(0, min(player.rect.y, fenetre.get_height() - player_size))

    # Apparition des ennemis par groupe de deux toutes les 1000 millisecondes
    current_time = pygame.time.get_ticks()
    if current_time - last_enemy_time >= 1000:
        last_enemy_time = current_time
        
        for _ in range(1):
            group_x = random.randint(0, screen_width - player_size)
            group_y = random.randint(0, screen_height - player_size)
            for _ in range(1): 
                ennemis.append(Ennemi(group_x, group_y))

    # Effacement de l'écran
    fenetre.fill(WHITE)

    # Dessiner les murs
    for wall in walls:
        wall.draw()

    # Afficher le joueur
    player.draw()

    # Afficher les bombes
    for bombe in bombes:
        bombe.draw()

        # Miniteur d'explosion de la bombe
        if time.time() - bombe.start_time >= 2:
            bombe.explode()

        # Suppression de la bombe apres explosions
        bombe.check_explosion()

    # Afficher les explosions
    explosion_group.update(walls, ennemis)
    explosion_group.draw(fenetre)

    # Déplacer et afficher les ennemis
    for ennemi in ennemis:
        ennemi.move(player.rect, walls)
        ennemi.draw()

        # Vérifier la collision entre l'ennemi et le joueur
        if ennemi.rect.colliderect(player.rect):
            # Afficher un message pour demander au joueur s'il veut rejouer
            font = pygame.font.SysFont('Arial', 30)
            game_over_text = font.render("Game Over! Voulez-vous rejouer? (O/N)", True, BLACK)
            fenetre.blit(game_over_text, (screen_width // 2 - 250, screen_height // 2))
            pygame.display.flip()

            # Attendre la réponse du joueur
            waiting_for_response = True
            while waiting_for_response:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_o:
                            # Réinitialiser le jeu
                            walls = []
                            for col in range(num_cols):
                                for row in range(num_rows):
                                    if random.random() < 0.2:  
                                        walls.append(Wall(col * grid_size, row * grid_size, True))
                                    elif random.random() < 0.1:  
                                        walls.append(Wall(col * grid_size, row * grid_size, False))
                            player = Player((num_cols // 2) * grid_size, (num_rows // 2) * grid_size)
                            ennemis = []
                            for _ in range(2):  
                                group_x = random.randint(0, screen_width - player_size)
                                group_y = random.randint(0, screen_height - player_size)
                                for _ in range(2):  
                                    ennemis.append(Ennemi(group_x, group_y))
                            last_enemy_time = pygame.time.get_ticks()
                            waiting_for_response = False
                        elif event.key == pygame.K_n:
                            running = False
                            waiting_for_response = False


    # Mettre à jour l'affichage
    pygame.display.flip()

    # Régulation de la vitesse de la boucle
    pygame.time.Clock().tick(60)

# Quitter Pygame
pygame.quit()
