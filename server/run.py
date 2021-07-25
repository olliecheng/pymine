from pymine_server import run_program
import sys

if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 19131

run_program(port=port)
