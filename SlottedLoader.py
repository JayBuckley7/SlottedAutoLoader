import re
import pygetwindow as gw
import psutil
import win32gui
import subprocess
import time
from pywinauto.timings import wait_until
from pywinauto.application import Application
import glob
import os
import tkinter as tk
from tkinter import filedialog
from pywinauto_recorder.player import *
import win32con
import ctypes



process_path = ""
process_name = os.path.basename(process_path) 
game_process_name = "League of Legends.exe"


def browse_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    if file_path:
        with open('path.txt', 'w') as f:
            f.write(file_path)
    return file_path

def restore_window(main_window_handle):
    placement = win32gui.GetWindowPlacement(main_window_handle)
    if placement[1] == win32con.SW_SHOWMINIMIZED:
        placement[1] = win32con.SW_SHOWNORMAL
        win32gui.SetWindowPlacement(main_window_handle, placement)

def find_and_click_button(main_window_handle):
    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202

    if main_window_handle:
        try:
            restore_window(main_window_handle)
            win32gui.SetForegroundWindow(main_window_handle)
            x = 690
            y = 460
            lParam = (y << 16) | x

            ctypes.windll.user32.SendMessageW(main_window_handle, WM_LBUTTONDOWN, 1, lParam)
            ctypes.windll.user32.SendMessageW(main_window_handle, WM_LBUTTONUP, 1, lParam)
        except:
            print("failed during click")
    else:
        print("main windows handle was false")

def find_slotted():
    path_file = os.path.join(os.getcwd(), "path.txt")
    if os.path.exists(path_file):
        with open(path_file, "r") as f:
            process_path = f.read().strip()
        if os.path.exists(process_path):
            print("pulled from config")
            process_name = os.path.basename(process_path)
            return process_name, process_path
        else:
            print(f"The process path from previous config {process_path} does not exist.")
            os.remove(path_file)
    else:
        print("The file path.txt does not exist.")
    

    print(f"Searching for exe's in {os.getcwd()}")
    pattern = "*.exe"
    files = glob.glob(pattern)

    # Find the file name that matches the regex
    regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z]).{5,18}$")
    for file in files:
        if regex.match(file):
            process_name = file
            process_path = os.path.abspath(file)
            return process_name, process_path

    # If no matching file was found
    print("couldnt find slotted")
    process_path = browse_file()
    process_name = os.path.basename(process_path) 
    return process_name, process_path

def find_exe_name():
    path = os.path.join(os.environ['APPDATA'],'QUFUQQ==').replace("Roaming", "Local")

    print("searching for exe in {}", path)
    exe_files = glob.glob(os.path.join(path, '*.exe'))

    if not exe_files:
        return None
    for file in exe_files:
        try:
            os.remove(file)
        except:
            return os.path.basename(exe_files[1])

def is_slotted_running():
    name = find_exe_name()
    if name:
        print("name: " + str(name))
        return True, name
    return False, None
    
def is_running(name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == name:
            return True
    return False

def is_game_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == game_process_name:
            return True
    return False

def find_process_pid(process_name):
    for process in psutil.process_iter(['name', 'pid']):
        if process.info['name'] == process_name:
            return process.info['pid']
    return None

def kill_process_by_name(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            proc.kill()
            print(f"Process '{process_name}' has been terminated.")
            return True
    print(f"No process found with the name '{process_name}'.")
    return False

def find_sub_window_and_switch_to(process_pid, window_name):
    print("... ...Find n switch...")
    app = Application().connect(process=process_pid)
    main_window = app.top_window()
    wait_until(0.1, 10, lambda: main_window.exists())
    for child in main_window.children():
        print(child.element_info.name)
        try:
            if child.element_info.class_name == "Chrome_WidgetWin_1" and child.element_info.name == window_name:
                child_window = main_window.child_window(title=window_name)
                for element in child_window.children():
                    element.element_info.name
                print("... ...waiting for it to load")
                wait_until(0.1, 15, lambda: child_window.exists())
                print(f"... ...found handle: {child_window.handle}")
                # child_window.set_focus()
                
                return True, child_window.handle
        except Exception as e:
            print(f"... ...Exception while searching for child window: {e}")
    return False, 0

def start_script():
    process_pid = find_process_pid(process_name)
    if process_pid:
        found, handle =find_sub_window_and_switch_to(process_pid, subwindowTitle)
        if found:
            print("click load")
            find_and_click_button(handle)
            return True
    return False

def launch_script():
    print("... Launch Script...")
    process_pid = find_process_pid(process_name)
    if not process_pid:
        print("... No process found with the specified name. opening slotted")
        subprocess.Popen(process_path)
        print(f"... Launched {process_path}")
        return False
    else:
        print("... slotted is running, wait for it...")
        find_sub_window_and_switch_to(process_pid, subwindowTitle)
        return True

       


    
def is_script_running():
    print("is running?...")
    process_pid = find_process_pid(process_name)
    if not process_pid:
        return False
    elif process_pid:
        return True
    return False
    

subwindowTitle = "https://tauri.localhost/select-product"

if process_path == "" or process_name =="":
    process_name, process_path = find_slotted()
print("located slotted at: {}", process_path)

while True:
    try:
        print("-==-=-= looping-=-=-=-==-")
        # print("game running: {}", is_game_running())
        # print("is slotted running: {}", is_slotted_running())
        game_running = is_game_running()
        script_running, name = is_slotted_running()

        if is_game_running():
            if not script_running:
                print("league is running: True")
                print("Launch script enter -->")
                if launch_script():
                    print("try start")
                    start_script()
                    print("-=-==--==-=--=-=-=-=-=-=-=")
                    print("waiting till game closes")
                    #wait_close()
                else:
                    print("Wasnt open already come back around")
            else:
                print("script already running king.")
                time.sleep(15)
        else:
            script_running, name = is_slotted_running()
            kill_process_by_name(name)
            time.sleep(15)

        time.sleep(8)
    except:
        time.sleep(8)
        print("idk")

    




