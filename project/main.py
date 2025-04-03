import pygame
import classes
import time
pygame.init()

screen = pygame.display.set_mode((1200, 800), pygame.SCALED)
pygame.display.set_caption("RPG")
pygame.display.set_icon(pygame.image.load("others/ну тупо я.webp"))
clock = pygame.time.Clock()
sprites = pygame.sprite.Group()
enemyes = pygame.sprite.Group()

spawner = classes.Spawner(100, 100, 3, enemyes, sprites)
sprites.add(spawner)

hero = classes.Hero(300, 400, enemyes)
sprites.add(hero)
sprites.add(hero.exp_bar)
sprites.add(hero.hp_bar)
sprites.add(hero.attack_area)

run = True
while run:
    print(hero.exp_bar.rect)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
    screen.fill("BLACK")
    sprites.draw(screen)
    sprites.update()
    pygame.display.update()

    clock.tick(80)