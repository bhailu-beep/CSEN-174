#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        int year = std::stoi(test.inputs.at(0));
        report(isLeapYear(year));
    }
    return 0;
}
