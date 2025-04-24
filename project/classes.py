import pygame
import time
from random import randint, choice

texture_cache = dict()

def add_texture(surface:pygame.Surface, name):
    cur_image = None
    if name in texture_cache.keys():
        cur_image = texture_cache[name]
    else:
        cur_image = pygame.image.load(f"./textures/{name}")
        texture_cache[name] = cur_image
    width = surface.get_width()
    height = surface.get_height()
    cur_image = pygame.transform.scale(cur_image, (width, height))
    surface.blit(cur_image, (0, 0))

class HPbar(pygame.sprite.Sprite):
    def __init__(self, owner, color, x, y, max_width, height):
        super().__init__()
        self.height = height
        self.max_width = max_width
        self.x = x
        self.y = y
        self.color = color
        self.owner = owner
        self.value = owner.rec_hp
        self.procent = int((self.owner.rec_hp/self.owner.max_hp) * self.max_width)
        self.image = pygame.Surface((self.procent, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(color)

    def check_hp(self):
        self.procent = int((self.owner.rec_hp/self.owner.max_hp) * self.max_width)
        if self.procent < 0:
            self.procent = 0

    def update(self, **kwargs):
        self.check_hp()
        self.image = pygame.Surface((self.procent, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.rect.x = self.owner.rect.x
        self.rect.y = self.owner.rect.y - 40

class Debugbar(pygame.sprite.Sprite):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.font = pygame.font.SysFont('Arial', 20)
        self.image = self.font.render('', False, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.text = ''

    def update(self, **kwargs):
        self.text = f'max_hp: {self.owner.max_hp}; rec_hp: {self.owner.rec_hp}'
        self.image = self.font.render(self.text, False, (255, 255, 255))
        self.rect = self.image.get_rect()

class Notificationbar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.SysFont('Arial', 20)
        self.image = self.font.render('', False, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = 650
        self.alpha = 0
        self.image.set_alpha(self.alpha)
    
    def set_text(self, text):
        self.image = self.font.render(text, False, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = 650
        self.alpha = 255
        self.image.set_alpha(self.alpha)

    def update(self):
        self.alpha = max(self.alpha - 5, 0)
        self.image.set_alpha(self.alpha)

class AttackArea(pygame.sprite.Sprite):
    def __init__(self, owner, attack_type):
        super().__init__()
        self.attack_type = attack_type
        self.color = "GREY"
        self.owner = owner
        self.width = 170
        self.height = 170
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.image.set_alpha(0)
        self.last_pressed_attack = time.perf_counter()

    def attack(self):
        if self.attack_type == "player":
            keys = pygame.key.get_pressed()
            if time.perf_counter() - self.last_pressed_attack >= self.owner.cd_attack:
                self.image.fill("GREY")
                if keys[pygame.K_1]:
                    for el in self.owner.enemy_list:
                        if self.rect.colliderect(el):
                            el.rec_hp -= self.owner.attack
                            el.who_attacked = self.owner

                    self.last_pressed_attack = time.perf_counter()
            else:
                self.image.fill("BLACK")
        
        if self.attack_type == "auto":
            if self.owner.who_attacked is not None and time.perf_counter() - self.last_pressed_attack >= self.owner.cd_attack and self.rect.colliderect(self.owner.who_attacked.rect):
                self.owner.who_attacked.rec_hp -= self.owner.attack
                        
                self.last_pressed_attack = time.perf_counter()
    
    def death(self):
        if self.owner.rec_hp <= 0:
            self.kill()

    def update(self, **kwargs):
        self.rect.center = self.owner.rect.center
        self.attack()
        self.death()

class Inventory(pygame.sprite.Sprite):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.image = pygame.Surface((800, 600), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 100
        add_texture(self.image, "inventory_background.png")
        self.items = []
        self.materials = {}
        self.length = 0
        self.open = False
        self.image.set_alpha(0)
        self.chosen_items = []
        self.selected_item = 0
        self.selection_surface = pygame.Surface((60, 60))
        self.selection_surface.fill((228, 242, 27))
        self.material_counter_surface = pygame.Surface((20, 14))
        self.material_counter_surface.fill("RED")
        self.material_counter_font = pygame.font.SysFont("Arial", 12, True)
        
    def open_close(self):
        if not self.open:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(0)
        
        self.open = not self.open
    
    def swap_items(self, ind):
        if ind >= self.length:
            return
        self.items[ind], self.items[self.selected_item] = self.items[self.selected_item], self.items[ind]

    def update(self):
        if self.length > 0:
            for keys, value in self.items[0].att.items():
                rec_stat = self.owner.__getattribute__(keys + "_default")
                self.owner.__setattr__(keys, rec_stat)
        for it in self.items[:min(self.length, 3)]:
            for keys, value in it.att.items():
                rec_stat = self.owner.__getattribute__(keys)
                self.owner.__setattr__(keys, rec_stat * value)
        self.length = len(self.items)

        x = 20
        y = 20

        add_texture(self.image, "inventory_background.png")

        for i in range(self.length):
            if i % 3 == 0:
                x = 20
                y += 70
            x += 70
            if i == self.selected_item:
                self.image.blit(self.selection_surface, (x - 5, y - 5))
            self.image.blit(self.items[i].image, (x, y))         
        
        x = 20
        y = 500

        for keys, value in self.materials.items():
            self.image.blit(keys.image, (x, y))
            self.image.blit(self.material_counter_surface, (x, y))
            self.image.blit(self.material_counter_font.render(str(value), False, "WHITE"), (x, y))
            x += 70

class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_list, wall_list, level_changer):
        super().__init__()
        self.inventory = Inventory(self)
        self.x = x
        self.y = y
        self.cd_attack = 1
        self.cd_attack_default = 1
        self.level = 0
        self.points = 0
        self.attack = 60
        self.attack_default = 60
        self.enemy_list = enemy_list
        self.wall_list = wall_list
        self.level_changer = level_changer
        self.width = 80
        self.height = 80
        self.color = "WHITE"
        self.set_texture("hero.png")
        self.rect = self.image.get_rect()
        self.speed = 5
        self.speed_default = 5
        self.max_hp = 100
        self.max_hp_default = 100
        self.rec_hp = 100
        self.rect.move_ip(x, y)
        self.hp_bar = HPbar(self, "GREEN", 0, self.x, 80, 20)
        self.attack_area = AttackArea(self, "player")
        self.camera = [260, -40]
        self.last_healed = 0
    
    def set_texture(self, texture):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        add_texture(self.image, texture)

    def death(self):
        if self.rec_hp > self.max_hp:
            self.rec_hp = self.max_hp
        if self.rec_hp > 0:
            return
        self.rec_hp = self.max_hp
        current_level = self.level_changer.level_name
        if current_level[-5:] == "_boss":
            current_level = current_level[:-5]
        self.level_changer.change_name(current_level)

    def return_if_collided(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.move_ip(self.speed, 0)
            self.camera[0] -= self.speed
        if keys[pygame.K_d]:
            self.rect.move_ip(-self.speed, 0)
            self.camera[0] += self.speed
        if keys[pygame.K_w]:
            self.rect.move_ip(0, self.speed)
            self.camera[1] -= self.speed
        if keys[pygame.K_s]:
            self.rect.move_ip(0, -self.speed)
            self.camera[1] += self.speed

    def move(self):
        keys = pygame.key.get_pressed()
        direction = 0
        vertical_direction = 0
        if keys[pygame.K_a]:
            self.rect.move_ip(-self.speed, 0)
            self.camera[0] += self.speed
            direction -= 1
        if keys[pygame.K_d]:
            self.rect.move_ip(self.speed, 0)
            self.camera[0] -= self.speed
            direction += 1
        if keys[pygame.K_w]:
            self.rect.move_ip(0, -self.speed)
            self.camera[1] += self.speed
            vertical_direction += 1
        if keys[pygame.K_s]:
            self.rect.move_ip(0, self.speed)
            self.camera[1] -= self.speed
            vertical_direction -= 1

        if direction < 0:
            self.set_texture("hero_left.png")
        elif direction > 0:
            self.set_texture("hero_right.png")
        elif vertical_direction > 0:
            self.set_texture("hero_up.png")
        else:
            self.set_texture("hero.png")

        for wall in self.wall_list:
            if pygame.Rect.colliderect(wall.rect, self.rect):
                self.return_if_collided()
                return
    
    def regenerate(self):
        if time.perf_counter() - self.last_healed >= 2:
            self.last_healed = time.perf_counter()
            self.rec_hp = min(self.max_hp, self.rec_hp + 10)

    def update(self, **kwargs):
        self.x = self.rect.x
        self.y = self.rect.y
        self.attack_area.update()
        self.regenerate()
        self.move()
        self.hp_bar.update()
        self.death()

class Spawner(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_cnt, enemy, enemy_list, all_sprites):
        super().__init__()
        self.x = x
        self.y = y
        self.enemy_cnt = enemy_cnt
        self.size = 400
        self.image = pygame.Surface((self.size, self.size))
        self.rect = self.image.get_rect()
        self.image.fill("BROWN")
        self.image.set_alpha(50)
        self.t = None
        self.enemies_spawned = 0
        self.enemy_list = enemy_list
        self.all_sprites = all_sprites
        self.enemy = enemy

    def check_spawn(self):
        if self.enemies_spawned == 0 and self.t is None:
            self.t = time.perf_counter()
        if self.t is not None and time.perf_counter() - self.t > 2:
            self.t = None
            for _ in range(self.enemy_cnt):
                random_x = self.x + randint(0, self.size - 100)
                random_y = self.y + randint(0, self.size - 100)
                enemy = Enemy(*self.enemy)
                enemy.spawn(self, random_x, random_y)
                self.all_sprites.add(enemy)
                self.all_sprites.add(enemy.hp_bar)
                self.all_sprites.add(enemy.attack_area)
                self.enemy_list.add(enemy)
                self.enemies_spawned += 1
    
    def update(self, **kwargs):
        self.rect.x = self.x
        self.rect.y = self.y
        self.check_spawn()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, attack, speed, hp, texture, items_chance:dict, materials_chance:dict):
        super().__init__()
        self.items_chance = items_chance
        self.attack = attack
        self.who_attacked = None
        self.speed = speed
        self.width = 80
        self.height = 80
        self.cd_attack = 1.5
        self.texture = texture
        self.max_hp = hp
        self.rec_hp = self.max_hp
        self.materials_chance = materials_chance

    def spawn(self, spawner, x, y):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        add_texture(self.image, self.texture)
        self.attack_area = AttackArea(self, "auto")
        self.spawner = spawner
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.hp_bar = HPbar(self, "Brown", x, y - 40 , 80, 20)

    def follow_and_check(self):
        if self.who_attacked is not None:
            if self.who_attacked.rect.x > self.rect.x:
                self.rect.x += self.speed
            elif self.who_attacked.rect.x < self.rect.x:
                self.rect.x -= self.speed
            
            if self.who_attacked.rect.y > self.rect.y:
                self.rect.y += self.speed
            elif self.who_attacked.rect.y < self.rect.y:
                self.rect.y -= self.speed
        
        distance = ((self.rect.x - self.spawner.rect.center[0])**2 + (self.rect.y - self.spawner.rect.center[1])**2) ** 0.5
        if distance > 400:
            self.rect.x, self.rect.y = self.spawner.rect.center[0], self.spawner.rect.center[1]
            self.who_attacked = None
            self.rec_hp = self.max_hp

    def death(self):
        if self.rec_hp <= 0:
            self.who_attacked.rec_hp += int(self.who_attacked.max_hp * 0.2)
            rec_item = choice(list(self.items_chance.keys()))
            if rec_item not in self.who_attacked.inventory.items and randint(1, 100) <= self.items_chance[rec_item]:
                self.who_attacked.inventory.items.append(rec_item)
            rec_material = choice(list(self.materials_chance.keys()))
            if randint(1, 100) <= self.materials_chance[rec_material]:
                if rec_material in self.who_attacked.inventory.materials.keys():
                    self.who_attacked.inventory.materials[rec_material] += 1
                else:
                    self.who_attacked.inventory.materials[rec_material] = 1
            self.spawner.enemies_spawned -= 1
            self.kill()

    def update(self, **kwargs):
        self.follow_and_check()
        self.death()
        self.attack_area.update()

class Minion(Enemy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def spawn(self, x, y):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        add_texture(self.image, "heroin_shadow.png")
        self.attack_area = AttackArea(self, "auto")
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.hp_bar = HPbar(self, "Brown", x, y - 40 , 80, 20)
    
    def follow_and_check(self):
        if self.who_attacked is not None:
            if self.who_attacked.rect.x > self.rect.x:
                self.rect.x += self.speed
            elif self.who_attacked.rect.x < self.rect.x:
                self.rect.x -= self.speed
            
            if self.who_attacked.rect.y > self.rect.y:
                self.rect.y += self.speed
            elif self.who_attacked.rect.y < self.rect.y:
                self.rect.y -= self.speed

    def death(self):
        if self.rec_hp > 0:
            return
        self.kill()

class Fireball(Enemy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def spawn(self, x, y):
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        add_texture(self.image, "fireball.png")
        self.attack_area = AttackArea(self, "auto")
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.hp_bar = HPbar(self, "Brown", x, y - 40 , 80, 20)
    
    def follow_and_check(self):
        if self.who_attacked is not None:
            if self.who_attacked.rect.x > self.rect.x:
                self.rect.x += self.speed
            elif self.who_attacked.rect.x < self.rect.x:
                self.rect.x -= self.speed
            
            if self.who_attacked.rect.y > self.rect.y:
                self.rect.y += self.speed
            elif self.who_attacked.rect.y < self.rect.y:
                self.rect.y -= self.speed

    def death(self):
        self.rec_hp -= self.max_hp / 350
        if self.rec_hp > 0:
            return
        self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, attack, speed, hp, minion, minion_count, fireball_count, level_name, level_changer, player, all_sprites):
        super().__init__()
        self.attack = attack
        self.max_hp = hp
        self.rec_hp = hp
        self.speed = speed
        self.cd_attack = 1
        self.attack_area = AttackArea(self, "auto")
        self.minion = minion
        self.minion_count = minion_count
        self.fireball_count = fireball_count
        self.level_name = level_name
        self.level_changer = level_changer
        self.who_attacked = player
        self.image = pygame.Surface((200, 200), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        add_texture(self.image, "boss.png")
        self.attack_area = AttackArea(self, "auto")
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.hp_bar = HPbar(self, "YELLOW", x, y - 40 , 180, 20)
        self.last_spawned = 0
        self.all_sprites = all_sprites
        self.player = player
        all_sprites.add(self.hp_bar)
        player.enemy_list.add(self)
    
    def spawn_minions(self):
        for _ in range(self.minion_count):
            random_x = self.x + randint(-300, 300)
            random_y = self.y + randint(-300, 300)
            enemy = Minion(*self.minion)
            enemy.spawn(random_x, random_y)
            enemy.who_attacked = self.player
            self.all_sprites.add(enemy)
            self.all_sprites.add(enemy.hp_bar)
            self.player.enemy_list.add(enemy)
        self.last_spawned = time.perf_counter()
    
    def spawn_fireballs(self):
        for _ in range(self.fireball_count):
            random_x = self.x + randint(-300, 300)
            random_y = self.y + randint(-300, 300)
            enemy = Fireball(10000, 2, 100, "hat.png", dict(), dict())
            enemy.spawn(random_x, random_y)
            enemy.who_attacked = self.player
            self.all_sprites.add(enemy)
            self.all_sprites.add(enemy.hp_bar)
            self.player.enemy_list.add(enemy)
        self.last_spawned = time.perf_counter()

    def follow_and_check(self):
        if self.who_attacked is not None:
            if self.who_attacked.rect.x > self.rect.x:
                self.rect.x += self.speed
            elif self.who_attacked.rect.x < self.rect.x:
                self.rect.x -= self.speed
            
            if self.who_attacked.rect.y > self.rect.y:
                self.rect.y += self.speed
            elif self.who_attacked.rect.y < self.rect.y:
                self.rect.y -= self.speed

    def random_attack(self):
        if time.perf_counter() - self.last_spawned < 10:
            return
        random_attack = randint(1, 2)
        if random_attack == 1:
            self.spawn_minions()
        else:
            self.spawn_fireballs()

    def death(self):
        if self.rec_hp > 0:
            return
        self.kill()
        portal = Portal(self.rect.x, self.rect.y, self.level_name, self.level_changer, self.player)
        self.all_sprites.add(portal)

    def update(self, **kwargs):
        self.x = self.rect.x
        self.y = self.rect.y
        self.follow_and_check()
        self.attack_area.update()
        self.random_attack()
        self.death()

class Blacksmith(pygame.sprite.Sprite):
    def __init__(self, x, y, coefficient, required_materials:dict, player, notification):
        super().__init__()
        self.required_materials = required_materials
        self.player = player
        self.traded = False
        self.image = pygame.surface.Surface((80, 80), pygame.SRCALPHA)
        add_texture(self.image, "blacksmith.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.coefficient = coefficient
        self.notification = notification
        self.traded_time = 0

    def check_collision(self):
        return pygame.Rect.colliderect(self.rect, self.player.rect)

    def update(self):
        if not self.check_collision():
            return
        keys = pygame.key.get_pressed()
        if not keys[pygame.K_e]:
            return
        if time.perf_counter() - self.traded_time < 1:
            return
        if self.traded:
            self.notification.set_text("You have already traded")
            return
        for material, count in self.required_materials.items():
            if self.player.inventory.materials.get(material, 0) < count:
                self.notification.set_text("Insufficient items")
                return
        self.traded = True
        for material, count in self.required_materials.items():
            self.player.inventory.materials[material] -= count
            if self.player.inventory.materials[material] == 0:
                self.player.inventory.materials.pop(material, None)
        self.player.max_hp_default = 100 * self.coefficient
        self.player.attack_default = 60 * self.coefficient
        self.notification.set_text("Equipment acquired")
        self.traded_time = time.perf_counter()

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y, level_name, level_changer, player):
        super().__init__()
        self.image = pygame.surface.Surface((80, 80), pygame.SRCALPHA)
        add_texture(self.image, "portal.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.level_name = level_name
        self.level_changer = level_changer
        self.player = player
    
    def check_collision(self):
        return pygame.Rect.colliderect(self.rect, self.player.rect)

    def update(self):
        if not self.check_collision():
            return
        keys = pygame.key.get_pressed()
        if not keys[pygame.K_e]:
            return
        self.level_changer.change_name(self.level_name)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, height, width, wall_list):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill("GREY")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        wall_list.add(self)

class Item(pygame.sprite.Sprite):
    def __init__(self, att:dict, texture):
        super().__init__()
        self.equipped = False
        self.att = att
        self.texture = texture
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        add_texture(self.image, self.texture)

class Material(pygame.sprite.Sprite):
    def __init__(self, name, texture):
        super().__init__()
        self.name = name
        self.texture = texture
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        add_texture(self.image, self.texture)

class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((2200, 1200), pygame.SRCALPHA)
        add_texture(self.image, "background.png")
        self.rect = self.image.get_rect()

class CurrentLevel():
    # a way to pass the current level's name to other classes and let them change it
    # changing the name of the level loads the other level
    def __init__(self, level_name):
        self.level_name = level_name
        self.changed = False
    
    def change_name(self, level_name):
        self.level_name = level_name
        self.changed = True