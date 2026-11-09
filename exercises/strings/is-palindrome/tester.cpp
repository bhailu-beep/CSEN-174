#include <string>
using std::string;

#include "solution.cpp"
#include "harness.h"

int main() {
    for (const TestCase& test : load_tests()) {
        report(isPalindrome(test.inputs.at(0)));
    }
    return 0;
}
