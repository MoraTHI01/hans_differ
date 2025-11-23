<template>
  <div class="questionnaire-container">
    <div v-if="messageStore.getServicesAvailable && genQuestionsActive">
      <div class="container questionnaire-settings justify-content-center align-items-center border-bottom">
        <label for="rangeValue" class="form-label">{{ t("QuestionnaireWithInterval.propertyIntervalLength") }}</label>
        <input id="rangeValue" type="range" class="form-range" min="1" max="5" v-model="contextMinutes" />
        <p v-if="contextMinutes > 1">{{ contextMinutes }} {{ t("QuestionnaireWithInterval.minutes") }}</p>
        <p v-else>{{ contextMinutes }} {{ t("QuestionnaireWithInterval.minute") }}</p>
      </div>
      <div
        v-if="!finished_loading && !messageStore.getRequestError"
        class="container d-flex justify-content-center align-items-center"
      >
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">{{ t("QuestionnaireWithInterval.loading") }}</span>
        </div>
        <p class="text-center questionnaire-generating">{{ t("QuestionnaireWithInterval.generating") }}</p>
      </div>
      <div v-else-if="messageStore.getRequestError" class="container d-flex justify-content-center align-items-center">
        <div class="alert alert-danger d-flex align-items-center" role="alert">
          <img
            class="img-fluid bi flex-shrink-0 me-2"
            width="24"
            height="24"
            src="/bootstrap-icons/exclamation-triangle-fill.svg"
            alt="error-image"
          />
          <div v-if="messageStore.getRequestWasCanceled">
            {{ t("QuestionnaireWithInterval.errorRequestCanceled") }}
          </div>
          <div v-else-if="messageStore.getRequestTimeoutError">
            {{ t("QuestionnaireWithInterval.errorRequestTimeout") }}
          </div>
          <div v-else>
            {{ t("QuestionnaireWithInterval.errorRequest") }}
          </div>
        </div>
      </div>
      <QuestionnaireContent
        id="questionnaireContentInterval"
        class="interval-questionnaire-content"
        ref="currentQuestionnaire"
        :hidden="!finished_loading"
      />
    </div>
    <div v-else>
      <ChatLoading></ChatLoading>
    </div>
  </div>
</template>

<script setup lang="ts">
import {defineExpose, nextTick, inject, onMounted, ref, watch} from "vue";
import type {Emitter, EventType} from "mitt";
import type {MediaItem} from "@/data/MediaItem.js";
import {SetPositionEvent} from "@/common/events";
import {useMediaStore} from "@/stores/media";
import {useMessageStore} from "@/stores/message";
import {useQuestionStore} from "@/stores/questions";
import ChatLoading from "@/components/ChatLoading.vue";
import QuestionnaireContent from "@/components/QuestionnaireContent.vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {QuestionnaireGenerator} from "@/common/genQuestionnaires";
import {MultipleChoiceQuestion} from "@/data/QuestionnaireResult";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  video: MediaItem;
}>();

const genQuestionsActive = ref(false);
const questionGenerator = new QuestionnaireGenerator();

const mediaStore = useMediaStore();
const messageStore = useMessageStore();
const qStore = useQuestionStore();

const finished_loading = ref(true);
const currentInterval = ref([0.0, 0.0]);

const eventBus: Emitter<Record<EventType, unknown>> = inject("eventBus")!;
const contextMinutes = ref(3);

const currentQuestionnaire = ref(null);

// Interval every contextMinutes
const calculateMatchingInterval = (timeInSeconds: number): [number, number] => {
  const intervalDurationInSeconds = contextMinutes.value * 60; // minutes to seconds

  // Calculate the number of intervals
  const numberOfIntervals = Math.floor(timeInSeconds / intervalDurationInSeconds);

  // Calculate the start and end times for the matching interval
  const intervalStart = numberOfIntervals * intervalDurationInSeconds;
  const intervalEnd = (numberOfIntervals + 1) * intervalDurationInSeconds;

  // Return the matching interval
  return [intervalStart, intervalEnd];
};

const handleInterval = async (matchedInterval: [number, number]) => {
  //loggerService.log("QuestionnaireWithInterval:handleInterval")
  if (messageStore.getServicesAvailable && genQuestionsActive.value === true) {
    //loggerService.log("QuestionnaireWithInterval:handleInterval: GenQuestionnaire")
    if (
      currentInterval.value[1] < matchedInterval[1] &&
      matchedInterval !== currentInterval.value &&
      finished_loading.value === true
    ) {
      finished_loading.value = false;
      loggerService.log("generateQuestionnaireForInteval");
      loggerService.log(matchedInterval);
      matomo_clicktracking("generate_questionaire", "Generate multiple choice question");
      matomo_clicktracking("generate_questionaire_interval_minutes", contextMinutes.value);
      const intervalContext = mediaStore.getCurrentTranscriptTextInInterval(locale.value, matchedInterval);
      const avoid: string[] = [""];
      const questionnaire = await questionGenerator.generateMcq(
        qStore.getDifficulty,
        avoid,
        locale.value,
        intervalContext,
        props.video.uuid,
        false,
      );
      loggerService.log(questionnaire);
      try {
        if (currentQuestionnaire.value) {
          currentQuestionnaire.value.setQuestionnaire(questionnaire as MultipleChoiceQuestion);
        } else {
          loggerService.error("Questionnaire instance is invalid!");
        }
      } catch (e) {
        loggerService.error("Questionnaire format error!");
      }
      currentInterval.value = matchedInterval;
      finished_loading.value = true;
    }
  }
};

onMounted(() => {
  eventBus.on("setPositionEvent", (event: SetPositionEvent) => {
    if (event !== undefined && event.position !== undefined) {
      const matchedInterval = calculateMatchingInterval(event.position);
      handleInterval(matchedInterval);
    }
  });

  eventBus.on("videoPlaying", (position: number) => {
    if (position !== undefined) {
      const matchedInterval = calculateMatchingInterval(position);
      handleInterval(matchedInterval);
    }
  });
});

// Method to validate and emit form validity to parent
const setActive = (value: boolean) => {
  loggerService.log("QuestionnaireWithInterval:setActive");
  genQuestionsActive.value = value;
  reload();
};

const reload = () => {
  nextTick(() => {
    finished_loading.value = true;
    currentInterval.value = [0.0, 0.0];
    handleInterval(currentInterval.value);
  });
};

defineExpose({setActive, reload});
</script>
<style scoped>
.questionnaire-container {
  overflow-y: auto;
  display: block;
  max-height: 56vh;
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
</style>
