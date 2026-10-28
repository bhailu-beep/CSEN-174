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
