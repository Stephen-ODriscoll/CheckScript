import os
import argparse
import subprocess
from time import sleep
from datetime import datetime
from collections import defaultdict


# Command line args
teams_folder, tests_folder, remove_after = "", "", False

# Don't modify
output_to = "output.out"
log = open("checkScript.log", 'a')
default_config = {"timeout": 30}


def run_tests(file, configs, inputs, outputs):
    try:
        for i in range(len(inputs)):
            if file.endswith(".exe"):
                command = "\"" + file + "\" \"" + inputs[i][0] + "\" " + output_to
            elif file.endswith(".py"):
                command = "python \"" + file + "\" \"" + inputs[i][0] + "\" " + output_to
            elif file.endswith(".java"):
                subprocess.call("javac \"" + file + "\"")
                command = "java \"" + file[:-5] + "\" \"" + inputs[i][0] + "\" " + output_to
            else:
                write("File extension " + os.path.splitext(file)[1] + " not recognised")
                return

            if os.path.exists(output_to):
                os.remove(output_to)

            write("Command = " + command)
            process = subprocess.Popen(command, stdin=None, stdout=None, stderr=None)
            try:
                process.wait(configs["timeout"])
            except subprocess.TimeoutExpired:
                write(file + " was timed out after " + str(configs["timeout"]) + " seconds")
                process.kill()
                return

            # Validate input & output file integrity. If a file was modified it may have been modified maliciously
            validate_integrity(inputs)
            validate_integrity(outputs)

            if not os.path.exists(output_to):
                write(file + " didn't produce an output file for test " + inputs[i][0])
                return

            if not compare_files(file, output_to, outputs[i][0]):
                write(file + " failed test case " + inputs[i][0])
                return

        write(file + " successfully passed all " + str(len(inputs)) + " tests")

    except FileNotFoundError:
        write("File not found error")
    except Exception:
        write("Unknown error occurred")


# Compare files whilst ignoring blank lines
def compare_files(file, output, expected):
    with open(output, 'r') as o_file, open(expected, 'r') as e_file:
        o_lines, e_lines = list(o_file), list(e_file)

    o_index, e_index = 0, 0
    o_length, e_length = len(o_lines), len(e_lines)
    while o_index < o_length or e_index < e_length:
        o_stripped, e_stripped = "", ""
        while o_index < o_length and not o_stripped:
            o_stripped = o_lines[o_index].strip()
            o_index += 1
        while e_index < e_length and not e_stripped:
            e_stripped = e_lines[e_index].strip()
            e_index += 1
        if o_stripped != e_stripped:
            if not o_stripped:
                write(file + " doesn't contain enough lines.")
            elif not e_stripped:
                write(file + " matches expected output but contains too many lines. ")
            else:
                write(file + " gave output: " + o_stripped + ". Expected output was: " + e_stripped)
            return False
    return True


# Verify the file still exists and hasn't been modified
def validate_integrity(files):
    for file in files:
        if not os.path.exists(file[0]):
            write("FATAL: " + file[0] + " no longer exists")
            exit()
        elif file[1] != os.path.getmtime(file[0]):
            write("FATAL: " + file[0] + " has been modified. Please verify this files integrity.")
            exit()


# Take options from .config file and put them into a dictionary
def parse_config_file(file_path):
    config = dict()

    # Get configurations from config file
    with open(file_path) as config_file:
        for line in config_file:
            splits = line.split('=')
            config[splits[0]] = int(splits[1])

    # Add default config for unspecified options
    for key, value in default_config.items():
        if key not in config:
            config[key] = value

    return config


def main():
    # Dictionary where key is file path, each entry contains config info, inputs and outputs with mod time
    tests = defaultdict(lambda: [dict(), [], []])

    for folder in os.listdir(tests_folder):
        found_config = False
        for file in os.listdir(os.path.join(tests_folder, folder)):
            file_path = os.path.join(tests_folder, folder, file)
            if file_path.endswith(".in"):
                file_path2 = (file_path[:-3] + ".out")
                if os.path.exists(file_path2):
                    tests[folder.lower()][1].append(tuple((file_path, os.path.getmtime(file_path))))
                    tests[folder.lower()][2].append(tuple((file_path2, os.path.getmtime(file_path2))))
                else:
                    write("No corresponding output for " + file_path)

            elif file_path.endswith(".config"):
                found_config = True
                tests[folder.lower()][0] = parse_config_file(file_path)

        if not found_config:
            write("No config file found in folder " + folder + ". Using defaults")
            tests[folder.lower()][0] = default_config

    files_to_ignore = list()
    while True:
        for folder in os.listdir(teams_folder):
            for file in os.listdir(os.path.join(teams_folder, folder)):

                file_path = os.path.join(teams_folder, folder, file)
                if file_path in files_to_ignore:
                    continue

                key = os.path.splitext(file)[0].lower()
                if key in tests:
                    run_tests(file_path, tests[key][0], tests[key][1], tests[key][2])

                    if remove_after:
                        attempts = 0
                        while os.path.exists(file_path) and attempts < 5:
                            try:
                                attempts += 1
                                os.remove(file_path)
                            except Exception:
                                sleep(0.2)
                        if os.path.exists(file_path):
                            write(file_path + " couldn't be removed and will be ignored instead")
                            files_to_ignore.append(file_path)
                        else:
                            write(file_path + " was removed")
                    else:
                        write(file_path + " will be ignored")
                        files_to_ignore.append(file_path)
                else:
                    write(file_path + " doesn't match any tests and will be ignored")
                    files_to_ignore.append(file_path)

        for ignored in list(files_to_ignore):
            if not os.path.exists(ignored):
                files_to_ignore.remove(ignored)
        sleep(1)


def write(message):
    print(message)
    log.write(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " | " + message + "\n")
    log.flush()


def parse_args():
    global teams_folder, tests_folder, remove_after
    parser = argparse.ArgumentParser()
    parser.add_argument("teams", help="Path to teams folder")
    parser.add_argument("tests", help="Path to tests folder")
    parser.add_argument("-r", "--remove_after", action="store_true", help="Remove tests after they've been run")
    args = parser.parse_args()

    teams_folder = args.teams
    tests_folder = args.tests
    remove_after = args.remove_after


if __name__ == "__main__":
    parse_args()
    main()
