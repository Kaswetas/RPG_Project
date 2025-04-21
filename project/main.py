# self.cd_attack = 1
# self.attack = 60
# self.speed = 5
# self.max_hp = 100
# self.rec_hp = 100


import pygame
import classes
import time
import json
pygame.init()

screen = pygame.display.set_mode((1400, 800), pygame.SCALED)
pygame.display.set_caption("RPG")
pygame.display.set_icon(pygame.image.load("others/ну тупо я.webp"))
clock = pygame.time.Clock()
sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
items = pygame.sprite.Group()
hero = classes.Hero(300, 400, enemies)
items_dict = dict()
enemy_list = []

def load_items():
    with open("./project/json/items.json") as items_file:
        items_list = json.load(items_file)
    for item in items_list:
        item_sprite = classes.Item({
            "speed": item["speed"],
            "max_hp": item["max_hp"],
            "attack": item["attack"],
            "cd_attack": item["cd_attack"]
        }, item["texture"])
        items.add(item_sprite)
        items_dict[item["name"]] = item_sprite


#-----------------------MATERIALS---------------------

iron = classes.Material("IRON", "WHITE")

platina = classes.Material("PLATINA", "BLACK")

#-----------------------OTHER-------------------------

def load_enemies():
    global enemy_list
    enemy_list.append((10, 10, 2, 100, {items_dict["boots"]: 50, items_dict["amulet"]: 30}, {iron: 50}))

def load_level():
    global hero, sprites, enemy_list
    sprites = pygame.sprite.Group()
    spawner1 = classes.Spawner(100, 100, 3, enemy_list[0], enemies, sprites)
    spawner2 = classes.Spawner(700, 200, 2, enemy_list[0], enemies, sprites)
    sprites.add(spawner1)
    sprites.add(spawner2)

    hero.rect.x = 300
    hero.rect.y = 400
    hero.camera[0] = 260
    hero.camera[1] = -40

    sprites.add(hero)
    sprites.add(hero.exp_bar)
    sprites.add(hero.hp_bar)
    sprites.add(hero.attack_area)
    sprites.add(hero.inventory)

def main():
    load_items()
    load_enemies()
    load_level()
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
                        hero.attack_area.attack()

                    if event.key == pygame.K_LEFT:
                        hero.inventory.selected_item -= 1
                        if hero.inventory.selected_item < 0:
                            hero.inventory.selected_item = 0
                    if event.key == pygame.K_RIGHT:
                        hero.inventory.selected_item += 1
                        if hero.inventory.selected_item >= hero.inventory.length:
                            hero.inventory.selected_item = 0
                    
                    if event.key == pygame.K_1:
                        hero.inventory.swap_items(0)
                    if event.key == pygame.K_2:
                        hero.inventory.swap_items(1)
                    if event.key == pygame.K_3:
                        hero.inventory.swap_items(2)

        screen.fill("BLACK")
        sprites.update()
        for sprite in sprites:
            if type(sprite) == classes.EXPbar or type(sprite) == classes.Inventory:
                screen.blit(sprite.image, sprite.rect.topleft)
                continue
            screen.blit(sprite.image, (sprite.rect.x + hero.camera[0], sprite.rect.y + hero.camera[1]))

        pygame.display.update()

        clock.tick(80)

if __name__ == "__main__":
    main()