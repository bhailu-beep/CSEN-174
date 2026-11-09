#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        double celsius = std::stod(test.inputs.at(0));
        report(toFahrenheit(celsius));
    }
    return 0;
}
