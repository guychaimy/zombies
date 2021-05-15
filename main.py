# KidsCanCode - Game Development with Pygame video series
import ntpath

import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *


class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        # start option of pygame to keep sending key event while the key is pressed
        pg.key.set_repeat(500, 100)
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        """Create a text on screen
        Function gets: text, font path, text size, color, location on screen and alignment code"""
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        """Loading the data for the Game"""
        # Folders
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        self.map_folder = path.join(game_folder, 'maps')
        # General functions
        self.title_font = path.join(img_folder, TITLE_FONT)
        self.hud_font = path.join(img_folder, HUD_FONT)
        # Dim the screen
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        # Load Images
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.bullet_images = dict()
        self.bullet_images['lg'] = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))
        self.gun_flashes = [pg.image.load(path.join(img_folder, img)).convert_alpha()
                            for img in MUZZLE_FLASHES]
        #  Dict of items the player can get
        self.item_images = dict()
        for item in ITEM_IMAGES.keys():
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item]))
        self.splat = pg.image.load(path.join(img_folder, MOB_SPLAT_IMG)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        # light effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, NIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

        # Sound loading
        #  BG music
        pg.mixer.music.load(path.join(music_folder, 'espionage.ogg'))
        # sounds effects
        self.effect_sounds = dict()
        for type in EFFECTS_SOUNDS:
            self.effect_sounds[type] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
        # shooting shounds
        self.weapon_sounds = dict()
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(WEAPON_VOLUME * TOTAL_VOLUME)
                self.weapon_sounds[weapon].append(s)
        # Zombie's sounds
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(ZOMBIE_VOLUME * TOTAL_VOLUME)
            self.zombie_moan_sounds.append(s)
        # Hit sounds Player/Zombie
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(PLAYER_HIT_VOLUME * TOTAL_VOLUME)
            self.player_hit_sounds.append(s)
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(ZOMBIE_HIT_VOLUME * TOTAL_VOLUME)
            self.zombie_hit_sounds.append(s)

    def new(self, level_number):
        """Initilazing a new game
        resets all the flags
        Getting level number to c map reat """
        # initialize all variables and do all the setup for a new game
        self.map = TiledMap(path.join(self.map_folder, MAP_FILE))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        for tile_object in self.map.tmxdata.objects:
            object_center = vec(tile_object.x + tile_object.width / 2,
                                tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x, tile_object.y)
            if tile_object.name == 'zombie':
                Mob(self, tile_object.x, tile_object.y)
            if tile_object.name in ['health', 'shotgun']:
                Item(self, object_center, tile_object.name)
            if tile_object.name == 'wall':
                Obstacale(self, tile_object.x, tile_object.y,
                          tile_object.width, tile_object.height)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.night = False
        self.effect_sounds['level_start'].play()
        self.present_minimap = True
        self.minimap = MiniMap(self, MINIMAP_SCALE)

    def run(self):
        """ Inner function that runs the loop of the game
        based of a flag called self.playing. The loop check event and update the screen
        in not in pause mode"""
        # game loop - set self.playing = False to end the game
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        # Game Over?
        if len(self.mobs) == 0:
            self.playing = False

        # Player hit item
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effect_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            if hit.type == 'shotgun':
                hit.kill()
                self.effect_sounds['gun_pickup'].play()
                self.player.weapon = 'shotgun'

        # Mob hit the player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            self.player.hit()
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)

        # Bullet hit mob
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.hit()
            mob.vel = vec(0, 0)

    def draw_grid(self):
        """draw a grid of lines according to the tile size in the setting
         Currently inactive."""
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        pg.display.set_caption('{:.2f}'.format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            if isinstance(sprite, MiniMap):
                if self.present_minimap:
                    self.screen.blit(sprite.image, sprite.rect)
            else:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
            # Draw rectangles around all sprites in debug mode
            if self.draw_debug:
                if isinstance(sprite, (Player, Mob)):
                    pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
                    try:
                        pg.draw.line(self.screen, GREEN, self.camera.apply_line(sprite), (sprite.pos + sprite.vel), 2)
                        pg.draw.line(self.screen, RED, sprite.pos, (sprite.pos + sprite.acc), 2)
                        pg.draw.circle(self.screen, YELLOW, sprite.displacement, 5)
                    except:
                        pass

                else:
                    pg.draw.rect(self.screen, CYAN, self.camera.apply(sprite), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)
        # Draw the fog
        if self.night:
            self.render_fog()
        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        self.draw_text('Zombies: {}'.format(len(self.mobs)), self.hud_font, 30, YELLOW,
                       WIDTH - 10, 10, align='ne')
        # Pause the game when p is pressed
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text('PAUSED', self.title_font, 105, WHITE, WIDTH / 2, HEIGHT / 2, align='center')

        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_n:
                    self.night = not self.night
                if event.key == pg.K_m:
                    self.present_minimap = not self.present_minimap

    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("KILL THEM ALL!!", self.title_font, 100, RED, WIDTH / 2, HEIGHT / 2, align='center')
        self.draw_text('Press a key to start', self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align='center')
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text('GAME oVER', self.title_font, 100, RED, WIDTH / 2, HEIGHT / 2, align='center')
        self.draw_text('Press a key to start', self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align='center')
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        pg.event.wait()
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYDOWN:
                    waiting = False

    def render_fog(self):
        """Based on an image of blured circle produce a map image that has some
        part brighter and others darker. The flag BLEND_MULT multiply the pixel of the image
        by 0-1 (black-white)"""
        # Draw the light mask (gradient) onto fog image
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)


def main():
    # create the game object
    g = Game()
    g.show_start_screen()
    while True:
        g.new(1)
        g.run()
        g.show_go_screen()


if __name__ == '__main__':
    main()
