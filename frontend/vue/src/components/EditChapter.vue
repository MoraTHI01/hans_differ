<template>
  <main>
    <h1>{{ t(`UploadGeneral.editIn${capitalize(props.language)}`) }}</h1>
    <input class="title form-control form-input" :value="model.title" @change="updateTitle($event)" />
    <div contenteditable="true" class="summary form-control" @input="updateSummary($event)" :innerText="summaryRef" />
    <h3 class="questions-heading">{{ t("EditChapter.heading") }}</h3>
    <textarea
      v-if="language === 'de'"
      id="readonlyText"
      class="container"
      rows="3"
      v-model="instructions"
      readonly
    ></textarea>
    <h5 class="difficulty-title">{{ t("EditChapter.difficultyTitle") }}</h5>
    <DifficultySelector v-model:validatorFormComp="questionRef" @difficultyChanged="setActiveDifficulty($event)">
    </DifficultySelector>
    <h5 class="questions-title">{{ t("EditChapter.questionsTitle") }}</h5>
    <div class="questions-select">
      <button
        v-for="(question, idx) in questionnaireResultItem.questionnaire[activeDifficulty]"
        :key="question"
        @click="setActiveQuestion(idx)"
        :class="{active: activeQuestion == idx}"
      >
        {{ t("EditChapter.question") }} {{ idx + 1 }}
      </button>
      <button
        v-if="messageStore.isRequestOngoing || llmGenerationOngoing"
        class="btn btn-primary d-flex align-items-center"
        type="button"
        disabled
      >
        <div class="spinner-border text-primary" role="status" style="width: 24px; height: 24px">
          <span class="visually-hidden">{{ t("EditChapter.generating") }}</span>
        </div>
      </button>
      <button v-else-if="language === 'de'" class="btn btn-primary" @click="addQuestion">
        <img width="24" height="24" src="/bootstrap-icons/plus.svg" alt="add question" class="img-fluid" />
      </button>
      <div v-if="language === 'de'" class="llm-switches">
        <div class="form-check form-switch llm-switch">
          <input
            class="form-check-input"
            type="checkbox"
            id="flexSwitchCheckChecked"
            v-model="useLLMtoAdd"
            :disabled="llmGenerationOngoing"
          />
          <label class="form-check-label" for="flexSwitchCheckChecked">{{ t("EditChapter.useLLM") }}</label>
        </div>
        <div class="form-check form-switch">
          <input
            class="form-check-input"
            type="checkbox"
            id="flexSwitchReasoningChecked"
            v-model="useLLMReasoning"
            :disabled="llmGenerationOngoing || !useLLMtoAdd"
          />
          <label class="form-check-label" for="flexSwitchReasoningChecked">{{
            t("EditChapter.useLLMReasoning")
          }}</label>
        </div>
      </div>
    </div>
    <div v-if="questionnaireResultItem.questionnaire[activeDifficulty].length > 0" class="question-container">
      <EditQuestion
        class="question-item"
        ref="questionRef"
        v-model:question="currQuestionItem"
        :questionCount="questionnaireResultItem.questionnaire[activeDifficulty].length"
        @delete="deleteQuestion"
        :language="props.language"
        :directEdit="doDirectEdit"
        @formValidation="handleFormValidation"
      />
    </div>
  </main>
</template>

<script setup lang="ts">
import {capitalize, defineExpose, ref, watch} from "vue";
import DifficultySelector from "@/components/DifficultySelector.vue";
import EditQuestion from "@/components/EditQuestion.vue";
import {TopicItem} from "@/data/Topics";
import {Answer, MultipleChoiceQuestion, QuestionItem, QuestionnaireResultItem} from "@/data/QuestionnaireResult";
import {useI18n} from "vue-i18n";
import {useMediaStore} from "@/stores/media";
import {useMessageStore} from "@/stores/message";
import type {Message, MessageContent} from "@/data/Message";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {QuestionnaireGenerator} from "@/common/genQuestionnaires";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();

const {t, locale} = useI18n({useScope: "global"});
const mediaStore = useMediaStore();
const messageStore = useMessageStore();
const questionGenerator = new QuestionnaireGenerator();

const instructions = ref(t("EditChapter.instructions"));

watch(locale, async (newText) => {
  instructions.value = t("EditChapter.instructions");
});

const model = defineModel<TopicItem>("model", {required: true});
const questionnaireResultItem = defineModel<QuestionnaireResultItem>("questionnaire", {required: true});

const activeDifficulty = ref(questionGenerator.default_difficulty);
const difficultyList = ref(questionGenerator.difficulties);
const activeQuestion = ref(0);
const doDirectEdit = ref(false);
const useLLMtoAdd = ref(true);
const useLLMReasoning = ref(true);
const llmGenerationOngoing = ref(false);
const currQuestionItem = ref(questionnaireResultItem.value.questionnaire[activeDifficulty.value][activeQuestion.value]);
const summaryRef = ref(model.value.summary);

// Reference to the question child component
const questionRef = ref(null);

// State to track if the form is valid in the parent component
const formIsValid = ref(true);

// Method to handle form validation event from child
const handleFormValidation = (isValid) => {
  formIsValid.value = isValid;
};

const setActiveQuestion = (idx) => {
  if (questionRef.value) {
    // Call the validateForm method exposed by the question child component
    const valid = questionRef.value.validateForm();
    if (valid === true) {
      activeQuestion.value = idx;
    }
  }
};

const setActiveDifficulty = (val) => {
  loggerService.log("EditChapter:setActiveDifficulty");
  if (questionRef.value) {
    // Call the validateForm method exposed by the question child component
    const valid = questionRef.value.validateForm();
    if (valid === true) {
      activeDifficulty.value = val;
    }
  }
};

watch(model, () => {
  summaryRef.value = model.value.summary;
  const last_index = questionnaireResultItem.value.questionnaire[activeDifficulty.value].length - 1;
  if (activeQuestion.value > last_index) {
    activeQuestion.value = last_index;
  }
  doDirectEdit.value = false;
  matomo_clicktracking("click_button", `Active chapter changed`);
});

watch(activeDifficulty, () => {
  const last_index = questionnaireResultItem.value.questionnaire[activeDifficulty.value].length - 1;
  if (activeQuestion.value > last_index) {
    activeQuestion.value = last_index;
  }
  currQuestionItem.value = questionnaireResultItem.value.questionnaire[activeDifficulty.value][activeQuestion.value];
  doDirectEdit.value = false;
  matomo_clicktracking("click_button", `Active difficulty changed: ${activeDifficulty.value}`);
});

watch(activeQuestion, () => {
  currQuestionItem.value = questionnaireResultItem.value.questionnaire[activeDifficulty.value][activeQuestion.value];
  doDirectEdit.value = false;
  matomo_clicktracking("click_button", `Active question index changed: ${activeQuestion.value}`);
});

watch(questionnaireResultItem, () => {
  const last_index = questionnaireResultItem.value.questionnaire[activeDifficulty.value].length - 1;
  if (activeQuestion.value > last_index) {
    activeQuestion.value = last_index;
  }
  currQuestionItem.value = questionnaireResultItem.value.questionnaire[activeDifficulty.value][activeQuestion.value];
  doDirectEdit.value = false;
  matomo_clicktracking("click_button", `Active questionnaire for chapter changed`);
});

const props = defineProps<{
  language: string;
  uuid: string;
}>();

function updateTitle(event: Event) {
  model.value.title = (event.target as HTMLInputElement).value;
  matomo_clicktracking("click_button", `Chapter title modified, uuid: ${props.uuid}`);
}

function updateSummary(event: Event) {
  model.value.summary = (event.target as HTMLInputElement).innerText;
  matomo_clicktracking("click_button", `Chapter summary modified, uuid: ${props.uuid}`);
}

async function addQuestion() {
  const add_index = questionnaireResultItem.value.questionnaire[activeDifficulty.value].length;

  if (useLLMtoAdd.value === true) {
    llmGenerationOngoing.value = true;
    const intervalContext = mediaStore.getCurrentTranscriptTextInInterval(props.language, model.value.interval);
    const avoid: string[] = [];
    for (let index = 0; index < difficultyList.value.length; index++) {
      const element = questionnaireResultItem.value.questionnaire[difficultyList.value[index]];
      element.forEach((questionItem) => {
        avoid.push(questionItem.mcq.question);
      });
    }
    const questionaire = await questionGenerator.generateMcq(
      activeDifficulty.value,
      avoid,
      props.language,
      intervalContext,
      props.uuid,
      useLLMReasoning.value,
    );
    loggerService.log(questionaire);
    try {
      const addItem = new QuestionItem();
      addItem.index = add_index;
      addItem.type = "mcq_one_correct";
      addItem.mcq = new MultipleChoiceQuestion();
      addItem.mcq.question = questionaire.question.trim();
      addItem.mcq.creator = "llm";
      addItem.mcq.editor = "";
      addItem.mcq.correct_answer_explanation = questionaire.correct_answer_explanation;
      addItem.mcq.correct_answer_index = questionaire.correct_answer_index;
      addItem.mcq.answers = questionaire.answers;
      questionnaireResultItem.value.questionnaire[activeDifficulty.value].push(addItem);
      doDirectEdit.value = true;
      activeQuestion.value = add_index;
    } catch (e) {
      loggerService.error("Questionnaire format error after json parsing!");
    }
    matomo_clicktracking("click_button", `Added new question generated by llm`);
    llmGenerationOngoing.value = false;
  } else {
    const addItem = new QuestionItem();
    addItem.index = add_index;
    addItem.type = "mcq_one_correct";
    addItem.mcq = new MultipleChoiceQuestion();
    addItem.mcq.question = t("EditChapter.newQuestionnaire");
    addItem.mcq.creator = "lecturer";
    addItem.mcq.editor = "lecturer";
    addItem.mcq.correct_answer_explanation = "";
    addItem.mcq.correct_answer_index = 0;
    addItem.mcq.answers = [
      {index: 0, answer: ""},
      {index: 1, answer: ""},
      {index: 2, answer: ""},
      {index: 3, answer: ""},
    ];
    questionnaireResultItem.value.questionnaire[activeDifficulty.value].push(addItem);
    doDirectEdit.value = true;
    activeQuestion.value = add_index;
    matomo_clicktracking("click_button", `Added new question generated by lecturer`);
  }
}

function deleteQuestion() {
  if (questionnaireResultItem.value.questionnaire[activeDifficulty.value].length > 1) {
    questionnaireResultItem.value.questionnaire[activeDifficulty.value].splice(activeQuestion.value, 1);
    activeQuestion.value -= 1;
    matomo_clicktracking("click_button", `Lecturer deleted a question`);
  }
}

function isFormValid() {
  return questionRef.value.validateForm();
}

defineExpose({isFormValid});
</script>

<style scoped>
h1 {
  color: var(--hans-dark-blue);
  font-size: 1.5rem;
}

.title {
  font-size: 2.5rem;
  font-weight: 500;
}

.questions-heading {
  margin-top: 1rem;
}

.instructions {
  margin-top: 1rem;
}

.difficulty-title {
  margin-top: 1rem;
}

.questions-title {
  margin-top: 1rem;
}

.summary {
  padding: 1rem 1.5rem;
  margin-top: 1rem;
}

main {
  padding: 2rem;
}

.questions-select {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.questions-select > button {
  background-color: transparent;
  padding: 0.25rem 0.75rem;
}

.questions-select > button:hover {
  text-decoration: underline;
}

.questions-select > button.active {
  background-color: var(--hans-light-gray);
}

button {
  border: none;
  border-radius: 0.25rem;
  background-color: transparent;
}

.question-container {
  display: flex;
  width: 100%;
}

.question-item {
  display: flex;
  width: 100%;
}

.llm-switches {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.llm-switch {
  padding-right: 1em;
}

textarea[readonly] {
  resize: none;
  border: none;
}
</style>
