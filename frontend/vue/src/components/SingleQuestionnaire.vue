<template>
  <HeaderRow />
  <LogoAndVideoSearchbarRow
    :placeholder="t('VideoPlayerView.searchplaceholder')"
    :surveys="mediaItem.surveys"
    :surveys_heading="t('VideoPlayerView.surveybanner')"
  />
  <div class="main-container">
    <div class="sub-container questionnaire-view">
      <aside>
        <h3 class="questionnaire-title">{{ t("LayoutOptions.questionnaire") }}</h3>
        <h5 class="difficulty-title">{{ t("EditChapter.difficultyTitle") }}:</h5>
        <DifficultySelector @difficultyChanged="setActiveDifficulty($event)" />
        <h5>{{ t("UploadChaptersView.topic") }}:</h5>
        <button
          v-for="(chapter, idx) in chapters"
          @click="changeChapter(chapter, idx)"
          :class="{topic: true, active: active?.result_index == chapter.result_index}"
        >
          {{ chapter.title }}
        </button>
      </aside>
      <main>
        <div class="questionnaire">
          <div v-if="finished_loading" class="previous">
            <button class="btn btn-primary skip-btn" @click="prevSlide" :disabled="currentQuestionIndex === 0">
              <img class="img-fluid left-arrow-image" src="/bootstrap-icons/arrow-left-circle.svg" alt="left arrow" />
            </button>
          </div>
          <div class="questionnaire-element">
            <QuestionnaireContent
              id="questionnaireContentStatic"
              class="static-questionnaire-content"
              ref="currentQuestionnaireRef"
            />
          </div>
          <div v-if="finished_loading" class="next">
            <button
              class="btn btn-primary skip-btn"
              @click="nextSlide"
              :disabled="currentQuestionIndex === currentQuestionnaires.length - 1"
            >
              <img
                class="img-fluid right-arrow-image"
                src="/bootstrap-icons/arrow-right-circle.svg"
                alt="right arrow"
              />
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import {ref, computed, nextTick, onMounted, onBeforeUnmount, watch} from "vue";
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoAndVideoSearchbarRow from "@/components/LogoAndVideoSearchbarRow.vue";
import QuestionnaireContent from "@/components/QuestionnaireContent.vue";
import DifficultySelector from "@/components/DifficultySelector.vue";
import type {MediaItem} from "@/data/MediaItem";
import type {TopicItem} from "@/data/Topics";
import type {QuestionnaireResultItem} from "@/data/QuestionnaireResult";
import type {MultipleChoiceQuestion} from "@/data/QuestionnaireResult";
import {matomo_trackpageview} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";
import {useMediaStore} from "@/stores/media";
import {useQuestionStore} from "@/stores/questions";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  mediaItem: MediaItem;
}>();
const mediaItem = props.mediaItem;
const uuid = mediaItem.uuid!;

const finished_loading = ref(false);

const chapters = ref<TopicItem[]>([]);
const questionnaires = ref<QuestionnaireResultItem[]>([]);
const active = ref<TopicItem>();
const activeQuestionnaire = ref<QuestionnaireResultItem>();

const currentQuestionnaires = ref(null);
const currentQuestionIndex = ref(0);
const currentQuestionnaireRef = ref(null);
const currentQuestionnaireItem = ref(null);

const mediaStore = useMediaStore();
const qStore = useQuestionStore();

const loadQuestionnaireData = async () => {
  finished_loading.value = false;
  await mediaStore.loadTopics(uuid, true).then(() => {
    chapters.value = mediaStore.topic.data?.find((topic) => topic.language == locale.value)?.result ?? [];
    active.value = chapters.value.length > 0 ? chapters.value[0] : undefined;
  });
  await mediaStore.loadQuestionnaire(uuid, true).then(() => {
    questionnaires.value =
      mediaStore.questionnaire.data?.find((questionnaire) => questionnaire.language == locale.value)?.result ?? [];
    activeQuestionnaire.value = questionnaires.value.length > 0 ? questionnaires.value[0] : undefined;
  });
  finished_loading.value = true;
};

const changeChapter = (chap, idx) => {
  active.value = chap;
  activeQuestionnaire.value = questionnaires.value[idx];
  updateQuestionnaire();
};

const updateQuestionnaire = () => {
  currentQuestionnaires.value = activeQuestionnaire.value.questionnaire[qStore.getDifficulty];
  currentQuestionIndex.value = 0;
  currentQuestionnaireItem.value = currentQuestionnaires.value[currentQuestionIndex.value];
  currentQuestionnaireRef.value.setQuestionnaire(currentQuestionnaireItem.value.mcq as MultipleChoiceQuestion);
};

const nextSlide = () => {
  if (currentQuestionIndex.value < currentQuestionnaires.value.length - 1) {
    currentQuestionIndex.value++;
    currentQuestionnaireItem.value = currentQuestionnaires.value[currentQuestionIndex.value];
    currentQuestionnaireRef.value.setQuestionnaire(currentQuestionnaireItem.value.mcq as MultipleChoiceQuestion);
  }
};

const prevSlide = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
    currentQuestionnaireItem.value = currentQuestionnaires.value[currentQuestionIndex.value];
    currentQuestionnaireRef.value.setQuestionnaire(currentQuestionnaireItem.value.mcq as MultipleChoiceQuestion);
  }
};

const setActiveDifficulty = (val) => {
  updateQuestionnaire();
};

onMounted(async () => {
  await loadQuestionnaireData();
});

watch(locale, async (newText) => {
  await loadQuestionnaireData();
});

watch(finished_loading, () => {
  updateQuestionnaire();
});
</script>
<style scoped>
.main-container {
  height: 100%;
}

h5 {
  margin-top: 1rem;
}

.sub-container {
  width: 100%;
  border: 1px solid var(--hans-light-gray);
  border-radius: 0.25rem;
  display: grid;
  grid-template-columns: 40% 60%;
  min-height: 58vh !important;
}

aside {
  border-right: 1px solid var(--hans-light-gray);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  grid-column: 1;
}

.topic {
  border: none;
  border-radius: 0.25rem;
  background-color: transparent;
  width: 100%;
  min-width: 10rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem 0.75rem;
}

.topic:hover {
  text-decoration: underline;
}

.topic.active {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
}

.questionnaire-view {
  border: 1px solid var(--hans-light-gray);
  border-radius: 0.25rem;
  height: 100%;
}

.questionnaire {
  display: grid;
  grid-template-columns: 15% 70% 15%;
  height: 100%;
}

.previous {
  justify-self: start;
  grid-column: 1;
}

.questionnaire-element {
  justify-self: center;
  grid-column: 2;
  margin-left: 2em;
  margin-right: 2em;
}

.next {
  justify-self: end;
  grid-column: 3;
}

.skip-btn {
  height: 100%;
  width: max-content;
  position: relative;
}

#questionnaireContentStatic {
  height: 100%;
  margin-top: 1em;
}

.left-arrow-image {
  width: 32px;
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}

.right-arrow-image {
  width: 32px;
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}

@media (max-width: 600px) {
  .sub-container {
    grid-template-columns: auto;
  }
  aside {
    grid-column: 1;
    grid-row: 1;
  }
  main {
    grid-column: 1;
    grid-row: 2;
  }
  .left-arrow-image {
    width: 16px;
  }
  .right-arrow-image {
    width: 16px;
  }
}
</style>
