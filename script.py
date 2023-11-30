from PIL import Image
import curses
import os
import time
import itertools

animated = 'example'

colors = {}

def init_color_variations():
    color_id = 1

    for r in range(0, 1001, 200):
        if r not in colors:
            colors[r] = {}

        for g in range(0, 1001, 200):
            if g not in colors[r]:
                colors[r][g] = {}

            for b in range(0, 1001, 200):
                colors[r][g][b] = color_id
                curses.init_color(color_id, r, g, b)
                color_id += 1

def closest_color(r, g, b):
    r *= 4
    g *= 4
    b *= 4
    return colors[round(r/200) * 200][round(g/200) * 200][round(b/200) * 200]

def main(stdscr):
    # terminal height & width
    height, width = stdscr.getmaxyx()

    w_pixels = width
    h_pixels = height * 2

    # Processing gif
    img = Image.open(animated)

    w,h = img.size

    ratio_w = w_pixels / w
    ratio_h = h_pixels / h

    ratio_min = min(ratio_w, ratio_h)

    if ratio_min < 1:
        w = int(w * ratio_min)
        h = int(h * ratio_min)

    frames = []

    #h = int(h / 2)

    for i in range(img.n_frames):
        img.seek(i)
        frame = img.convert('RGBA').resize((w, h)).copy()
        frames.append(frame)

    # Initialize curses
    stdscr.clear()

    if not curses.can_change_color() or curses.COLORS < 256:
        raise Exception("Terminal does not support 256 colors")

    curses.start_color()

    init_color_variations()

    color_pair_map = {}
    pair_number = 1

    # Adding borders
    win_w = w
    win_h = h // 2

    # Create a smaller window at a specific position
    win = curses.newwin(win_h, win_w, height//2 - win_h//2, width//2 - win_w//2)

    # Box the window and add some text
    win.box()
    for frame in frames:
        for y in range(0, win_h - 2):
            for x in range(0, win_w - 1):
                rt, gt, bt, at = frame.getpixel((x, 2 * y))
                rb, gb, bb, ab = frame.getpixel((x, 2 * y + 1))
                closest_top = closest_color(rt, gt, bt)
                closest_bottom = closest_color(rb, gb, bb)

                color_id = closest_top + closest_bottom

                if color_id not in color_pair_map:
                    curses.init_pair(pair_number, closest_bottom, closest_top)
                    color_pair_map[color_id] = pair_number
                    pair_number += 1

                win.addch(y + 1, x + 1, '▄', curses.color_pair(color_pair_map[color_id]))

        win.refresh()
        time.sleep(frame.info['duration'] / 1000)

    # Refresh the window to show changes
    win.refresh()

    # Wait for a key press
    win.getch()

curses.wrapper(main)
