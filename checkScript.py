import os
import filecmp
import subprocess
from datetime import datetime
from collections import defaultdict

DETACHED_PROCESS = 0x00000008
erase_after_run = True
log = open("CheckLog.txt", 'a')
defaultConfig = {"timeout": 30}
teams_folder = "C:\\Users\\steph\\OneDrive\\Desktop\\checkScript\\teams"
tests_folder = "C:\\Users\\steph\\OneDrive\\Desktop\\checkScript\\tests"


def run_tests(file, configs, inputs, outputs):

    # Validate input file integrity, if a file was modified it may have been modified maliciously
    for input_file in inputs:
        if input_file[1] != os.path.getmtime(input_file[0]):
            write("FATAL: " + input_file[0] + " was modified, this action may have been malicious")
            exit()

    try:
        for i in range(len(inputs)):
            if file.endswith(".exe"):
                command = "\"" + file + "\" \"" + inputs[i][0] + "\" output.txt"
            elif file.endswith(".py"):
                command = "python \"" + file + "\" \"" + inputs[i][0] + "\" output.txt"
            elif file.endswith(".java"):
                subprocess.call("javac \"" + file + "\"")
                command = "java \"" + file[:-5] + "\" \"" + inputs[i][0] + "\" output.txt"
            else:
                write("File extension " + os.path.splitext(file)[1] + " not recognised")
                return

            if os.path.exists("output.txt"):
                os.remove("output.txt")

            write("Executing: " + command)
            subprocess.Popen(command, shell=True, creationflags=DETACHED_PROCESS).wait(configs["timeout"])

            with open('output.txt') as output, open(outputs[i]) as expected:
                if not filecmp.cmp(output, expected, False):
                    write(file + " failed test case " + inputs[i][0] + "\n")
                    return

        write(file + " successfully passed all tests\n")

    except subprocess.CalledProcessError:
        write(file + " threw an exception during execution\n")
    except subprocess.TimeoutExpired:
        write(file + " was timed out after " + str(configs["timeout"]) + " seconds\n")
    except FileNotFoundError:
        write("File not found error (Maybe output file wasn't created)\n")
    except Exception:
        write("Unknown error occurred\n")


def parse_config_file(file_path):
    config = dict()

    # Get configurations from config file
    with open(file_path) as config_file:
        for line in config_file:
            splits = line.split('=')
            config[splits[0]] = int(splits[1])

    # Add default config for unspecified options
    for key, value in defaultConfig.items():
        if key not in config:
            config[key] = value

    return config


def main():
    # Dictionary where key is file path, each entry contains config info, inputs and outputs with mod time
    tests = defaultdict(lambda: [dict(), [], []])

    for folder in os.listdir(tests_folder):
        found_config = False
        for file in os.path.join(tests_folder, folder):
            file_path = os.path.join(tests_folder, folder, file).lower()
            if file_path.endswith(".in"):
                file_path2 = (file_path[:-3] + ".out").lower()
                if os.path.exists(file_path2):
                    tests[folder][1].append(tuple((file_path, os.path.getmtime(file_path))))
                    tests[folder][2].append(tuple((file_path2, os.path.getmtime(file_path2))))
                else:
                    write("No corresponding output for " + file_path)

            elif file_path.endswith(".config"):
                found_config = True
                tests[folder][0] = parse_config_file(file_path)

        if not found_config:
            write("No config file found in folder " + folder)

    files_to_ignore = set()
    while True:
        for folder in os.listdir(teams_folder):
            for file in os.listdir(os.path.join(teams_folder, folder)):

                file_path = os.path.join(teams_folder, folder, file).lower()
                if file_path in files_to_ignore:
                    continue

                key = os.path.splitext(file)
                if key in tests:
                    run_tests(file_path, tests[key][0], tests[key][1], tests[key][2])
                else:
                    write(file + " doesn't match any tests and will be ignored")

                while os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass

        for ignored in list(files_to_ignore):
            if os.path.exists(ignored):
                files_to_ignore.remove(ignored)


def write(message):
    print(message)
    log.write(str(datetime.now()) + "\t" + message)
    log.flush()


if __name__ == "__main__":
    main()
