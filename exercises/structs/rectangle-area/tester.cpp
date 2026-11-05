#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        Rectangle rectangle{std::stoi(test.inputs.at(0)), std::stoi(test.inputs.at(1))};
        report(area(rectangle));
    }
    return 0;
}
