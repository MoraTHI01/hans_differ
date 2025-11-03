<template>
  <div class="container questionnaire-content">
    <div class="row">
      <h6 class="questionnaire-question">{{ question }}</h6>
    </div>
    <div class="row d-flex justify-content-center form-check form-check-inline">
      <div class="col-4 questionnaire-answer" v-for="(option, index) in options" :key="index">
        <input
          type="radio"
          class="btn-check"
          name="options-outlined"
          :id="'option-' + index"
          autocomplete="off"
          v-model="selectedOption"
          :value="option"
          @click="checkAnswer(option.answer)"
        />
        <label
          v-if="showResult && isCorrectOption(option.answer)"
          class="btn btn-outline-success questionnaire-label"
          :for="'option-' + index"
        >
          {{ option.answer }}
          <!-- <img src="/bootstrap-icons/x-circle.svg" alt="api-btn" class="img-fluid questionnaire-img"/>-->
        </label>
        <label
          v-else-if="showResult && !isCorrectOption(option.answer)"
          class="btn btn-outline-danger questionnaire-label"
          :for="'option-' + index"
        >
          {{ option.answer }}
          <!-- <img src="/bootstrap-icons/x-circle.svg" alt="api-btn" class="img-fluid questionnaire-img"/> -->
        </label>
        <label v-else class="btn btn-outline-primary questionnaire-label" :for="'option-' + index">
          {{ option.answer }}
        </label>
      </div>
    </div>
    <div class="row">
      <div v-if="showResult" class="questionnaire-explanation">
        <h6 class="questionnaire-explanation-heading">
          {{ t("QuestionnaireWithInterval.explanation")
          }}<ButtonHint route="generalnotes" :hovertext="t('QuestionnaireWithInterval.hint')" :hint_after="true" />:
        </h6>
        <label class="btn btn-outline-primary questionnaire-label">
          {{ answerExplanation }}
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {defineExpose, ref, watch} from "vue";
import ButtonHint from "@/components/ButtonHint.vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import type {MultipleChoiceQuestion} from "@/data/QuestionnaireResult";
import {Answer} from "@/data/QuestionnaireResult";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

let question_text = "What is the capital of Germany?";
if (locale.value === "de") {
  question_text = "Wie heißt die Hauptstadt von Deutschland?";
}
const question = ref(question_text);
const defaultAnswers = [];
defaultAnswers.push({index: 0, answer: "London"} as Answer);
defaultAnswers.push({index: 1, answer: "Berlin"} as Answer);
defaultAnswers.push({index: 2, answer: "Madrid"} as Answer);
defaultAnswers.push({index: 3, answer: "Paris"} as Answer);
const options = ref(defaultAnswers);
const correctAnswer = ref("Berlin");
const answerExplanation = ref(
  "Berlin is the capital of Germany and has around 3.4 million inhabitants. As a separate federal state, with an area of 891 km², it is located in the federal state of Brandenburg.",
);
if (locale.value === "de") {
  answerExplanation.value =
    "Berlin ist die Hauptstadt Deutschlands und hat etwa 3,4 Millionen Einwohner. Als eigenes Bundesland, mit einer Fläche von 891 km², liegt es im Bundesland Brandenburg.";
}

const selectedOption = ref("");
const showResult = ref(false);
const cleanCorrectRegex = /[.,!?-\s]/;

const setQuestionnaire = (questionnaire: MultipleChoiceQuestion) => {
  loggerService.log("QuestionnaireContent: Set current questionnaire");
  showResult.value = false;
  selectedOption.value = "";
  question.value = questionnaire.question.trim();
  loggerService.log("QuestionnaireContent: Set current questionnaire answers");
  options.value = questionnaire.answers;
  loggerService.log("QuestionnaireContent: Set current questionnaire correct answer");
  correctAnswer.value = questionnaire.answers[questionnaire.correct_answer_index].answer;
  loggerService.log("QuestionnaireContent: Set current questionnaire explanation");
  answerExplanation.value = questionnaire.correct_answer_explanation;
  loggerService.log("QuestionnaireContent: Set current questionnaire finished");
};

const isCorrectOption = (option: string) => {
  const isCorrect =
    (showResult.value &&
      option.split(cleanCorrectRegex).join("").trim() ===
        correctAnswer.value.split(cleanCorrectRegex).join("").trim()) ||
    (showResult.value && option.trim().includes(correctAnswer.value.trim()));
  if (isCorrect === true) {
    matomo_clicktracking("verify_option_correct", "Multiple choice answer was correct.");
  } else {
    matomo_clicktracking("verify_option_wrong", "Multiple choice answer was wrong.");
  }
  return isCorrect;
};

const checkAnswer = (selected: string) => {
  if (showResult.value === false) {
    // Only track first clicked answer
    matomo_clicktracking("click_option", "Multiple choice answer selected");
  }
  selectedOption.value = selected;
  showResult.value = true;
};

defineExpose({setQuestionnaire});
</script>

<style scoped>
.questionnaire-content {
  display: block;
  overflow-y: auto;
  word-break: break-word;
  cursor: default;
  height: 36vh;
  /*max-height: 290px;*/
  /*min-height: 8em;*/
}

.questionnaire-img {
  width: 12px;
}

.questionnaire-answer {
  margin: 5px;
  width: fit-content;
}

.questionnaire-label {
  /*font-size: 8px;*/
}

.questionnaire-question {
  /*font-size: 12px;*/
}

.questionnaire-explanation {
  /*font-size: 12px;*/
}

.questionnaire-img {
  width: 12px;
}
</style>
