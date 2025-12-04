<template>
  <div v-if="loading || !loaded" class="code-loading">
    <LoadingBarComponent />
  </div>
  <div v-else>
    <pre><code :class="getHighlightClass()">{{ codeContent }}</code></pre>
  </div>
</template>

<script setup lang="ts">
import Prism from "prismjs";
import "prismjs/themes/prism-coy.min.css";
import {computed, inject, nextTick, onMounted, ref, watch} from "vue";
import {useI18n} from "vue-i18n";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  name: string;
  dataUrl: string;
}>();

const loading = ref(true);
const loaded = ref<boolean>(false);

const codeContent = ref("Loading...");
//const codeContent = ref("<p>Code</p>");

const getHighlightClass = () => {
  if (props.name.match(/\.(cs)$/)) {
    return "language-csharp";
  } else if (props.name.match(/\.(py)$/)) {
    return "language-python";
  } else if (props.name.match(/\.(js)$/)) {
    return "language-javascript";
  } else if (props.name.match(/\.(html)$/)) {
    return "language-html";
  } else if (props.name.match(/\.(css)$/)) {
    return "language-css";
  } else if (props.name.match(/\.(java)$/)) {
    return "language-java";
  } else if (props.name.match(/\.(cpp)$/)) {
    return "language-cpp";
  } else if (props.name.match(/\.(ts)$/)) {
    return "language-typescript";
  } else if (props.name.match(/\.(vue)$/)) {
    return "language-html";
  } else if (props.name.match(/\.(rs)$/)) {
    return "language-rust";
  } else if (props.name.match(/\.(txt)$/)) {
    return "language-vim";
  }
  return "no-language";
};

const loadBlobContent = async () => {
  if (!props.dataUrl) return;

  try {
    loading.value = true;
    const response = await fetch(props.dataUrl);
    const blob = await response.blob();
    codeContent.value = await blob.text();
  } catch (error) {
    loggerService.error("CodeViewer: Error loading blob content");
  }
  loading.value = false;
  loaded.value = true;
  await nextTick(async () => {
    Prism.highlightAll();
  });
};

// Load content when the component mounts or `dataUrl` changes
onMounted(async () => {
  loggerService.log("CodeViewer:onMounted");
  await loadBlobContent();
  Prism.highlightAll();
});

watch(() => props.dataUrl, loadBlobContent);
watch(() => codeContent, Prism.highlightAll());
</script>

<style scoped>
.code-loading {
  text-align: center;
}
</style>
