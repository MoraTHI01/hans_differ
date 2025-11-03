<template>
  <div>
    <ol class="list-group list-group-flush">
      <li class="list-group-item d-flex justify-content-between align-items-start">
        <div class="ms-2 me-auto">
          <div class="fw-bold">{{ t("ModelInfo.modelId") }}</div>
          <p>
            <a class="link-text" :href="'https://huggingface.co/' + props.modelId" target="_blank">{{
              props.modelId
            }}</a>
          </p>
        </div>
      </li>
      <li class="list-group-item d-flex justify-content-between align-items-start">
        <div class="ms-2 me-auto">
          <div class="fw-bold">{{ t("ModelInfo.modelHash") }}</div>
          <p>{{ props.modelSha }}</p>
        </div>
      </li>
      <li class="list-group-item d-flex justify-content-between align-items-start">
        <div class="ms-2 me-auto">
          <div class="fw-bold">{{ t("ModelInfo.modelType") }}</div>
          <p>{{ props.modelDtype }}</p>
        </div>
      </li>
      <li class="list-group-item d-flex justify-content-between align-items-start">
        <div class="ms-2 me-auto">
          <div class="fw-bold">{{ t("ModelInfo.modelMaxToken") }}</div>
          <p>{{ props.modelMaxTotalTokens }}</p>
        </div>
      </li>
      <li class="list-group-item d-flex justify-content-between align-items-start">
        <div class="ms-2 me-auto">
          <div class="fw-bold">{{ t("ModelInfo.maxNewToken") }}</div>
          <p>{{ props.modelMaxNewTokens }}</p>
        </div>
      </li>
    </ol>
  </div>
</template>

<script setup lang="ts">
import {defineProps, ref} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {useMessageStore} from "@/stores/message";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  modelId: string;
  modelSha: string;
  modelDtype: string;
  modelMaxTotalTokens: string;
  modelMaxNewTokens: string;
}>();
</script>
<style scoped></style>
