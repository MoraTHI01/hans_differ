<template>
  <!-- ChannelSettingsWindow -->
  <button
    :class="['btn', 'btn-primary', 'form-control', 'settings-button']"
    :title="t('ChannelSettingsWindow.tooltipSettingsButton')"
    @click="openModal"
    :disabled="false"
  >
    <img src="/bootstrap-icons/gear-fill.svg" alt="api-btn" class="img-fluid settings-img" />
  </button>
  <div class="modal fade settings-modal" tabindex="-1" role="dialog" ref="myChannelSettingsModal">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">{{ t("ChannelSettingsWindow.title") }}</h1>
          <button
            type="button"
            class="btn-close modal-close"
            @click="closeModal"
            :aria-label="t('ChannelSettingsWindow.closeButton')"
          ></button>
        </div>
        <div class="modal-body">
          <ul class="nav nav-tabs" id="mySettingsTab" role="tablist">
            <li v-if="!props.channelmode" class="nav-item" role="presentation">
              <button
                class="nav-link active"
                id="lms-gated-settings-tab"
                data-bs-toggle="tab"
                data-bs-target="#lms-gated-settings"
                type="button"
                role="tab"
                aria-controls="lms-gated-settings"
                aria-selected="true"
              >
                <img src="/bootstrap-icons/shield-lock-fill.svg" alt="api-btn" class="img-fluid copy-img" />
                {{ t("ChannelSettingsWindow.lmsGatedAccess") }}
              </button>
            </li>
          </ul>
          <!-- Tab Content -->
          <div class="tab-content mt-3" id="myChannelSettingsTabContent">
            <!-- First Tab: Context List -->
            <div
              class="tab-pane fade show active"
              id="lms-gated-settings"
              role="tabpanel"
              aria-labelledby="lms-gated-settings-tab"
            >
              <div class="mt-3 general-container">
                <textarea
                  id="descriptionGeneral"
                  class="form-control general-description"
                  rows="4"
                  :value="t('ChannelSettingsWindow.lmsGatedSettingsDescription')"
                  disabled
                  readonly
                ></textarea>
                <ol class="list-group list-group-flush">
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div class="form-group">
                      <label for="formGroupCourseId">{{ t("ChannelSettingsWindow.courseIdLabel") }}</label>
                      <input
                        type="text"
                        class="form-control"
                        v-model="currCourseId"
                        id="formGroupCourseId"
                        :disabled="changeGatedSettingsOngoing"
                        :placeholder="t('ChannelSettingsWindow.courseId')"
                      />
                      <button
                        type="submit"
                        @click="applyGatedSettings"
                        :disabled="changeGatedSettingsOngoing"
                        class="btn btn-primary"
                      >
                        {{ t("ChannelSettingsWindow.apply") }}
                      </button>
                      <button
                        type="submit"
                        @click="resetGatedSettings"
                        :disabled="changeGatedSettingsOngoing"
                        class="btn btn-danger"
                      >
                        {{ t("ChannelSettingsWindow.reset") }}
                      </button>
                    </div>
                    <div v-if="changeGatedSettingsOngoing" class="change-ongoing-spinner">
                      <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
                      <span class="" role="status">{{ t("ChannelSettingsWindow.changeOngoing") }}</span>
                    </div>
                  </li>
                </ol>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" :disabled="changeGatedSettingsOngoing" @click="closeModal">
            {{ t("ChannelSettingsWindow.closeButton") }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <!-- ChannelSettingsWindow end -->
</template>

<script setup lang="ts">
import {defineProps, ref, watch} from "vue";
import type {ChannelItem} from "@/data/ChannelItem";
import type {MediaItem} from "@/data/MediaItem";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {useChatStore} from "@/stores/chat";
import {apiClient} from "@/common/apiClient";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const chatStore = useChatStore();

const props = defineProps<{
  channelItem: ChannelItem;
}>();

const myChannelSettingsModal = ref(null);
const currCourseId = ref("");

if (props.channelItem?.lms_gated_access === true) {
  currCourseId.value = props.channelItem?.lms_gated_access_details?.course_id;
}

const emit = defineEmits(["channelSettingsWindowClosed", "channelSettingsWindowRefresh"]);
const changeGatedSettingsOngoing = ref(false);

const openModal = async () => {
  if (myChannelSettingsModal.value) {
    loggerService.log("ChannelSettingsWindow:Open");
    chatStore.loadChatSettings();
    myChannelSettingsModal.value.classList.add("show");
    myChannelSettingsModal.value.style.display = "block";
    matomo_clicktracking("click_button", "Channel settings");
    chatStore.toggleSettingsOpen(true);
  }
};

const closeModal = () => {
  if (myChannelSettingsModal.value) {
    loggerService.log("ChannelSettingsWindow:Close");
    chatStore.storeChatSettings();
    myChannelSettingsModal.value.classList.remove("show");
    myChannelSettingsModal.value.style.display = "none";
    matomo_clicktracking("click_button", "Close channel settings");
    chatStore.toggleSettingsOpen(false);
    emit("channelSettingsWindowClosed", true);
  }
};

const applyGatedSettings = async () => {
  changeGatedSettingsOngoing.value = true;
  try {
    const uuid = props.channelItem.uuid!;
    const {data} = await apiClient.put(
      "/updateChannelProtection",
      {uuid, lmsGatedAccess: true, courseId: String(currCourseId.value)},
      {
        headers: {
          "Content-type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
    //loggerService.log(data);
    // Stores all uploaded videos in a map for fast lookup
    // Note that the Javascript Map preserves insertion order
    if ("result" in data && "success" in data.result) {
      loggerService.log(data.result.success);
      if (data.result.success === false) {
        loggerService.error(`Error during changing protection of channel: ${uuid}`);
      }
    } else {
      loggerService.error(`Connection issue during changing protection of channel: ${uuid}`);
    }
    matomo_clicktracking("click_button", `Channel item protection changed: lmsGatedAccess=${true}, channelId:${uuid}`);
  } catch (e) {
    // TODO
  }
  changeGatedSettingsOngoing.value = false;
  emit("channelSettingsWindowRefresh", true);
};

const resetGatedSettings = async () => {
  changeGatedSettingsOngoing.value = true;
  currCourseId.value = "";
  try {
    const uuid = props.channelItem.uuid!;
    const {data} = await apiClient.put(
      "/updateChannelProtection",
      {uuid, lmsGatedAccess: false, courseId: currCourseId.value},
      {
        headers: {
          "Content-type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
    //loggerService.log(data);
    // Stores all uploaded videos in a map for fast lookup
    // Note that the Javascript Map preserves insertion order
    if ("result" in data && "success" in data.result) {
      loggerService.log(data.result.success);
      if (data.result.success === false) {
        loggerService.error(`Error during changing protection of channel: ${uuid}`);
      }
    } else {
      loggerService.error(`Connection issue during changing protection of channel: ${uuid}`);
    }
    matomo_clicktracking("click_button", `Channel item protection changed: lmsGatedAccess=${false}, channelId:${uuid}`);
  } catch (e) {
    // TODO
  }
  changeGatedSettingsOngoing.value = false;
  emit("channelSettingsWindowRefresh", true);
};

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {});
</script>
<style scoped>
.settings-modal {
}
.settings-button {
  color: var(--hans-light);
  border-radius: 25px;
  width: fit-content;
  margin-left: auto;
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
