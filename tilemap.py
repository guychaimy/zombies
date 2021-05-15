import pygame as pg
import pytmx

from settings import *


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


class Map:
    """Create the game map based on txt file
    NOT in USE"""

    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            self.data = list(f.read().splitlines())
        self.tile_width = len(self.data[0])
        self.tile_height = len(self.data)
        self.width = self.tile_width * TILESIZE
        self.height = self.tile_height * TILESIZE


class TiledMap:
    """Create the game map based on tile file"""

    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        """Build the map according to the tmx (tile map file)
        return a surface with all the tiles according to VISIBLE layers"""
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Camera:
    """Used to follow the player and reveal relevant parts of the map"""

    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        """used to shift sprites based on cmera location"""
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        """used to shift Obstacles based on camera location"""
        return rect.move(self.camera.topleft)

    def apply_line(self, entity):
        """used to shift Obstacles based on camera location"""
        return entity.pos.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)

