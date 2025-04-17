import pygame
import classes
import time
pygame.init()

screen = pygame.display.set_mode((1400, 800), pygame.SCALED)
pygame.display.set_caption("RPG")
pygame.display.set_icon(pygame.image.load("others/ну тупо я.webp"))
clock = pygame.time.Clock()
sprites = pygame.sprite.Group()
enemyes = pygame.sprite.Group()

boots = classes.Item({"speed": 10,
                        "cd_attack": -0.5}, "WHITE")
sword = classes.Item({"max_hp": 50,
                      "attack": 50}, "BLACK")

spawner1 = classes.Spawner(100, 100, 3, enemyes, sprites, 10, 5, 2, 100, {boots: 100,
                                                                          sword: 100})
spawner2 = classes.Spawner(700, 200, 2, enemyes, sprites, 25, 10, 2, 200, {boots: 100})
sprites.add(spawner1)
sprites.add(spawner2)


hero = classes.Hero(300, 400, enemyes)
sprites.add(hero)
sprites.add(hero.exp_bar)
sprites.add(hero.hp_bar)
sprites.add(hero.attack_area)
sprites.add(hero.inventory)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    hero.inventory.open_close()
                if event.key == pygame.K_1:
                    hero.attack_event()
    screen.fill("BLACK")
    sprites.update()
    for sprite in sprites:
        if type(sprite) == classes.EXPbar or type(sprite) == classes.Inventory:
            screen.blit(sprite.image, sprite.rect.topleft)
            continue
        screen.blit(sprite.image, (sprite.rect.x + hero.camera[0], sprite.rect.y + hero.camera[1]))

    pygame.display.update()

    clock.tick(80)