#include <sstream>
#include <string>

#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        Counter counter;
        std::stringstream stream(test.inputs.at(0));
        std::string step;
        int result = 0;
        while (std::getline(stream, step, ',')) {
            if (step == "increment") {
                counter.increment();
            } else if (step == "reset") {
                counter.reset();
            } else if (step == "get") {
                result = counter.get();
            }
        }
        report(result);
    }
    return 0;
}
