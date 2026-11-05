// The C++ topics shown on the dashboard, in the order students usually learn them.
export type Topic = {
  id: string; // used in the URL: /topics/<id>
  name: string;
  description: string;
};

export const topics: Topic[] = [
  { id: "basics", name: "Basics", description: "Variables, operators, and writing your first functions." },
  { id: "conditionals", name: "Conditionals", description: "Make decisions with if, else if, and else." },
  { id: "loops", name: "Loops", description: "Repeat work with for and while loops." },
  { id: "strings", name: "Strings", description: "Work with text using std::string." },
  { id: "arrays", name: "Arrays & Vectors", description: "Store and process lists of values." },
  { id: "recursion", name: "Recursion", description: "Solve problems with functions that call themselves." },
  { id: "pointers", name: "Pointers & References", description: "Work with memory addresses, * and &." },
  { id: "structs", name: "Structs & Classes", description: "Group data together and build your own types." },
];

// "Full C++" is a special section that shows every exercise from every topic.
export const ALL_TOPICS_ID = "all";

export function findTopic(id: string): Topic | undefined {
  return topics.find((t) => t.id === id);
}
