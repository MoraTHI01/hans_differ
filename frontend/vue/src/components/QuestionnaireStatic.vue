<template>
  <div class="questionnaire-container">
    <div v-if="isActive" class="row justify-content-center">
      <div class="main-question-container">
        <div v-if="isActive && finished_loading" class="previous">
          <button class="btn btn-primary me-2" @click="prevSlide" :disabled="currentQuestionIndex === 0">
            <img class="img-fluid left-arrow-image" src="/bootstrap-icons/arrow-left-circle.svg" alt="left arrow" />
          </button>
          <p class="bottom-text">
            {{ t("QuestionnaireStatic.topic") }} {{ currentQuestionnaireItem.result_index + 1 }}
          </p>
        </div>
        <div class="slide-content">
          <QuestionnaireContent
            id="questionnaireContentStatic"
            class="static-questionnaire-content"
            ref="currentQuestionnaireRef"
          />
        </div>
        <div v-if="isActive && finished_loading" class="next">
          <button
            class="btn btn-primary me-2"
            @click="nextSlide"
            :disabled="currentQuestionIndex === currentQuestionnaires.length - 1"
          >
            <img class="img-fluid right-arrow-image" src="/bootstrap-icons/arrow-right-circle.svg" alt="right arrow" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {defineExpose, inject, onMounted, nextTick, ref, watch} from "vue";
import type {Emitter, EventType} from "mitt";
import type {MediaItem} from "@/data/MediaItem.js";
import {useMediaStore} from "@/stores/media";
import {useQuestionStore} from "@/stores/questions";
import QuestionnaireContent from "@/components/QuestionnaireContent.vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  video: MediaItem;
}>();

const isActive = ref(false);
const mediaStore = useMediaStore();
const qStore = useQuestionStore();
const questionnaireResults = ref(mediaStore.questionnaire);

const currentQuestionnaireItem = ref(null);
const currentQuestionnaires = ref(null);
const currentInterval = ref([0.0, 0.1]);
const finished_loading = ref(false);
const currentPosition = ref(0.0);
const currentQuestionIndex = ref(0);
const currentQuestionnaireRef = ref(null);
const visible = ref(false);

const isPositionInInterval = (posInSec: number, interval: [number, number]) => {
  if (posInSec >= interval[0] && posInSec <= interval[1]) {
    return true;
  }
  return false;
};

const loadCurrentQuestionnaireItemByPosition = (posInSec: number) => {
  //loggerService.log("QuestionnaireStatic:loadCurrentQuestionnaireItemByPosition: Start");
  //loggerService.log(`QuestionnaireStatic:loadCurrentQuestionnaireItemByPosition: ${posInSec}`);
  if (
    questionnaireResults.value !== undefined &&
    questionnaireResults.value !== null &&
    currentQuestionnaireRef.value !== undefined &&
    currentQuestionnaireRef.value !== null
  ) {
    const questionnaires =
      questionnaireResults.value.data?.find((questionnaire) => questionnaire.language == locale.value)?.result ?? [];
    loggerService.log("QuestionnaireStatic:loadCurrentQuestionnaireItemByPosition: CurrentQuestionnaires");
    loggerService.log(questionnaires);
    for (const tItem in questionnaires) {
      const qItem = questionnaires[tItem] as QuestionnaireResultItem;
      loggerService.log("QuestionnaireStatic:loadCurrentQuestionnaireItemByPosition: QuestionnaireResultItem");
      loggerService.log(qItem);
      if (isPositionInInterval(posInSec, qItem.interval) === true) {
        loggerService.log("QuestionnaireStatic:loadCurrentQuestionnaireItemByPosition: Found!");
        currentQuestionnaireItem.value = qItem;
        loggerService.log(
          `QuestionnaireStatic:loadCurrentQuestionnaireItemByPosition: Difficulty: ${qStore.getDifficulty}`,
        );
        currentQuestionnaires.value = qItem.questionnaire[qStore.getDifficulty];
        currentInterval.value = qItem.interval;
        currentPosition.value = posInSec;
        currentQuestionIndex.value = 0;
        loggerService.log(
          `QuestionnaireStatic:loadCurrentQuestionnaireItemByPosition: Index: ${currentQuestionIndex.value}`,
        );
        const finItem = qItem.questionnaire[qStore.getDifficulty][currentQuestionIndex.value];
        loggerService.log(
          `QuestionnaireStatic:loadCurrentQuestionnaireItemByPosition: ItemQuestion: ${finItem.mcq.question}`,
        );
        currentQuestionnaireRef.value.setQuestionnaire(finItem.mcq as MultipleChoiceQuestion);
        finished_loading.value = true;
        break;
      }
    }
  }
  //loggerService.log("QuestionnaireStatic:loadCurrentQuestionnaireItemByPosition: Exit");
};

const eventBus: Emitter<Record<EventType, unknown>> = inject("eventBus")!;

const handleInterval = async (positionInSec: number) => {
  if (isPositionInInterval(positionInSec, currentInterval.value) === false && isActive.value === true) {
    finished_loading.value = false;
    loadCurrentQuestionnaireItemByPosition(positionInSec);
  }
};

onMounted(async (): Promise<T> => {
  questionnaireResults.value = await mediaStore.loadQuestionnaire(props.video?.uuid);
  loadCurrentQuestionnaireItemByPosition(currentPosition.value);
  eventBus.on("setPositionEvent", (event: SetPositionEvent) => {
    if (event !== undefined && event.position !== undefined) {
      handleInterval(event.position);
    }
  });

  eventBus.on("videoPlaying", (position: number) => {
    if (position !== undefined) {
      handleInterval(position);
    }
  });
});

const nextSlide = () => {
  if (currentQuestionIndex.value < currentQuestionnaires.value.length - 1) {
    currentQuestionIndex.value++;
    currentQuestionnaireRef.value.setQuestionnaire(
      currentQuestionnaires.value[currentQuestionIndex.value].mcq as MultipleChoiceQuestion,
    );
  }
};

const prevSlide = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
    currentQuestionnaireRef.value.setQuestionnaire(
      currentQuestionnaires.value[currentQuestionIndex.value].mcq as MultipleChoiceQuestion,
    );
  }
};

// Method to validate and emit form validity to parent
const setActive = (value: boolean) => {
  loggerService.log("QuestionnaireStatic:setActive");
  isActive.value = value;
  reload();
};

const reload = () => {
  nextTick(() => {
    finished_loading.value = false;
    loadCurrentQuestionnaireItemByPosition(currentPosition.value);
  });
};

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {
  reload();
});

defineExpose({setActive, reload});
</script>
<style scoped>
.questionnaire-container {
  display: block;
  max-height: 56vh;
  width: 100%;
}

.questionnaire-settings {
  display: block;
  overflow-y: auto;
  word-break: break-word;
  cursor: default;
  height: max-content;
  margin-bottom: 1em;
}

.questionnaire-generating {
  margin-top: 20px;
  margin-left: 5px;
}

.main-question-container {
  /* margin-top: 2rem; */
  display: grid;
  /* grid-template-columns: repeat(3,1fr); */
  /* gap: 1rem; */
  width: 100%;
  bottom: 1rem;
  position: relative;
}

.previous {
  padding-top: 1em;
  justify-self: start;
  grid-column: 1;
}

.slide-content {
  justify-self: center;
  grid-column: 2;
  padding: 1em;
}

.next {
  padding-top: 1em;
  justify-self: end;
  grid-column: 3;
}

.left-arrow-image {
  height: 32px;
  width: 32px;
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}

.right-arrow-image {
  height: 32px;
  width: 32px;
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}

.bottom-text {
  position: absolute;
  bottom: 0;
  left: 0;
}
</style>
