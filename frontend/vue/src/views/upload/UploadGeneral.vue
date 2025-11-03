<template>
  <HeaderRow />
  <LogoAndSearchbarRow
    :placeholder="t('HomeView.searchplaceholder')"
    :showSearch="false"
    :showProgress="true"
    :progressLanguage="language"
    :progressLanguageDeMatchStep="1"
    :progressLanguageDeNotMatchStep="2"
    :progressTotalSteps="5"
  />
  <div class="main-container">
    <div class="sub-container management-view">
      <h1>{{ t(`UploadGeneral.editIn${capitalize(language)}`) }}</h1>
      <input
        class="title form-control form-input"
        :disabled="language != 'de'"
        :value="mediaItem?.title"
        ref="titleRef"
      />
      <div class="summary-wrapper">
        <span>{{ t("UploadGeneral.shortSummary") }}</span>
        <div class="short-summary" contenteditable="true" ref="shortSummaryRef"></div>
      </div>
      <div class="summary-wrapper">
        <span>{{ t("UploadGeneral.summary") }}</span>
        <div class="summary" contenteditable="true" ref="summaryRef">
          {{ store.summary.data?.find((entry) => entry.language === language)?.result?.[0].summary }}
        </div>
      </div>
    </div>
    <UploadNavigation :step="language == 'de' ? 1 : 2" :uuid="uuid" @save="upload" v-model:loading="uploading" />
  </div>
  <BottomRow />
</template>

<script lang="ts">
import {routeToRefreshMedia} from "@/common/loadMedia";

export default {
  beforeRouteEnter: routeToRefreshMedia,
};
</script>

<script setup lang="ts">
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import UploadNavigation from "@/components/UploadNavigation.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";

import {useRoute} from "vue-router";
import {useMediaStore} from "@/stores/media";
import {useI18n} from "vue-i18n";
import {apiClient} from "@/common/apiClient";
import {capitalize, ref} from "vue";
import router from "@/router";
import {useAuthStore} from "@/stores/auth";
import {matomo_trackpageview, matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

matomo_trackpageview();
const loggerService = new LoggerService();
const {t} = useI18n({useScope: "global"});

const uuid = useRoute().params.uuid as string;

const {language} = defineProps({
  language: {
    type: String,
    required: true,
  },
});

const uploading = ref(false);

const store = useMediaStore();
const authStore = useAuthStore();
const mediaItem = store.getMediaItemByUuid(uuid);
if (
  !mediaItem ||
  mediaItem.state?.overall_step !== "EDITING" ||
  !["de", "en"].includes(language) ||
  authStore.getRole() == "everybody"
) {
  router.push("/upload/overview");
} else {
  Promise.all([store.loadShortSummary(uuid, true), store.loadSummary(uuid, true)]).then(() => {
    loggerService.log(store.summary.data);
    if (!shortSummaryRef.value) {
      return;
    }
    shortSummaryRef.value.innerText =
      store.shortSummary.data?.find((entry) => entry.language === language)?.result?.[0].summary ?? "";
  });
}

const titleRef = ref<HTMLInputElement>();
const shortSummaryRef = ref<HTMLDivElement>();
const summaryRef = ref<HTMLDivElement>();

async function upload(nextUrl: string) {
  if (!mediaItem || !titleRef.value || !shortSummaryRef.value || !summaryRef.value) return;
  uploading.value = true;

  const bodyData = {
    uuid: mediaItem.uuid!,
    language: language,
    title: titleRef.value.value,
    short_summary: shortSummaryRef.value.innerText,
    summary: summaryRef.value.innerText,
  };

  try {
    await apiClient.put("/general", bodyData, {
      headers: {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      // Adjust timeout as needed, currently 360 seconds
      timeout: 360000,
    });
    matomo_clicktracking("click_button", `Upload edited title, summary, and short summary for media item: ${uuid}`);
    uploading.value = false;
    await router.push(nextUrl);
  } catch (e) {
    console.error(`Error uploading edited title, summary, and short summary for media item: ${uuid}`);
    uploading.value = false;
    await router.push("/upload/overview");
  }
}
</script>

<style scoped>
.main-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sub-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  border: 1px solid var(--hans-light-gray);
  border-radius: 0.25rem;
  padding: 2rem;
}

h1 {
  color: var(--hans-dark-blue);
  font-size: 1.5rem;
}

p {
  margin-bottom: 0;
}

.title {
  font-size: 2.5rem;
  font-weight: 500;
}

.hidden {
  display: none;
}

.summary-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.summary-wrapper span {
  color: var(--hans-dark-gray);
  font-size: 0.875rem;
  margin-left: 0.5rem;
}

.short-summary,
.summary {
  border: 1px solid var(--hans-light-gray);
  border-radius: 0.25rem;
  padding: 1rem 1.5rem;
}

button {
  border: none;
  border-radius: 25%;
  background-color: transparent;
}

button:hover {
  background-color: var(--hans-light-gray);
}

.management-view {
  height: 74vh;
  position: relative;
  overflow-y: scroll;
}
</style>
