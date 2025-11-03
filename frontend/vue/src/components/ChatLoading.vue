<template>
  <div class="container chat-container-loading justify-content-center align-items-center">
    <div class="container chat-container-loading-spinner d-flex justify-content-center align-items-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">{{ t("ChatLoading.loading") }}</span>
      </div>
    </div>
    <div class="container chat-container-loading-text">
      <p class="text-center ml-services-loading">{{ t("ChatLoading.loading") }}</p>
      <p class="text-center ml-services-loading">{{ t("ChatLoading.explanation") }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, watch, onMounted} from "vue";
import {useMessageStore} from "@/stores/message";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const messageStore = useMessageStore();
</script>

<style scoped>
.chat-container-loading {
  overflow-y: auto;
  word-break: break-word;
  cursor: default;
  height: max-content;
}
.chat-container-loading-spinner {
  width: 100%;
  height: max-content;
  top: 1em;
  position: relative;
}
.chat-container-loading-text {
  width: 100%;
  height: max-content;
  top: 1em;
  position: relative;
}
</style>
