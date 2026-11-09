#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        int a = std::stoi(test.inputs.at(0));
        int b = std::stoi(test.inputs.at(1));
        int c = std::stoi(test.inputs.at(2));
        report(maxOfThree(a, b, c));
    }
    return 0;
}
