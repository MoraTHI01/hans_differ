<template>
  <div class="card-body p-1">
    <div v-if="viewportWidth > 786">
      <div class="col-12 difficulty-container d-flex justify-content-between align-items-center">
        <div class="difficulty-title">
          <h5>{{ t("DynamicQuestionnaire.difficultyTitle") }}</h5>
        </div>
        <DifficultySelector @difficultyChanged="setActiveDifficulty($event)" />
      </div>
      <div class="col-12 accordion accordion-flush" id="accordionQuestionniare">
        <div class="accordion-item">
          <h2 class="accordion-header" id="headingOne">
            <button
              class="accordion-button"
              type="button"
              @click="setQuestInactive()"
              data-bs-toggle="collapse"
              data-bs-target="#collapseOne"
              aria-expanded="true"
              aria-controls="collapseOne"
            >
              {{ questionnaireText }}
            </button>
          </h2>
          <div
            id="collapseOne"
            class="accordion-collapse collapse show"
            aria-labelledby="headingOne"
            data-bs-parent="#accordionQuestionniare"
          >
            <div class="accordion-body static-questionnaire">
              <QuestionnaireStatic
                class="accordion-body"
                ref="staticQuestionnaire"
                :video="props.video"
              ></QuestionnaireStatic>
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header" id="flush-headingTwo">
            <button
              class="accordion-button collapsed"
              type="button"
              @click="setQuestActive()"
              data-bs-toggle="collapse"
              data-bs-target="#flush-collapseTwo"
              aria-expanded="false"
              aria-controls="flush-collapseTwo"
            >
              {{ t("DynamicQuestionnaire.dynamicQuestionnaires") }}
            </button>
          </h2>
          <div
            id="flush-collapseTwo"
            class="accordion-collapse collapse"
            aria-labelledby="flush-headingTwo"
            data-bs-parent="#accordionQuestionniare"
          >
            <QuestionnaireWithInterval
              class="accordion-body"
              ref="intervalQuestionnaire"
              :video="props.video"
            ></QuestionnaireWithInterval>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="container questionnaire-container-modal d-flex justify-content-center align-items-center">
      <button
        :class="['btn', 'btn-primary', 'btn-sm', 'btn-open-questionnaire']"
        :title="t('DynamicQuestionnaire.openQuestionnaireButton')"
        @click="openModal"
      >
        <img src="/bootstrap-icons/question-circle.svg" alt="open-questionnaire" class="img-fluid img-btn" />
        {{ t("DynamicQuestionnaire.openQuestionnaireButton") }}
      </button>
      <div class="modal fade" tabindex="-2" role="dialog" ref="questionnaireModal">
        <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5">{{ t("DynamicQuestionnaire.title") }}</h1>
              <button
                type="button"
                class="btn-close modal-close"
                @click="closeModal"
                :aria-label="t('DynamicQuestionnaire.closeButton')"
              ></button>
            </div>
            <div class="modal-body card-body p-1 questionnaire-container container">
              <div class="col-12 difficulty-container d-flex justify-content-between align-items-center">
                <div class="difficulty-title">
                  <h5>{{ t("DynamicQuestionnaire.difficultyTitle") }}</h5>
                </div>
                <DifficultySelector @difficultyChanged="setActiveDifficulty($event)" />
              </div>
              <div class="col-12 accordion accordion-flush" id="accordionQuestionniare">
                <div class="accordion-item">
                  <h2 class="accordion-header" id="headingOne">
                    <button
                      class="accordion-button"
                      type="button"
                      @click="setQuestInactive()"
                      data-bs-toggle="collapse"
                      data-bs-target="#collapseOne"
                      aria-expanded="true"
                      aria-controls="collapseOne"
                    >
                      {{ questionnaireText }}
                    </button>
                  </h2>
                  <div
                    id="collapseOne"
                    class="accordion-collapse collapse show"
                    aria-labelledby="headingOne"
                    data-bs-parent="#accordionQuestionniare"
                  >
                    <div class="accordion-body static-questionnaire">
                      <QuestionnaireStatic
                        class="accordion-body"
                        ref="staticQuestionnaire"
                        :video="props.video"
                      ></QuestionnaireStatic>
                    </div>
                  </div>
                </div>
                <div class="accordion-item">
                  <h2 class="accordion-header" id="flush-headingTwo">
                    <button
                      class="accordion-button collapsed"
                      type="button"
                      @click="setQuestActive()"
                      data-bs-toggle="collapse"
                      data-bs-target="#flush-collapseTwo"
                      aria-expanded="false"
                      aria-controls="flush-collapseTwo"
                    >
                      {{ t("DynamicQuestionnaire.dynamicQuestionnaires") }}
                    </button>
                  </h2>
                  <div
                    id="flush-collapseTwo"
                    class="accordion-collapse collapse"
                    aria-labelledby="flush-headingTwo"
                    data-bs-parent="#accordionQuestionniare"
                  >
                    <QuestionnaireWithInterval
                      class="accordion-body"
                      ref="intervalQuestionnaire"
                      :video="props.video"
                    ></QuestionnaireWithInterval>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-primary" @click="closeModal">
                {{ t("DynamicQuestionnaire.closeButton") }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, nextTick, watch} from "vue";
import type {MediaItem} from "@/data/MediaItem.js";
import {useQuestionStore} from "@/stores/questions";
import DifficultySelector from "@/components/DifficultySelector.vue";
import QuestionnaireWithInterval from "@/components/QuestionnaireWithInterval.vue";
import QuestionnaireStatic from "@/components/QuestionnaireStatic.vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {useMediaStore} from "@/stores/media";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const store = useMediaStore();
const viewportWidth = ref(window.innerWidth);

const props = defineProps<{
  video: MediaItem;
  active: boolean;
}>();

const questionnaireModal = ref(null);
const questionnaireText = ref("");

const openModal = () => {
  if (questionnaireModal.value) {
    loggerService.log("DynamicQuestionnaire:WindowOpen");
    questionnaireModal.value.classList.add("show");
    questionnaireModal.value.style.display = "block";
  }
};

const closeModal = () => {
  if (questionnaireModal.value) {
    loggerService.log("DynamicQuestionnaire:WindowClose");
    questionnaireModal.value.classList.remove("show");
    questionnaireModal.value.style.display = "none";
  }
};

const intervalQuestionnaire = ref(null);
const staticQuestionnaire = ref(null);

const setQuestInactive = () => {
  intervalQuestionnaire.value.setActive(false);
  staticQuestionnaire.value.setActive(true);
};

const setQuestActive = () => {
  staticQuestionnaire.value.setActive(false);
  intervalQuestionnaire.value.setActive(true);
};

const setActiveDifficulty = (val: string) => {
  loggerService.log("DynamicQuestionnaire:updateChildComponents");
  intervalQuestionnaire.value.reload();
  staticQuestionnaire.value.reload();
};

onMounted(async () => {
  questionnaireText.value = t("DynamicQuestionnaire.lecturerQuestionnaires");
  if (props.video.questionnaire_curated === false) {
    questionnaireText.value = t("DynamicQuestionnaire.generatedQuestionnaires");
  }
  await store.loadQuestionnaire(props.video?.uuid);
  intervalQuestionnaire.value.setActive(false);
  staticQuestionnaire.value.setActive(true);
});

watch(locale, async (newText) => {
  questionnaireText.value = t("DynamicQuestionnaire.lecturerQuestionnaires");
  if (props.video.questionnaire_curated === false) {
    questionnaireText.value = t("DynamicQuestionnaire.generatedQuestionnaires");
  }
});
</script>
<style scoped>
.difficulty-title {
  margin-top: 1.5rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.difficulty-container {
  display: flex;
  align-items: baseline;
}

.accordion {
  margin-top: 1rem;
}

.static-questionnaire {
  height: 40vh;
}

.img-btn {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  height: 24px;
  width: 32px;
}

.questionnaire-container-modal {
  overflow-y: auto;
  word-break: break-word;
  cursor: default;
  height: max-content;
  min-height: 8vh;
}

.btn-open-questionnaire {
  top: 1em;
  position: relative;
  display: flex;
}

.modal-header {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
}

.modal-title {
  color: var(--hans-light);
}

.modal-close {
  color: var(--hans-light);
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}

.modal-dialog-scrollable .modal-content {
  max-height: 100%;
  overflow: hidden;
  min-height: 76vh;
  top: -1%;
}
</style>
