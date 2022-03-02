import os
import subprocess
import sys

# Runs a single game
def run_single_game(process_command):
    print("Start run a match")
    p = subprocess.Popen(
        process_command,
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr
        )
    # daemon necessary so game shuts down if this script is shut down by user
    p.daemon = 1
    p.wait()
    print("Finished running match")

# Get location of this run file
file_dir = os.path.dirname(os.path.realpath(__file__))

# Set default path for algos if script is run with no params
default_algo =  file_dir + "/python-algo/run.sh"
algo1 = default_algo
algo2 = default_algo

# If script run with params, use those algo locations when running the game
if len(sys.argv) > 1:
    algo1 = sys.argv[1]
if len(sys.argv) > 2:
    algo2 = sys.argv[2]

if "run.sh" not in algo1:
    trailing_char = "" if algo1.endswith('/') else "/"
    algo1 = algo1 + trailing_char + "run.sh"
if "run.sh" not in algo2:
    trailing_char = "" if algo2.endswith('/') else "/"
    algo2 = algo2 + trailing_char + "run.sh"

print("Algo 1: ", algo1)
print("Algo 2:", algo2)

run_single_game("cd {} && java -jar engine.jar work {} {}".format(file_dir, algo1, algo2))