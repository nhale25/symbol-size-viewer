import subprocess
import sys

subprocess.call(["python", "src/symbolSizeViewer.py"] + sys.argv[1:], shell=True)
