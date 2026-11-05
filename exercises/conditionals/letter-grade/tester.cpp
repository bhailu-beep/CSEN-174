#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        int score = std::stoi(test.inputs.at(0));
        report(letterGrade(score));
    }
    return 0;
}
