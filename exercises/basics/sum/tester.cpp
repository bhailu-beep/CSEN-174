#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        int a = std::stoi(test.inputs.at(0));
        int b = std::stoi(test.inputs.at(1));
        report(sum(a, b));
    }
    return 0;
}
