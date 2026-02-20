import sys
import os
# Add current directory (backend/) to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print(f"Sys path: {sys.path}")
print(f"CWD: {os.getcwd()}")

try:
    from app.routers import jobs
    print("Import 'app.routers.jobs' successful")
except Exception as e:
    import traceback
    traceback.print_exc()
