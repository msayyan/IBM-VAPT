import os
import platform
from datetime import datetime

print("=== STAGE 2 RESULTS VIEWER ===")
print("Reading saved exploit results...")
print("Timestamp: " + str(datetime.now()))

# Look for the results file in multiple locations
result_files = [
    'uploads/exploit_results.txt',
    'exploit_results.txt',
    'uploads/stage1_results.txt'
]

results_found = False

for result_file in result_files:
    if os.path.exists(result_file):
        print("\nResults file found: " + result_file)
        results_found = True
        
        try:
            with open(result_file, 'r') as f:
                content = f.read()
                
            print("\n" + "="*60)
            print("RETRIEVED EXPLOIT RESULTS")
            print("="*60)
            print(content)
            print("="*60)
            print("END OF EXPLOIT RESULTS")
            print("="*60)
            
            break
            
        except Exception as e:
            print("Failed to read results file: " + str(e))
            continue

if not results_found:
    print("\nNo results file found!")
    print("Stage 1 payload may not have executed yet.")
    
    # Show what files are available
    print("\nAvailable files in uploads directory:")
    if os.path.exists('uploads'):
        upload_files = os.listdir('uploads')
        if upload_files:
            for file in upload_files:
                print("  " + file)
        else:
            print("  (empty)")
    else:
        print("  uploads directory not found")
    
    print("\nAvailable files in current directory:")
    current_files = [f for f in os.listdir('.') if f.endswith(('.txt', '.py', '.log'))]
    if current_files:
        for file in current_files:
            print("  " + file)
    else:
        print("  (no relevant files found)")

print("\n=== ADDITIONAL SYSTEM INFO ===")
print("Current working directory: " + os.getcwd())
print("Platform: " + platform.system() + " " + platform.release())
print("Stage 2 execution completed!")

print("\n=== INSTRUCTIONS ===")
print("1. First upload 'stage1_payload.py' (runs silently)")
print("2. Then upload 'stage2_executor.py' (shows results)")
print("3. Results are retrieved from saved files, not live execution")