""""
Author: Avinash Nagarajan
"""
import sys
import re


def gridSearch(grid, pattern):
    for i in range(len(grid)):
        row = re.sub("\n", '', grid[i])
        track = i
        start_pos = -1
        end_pos = -1
        for line in pattern:
            line = re.sub("\n", '', line)
            locate_line = re.search(line, row)
            if locate_line is not None:
                if start_pos == -1:
                    track += 1
                    if track < len(grid):
                        row = re.sub("\n", '', grid[track])
                    start_pos = locate_line.start()
                    end_pos = locate_line.end()
                else:
                    if locate_line.start() == start_pos and locate_line.end() == end_pos:
                        track += 1
                        if track < len(grid):
                            row = re.sub("\n", '', grid[track])

        if (track - i) == len(pattern):
            return 'YES'
    return 'NO'


if __name__ == '__main__':
    input_file = open(sys.argv[1], "r")
    test_case = int(input_file.readline())

    result = ""
    for i in range(1, test_case+1):
        r_and_c = input_file.readline().split()
        rows = int(r_and_c[0])
        grid = []
        for j in range(1, rows+1):
            grid.append(input_file.readline())
        rows = int(input_file.readline().split()[0])
        pattern = []
        for _ in range(rows):
            pattern.append(input_file.readline())
        
        result += gridSearch(grid, pattern) + "\n"

    with open(sys.argv[2], 'w') as output_file:
        output_file.write(result)
