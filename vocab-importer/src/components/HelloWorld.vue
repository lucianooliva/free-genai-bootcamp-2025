<template>
  <div class="hello">
    <form @submit.prevent="submitForm">
      <label for="category">Enter the name of a category:</label>
      <input type="text" id="category" v-model="category">
      <button type="submit">Submit</button>
      <button v-if="jsonObj" @click="downloadJson">Download JSON</button>
      <pre>{{ jsonObj }}</pre>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useStore } from 'vuex';

const store = useStore();
const category = ref('');
const jsonObj = ref(null);

const submitForm = async () => {
  const content = await store.dispatch('words/submitCategory', category.value);
  jsonObj.value = extractJSONFromString(content);
};

function extractJSONFromString(str) {
  const jsonMatch = str.match(/```\n({[\s\S]*?})\n```/);
  if (!jsonMatch) {
    throw new Error("JSON not found in the string");
  }
  let jsonString = jsonMatch[1];
  jsonString = jsonString.replace(/"parts":\s*"(\[.*?\])"/g, (match, group) => {
    return `"parts": ${group.replace(/\\"/g, '"')}`;
  });
  try {
    return JSON.parse(jsonString);
  } catch (error) {
    throw new Error("Invalid JSON format");
  }
}

const downloadJson = () => {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(jsonObj.value, null, 2));
  const downloadAnchorNode = document.createElement('a');
  downloadAnchorNode.setAttribute("href", dataStr);
  downloadAnchorNode.setAttribute("download", "data.json");
  document.body.appendChild(downloadAnchorNode);
  downloadAnchorNode.click();
  downloadAnchorNode.remove();
};
</script>

<style scoped>
h1 {
  font-size: 2em;
  color: #42b983;
}
</style>
