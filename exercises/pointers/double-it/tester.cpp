#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        int value = std::stoi(test.inputs.at(0));
        doubleIt(&value);
        report(value);
    }
    return 0;
}
