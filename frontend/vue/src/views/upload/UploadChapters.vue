<template>
  <HeaderRow />
  <LogoAndSearchbarRow
    :placeholder="t('HomeView.searchplaceholder')"
    :showSearch="false"
    :showProgress="true"
    :progressLanguage="language"
    :progressLanguageDeMatchStep="4"
    :progressLanguageDeNotMatchStep="5"
    :progressTotalSteps="5"
  />
  <div class="main-container">
    <div class="sub-container management-view">
      <aside>
        <button
          v-for="(chapter, idx) in chapters"
          @click="changeChapter(chapter, idx)"
          :class="{active: active?.result_index == chapter.result_index}"
          :disabled="uploading"
        >
          {{ t("UploadChaptersView.topic") }} {{ idx + 1 }}
        </button>
      </aside>
      <select
        class="form-select"
        @change="active = chapters[Number(($event.target as HTMLSelectElement).value)]"
        :disabled="uploading"
      >
        <option v-for="(_, idx) in chapters" :key="idx" :value="idx">
          {{ t("UploadChaptersView.topic") }} {{ idx + 1 }}
        </option>
      </select>
      <EditChapter
        v-if="active && activeQuestionnaire"
        v-model:model="active"
        ref="editChapterRef"
        v-model:questionnaire="activeQuestionnaire"
        :language="language"
        :uuid="uuid"
        @difficultyChanged="handleFormValidation"
        :disabled="uploading"
      ></EditChapter>
    </div>
    <UploadNavigation
      :step="language == 'de' ? 4 : 5"
      :uuid="uuid"
      @save="upload"
      v-model:loading="uploading"
      ref="uploadNav"
    />
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
import UploadNavigation from "@/components/UploadNavigation.vue";
import EditChapter from "@/components/EditChapter.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import LogoAndSearchbarRow from "@/components/LogoAndSearchbarRow.vue";

import {useI18n} from "vue-i18n";
import {ref} from "vue";
import {useRoute} from "vue-router";
import {useMediaStore} from "@/stores/media";
import {apiClient} from "@/common/apiClient";
import router from "@/router";
import type {TopicItem} from "@/data/Topics";
import type {QuestionnaireResultItem} from "@/data/QuestionnaireResult";
import {useAuthStore} from "@/stores/auth";
import {matomo_trackpageview, matomo_clicktracking} from "@/common/matomo_utils";

matomo_trackpageview();
const {t} = useI18n({useScope: "global"});

const {language} = defineProps({
  language: {
    type: String,
    required: true,
  },
});

const chapters = ref<TopicItem[]>([]);
const questionnaires = ref<QuestionnaireResultItem[]>([]);
const active = ref<TopicItem>();
const activeQuestionnaire = ref<QuestionnaireResultItem>();
const uploading = ref(false);

// Reference to the edit chapter child component
const editChapterRef = ref(null);

const uploadNav = ref(null);

const uuid = useRoute().params.uuid as string;

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
  store.loadTopics(uuid, true).then(() => {
    chapters.value = store.topic.data?.find((topic) => topic.language == language)?.result ?? [];
    active.value = chapters.value.length > 0 ? chapters.value[0] : undefined;
  });
  store.loadQuestionnaire(uuid, true).then(() => {
    questionnaires.value =
      store.questionnaire.data?.find((questionnaire) => questionnaire.language == language)?.result ?? [];
    activeQuestionnaire.value = questionnaires.value.length > 0 ? questionnaires.value[0] : undefined;
  });
  store.loadTranscriptResults(uuid);
}

const changeChapter = (chap, idx) => {
  const valid = editChapterRef.value.isFormValid();
  if (!valid) return;
  active.value = chap;
  activeQuestionnaire.value = questionnaires.value[idx];
};

// Method to handle form validation event from child
const handleFormValidation = (isValid) => {
  uploadNav.value.toggleNavigationClickable(isValid);
};

async function upload(nextUrl: string) {
  if (!mediaItem) return;
  const valid = editChapterRef.value.isFormValid();
  if (!valid) return;
  uploading.value = true;

  const bodyData = {
    uuid,
    topicResult: {
      type: "TopicResult",
      language: language,
      result: store.topic.data?.find((topic) => topic.language == language)?.result,
    },
    questionnaireResult: {
      type: "QuestionnaireResult",
      language: language,
      result: store.questionnaire.data?.find((questionnaire) => questionnaire.language == language)?.result,
    },
  };

  try {
    await apiClient.post("/chapters", bodyData, {
      headers: {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      // Adjust timeout as needed, currently 120 seconds
      timeout: 120000,
    });
    matomo_clicktracking("click_button", `Upload edited chapters and questions for media item: ${uuid}`);
    uploading.value = false;
    await router.push(nextUrl);
  } catch (e) {
    console.error(`Error uploading edited chapters and questions for media item: ${uuid}`);
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
  width: 100%;
  border: 1px solid var(--hans-light-gray);
  border-radius: 0.25rem;
  display: grid;
  grid-template-columns: auto 1fr;
}

aside {
  border-right: 1px solid var(--hans-light-gray);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

select {
  display: none;
  margin: 2rem 2rem 0;
  width: calc(100% - 4rem);
}

@media (max-width: 768px) {
  .sub-container {
    display: flex;
    flex-direction: column;
  }

  select {
    display: block;
  }

  aside {
    display: none;
  }
}

button {
  border: none;
  border-radius: 0.25rem;
  background-color: transparent;
  width: 100%;
  min-width: 10rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem 0.75rem;
}

button:hover {
  text-decoration: underline;
}

button.active {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
}

.management-view {
  height: 74vh;
  position: relative;
  overflow-y: scroll;
}
</style>
