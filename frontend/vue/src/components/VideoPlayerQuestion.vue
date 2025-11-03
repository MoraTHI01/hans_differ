<template>
  <div>
    <!-- Bootstrap Modal -->
    <div class="modal fade" tabindex="-1" role="dialog" ref="videoPlayQuestionModal" @click.self="closeModal">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fs-5">{{ t("VideoPlayerQuestion.title") }}</h5>
            <button type="button" class="btn-close modal-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <p>
              {{ t("VideoPlayerQuestion.textBeforeTime") }} {{ timer }} {{ t("VideoPlayerQuestion.textAfterTime") }}
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="handleCancel">
              {{ t("VideoPlayerQuestion.cancel") }}
            </button>
            <button type="button" class="btn btn-primary" @click="handleContinue">
              {{ t("VideoPlayerQuestion.continue") }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {inject, ref, onMounted, onBeforeUnmount, defineProps, defineEmits} from "vue";
import {useHistoryStore} from "@/stores/history";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import type {Emitter, EventType} from "mitt";
import {PlayEvent, PauseEvent, SetPositionEvent} from "@/common/events";

const eventBus: Emitter<Record<EventType, unknown>> = inject("eventBus")!;

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const historyStore = useHistoryStore();

interface Props {
  uuid: string;
}

const props = defineProps<Props>();
const videoPlayQuestionModal = ref(null);
const timer = ref(10); // Set timer duration in seconds
let interval: NodeJS.Timeout | null = null;
const currHistory = ref(null);

const emit = defineEmits(["play"]);

const handleContinue = () => {
  closeModal();
  // Logic to continue playback
  loggerService.log("VideoPlayerQuestion:ContinuePlayback");
  if (currHistory.value) {
    loggerService.log("VideoPlayerQuestion:ContinuePlayback:SetPositionEvent");
    eventBus.emit("setPositionEvent", new SetPositionEvent(currHistory.value.position, "history", 0));
  }
};

const handleCancel = () => {
  closeModal();
  // Logic to stop playback or take other action
  loggerService.log("VideoPlayerQuestion:Timeout");
};

const closeModal = () => {
  if (videoPlayQuestionModal.value) {
    videoPlayQuestionModal.value.classList.remove("show");
    videoPlayQuestionModal.value.style.display = "none";
  }
  loggerService.log("VideoPlayerQuestion:closeModal:emitPlay");
  eventBus.emit("play", new PlayEvent("history"));
  emit("play");
  clearInterval(interval!); // Clear the timer when the modal is closed
};

const startTimer = () => {
  interval = setInterval(() => {
    if (timer.value > 0) {
      timer.value--;
    } else {
      handleContinue(); // Automatically continue when timer reaches 0
    }
  }, 1000);
};

onMounted(() => {
  loggerService.log("VideoPlayerQuestion:onMounted");
  currHistory.value = historyStore.getHistoryForMediaItem(props.uuid);
  if (currHistory.value != undefined && currHistory.value != null) {
    loggerService.log("VideoPlayerQuestion:showModal");
    videoPlayQuestionModal.value.classList.add("show");
    videoPlayQuestionModal.value.style.display = "block";
    startTimer(); // Start the timer when the modal is shown
  } else {
    closeModal();
  }
});

onBeforeUnmount(() => {
  clearInterval(interval!); // Clear the timer on component unmount
});
</script>

<style scoped>
.modal {
  display: block;
  /* Show modal */
  background: rgba(0, 0, 0, 0.5);
  /* Background overlay */
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
</style>
