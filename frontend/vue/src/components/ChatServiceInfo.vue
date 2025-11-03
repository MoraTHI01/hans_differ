<template>
  <!-- ChatServiceInfo -->
  <div class="modal fade" tabindex="-1" role="dialog" ref="infoModal">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">{{ t("ChatServiceInfo.title") }}</h1>
          <button
            type="button"
            class="btn-close modal-close"
            @click="closeModal"
            :aria-label="t('ChatServiceInfo.closeButton')"
          ></button>
        </div>
        <div class="modal-body">
          <div v-if="data">
            <!-- Bootstrap Tabs for switching between contextList and contextListtranslation -->
            <ul class="nav nav-tabs" id="myMLServiceInfoTab" role="tablist">
              <template v-for="(item, index) in data.services" :key="index">
                <div v-if="item.type === 'llm'">
                  <li class="nav-item" role="presentation">
                    <button
                      class="nav-link active"
                      id="llm-info-tab"
                      data-bs-toggle="tab"
                      data-bs-target="#llm-info"
                      type="button"
                      role="tab"
                      aria-controls="llm-info"
                      aria-selected="true"
                    >
                      {{ t("ChatServiceInfo.llmService") }}
                    </button>
                  </li>
                </div>
                <div v-else-if="item.type === 'vllm'">
                  <li class="nav-item" role="presentation">
                    <button
                      class="nav-link"
                      id="vllm-info-tab"
                      data-bs-toggle="tab"
                      data-bs-target="#vllm-info"
                      type="button"
                      role="tab"
                      aria-controls="vllm-info"
                      aria-selected="false"
                    >
                      {{ t("ChatServiceInfo.vllmService") }}
                    </button>
                  </li>
                </div>
                <div v-else-if="item.type === 'embedding'">
                  <li class="nav-item" role="presentation">
                    <button
                      class="nav-link"
                      id="embedding-info-tab"
                      data-bs-toggle="tab"
                      data-bs-target="#embedding-info"
                      type="button"
                      role="tab"
                      aria-controls="embedding-info"
                      aria-selected="false"
                    >
                      {{ t("ChatServiceInfo.embeddingService") }}
                    </button>
                  </li>
                </div>
                <div v-else-if="item.type === 'translation'">
                  <li class="nav-item" role="presentation">
                    <button
                      class="nav-link"
                      id="translation-info-tab"
                      data-bs-toggle="tab"
                      data-bs-target="#translation-info"
                      type="button"
                      role="tab"
                      aria-controls="translation-info"
                      aria-selected="false"
                    >
                      {{ t("ChatServiceInfo.translationService") }}
                    </button>
                  </li>
                </div>
              </template>
            </ul>
            <div class="tab-content mt-3" id="myMLServiceInfoTabContent">
              <template v-for="(item, index) in data.services" :key="index">
                <div
                  v-if="item.type === 'llm'"
                  class="tab-pane fade show active"
                  id="llm-info"
                  role="tabpanel"
                  aria-labelledby="llm-info-tab"
                >
                  <ModelInfo
                    id="llm-info-model"
                    :modelId="item.info.model_id"
                    :modelSha="item.info.model_sha"
                    :modelDtype="item.info.model_dtype"
                    :modelMaxTotalTokens="item.info.max_total_tokens"
                    :modelMaxNewTokens="item.info.max_new_tokens"
                  />
                </div>
                <div
                  v-else-if="item.type === 'vllm'"
                  class="tab-pane fade"
                  id="vllm-info"
                  role="tabpanel"
                  aria-labelledby="vllm-info-tab"
                >
                  <ModelInfo
                    id="vllm-info-model"
                    :modelId="item.info.model_id"
                    :modelSha="item.info.model_sha"
                    :modelDtype="item.info.model_dtype"
                    :modelMaxTotalTokens="item.info.max_total_tokens"
                    :modelMaxNewTokens="item.info.max_new_tokens"
                  />
                </div>
                <div
                  v-else-if="item.type === 'embedding'"
                  class="tab-pane fade"
                  id="embedding-info"
                  role="tabpanel"
                  aria-labelledby="embedding-info-tab"
                >
                  <ModelInfo
                    id="embedding-info-model"
                    :modelId="item.info.model_id"
                    :modelSha="item.info.model_sha"
                    :modelDtype="item.info.model_dtype"
                    :modelMaxTotalTokens="item.info.max_total_tokens"
                    :modelMaxNewTokens="item.info.max_new_tokens"
                  />
                </div>
                <div
                  v-else-if="item.type === 'translation'"
                  class="tab-pane fade"
                  id="translation-info"
                  role="tabpanel"
                  aria-labelledby="translation-info-tab"
                >
                  <ModelInfo
                    id="translation-info-model"
                    :modelId="item.info.model_id"
                    :modelSha="item.info.model_sha"
                    :modelDtype="item.info.model_dtype"
                    :modelMaxTotalTokens="item.info.max_total_tokens"
                    :modelMaxNewTokens="item.info.max_new_tokens"
                  />
                </div>
              </template>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" @click="closeModal">
            {{ t("ChatServiceInfo.closeButton") }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <!-- ChatServiceInfo end -->
</template>

<script setup lang="ts">
import {defineExpose, ref} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {useMessageStore} from "@/stores/message";
import {MLServiceInfoResult} from "@/data/MLServiceInfo";
import ModelInfo from "./ModelInfo.vue";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const messageStore = useMessageStore();
const infoModal = ref(null);
const data = ref(null);

const chatServiceInfoOpenModal = async () => {
  if (infoModal.value) {
    loggerService.log("ChatServiceInfo:Open");
    data.value = await messageStore.queryServiceInfoFromApi();
    infoModal.value.classList.add("show");
    infoModal.value.style.display = "block";
    matomo_clicktracking("click_button", "Show chat services info");
  }
};

const closeModal = () => {
  if (infoModal.value) {
    loggerService.log("ChatServiceInfo:Close");
    infoModal.value.classList.remove("show");
    infoModal.value.style.display = "none";
    matomo_clicktracking("click_button", "Close chat services info");
  }
};

defineExpose({
  chatServiceInfoOpenModal,
});
</script>

<style scoped>
#myMLServiceInfoTab {
  min-width: 38vh;
}

.stack-button {
  float: right;
  border-radius: 15px;
  width: 48px;
  height: 32px;
  margin-bottom: 1vw;
}
.stack-img {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  width: 24px;
}
.modal-header {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
}
.modal-title {
  color: var(--hans-light);
}
.modal-close {
  color: var(--hans-light);
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}
</style>
