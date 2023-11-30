from PIL import Image
import curses
import time

# default gif
animated = 'example'

colors = {}

def init_color_variations():
    """ inits a range of 216 colors (in curses) to reproduce
    a rgb-like color palette in the terminal
    - in curses, colors are initialized over r g b values
    spanning on 1000 (not 255)
    - the ids of initialized color are put in a 3-depth dictionary
    (ex: r:10 g:15 b:20 -> colors[10][15][20] = ID)
    """
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
    """ given (0-255) rgb values finds the closest color id
    previously initialized in init_color_variatiosn()
    """
    return colors[round(r/50) * 200][round(g/50) * 200][round(b/50) * 200]

""" curses works with color pairs (fg - bg), we can create
65536 of those, to optimize this we will save the pairs we
create and reuse them when necessary (an image generally uses
a lot of times the same colors)
"""
color_pair_map = {}
pair_number = 1

def play(win, frames):
    """ for each frame in the image, we iterate through each pixel in the curses
    window, we get two corresponding pixels in the frame, we get their colors and
    check if their pair is already mapped, if not we map it, then we write the pixel
    in the window with a '▄' character (top is bg, bottom is fg) with the required
    color pair
    - we refresh the window between each frame to show changes, and wait for the frame
    duration to simulate the gif playing
    """
    global color_pair_map, pair_number

    h, w = win.getmaxyx()
    for frame in frames:
        for y in range(0, h - 2):
            for x in range(0, w - 1):
                rt, gt, bt = frame.getpixel((x, 2 * y))
                rb, gb, bb = frame.getpixel((x, 2 * y + 1))
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

def main(stdscr):
    # terminal height & width
    height, width = stdscr.getmaxyx()

    """ characters are generally twice as tall as they are large in terminals
    thus we can fit two pixels in a single character playing with background and
    foreground colors, that is why we double the height
    """
    w_pixels, h_pixels = width, height * 2

    img = Image.open(animated)

    w,h = img.size

    # Calculating size ratio for images to fit in the terminal
    ratio_w, ratio_h = w_pixels / w, h_pixels / h
    ratio_min = min(ratio_w, ratio_h)

    if ratio_min < 1:
        w = int(w * ratio_min)
        h = int(h * ratio_min)

    frames = []

    # Editing each frame
    for i in range(img.n_frames):
        img.seek(i)
        frame = img.convert('RGB').resize((w, h)).copy()
        frames.append(frame)

    # Clearing curses screen
    stdscr.clear()

    if not curses.can_change_color() or curses.COLORS < 256:
        raise Exception("Terminal does not support 256 colors!")

    # Required to use colors
    curses.start_color()
    init_color_variations()

    # Curses window dimensions
    win_w, win_h = w, h // 2

    # Creating the window
    win = curses.newwin(win_h, win_w, height//2 - win_h//2, width//2 - win_w//2)
    win.box()

    play(win, frames)

curses.wrapper(main)
