# Umbrella Weather

Given the `weather` forecast and the percent `chance` of seeing that weather condition, return `true` or `false` for whether you need an umbrella.

There are three options for the weather: `sunny`, `rainy`, and `hail`.

Here are the weather rules:
- If it is `sunny`, bring an umbrella if the chance of sun is less than 25%.
- If it is `rainy`, bring an umbrella if the chance of rain is at least 50%. 
- If the forecast is `hail`, you always need an umbrella.

## Examples

```text
umbrella_weather("sunny", 80) → false
umbrella_weather("sunny", 50) → false
umbrella_weather("sunny", 0) → true

umbrella_weather("rainy", 80) → true
umbrella_weather("rainy", 50) → true
umbrella_weather("rainy", 0) → false

umbrella_weather("hail", 80) → true
umbrella_weather("hail", 50) → true
umbrella_weather("hail", 0) → true
```