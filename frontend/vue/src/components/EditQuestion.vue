<template>
  <div class="question" v-if="!edit">
    <div class="top">
      <h4>{{ questionItem.mcq.question }}</h4>
      <div class="actions">
        <button @click="toggleEdit">{{ t("EditQuestion.edit") }}</button>
        <button v-if="props.questionCount > 1 && language === 'de'" @click="$emit('delete')">
          {{ t("EditQuestion.delete") }}
        </button>
      </div>
    </div>
    <label v-for="(answerItem, idx) in questionItem.mcq.answers" :key="idx">
      <input
        type="radio"
        :name="answerItem.answer"
        disabled
        :checked="questionItem.mcq.correct_answer_index === idx ? 'checked' : null"
      />
      {{ answerItem.answer }}
    </label>
    <div class="bottom">
      <h4>{{ t("EditQuestion.explanation") }}:</h4>
      <br />
      <h5 class="explanation">{{ questionItem.mcq.correct_answer_explanation }}</h5>
    </div>
  </div>
  <form class="question edit" v-if="edit" @submit.prevent>
    <div v-if="!isFormValid" class="text-danger mt-3">
      {{ t("EditQuestion.validationError") }}
    </div>
    <div class="top">
      <!-- Input for question title with validation -->
      <input
        type="text"
        id="question-title"
        v-model="questionItem.mcq.question"
        class="form-control title"
        :class="{'is-invalid': !isQuestionValid && isTouchedQuestion, 'is-valid': isQuestionValid && isTouchedQuestion}"
        @blur="validateQuestion"
        @change="updateQuestionHeader($event)"
        :placeholder="t('EditQuestion.questionPlaceholder')"
      />

      <!-- Validation feedback -->
      <div v-if="!isQuestionValid && isTouchedQuestion" class="invalid-feedback">
        {{ t("EditQuestion.questionValidation") }}
      </div>
      <button class="button-save" @click="toggleEdit">{{ t("EditQuestion.saveQuestion") }}</button>
    </div>
    <label v-for="(answerItem, idx) in questionItem.mcq.answers" :key="idx">
      <input
        type="radio"
        @change="updateRadio(idx, $event)"
        name="answer"
        :value="idx"
        :checked="questionItem.mcq.correct_answer_index === idx ? 'checked' : null"
      />
      <!-- Input for answer text with validation -->
      <input
        class="form-control"
        type="text"
        v-model="answerItem.answer"
        @change="updateText(idx, $event)"
        :class="{
          'is-invalid': !isAnswerValid(idx) && touchedAnswers[idx],
          'is-valid': isAnswerValid(idx) && touchedAnswers[idx],
          answer: true,
        }"
        @blur="markAsTouched(idx)"
        :id="'answer' + idx"
        :placeholder="t('EditQuestion.answerPlaceholder')"
      />
      <!-- Validation feedback for each answer -->
      <div v-if="!isAnswerValid(idx) && touchedAnswers[idx]" class="invalid-feedback">
        {{ t("EditQuestion.answerValidation") }}
      </div>
      <!-- <button class="delete" v-if="questionItem.mcq.answers.length > 2" @click="deleteAnswer(idx)">
        <img width="24" height="24" src="/bootstrap-icons/trash.svg" alt="trash" class="img-fluid img-btn">
      </button> -->
    </label>
    <!-- <button @click="addAnswer">
      <img width="24" height="24" src="/bootstrap-icons/plus.svg" alt="add" class="img-fluid img-btn">
      {{ t("EditQuestion.addAnswer") }}
    </button> -->
    <div class="bottom">
      <label for="explanation" class="form-label">{{ t("EditQuestion.explanation") }}</label>
      <textarea
        id="explanation"
        v-model="questionItem.mcq.correct_answer_explanation"
        class="form-control explanation"
        :class="{
          'is-invalid': !isExplanationValid && isExplanationTouched,
          'is-valid': isExplanationValid && isExplanationTouched,
        }"
        rows="4"
        @blur="validateExplanation"
        @change="updateExplanation($event)"
        :placeholder="t('EditQuestion.explanationPlaceholder')"
      ></textarea>
      <!-- Validation feedback -->
      <div v-if="!isExplanationValid && isExplanationTouched" class="invalid-feedback">
        {{ t("EditQuestion.explanationValidation") }}
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
import {computed, defineExpose, ref} from "vue";
import {QuestionItem} from "@/data/QuestionnaireResult";
import {useI18n} from "vue-i18n";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t} = useI18n({useScope: "global"});
const questionItem = defineModel<QuestionItem>("question", {required: true});

const props = defineProps<{
  language: string;
  questionCount: number;
  directEdit: boolean;
}>();

defineEmits(["delete"]);

const edit = ref(false);
const changed = ref(false);

if (props.directEdit.value === true) {
  edit.value = true;
}

function toggleEdit() {
  edit.value = !edit.value;
  matomo_clicktracking("click_button", `Question edit mode toggled`);
  if (changed.value === true) {
    validateForm();
    questionItem.value.mcq.editor = "lecturer";
    matomo_clicktracking("click_button", `Question modified by lecturer`);
  }
}

function updateQuestionHeader(event: Event) {
  questionItem.value.mcq.question = (event.target as HTMLInputElement).value;
  changed.value = true;
  matomo_clicktracking("click_button", `Question text modified`);
}

function updateExplanation(event: Event) {
  questionItem.value.mcq.correct_answer_explanation = (event.target as HTMLInputElement).value;
  changed.value = true;
  matomo_clicktracking("click_button", `Explanation for correct answer changed`);
}

// State for tracking if the input has been touched (used to show validation after user interaction)
const isTouchedQuestion = ref(false);

// Validation logic for question: checks if the question title is at least 5 characters long
const isQuestionValid = computed(() => {
  return questionItem.value.mcq.question.length >= 5;
});

// Trigger validation when input loses focus
const validateQuestion = () => {
  isTouchedQuestion.value = true;
};

// Reactive array to track which answers have been touched (for validation)
const touchedAnswers = ref([false, false, false, false]);

function updateText(idx: number, event: Event) {
  questionItem.value.mcq.answers[idx].answer = (event.target as HTMLInputElement).value;
  changed.value = true;
  matomo_clicktracking("click_button", `Answer ${idx} text modified`);
}

function updateRadio(idx: number, event: Event) {
  //options.value.forEach((value) => (value.correct = !(event.target as HTMLInputElement).checked));
  //options.value[idx].correct = (event.target as HTMLInputElement).checked;
  questionItem.value.mcq.correct_answer_index = idx;
  changed.value = true;
  matomo_clicktracking("click_button", `Correct answer index changed to ${idx}`);
}

// Mark an answer input as touched when the user interacts with it (on blur)
const markAsTouched = (idx) => {
  touchedAnswers.value[idx] = true;
};

// Validation logic for answer text (at least 1 character long)
const isAnswerValid = (idx) => {
  return questionItem.value.mcq.answers[idx].answer.length >= 1;
};

// State for form validation
const isExplanationTouched = ref(false);

// Validation logic: checks if the explanation is at least 5 characters long
const isExplanationValid = computed(() => {
  return questionItem.value.mcq.correct_answer_explanation.length >= 5;
});

// Trigger validation when input is blurred
const validateExplanation = () => {
  isExplanationTouched.value = true;
};

// State to track form validation status
const isFormValid = ref(true);

// Method to trigger validation for all fields when Save button is clicked
const validateForm = () => {
  let isValid = true;

  // Mark title as touched and validate
  isTouchedQuestion.value = true;
  if (!isQuestionValid.value) {
    isValid = false;
  }

  // Mark explanation as touched and validate
  isExplanationTouched.value = true;
  if (!isExplanationValid.value) {
    isValid = false;
  }

  // Mark all answers as touched and validate each one
  for (let i = 0; i < touchedAnswers.value.length; i++) {
    touchedAnswers.value[i] = true;
    if (!isAnswerValid(i)) {
      isValid = false;
    }
  }

  // Update the overall form validation state
  isFormValid.value = isValid;

  if (isValid === false && edit.value === false) {
    toggleEdit();
  }
  return isValid;
};

function addAnswer() {
  //options.value.push({text: "", correct: false});
}

function deleteAnswer(idx: number) {
  //options.value.splice(idx, 1);
}

defineExpose({validateForm});
</script>

<style scoped>
h4 {
  margin-bottom: 0;
}

h5 {
  margin-bottom: 0;
}

.answer {
  min-width: max-content;
}

.question {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border: 1px solid var(--hans-light-gray);
  border-radius: 0.25rem;
  padding: 1rem 1.5rem;
  margin-top: 1rem;
  width: 100%;
}

.explanation {
  border: 1px solid var(--hans-light-gray);
  border-radius: 0.25rem;
  padding: 1rem 1.5rem;
  margin-top: 0.5rem;
  font-size: 1rem;
  resize: vertical; /* Allows vertical resizing only */
  min-height: 100px; /* Minimum height for textarea */
}

.top {
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.top > h4 {
  width: 90%;
  text-wrap: wrap;
}

.bottom {
  display: inline-grid;
}

.bottom > h4 {
  font-size: 1.175rem;
}

.edit .top {
  align-items: center;
}

.title {
  font-size: 1.275rem;
  font-weight: 500;
  flex: 1;
  margin-right: 0.5rem;
  min-width: max-content;
}

label {
  display: flex;
  align-items: center;
}

label input[type="radio"] {
  margin-right: 0.5rem;
}

label input[type="text"] {
  flex: 1;
}

.button-save {
  background-color: var(--hans-dark-blue);
  color: white;
  padding: 0.5rem 0.75rem;
}

button {
  border: none;
  border-radius: 0.25rem;
  background-color: transparent;
  width: fit-content;
}

.delete {
  margin-left: 0.5rem;
}

.actions {
  display: flex;
  gap: 1rem;
}

.actions button:hover {
  text-decoration: underline;
}
</style>
