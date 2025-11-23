<template>
  <div class="container">
    <div class="row">
      <ChatServiceInfo ref="chatServiceInfo"></ChatServiceInfo>
      <div v-if="!chatStore.isSettingsOpen" class="col-12 d-flex justify-content-center align-items-center">
        <div
          v-if="messageStore.videoSnapshot !== '' && chatStore.isSwitchVisionSnapshotEnabled"
          class="snapshot-container"
        >
          <img :src="messageStore.videoSnapshot" alt="Screenshot" class="img-snapshot" />
          <button
            @click="clearSnapshot()"
            class="btn btn-primary form-control btn-del-snapshot"
            data-bs-toggle="tooltip"
            data-bs-placement="bottom"
            :title="t('ChatInput.tooltipDeleteSnapshotButton')"
            :disabled="allButtonsDisabled"
          >
            <img src="/bootstrap-icons/x-circle.svg" alt="api-btn" class="img-fluid img-btn" />
          </button>
        </div>
        <div class="message-container-wrapper">
          <textarea
            v-model="message"
            rows="3"
            @keyup.enter="sendMessagePressEnter"
            @keyup="onKeyup"
            :placeholder="currTextAreaPlaceholder"
            class="form-control message-container"
            :readonly="messageStore.isRequestOngoing || allButtonsDisabled"
            :disabled="messageStore.isRequestOngoing || allButtonsDisabled"
          >
          </textarea>

          <!-- Buttons below the text area -->
          <div class="buttons-container">
            <button
              v-if="props.channelmode === true"
              :class="
                currToggleShortcutOptionSearch === true
                  ? 'btn btn-primary form-control option-button option-button-active'
                  : 'btn btn-primary form-control option-button'
              "
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              @click="toggleShortcutOptionSearch()"
              :title="t('ChatInput.tooltipShortcutOptionSearch')"
              :disabled="messageStore.isRequestOngoing || allButtonsDisabled"
            >
              <img
                src="/bootstrap-icons/search.svg"
                alt="api-btn"
                :class="
                  currToggleShortcutOptionSearch === true
                    ? 'img-fluid img-option-btn-active'
                    : 'img-fluid img-option-btn'
                "
              />
              <span class="button-text">{{ t("ChatInput.shortcutOptionSearch") }}</span>
            </button>
            <button
              v-if="props.channelmode === false"
              :class="
                currToggleShortcutOptionSlides === true
                  ? 'btn btn-primary form-control option-button option-button-active'
                  : 'btn btn-primary form-control option-button'
              "
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              @click="toggleShortcutOptionSlides()"
              :title="t('ChatInput.tooltipShortcutOptionSlides')"
              :disabled="messageStore.isRequestOngoing || allButtonsDisabled"
            >
              <img
                src="/bootstrap-icons/file-earmark-slides.svg"
                alt="api-btn"
                :class="
                  currToggleShortcutOptionSlides === true
                    ? 'img-fluid img-option-btn-active'
                    : 'img-fluid img-option-btn'
                "
              />
              <span class="button-text">{{ t("ChatInput.shortcutOptionSlides") }}</span>
            </button>
            <button
              v-if="props.channelmode === false"
              :class="
                currToggleShortcutOptionSnapshot === true
                  ? 'btn btn-primary form-control option-button option-button-active'
                  : 'btn btn-primary form-control option-button'
              "
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              @click="toggleShortcutOptionSnapshot()"
              :title="t('ChatInput.tooltipShortcutOptionSnapshot')"
              :disabled="messageStore.isRequestOngoing || allButtonsDisabled"
            >
              <img
                src="/bootstrap-icons/camera.svg"
                alt="api-btn"
                :class="
                  currToggleShortcutOptionSnapshot === true
                    ? 'img-fluid img-option-btn-active'
                    : 'img-fluid img-option-btn'
                "
              />
              <span class="button-text">{{ t("ChatInput.shortcutOptionSnapshot") }}</span>
            </button>
            <button
              :class="
                currToggleShortcutOptionReasoning === true
                  ? 'btn btn-primary form-control option-button option-button-active'
                  : 'btn btn-primary form-control option-button'
              "
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              @click="toggleShortcutOptionReasoning()"
              :title="t('ChatInput.tooltipShortcutOptionReasoning')"
              :disabled="messageStore.isRequestOngoing || allButtonsDisabled"
            >
              <img
                src="/bootstrap-icons/lightbulb.svg"
                alt="api-btn"
                :class="
                  currToggleShortcutOptionReasoning === true
                    ? 'img-fluid img-option-btn-active'
                    : 'img-fluid img-option-btn'
                "
              />
              <span class="button-text">{{ t("ChatInput.shortcutOptionReasoning") }}</span>
            </button>
            <button
              :class="
                currToggleShortcutOptionTutor === true
                  ? 'btn btn-primary form-control option-button option-button-active'
                  : 'btn btn-primary form-control option-button'
              "
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              @click="toggleShortcutOptionTutor()"
              :title="t('ChatInput.tooltipShortcutOptionTutor')"
              :disabled="messageStore.isRequestOngoing || allButtonsDisabled"
            >
              <img
                src="/bootstrap-icons/mortarboard-fill.svg"
                alt="api-btn"
                :class="
                  currToggleShortcutOptionTutor === true
                    ? 'img-fluid img-option-btn-active'
                    : 'img-fluid img-option-btn'
                "
              />
              <span class="button-text">{{ t("ChatInput.shortcutOptionTutor") }}</span>
            </button>
            <button
              type="button"
              class="btn btn-primary form-control dropdown-toggle help-button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
              :disabled="allButtonsDisabled"
            >
              <img src="/bootstrap-icons/question-circle-fill.svg" alt="api-btn" class="img-fluid img-btn" />
              <span class="button-text">{{ t("ChatInput.help") }}</span>
            </button>
            <ul v-if="props.channelmode" class="dropdown-menu help-dropdown-menu btn-container">
              <li class="template-item">
                <a class="dropdown-item" href="#" @click="handleTemplateSelection(t('ChatInput.promptExampleSearch'))"
                  ><img src="/bootstrap-icons/search.svg" alt="api-btn" class="img-fluid dropdown-img" />{{
                    t("ChatInput.promptExampleSearchBtn")
                  }}</a
                >
              </li>
            </ul>
            <ul v-else class="dropdown-menu help-dropdown-menu btn-container">
              <li class="template-item">
                <a class="dropdown-item" href="#" @click="handleTemplateSelection(t('ChatInput.promptExampleExercise'))"
                  ><img src="/bootstrap-icons/card-text.svg" alt="api-btn" class="img-fluid dropdown-img" />{{
                    t("ChatInput.promptExampleExerciseBtn")
                  }}</a
                >
              </li>
              <li class="template-item">
                <a
                  class="dropdown-item"
                  href="#"
                  @click="handleTemplateSelection(t('ChatInput.promptExampleExplainTerm'))"
                  ><img src="/bootstrap-icons/card-text.svg" alt="api-btn" class="img-fluid dropdown-img" />{{
                    t("ChatInput.promptExampleExplainTermBtn")
                  }}</a
                >
              </li>
              <li class="template-item">
                <a
                  class="dropdown-item"
                  href="#"
                  @click="handleTemplateSelection(t('ChatInput.promptExampleSolveEquation'))"
                  ><img src="/bootstrap-icons/card-text.svg" alt="api-btn" class="img-fluid dropdown-img" />{{
                    t("ChatInput.promptExampleSolveEquationBtn")
                  }}</a
                >
              </li>
              <li class="template-item">
                <a
                  class="dropdown-item"
                  href="#"
                  @click="handleTemplateSelection(t('ChatInput.promptExampleCalcFunction'))"
                  ><img src="/bootstrap-icons/card-text.svg" alt="api-btn" class="img-fluid dropdown-img" />{{
                    t("ChatInput.promptExampleCalcFunctionBtn")
                  }}</a
                >
              </li>
              <li class="template-item">
                <a
                  class="dropdown-item"
                  href="#"
                  @click="handleTemplateSelection(t('ChatInput.promptExampleQuestionaire'))"
                  ><img src="/bootstrap-icons/card-text.svg" alt="api-btn" class="img-fluid dropdown-img" />{{
                    t("ChatInput.promptExampleQuestionaireBtn")
                  }}</a
                >
              </li>
            </ul>
          </div>
        </div>
      </div>
      <!-- Menu Bar -->
      <div class="col-12 d-flex justify-content-center align-items-center">
        <div class="col-8 d-flex justify-content-center align-items-center control-box">
          <div class="input-group dropup">
            <button
              v-if="messageStore.isRequestOngoing || allButtonsDisabled"
              class="btn btn-primary form-control btn-container"
              type="button"
              disabled
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              :title="sendButtonTooltipTitle"
            >
              <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
              <span class="visually-hidden" role="status">{{ t("ChatInput.loading") }}</span>
            </button>
            <button
              v-else-if="!chatStore.isSettingsOpen"
              @click="sendMessageClickButton"
              class="btn btn-primary form-control btn-container"
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              :title="sendButtonTooltipTitle"
            >
              <img :src="sendButtonImage" alt="api-btn" class="img-fluid img-btn" />
            </button>
            <button
              v-if="!messageStore.isMessagesEmpty(props.uuid)"
              @click="regenerateMessageClickButton"
              class="btn btn-primary form-control btn-container"
              data-bs-toggle="tooltip"
              data-bs-placement="bottom"
              :title="t('ChatInput.tooltipRegenerateButton')"
              :disabled="allButtonsDisabled"
            >
              <img src="/bootstrap-icons/arrow-repeat.svg" alt="api-btn" class="img-fluid img-btn" />
            </button>
            <ChatSettingsWindow
              :disableComp="messageStore.isRequestOngoing || allButtonsDisabled"
              :channelmode="props.channelmode"
              @chatSettingsWindowClosed="handleChatSettingsWindowClosed($event)"
            />
            <button
              id="btnGroupDrop2"
              type="button"
              class="btn btn-primary form-control option-toggle"
              data-bs-toggle="dropdown"
              aria-expanded="false"
              :disabled="allButtonsDisabled"
            ></button>
            <ul class="dropdown-menu btn-container" aria-labelledby="btnGroupDrop2">
              <li>
                <a class="dropdown-item" href="#" @click="clearMessagesClickButton"
                  ><img src="/bootstrap-icons/trash.svg" alt="api-btn" class="img-fluid dropdown-img" />{{
                    t("ChatInput.dropdownOptionsClearChatHistory")
                  }}</a
                >
              </li>
              <li>
                <a class="dropdown-item" href="#" @click="chatServiceInfo.chatServiceInfoOpenModal()"
                  ><img src="/bootstrap-icons/info-circle-fill.svg" alt="api-btn" class="img-fluid dropdown-img" />{{
                    t("ChatInput.dropdownOptionsInfo")
                  }}</a
                >
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed, inject, nextTick, onMounted, ref, watch} from "vue";
import {useI18n} from "vue-i18n";
import type {Emitter, EventType} from "mitt";
import {SetPageEvent} from "@/common/events";
import {useMediaStore} from "@/stores/media";
import ChatServiceInfo from "@/components/ChatServiceInfo.vue";
import ChatSettingsWindow from "./ChatSettingsWindow.vue";
import type {MediaItem} from "@/data/MediaItem";
import type {ChannelItem} from "@/data/ChannelItem";
import type {Message, MessageContent, TextContent} from "@/data/Message";
import {useMessageStore} from "@/stores/message";
import {useChatStore} from "@/stores/chat";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();

const {t, locale} = useI18n({useScope: "global"});

const mediaStore = useMediaStore();
const messageStore = useMessageStore();
const chatStore = useChatStore();
const eventBus: Emitter<Record<EventType, unknown>> = inject("eventBus")!;

const props = defineProps<{
  uuid: string;
  language: string;
  channelmode: boolean;
}>();

const chatServiceInfo = ref(null);

const message = ref("");
const curr_page = ref<number>(1);

const isSettingsButtonDisabled = ref(false);
const isOptionButtonDisabled = ref(false);
const isTextareaDisabled = ref(false);
const isRegenerateButtonDisabled = ref(false);
const isTemplateButtonDisabled = ref(false);

const sendButtonImage = ref("/bootstrap-icons/send-check-fill.svg");
const sendButtonTooltipTitle = ref(t("ChatInput.tooltipSendButtonContextAndCite"));

chatStore.toggleSwitchContext(true);
chatStore.toggleSwitchCitation(true);
chatStore.toggleSwitchTutor(false);

const allButtonsDisabled = computed(() => {
  return (
    isSettingsButtonDisabled.value ||
    isOptionButtonDisabled.value ||
    isTextareaDisabled.value ||
    isRegenerateButtonDisabled.value ||
    isTemplateButtonDisabled.value ||
    !messageStore.getServicesAvailable ||
    !messageStore.getServicesAlive
  );
});

const currToggleShortcutOptionSearch = ref(
  false || (chatStore.isSwitchChannelContextEnabled && chatStore.isSwitchChannelCitationEnabled),
);
const toggleShortcutOptionSearch = () => {
  const wasSlidesModeActive = currToggleShortcutOptionSlides.value;
  currToggleShortcutOptionSearch.value = !currToggleShortcutOptionSearch.value;
  if (currToggleShortcutOptionSearch.value === true) {
    chatStore.toggleSwitchVision(false);
    chatStore.toggleSwitchVisionSnapshot(false);
    chatStore.toggleSwitchSelectedContext(false);
    chatStore.toggleSwitchContext(true);
    chatStore.toggleSwitchCitation(true);
    chatStore.toggleSwitchChannelContext(true);
    chatStore.toggleSwitchChannelCitation(true);
    currToggleShortcutOptionSlides.value = false;
    currToggleShortcutOptionSnapshot.value = false;
  } else {
    chatStore.toggleSwitchContext(true);
    chatStore.toggleSwitchCitation(true);
    chatStore.toggleSwitchChannelContext(false);
    chatStore.toggleSwitchChannelCitation(false);
  }
  if (wasSlidesModeActive === true) {
    mediaStore.setSwitchSlidesAndVideo(false);
    chatStore.storeChatSettings();
    //router.push(router.currentRoute.value);
    nextTick(() => {
      window.location.reload();
    });
  } else {
    chatStore.storeChatSettings();
  }
  updateUI();
};

const currToggleShortcutOptionSnapshot = ref(false || chatStore.isSwitchVisionSnapshotEnabled);
const toggleShortcutOptionSnapshot = () => {
  const wasSlidesModeActive = currToggleShortcutOptionSlides.value;
  currToggleShortcutOptionSnapshot.value = !currToggleShortcutOptionSnapshot.value;
  if (currToggleShortcutOptionSnapshot.value === true) {
    chatStore.toggleSwitchReasoning(false);
    chatStore.toggleSwitchVisionSnapshot(true);
    chatStore.toggleSwitchSelectedContext(false);
    chatStore.toggleSwitchContext(true);
    chatStore.toggleSwitchCitation(true);
    currToggleShortcutOptionSlides.value = false;
    currToggleShortcutOptionReasoning.value = false;
    currToggleShortcutOptionSearch.value = false;
  } else {
    chatStore.toggleSwitchVisionSnapshot(false);
  }
  if (wasSlidesModeActive === true) {
    mediaStore.setSwitchSlidesAndVideo(false);
    chatStore.storeChatSettings();
    //router.push(router.currentRoute.value);
    nextTick(() => {
      window.location.reload();
    });
  } else {
    chatStore.storeChatSettings();
  }
  updateUI();
};

const currToggleShortcutOptionReasoning = ref(false || chatStore.isSwitchReasoningEnabled);
const toggleShortcutOptionReasoning = () => {
  const wasSlidesModeActive = currToggleShortcutOptionSlides.value;
  currToggleShortcutOptionReasoning.value = !currToggleShortcutOptionReasoning.value;
  if (currToggleShortcutOptionReasoning.value === true) {
    chatStore.toggleSwitchReasoning(true);
    chatStore.toggleSwitchVisionSnapshot(false);
    chatStore.toggleSwitchVisionSnapshot(false);
    chatStore.toggleSwitchSelectedContext(false);
    chatStore.toggleSwitchContext(true);
    chatStore.toggleSwitchCitation(true);
    currToggleShortcutOptionSnapshot.value = false;
    currToggleShortcutOptionSlides.value = false;
    currToggleShortcutOptionSearch.value = false;
  } else {
    chatStore.toggleSwitchReasoning(false);
  }
  if (wasSlidesModeActive === true) {
    mediaStore.setSwitchSlidesAndVideo(false);
    chatStore.storeChatSettings();
    //router.push(router.currentRoute.value);
    nextTick(() => {
      window.location.reload();
    });
  } else {
    chatStore.storeChatSettings();
  }
  updateUI();
};

const currToggleShortcutOptionTutor = ref(false || chatStore.isSwitchTutorEnabled);
const toggleShortcutOptionTutor = () => {
  currToggleShortcutOptionTutor.value = !currToggleShortcutOptionTutor.value;
  if (currToggleShortcutOptionTutor.value === true) {
    chatStore.toggleSwitchTutor(true);
  } else {
    chatStore.toggleSwitchTutor(false);
  }
  chatStore.storeChatSettings();
  updateUI();
};

const currToggleShortcutOptionSlides = ref(false || chatStore.isSwitchVisionEnabled);
const toggleShortcutOptionSlides = () => {
  currToggleShortcutOptionSlides.value = !currToggleShortcutOptionSlides.value;
  mediaStore.setSwitchSlidesAndVideo(currToggleShortcutOptionSlides.value);
  if (currToggleShortcutOptionSlides.value === true) {
    chatStore.toggleSwitchVision(true);
    chatStore.toggleSwitchContext(true);
    chatStore.toggleSwitchCitation(true);
    currToggleShortcutOptionSnapshot.value = false;
    currToggleShortcutOptionReasoning.value = false;
    currToggleShortcutOptionSearch.value = false;
  } else {
    chatStore.toggleSwitchVision(false);
    chatStore.toggleSwitchContext(true);
    chatStore.toggleSwitchCitation(true);
  }
  chatStore.storeChatSettings();
  updateUI();
  //router.push(router.currentRoute.value);
  nextTick(() => {
    window.location.reload();
  });
};

const currTextAreaPlaceholder = ref(t("ChatInput.dropdownPromptOptionWithContext"));

const updateUI = () => {
  if (!messageStore.getServicesAvailable || !messageStore.getServicesAlive) {
    currTextAreaPlaceholder.value = t("ChatInput.loading");
  } else if (chatStore.isSwitchSelectedContextEnabled === true && chatStore.isSwitchContextEnabled === false) {
    currTextAreaPlaceholder.value = t("ChatInput.dropdownPromptOptionWithSelectedTranscriptContext") + ".";
    sendButtonImage.value = "/bootstrap-icons/send-arrow-down-fill.svg";
    sendButtonTooltipTitle.value = t("ChatInput.dropdownPromptOptionWithSelectedTranscriptContext");
  } else if (chatStore.isSwitchCitationEnabled === true && chatStore.isSwitchContextEnabled === true) {
    currTextAreaPlaceholder.value = t("ChatInput.dropdownPromptOptionWithContextAndCite") + ".";
    sendButtonImage.value = "/bootstrap-icons/send-check-fill.svg";
    sendButtonTooltipTitle.value = t("ChatInput.tooltipSendButtonContextAndCite");
  } else if (chatStore.isSwitchContextEnabled === true) {
    currTextAreaPlaceholder.value = t("ChatInput.dropdownPromptOptionWithContext") + ".";
    sendButtonImage.value = "/bootstrap-icons/send-plus-fill.svg";
    sendButtonTooltipTitle.value = t("ChatInput.tooltipSendButtonContext");
  } else {
    currTextAreaPlaceholder.value = t("ChatInput.placeholder") + ".";
    sendButtonImage.value = "/bootstrap-icons/send-fill.svg";
    sendButtonTooltipTitle.value = t("ChatInput.tooltipSendButton");
  }

  if (chatStore.isSwitchVisionSnapshotEnabled === true) {
    currTextAreaPlaceholder.value = t("ChatInput.dropdownPromptOptionWithSnapshotContext") + ".";
    sendButtonImage.value = "/bootstrap-icons/send-check-fill.svg";
    sendButtonTooltipTitle.value = t("ChatInput.tooltipSendButtonSnapshotContext");
  } else if (chatStore.isSwitchVisionEnabled === true) {
    currTextAreaPlaceholder.value += t("ChatInput.currentSlide") + curr_page.value + "].";
  }

  if (
    props.channelmode === true &&
    chatStore.isSwitchChannelCitationEnabled === true &&
    chatStore.isSwitchChannelContextEnabled === true
  ) {
    currTextAreaPlaceholder.value = t("ChatInput.dropdownPromptOptionWithChannelContextAndCite") + ".";
    sendButtonImage.value = "/bootstrap-icons/send-check-fill.svg";
    sendButtonTooltipTitle.value = t("ChatInput.tooltipSendButtonChannelContextAndCite");
  } else if (props.channelmode === true && chatStore.isSwitchChannelContextEnabled === true) {
    currTextAreaPlaceholder.value = t("ChatInput.dropdownPromptOptionWithChannelContext") + ".";
    sendButtonImage.value = "/bootstrap-icons/send-plus-fill.svg";
    sendButtonTooltipTitle.value = t("ChatInput.tooltipSendButtonChannelContext");
  }

  if (props.channelmode === false && chatStore.isSwitchReasoningEnabled === true) {
    currTextAreaPlaceholder.value =
      currTextAreaPlaceholder.value + " " + t("ChatInput.shortcutOptionReasoning") + " " + t("ChatInput.active") + ".";
    sendButtonTooltipTitle.value =
      currTextAreaPlaceholder.value + " " + t("ChatInput.shortcutOptionReasoning") + " " + t("ChatInput.active") + ".";
  }
  if (props.channelmode === false && chatStore.isSwitchTutorEnabled === true) {
    currTextAreaPlaceholder.value =
      currTextAreaPlaceholder.value + " " + t("ChatInput.shortcutOptionTutor") + " " + t("ChatInput.active") + ".";
    sendButtonTooltipTitle.value =
      currTextAreaPlaceholder.value + " " + t("ChatInput.shortcutOptionTutor") + " " + t("ChatInput.active") + ".";
  }
  // Update Option Shortcuts
  currToggleShortcutOptionSearch.value =
    chatStore.isSwitchChannelContextEnabled === true && chatStore.isSwitchChannelCitationEnabled === true;
  currToggleShortcutOptionSnapshot.value = chatStore.isSwitchVisionSnapshotEnabled;
  currToggleShortcutOptionSlides.value = chatStore.isSwitchVisionEnabled;
  currToggleShortcutOptionReasoning.value = chatStore.isSwitchReasoningEnabled;
  currToggleShortcutOptionTutor.value = chatStore.isSwitchTutorEnabled;
  updateTranslateDisabled();
};

const updateTranslateDisabled = (toggle: boolean = false) => {
  if (locale.value === "de") {
    if (toggle) {
      chatStore.toggleTranslationEnabled(!chatStore.isTranslationEnabled);
    } else {
      chatStore.toggleTranslationEnabled(true);
    }
  } else if (locale.value === "en") {
    chatStore.toggleTranslationEnabled(false);
  }
};

const handlePage = async (page: number) => {
  loggerService.log("ChatInput:handlePage");
  curr_page.value = page;
  updateUI();
};

const onKeyup = (event: KeyboardEvent) => {
  const textarea = event.target as HTMLTextAreaElement; // Cast event target as HTMLTextAreaElement
  const key = event.key;

  if (key === "[" && chatStore.isSwitchVisionEnabled === true) {
    // Trigger the autocomplete logic when `[` is typed
    const comp_text = t("ChatInput.slide") + " " + curr_page.value.toString() + "]";
    insertTextAtCursor(textarea, comp_text);
  }
};

// Function to insert text at the cursor position
const insertTextAtCursor = (textarea: HTMLTextAreaElement, text: string) => {
  const caretPosition = textarea.selectionStart;
  const currentValue = message.value;

  // Check if the last typed character is `[` to avoid overwriting anything else
  if (currentValue[caretPosition - 1] === "[") {
    // Insert "Page 1]" after the `[` character
    const newMessage = currentValue.slice(0, caretPosition) + text + currentValue.slice(caretPosition);

    // Update the message value
    message.value = newMessage;

    // Move the caret to the end of the inserted text after the next DOM update
    nextTick(() => {
      textarea.selectionStart = caretPosition + text.length;
      textarea.selectionEnd = caretPosition + text.length;
    });
  }
};

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {
  updateUI();
});

watch(messageStore.servicesAvailable, () => {
  updateUI();
});

watch(messageStore.servicesAlive, () => {
  updateUI();
});

watch(chatStore.isSettingsOpen, async (newText) => {
  updateUI();
});

watch(messageStore.messages, () => {
  const lastBotMessage = messageStore.getLastMessage(props.uuid);
  if (
    lastBotMessage !== undefined &&
    lastBotMessage !== null &&
    lastBotMessage.stream === false &&
    lastBotMessage.isUser === false
  ) {
    loggerService.log("ChatInput:LlmMessageStream:Finished");
    for (let index = 0; index < lastBotMessage.content.length; index++) {
      const element = lastBotMessage.content[index];
      matomo_clicktracking("llm_response_" + element.language, element.content[0].text);
    }
    messageStore.storeMessages();
    messageStore.setAllRequestsFinished();
    message.value = "";
    switchControlsActive();
  }
});

onMounted(() => {
  loggerService.log("ChatInput:onMounted");
  updateUI();
  eventBus.on("setPageEvent", (event: SetPageEvent) => {
    if (event !== undefined && event.page !== undefined) {
      handlePage(event.page);
    }
  });
});

const handleChatSettingsWindowClosed = (val) => {
  loggerService.log("ChatInput:ChatSettingsWindowClosed");
  updateUI();
};

const clearSnapshot = () => {
  loggerService.log("ChatInput:clearSnapshot:Start");
  matomo_clicktracking("click_button", "Clear video snapshot");
  messageStore.setVideoSnapshot("");
  loggerService.log("ChatInput:clearSnapshot:Finished");
};

const switchControlsActive = () => {
  isSettingsButtonDisabled.value = !isSettingsButtonDisabled.value;
  isOptionButtonDisabled.value = !isOptionButtonDisabled.value;
  isTextareaDisabled.value = !isTextareaDisabled.value;
  isRegenerateButtonDisabled.value = !isRegenerateButtonDisabled.value;
  isTemplateButtonDisabled.value = !isTemplateButtonDisabled.value;
  updateUI();
};

const handleError = (error_message_t: string) => {
  loggerService.log("handleError");
  messageStore.activateErrorMessage(t(error_message_t));
  message.value = "";
  switchControlsActive();
};

const performMessageRequest = async (
  uuid: string,
  requestMessage: Message,
  regenerate: boolean = false,
): Promise<void> => {
  messageStore.deactivateErrorMessage();
  switchControlsActive();
  if (
    chatStore.isSwitchContextEnabled === true ||
    (chatStore.isSwitchChannelContextEnabled === true && props.channelmode === true)
  ) {
    loggerService.log("ChatInput:ContextMessage:Start");
    // Empty context means use vector db
    requestMessage.context = "";
    requestMessage = await messageStore.adaptMessageContext(uuid, requestMessage);
    if (requestMessage === undefined) {
      handleError("ChatInput.errorAdaptingMessageContext");
      return;
    }
    loggerService.log("ChatInput:ContextMessage:Finished");
  } else if (chatStore.isSwitchSelectedContextEnabled === true && props.channelmode === false) {
    loggerService.log("ChatInput:ContextSelectedMessage:Start");
    const selectedTranscriptContext = messageStore.getCurrentTranscriptSelection;
    loggerService.log("selectedTranscriptContext: " + selectedTranscriptContext);
    const interval = mediaStore.getIntervalFromCurrentTranscriptText(props.language, selectedTranscriptContext);
    requestMessage.context = mediaStore.getCurrentTranscriptTextInInterval("en", interval);
    loggerService.log("translatedSelectedTranscriptContext: " + requestMessage.context);
    // Context set use selected context
    requestMessage = await messageStore.adaptMessageContext(uuid, requestMessage);
    if (requestMessage === undefined) {
      handleError("ChatInput.errorAdaptingMessageContext");
      return;
    }
    loggerService.log("ChatInput:ContextSelectedMessage:Finished");
  } else {
    matomo_clicktracking("click_button", "Send chat messages without media context");
  }
  if (chatStore.isSwitchTranslationEnabled === true) {
    loggerService.log("ChatInput:TranslateMessage:Start");
    requestMessage = await messageStore.translateMessage(uuid, requestMessage);
    if (requestMessage === undefined) {
      handleError("ChatInput.errorTranslateMessage");
      return;
    }
    loggerService.log("ChatInput:TranslateMessage:Finished");
  }
  if (!regenerate) {
    messageStore.addMessage(uuid, requestMessage);
  }
  loggerService.log("ChatInput:LlmMessage:TrackContext:Start");
  for (let index = 0; index < requestMessage.content.length; index++) {
    const element = requestMessage.content[index];
    matomo_clicktracking("message_to_llm_" + element.language, element.content[0].text);
  }
  loggerService.log("ChatInput:LlmMessage:TrackContext:Finished");
  loggerService.log("ChatInput:LlmMessageStream:Start");
  messageStore.sendMessageStream(uuid, requestMessage, chatStore.isSwitchTranslationEnabled);
};

const addMessage = async (): Promise<void> => {
  if (chatStore.isSwitchVisionSnapshotEnabled && messageStore.getVideoSnapshot === "") {
    return;
  }
  if (
    message.value.trim() !== "" &&
    messageStore.getServicesAvailable === true &&
    messageStore.getServicesAlive === true
  ) {
    const uuid = props.uuid;
    const messageContentText = message.value.split("\\n").join(" ").trim().split("_").join(" ").trim();
    const contentItem = {
      type: "text",
      text: messageContentText,
    } as TextContent;
    let requestMessage = {
      content: [{language: locale.value, content: [contentItem]} as MessageContent],
      isUser: true,
      context: "",
      contextUuid: uuid,
      useContext:
        chatStore.isSwitchContextEnabled ||
        chatStore.isSwitchSelectedContextEnabled ||
        (chatStore.isSwitchChannelContextEnabled && props.channelmode === true),
      useContextAndCite:
        chatStore.isSwitchCitationEnabled || (chatStore.isSwitchChannelCitationEnabled && props.channelmode === true),
      useChannelContext: props.channelmode,
      useTranslate: chatStore.isSwitchTranslationEnabled,
      history: messageStore.createMessageHistory(uuid),
      actAsTutor: chatStore.isSwitchTutorEnabled,
      useVision: chatStore.isSwitchVisionEnabled && props.channelmode === false,
      useVisionSurroundingSlides: chatStore.isSwitchVisionSurroundingSlidesEnabled && props.channelmode === false,
      useVisionSnapshot: chatStore.isSwitchVisionSnapshotEnabled && props.channelmode === false,
      snapshot: messageStore.getVideoSnapshot,
      stream: false,
      reasoning: chatStore.isSwitchReasoningEnabled,
      mediaContextUuids: [],
      documentContextUuids: [],
    } as Message;
    // TODO: CHECK IF WE NEED TO LOG THE MESSAGES HERE
    matomo_clicktracking("message_to_llm", messageContentText);
    performMessageRequest(uuid, requestMessage);
  }
};

const regenerateMessageClickButton = () => {
  trackSending("click_button", true);
  const uuid = props.uuid;
  if (messageStore.getMessages(uuid)?.length > 1) {
    messageStore.removeLastBotMessages(uuid);
    const lastUserMessage = messageStore.getLastMessage(uuid);
    for (const item of lastUserMessage?.content as MessageContent[]) {
      if (item.language === locale.value) {
        matomo_clicktracking("message_to_llm", item.content[0].text);
        const pastMessages = messageStore.createMessageHistory(uuid);
        pastMessages?.pop();
        const requestMessage = {
          content: [item],
          isUser: true,
          context: "",
          contextUuid: uuid,
          useContext:
            chatStore.isSwitchContextEnabled ||
            chatStore.isSwitchSelectedContextEnabled ||
            (chatStore.isSwitchChannelContextEnabled && props.channelmode === true),
          useContextAndCite:
            chatStore.isSwitchCitationEnabled ||
            (chatStore.isSwitchChannelCitationEnabled && props.channelmode === true),
          useChannelContext: props.channelmode,
          useTranslate: chatStore.isSwitchTranslationEnabled,
          history: pastMessages,
          actAsTutor: chatStore.isSwitchTutorEnabled,
          useVision: chatStore.isSwitchVisionEnabled && props.channelmode === false,
          useVisionSurroundingSlides: chatStore.isSwitchVisionSurroundingSlidesEnabled && props.channelmode === false,
          useVisionSnapshot: chatStore.isSwitchVisionSnapshotEnabled && props.channelmode === false,
          snapshot: messageStore.getVideoSnapshot,
          stream: false,
          reasoning: chatStore.isSwitchReasoningEnabled,
          mediaContextUuids: [],
          documentContextUuids: [],
        } as Message;
        performMessageRequest(uuid, requestMessage, true);
        return;
      }
    }
  }
  return;
};

const clearMessagesClickButton = () => {
  matomo_clicktracking("click_button", "Clear messages");
  messageStore.clearMessages(props.uuid);
  messageStore.storeMessages();
};

const trackSending = (event: string, regenerate: boolean = false) => {
  let action = "Send";
  if (regenerate === true) {
    action = "Regenerate";
  }
  if (chatStore.isSwitchContextEnabled || chatStore.isSwitchSelectedContextEnabled) {
    if (chatStore.isSwitchTranslationEnabled) {
      matomo_clicktracking(event, action + " message with media context using translation");
    } else {
      matomo_clicktracking(event, action + " message with media context");
    }
  } else {
    if (chatStore.isSwitchTranslationEnabled) {
      matomo_clicktracking(event, action + " message using translation");
    } else {
      matomo_clicktracking(event, action + " message");
    }
  }
};

const sendMessageClickButton = () => {
  trackSending("click_button");
  addMessage();
};

const sendMessagePressEnter = () => {
  trackSending("press_enter");
  addMessage();
};

const handleTemplateSelection = (text: string) => {
  matomo_clicktracking("click_button", "Use prompt template");
  message.value = text;
};
</script>

<style scoped>
.control-box {
  padding: 5px;
}

.snapshot-container {
  display: flex;
  flex: 1;
  position: relative;
  border-radius: 25px;
  height: 100%;
  z-index: 1;
  max-width: 256px;
  margin-left: 0.5em;
  min-width: 128px;
}

.btn-del-snapshot {
  color: var(--hans-light);
  padding: 5px;
  border-radius: 25px;
  width: 32px;
  height: 32px;
  align-items: center;
  position: absolute;
  left: 87%;
  top: -16px;
  display: flex;
}

.img-snapshot {
  border: 1px solid #ccc;
  width: 100%;
  max-width: 128px;
}

.message-container {
  flex: 1;
  border-radius: 25px;
  width: 100%;
  padding-left: 2%;
  padding-right: 2%;
  position: relative;
  overflow: hidden;
  resize: none;
  z-index: 2;
  left: 0.7em;
}

.message-container-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
}

textarea.message-container {
  width: 100%;
  padding: 10px;
  box-sizing: border-box;
}

.buttons-container {
  display: flex;
  justify-content: center;
  gap: 0.1em;
  left: 0.7em;
  position: relative;
  padding-top: 0.3em;
  container-type: inline-size;
}

.option-button {
  color: var(--hans-dark);
  background-color: var(--hans-light-blue);
  border-color: var(--hans-light-blue);
  border-radius: 25px;
  width: fit-content;
  min-width: 2rem;
  align-items: center;
  display: flex;
  padding: 0.5rem;
}

.option-button:hover {
  color: var(--hans-dark);
  background-color: var(--hans-medium-blue);
  border-color: var(--hans-medium-blue);
}

.option-button-active {
  color: var(--hans-light-gray); /* rgb(72 170 255); */
  background-color: var(--hans-medium-blue); /* rgb(13, 110, 253); or #00bdff42;*/
  border-color: var(--hans-light-gray); /* rgb(72 170 255); */
}

.img-option-btn {
  /*filter: invert(calc(1 - var(--button-dark-mode, 0)));*/
  height: 24px;
  width: 32px;
}

.img-option-btn-active {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  height: 24px;
  width: 32px;
}

.help-button {
  color: var(--hans-light);
  border-radius: 25px;
  width: fit-content;
  min-width: 2rem;
  align-items: center;
  display: flex;
  padding: 0.5rem;
}

.button-text {
  display: flex;
  padding-left: 0.2em;
}

.btn-container {
  color: var(--hans-light);
  padding: 5px;
  border-radius: 25px;
}

.btn-translate {
  background-color: var(--hans-light-blue);
}

.btn-check:checked + .btn,
.btn.active,
.btn.show,
.btn:first-child:active,
:not(.btn-check) + .btn:active {
  background-color: var(--bs-btn-bg);
  border: none;
}

.option-toggle {
  border-top-right-radius: 25px !important;
  border-bottom-right-radius: 25px !important;
}

.option-toggle::after {
  content: "\2026"; /* Unicode for ellipsis (three dots) */
  padding: 5px;
}

.option-toggle:focus {
  outline: none;
}

.translate-img {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}

.btn-container:hover {
  color: var(--hans-dark);
  background-color: var(--hans-light);
}

.img-btn {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  height: 24px;
  width: 32px;
}

.btn-container:hover > .img-btn {
  filter: invert(calc(var(--button-dark-mode, 0) - 0));
}

.dropdown-img {
  filter: invert(calc(var(--button-dark-mode, 0) - 0));
  padding: 10px;
}

.dropdown-img-active {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}

.dropdown-item {
  border-radius: 25px;
  padding-inline: 2em;
  margin-top: 0.4vh;
}

.template-button {
  background-image: url("/bootstrap-icons/card-text.svg");
}

.help-dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
}

.template-item > a {
  margin-right: 20px;
}

@media (max-width: 600px) {
  .button-text {
    display: none;
  }
  .img-btn {
    font-size: 20px; /* Adjust icon size */
  }
}

@container (max-width: 544px) {
  .button-text {
    display: none;
  }
  .img-btn {
    font-size: 20px; /* Adjust icon size */
  }
}
</style>
