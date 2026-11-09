#include <sstream>
#include <string>
#include <vector>
using std::string;
using std::vector;

#include "solution.cpp"
#include "harness.h"

std::vector<int> ints(const std::string& text) {
    std::vector<int> values;
    std::stringstream stream(text);
    std::string item;
    while (std::getline(stream, item, ',')) {
        if (!item.empty()) {
            values.push_back(std::stoi(item));
        }
    }
    return values;
}

int main() {
    for (const TestCase& test : load_tests()) {
        report(average(ints(test.inputs.at(0))));
    }
    return 0;
}
