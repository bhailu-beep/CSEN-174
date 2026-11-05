#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        int n = std::stoi(test.inputs.at(0));
        report(sumDigits(n));
    }
    return 0;
}
