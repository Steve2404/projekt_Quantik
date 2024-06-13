import sys
import os

def read_file(path_name):
    if getattr(sys, 'frozen', False):
        # Ran from a PyInstaller executable file
        # application_path = sys._MEIPASS
        
        # Ran from a cx_freeze executable file
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.abspath(".")
    
    token_path = os.path.join(application_path, path_name) 
    
    
    try:
        with open(token_path, 'r') as file:
            token = file.read()
        
        return token
    except FileNotFoundError:
        print(f"Error: file{token_path} was not found.")
        sys.exit(1)

if __name__ == "__main__":
    print(read_file('kommu/chat4/GUI/token.txt'))

