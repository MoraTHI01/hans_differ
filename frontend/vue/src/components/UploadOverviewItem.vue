<template>
  <div class="upload-item-container">
    <UploadModal
      v-model="deleteModal"
      @submit="deleteItem"
      :title="t('UploadOverviewItem.deleteVideo')"
      :content="t('UploadOverviewItem.deleteVideoContent')"
    ></UploadModal>
    <UploadModal
      v-model="overwriteModal"
      @submit="overwriteItem"
      :title="t('UploadOverviewItem.overwriteVideo')"
      :content="t('UploadOverviewItem.overwriteVideoContent')"
    ></UploadModal>
    <div v-if="media.state?.published === true">
      <router-link
        :to="{name: 'VideoPlayer', query: {uuid: media.uuid}}"
        @click="matomo_clicktracking('click_videocard_uploadoverviewitem', media.title)"
      >
        <img class="img-fluid mediathumb grow" :src="media.thumbnails?.media" alt="thumbnail" height="221px" />
      </router-link>
    </div>
    <div v-else>
      <img class="img-fluid mediathumb grow" :src="media.thumbnails?.media" alt="thumbnail" height="221px" />
    </div>
    <div class="info">
      <div>
        <h3>{{ media.title }}</h3>
        <p>{{ media.description?.course }}</p>
      </div>
      <div class="state">
        <img
          v-if="media.state?.overall_step === 'PROCESSING'"
          src="/bootstrap-icons/hourglass-split.svg"
          class="progimg"
          alt="processing"
        />
        <img
          v-if="media.state?.overall_step === 'EDITING'"
          src="/bootstrap-icons/pencil-square.svg"
          class="progimg"
          alt="editing"
        />
        <img
          v-if="media.state?.overall_step === 'FINISHED'"
          src="/bootstrap-icons/check-circle-fill.svg"
          class="progimg"
          alt="finished"
        />
        <p>{{ parseState() }}</p>
      </div>
    </div>
    <div class="actions">
      <div class="buttons">
        <a class="button accent" v-if="parseAction() && parseAction()?.href" :href="parseAction()?.href">{{
          parseAction()?.text
        }}</a>
        <button
          class="button accent"
          v-if="parseAction() && parseAction()?.click"
          href=""
          @click.prevent="parseAction()?.click"
          :disabled="!messageStore.servicesAvailable"
        >
          {{ parseAction()?.text }}
        </button>
        <button class="btn btn-outline-danger" v-if="authStore.getRole() === 'admin'" @click="deleteModal = true">
          {{ t("UploadOverviewItem.deleteButton") }}
        </button>
        <button
          class="btn btn-outline-danger"
          v-if="
            (authStore.getRole() === 'admin' || authStore.getRole() === 'lecturer') &&
            media.state?.overall_step === 'EDITING'
          "
          @click="overwriteModal = true"
        >
          {{ t("UploadOverviewItem.overwriteButton") }}
        </button>
      </div>
      <div class="toggles" v-if="media.state?.overall_step === 'FINISHED'">
        <div class="toggle">
          <span>{{ t("UploadOverviewItem.publishedLabel") }}</span>
          <div class="form-check form-switch">
            <input
              class="form-check-input btn-lg"
              type="checkbox"
              role="switch"
              v-model="publishedRef"
              @change="setVisibility"
            />
          </div>
        </div>
        <div class="toggle">
          <span>{{ t("UploadOverviewItem.listedLabel") }}</span>
          <div class="form-check form-switch">
            <input
              class="form-check-input"
              type="checkbox"
              role="switch"
              v-model="listedRef"
              @change="setVisibility"
              :disabled="!publishedRef"
            />
          </div>
        </div>
        <div v-if="publishedRef" :id="`copy-wrapper-${media.uuid}`" class="copy-wrapper">
          <a class="copy-link" :href="`/video-player?uuid=${media.uuid}`" @click.prevent="copyDirectLink(media.uuid)"
            >{{ t("UploadOverviewItem.copyButton") }}
          </a>
          <img src="/bootstrap-icons/clipboard.svg" alt="api-btn" class="img-fluid copy-img clip" />
          <img src="/bootstrap-icons/check-circle-fill.svg" alt="api-btn" class="img-fluid copy-img check" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, watch} from "vue";
import type {MediaItem} from "@/data/MediaItem";
import {useI18n} from "vue-i18n";
import {apiClient} from "@/common/apiClient";
import router from "@/router";
import UploadModal from "@/components/UploadModal.vue";
import {useAuthStore} from "@/stores/auth";
import {useMessageStore} from "@/stores/message";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t} = useI18n({useScope: "global"});

const props = defineProps<{
  media: MediaItem;
}>();

const publishedRef = ref(props.media.state!.published);
const listedRef = ref(props.media.state!.listed);
const authStore = useAuthStore();
const messageStore = useMessageStore();

watch(publishedRef, () => {
  if (publishedRef.value == false) {
    listedRef.value = publishedRef.value;
  }
});

const deleteModal = ref(false);
const overwriteModal = ref(false);

async function setVisibility() {
  try {
    const uuid = props.media.uuid!;
    await apiClient.put(
      "/visibility",
      {uuid, published: publishedRef.value, listed: listedRef.value},
      {
        headers: {
          "Content-type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
    matomo_clicktracking(
      "click_button",
      `Media item visiblity changed: published=${publishedRef.value}, listed:${listedRef.value}`,
    );
  } catch (e) {
    // TODO
  }
}

function parseState() {
  const uuid = props.media.uuid!;
  switch (props.media.state?.overall_step) {
    case "PROCESSING":
      matomo_clicktracking("click_button", `Media item ${uuid}, state: PROCESSING`);
      return t("UploadOverviewItem.state.processing");
    case "EDITING":
      matomo_clicktracking("click_button", `Media item ${uuid}, state: EDITING`);
      return t("UploadOverviewItem.state.editing", {step: props.media.state.editing_progress!});
    case "FINISHED":
      matomo_clicktracking("click_button", `Media item ${uuid}, state: FINISHED`);
      return t("UploadOverviewItem.state.finished");
  }
}

function parseAction(): {text: string; href?: string; click?: () => void} | undefined {
  switch (props.media.state?.overall_step) {
    case "PROCESSING":
      return undefined;
    case "EDITING":
      return {
        text:
          props.media.state.editing_progress == 0
            ? t("UploadOverviewItem.cta.editing_0")
            : t("UploadOverviewItem.cta.editing"),
        href: `/upload/${props.media.state.editing_progress! + 1}?uuid=${props.media.uuid!}`,
      };
    case "FINISHED":
      return {text: t("UploadOverviewItem.cta.redo"), click: triggerRedo};
  }
}

async function triggerRedo() {
  try {
    const uuid = props.media.uuid!;
    await apiClient.post(
      "/redo",
      {uuid},
      {
        headers: {
          "Content-type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
    matomo_clicktracking("click_button", `Redo editing step for media item uuid: ${uuid}`);
    await router.push(`/upload/1?uuid=${uuid}`);
  } catch (e) {
    // TODO
  }
}

async function deleteItem() {
  try {
    const uuid = props.media.uuid!;
    await apiClient.post(
      "/delete",
      {uuid},
      {
        headers: {
          "Content-type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
    matomo_clicktracking("click_button", `Deleted media item uuid: ${uuid}`);
    location.reload();
  } catch (e) {
    // TODO
  }
}

async function overwriteItem() {
  try {
    const uuid = props.media.uuid!;
    await apiClient.post(
      "/overwriteEditProgress",
      {
        uuid: uuid,
      },
      {
        headers: {
          "Content-type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
    matomo_clicktracking("click_button", `Overwrite media item edit progress with uuid: ${uuid}`);
    location.reload();
  } catch (e) {
    // TODO
  }
}

async function copyDirectLink(uuid) {
  const copyWrapper = document.getElementById("copy-wrapper-" + uuid);
  matomo_clicktracking("click_button", `Copy direct link`);
  copyWrapper?.classList.add("copying");

  setTimeout(() => {
    copyWrapper?.classList.remove("copying");
  }, 2500);

  await navigator.clipboard.writeText(
    `${window.location.protocol}//${window.location.host}/video-player?uuid=${props.media.uuid}`,
  );
}
</script>

<style scoped>
.upload-item-container {
  width: 100%;
  border: 1px solid var(--hans-light-gray);
  border-radius: 0.25rem;

  display: flex;
  flex-direction: row;
  padding: 1.5rem;
  gap: 1.5rem;
}

.mediathumb {
  display: none;
  aspect-ratio: 4 / 3;
  height: 100%;
  width: 14rem;
  border-radius: 0.125rem;
}

@media (min-width: 768px) {
  .mediathumb {
    display: block;
  }
}

.progimg {
  width: 24px;
  height: 24px;
}

.state {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: bold;
}

.state p {
  margin-bottom: 0;
}

.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-bottom: 0.25rem;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: end;
}

.toggles {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: end;
}

.toggle {
  display: flex;
  gap: 1rem;
}

.button {
  border: none;
  background-color: var(--hans-light-gray);
  color: var(--hans-dark);
  text-decoration: none;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  text-align: center;
}

.button:hover {
  background-color: var(--hans-medium-gray);
}

.button.accent {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
}

.button.accent:hover {
  background-color: var(--hans-medium-blue);
}

.copy-wrapper {
  display: flex;
  align-items: center;
}

.copy-wrapper > .check {
  display: none;
}

.copy-wrapper.copying > .clip {
  display: none;
}

.copy-wrapper.copying > .check {
  display: block;
}

.copy-link {
  margin-right: 0.5rem;
}

.grow {
  transition: all 0.2s ease-in-out;
}

.grow:hover {
  transform: scale(1.1);
}
</style>
