import pygame as pg

vec = pg.math.Vector2
# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

# game settings
WIDTH = 1024  # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = BROWN
MAP_FILE = 'level1.tmx'
TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE
WALL_IMG = 'tileGreen_39.png'
TITLE_FONT = 'ZOMBIE.TTF'
HUD_FONT = 'Impacted2.0.ttf'
MINIMAP_SCALE = 0.15  # size of the mini map relative to the actual map.

# Player's setting
PLAYER_HEALTH = 100

PLAYER_SPEED = 250
PLAYER_IMG = 'manBlue_gun.png'
PLAYER_ROT_SPEED = 258
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)  # size of the rect which is calculated for collisions
BARREL_OFFSET = vec(30, 10)  # vector for the barrel offset to the center of the player

# Weapon settings
BULLET_IMG = 'bullet.png'
WEAPONS = dict()
WEAPONS['pistol'] = {'bullet_speed': 500,
                     'bullet_life_time': 1000,
                     'rate': 250,
                     'kickback': 200,
                     'spread': 5,
                     'damage': 10,
                     'bullet_size': 'lg',
                     'bullet_count': 1
                     }
WEAPONS['shotgun'] = {'bullet_speed': 400,  # bullet velocity
                      'bullet_life_time': 500,  # how long a bullet "lives"
                      'rate': 900,  # number of m/s between vullets
                      'kickback': 300,  # a velocity when a bullet was fired
                      'spread': 20,  # how many degrees the bullet will offset when spawned
                      'damage': 5,  # damage to health by each bullet
                      'bullet_size': 'sm',
                      'bullet_count': 12
                      }

# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPLAT_IMG = 'splat green.png'
MOB_SPEED = [150, 100, 75, 125]  # speed of a mobs - pixels/sec
MOB_SPEED = [200, 150, 100, 150]  # speed of a mobs - pixels/sec
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100  # total health of a MOB
MOB_DAMGE = 30
MOB_KNOCKBACK = 20
MOB_AVOID_RADIUS = 50
DETECT_RADIUS = 400
RANDOM_MOVE_RANGE = 50
RANDOM_MOVE_SPEED = 25
WAITING_FORCE = 0.5


# Items
ITEM_IMAGES = {'health': 'health_pack.png',
               'shotgun': 'obj_shotgun.png'}
HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 20
BOB_SPEED = 0.6

# Effects
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png',
                  'whitePuff18.png']  # list of effects when the gun fires
FLASH_DURATION = 40
DAMAGED_ALPHA = [i for i in range(0, 255, 75)]
NIGHT_COLOR = (30, 30, 30)
NIGHT_RADIUS = (500, 500)
LIGHT_MASK = 'light_350_med.png'

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEM_LAYER = 1

# Sounds
BG_MUSIC = 'espionage.ogg'
TOTAL_VOLUME = 0.5
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
PLAYER_HIT_VOLUME = 0.5
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav',
                      'zombie-roar-7.wav']
ZOMBIE_VOLUME = 0.2
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
ZOMBIE_HIT_VOLUME = 0.5
WEAPON_SOUNDS = {'pistol': ['sfx_weapon_singleshot2.wav'],
                 'shotgun': ['shotgun.wav']}
WEAPON_VOLUME = 0.4
EFFECTS_SOUNDS = {'level_start': 'level_start.wav',
                  'health_up': 'health_pack.wav',
                  'gun_pickup': 'gun_pickup.wav'}
