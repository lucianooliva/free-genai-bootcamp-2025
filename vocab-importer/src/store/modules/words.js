import prompt from '../../data/prompt';

export default {
	namespaced: true,
	state: {
	},
	mutations: {
    setCategory(state, category) {
      state.category = category;
    }
  },
  actions: {
    async submitCategory({ commit }, category) {
      try {
        const apiKey = process.env.GROQ_API_KEY;
        const content = prompt(category);
        const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            messages: [{ role: 'user', content: content }],
            model: 'llama-3.3-70b-versatile'
          })
        });
        const data = await response.json();
        commit('setCategory', data.category);
        return data.choices[0].message.content
      } catch (error) {
        console.error('Error:', error);
      }
    }
  }
}