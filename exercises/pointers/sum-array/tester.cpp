#include <sstream>
#include <string>
#include <vector>

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
        std::vector<int> nums = ints(test.inputs.at(0));
        int size = std::stoi(test.inputs.at(1));
        report(sumArray(nums.data(), size));
    }
    return 0;
}
