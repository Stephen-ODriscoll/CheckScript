# CheckScript

### Structure

* tests: Should contain the input and output files with a configuration file as shown.
          
          ‣ Use .in for input
          
          ‣ Use .out for output
          
          ‣ Use .config for configuration files to specify timeout

* teams: Should contain a directory for every team and their solutions are to be put in this folder

### Features
* Solutions are automatically tested
* If am input or expected output file is modified by the solution being tested this is reported to the user
* Blank lines are ignored during the file comparison.
* Std out is used to inform users of successful or unsuccessful tests
* A log file is produced which contains all std out with timestamps
