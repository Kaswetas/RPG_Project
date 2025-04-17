import pygame
import time
from random import randint, choice

from pygame import Vector2


class EXPbar(pygame.sprite.Sprite):
    max_exp = 20
    height = 40
    level = 0
    upgrade_hp_list = [1.1, 1.2, 1.1, 1.3, 1.5]
    upgrade_damage_list = [1.2, 1.15, 1.1, 1.3, 1.5]

    def __init__(self, hero):
        super().__init__()
        self.exp = 0
        self.hero = hero
        self.procent = None

        self.update()

    def update(self):
        self.procent = int((self.exp / self.max_exp) * 1200)
        self.image = pygame.Surface((self.procent, self.height))
        self.rect = self.image.get_rect()
        self.image.fill("GOLD")
        if self.exp >= self.max_exp:
            self.level += 1
            self.exp = self.exp % self.max_exp
            self.max_exp = int(self.max_exp * 1.5)

            self.hero.attack = int(self.hero.attack * 1.3)
            self.hero.max_hp = int(self.hero.max_hp * 1.2)
            self.hero.hp = self.hero.max_hp


class HPbar(pygame.sprite.Sprite):
    def __init__(self, owner, color, x, y, max_width, height):
        super().__init__()
        self.procent = None
        self.height = height
        self.max_width = max_width
        self.pos = Vector2(x, y)
        self.color = color
        self.owner = owner
        self.update()

    def check_hp(self):
        self.procent = int((self.owner.hp / self.owner.max_hp) * self.max_width)
        self.procent = (abs(self.procent) + self.procent) / 2

    def update(self):
        self.check_hp()
        self.image = pygame.Surface((self.procent, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.rect.x = self.owner.rect.x
        self.rect.y = self.owner.rect.y - 40


class AttackArea(pygame.sprite.Sprite):
    width = 170
    height = 170

    def __init__(self, owner, attack_type):
        super().__init__()
        self.attack_type = attack_type
        self.color = "GREY"
        self.owner = owner
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.image.set_alpha(120)
        self.last_pressed_attack = time.perf_counter()

    def change_color(self):
        if time.perf_counter() - self.owner.last_pressed_attack >= self.owner.cd_attack:
            self.image.fill("GREY")
        else:
            self.image.fill("BLACK")

    def attack(self):
        if self.attack_type == "auto":
            if self.owner.who_attacked is not None and time.perf_counter() - self.last_pressed_attack >= self.owner.cd_attack and self.rect.colliderect(
                    self.owner.who_attacked.rect):
                self.owner.who_attacked.hp -= self.owner.attack

                self.last_pressed_attack = time.perf_counter()

    def death(self):
        if self.owner.hp <= 0:
            self.kill()

    def update(self):
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
        self.length = 0
        self.open = False
        self.image.set_alpha(0)
    
    def open_close(self):
        if not self.open:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(0)
        
        self.open = not self.open
    
    def update(self):
        if len(self.items) > self.length:
            for it in self.items[:self.length - 1]:
                for keys, value in it.att.items():
                    rec_stat = self.owner.__getattribute__(keys)
                    self.owner.__setattr__(keys, rec_stat + value)
            self.length = len(self.items)

        x = 20
        y = 20

        for i in range(self.length):
            if i % 3 == 0:
                x = 20
                y += 70
            x += 70
            self.image.blit(self.items[i].image, (x, y))


class Hero(pygame.sprite.Sprite):
    width = 80
    height = 80
    color = 'WHITE'

    def __init__(self, x, y, enemy_list):
        super().__init__()

        self.image = pygame.Surface((Hero.width, Hero.height))
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.rect.move_ip(x, y)
        self.camera = Vector2(260, -40)

        self.pos = Vector2(x, y)
        self.speed = 5

        self.cd_attack = 1
        self.attack = 60
        self.attack_area = AttackArea(self, "player")

        self.max_hp = 100
        self.hp = self.max_hp
        self.hp_bar = HPbar(self, "GREEN", 0, self.pos.x, 80, 20)

        self.exp_bar = EXPbar(self)

        self.enemy_list = enemy_list

        self.inventory = Inventory(self)

        self.last_pressed_attack = time.perf_counter()
    
    def death(self):
        if self.hp <= 0:
            self.kill()

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
        self.pos.x, self.pos.y = self.rect.x, self.rect.y
        self.attack_event()
        self.move()
        self.death()

    def attack_event(self):
        self.attack_area.change_color()
        if time.perf_counter() - self.last_pressed_attack >= self.cd_attack:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                for el in self.enemy_list:
                    if self.attack_area.rect.colliderect(el):
                        el.hp -= self.attack
                        el.who_attacked = self
                    if el.hp <= 0:
                        el.get_exp()
                self.last_pressed_attack = time.perf_counter()


class Spawner(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_cnt, enemyes, sprites, enemy_attack, enemy_exp, enemy_speed, enemy_hp, items_chance):
        super().__init__()
        self.items_chance = items_chance
        self.x = x
        self.y = y
        self.enemy_cnt = enemy_cnt
        self.size = 400
        self.enemy_attack = enemy_attack
        self.enemy_exp = enemy_exp
        self.enemy_speed = enemy_speed
        self.enemy_hp = enemy_hp
        self.image = pygame.Surface((self.size, self.size))
        self.rect = self.image.get_rect()
        self.image.fill("BROWN")
        self.image.set_alpha(50)
        self.enemyes_group = enemyes
        self.all_sprites = sprites
        self.t = None
        self.spawns_enemyes = []

    def check_spawn(self):
        if len(self.spawns_enemyes) == 0 and self.t is None:
            self.t = time.perf_counter()
        if self.t is not None and time.perf_counter() - self.t > 2:
            self.t = None
            for _ in range(self.enemy_cnt):
                enemy = Enemy(self, self.x + randint(0, self.size - 100), self.y + randint(0, self.size - 100), self.enemy_attack, self.enemy_exp, self.enemy_speed,  self.enemy_hp, self.items_chance)
                self.spawns_enemyes.append(enemy)
                self.all_sprites.add(enemy)
                self.all_sprites.add(enemy.hp_bar)
                self.all_sprites.add(enemy.attack_area)
                self.enemyes_group.add(enemy)
    
    def update(self, **kwargs):
        self.rect.x = self.x
        self.rect.y = self.y
        self.check_spawn()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, spawner, x, y, attack, exp, speed, hp, items_chance:dict):
        super().__init__()
        self.items_chance = items_chance
        self.attack = attack
        self.who_attacked = None
        self.spawner = spawner
        self.give_exp = exp
        self.x = x
        self.y = y
        self.speed = speed
        self.width = 80
        self.height = 80
        self.cd_attack = 1.5
        self.color = "RED"
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.rect.x = self.x
        self.rect.y = self.y
        self.max_hp = hp
        self.hp = self.max_hp
        self.hp_bar = HPbar(self, "Brown", x, y - 40 , 80, 20)
        self.attack_area = AttackArea(self, "auto")

    def get_exp(self):
        self.who_attacked.exp_bar.exp += self.give_exp

    def follow_and_check(self):
        if self.who_attacked is not None and not self.rect.colliderect(self.who_attacked.rect):
            dirvect = pygame.math.Vector2(self.who_attacked.rect.x - self.rect.x,
                                         self.who_attacked.rect.y - self.rect.y)
            dirvect.normalize()
            dirvect.scale_to_length(self.speed)
            self.rect.move_ip(dirvect)
        distance = ((self.rect.x - self.spawner.rect.center[0])**2 + (self.rect.y - self.spawner.rect.center[1])**2) ** 0.5
        if distance > 400:
            self.rect.x, self.rect.y = self.spawner.rect.center[0], self.spawner.rect.center[1]
            self.who_attacked = None
            self.hp = self.max_hp

    def death(self):
        if self.hp <= 0:
            rec_item = choice(list(self.items_chance.keys()))
            if rec_item not in self.who_attacked.inventory.items and randint(1, 100) <= self.items_chance[rec_item]:
                self.who_attacked.inventory.items.append(rec_item)

            self.spawner.spawns_enemyes.remove(self)
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