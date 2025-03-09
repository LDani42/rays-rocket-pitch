import App from './App.svelte';

// For debugging
console.log("Initializing Svelte app...");

// Make sure the target element exists
const appElement = document.getElementById('app');
if (!appElement) {
  console.error("Could not find #app element in the DOM");
}

const app = new App({
  target: document.getElementById('app')
});

export default app;

console.log("Svelte app initialized");
