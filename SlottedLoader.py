import re
import pygetwindow as gw
import pyautogui
import psutil
import win32process
import win32gui
import subprocess
import time
from pywinauto import Desktop
from pywinauto.timings import wait_until
from pywinauto.application import Application
import glob
import os
from pywinauto import keyboard
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as mbox
from PIL import ImageGrab

# hex_pattern = r"^[0-9a-fA-F]{32}$"
# # matched_title = find_window_title_by_regex(hex_pattern)
process_path = ""
process_name = os.path.basename(process_path) 
game_process_name = "League of Legends.exe"
loadBtn = ""


def wait_until_process_not_running(process_name, timeout):
    start_time = time.monotonic()
    while time.monotonic() - start_time < timeout:
        if not any(proc.name() == process_name for proc in psutil.process_iter()):
            return True
        time.sleep(0.5)
    return False

def browse_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    if file_path:
        with open('path.txt', 'w') as f:
            f.write(file_path)
    return file_path


def find_load_button(i=1):
    if i>=8:
        print("something is wrong getting the button image")
        if os.path.exists("loadBtn.png"):
            os.remove("loadBtn.png")
        exit()
    print(f"Searching for PNG files in {os.getcwd()}")
    pattern = "*.png"
    files = glob.glob(pattern)

    # Find the file name that matches the regex
    regex = re.compile(r"^LoadBtn\.PNG$", re.IGNORECASE)
    for file in files:
        if regex.match(os.path.basename(file)):
            loadBtn = os.path.abspath(file)
            print(f"Load button PNG found at: {loadBtn}")
            return loadBtn

    # If no matching file was found
    print("Load button PNG not found, please select the region where the button is located...")
    print("trying to put script in view...")
    launch_script()
    print("in view?...")
    time.sleep(2)
    mbox.showinfo("waiting for snip...", "Load button PNG not found, please select the region where the button is located...")
    keyboard.send_keys("{VK_LWIN down}{VK_SHIFT down}s{VK_SHIFT up}{VK_LWIN up}")
    time.sleep(2)
    if is_running("ScreenSketch.exe"):
        print("waiting for snip...")
        wait_until_process_not_running("ScreenSketch.exe")
    print("out of wait for snip")

    image = ImageGrab.grabclipboard()

    # Save the image as loadBtn.png in the current directory
    if image:
        image.save("loadBtn.png")
        print("Load button PNG saved to current directory.")
        return find_load_button()
    else:
        print("No image found in clipboard.")
    return find_load_button(i+1)


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

def list_window_titles():
    all_windows = gw.getAllTitles()
    return all_windows

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
    print("Find n switch...")
    app = Application().connect(process=process_pid)
    main_window = app.top_window()
    wait_until(0.1, 5, lambda: main_window.exists())
    for child in main_window.children():
        try:
            if child.element_info.class_name == "Chrome_WidgetWin_1" and child.element_info.name == window_name:
                child_window = main_window.child_window(title=window_name)
                wait_until(0.1, 5, lambda: child_window.exists())
                print(f"Switching to child window with handle: {child_window.handle}")
                child_window.set_focus()
                return True
        except Exception as e:
            print(f"Exception while searching for child window: {e}")
    return False

def find_window_title_by_pid(pid):
    print("looking for pid: {}",pid)
    windows = gw.getWindowsWithTitle('')
    for window in windows:
        _, window_pid = win32process.GetWindowThreadProcessId(window._hWnd)
        if window_pid == pid:
            print("found pid: {}",pid)
            # bring the window to the front
            hwnd = win32gui.FindWindow(None, window.title)
            win32gui.SetForegroundWindow(hwnd)
            print("tried to setForeGround")
            return window.title
    print("no sorry cant find")
    return None

def find_window_by_process_name(process_name):
    for process in psutil.process_iter(['name', 'pid']):
        # print(process.info['name'])
        if process.info['name'] == process_name:
            print("=-=-=--==--=-=-==--==--=-=-=-=")
            pid = process.info['pid']
            print("pid: {}",pid)
            window_title = find_window_title_by_pid(pid)
            window = gw.getWindowsWithTitle(window_title)
            if window:

                return window[0]
    return None

def find_window_title_by_regex(pattern):
    regex = re.compile(pattern)
    all_windows = gw.getAllTitles()
    
    for title in all_windows:
        if regex.match(title):
            return title
            
    return None

def find_and_click_button(window_title, button_image, i=1):
    if i > 12:
        if kill_process_by_name(process_name):
            return 

    print("I think we have the window?")
    print("=-=-=--==--=-=-==--==--=-=-=-=")

    button_location = pyautogui.locateOnScreen(button_image, confidence=0.9)
    if button_location:
        button_center = pyautogui.center(button_location)
        pyautogui.click(button_center)
    else:
        print("looking for loadBtn...{}",i)
        time.sleep(1)
        find_and_click_button(window_title, button_image,i+1)
    return True

def wait_close():
        print("Wait Close...")
        while is_game_running():
            print("game is running...")
            process_pid = find_process_pid(process_name)
            if not process_pid:
                launch_script()
                return True
            else:
                while is_game_running():
                    print("script already running")
                    time.sleep(30)



def start_script():
    process_pid = find_process_pid(process_name)
    if process_pid:
        find_sub_window_and_switch_to(process_pid, subwindowTitle)
        print("click load")
        find_and_click_button(process_name, loadBtn)
        return True
    return False



def launch_script():
    print("Launch Script...")
    process_pid = find_process_pid(process_name)
    if not process_pid:
        print("No process found with the specified name.")
        subprocess.Popen(process_path)
        print(f"Launched {process_path}")
        return True
    else:
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

if loadBtn == "":
    loadBtn = find_load_button()
print("Located Load button at: {}", loadBtn)

while True:
    print("inf loop...")
    if is_game_running():
        print("inf loop game running...")
        if launch_script():
            start_script()
            wait_close()    
    else:
        print("League of Legends game is not running.")
        time.sleep(35)
    print("sleep for 5 secs on principle")
    time.sleep(5)




