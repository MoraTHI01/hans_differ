<template>
  <div v-if="messageStore.getServicesAvailable">
    <div v-if="viewportWidth > 786">
      <div class="card-body p-1 chat-container container" @mouseenter="handleFocus" ref="chatComponent">
        <div class="row-6 chat-messages-container">
          <ChatMessages :video="props.video" />
        </div>
        <div class="card-body p-1">
          <ChatInput :video="props.video" />
        </div>
      </div>
    </div>
    <div v-else class="container chat-container-modal d-flex justify-content-center align-items-center">
      <button
        :class="['btn', 'btn-primary', 'btn-sm', 'btn-open-chat']"
        :title="t('ChatComponent.openChatButton')"
        @click="openModal"
      >
        <img src="/bootstrap-icons/robot.svg" alt="open-chat" class="img-fluid img-btn" />
        {{ t("ChatComponent.openChatButton") }}
      </button>
      <div class="modal fade" tabindex="-2" role="dialog" ref="chatModal">
        <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" role="document">
          <div class="modal-content">
            <div class="modal-header">
              <h1 class="modal-title fs-5">{{ t("ChatComponent.title") }}</h1>
              <button
                type="button"
                class="btn-close modal-close"
                @click="closeModal"
                :aria-label="t('ChatComponent.closeButton')"
              ></button>
            </div>
            <div
              class="modal-body card-body p-1 chat-container container"
              @mouseenter="handleFocus"
              ref="chatComponent"
            >
              <div class="row-6 chat-messages-container">
                <ChatMessages :video="props.video" />
              </div>
              <div class="card-body p-1">
                <ChatInput :video="props.video" />
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-primary" @click="closeModal">
                {{ t("ChatComponent.closeButton") }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else>
    <ChatLoading></ChatLoading>
  </div>
</template>

<script setup lang="ts">
import {ref, watch, onMounted} from "vue";
import ChatMessages from "@/components/ChatMessages.vue";
import ChatInput from "@/components/ChatInput.vue";
import ChatLoading from "@/components/ChatLoading.vue";
import {useMessageStore} from "@/stores/message";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import type {MediaItem} from "@/data/MediaItem";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  video: MediaItem;
  active: boolean;
}>();

const chatModal = ref(null);

const openModal = () => {
  if (chatModal.value) {
    loggerService.log("ChatComponent:WindowOpen");
    chatModal.value.classList.add("show");
    chatModal.value.style.display = "block";
    scrollChatComponent();
  }
};

const closeModal = () => {
  if (chatModal.value) {
    loggerService.log("ChatComponent:WindowClose");
    chatModal.value.classList.remove("show");
    chatModal.value.style.display = "none";
  }
};

const messageStore = useMessageStore();
const chatComponent = ref(null);
const viewportWidth = ref(window.innerWidth);

const scrollChatComponent = () => {
  if (chatComponent.value) {
    if (messageStore.getShowErrorMessage === true) {
      chatComponent.value.scrollTop = 0;
      loggerService.log("scrollChatComponent:ToTop");
    } else {
      const children = chatComponent.value.children;
      let totalHeight = 0;

      for (let i = 0; i < children.length; i++) {
        totalHeight += children[i].clientHeight;
      }
      loggerService.log(totalHeight);
      chatComponent.value.scrollTop = totalHeight;
      loggerService.log("scrollChatComponent:ToBottom");
    }
  }
};

const handleFocus = async () => {
  loggerService.log("Chat window has gained focus");
  scrollChatComponent();
  await messageStore.fetchServiceAlive();
};

// Automatically scroll to the bottom when the component is mounted
onMounted(() => {
  loggerService.log("ChatComponent:onMounted");
  scrollChatComponent();
});
</script>

<style scoped>
.chat-container {
  overflow-y: auto;
  overflow-x: clip;
}
.chat-container-loading {
  overflow-y: auto;
  word-break: break-word;
  cursor: default;
  height: max-content;
}
.chat-container-loading-spinner {
  width: 100%;
  height: max-content;
  top: 1em;
  position: relative;
}
.chat-container-loading-text {
  width: 100%;
  height: max-content;
  top: 1em;
  position: relative;
}
.chat-messages-container {
  width: 100%;
  height: 40vh;
}
.chat-input-container {
  height: 15vh;
  padding-top: 10px;
}
.popout {
  position: absolute;
  top: 0px;
  left: 50%;
  transform: translate(-50%);
  background-color: #fff;
  border: 1px solid #ccc;
  box-shadow: 0 2px 4px #0000001a;
  z-index: 999;
  width: 110%;
}
.img-btn {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  height: 24px;
  width: 32px;
}
.chat-container-modal {
  overflow-y: auto;
  word-break: break-word;
  cursor: default;
  height: max-content;
  min-height: 8vh;
}
.btn-open-chat {
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
