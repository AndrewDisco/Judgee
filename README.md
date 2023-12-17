# Judgee

<p align="center">
  <img src="https://github.com/AndrewDisco/Judgee/blob/main/icon.png?raw=true" alt="Judgee Logo">
</p>

Judgee is a sophisticated tool designed to aid competitive programmers in verifying the correctness of their code. It allows users to check their code against a set of test cases and provides feedback on whether the code passed or failed each test. Users can perform a mass check of `.in` and `.ok` files or a single test.

## Features

<p align="center">
  <img src="https://i.postimg.cc/8CHrbScy/judgee-Showcase.gif" alt="Judgee Showcase">
</p>

- **C++ Code Verification**: The main feature of Judgee is the ability to verify C++ code. Users can paste their code into the application, and Judgee will compile and run the code against a set of test cases.

- **Mass Check**: This feature allows users to check their code against multiple test cases at once. The test cases should be stored in `.in` and `.ok` files in a selected directory.

- **Single Test Check**: Users can also verify their code against a single test case.

- **Mingw Integration**: Judgee integrates with Mingw for C++ code compilation. Users can specify the path to their Mingw installation, or let the application auto-detect it.

- **Test Results**: After running the tests, Judgee provides a detailed report of the results. The report includes the test number, whether the code passed or failed the test, and the time taken to run the test.

- **Syntax Highlighting**: Judgee includes syntax highlighting for C++ code to improve readability and help users spot errors more easily.

## Code Overview

The code for Judgee is organized as a `QWidget` application. The main class, `CPPCheckerApp`, contains the user interface and the core functionality of the application.

The user interface includes text fields for the C++ code and the Mingw path, buttons to browse for the C++ file and the Mingw directory, and a table to display the test results.

The core functionality of the application is implemented in the `massCheck` method. This method compiles the C++ code, runs it against each test case, and compares the output to the expected output. The results are then displayed in the table.

## Usage

To use Judgee, simply paste your C++ code into the application, specify the path to your Mingw installation / auto-detect it, and select the directory containing your test cases. Then, click the "Mass Check" button to run the tests. The results will be displayed in the table.

## Future Work

Future enhancements to Judgee could include support for additional programming languages, the ability to import and export test cases, and improved error handling.

## Conclusion

Judgee is a powerful tool for competitive programmers. It simplifies the process of verifying code and provides valuable feedback to help users improve their programming skills. Whether you're preparing for a coding competition or just want to improve your programming skills, Judgee is the tool for you.
