<template>
  <!-- ChatSettingsWindow -->
  <button
    :class="['btn', 'btn-primary', 'form-control', 'settings-button']"
    :title="t('ChatSettingsWindow.tooltipSettingsButton')"
    @click="openModal"
    :disabled="props.disableComp"
  >
    <img src="/bootstrap-icons/gear-fill.svg" alt="api-btn" class="img-fluid settings-img" />
  </button>
  <div class="modal fade settings-modal" tabindex="-1" role="dialog" ref="mySettingsModal">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">{{ t("ChatSettingsWindow.title") }}</h1>
          <button
            type="button"
            class="btn-close modal-close"
            @click="closeModal"
            :aria-label="t('ChatSettingsWindow.closeButton')"
          ></button>
        </div>
        <div class="modal-body">
          <!-- Bootstrap Tabs for switching between contextList and contextListtranslation -->
          <ul class="nav nav-tabs" id="mySettingsTab" role="tablist">
            <li class="nav-item" role="presentation">
              <button
                class="nav-link active"
                id="llm-settings-tab"
                data-bs-toggle="tab"
                data-bs-target="#llm-settings"
                type="button"
                role="tab"
                aria-controls="llm-settings"
                aria-selected="true"
              >
                {{ t("ChatSettingsWindow.context") }}
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button
                class="nav-link"
                id="vllm-settings-tab"
                data-bs-toggle="tab"
                data-bs-target="#vllm-settings"
                type="button"
                role="tab"
                aria-controls="vllm-settings"
                aria-selected="false"
              >
                {{ t("ChatSettingsWindow.vision") }}
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button
                class="nav-link"
                id="tutor-tab"
                data-bs-toggle="tab"
                data-bs-target="#tutor"
                type="button"
                role="tab"
                aria-controls="tutor"
                aria-selected="false"
              >
                {{ t("ChatSettingsWindow.tutor") }}
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button
                class="nav-link"
                id="translation-tab"
                data-bs-toggle="tab"
                data-bs-target="#translation"
                type="button"
                role="tab"
                aria-controls="translation"
                aria-selected="false"
              >
                {{ t("ChatSettingsWindow.translation") }}
              </button>
            </li>
          </ul>
          <!-- Tab Content -->
          <div class="tab-content mt-3" id="mySettingsTabContent">
            <!-- First Tab: Context List -->
            <div class="tab-pane fade show active" id="llm-settings" role="tabpanel" aria-labelledby="llm-settings-tab">
              <div class="mt-3 general-container">
                <textarea
                  id="descriptionGeneral"
                  class="form-control general-description"
                  rows="4"
                  :value="t('ChatSettingsWindow.generalDescription')"
                  disabled
                  readonly
                ></textarea>
              </div>
              <ol class="list-group list-group-flush">
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <Switch
                    v-model="chatStore.switchContext"
                    :label="t('ChatSettingsWindow.modeContext')"
                    id="switchContext"
                    :isEnabled="true"
                    :description="t('ChatSettingsWindow.switchContextDescription')"
                    trackingMessageOn="Use media context for chat messages"
                    trackingMessageOff="Do not use media context for chat messages"
                  />
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <Switch
                    v-model="chatStore.switchCitation"
                    :label="t('ChatSettingsWindow.modeCitation')"
                    id="switchCite"
                    :isEnabled="chatStore.switchContext"
                    :description="t('ChatSettingsWindow.switchCitationDescription')"
                    trackingMessageOn="Use media context and cite for chat messages"
                    trackingMessageOff="Do not use media context and cite for chat messages"
                  />
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <Switch
                    v-model="chatStore.switchSelectedContext"
                    :label="t('ChatSettingsWindow.modeSelectedContext')"
                    id="switchCite"
                    :isEnabled="!chatStore.switchContext"
                    :description="t('ChatSettingsWindow.switchSelectedContextDescription')"
                    trackingMessageOn="Use selected media context and cite for chat messages"
                    trackingMessageOff="Do not use selected media context and cite for chat messages"
                  />
                </li>
              </ol>
            </div>
            <div class="tab-pane fade" id="vllm-settings" role="tabpanel" aria-labelledby="vllm-settings-tab">
              <ol class="list-group list-group-flush">
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <Switch
                    v-model="chatStore.switchVision"
                    :label="t('ChatSettingsWindow.modeVision')"
                    id="switchVision"
                    :isEnabled="true"
                    :description="t('ChatSettingsWindow.switchVisionDescription')"
                    trackingMessageOn="Use images as context with vllm"
                    trackingMessageOff="Do not use images as context with vllm"
                  />
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <Switch
                    v-model="chatStore.switchVisionSurroundingSlides"
                    :label="t('ChatSettingsWindow.modeVisionSurroundingSlides')"
                    id="switchVisionSurroundingSlides"
                    :isEnabled="chatStore.switchVision"
                    :description="t('ChatSettingsWindow.switchVisionSurroundingSlidesDescription')"
                    trackingMessageOn="Use surrounding slide images as context with vllm"
                    trackingMessageOff="Do not use surrounding slide images as context with vllm"
                  />
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <Switch
                    v-model="chatStore.switchVisionSnapshot"
                    :label="t('ChatSettingsWindow.modeVisionSnapshot')"
                    id="switchVisionSnapshot"
                    :isEnabled="!chatStore.switchVision && !chatStore.switchVisionSurroundingSlides"
                    :description="t('ChatSettingsWindow.switchVisionSnapshotDescription')"
                    trackingMessageOn="Use video snapshot image as context with vllm"
                    trackingMessageOff="Do not use video snapshot image as context with vllm"
                  />
                </li>
              </ol>
            </div>
            <div class="tab-pane fade" id="tutor" role="tabpanel" aria-labelledby="tutor-tab">
              <div class="mt-3 act-container">
                <textarea
                  id="descriptionGeneral"
                  class="form-control act-description"
                  rows="4"
                  :value="t('ChatSettingsWindow.actDescription')"
                  disabled
                  readonly
                ></textarea>
              </div>
              <ol id="tutor-list" class="list-group list-group-flush">
                <li id="tutor-item" class="list-group-item d-flex justify-content-between align-items-center">
                  <Switch
                    v-model="chatStore.switchTutor"
                    :label="t('ChatSettingsWindow.modeTutor')"
                    id="switchTutor"
                    :isEnabled="true"
                    :description="t('ChatSettingsWindow.switchTutorDescription')"
                    trackingMessageOn="Activate tutor mode"
                    trackingMessageOff="Deactivate tutor mode"
                  />
                </li>
              </ol>
            </div>
            <!-- Second Tab: translation -->
            <div class="tab-pane fade" id="translation" role="tabpanel" aria-labelledby="translation-tab">
              <ol id="translation-list" class="list-group list-group-flush">
                <li id="translation-item" class="list-group-item d-flex justify-content-between align-items-center">
                  <Switch
                    v-model="chatStore.switchTranslation"
                    :label="t('ChatSettingsWindow.modeTranslation')"
                    id="switchTranslation"
                    :isEnabled="chatStore.isTranslationEnabled"
                    :description="t('ChatSettingsWindow.switchTranslationDescription')"
                    trackingMessageOn="Translate chat messages"
                    trackingMessageOff="No translation for chat messages"
                  />
                </li>
              </ol>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" @click="closeModal">
            {{ t("ChatSettingsWindow.closeButton") }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <!-- ChatSettingsWindow end -->
</template>

<script setup lang="ts">
import {defineProps, ref, watch} from "vue";
import Switch from "@/components/Switch.vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {useChatStore} from "@/stores/chat";
import {apiClient} from "@/common/apiClient";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const chatStore = useChatStore();

const props = defineProps<{
  disableComp: boolean;
}>();

const mySettingsModal = ref(null);
const emit = defineEmits(["chatSettingsWindowClosed"]);

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {});

const openModal = async () => {
  if (mySettingsModal.value) {
    loggerService.log("ChatSettingsWindow:Open");
    chatStore.loadChatSettings();
    mySettingsModal.value.classList.add("show");
    mySettingsModal.value.style.display = "block";
    matomo_clicktracking("click_button", "Chat settings");
    chatStore.toggleSettingsOpen(true);
  }
};

const closeModal = () => {
  if (mySettingsModal.value) {
    loggerService.log("ChatSettingsWindow:Close");
    chatStore.storeChatSettings();
    mySettingsModal.value.classList.remove("show");
    mySettingsModal.value.style.display = "none";
    matomo_clicktracking("click_button", "Close chat settings");
    chatStore.toggleSettingsOpen(false);
    emit("chatSettingsWindowClosed", true);
  }
};
</script>
<style scoped>
.settings-modal {
}
.settings-button {
  color: var(--hans-light);
  padding: 5px;
  border-radius: 25px;
}
.settings-button:hover {
  background-color: var(--hans-light);
}
.settings-img {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  height: 24px;
  width: 32px;
}
.settings-button:hover > .settings-img {
  filter: invert(calc(var(--button-dark-mode, 0) - 0));
}
.general-container {
  border-bottom: 2px solid #000;
  padding: 10px;
  margin-bottom: 20px;
}
.general-description {
  width: 34vh;
  height: auto;
  resize: none;
  color: var(--hans-light);
  background-color: var(--hans-dark-blue);
}
.act-container {
  border-top: 2px solid #000;
  border-bottom: 2px solid #000;
  padding: 10px;
  margin-bottom: 20px;
  margin-top: 20px;
}
.act-description {
  width: 34vh;
  height: auto;
  resize: none;
  color: var(--hans-light);
  background-color: var(--hans-dark-blue);
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
