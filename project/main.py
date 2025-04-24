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
walls = pygame.sprite.Group()
notification = classes.Notificationbar()
current_level = classes.CurrentLevel("level_1")
hero = classes.Hero(300, 400, enemies, walls, current_level)
background = classes.Background()
# debug = classes.Debugbar(hero)
gui_classes = [classes.Inventory, classes.Debugbar, classes.Notificationbar]
items_dict = dict()
enemy_dict = dict()
material_dict = dict()

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
        items_dict[item["name"]] = item_sprite


#-----------------------MATERIALS---------------------

def load_materials():
    global material_dict
    # material_dict["iron"] = classes.Material("IRON", "WHITE")
    # material_dict["platinum"] = classes.Material("PLATINUM", "BLACK")
    with open("./project/json/materials.json") as materials_file:
        materials_list = json.load(materials_file)
    for material in materials_list:
        cur_sprite = classes.Material(material["name"], material["texture"])
        material_dict[material["name"]] = cur_sprite

#-----------------------OTHER-------------------------

def load_enemies():
    global enemy_dict
    enemy_dict["enemy_1"] = (10, 2, 100, "heroin_shadow.png", {items_dict["boots"]: 50, items_dict["amulet"]: 30}, {material_dict["copper"]: 50, material_dict["bronze"]: 30})
    enemy_dict["enemy_2"] = (20, 2, 200, "heroin_shadow.png", {items_dict["scythe"]: 50, items_dict["hat"]: 30}, {material_dict["iron"]: 50, material_dict["steel"]: 30})
    enemy_dict["enemy_3"] = (50, 2, 300, "heroin_shadow.png", {items_dict["voodoo"]: 50, items_dict["ghost"]: 30}, {material_dict["platinum"]: 50, material_dict["diamond"]: 30})

def load_walls():
    walls.add(classes.Wall(0, 0, 30, 2200, walls))
    walls.add(classes.Wall(0, 1200, 30, 2200, walls))
    walls.add(classes.Wall(0, 0, 1200, 30, walls))
    walls.add(classes.Wall(2200, 0, 1200, 30, walls))
    for wall in walls:
        sprites.add(walls)

def load_level(level_name):
    global hero, sprites, enemy_list, debug, notification
    sprites = pygame.sprite.Group()

    with open("./project/json/levels.json") as levels_file:
        levels = json.load(levels_file)
    level = levels[level_name]

    for sprite in level:
        cur_sprite = None
        if sprite["name"] == "spawner":
            sprite["attributes"]["enemy"] = enemy_dict[sprite["attributes"]["enemy"]]
            cur_sprite = classes.Spawner(**sprite["attributes"], enemy_list=enemies, all_sprites=sprites)
        if sprite["name"] == "blacksmith":
            required_materials = dict()
            for material_name, count in sprite["attributes"]["required_materials"].items():
                required_materials[material_dict[material_name]] = count
            sprite["attributes"]["required_materials"] = required_materials
            cur_sprite = classes.Blacksmith(**sprite["attributes"], player=hero, notification=notification)
        if sprite["name"] == "portal":
            cur_sprite = classes.Portal(**sprite["attributes"], level_changer=current_level, player=hero)
        if sprite["name"] == "boss":
            sprite["attributes"]["minion"] = enemy_dict[sprite["attributes"]["minion"]]
            cur_sprite = classes.Boss(**sprite["attributes"], level_changer=current_level, player=hero, all_sprites=sprites)
        sprites.add(cur_sprite)

    load_walls()

    hero.rect.x = 300
    hero.rect.y = 400
    hero.camera[0] = 260
    hero.camera[1] = -40
  
    sprites.add(hero)
    sprites.add(hero.hp_bar)
    sprites.add(hero.attack_area)
    sprites.add(hero.inventory)
    # sprites.add(debug)
    sprites.add(notification)

def main():
    pygame.font.init()
    load_items()
    load_materials()
    load_enemies()
    load_level("level_1")
    run = True
    while run:
        if current_level.changed:
            if current_level.level_name == "end":
                pygame.quit()
                run = False
                break
            load_level(current_level.level_name)
            current_level.changed = False
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

        screen.fill((66, 245, 173))
        sprites.update()
        screen.blit(background.image, (background.rect.x + hero.camera[0], background.rect.y + hero.camera[1]))
        for sprite in sprites:
            if type(sprite) in gui_classes:
                screen.blit(sprite.image, sprite.rect.topleft)
                continue
            screen.blit(sprite.image, (sprite.rect.x + hero.camera[0], sprite.rect.y + hero.camera[1]))

        pygame.display.update()

        clock.tick(80)

if __name__ == "__main__":
    main()