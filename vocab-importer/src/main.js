import { createApp } from 'vue';
import HelloWorld from './components/HelloWorld.vue';
import store from './store';

const app = createApp(HelloWorld, { msg: 'Welcome to Your Vue.js App' });
app.use(store);
app.mount('#app');
