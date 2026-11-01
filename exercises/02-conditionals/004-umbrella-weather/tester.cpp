#include "student.cpp"
#include "harness.h"

#include <string>

int main() {
    for (const TestCase& test : load_tests()) {
        std::string weather = test.inputs.at(0);
        double chance = std::stod(test.inputs.at(1));
        report(umbrella_weather(weather, chance));
    }
    return 0;
}
