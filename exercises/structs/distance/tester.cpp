#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        Point a{std::stod(test.inputs.at(0)), std::stod(test.inputs.at(1))};
        Point b{std::stod(test.inputs.at(2)), std::stod(test.inputs.at(3))};
        report(distance(a, b));
    }
    return 0;
}
