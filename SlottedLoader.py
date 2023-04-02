import re
import psutil
import win32gui
import subprocess
import time
from pywinauto.timings import wait_until
from pywinauto.application import Application
import glob
import os
import win32con
import ctypes
import tkinter as tk
from tkinter import filedialog


process_path = ""
process_name = os.path.basename(process_path) 
appdata_path = ""
appdata_name = os.path.basename(appdata_path) 
game_process_name = "League of Legends.exe"




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

def update_path_file(line_number, new_value):
    path_file = os.path.join(os.getcwd(), "path.txt")

    # Create the file if it doesn't exist
    if not os.path.exists(path_file):
        with open(path_file, "w") as f:
            pass

    with open(path_file, "r") as f:
        lines = f.readlines()

    if line_number < len(lines):
        lines[line_number] = new_value + "\n"
    else:
        lines.append(new_value + "\n")

    with open(path_file, "w") as f:
        f.writelines(lines)

def find_slotted():
    path_file = os.path.join(os.getcwd(), "path.txt")
    if os.path.exists(path_file):
        with open(path_file, "r") as f:
            process_path = f.readline().strip()
        if os.path.exists(process_path):
            process_name = os.path.basename(process_path)
            print(f"pulled {process_path} from config")
            return process_name, process_path
        else:
            print(f"The process path from previous config {process_path} does not exist.")
    else:
        print("The file path.txt does not exist.")
    
    print(f"Searching for slotted launcher exe's in {os.getcwd()}")
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
    print("couldnt find slotted launcher")
    process_path = filedialog.askopenfilename(title='Please select a the slotted launcher exe')
    process_name = os.path.basename(process_path)
    update_path_file(0, process_path)
    return process_name, process_path

def find_slotted_appdata():
    path_file = os.path.join(os.getcwd(), "path.txt")
    if os.path.exists(path_file):
        with open(path_file, "r") as f:
            f.readline()  # Skip the first line
            appdata_path = f.readline().strip()
        if os.path.exists(appdata_path):
            appdata_name = os.path.basename(appdata_path)
            print(f"pulled {appdata_path} from config")
            return appdata_name, appdata_name
        else:
            print(f"The process path from previous config {appdata_path} does not exist.")
            update_path_file(1, "")
    else:
        print("The file path.txt does not exist.")
    
    # Get the AppData\Local folder path
    appdata_local = os.path.join(os.environ["LOCALAPPDATA"])

    print(f"Searching for folders in {appdata_local}")

    # Find the folder name that matches the regex
    regex = re.compile(r"^[A-Za-z0-9]{5,10}==$")
    for folder_name in os.listdir(appdata_local):
        folder_path = os.path.join(appdata_local, folder_name)
        if os.path.isdir(folder_path) and regex.match(folder_name):
            a_file_path = os.path.join(folder_path, "a")
            if os.path.isfile(a_file_path):
                appdata_name = folder_name
                appdata_path = folder_path
                return appdata_name, appdata_path
            
    # If no matching folder was found
    print("couldnt find slotted appdata_folder")
    appdata_path = os.path.dirname(filedialog.askopenfilename(initialdir=appdata_local, title='Please select the slotted app data folder [a] file'))

    appdata_name = os.path.basename(appdata_path)
    update_path_file(1, appdata_path)
    return appdata_name, appdata_path


def find_exe_name(slotted_app_data_path):
    path = appdata_path

    # print("searching for exe in {}", path)
    exe_files = glob.glob(os.path.join(path, '*.exe'))

    if not exe_files:
        return None
    for file in exe_files:
        try:
            os.remove(file)
        except:
            return os.path.basename(exe_files[1])

def is_slotted_running():
    name = find_exe_name(appdata_path)
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

if appdata_path == "" or appdata_name =="":
    appdata_name, appdata_path = find_slotted_appdata()
print("located slotted appdata at: {}", appdata_path)

# I forget why these are here
process_name = os.path.basename(process_path) 
appdata_name = os.path.basename(appdata_path) 


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
            if script_running:
                kill_process_by_name(name)
                
            time.sleep(15)

        time.sleep(8)
    except Exception as e:
        time.sleep(8)
        print("idk")

