#! /usr/bin/env python

import pygame as pg
import os, sys

filelist = sys.argv[1:]

size = width, height = 640, 480
screen = pg.display.set_mode((width, height))
KEYMAP = {
    pg.K_b: 'blue',
    pg.K_f: 'back',
    pg.K_g: 'green',
    pg.K_k: 'black',
    pg.K_r: 'red',
    pg.K_w: 'white',
    pg.K_o: 'other',
    pg.K_m: 'mana',
    pg.K_e: 'empty',
    pg.K_u: '.',
}

def message_display(text):
    font = pg.font.Font('freesansbold.ttf',115)
    text_surf = font.render(text, True, (255,0,0))
    text_rect = text_surf.get_rect()
    text_rect.center = ((width//2), (height//2))
    screen.blit(text_surf, text_rect)

def update(img, label):
    screen.blit(img, (0,0))
    message_display(label)
    pg.display.flip()

cnt = 0

pg.init()
pg.font.init()
pg.key.set_repeat() # turns off key repeat
img = pg.image.load(filelist[cnt], 'RGB')
label = '.'
update(img, label)

while True:
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            sys.exit()
        elif ev.type == pg.KEYDOWN:
            if ev.key in KEYMAP:
                label = KEYMAP[ev.key]
                update(img, label)
            elif ev.key == pg.K_RETURN:
                filename = filelist[cnt]
                filedir, filebase = os.path.split(filename)
                newdir = os.path.join(filedir, label)
                if not os.path.exists(newdir):
                    os.mkdir(newdir)
                newname = os.path.join(newdir, filebase)
                print('Moving {} -> {}'.format(filename, newname))
                os.rename(filename, newname)
                cnt += 1
                if cnt >= len(filelist):
                    break
                img = pg.image.load(filelist[cnt], 'RGB')
                label = '.'
                update(img, label)
