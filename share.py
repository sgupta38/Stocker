##
##  Author: Sonu Gupta
##  Date: 17-Jan-2018
##  Purpose: This continously monitors for the value of 'stock' and whenever ant change happens, gives notification for user.

import bs4, requests
import os
import sys
import time
import win32con
import win32gui
from win32api import GetModuleHandle

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

## Function for web scraping the 'Share' value
def findSharePrice(url):
    #res = requests.get(url, proxies=proxies)  ## Private Network
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    nseElems = soup.select('#ref_649130089307642_l')
    #print('Price: '+ nseElems[0].text.strip())
    count = nseElems[0].text.strip()
    count = count.replace(",", "")
    #print('Plane Price: '+ count)
    return float(count)

currentPrice = findSharePrice('https://finance.google.com/finance?q=NSE:QUICKHEAL')
print('Current Price is: ' + str(currentPrice))

print('Enter the MINIMUM threshold value for which you want to get notify: ')
minThreshold = input()

print('Enter the MAXIMUM threshold value for which you want to get notify: ')
maxThreshold = input()

while(1):
  actual = findSharePrice('https://finance.google.com/finance?q=NSE:QUICKHEAL')
  if(float(actual) == float(minThreshold) ):
    print('Value is equal to Minimum threshold')
    balloon_tip('QUICKHEAL MINIMUM Threshold Value Reached...', 'Price is: ' + str(actual))
    #break;

  elif(float(actual) == float(maxThreshold)):
    print('Value is equal to maximum threshold')
    balloon_tip('QUICKHEAL MAXIMUM Threshold Value Reached...', 'Price is: ' + str(actual))
    #break;
