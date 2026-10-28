// Shared test-harness helpers. The runner concatenates, in this order:
//   1. the student's code
//   2. this file
//   3. the exercise's tests.cpp (which defines main)
// so everything the tests need must be declared here, above check().
#ifndef CPP_PLATFORM_HARNESS_H
#define CPP_PLATFORM_HARNESS_H

#include <iostream>
#include <sstream>
#include <string>

// Handles special characters in output
inline std::string json_escape(const std::string& s) {
    std::string json_string = "";

    for (std::size_t i = 0; i < s.size(); ++i) {
        if (s[i] == '\"' or s[i] == '\\') {
            json_string += '\\';
            json_string += s[i];
        }
        else if (s[i] == '\n') {
            json_string += "\\n";
        }
        else {
            json_string += s[i];
        }
    }

    return json_string;
}

// to_str overloads: must stay above check() so the template can find them.
// Add an overload here for any new type a test needs to print.
inline std::string to_str(bool b) {
    return b ? "true" : "false";
}

inline std::string to_str(const std::string& s) {
    return s;
}

inline std::string to_str(const char* s) {
    return s;
}

inline std::string to_str(char c) {
    return std::string(1, c);
}

inline std::string to_str(int n) {
    return std::to_string(n);
}

inline std::string to_str(long n) {
    return std::to_string(n);
}

inline std::string to_str(double d) {
    std::ostringstream out;
    out << d;
    return out.str();
}

// Checks one test and prints the result as one JSONL line.
// Never exits or throws on a mismatch, so later tests still run.
template <typename Expected, typename Actual>
void check(const std::string& name, const Expected& expected, const Actual& actual) {
    bool passed = expected == actual;
    std::string score_output;

    score_output += "{\"name\": \"";
    score_output += json_escape(name);
    score_output += "\", \"passed\": ";
    score_output += to_str(passed);
    score_output += ", \"expected\": \"";
    score_output += json_escape(to_str(expected));
    score_output += "\", \"actual\": \"";
    score_output += json_escape(to_str(actual));
    score_output += "\"}";

    std::cout << score_output << std::endl;
}

#endif  // CPP_PLATFORM_HARNESS_H
