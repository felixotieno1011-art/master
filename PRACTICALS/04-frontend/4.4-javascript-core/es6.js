// 1. Template Literals
const name = "Felix";
const age = 25;
console.log(`Hello, ${name}! You are ${age}.`);

// 2. Arrow Functions
const add = (a, b) => a + b;
console.log("Add:", add(5, 3));

// 3. Destructuring
const user = { id: 1, username: "felix", role: "admin" };
const { username, role } = user;
console.log("User:", username, "Role:", role);

// 4. Spread
const arr1 = [1, 2, 3];
const arr2 = [4, 5];
const combined = [...arr1, ...arr2];
console.log("Combined:", combined);

// 5. Rest
function sum(...numbers) {
  return numbers.reduce((a, b) => a + b, 0);
}
console.log("Sum:", sum(1, 2, 3, 4, 5));
