import os
import subprocess
from datetime import datetime
from collections import defaultdict

DETACHED_PROCESS = 0x00000008
erase_after_run = True
output_to = "output.out"
log = open("CheckLog.txt", 'a')
default_config = {"timeout": 30}
teams_folder = "C:\\Users\\R00146853\\Desktop\\CheckScript\\teams"
tests_folder = "C:\\Users\\R00146853\\Desktop\\CheckScript\\tests"


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
            subprocess.Popen(command, shell=True, creationflags=DETACHED_PROCESS).wait(configs["timeout"])

            # Validate input & output file integrity. If a file was modified it may have been modified maliciously
            validate_integrity(inputs)
            validate_integrity(outputs)

            if not os.path.exists(output_to):
                write(file + " didn't produce an output file for test " + inputs[i][0])
                return

            if not compare_files(output_to, outputs[i][0]):
                write(file + " failed test case " + inputs[i][0])
                return

        write(file + " successfully passed all " + str(len(inputs)) + " tests")

    except subprocess.CalledProcessError:
        write(file + " threw an exception during execution")
    except subprocess.TimeoutExpired:
        write(file + " was timed out after " + str(configs["timeout"]) + " seconds")
    except FileNotFoundError:
        write("File not found error")
    except Exception:
        write("Unknown error occurred")


def compare_files(output, expected):
    with open(output, 'r') as o_file, open(expected, 'r') as e_file:
        o_lines, e_lines = list(o_file), list(e_file)

    i, j = 0, 0
    while i < len(e_lines):
        e_stripped = e_lines[i].strip()
        if e_stripped:
            if len(o_lines) <= j:
                return False

            o_stripped = o_lines[j].strip()
            if o_stripped:
                if e_stripped == o_stripped:
                    i += 1
                    j += 1
                else:
                    return False
            else:
                j += 1
        else:
            i += 1

    return True


def validate_integrity(files):
    for file in files:
        if not os.path.exists(file[0]):
            write("FATAL: " + file[0] + " no longer exists")
            exit()
        elif file[1] != os.path.getmtime(file[0]):
            write("FATAL: " + file[0] + " has been modified, this action may have been malicious")
            exit()


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

                    while os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except Exception:
                            pass
                else:
                    write(file_path + " doesn't match any tests and will be ignored")
                    files_to_ignore.append(file_path)

        for ignored in list(files_to_ignore):
            if not os.path.exists(ignored):
                files_to_ignore.remove(ignored)


def write(message):
    print(message)
    log.write(str(datetime.now()) + " | " + message + "\n")
    log.flush()


if __name__ == "__main__":
    main()
