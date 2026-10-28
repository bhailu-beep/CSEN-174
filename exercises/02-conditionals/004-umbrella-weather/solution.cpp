#include <string>

bool umbrella_weather(std::string weather, double chance) {
    if (weather == "hail") {
        return true;
    }
    else if (weather == "rainy" && chance >= 50) {
        return true;
    }
    else if (weather == "sunny" && chance < 25) {
        return true;
    }
    return false;
}
