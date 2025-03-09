import App from './App.svelte';
import Gallery from './components/Gallery.svelte';
import PitchDetail from './components/PitchDetail.svelte';

// For debugging
console.log("Initializing Svelte app...");

// Make sure the target element exists
const appElement = document.getElementById('app');
if (!appElement) {
  console.error("Could not find #app element in the DOM");
}

const app = new App({
  target: appElement || document.body // Fallback to body if app element not found
});

const routes = [
  { path: '/gallery', component: Gallery },
  { path: '/gallery/:id', component: PitchDetail, props: route => ({ pitchId: route.params.id }) }
];

console.log("Svelte app initialized");

export default app;
