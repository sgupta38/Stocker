##
##  Author: Sonu Gupta
##  Date: 17-Jan-2018
##  Purpose: This continously monitors for the value of 'stock' and whenever any change happens, gives notification to user.
##

import bs4, requests
import os
import sys
import time
import win32con
import win32gui
from win32api import GetModuleHandle
import traceback
from nsetools import Nse
import json

# Often I work in private network so I need to provide proxies. You can update as per your requirement or simply just ignore.
proxies = {"http": "http://10.10.5.18:8080",
           "https": "http://10.10.5.18:8080"}


class WindowsBalloonTip:
    def __init__(self, title, msg):
        message_map = {win32con.WM_DESTROY: self.OnDestroy, }
        # Register the Window class.
        wc = win32gui.WNDCLASS()
        self.destroyed = False
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"
        wc.lpfnWndProc = message_map    # could also specify a wndproc.
        class_atom = win32gui.RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(class_atom, "Taskbar", style,
                                          0, 0, win32con.CW_USEDEFAULT,
                                          win32con.CW_USEDEFAULT, 0, 0,
                                          hinst, None)
        win32gui.UpdateWindow(self.hwnd)
        icon_path_name = os.path.abspath(os.path.join(sys.path[0],
                                                      "balloontip.ico"))
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
            hicon = win32gui.LoadImage(hinst, icon_path_name,
                                       win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "tooltip")
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY,
                                  (self.hwnd, 0, win32gui.NIF_INFO,
                                   win32con.WM_USER+20, hicon,
                                   "Balloon  tooltip", msg, 200, title))
        # self.show_balloon(title, msg)
        time.sleep(14)
        win32gui.DestroyWindow(self.hwnd)
        win32gui.UnregisterClass(class_atom, hinst)
        self.destroyed = True

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)  # Terminate the app.

    def isDestroyed(self):
        return self.destroyed

def balloon_tip(title, msg):
    w = WindowsBalloonTip(title, msg)
    return w

def printData(stockData):

    ## Here you can add more data if you want.
    data = '\n'.join([
                    'Current: ' + str(stockData['lastPrice']),
                    'High: ' + str(stockData['dayHigh']),
                    'Low: ' + str(stockData['dayLow']),
                    'Average Price: ' + str(stockData['averagePrice']),
                     ])
    return data

nse = Nse() # Constructor

print('Enter the STOCK CODE to monitor:')
code = input()
stock_quote = nse.get_quote(code, as_json=True)
response = json.loads(stock_quote)
data = printData(response)
print(data)

balloon_tip(str(response['companyName']), data)

#print(response['lastPrice'])
