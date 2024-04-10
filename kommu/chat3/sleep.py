import threading
import time

def autre_tache():
    while True:
        print("1-")
        time.sleep(5)
        print("je dors un peu 1-")

thread = threading.Thread(target=autre_tache)
thread.start()

while True:
    print("2- ")
    time.sleep(5)
    print("je dors aussi 2- ")
