// SPEC: my first JavaScript
// 1. Variables (let + const)
// 2. console.log
// 3. Function
// 4. Loop
// 5. Array

const name = "Felix";
const age = 25;

console.log("Hello, " + name);
console.log("Age: " + age);

function greet(person) {
    return "Hello, " + person + "!";
}

console.log(greet("Mombasa"));

for (let i = 1; i <= 3; i++) {
    console.log("Count: " + i);
}

const fruits = ["apple", "banana", "orange"];
for (const fruit of fruits) {
    console.log(fruit);
}
// Test the === trap
console.log("5" == 5);    // true (type conversion)
console.log("5" === 5);   // false (strict)

// Test const can't be changed
const fixed = 10;
// fixed = 20;  // ← uncomment to see error

// Test array methods
const numbers = [3, 1, 4, 1, 5];
console.log("Original:", numbers);
console.log("Sorted:", numbers.sort());
console.log("Length:", numbers.length);
