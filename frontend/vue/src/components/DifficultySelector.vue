<template>
  <div class="difficulty-select">
    <button
      v-for="difficulty in difficultyList"
      :key="difficulty"
      @click="setActiveDifficulty(difficulty)"
      :class="{active: activeDifficulty == difficulty}"
    >
      {{ t(`DifficultySelector.${difficulty}`) }}
    </button>
  </div>
</template>

<script setup lang="ts">
import {defineEmits, defineExpose, defineModel, ref, watch, onMounted} from "vue";
import {useQuestionStore} from "@/stores/questions";
import {QuestionnaireGenerator} from "@/common/genQuestionnaires";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import type EditQuestion from "@/components/EditQuestion.vue";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const qStore = useQuestionStore();
const emit = defineEmits(["difficultyChanged"]);

const validatorRef = defineModel<EditQuestion>("validatorFormComp", {required: false});

const questionGenerator = new QuestionnaireGenerator();
const difficultyList = ref(questionGenerator.difficulties);
const activeDifficulty = ref(questionGenerator.default_difficulty);
qStore.setDifficulty(activeDifficulty.value);

const setActiveDifficulty = (val) => {
  if (validatorRef.value) {
    loggerService.log("Set active difficulty with validation");
    // Call the validateForm method exposed by the question child component
    const valid = validatorRef.value.validateForm();
    if (valid === true) {
      loggerService.log("Validation successful set difficulty");
      activeDifficulty.value = val;
      qStore.setDifficulty(val);
    }
  } else {
    loggerService.log("Set active difficulty without validation");
    activeDifficulty.value = val;
    qStore.setDifficulty(val);
  }
  emit("difficultyChanged", activeDifficulty.value);
};
</script>

<style scoped>
button {
  border: none;
  border-radius: 0.25rem;
  background-color: transparent;
}

.difficulty-select {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.difficulty-select > button {
  background-color: transparent;
  padding: 0.25rem 0.75rem;
}

.difficulty-select > button:hover {
  text-decoration: underline;
}

.difficulty-select > button.active {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
}
</style>
