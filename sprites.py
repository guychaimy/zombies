import itertools

import pygame as pg
from settings import *
from tilemap import collide_hit_rect
from random import uniform, choice, randint, random
import pytweening as tween

vec = pg.math.Vector2


# HUD functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)

    if pct > 0.6:
        color = GREEN
    elif pct > 0.3:
        color = YELLOW
    else:
        color = RED
    pg.draw.rect(surf, color, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


def collide_with_wall(sprite, group, dir):
    # check for collision on the x axis
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x

    # check for collision on the y axis
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.weapon = 'pistol'  # pistol/shotgun
        self.damaged = False

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            self.shoot()

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
            self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(self.rot)
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                spread = uniform(-WEAPONS[self.weapon]['spread'], WEAPONS[self.weapon]['spread'])
                Bullet(self.game, pos, dir.rotate(spread), WEAPONS[self.weapon]['damage'])
                snd = choice(self.game.weapon_sounds[self.weapon])
                if snd.get_num_channels() > 2:
                    snd.stop()
                snd.play()
            MuzzelFlash(self.game, pos)

    def hit(self):
        self.damaged = True
        self.damaged_alpha = itertools.chain(DAMAGED_ALPHA * 4)

    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        if self.damaged:
            try:
                self.image.fill((255, 255, 255, next(self.damaged_alpha)),
                                special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_wall(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_wall(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH

        self.speed = choice(MOB_SPEED)

        self.target = game.player
        self.damaged = False

        self.wait_pos = vec(x + 5, y + 5)
        self.rot = uniform(0, 359)

        self.last_move_change = 0

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < MOB_AVOID_RADIUS:
                    self.acc += dist.normalize()

    def draw_health(self):
        # Draw health bar
        if self.health > 60:
            color = GREEN
        elif self.health > 30:
            color = YELLOW
        else:
            color = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, color, self.health_bar)

    def hit(self):
        self.damaged = True
        self.damaged_alpha = itertools.chain(DAMAGED_ALPHA * 4)

    def random_move(self):
        """currently not in use"""
        # check distance from initial span spot
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.rect = self.image.get_rect()
        dist_from_init = self.pos - self.wait_pos
        if dist_from_init.length_squared() > MOB_WAITING_RANGE ** 2:
            self.rot = (self.rot + uniform(160, 200)) % 360
        self.vel = vec(MOB_WAITING_SPEED, 0).rotate(-self.rot)
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        collide_with_wall(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_wall(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * MOB_WAITING_SPEED
        steer = (self.desired - self.vel)
        if steer.length() > MOB_WAITING_SPEED:
            steer.scale_to_length(MOB_WAITING_SPEED)
        return steer

    def wander(self):
        circle_pos = self.wait_pos
        target = circle_pos + vec(MOB_WAITING_RANGE, 0).rotate(uniform(0, 360))
        self.displacement = target
        return self.seek(target)

    def update(self):
        # check distance from player
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < DETECT_RADIUS ** 2:
            # Play a zombie sound
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
            # self.image = pg.transform.rotate(self.game.mob_img, self.rot)
            # self.rect = self.image.get_rect()
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            # self.vel += self.acc * self.game.dt
            # self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            # self.rect.center = self.pos
            # self.hit_rect.centerx = self.pos.x
            # collide_with_wall(self, self.game.walls, 'x')
            # self.hit_rect.centery = self.pos.y
            # collide_with_wall(self, self.game.walls, 'y')
            # self.rect.center = self.hit_rect.center
            self.wait_pos = self.pos * 1
        else:
            # self.random_move()
            now = pg.time.get_ticks()
            if now - self.last_move_change > DIRECTION_CHANGE_TIME:
                self.last_move_change = now
                self.acc = self.wander()
                # equations of motion
        self.rot = self.vel.angle_to(vec(1, 0))
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        collide_with_wall(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_wall(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

        if self.health <= 0:
            self.kill()
            choice(self.game.zombie_hit_sounds).play()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))
        # Blinks when hit
        if self.damaged:
            try:
                self.image.fill((255, 255, 255, next(self.damaged_alpha)),
                                special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False
                self.image = pg.transform.rotate(self.game.mob_img, self.rot)


class Wall(pg.sprite.Sprite):
    '''class for walls. not in use '''

    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Obstacale(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.hit_rec = self.rect
        self.pos = vec(pos)
        # spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.rect.center = pos
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > \
                WEAPONS[self.game.player.weapon]['bullet_life_time']:
            self.kill()


class MuzzelFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.image = pg.transform.rotate(self.image, self.game.player.rot)
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEM_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step >= BOB_RANGE:
            self.step = 0
            self.dir *= -1


class MiniMap(pg.sprite.Sprite):
    """Used to follow the player and reveal relevant parts of the map"""

    def __init__(self, game, scale):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.scale = scale
        self.image = pg.transform.scale(game.map_img, (int(WIDTH * self.scale),
                                                       int(HEIGHT * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (WIDTH * (0.97 - scale), HEIGHT * (0.97 - scale))
        self.actual_scale = WIDTH * scale / game.map.width

    def update(self):
        self.image = pg.transform.scale(self.game.map_img, (int(WIDTH * self.scale),
                                                            int(HEIGHT * self.scale)))
        for sprite in self.game.all_sprites:
            if isinstance(sprite, Mob):
                pg.draw.circle(self.image, RED, sprite.pos * self.actual_scale, 3)
        self.rect.topleft = (WIDTH * (1 - self.scale) - 10,
                             HEIGHT * (1 - self.scale) - 10)
