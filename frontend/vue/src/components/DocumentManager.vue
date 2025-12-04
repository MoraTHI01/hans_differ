<template>
  <div class="doc-man-container">
    <div v-if="showModal" class="modal d-block">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ t("DocumentManager.uploadFiles") }}</h5>
            <button type="button" class="btn-close" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <p class="mt-2">{{ t("DocumentManager.supportedFiles") }}</p>
            <p class="mt-2">{{ t("DocumentManager.uploadRestriction") }}</p>
            <div class="upload-box" @dragover.prevent="dragOver" @drop.prevent="dropFiles">
              <input
                type="file"
                multiple
                accept="image/*,application/pdf,.cs,.py,.js,.html,.css,.java,.cpp,.ts,.vue,.rs"
                ref="fileInput"
                class="d-none"
                @change="handleFileSelect"
              />
              <!-- Select Files and Drag & Drop area -->
              <button class="btn btn-primary" @click="selectFiles">{{ t("DocumentManager.selectFiles") }}</button>
              <p class="mt-2">{{ t("DocumentManager.dropFiles") }}</p>

              <!-- Files being selected for upload (Temp files) -->
              <ul class="list-group mt-3" v-if="tempFiles.length">
                <li v-for="(file, index) in tempFiles" :key="index" class="list-group-item">
                  <div class="d-flex justify-content-between align-items-center">
                    <span class="col-6 file-text"> {{ file.name }} ({{ formatSize(file.size) }}) </span>

                    <!-- Status display for each file -->
                    <span class="d-flex align-items-center">
                      <!-- Show processing spinner if the file is being processed -->
                      <span v-if="file.status === 'Processing'" class="text-warning">
                        <div class="spinner-border spinner-border-sm" role="status">
                          <span class="visually-hidden">Processing...</span>
                        </div>
                        Processing...
                      </span>

                      <!-- Status text with dynamic class -->
                      <span v-else :class="getStatusClass(file.status)">
                        {{ file.status }}
                      </span>
                    </span>
                  </div>
                </li>
              </ul>

              <!-- Error message if any -->
              <p class="text-danger" v-if="uploadError">{{ uploadError }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button
              class="btn btn-success"
              @click="startUpload"
              :disabled="uploading || processing || !tempFiles.length"
            >
              {{ t("DocumentManager.upload") }}
            </button>
            <button class="btn btn-secondary" @click="closeModal" :disabled="uploading || processing">
              {{ t("DocumentManager.close") }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="d-flex mt-3 doc-man-inner">
      <!-- File List -->
      <div class="file-list">
        <div class="file-list-header d-flex justify-content-between align-items-center">
          <div class="menu p-2 my-1 rounded border">{{ t("DocumentManager.list") }}</div>
          <button class="btn btn-primary p-2 my-1 upload-btn" @click="showModal = true">+</button>
        </div>
        <div
          v-if="channelStore.getChannelDocumentsLoading"
          class="container document-loading-spinner d-flex justify-content-center align-items-center"
        >
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">{{ t("ChatLoading.loading") }}</span>
          </div>
        </div>
        <ul v-else class="list-group my-docs">
          <li
            v-for="(file, index) in documentFiles"
            :key="index"
            :class="
              selectedFile == file
                ? 'list-group-item btn file-container button-dark selected-file'
                : 'list-group-item btn file-container button-dark'
            "
            @click="
              selectedFile = file;
              forceRerenderKey++;
            "
          >
            <div
              v-if="!isUser"
              :class="viewportWidth >= 768 ? 'row file-list-container' : 'row file-list-container container-small'"
            >
              <div class="col-1 file-icon-container">
                <img :src="getIcon(file)" alt="file-image" class="img-fluid img-file align-self-start" />
              </div>
              <div class="col-8">
                <span class="file-text align-self-center">{{ file.filename }}</span>
              </div>
              <div class="col-1 file-actions-container">
                <button
                  @click="changeVisibility(file)"
                  class="btn btn-primary form-control btn-vis-file"
                  data-bs-toggle="tooltip"
                  data-bs-placement="bottom"
                  :title="file.visible === true ? t('DocumentManager.visilityOn') : t('DocumentManager.visilityOff')"
                  :disabled="!canChangeVisibility"
                  :hidden="!canChangeVisibility"
                >
                  <img
                    v-if="file.visible === true"
                    src="/bootstrap-icons/eye.svg"
                    alt="eye icon"
                    class="img-fluid img-btn"
                  />
                  <img v-else src="/bootstrap-icons/eye-slash.svg" alt="eye with a slash" class="img-fluid img-btn" />
                </button>
                <button
                  @click="showDeleteFile(file)"
                  class="btn btn-primary form-control btn-del-file"
                  data-bs-toggle="tooltip"
                  data-bs-placement="bottom"
                  :title="t('DocumentManager.deleteFile')"
                  :disabled="!canDeleteFile"
                  :hidden="!canDeleteFile"
                >
                  <img src="/bootstrap-icons/trash.svg" alt="api-btn" class="img-fluid img-btn" />
                </button>
              </div>
            </div>
            <div
              v-else
              :class="viewportWidth >= 768 ? 'row file-list-container' : 'row file-list-container container-small'"
            >
              <div class="col-1 file-icon-container">
                <img :src="getIcon(file)" alt="file-image" class="img-fluid img-file align-self-start" />
              </div>
              <div class="col-10">
                <span class="file-text align-self-center">{{ file.filename }}</span>
              </div>
            </div>
          </li>
        </ul>
      </div>
      <div class="vl"></div>
      <!-- Preview Area -->
      <div class="preview-container-header">
        <div class="col">
          <div class="menu p-2 my-1 rounded border preview-heading-text align-self-start" style="display: inline-block">
            {{ t("DocumentManager.view") }}
          </div>
          <div
            v-if="selectedFile && selectedFile.mime_type === 'application/pdf'"
            class="menu p-2 my-1 rounded border preview-page-text align-self-center"
            style="display: inline-block"
          >
            {{ t("DocumentManager.page") }} {{ pageNumber }}
          </div>
        </div>
        <div class="preview-container" v-if="selectedFile" :key="forceRerenderKey">
          <img v-if="selectedFile.mime_type.startsWith('image/')" :src="selectedFile.url" class="img-thumbnail" />
          <div v-else-if="selectedFile.mime_type === 'application/pdf'" class="pdf-preview">
            <DocumentViewer :pdfUrl="selectedFile.url" @pageChanged="pageChanged($event)"></DocumentViewer>
          </div>
          <div v-else class="code-preview">
            <CodeViewer :name="selectedFile.mime_type" :dataUrl="selectedFile.url"></CodeViewer>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import DocumentViewer from "@/components/DocumentViewer.vue";
import UploadModal from "@/components/UploadModal.vue";
import {PlayEvent, PauseEvent, SetPositionEvent} from "@/common/events";
import type {Emitter, EventType} from "mitt";
import {useAuthStore} from "@/stores/auth";
import {useChannelStore} from "@/stores/channels";
import {h, onBeforeUnmount, inject, ref, render, onMounted, onUnmounted, watch} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import CodeViewer from "./CodeViewer.vue";
import {apiClient} from "@/common/apiClient";
import type {ChannelItem} from "@/data/ChannelItem";
import type {DocumentItem} from "@/data/DocumentItem";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const authStore = useAuthStore();
const channelStore = useChannelStore();
const viewportWidth = ref(window.innerWidth);

const props = defineProps<{
  channelItem: ChannelItem;
}>();

const emit = defineEmits<{}>();
const deleteFileModal = ref(false);
const forceRerenderKey = ref(0);

const documentFiles = ref<DocumentItem[]>([]);

onMounted(async () => {
  documentFiles.value = await channelStore.loadChannelDocuments(props.channelItem.uuid);
  console.log("DocumentsFetched!");
  console.log(documentFiles.value);
});

onBeforeUnmount(() => {});

const showDeleteFile = (currFile: DocumentItem) => {
  selectedFile.value = currFile;
  deleteFileModal.value = true;
};

const getIcon = (mFile: DocumentItem) => {
  console.log(mFile);
  if (mFile.mime_type === "application/pdf") {
    return "/bootstrap-icons/file-earmark-pdf.svg";
  } else if (mFile.filename.match(/\.(cs|py|js|html|css|java|cpp|ts|vue|rs)$/)) {
    return "/bootstrap-icons/file-earmark-code.svg";
  } else if (mFile.mime_type.startsWith("image/") === true) {
    return "/bootstrap-icons/file-earmark-image.svg";
  } else if (mFile.mime_type === "text/plain") {
    return "/bootstrap-icons/file-earmark-text.svg";
  }
  return "/bootstrap-icons/file-earmark.svg";
};

async function deleteFile() {
  try {
    //const uuid = props.media.uuid!;
    //await apiClient.post(
    //  "/delete",
    //  {uuid},
    //  {
    //    headers: {
    //      "Content-type": "application/json",
    //      "Access-Control-Allow-Origin": "*",
    //    },
    //  },
    //);
    //matomo_clicktracking("click_button", `Deleted file item uuid: ${uuid}`);
    //location.reload();
  } catch (e) {
    // TODO
  }
}

const changeVisibility = (currFile: DocumentItem) => {
  // TODO
  currFile.visible = !currFile.visible;
};

const closeModal = async () => {
  documentFiles.value = await channelStore.loadChannelDocuments(props.channelItem.uuid);
  showModal.value = false;
};

const isUser = ref(true);
const canChangeVisibility = ref(false);
const canDeleteFile = ref(false);
const pageNumber = ref(-1);
if (["admin", "lecturer"].includes(authStore.getRole())) {
  canChangeVisibility.value = true;
  canDeleteFile.value = true;
  isUser.value = false;
}

const pageChanged = (currPageNumber) => {
  pageNumber.value = currPageNumber;
};

const showModal = ref(false);
const uploading = ref(false);
const processing = ref(false);

const tempFiles = ref<
  {
    file: File;
    name: string;
    size: number;
    type: string;
    visible: boolean;
    preview?: string;
    uuid?: string;
    status: string;
  }[]
>([]);

const selectedFile = ref<DocumentItem | null>(null);

const fileInput = ref<HTMLInputElement | null>(null);
const uploadError = ref<string | null>(null);

const selectFiles = () => {
  fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    addTempFiles(Array.from(target.files));
  }
};

const dropFiles = (event: DragEvent) => {
  if (event.dataTransfer?.files) {
    addTempFiles(Array.from(event.dataTransfer.files));
  }
};

const addTempFiles = (newFiles: File[]) => {
  uploadError.value = null;
  newFiles.forEach((file) => {
    if (file.size > 100 * 1024 * 1024) {
      // 100MB limit
      uploadError.value = `File ${file.name} exceeds 100MB size limit.`;
      return;
    }
    const allowedTypes = ["image/png", "image/jpeg", "image/jpg", "application/pdf", "text/plain"];
    if (allowedTypes.includes(file.type) || file.name.match(/\.(cs|py|js|html|css|java|cpp|ts|vue|rs)$/)) {
      loggerService.log(file.type);
      let my_filetype = file.type;
      if (file.type === undefined || file.type === null || file.type == "") {
        my_filetype = "text/plain";
      }
      loggerService.log(my_filetype);
      const fileData = {file: file, name: file.name, size: file.size, type: my_filetype, visible: false};
      fileData.preview = URL.createObjectURL(file);
      tempFiles.value.push(fileData);
    }
  });
};

const deleteTempFile = (uuid: string) => {
  tempFiles.value = tempFiles.value.filter((file) => file.uuid !== uuid);
};

const startUpload = async () => {
  uploading.value = true;
  for (const fileObj of tempFiles.value) {
    await uploadFile(fileObj);
    const interval = setInterval(async () => {
      try {
        deleteTempFile(fileObj.uuid);
        documentFiles.value = await channelStore.loadChannelDocuments(props.channelItem.uuid);
        clearInterval(interval);
      } catch (error) {
        clearInterval(interval);
      }
    }, 3000);
  }
  uploading.value = false;
};

const updateFileStatus = () => {
  uploading.value = tempFiles.value.some((file) => file.status === "Uploading" || file.status === "Uploaded")
    ? true
    : false;
  processing.value = tempFiles.value.some((file) => file.status === "Processing" || file.status === "Completed")
    ? true
    : false;
};

const uploadFile = async (fileObj: {
  file: File;
  name: string;
  size: number;
  type: string;
  status: string;
  uuid?: string;
}) => {
  fileObj.status = "Uploading";
  const formData = new FormData();
  formData.append("uuid", props.channelItem.uuid);
  formData.append("language", props.channelItem.language);
  formData.append("document", fileObj.file);
  formData.append("filename", fileObj.name);
  formData.append("mimetype", fileObj.type);
  try {
    const response = await apiClient.post("/upload-document", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    if (response.data.status === 200 && response.data.result.uuid) {
      fileObj.uuid = response.data.result.uuid;
      fileObj.status = "Uploaded";
      updateFileStatus();

      // Start checking processing status
      checkProcessingStatus(fileObj);
    } else {
      throw new Error("Invalid response from server");
    }
  } catch (error) {
    fileObj.status = "Failed";
    console.error("Upload failed:", error);
  }
};

const checkProcessingStatus = async (fileObj: {uuid?: string; status: string}) => {
  if (!fileObj.uuid) return;
  fileObj.status = "Processing";
  processing.value = true;

  const interval = setInterval(async () => {
    try {
      const response = await apiClient.get(`/process-status/${fileObj.uuid}`);

      // Ensure response is in the expected format
      if (response.data.result) {
        const parsedResult = response.data.result;
        const status = parsedResult.status;

        if (status === "Completed") {
          fileObj.status = "Completed";
          documentFiles.value = await channelStore.loadChannelDocuments(props.channelItem.uuid);
          updateFileStatus();
          clearInterval(interval);
        } else if (status === "Failed") {
          fileObj.status = "Failed";
          clearInterval(interval);
        }
      }
    } catch (error) {
      console.error("Error fetching processing status", error);
      fileObj.status = "Failed";
      clearInterval(interval);
    }
  }, 3000);
  processing.value = false;
};

const getStatusClass = (status: string) => {
  if (status === "Processing") {
    processing.value = true;
    return "text-warning"; // Yellow color for processing
  } else if (status === "Uploaded") {
    return "text-primary"; // Blue color for uploaded
  } else if (status === "Completed") {
    return "text-success"; // Green color for completed
  } else if (status === "Failed") {
    return "text-danger"; // Red color for failed
  } else if (status === "Error") {
    return "text-danger"; // Red color for failed
  }
  return "";
};

const formatSize = (size: number) => {
  return size < 1024
    ? `${size} B`
    : size < 1048576
      ? `${(size / 1024).toFixed(1)} KB`
      : `${(size / 1048576).toFixed(1)} MB`;
};
</script>

<style scoped>
.doc-man-container {
  position: relative;
}
.doc-man-inner {
  overflow: hidden;
}
.container-small {
  width: 16vh;
  display: block;
  align-content: center;
}
.preview-heading-text {
  position: relative;
  width: min-content;
  height: min-content;
}
.preview-page-text {
  position: relative;
  width: max-content;
  height: min-content;
}
.modal {
  background: rgba(0, 0, 0, 0.5);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.file-list {
  width: 16vw;
}
.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.preview-container-header {
  width: 44vw;
  padding-left: 0.5em;
}
.preview-container {
  width: 98%;
}
.upload-box {
  padding: 20px;
  cursor: pointer;
  border: 2px dashed #ccc;
  text-align: center;
  border-radius: 10px;
}
.img-thumbnail {
  max-width: 100%;
  height: auto;
  margin-bottom: 10px;
}
.pdf-preview {
  padding: 10px;
  background: #f8f9fa;
  border: 1px solid #ccc;
  border-radius: 5px;
  text-align: center;
  width: 25vw;
}
.code-preview {
  padding: 10px;
  background: #f8f9fa;
  border: 1px solid #ccc;
  border-radius: 5px;
  text-align: left;
  width: 25vw;
}
.text-danger {
  color: red;
}
.my-1 {
  margin-top: 0.25rem !important;
  margin-bottom: 0.75rem !important;
}
.vl {
  border-right: 3px dashed #bbb;
  width: 0.5vw;
  height: 56vh;
}
.my-docs {
  overflow-y: auto;
  height: 50vh;
  margin-right: 0.2em;
}
.upload-btn {
  margin-right: 0.2em;
}
.file-container {
  display: flex;
  align-items: center;
  float: left;
  color: var(--hans-light);
}
.img-file {
  height: 24px;
  width: 32px;
}
.file-text {
  color: var(--hans-dark);
  text-wrap: wrap;
  overflow-wrap: break-word;
  inline-size: 16vh;
}
.file-container:hover {
  color: var(--hans-light);
  background-color: var(--hans-dark-blue);
}
.file-container:hover > div > div > .img-file {
  filter: invert(1);
}
.file-container:hover > div > div > .file-text {
  color: var(--hans-light);
}
.file-container:hover > div > div > .img-text {
  color: var(--hans-light);
}
.img-btn {
  height: 24px;
  width: 32px;
}
.btn-del-file {
  color: var(--hans-light);
  background-color: var(--hans-light-blue);
  padding: 5px;
  border-radius: 25px;
  width: 32px;
  height: 32px;
  align-items: center;
  position: relative;
  top: -5px;
  display: flex;
  margin-top: 0.1em;
}
.btn-del-file:hover > .img-btn {
  filter: invert(1);
}
.btn-vis-file {
  color: var(--hans-light);
  background-color: var(--hans-light-blue);
  padding: 5px;
  border-radius: 25px;
  width: 32px;
  height: 32px;
  align-items: center;
  position: relative;
  top: -5px;
  display: flex;
  margin-top: 0.1em;
}
.btn-vis-file:hover > .img-btn {
  filter: invert(1);
}
.selected-file {
  background-color: var(--hans-light-blue);
}
.file-icon-container {
  width: 48px;
}
.file-actions-container {
  width: 56px;
}
.file-list-container {
  display: contents;
}
</style>
