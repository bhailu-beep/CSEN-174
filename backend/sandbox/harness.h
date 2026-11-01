// Shared helpers for tester.cpp. The sandbox reports actual return values only.
// Python reads tests.txt and decides which cases passed.
#ifndef CPP_PLATFORM_HARNESS_H
#define CPP_PLATFORM_HARNESS_H

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

inline std::string json_escape(const std::string& s) {
    std::string json_string;
    for (char character : s) {
        if (character == '"' || character == '\\') {
            json_string += '\\';
            json_string += character;
        } else if (character == '\n') {
            json_string += "\\n";
        } else {
            json_string += character;
        }
    }
    return json_string;
}

// to_str overloads stay above report() so the template can find them.
inline std::string to_str(bool value) {
    return value ? "true" : "false";
}

inline std::string to_str(const std::string& value) {
    return value;
}

inline std::string to_str(const char* value) {
    return value;
}

inline std::string to_str(char value) {
    return std::string(1, value);
}

inline std::string to_str(int value) {
    return std::to_string(value);
}

inline std::string to_str(long value) {
    return std::to_string(value);
}

inline std::string to_str(double value) {
    std::ostringstream out;
    out << value;
    return out.str();
}

// One case from the sandbox copy of tests.txt. Expected answers are not in that file.
// Cases stay in file order. There is no name.
struct TestCase {
    std::vector<std::string> inputs;
};

// Blocks separated by a blank line:
//   input: sunny
//   input: 80
// A line "case" is a case with no arguments. Lines starting with # are comments.
inline std::vector<TestCase> load_tests(const std::string& path = "/src/tests.txt") {
    std::vector<TestCase> cases;
    std::ifstream in(path);
    if (!in) {
        return cases;
    }

    TestCase current;
    bool in_case = false;
    auto flush = [&]() {
        if (!in_case) {
            return;
        }
        cases.push_back(current);
        current = TestCase{};
        in_case = false;
    };

    std::string line;
    while (std::getline(in, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line.empty()) {
            flush();
            continue;
        }
        if (line[0] == '#') {
            continue;
        }
        if (line.rfind("expected: ", 0) == 0 || line.rfind("name: ", 0) == 0) {
            continue;
        }
        if (line == "case") {
            in_case = true;
            continue;
        }
        if (line.rfind("input: ", 0) == 0) {
            current.inputs.push_back(line.substr(7));
            in_case = true;
        }
    }
    flush();
    return cases;
}

// Prints one JSON line: {"actual"}. Does not compare or stop the run.
template <typename Actual>
void report(const Actual& actual) {
    std::cout << "{\"actual\":\"" << json_escape(to_str(actual)) << "\"}" << std::endl;
}

#endif  // CPP_PLATFORM_HARNESS_H
