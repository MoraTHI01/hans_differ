<template>
  <!-- ExportTranscriptWindow -->
  <button
    :class="['btn', 'btn-primary', 'export-transcript-button']"
    :title="t('ExportTranscriptWindow.tooltipTranscriptExportButton')"
    @click="openModal"
    :disabled="props.disableComp"
  >
    <img src="/bootstrap-icons/download.svg" alt="api-btn" class="img-fluid export-transcript-img" />
  </button>
  <div class="modal fade export-transcript-modal" tabindex="-1" role="dialog" ref="myExportTranscriptModal">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">{{ t("ExportTranscriptWindow.title") }}</h1>
          <button
            type="button"
            class="btn-close modal-close"
            @click="closeModal"
            :aria-label="t('ExportTranscriptWindow.closeButton')"
          ></button>
        </div>
        <div class="modal-body">
          <div class="container mt-5">
            <div class="row">
              <div class="col-md-6">
                <!-- Language Selector Combobox -->
                <div class="mb-3">
                  <label for="languageSelect" class="form-label">{{
                    t("ExportTranscriptWindow.selectLanguage")
                  }}</label>
                  <select
                    id="languageSelect"
                    v-model="selectedLanguage"
                    class="form-select"
                    aria-label="Language select"
                  >
                    <option v-for="language in languages" :key="language.value" :value="language.value">
                      {{ t("ExportTranscriptWindow." + language.label) }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="col-md-6">
                <!-- File Type Selector -->
                <div class="mb-3">
                  <label for="fileTypeSelect" class="form-label">{{
                    t("ExportTranscriptWindow.selectFileType")
                  }}</label>
                  <select
                    id="fileTypeSelect"
                    v-model="selectedFileType"
                    class="form-select"
                    aria-label="File Type select"
                  >
                    <option value="txt">{{ t("ExportTranscriptWindow.textFile") }}</option>
                    <option value="vtt">{{ t("ExportTranscriptWindow.subtitleFile") }}</option>
                  </select>
                </div>
              </div>
            </div>
            <!-- Download Button -->
            <div class="mt-3">
              <button class="btn btn-primary" @click="downloadFile" :disabled="downloadDisabled">
                {{ t("ExportTranscriptWindow.download") }}
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" @click="closeModal">
            {{ t("ExportTranscriptWindow.closeButton") }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <!-- ExportTranscriptWindow end -->
</template>

<script setup lang="ts">
import axios from "axios";
import {defineProps, ref, watch} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {useMediaStore} from "@/stores/media";
import {apiClient} from "@/common/apiClient";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const mediaStore = useMediaStore();

const props = defineProps<{
  uuid: string;
  disableComp: boolean;
}>();

const myExportTranscriptModal = ref(null);
const downloadDisabled = ref(false);
const emit = defineEmits(["ExportTranscriptWindowClosed"]);

const languages = [
  {label: "english", value: "en"},
  {label: "german", value: "de"},
];

// Reactive properties
const selectedLanguage = ref<string>("en");
const selectedFileType = ref<string>("txt");

// Function to trigger the file download
const downloadFile = async () => {
  downloadDisabled.value = true;
  const language = selectedLanguage.value;
  const fileType = selectedFileType.value;
  const mediaItem = mediaStore.getMediaItemByUuid(props.uuid);

  // Construct the file name based on the selection
  const fileName = mediaItem.title + `.transcript-${language}.${fileType}`;

  // Create a Blob and simulate a download
  let content = "";
  if (fileType === "txt") {
    content = mediaStore.getCurrentTranscriptText(language);
  } else {
    let content_url = mediaItem.subtitle;
    if (language === "en") {
      content_url = mediaItem.subtitle_en;
    }
    const response = await axios.get(content_url, {headers: {"Access-Control-Allow-Origin": "*"}});
    content = response.data;
  }
  const blob = new Blob([content], {type: fileType === "txt" ? "text/plain" : "text/vtt"});
  const url = URL.createObjectURL(blob);

  // Create a temporary anchor element to initiate download
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();

  // Cleanup the object URL
  URL.revokeObjectURL(url);
  downloadDisabled.value = false;
};

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {});

const openModal = async () => {
  if (myExportTranscriptModal.value) {
    loggerService.log("ExportTranscriptWindow:Open");
    myExportTranscriptModal.value.classList.add("show");
    myExportTranscriptModal.value.style.display = "block";
    matomo_clicktracking("click_button", "Export transcript");
  }
};

const closeModal = () => {
  if (myExportTranscriptModal.value) {
    loggerService.log("ExportTranscriptWindow:Close");
    myExportTranscriptModal.value.classList.remove("show");
    myExportTranscriptModal.value.style.display = "none";
    matomo_clicktracking("click_button", "Close export transcript");
    emit("ExportTranscriptWindowClosed", true);
  }
};
</script>
<style scoped>
.export-transcript-modal {
}
.export-transcript-button {
  color: var(--hans-light);
  padding: 0.2em;
  width: 32px;
  height: 32px;
  align-items: center;
  left: 1em;
  border-radius: 25px;
  position: relative;
}
.export-transcript-button:hover {
  background-color: var(--hans-light);
}
.export-transcript-img {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  height: 24px;
  width: 24px;
  padding: 0.1em;
}
.export-transcript-button:hover > .export-transcript-img {
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
