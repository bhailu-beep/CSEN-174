#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        int base = std::stoi(test.inputs.at(0));
        int exp = std::stoi(test.inputs.at(1));
        report(power(base, exp));
    }
    return 0;
}
