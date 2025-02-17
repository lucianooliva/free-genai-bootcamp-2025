import { createStore } from 'vuex';
import words from './modules/words';

export default createStore({
  modules: {
    words
  }
});
