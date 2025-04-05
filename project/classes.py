import pygame
import time
from random import randint

from pygame import Vector2


class EXPbar(pygame.sprite.Sprite):
    def __init__(self, x, y, owner):
        super().__init__()
        self.x = x
        self.y = y
        self.owner = owner
        self.procent = int((owner.exp / owner.max_exp) * 1200)
        self.height = 40
        self.image = pygame.Surface((self.procent, self.height))
        self.rect = self.image.get_rect()
        self.image.fill("YELLOW")
    
    def update(self):
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

    def update(self):
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

    def update(self):
        self.rect.center = self.owner.rect.center
        self.attack()
        self.death()


class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_list):
        super().__init__()
        self.x = x
        self.y = y
        self.cd_attack = 1
        self.level = 0
        self.points = 0
        self.exp = 0
        self.max_exp = 20
        self.attack = 60
        self.enemy_list = enemy_list
        self.width = 80
        self.height = 80
        self.color = "WHITE"
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.speed = 5
        self.max_hp = 100
        self.rec_hp = 100
        self.rect.move_ip(x, y)
        self.exp_bar = EXPbar(0, 0, self)
        self.hp_bar = HPbar(self, "GREEN", 0, self.x, 80, 20)
        self.attack_area = AttackArea(self, "player")
        self.camera = Vector2(300 - 80, 0 - 80)
    
    def death(self):
        if self.rec_hp <= 0:
            self.kill()

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
            self.camera.x += self.speed
        if keys[pygame.K_d]:
            self.rect.move_ip(self.speed, 0)
            self.camera.x -= self.speed
        if keys[pygame.K_w]:
            self.rect.move_ip(0, -self.speed)
            self.camera.y += self.speed
        if keys[pygame.K_s]:
            self.rect.move_ip(0, self.speed)
            self.camera.y -= self.speed
    
    def update(self, *args, **kwargs):
        self.x = self.rect.x
        self.y = self.rect.y
        self.attack_area.update()
        self.exp_check()
        self.move()
        self.hp_bar.update()
        self.exp_bar.update()
        self.death()

class Spawner(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_cnt, enemyes, sprites):
        super().__init__()
        self.x = x
        self.y = y
        self.enemy_cnt = enemy_cnt
        self.size = 700
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
                enemy = Enemy(self.x + randint(0, self.size - 100), self.y + randint(0, self.size - 100), self)
                self.spawns_enemyes.append(enemy)
                self.all_sprites.add(enemy)
                self.all_sprites.add(enemy.hp_bar)
                self.all_sprites.add(enemy.attack_area)
                self.enemyes_group.add(enemy)
    
    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y
        self.check_spawn()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, spawner):
        super().__init__()
        self.attack = 10
        self.who_attacked = None
        self.spawner = spawner
        self.give_exp = 5
        self.start_position = (x, y)
        self.x = x
        self.y = y
        self.speed = 1
        self.width = 80
        self.height = 80
        self.cd_attack = 2
        self.color = "RED"
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.rect.x = self.x
        self.rect.y = self.y
        self.max_hp = 150
        self.rec_hp = self.max_hp
        self.hp_bar = HPbar(self, "Brown", x, y - 40 , 80, 20)
        self.attack_area = AttackArea(self, "auto")

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
        
        distance = ((self.rect.x - self.start_position[0])**2 + (self.rect.y - self.start_position[1])**2) ** 0.5
        if distance > 400:
            self.rect.x, self.rect.y = self.start_position[0], self.start_position[1]
            self.who_attacked = None
            self.rec_hp = self.max_hp

    def death(self):
        if self.rec_hp <= 0:
            self.spawner.spawns_enemyes.remove(self)
            self.kill()

    def update(self):
        self.follow_and_check()
        self.death()
        self.attack_area.update()