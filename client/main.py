#import subprocess; subprocess.call('pip install pyperclip', shell=True)
import time
import requests
import subprocess
from subprocess import check_call
from sys import platform
import pyperclip

try:
    from win10toast import ToastNotifier
except ImportError:
    from dummy import ToastNotifier # MacOS cant use this
        


def notify():
    """
    Toast notification on macOS with a fixed message about clipboard string.
    """
    CMD = '''
display notification "String copied from phone!"
'''
    subprocess.call(['osascript', '-e', CMD])

def main():
    """
    Blocking main function
    """
    while True:
        req = requests.get("http://127.0.0.1:5001/get")
        data = req.json()
        if not data.get("success", False):
            time.sleep(2) # 2 sec delay between scans
            continue
        print(data)
        string = data.get("string", "")
        print(string)

        # Mac OS
        if platform == "darwin":
            notify()
            pyperclip.copy(string)

        # Windows
        elif platform == "win32":
            toaster = ToastNotifier()
            toaster.show_toast("NAME","String copied from phone!", duration=5)
            print(string)
            cmd='echo '+string.strip()+'|clip'
            check_call(cmd, shell=True)

        time.sleep(10)




if __name__ == "__main__":
    print("Client starting scan on http://127.0.0.1:5001/get")
    main()
