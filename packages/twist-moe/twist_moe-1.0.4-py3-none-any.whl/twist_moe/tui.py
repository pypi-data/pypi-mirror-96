import curses
import string
import argparse
import atexit
import sys
import time
import os
from .twist_api import download, stream, get_num_episodes, get_show_to_slug, get_title_translations

def init_window():
    screen = curses.initscr()
    curses.noecho()
    screen.keypad(True)
    curses.curs_set(0)
    return screen

def exit_window(screen):
    curses.curs_set(1)
    curses.echo()
    screen.keypad(False)
    curses.endwin()

def parse_twist_url(url, with_ep=True):
    if with_ep:
        slug, ep_number = tuple(url[20:].split("/"))
        ep_number = int(ep_number)
        return slug, ep_number
    else:
        slug = url[20:].split("/")[0]
        return slug

def stream_menu(screen, show, slug, num_episodes):
    selected_index = 0
    playing_index = None
    shift = 0
    ymax, xmax = screen.getmaxyx()
    
    while True:
        screen.clear()
        screen.addstr(0, 0, f"Starting episode? {selected_index + 1 + shift}")
        screen.addstr(1, 0, f"{show}:", curses.A_BOLD)
        max_index = shift + ymax - 1
        num_lines = min(num_episodes, ymax-2)

        for i in range(num_lines):
            try:
                if i == selected_index:
                    screen.addstr(i+2, 0, f"Episode {i + 1 + shift}", curses.A_REVERSE)
                else:
                    screen.addstr(i+2, 0, f"Episode {i + 1 + shift}")
            except:
                raise Exception(f"{i} {shift} {i+2-shift} {num_lines}")
        
        try:
            c = screen.getch()
        except:
            quit()
        
        if c == curses.KEY_UP:
            if selected_index > 0:
                selected_index -= 1
            elif shift > 0:
                shift -= 1 
        elif c == curses.KEY_DOWN:
            if selected_index < num_lines - 1:
                selected_index += 1
            elif max_index <= num_episodes:
                shift += 1
        elif c in (10, curses.KEY_ENTER):
            start_stream(screen, slug, selected_index + 1 + shift, num_episodes)
        elif chr(c) in ["b", "B"]:
            return False

        screen.refresh()

def start_stream(screen, slug, ep_start, num_episodes):
    i = ep_start
    while i <= num_episodes:
        screen.clear()
        screen.addstr(0, 0, f"Playing episode {i}, press Ctrl+C to quit\n")
        screen.refresh()
        if stream(slug, i):
            quit()
        
        time.sleep(1)
        screen.addstr(1, 0, "Rewatch? (y/n/b) [n]")
        screen.refresh()
        c = chr(screen.getch())

        if c in ("b", "B"):
            return
        elif c in ("y", "Y"):
            pass
        else:
            i += 1

def tui_main(screen):
    curses.curs_set(0)
    screen.clear()
    screen.addstr(0, 0, "Loading...")
    screen.refresh()
    search_term = ""
    selected_index = 0
    shift = 0
    switch_lang = False
    ymax, xmax = screen.getmaxyx()
    show_to_slug = get_show_to_slug()
    translations = get_title_translations()

    while True:
        shows = translations.keys() if switch_lang else translations.values()
        screen.clear()
        screen.addstr(0, 0, "Search: "+search_term, curses.A_BOLD)
        max_index = shift+ymax-2
        matches = list(filter(lambda i: search_term.lower() in i.lower(), shows))
        visible_matches = list(enumerate(matches[shift:max_index+1]))
        max_selection = len(visible_matches) - 1

        if max_selection < ymax-2 and shift > 0:
            shift = 0
            continue

        if selected_index > max_selection:
            selected_index = max_selection

        if selected_index == -1:
            selected_index = 0

        for i, show in visible_matches:
            try:
                if i == selected_index:
                    screen.addstr(i+1, 0, show, curses.A_REVERSE)
                else:
                    screen.addstr(i+1, 0, show)
            except:
                raise Exception(f"{i} {ymax}")

        try:
            c = screen.getch()
        except:
            quit()
        
        if c == curses.KEY_UP:
            if selected_index > 0:
                selected_index -= 1
            elif shift > 0:
                shift -= 1 
        elif c == curses.KEY_DOWN:
            if selected_index < max_selection:
                selected_index += 1
            elif max_index+1 < len(matches):
                shift += 1
        elif c in (curses.KEY_LEFT, curses.KEY_RIGHT):
            switch_lang = not switch_lang
        elif c in (10, curses.KEY_ENTER):
            _, show = visible_matches[selected_index]

            if switch_lang:
                show = translations[show]

            slug = show_to_slug[show]
            num_episodes = get_num_episodes(slug)
            if stream_menu(screen, show, slug, num_episodes):
                break
        elif c == curses.KEY_BACKSPACE:
            search_term = search_term[:-1]
        elif chr(c) == "\t":
            _, show = visible_matches[selected_index]
            search_term = show
        elif chr(c) in string.printable:
            search_term += chr(c)

        screen.refresh()

def main():
    parser = argparse.ArgumentParser(description='Download/Stream anime from twist.moe')
    parser.add_argument("--download", "-d", nargs='*', help="Download from twist.moe url")
    parser.add_argument("--stream", "-s", nargs='*', help="Stream from twist.moe url with mplayer")
    parser.add_argument("--download-show", "-w", nargs='*', help="Download all episodes of show from twist.moe url")
    parsed = parser.parse_args()
    
    slug_to_show = {j: i for i, j in get_show_to_slug().items()}
    
    if len(sys.argv) == 1:
        screen = init_window()
        atexit.register(exit_window, screen)
        tui_main(screen)
    else:
        if parsed.download:
            for url in parsed.download:
                slug, ep = parse_twist_url(url)
                show = slug_to_show[slug]
                print(f"Downloading episode {ep} of {show} to {slug}/{slug}-{ep}.mp4")
                download(slug, ep)
        if parsed.stream:
            for url in parsed.stream:
                slug, ep = parse_twist_url(url)
                show = slug_to_show[slug]
                print(f"Streaming episode {ep} of {show}...")
                stream(slug, ep)
        if parsed.download_show:
            for url in parsed.download_show:
                slug = parse_twist_url(url, with_ep=False)
                show = slug_to_show[slug]
                num_eps = get_num_episodes(slug)
                
                for i in range(1, num_eps+1):
                    print(f"Downloading episode {i} of {show} to {slug}/{slug}-{i}.mp4")
                    download(slug, i)

if __name__ == "__main__":
    main()
