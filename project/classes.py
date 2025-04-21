import pygame
import time
from random import randint, choice

class EXPbar(pygame.sprite.Sprite):
    def __init__(self, x, y, owner):
        super().__init__()
        self.x = x
        self.y = y
        self.owner = owner
        self.procent = int((owner.exp / owner.max_exp) * 1400)
        self.height = 40
        self.image = pygame.Surface((self.procent, self.height))
        self.rect = self.image.get_rect()
        self.image.fill("YELLOW")
    
    def update(self, **kwargs):
        self.procent = int((self.owner.exp / self.owner.max_exp) * 1200)
        self.image = pygame.Surface((self.procent, self.height))
        self.rect = self.image.get_rect()
        self.image.fill("YELLOW")
        self.rect.x = self.x
        self.rect.y = self.y

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
        self.image.set_alpha(120)
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
                        
                        if el.rec_hp <= 0:
                            el.get_exp(self.owner)
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
        self.image = pygame.Surface((800, 600))
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 100
        self.image.fill("BROWN")
        self.items = []
        self.materials = {}
        self.length = 0
        self.open = False
        self.image.set_alpha(0)
        self.chosen_items = []
        self.selected_item = 0
        self.selection_surface = pygame.Surface((60, 60))
        self.selection_surface.fill((228, 242, 27))
        
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

        self.image.fill("BROWN")
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
        for keys, value in enumerate(self.materials):
            self.image.blit(value.image, (x, y))
            x += 70

class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_list):
        super().__init__()
        self.inventory = Inventory(self)
        self.x = x
        self.y = y
        self.cd_attack = 1
        self.cd_attack_default = 1
        self.level = 0
        self.points = 0
        self.exp = 0
        self.max_exp = 20
        self.attack = 60
        self.attack_default = 60
        self.enemy_list = enemy_list
        self.width = 80
        self.height = 80
        self.color = "WHITE"
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.speed = 5
        self.speed_default = 5
        self.max_hp = 100
        self.max_hp_default = 100
        self.rec_hp = 100
        self.rect.move_ip(x, y)
        self.exp_bar = EXPbar(0, 0, self)
        self.hp_bar = HPbar(self, "GREEN", 0, self.x, 80, 20)
        self.attack_area = AttackArea(self, "player")
        self.camera = [260, -40]
    
    def death(self):
        if self.rec_hp <= 0:
            self.kill()
        if self.rec_hp > self.max_hp:
            self.rec_hp = self.max_hp

    def exp_check(self):
        if self.exp >= self.max_exp:
            self.level += 1
            self.points += 1
            self.exp = self.exp % self.max_exp
            self.max_exp = int(self.max_exp * 1.5)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.move_ip(-self.speed, 0)
            self.camera[0] += self.speed
        if keys[pygame.K_d]:
            self.rect.move_ip(self.speed, 0)
            self.camera[0] -= self.speed
        if keys[pygame.K_w]:
            self.rect.move_ip(0, -self.speed)
            self.camera[1] += self.speed
        if keys[pygame.K_s]:
            self.rect.move_ip(0, self.speed)
            self.camera[1] -= self.speed
        
    def update(self, **kwargs):
        self.x = self.rect.x
        self.y = self.rect.y
        self.attack_area.update()
        self.exp_check()
        self.move()
        self.hp_bar.update()
        self.exp_bar.update()
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
        self.all_sprites = all_sprites
        self.enemy = enemy
        self.enemy_list = enemy_list

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
                self.enemy_list.add(enemy)
                self.all_sprites.add(enemy)
                self.all_sprites.add(enemy.hp_bar)
                self.all_sprites.add(enemy.attack_area)
                self.enemies_spawned += 1
    
    def update(self, **kwargs):
        self.rect.x = self.x
        self.rect.y = self.y
        self.check_spawn()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, attack, exp, speed, hp, items_chance:dict, materials_chance:dict):
        super().__init__()
        self.items_chance = items_chance
        self.attack = attack
        self.who_attacked = None
        self.give_exp = exp
        self.speed = speed
        self.width = 80
        self.height = 80
        self.cd_attack = 1.5
        self.color = "RED"
        self.max_hp = hp
        self.rec_hp = self.max_hp
        self.materials_chance = materials_chance

    def spawn(self, spawner, x, y):
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.attack_area = AttackArea(self, "auto")
        self.spawner = spawner
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.hp_bar = HPbar(self, "Brown", x, y - 40 , 80, 20)

    def get_exp(self, hero):
        hero.exp += self.give_exp

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

class Item(pygame.sprite.Sprite):
    def __init__(self, att:dict, texture):
        super().__init__()
        self.equipped = False
        self.att = att
        self.texture = texture
        self.image = pygame.Surface((50, 50))
        self.rect = self.image.get_rect()
        self.image.fill(texture)

class Material(pygame.sprite.Sprite):
    def __init__(self, name, texture):
        super().__init__()
        self.name = name
        self.texture = texture
        self.image = pygame.Surface((50, 50))
        self.rect = self.image.get_rect()
        self.image.fill(texture)