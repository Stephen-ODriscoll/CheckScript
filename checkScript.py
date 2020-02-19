import os
import filecmp
import subprocess
from datetime import datetime

erase_after_run = True
log = open("CheckLog.txt", 'a')
teams_folder = "C:\\Users\\steph\\OneDrive\\Desktop\\checkScript\\teams"
input_folder = "C:\\Users\\steph\\OneDrive\\Desktop\\checkScript\\input"
output_folder = "C:\\Users\\steph\\OneDrive\\Desktop\\checkScript\\output"


def p1(file):
    inputs = [problems_folder + "\\P1\\input00.txt", problems_folder + "\\P1\\input01.txt",
              problems_folder + "\\P1\\input02.txt", problems_folder + "\\P1\\input03.txt"]
    outputs = [problems_folder + "\\P1\\output00.txt", problems_folder + "\\P1\\output01.txt",
               problems_folder + "\\P1\\output02.txt", problems_folder + "\\P1\\output03.txt"]
    check_problem(file, inputs, outputs, 30)


def p2(file):
    inputs = [problems_folder + "\\P2\\input00.txt", problems_folder + "\\P2\\input01.txt",
              problems_folder + "\\P2\\input02.txt", problems_folder + "\\P2\\input03.txt",
              problems_folder + "\\P2\\input04.txt"]
    outputs = [problems_folder + "\\P2\\output00.txt", problems_folder + "\\P2\\output01.txt",
               problems_folder + "\\P2\\output02.txt", problems_folder + "\\P2\\output03.txt",
               problems_folder + "\\P2\\output04.txt"]
    check_problem(file, inputs, outputs, 20)


def p3(file):
    inputs = [problems_folder + "\\P3\\input00.txt", problems_folder + "\\P3\\input01.txt",
              problems_folder + "\\P3\\input02.txt", problems_folder + "\\P3\\input03.txt"]
    outputs = [problems_folder + "\\P3\\output00.txt", problems_folder + "\\P3\\output01.txt",
               problems_folder + "\\P3\\output02.txt", problems_folder + "\\P3\\output03.txt"]
    check_problem(file, inputs, outputs, 10)


def p4(file):
    inputs = [problems_folder + "\\P4\\input00.txt", problems_folder + "\\P4\\input01.txt",
              problems_folder + "\\P4\\input02.txt", problems_folder + "\\P4\\input03.txt",
              problems_folder + "\\P4\\input04.txt"]
    outputs = [problems_folder + "\\P4\\output00.txt", problems_folder + "\\P4\\output01.txt",
               problems_folder + "\\P4\\output02.txt", problems_folder + "\\P4\\output03.txt",
               problems_folder + "\\P4\\output04.txt"]
    check_problem(file, inputs, outputs, 10)


def p5(file):
    inputs = [problems_folder + "\\P5\\input00.txt", problems_folder + "\\P5\\input01.txt",
              problems_folder + "\\P5\\input02.txt", problems_folder + "\\P5\\input03.txt"]
    outputs = [problems_folder + "\\P5\\output00.txt", problems_folder + "\\P5\\output01.txt",
               problems_folder + "\\P5\\output02.txt", problems_folder + "\\P5\\output03.txt"]
    check_problem(file, inputs, outputs, 10)


def check_problem(file, inputs, outputs, timeout):
    if len(inputs) != len(outputs):
        return ""

    try:
        correct = 0
        for i in range(len(inputs)):
            if file.endswith(".exe"):
                command = file + " " + inputs[i] + " output.txt"
            elif file.endswith(".py"):
                command = "python " + file + " " + inputs[i] + " output.txt"
            elif file.endswith(".java"):
                subprocess.call("javac " + file)
                command = "java " + file[:len(file) - 5] + " " + inputs[i] + " output.txt"
            else:
                break

            if os.path.exists("output.txt"):
                os.remove("output.txt")

            write("Executing: " + command)
            subprocess.Popen(command, shell=True, creationflags=subprocess.DETACHED_PROCESS).wait(timeout)

            with open('output.txt') as output, open(outputs[i]) as expected:
                if filecmp.cmp(output, expected, False):
                    correct += 1
                else:
                    break

        if correct == len(outputs):
            write(file + " successfully passed all tests\n")
        else:
            write(file + " failed test case " + str(correct) + "\n")

    except subprocess.CalledProcessError:
        write(file + " threw an exception during execution\n")
    except subprocess.TimeoutExpired:
        write(file + " was timed out after " + str(timeout) + " seconds\n")
    except FileNotFoundError:
        write("File not found error (Maybe output file wasn't created)\n")
    except Exception:
        write("Unknown error occurred\n")


def main():
    test_inputs = [folder.lower() for folder in os.listdir(input_folder)]
    test_outputs = [folder.lower() for folder in os.listdir(output_folder)]

    if test_inputs != test_outputs:
        write("Some inputs don't have corresponding outputs or vice versa. Exiting")
        exit()

    files_to_ignore = []
    while True:
        for folder in os.listdir(teams_folder):
            for file in os.listdir(os.path.join(teams_folder, folder)):

                file_path = os.path.join(teams_folder, folder, file)
                if files_to_ignore.__contains__(file_path):
                    continue

                try:
                    index = test_inputs.index(os.path.basename(file).lower())
                except ValueError:
                    write(file + " doesn't match any tests, tests are: " + str(input_folder))
                if to_match == "P1":
                    result = p1(file_path)
                elif to_match.__contains__("P2"):
                    result = p2(file_path)
                elif to_match.__contains__("P3"):
                    result = p3(file_path)
                elif to_match.__contains__("P4"):
                    result = p4(file_path)
                elif to_match.__contains__("P5"):
                    result = p5(file_path)
                else:
                    write(file_path + " didn't match any known problems\n")

                while os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass


def write(message):
    print(message)
    now = datetime.now()
    log.write(str(now) + "\t" + message)
    log.flush()


if __name__ == "__main__":
    main()
