// A short lesson for each topic, shown at the top of the topic page before the exercises.
// Text wrapped in `backticks` is shown as code.
// Like exercises.ts, this is written in the frontend for now. The team can decide whether it moves to the backend.
export type LessonSection = {
  heading: string;
  text: string;
  code?: string; // optional C++ example
};

export type Lesson = {
  topic: string; // a topic id from topics.ts
  intro: string;
  sections: LessonSection[];
  mistake: { text: string; wrong: string; right: string }; // one common mistake, shown wrong vs. right
  keyPoints: string[];
};

export const lessons: Lesson[] = [
  {
    topic: "basics",
    intro:
      "A C++ function takes some inputs, does some work, and returns an answer. Every exercise on CompleteC asks you to finish one function, so this is the most important idea on the site.",
    sections: [
      {
        heading: "Variables and types",
        text: "Every variable has a type that says what kind of value it holds. You choose the type once, when you create the variable.",
        code: 'int age = 19;          // whole number\ndouble gpa = 3.7;      // decimal number\nbool passed = true;    // true or false\nchar grade = \'A\';      // one character\nstring name = "Zack";  // text',
      },
      {
        heading: "Math operators",
        text: "C++ has `+`, `-`, `*`, `/`, and `%` (remainder). When both numbers are `int`, `/` throws away the decimal part.",
        code: "7 / 2      // 3   (int / int drops the .5)\n7 % 2      // 1   (the remainder)\n7 / 2.0    // 3.5 (one double makes it a double)",
      },
      {
        heading: "Writing a function",
        text: "A function starts with its return type, then its name, then its inputs (called parameters). `return` sends the answer back. You don't need `main()` or `cout` here, because CompleteC calls your function for you.",
        code: "int square(int x) {\n    return x * x;\n}\n\n// square(4) gives 16",
      },
    ],
    mistake: {
      text: "Integer division gives the wrong answer when you expect decimals.",
      wrong: "double half = 5 / 2;    // 2, not 2.5",
      right: "double half = 5 / 2.0;  // 2.5",
    },
    keyPoints: [
      "Every statement ends with a semicolon `;`",
      "`=` stores a value, `==` compares two values",
      "Pick the return type that matches your answer: `int`, `double`, `bool`, …",
    ],
  },
  {
    topic: "conditionals",
    intro: "Conditionals let your code make decisions: do one thing if something is true, and something else if it isn't.",
    sections: [
      {
        heading: "if, else if, else",
        text: "C++ checks each condition from top to bottom and runs the first one that is true. Once one runs, the rest are skipped, so order matters.",
        code: 'string weather(int temp) {\n    if (temp > 90) {\n        return "hot";\n    } else if (temp > 60) {\n        return "nice";\n    } else {\n        return "cold";\n    }\n}',
      },
      {
        heading: "Comparing and combining",
        text: "Compare with `==`, `!=`, `<`, `<=`, `>`, `>=`. Combine conditions with `&&` (and), `||` (or), and `!` (not).",
        code: "bool canVote = age >= 18 && isCitizen;\nbool weekend = day == 6 || day == 7;\nbool notDone = !finished;",
      },
      {
        heading: "Return the condition directly",
        text: "A comparison is already `true` or `false`, so you can often return it instead of writing an if/else.",
        code: "// Long way\nif (n > 0) {\n    return true;\n} else {\n    return false;\n}\n\n// Short way, same result\nreturn n > 0;",
      },
    ],
    mistake: {
      text: "Using one `=` inside an if. That stores a value instead of comparing, and the condition is almost always true.",
      wrong: "if (score = 100) { ... }",
      right: "if (score == 100) { ... }",
    },
    keyPoints: [
      "The first true branch wins; put the most specific check first",
      "`&&` needs both sides true, `||` needs at least one",
      "Every path through the function must `return` something",
    ],
  },
  {
    topic: "loops",
    intro: "Loops repeat code so you don't have to write it over and over. Use a `for` loop when you know how many times to repeat, and a `while` loop when you don't.",
    sections: [
      {
        heading: "for loops",
        text: "A `for` loop has three parts: where to start, when to keep going, and how to step.",
        code: "int total = 0;\nfor (int i = 1; i <= 5; i++) {\n    total += i;        // same as total = total + i\n}\n// total is 1 + 2 + 3 + 4 + 5 = 15",
      },
      {
        heading: "while loops",
        text: "A `while` loop keeps going as long as its condition is true. Something inside the loop must change so the condition eventually becomes false.",
        code: "int n = 1234;\nint digits = 0;\nwhile (n > 0) {\n    n /= 10;      // drop the last digit\n    digits++;\n}\n// digits is 4",
      },
      {
        heading: "Shortcuts you'll see",
        text: "`i++` adds 1. `total += x` adds x to total. `n /= 10` divides n by 10. These are just shorter ways to write `i = i + 1` and so on.",
      },
    ],
    mistake: {
      text: "Off-by-one: using `<` when you meant `<=`, so the loop stops one step early.",
      wrong: "for (int i = 1; i < n; i++)   // skips n",
      right: "for (int i = 1; i <= n; i++)  // includes n",
    },
    keyPoints: [
      "If the condition never becomes false, the loop never ends and your code times out",
      "Start totals at 0 and products at 1",
      "Trace the first two and last two steps by hand to check your loop",
    ],
  },
  {
    topic: "strings",
    intro: "A `string` is a sequence of characters, like a row of boxes. Each box holds one `char`, and the boxes are numbered starting at 0.",
    sections: [
      {
        heading: "The basics",
        text: "Use `.size()` for the length, `[i]` to get one character, and `+` to join strings.",
        code: 'string word = "hello";\nword.size();    // 5\nword[0];        // \'h\'  (the first char)\nword[4];        // \'o\'  (the last char is at size() - 1)\nword + "!";     // "hello!"',
      },
      {
        heading: "Looping over characters",
        text: "Use a range-based `for` loop to look at every character, or an index loop when you need the position.",
        code: "int count = 0;\nfor (char c : word) {\n    if (c == 'l') {\n        count++;\n    }\n}\n// count is 2\n\nfor (int i = 0; i < word.size(); i++) {\n    // word[i] is the character at position i\n}",
      },
      {
        heading: "char vs. string",
        text: "Single quotes make a `char` (one character). Double quotes make a `string`. `'a'` and `\"a\"` are different types.",
      },
    ],
    mistake: {
      text: "Reading one past the end. The last character is at `size() - 1`, not `size()`.",
      wrong: "char last = word[word.size()];",
      right: "char last = word[word.size() - 1];",
    },
    keyPoints: [
      "Indexes start at 0",
      "Compare characters with single quotes: `c == 'a'`",
      "You can build a new string by starting with `\"\"` and adding to it",
    ],
  },
  {
    topic: "arrays",
    intro: "A `vector` is a list of values of the same type. It can grow and shrink, and it remembers its own size, which makes it the go-to list in modern C++.",
    sections: [
      {
        heading: "Creating and using a vector",
        text: "Like strings, items are numbered from 0. Use `.size()` for the count and `.push_back()` to add to the end.",
        code: "vector<int> nums = {3, 9, 2};\nnums.size();       // 3\nnums[1];           // 9\nnums.push_back(5); // now {3, 9, 2, 5}",
      },
      {
        heading: "Looping through a vector",
        text: "The range-based `for` loop visits every item. Use an index loop if you need positions.",
        code: "int total = 0;\nfor (int x : nums) {\n    total += x;\n}",
      },
      {
        heading: "The \"best so far\" pattern",
        text: "To find a maximum or minimum, start with the first item and update whenever you find something better.",
        code: "int best = nums[0];\nfor (int x : nums) {\n    if (x > best) {\n        best = x;\n    }\n}",
      },
    ],
    mistake: {
      text: "Dividing two ints when you want a decimal average.",
      wrong: "double avg = total / nums.size();   // drops the decimals",
      right: "double avg = (double) total / nums.size();",
    },
    keyPoints: [
      "Valid indexes go from 0 to `size() - 1`",
      "Reading outside the vector can crash your program",
      "`for (int x : nums)` gives you a copy of each item, which is fine for reading",
    ],
  },
  {
    topic: "recursion",
    intro: "A recursive function solves a problem by calling itself on a smaller version of the same problem, until the problem is so small the answer is obvious.",
    sections: [
      {
        heading: "Two parts every time",
        text: "The base case is where you stop and return a simple answer. The recursive case calls the function again on something smaller.",
        code: "int sumTo(int n) {\n    if (n == 0) {\n        return 0;               // base case: stop here\n    }\n    return n + sumTo(n - 1);    // recursive case: smaller problem\n}",
      },
      {
        heading: "Tracing it",
        text: "Each call waits for the smaller one to finish, then adds its part.",
        code: "sumTo(3)\n= 3 + sumTo(2)\n= 3 + 2 + sumTo(1)\n= 3 + 2 + 1 + sumTo(0)\n= 3 + 2 + 1 + 0\n= 6",
      },
      {
        heading: "Trust the smaller call",
        text: "When writing the recursive case, assume the smaller call already works. Your only job is to use its answer to build the answer for n.",
      },
    ],
    mistake: {
      text: "Forgetting the base case, or never getting closer to it. The function calls itself forever and the program crashes.",
      wrong: "return n + sumTo(n);       // n never shrinks",
      right: "return n + sumTo(n - 1);   // n gets closer to 0",
    },
    keyPoints: [
      "Write the base case first",
      "Each call must move toward the base case",
      "Many recursive problems can also be solved with a loop",
    ],
  },
  {
    topic: "pointers",
    intro: "Every variable lives somewhere in memory. References and pointers let a function work with the original variable instead of a copy.",
    sections: [
      {
        heading: "Copies vs. references",
        text: "Normally a function gets a copy of what you pass in, so changes don't reach the caller. Adding `&` to the parameter type makes it a reference: another name for the caller's actual variable.",
        code: "void addOne(int& x) {\n    x = x + 1;\n}\n\nint score = 5;\naddOne(score);   // score is now 6",
      },
      {
        heading: "Pointers",
        text: "A pointer stores the memory address of another variable. `&x` gets the address of x. `*p` follows the pointer to the value it points at.",
        code: "int x = 5;\nint* p = &x;   // p holds x's address\n*p = 10;       // x is now 10",
      },
      {
        heading: "Arrays and pointers",
        text: "An array's name acts like a pointer to its first element, so `arr[i]` works on a pointer too. It means the same thing as `*(arr + i)`.",
        code: "int sumArray(const int* arr, int size) {\n    int total = 0;\n    for (int i = 0; i < size; i++) {\n        total += arr[i];\n    }\n    return total;\n}",
      },
    ],
    mistake: {
      text: "Changing the pointer instead of the value it points at.",
      wrong: "p = p * 2;     // doesn't compile: p is an address",
      right: "*p = *p * 2;   // doubles the value p points at",
    },
    keyPoints: [
      "In a type, `int&` means reference and `int*` means pointer",
      "Before a variable, `&x` means \"address of x\" and `*p` means \"value at p\"",
      "`const` means the function promises not to change it",
    ],
  },
  {
    topic: "structs",
    intro: "Structs and classes let you make your own types by grouping related data together, so one variable can hold a whole \"thing\", like a student or a point.",
    sections: [
      {
        heading: "Structs group data",
        text: "Define the fields once, then create values of that type. Use a dot to reach each field.",
        code: 'struct Student {\n    string name;\n    double gpa;\n};\n\nStudent s = {"Lori", 3.9};\ns.name;   // "Lori"\ns.gpa;    // 3.9',
      },
      {
        heading: "Classes add behavior",
        text: "A class bundles data with functions (called methods) that work on it. `private` data can only be changed through the class's own methods, which keeps it safe.",
        code: "class BankAccount {\nprivate:\n    double balance = 0;\n\npublic:\n    void deposit(double amount) {\n        balance += amount;\n    }\n    double getBalance() {\n        return balance;\n    }\n};\n\nBankAccount acct;\nacct.deposit(50);\nacct.getBalance();   // 50",
      },
      {
        heading: "struct vs. class",
        text: "They're almost the same. The only difference is the default: struct members are `public` unless you say otherwise, and class members are `private`.",
      },
    ],
    mistake: {
      text: "Forgetting the semicolon after the closing brace of a struct or class.",
      wrong: "struct Point {\n    double x;\n    double y;\n}",
      right: "struct Point {\n    double x;\n    double y;\n};",
    },
    keyPoints: [
      "Use a dot to reach fields and methods: `s.gpa`, `acct.deposit(50)`",
      "Keep data `private` and change it through methods",
      "Methods can read and change the object's own fields directly",
    ],
  },
];

export function findLesson(topicId: string): Lesson | undefined {
  return lessons.find((l) => l.topic === topicId);
}
