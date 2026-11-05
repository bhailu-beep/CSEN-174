// TODO(backend): sample exercises, grouped by lesson. Replace with data from the backend once it's ready.
// Problem text, hints, and starter code live here. The backend folder for an exercise only has tester.cpp and tests.txt.
export type Example = { input: string; output: string };

export type Exercise = {
  id: string; // backend exercise id, the folder slug, e.g. "sum"
  slug: string; // used in the URL: /exercises/<slug>
  title: string;
  topic: string; // lesson id, the parent folder, e.g. "basics"
  tags: string[];
  description: string;
  examples: Example[];
  hint: string;
  starterCode: string;
};

export const exercises: Exercise[] = [
  // ---------- Basics ----------
  {
    id: "sum", slug: "sum-two-numbers", title: "Sum Two Numbers", topic: "basics", tags: ["math", "functions"],
    description: "Write a function that returns the sum of two integers.",
    examples: [{ input: "sum(2, 3)", output: "5" }, { input: "sum(-4, 4)", output: "0" }],
    hint: "Use the + operator and return the result.",
    starterCode: "int sum(int a, int b) {\n    // Your code here\n}",
  },
  {
    id: "to-fahrenheit", slug: "celsius-to-fahrenheit", title: "Celsius to Fahrenheit", topic: "basics", tags: ["math", "double"],
    description: "Convert a temperature from Celsius to Fahrenheit using F = C × 9 / 5 + 32.",
    examples: [{ input: "toFahrenheit(0)", output: "32" }, { input: "toFahrenheit(100)", output: "212" }],
    hint: "Write 9.0 / 5 instead of 9 / 5, otherwise C++ does integer division and you get 1.",
    starterCode: "double toFahrenheit(double celsius) {\n    // Your code here\n}",
  },
  {
    id: "is-even", slug: "is-even", title: "Even or Odd", topic: "basics", tags: ["math", "bool"],
    description: "Return true if n is even and false if it is odd.",
    examples: [{ input: "isEven(4)", output: "true" }, { input: "isEven(7)", output: "false" }],
    hint: "The % operator gives the remainder. What is the remainder when an even number is divided by 2?",
    starterCode: "bool isEven(int n) {\n    // Your code here\n}",
  },

  // ---------- Conditionals ----------
  {
    id: "max-of-three", slug: "max-of-three", title: "Largest of Three", topic: "conditionals", tags: ["if-else"],
    description: "Return the largest of three integers.",
    examples: [{ input: "maxOfThree(1, 5, 3)", output: "5" }, { input: "maxOfThree(-2, -8, -1)", output: "-1" }],
    hint: "Compare a with b first, then compare the winner with c.",
    starterCode: "int maxOfThree(int a, int b, int c) {\n    // Your code here\n}",
  },
  {
    id: "letter-grade", slug: "letter-grade", title: "Letter Grade", topic: "conditionals", tags: ["if-else", "char"],
    description: "Return 'A' for 90 and above, 'B' for 80–89, 'C' for 70–79, 'D' for 60–69, and 'F' below 60.",
    examples: [{ input: "letterGrade(95)", output: "'A'" }, { input: "letterGrade(72)", output: "'C'" }],
    hint: "Check the highest grade first with if / else if, so each later check only runs if the earlier ones failed.",
    starterCode: "char letterGrade(int score) {\n    // Your code here\n}",
  },
  {
    id: "leap-year", slug: "leap-year", title: "Leap Year", topic: "conditionals", tags: ["if-else", "math"],
    description: "A year is a leap year if it is divisible by 4, except years divisible by 100 are not, unless they are also divisible by 400.",
    examples: [{ input: "isLeapYear(2024)", output: "true" }, { input: "isLeapYear(1900)", output: "false" }, { input: "isLeapYear(2000)", output: "true" }],
    hint: "Check the 400 rule first, then the 100 rule, then the 4 rule.",
    starterCode: "bool isLeapYear(int year) {\n    // Your code here\n}",
  },

  // ---------- Loops ----------
  {
    id: "sum-to-n", slug: "sum-to-n", title: "Sum 1 to N", topic: "loops", tags: ["for-loop", "math"],
    description: "Return the sum of all integers from 1 to n. If n is 0 or less, return 0.",
    examples: [{ input: "sumTo(5)", output: "15" }, { input: "sumTo(0)", output: "0" }],
    hint: "Start a total at 0 and add i to it in a for loop from 1 to n.",
    starterCode: "int sumTo(int n) {\n    // Your code here\n}",
  },
  {
    id: "count-digits", slug: "count-digits", title: "Count Digits", topic: "loops", tags: ["while-loop", "math"],
    description: "Return how many digits a non-negative integer has.",
    examples: [{ input: "countDigits(1234)", output: "4" }, { input: "countDigits(0)", output: "1" }],
    hint: "Dividing by 10 removes the last digit. Count how many times you can do that.",
    starterCode: "int countDigits(int n) {\n    // Your code here\n}",
  },
  {
    id: "power", slug: "power", title: "Power", topic: "loops", tags: ["for-loop", "math"],
    description: "Return base raised to the power exp (exp ≥ 0) using a loop, without using pow().",
    examples: [{ input: "power(2, 10)", output: "1024" }, { input: "power(5, 0)", output: "1" }],
    hint: "Start with result = 1 and multiply by base exp times.",
    starterCode: "int power(int base, int exp) {\n    // Your code here\n}",
  },

  // ---------- Strings ----------
  {
    id: "reverse", slug: "reverse-string", title: "Reverse a String", topic: "strings", tags: ["strings", "loops"],
    description: "Return a string with its characters in reverse order.",
    examples: [{ input: 'reverse("cat")', output: '"tac"' }, { input: 'reverse("")', output: '""' }],
    hint: "Loop from the last index (s.size() - 1) down to 0 and build a new string.",
    starterCode: "string reverse(string s) {\n    // Your code here\n}",
  },
  {
    id: "count-vowels", slug: "count-vowels", title: "Count Vowels", topic: "strings", tags: ["strings", "char"],
    description: "Return how many vowels (a, e, i, o, u, lowercase only) are in the string.",
    examples: [{ input: 'countVowels("hello")', output: "2" }, { input: 'countVowels("sky")', output: "0" }],
    hint: "Loop over each char c in s and check if it is one of the five vowels.",
    starterCode: "int countVowels(string s) {\n    // Your code here\n}",
  },
  {
    id: "is-palindrome", slug: "is-palindrome", title: "Palindrome Check", topic: "strings", tags: ["strings", "two-pointers"],
    description: "Return true if the string reads the same forwards and backwards.",
    examples: [{ input: 'isPalindrome("level")', output: "true" }, { input: 'isPalindrome("hello")', output: "false" }],
    hint: "Compare the first and last characters, then move both ends toward the middle.",
    starterCode: "bool isPalindrome(string s) {\n    // Your code here\n}",
  },

  // ---------- Arrays & Vectors ----------
  {
    id: "find-max", slug: "find-max", title: "Largest Number", topic: "arrays", tags: ["vectors", "loops"],
    description: "Given a non-empty vector of integers, return the largest one.",
    examples: [{ input: "findMax({3, 9, 2})", output: "9" }, { input: "findMax({-5, -1})", output: "-1" }],
    hint: "Assume nums[0] is the largest, then compare it with every other element.",
    starterCode: "int findMax(vector<int> nums) {\n    // Your code here\n}",
  },
  {
    id: "average", slug: "average", title: "Average", topic: "arrays", tags: ["vectors", "double"],
    description: "Return the average of a non-empty vector of integers as a double.",
    examples: [{ input: "average({2, 4, 9})", output: "5.0" }, { input: "average({1, 2})", output: "1.5" }],
    hint: "Add everything up, then divide by nums.size(). Convert to double before dividing.",
    starterCode: "double average(vector<int> nums) {\n    // Your code here\n}",
  },
  {
    id: "count-of", slug: "count-occurrences", title: "Count Occurrences", topic: "arrays", tags: ["vectors", "loops"],
    description: "Return how many times target appears in nums.",
    examples: [{ input: "countOf({1, 2, 1, 1}, 1)", output: "3" }, { input: "countOf({4, 5}, 9)", output: "0" }],
    hint: "A range-based for loop works well: for (int x : nums) { ... }",
    starterCode: "int countOf(vector<int> nums, int target) {\n    // Your code here\n}",
  },

  // ---------- Recursion ----------
  {
    id: "factorial", slug: "factorial", title: "Factorial", topic: "recursion", tags: ["recursion", "math"],
    description: "Return the factorial of a non-negative integer. The factorial of 0 is 1.",
    examples: [{ input: "factorial(4)", output: "24" }, { input: "factorial(0)", output: "1" }],
    hint: "factorial(n) = n × factorial(n − 1). The base case is n == 0.",
    starterCode: "int factorial(int n) {\n    // Your code here\n}",
  },
  {
    id: "fibonacci", slug: "fibonacci", title: "Fibonacci", topic: "recursion", tags: ["recursion", "math"],
    description: "Return the nth Fibonacci number, where fib(0) = 0 and fib(1) = 1.",
    examples: [{ input: "fib(6)", output: "8" }, { input: "fib(10)", output: "55" }],
    hint: "fib(n) = fib(n − 1) + fib(n − 2). You need two base cases.",
    starterCode: "int fib(int n) {\n    // Your code here\n}",
  },
  {
    id: "sum-digits", slug: "sum-digits", title: "Sum of Digits", topic: "recursion", tags: ["recursion", "math"],
    description: "Using recursion, return the sum of the digits of a non-negative integer.",
    examples: [{ input: "sumDigits(1234)", output: "10" }, { input: "sumDigits(7)", output: "7" }],
    hint: "n % 10 is the last digit and n / 10 is everything else.",
    starterCode: "int sumDigits(int n) {\n    // Your code here\n}",
  },

  // ---------- Pointers & References ----------
  {
    id: "swap", slug: "swap-values", title: "Swap with References", topic: "pointers", tags: ["references"],
    description: "Swap the values of a and b. Because they are passed by reference (&), the caller's variables change.",
    examples: [{ input: "a = 1, b = 2; swap(a, b)", output: "a = 2, b = 1" }],
    hint: "Use a temporary variable to hold one value while you overwrite it.",
    starterCode: "void swap(int& a, int& b) {\n    // Your code here\n}",
  },
  {
    id: "double-it", slug: "double-through-pointer", title: "Double Through a Pointer", topic: "pointers", tags: ["pointers"],
    description: "p points to an integer. Double the value it points to.",
    examples: [{ input: "x = 5; doubleIt(&x)", output: "x = 10" }],
    hint: "*p means \"the value p points to\". You can read it and assign to it.",
    starterCode: "void doubleIt(int* p) {\n    // Your code here\n}",
  },
  {
    id: "sum-array", slug: "sum-array-pointer", title: "Sum an Array", topic: "pointers", tags: ["pointers", "arrays"],
    description: "Return the sum of the first size elements of a C-style array.",
    examples: [{ input: "sumArray({1, 2, 3}, 3)", output: "6" }, { input: "sumArray({}, 0)", output: "0" }],
    hint: "arr[i] works on pointers too. It means *(arr + i).",
    starterCode: "int sumArray(const int* arr, int size) {\n    // Your code here\n}",
  },

  // ---------- Structs & Classes ----------
  {
    id: "rectangle-area", slug: "rectangle-area", title: "Rectangle Area", topic: "structs", tags: ["structs"],
    description: "Return the area of the rectangle.",
    examples: [{ input: "area({3, 4})", output: "12" }, { input: "area({5, 0})", output: "0" }],
    hint: "Access struct members with a dot: r.width",
    starterCode: "struct Rectangle {\n    int width;\n    int height;\n};\n\nint area(Rectangle r) {\n    // Your code here\n}",
  },
  {
    id: "distance", slug: "point-distance", title: "Distance Between Points", topic: "structs", tags: ["structs", "math"],
    description: "Return the straight-line distance between two points.",
    examples: [{ input: "distance({0, 0}, {3, 4})", output: "5.0" }],
    hint: "Distance = sqrt(dx² + dy²). sqrt is in <cmath>.",
    starterCode: "struct Point {\n    double x;\n    double y;\n};\n\ndouble distance(Point a, Point b) {\n    // Your code here\n}",
  },
  {
    id: "counter", slug: "counter-class", title: "Counter Class", topic: "structs", tags: ["classes"],
    description: "Finish the Counter class. increment() adds 1, reset() sets it back to 0, and get() returns the current count.",
    examples: [{ input: "c.increment(); c.increment(); c.get()", output: "2" }, { input: "c.reset(); c.get()", output: "0" }],
    hint: "Each method only needs one line that reads or changes the private member count.",
    starterCode:
      "class Counter {\nprivate:\n    int count = 0;\n\npublic:\n    void increment() {\n        // Your code here\n    }\n\n    void reset() {\n        // Your code here\n    }\n\n    int get() {\n        // Your code here\n    }\n};",
  },
];

export function findExercise(slug: string): Exercise | undefined {
  return exercises.find((e) => e.slug === slug);
}

export function exercisesInTopic(topicId: string): Exercise[] {
  return exercises.filter((e) => e.topic === topicId);
}

// Used by the Full C++ page: match a search word (title or tag) and an optional topic.
export function filterExercises(list: Exercise[], search: string, topicId: string | null): Exercise[] {
  const q = search.trim().toLowerCase();
  return list.filter(
    (e) =>
      (!topicId || e.topic === topicId) &&
      (!q || e.title.toLowerCase().includes(q) || e.tags.some((tag) => tag.includes(q))),
  );
}
