#include <iostream>
#include <string>

// Handles special characters in output
std::string json_escape(const std::string& s) {
    std::string json_string = "";

    for (std::size_t i = 0; i < s.size(); ++i) {
        if (s[i] == '\"' or s[i] == '\\') {
            json_string += '\\';
            json_string += s[i];
        }
        else if (s[i] == '\n') {
            json_string += "\\n";
        }
        else {
            json_string += s[i];
        }
        
    }

    return json_string;
}

// Returns a boolean output in C++ string format
std::string bool_str(bool b) {
    return b ? "true" : "false";
}

// Checks one test and prints the output in one line
void check(const std::string& name, bool expected, bool actual) {
    bool passed = expected == actual;
    std::string score_output;

    score_output += "{\"name\": \"";
    score_output += json_escape(name);
    score_output += "\", \"passed\": ";
    score_output += bool_str(passed);
    score_output += ", \"expected\": \"";
    score_output += bool_str(expected);
    score_output += "\", \"actual\": \"";
    score_output += bool_str(actual);
    score_output += "\"}";

    std::cout << score_output << std::endl;
}

int main() {
    check("umbrella_weather(\"sunny\", 80)", false, umbrella_weather("sunny", 80));
    check("umbrella_weather(\"sunny\", 25)", false, umbrella_weather("sunny", 25));
    check("umbrella_weather(\"sunny\", 24)", true, umbrella_weather("sunny", 24));
    check("umbrella_weather(\"sunny\", 0)", true, umbrella_weather("sunny", 0));

    check("umbrella_weather(\"rainy\", 80)", true, umbrella_weather("rainy", 80));
    check("umbrella_weather(\"rainy\", 50)", true, umbrella_weather("rainy", 50));
    check("umbrella_weather(\"rainy\", 49)", false, umbrella_weather("rainy", 49));
    check("umbrella_weather(\"rainy\", 0)", false, umbrella_weather("rainy", 0));

    check("umbrella_weather(\"hail\", 80)", true, umbrella_weather("hail", 80));
    check("umbrella_weather(\"hail\", 50)", true, umbrella_weather("hail", 50));
    check("umbrella_weather(\"hail\", 0)", true, umbrella_weather("hail", 0));
    return 0;
}
