import asyncio
import evdev
from evdev import ecodes
import subprocess
import os
import curses
import time

# --- Configuration ---
DEFAULT_MULTIPLIER = 3
LOOP_INTERVAL = 0.01

KEY_MAP = {
    "KEY_LEFT": "Left",
    "KEY_RIGHT": "Right",
    "KEY_UP": "Up",
    "KEY_DOWN": "Down",
    "KEY_Z": "Left",
    "KEY_X": "Down",
    "KEY_C": "Up",
    "KEY_V": "Right"
}

# State
state = {
    "multiplier": DEFAULT_MULTIPLIER,
    "physical_keys_down": set(),
    "client_name": "Searching...",
    "active": False,
    "running": True,
    "zxcv_enabled": False
}

def get_darkages_window_info():
    try:
        # Get active window ID
        wid = subprocess.check_output(["xdotool", "getactivewindow"], stderr=subprocess.DEVNULL).decode().strip()
        # Get window name
        name = subprocess.check_output(["xdotool", "getwindowname", wid], stderr=subprocess.DEVNULL).decode().strip()
        return wid, name
    except:
        return None, "Not Found"

async def monitor_device(device):
    try:
        async for event in device.async_read_loop():
            if not state["running"]: break
            if event.type == ecodes.EV_KEY:
                try:
                    key_name = ecodes.KEY[event.code]
                except:
                    continue

                if key_name in KEY_MAP:
                    if event.value == 1: # Down
                        state["physical_keys_down"].add(key_name)
                    elif event.value == 0: # Up
                        state["physical_keys_down"].discard(key_name)
                
                # Level adjustment via physical keys (Keyboard + and -)
                if event.value == 1:
                    if key_name in ["KEY_KPMINUS", "KEY_MINUS"]:
                        state["multiplier"] = max(1, state["multiplier"] - 1)
                    elif key_name in ["KEY_KPPLUS", "KEY_EQUAL"]:
                        state["multiplier"] = min(10, state["multiplier"] + 1)
    except:
        pass

async def injection_loop():
    while state["running"]:
        wid, name = get_darkages_window_info()
        state["client_name"] = name
        state["active"] = "Darkages" in name

        if state["active"] and state["physical_keys_down"]:
            active_targets = set()
            for k in state["physical_keys_down"]:
                if k in ["KEY_Z", "KEY_X", "KEY_C", "KEY_V"] and not state["zxcv_enabled"]:
                    continue
                if k in KEY_MAP:
                    active_targets.add(KEY_MAP[k])
            
            for target in active_targets:
                for _ in range(state["multiplier"]):
                    subprocess.run(f"xdotool key {target}", shell=True, stderr=subprocess.DEVNULL)
        
        await asyncio.sleep(LOOP_INTERVAL)

def draw_ui(stdscr):
    curses.curs_set(0) # Hide cursor
    stdscr.nodelay(True) # Non-blocking input
    
    while state["running"]:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        # Header
        stdscr.attron(curses.A_BOLD | curses.color_pair(1))
        stdscr.addstr(1, 2, "BUTTERWALK LINUX - IMPROVED MOVEMENT")
        stdscr.attroff(curses.A_BOLD | curses.color_pair(1))
        
        # Client Info
        stdscr.addstr(3, 2, f"Client:  ")
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(state["client_name"][:w-15])
        stdscr.attroff(curses.A_BOLD)

        # Status
        stdscr.addstr(5, 2, f"Status:  ")
        if state["active"]:
            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addstr("ACTIVE")
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        else:
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr("INACTIVE (Focus Darkages)")
            stdscr.attroff(curses.color_pair(3))

        # Level
        stdscr.addstr(7, 2, f"Level:   ")
        stdscr.attron(curses.A_BOLD | curses.color_pair(4))
        stdscr.addstr(str(state["multiplier"]))
        stdscr.attroff(curses.A_BOLD | curses.color_pair(4))
        stdscr.addstr("  [+/- to adjust]")

        # ZXCV Movement Toggle
        stdscr.addstr(9, 2, f"ZXCV:    ")
        if state["zxcv_enabled"]:
            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addstr("ENABLED")
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        else:
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr("DISABLED (Arrows Only)")
            stdscr.attroff(curses.color_pair(3))
        stdscr.addstr("  ['m' to toggle]")

        # Input
        keys = ", ".join([k.replace("KEY_", "") for k in state["physical_keys_down"]])
        stdscr.addstr(11, 2, f"Input:   [{keys if keys else 'None'}]")

        # Footer
        stdscr.addstr(h-2, 2, "Press 'q' to Exit")

        stdscr.refresh()
        
        # Check for UI-based keys
        try:
            ch = stdscr.getch()
            if ch == ord('q'):
                state["running"] = False
            elif ch in [ord('m'), ord('M')]:
                state["zxcv_enabled"] = not state["zxcv_enabled"]
        except:
            pass
            
        time.sleep(0.05)

async def main_async():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    tasks = [monitor_device(d) for d in devices if ecodes.EV_KEY in d.capabilities()]
    tasks.append(injection_loop())
    await asyncio.gather(*tasks)

def main(stdscr):
    # Setup Colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run the async logic in a separate thread so curses can own the main thread
    import threading
    t = threading.Thread(target=lambda: loop.run_until_complete(main_async()), daemon=True)
    t.start()

    draw_ui(stdscr)
    state["running"] = False
    loop.stop()

if __name__ == "__main__":
    if not os.access("/dev/input/event0", os.R_OK):
        print("ERROR: Permission denied for /dev/input/. Run 'sudo ./setup_permissions.sh' first.")
    else:
        curses.wrapper(main)
