<template>
  <div ref="chatScrollContainer" class="d-col chat-messages">
    <div
      v-if="messageStore.getShowErrorMessage || messageStore.getRequestError"
      class="alert alert-danger d-flex align-items-center error-container"
      role="alert"
    >
      <img
        class="img-fluid bi flex-shrink-0 me-2"
        width="24"
        height="24"
        src="/bootstrap-icons/exclamation-triangle-fill.svg"
        alt="error-image"
      />
      <p v-if="messageStore.getShowErrorMessage">
        {{ messageStore.getErrorMessageText }}
      </p>
      <p v-else-if="messageStore.getRequestWasCanceled">
        {{ t("ChatMessages.errorRequestCanceled") }}
      </p>
      <p v-else-if="messageStore.getRequestTimeoutError">
        {{ t("ChatMessages.errorRequestTimeout") }}
      </p>
      <p v-else>
        {{ t("ChatMessages.errorRequest") }}
      </p>
    </div>
    <div
      v-for="(message, index) in messages"
      :key="index"
      :class="message.isUser ? 'user-chat-messages-inner' : 'bot-chat-messages-inner'"
    >
      <div v-if="message.content?.length > 1" :class="message.isUser ? 'user-message' : 'bot-message'">
        <div v-if="message.content[0].language === locale" class="message-content">
          <div :id="'pMessageContainer_' + index">
            <div v-if="message.isUser === true">
              {{ message.content[0].content[0].text }}
            </div>
            <div
              :id="'botContainer_' + index"
              v-else
              :innerHTML="
                renderBotContent(
                  'botContainer_' + index,
                  message.content[0],
                  message.context,
                  message.useContextAndCite,
                  message.snapshot,
                )
              "
            ></div>
            <div v-if="showInfo === index && message.content[1]">
              <hr class="my-1 dotted-divider" />
              <div v-if="message.isUser === true">
                {{ message.content[1].content[0].text }}
              </div>
              <div
                :id="'botContainerTranslation_' + index"
                v-else
                :innerHTML="
                  renderBotContent(
                    'botContainerTranslation_' + index,
                    message.content[1],
                    message.context,
                    message.useContextAndCite,
                    message.snapshot,
                  )
                "
              ></div>
            </div>
            <div :class="[showInfo === index ? 'dropup' : 'dropdown', 'd-flex', 'justify-content-end']">
              <button
                :class="[
                  'btn',
                  'btn-primary',
                  'btn-sm',
                  'dropdown-toggle',
                  showInfo === index ? 'btn-content-additional' : 'btn-content',
                ]"
                @click="toggleAdditionalInfo(index)"
              >
                <img src="/bootstrap-icons/translate.svg" alt="api-btn" class="img-fluid additional-translation-img" />
              </button>
              <button
                :class="['btn', 'btn-primary', 'btn-sm', showInfo === index ? 'btn-content-additional' : 'btn-content']"
                @click="copyContentToClipboard('pMessageContainer_' + index, 'pMessageContainerCopyImg_' + index)"
                data-bs-toggle="tooltip"
                data-bs-placement="bottom"
                :title="t('ChatInput.tooltipCopyButton')"
              >
                <img
                  :id="'pMessageContainerCopyImg_' + index"
                  src="/bootstrap-icons/clipboard.svg"
                  alt="api-btn"
                  class="img-fluid copy-img"
                />
              </button>
              <ChatContextWindow
                index-suffix="pMessageContainer"
                :is-user="message.isUser"
                :use-context="message.useContext"
                :css-class="showInfo === index ? 'btn-content-additional' : 'btn-content'"
                :index="index"
                :context="message.context"
                :context-uuid="message.contextUuid"
                :videoUuid="props.video.uuid"
              ></ChatContextWindow>
              <ChatFeedback
                index-suffix="pMessageContainer"
                :is-user="message.isUser"
                :css-class="showInfo === index ? 'btn-content-additional' : 'btn-content'"
                :index="index"
                :content="message.content"
                :use-context="message.useContext"
                :use-context-and-cite="message.useContextAndCite"
                :context-uuid="message.contextUuid"
              ></ChatFeedback>
            </div>
          </div>
        </div>
        <div v-else-if="message.content[1].language === locale" class="message-content">
          <div :id="'pMessageContainerT_' + index">
            <div v-if="message.isUser === true">
              {{ message.content[1].content[0].text }}
            </div>
            <div
              :id="'botContainer_' + index"
              v-else
              :innerHTML="
                renderBotContent(
                  'botContainer_' + index,
                  message.content[1],
                  message.context,
                  message.useContextAndCite,
                  message.snapshot,
                )
              "
            ></div>
            <div v-if="showInfo === index && message.content[0]">
              <hr class="my-1 dotted-divider" />
              <div v-if="message.isUser === true">
                {{ message.content[0].content[0].text }}
              </div>
              <div
                :id="'botContainerTranslation_' + index"
                v-else
                :innerHTML="
                  renderBotContent(
                    'botContainerTranslation_' + index,
                    message.content[0],
                    message.context,
                    message.useContextAndCite,
                    message.snapshot,
                  )
                "
              ></div>
            </div>
            <div :class="[showInfo === index ? 'dropup' : 'dropdown', 'd-flex', 'justify-content-end']">
              <button
                :class="[
                  'btn',
                  'btn-primary',
                  'btn-sm',
                  'dropdown-toggle',
                  showInfo === index ? 'btn-content-additional' : 'btn-content',
                ]"
                @click="toggleAdditionalInfo(index)"
              >
                <img src="/bootstrap-icons/translate.svg" alt="api-btn" class="img-fluid additional-translation-img" />
              </button>
              <button
                :class="['btn', 'btn-primary', 'btn-sm', showInfo === index ? 'btn-content-additional' : 'btn-content']"
                @click="copyContentToClipboard('pMessageContainerT_' + index, 'pMessageContainerTCopyImg_' + index)"
                data-bs-toggle="tooltip"
                data-bs-placement="bottom"
                :title="t('ChatInput.tooltipCopyButton')"
              >
                <img
                  :id="'pMessageContainerTCopyImg_' + index"
                  src="/bootstrap-icons/clipboard.svg"
                  alt="api-btn"
                  class="img-fluid copy-img"
                />
              </button>
              <ChatContextWindow
                index-suffix="pMessageContainerT"
                :is-user="message.isUser"
                :use-context="message.useContext"
                :css-class="showInfo === index ? 'btn-content-additional' : 'btn-content'"
                :index="index"
                :context="message.context"
                :context-uuid="message.contextUuid"
                :videoUuid="props.video.uuid"
              ></ChatContextWindow>
              <ChatFeedback
                index-suffix="pMessageContainerT"
                :is-user="message.isUser"
                :css-class="showInfo === index ? 'btn-content-additional' : 'btn-content'"
                :index="index"
                :content="message.content"
                :use-context="message.useContext"
                :use-context-and-cite="message.useContextAndCite"
                :context-uuid="message.contextUuid"
              ></ChatFeedback>
            </div>
          </div>
        </div>
      </div>
      <div v-else :class="message.isUser ? 'user-message' : 'bot-message'">
        <div class="message-content" v-for="(content, cindex) in message.content" :key="cindex">
          <div :id="'pMessageContainerS_' + index">
            <div v-if="message.isUser === true">
              {{ content.content[0].text }}
            </div>
            <div
              :id="'botContainerContent_' + cindex"
              v-else
              :innerHTML="
                renderBotContent(
                  'botContainerContent_' + cindex,
                  content,
                  message.context,
                  message.useContextAndCite,
                  message.snapshot,
                )
              "
            ></div>
            <div class="d-flex justify-content-end">
              <button
                :class="['btn', 'btn-primary', 'btn-sm', 'btn-content']"
                @click="copyContentToClipboard('pMessageContainerS_' + index, 'pMessageContainerSCopyImg_' + index)"
                data-bs-toggle="tooltip"
                data-bs-placement="bottom"
                :title="t('ChatInput.tooltipCopyButton')"
              >
                <img
                  :id="'pMessageContainerSCopyImg_' + index"
                  src="/bootstrap-icons/clipboard.svg"
                  alt="api-btn"
                  class="img-fluid copy-img"
                />
              </button>
              <ChatContextWindow
                index-suffix="pMessageContainerS"
                :is-user="message.isUser"
                :use-context="message.useContext"
                :css-class="showInfo === index ? 'btn-content-additional' : 'btn-content'"
                :index="index"
                :context="message.context"
                :context-uuid="message.contextUuid"
                :videoUuid="props.video.uuid"
              ></ChatContextWindow>
              <ChatFeedback
                index-suffix="pMessageContainerS"
                :is-user="message.isUser"
                :css-class="showInfo === index ? 'btn-content-additional' : 'btn-content'"
                :index="index"
                :content="message.content"
                :use-context="message.useContext"
                :use-context-and-cite="message.useContextAndCite"
                :context-uuid="message.contextUuid"
              ></ChatFeedback>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as bootstrap from "bootstrap/dist/js/bootstrap.bundle.min.js";
import Prism from "prismjs";
import "prismjs/themes/prism-coy.min.css";
import renderMathInElement from "katex/dist/contrib/auto-render.mjs";
import "katex/dist/katex.min.css";
import DOMPurify from "dompurify";
import * as marked from "marked";
import {computed, inject, onMounted, nextTick, ref, watch} from "vue";
import {useI18n} from "vue-i18n";
import {useRouter} from "vue-router";
import {useMessageStore} from "@/stores/message";
import {useMediaStore} from "@/stores/media";
import {LoggerService} from "@/common/loggerService";
import type {MediaItem} from "@/data/MediaItem.js";
import ChatContextWindow from "@/components/ChatContextWindow.vue";
import ChatFeedback from "@/components/ChatFeedback.vue";
import type {MessageContent} from "@/data/Message";
import {apiClient} from "@/common/apiClient";
import {SetPageEvent, SetPositionEvent} from "@/common/events";

const loggerService = new LoggerService();

const {t, locale} = useI18n({useScope: "global"});
const props = defineProps<{
  video: MediaItem;
}>();

const showInfo = ref(null);
const eventBus = inject("eventBus"); // Inject `eventBus`

const skipVideoToPosition = (position) => {
  loggerService.log(`ChatMessages:skipVideoToPosition: ${position}`);
  eventBus.emit("setPositionEvent", new SetPositionEvent(position, "popover", 0));
};

const skipSlidesToPage = (page) => {
  loggerService.log(`ChatMessages:skipSlidesToPage: ${page}`);
  eventBus.emit("setPageEvent", new SetPageEvent(page, "popover", page - 1));
};

const renderLatexMath = () => {
  loggerService.log("ChatMessages:renderLatexMath:Start");
  const elements = document.querySelectorAll('[id^="botContainerContent"]');
  elements.forEach((item) => {
    renderMathInElement(item, {
      delimiters: [
        {left: "\\begin{equation}", right: "\\end{equation}", display: true},
        {left: "\\begin{align}", right: "\\end{align}", display: true},
        {left: "\\begin{alignat}", right: "\\end{alignat}", display: true},
        {left: "\\begin{gather}", right: "\\end{gather}", display: true},
        {left: "\\begin{CD}", right: "\\end{CD}", display: true},
        {left: "$$", right: "$$", display: true},
        {left: "$", right: "$", display: false},
        {left: "\\(", right: "\\)", display: true},
        {left: "\\[", right: "\\]", display: true},
        {left: "\n(", right: "\n)", display: false},
        {left: "\n[", right: "\n]", display: true},
        {left: "<li>(", right: ")</li>", display: true},
        {left: "( ", right: " )", display: false},
        {left: "[ ", right: " ]", display: true},
      ],
      displayMode: true,
      //ignoredClasses: ["ignore_Format"],
      throwOnError: true,
      // see https://katex.org/docs/options
      strict: "unicodeTextInMathMode",
    });
  });
  loggerService.log("ChatMessages:renderLatexMath:End");
};

const toggleAdditionalInfo = async (index) => {
  showInfo.value = showInfo.value === index ? null : index;
  await nextTick(async () => {
    loggerService.log("ChatMessages:toggleAdditionalInfo: Activate popovers!");
    renderLatexMath();
    Prism.highlightAll();
    await loadPopovers();
  });
};

const messageStore = useMessageStore();
const mediaStore = useMediaStore();
const router = useRouter();

const beforeRouteLeave = () => {
  loggerService.log("ChatMessages:beforeRouteLeave: storeMessages");
  messageStore.storeMessages();
};

// Register the beforeRouteLeave guard
router.beforeEach((to, from, next) => {
  beforeRouteLeave();
  next();
});

if (!messageStore.isInitialized()) {
  loggerService.log("ChatMessages:loadMessages");
  messageStore.loadMessages();
}

const messages = computed(() => messageStore.getMessages(props.video.uuid));
const chatScrollContainer = ref<HTMLElement | null>(null);

// Watch for changes in messages and scroll to the bottom
watch(messageStore.messages, async () => {
  await nextTick(async () => {
    loggerService.log("ChatMessages: messages changed!");
    scrollChat();
    renderLatexMath();
    Prism.highlightAll();
    await loadPopovers();
  });
});

const scrollChat = () => {
  if (chatScrollContainer.value) {
    if (messageStore.getShowErrorMessage === true) {
      chatScrollContainer.value.scrollTop = 0;
      loggerService.log("ChatMessages:scrollChat:ToTop");
    } else {
      const children = chatScrollContainer.value.children;
      let totalHeight = 0;

      for (let i = 0; i < children.length; i++) {
        totalHeight += children[i].clientHeight;
      }
      loggerService.log(totalHeight);
      chatScrollContainer.value.scrollTop = totalHeight;
      loggerService.log("ChatMessages:scrollChat:ToBottom");
    }
  }
};

const loadPopovers = async () => {
  const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
  for (const popoverTriggerEl of popoverTriggerList) {
    // Get the current content of the data-bs-content attribute
    let content = popoverTriggerEl.getAttribute("data-bs-content");
    if (popoverTriggerEl.hasAttribute("data-slide")) {
      const slideNumber = popoverTriggerEl.getAttribute("data-slide");
      popoverTriggerEl.addEventListener("click", (event) => {
        skipSlidesToPage(Number(slideNumber));
      });
    } else if (popoverTriggerEl.hasAttribute("data-interval")) {
      const interval = popoverTriggerEl.getAttribute("data-interval");
      popoverTriggerEl.addEventListener("click", (event) => {
        skipVideoToPosition(Number(interval));
      });
    }

    // Regular expression to match the src value in an img tag
    const srcRegex = /src="(.*?)"/;

    // Extract the current src value (if exists)
    const match = content.match(srcRegex);

    if (match && match[1]) {
      const previousSrc = match[1]; // This is the previous src value
      loggerService.log("ChatMessages:PreviousImageSrc: " + previousSrc);
      if (previousSrc?.length > 0 && !previousSrc.includes("http") && !previousSrc.includes("data:image/png;base64")) {
        const {data} = await apiClient.get("/getThumbnail?urn=" + previousSrc);
        loggerService.log(`ChatMessages:SlideContextUrlObject: ${data}`);
        if ("data" in data && Object.keys(data.data).length > 0) {
          loggerService.log("ChatMessages:NewImageSrc:", data.data);
          // Replace the old src with the new one
          const newContent = content.replace(srcRegex, `src="${data.data}"`);
          // Update the data-bs-content attribute with the new content
          popoverTriggerEl.setAttribute("data-bs-content", newContent);
        } else {
          loggerService.error("Error fetching slide image url from urn!");
        }
      } else {
        loggerService.log("Warning: PreviousImageSrc is empty or already an url.");
      }
    }
    // Initialize the popover with the updated content
    new bootstrap.Popover(popoverTriggerEl, {
      html: true, // Enable HTML rendering in the popover
    });
  }
};

// Automatically scroll to the bottom when the component is mounted
onMounted(async () => {
  loggerService.log("ChatMessages:onMounted");
  scrollChat();
  renderLatexMath();
  Prism.highlightAll();
  await loadPopovers();
});

// MAYBE replace with https://www.npmjs.com/package/isomorphic-dompurify
// check also https://marked.js.org/using_pro
// Example: Sanitize HTML with isomorphic-dompurify
// https://stackoverflow.com/questions/65646007/next-js-dompurify-sanitize-shows-typeerror-dompurify-webpack-imported-module
interface IDOMPurifyWindow extends Window {
  DOMPurify: typeof DOMPurify;
}
const purify = (window as unknown as IDOMPurifyWindow)?.DOMPurify || DOMPurify;
const sanitize = (html: string): string => purify.sanitize(html);

// https://marked.js.org/using_advanced#options
/*marked.use({
  async: false,
  pedantic: false,
  gfm: true,
});*/

// Adjust rendering of the content returned by the bot
const renderBotContent = (
  elementId: string,
  messageContent: MessageContent,
  context: string,
  modeUseContextAndCite: boolean,
  snapshot: string,
) => {
  loggerService.log("ChatMessages:renderBotContent");
  // https://marked.js.org/
  let dirtyHtml = marked.parse(messageContent.content[0].text.replace("/^[\u200B\u200C\u200D\u200E\u200F\uFEFF]/", ""));
  // Remove empty elements
  dirtyHtml = dirtyHtml.split("\\n").join("<br>");
  // Add missing pre if necessary
  if (dirtyHtml.includes("<p><code>")) {
    dirtyHtml = dirtyHtml.split("<p><code>").join("<p><pre><code>");
    dirtyHtml = dirtyHtml.split("</code></p>").join("</code></pre></p>");
  }
  dirtyHtml = dirtyHtml.split("<pre><code></code></pre>").join("");
  dirtyHtml = dirtyHtml
    .split("<br>&#39;</p>")
    .join("</p>")
    .replace(/(<br>){3,}/g, "<br><br>");
  loggerService.log(dirtyHtml);
  loggerService.log("ChatMessages:cleanHTML");
  // https://www.npmjs.com/package/dompurify#how-do-i-use-it
  let clean = sanitize(dirtyHtml);

  // Inject links for references
  if (modeUseContextAndCite === true) {
    const replaceList = new Map<string, string>();
    const regex = /(\[[0-9]+\])/g; // Add 'g' flag for global matching
    let match;
    while ((match = regex.exec(clean)) !== null) {
      const citation = match[1]; // The captured citation, e.g., "[0]", "[1]", "[2]"
      loggerService.log(citation);
      const citationId = citation.replace("[", "").replace("]", "");
      const citationIndex = parseInt(citationId, 10);
      loggerService.log(citationIndex);
      const splitQuote = "- [";
      const contextArr = context.trim().split(splitQuote);
      loggerService.log(contextArr);
      const prefix = citationId + "]";
      contextArr.forEach((hoverContext) => {
        if (hoverContext.startsWith(prefix)) {
          // https://getbootstrap.com/docs/5.3/components/popovers/
          hoverContext = hoverContext.replace(citationId + "]", "");
          const hoverContextTextEnOrig = hoverContext.split("\\n").join("\n");
          let hoverContextText = hoverContextTextEnOrig;
          if (citationIndex < 100) {
            // Cite transcript
            let interval = mediaStore.getIntervalFromCurrentTranscriptText("de", hoverContextTextEnOrig);
            if (messageContent.language === "de") {
              interval = mediaStore.getIntervalFromCurrentTranscriptText("en", hoverContextTextEnOrig);
              hoverContextText = mediaStore.getCurrentTranscriptTextInInterval("de", interval);
            }
            const hoverElement = `
            <a href="#"
              class="reference-link"
              data-bs-trigger="focus"
              data-bs-toggle="popover"
              data-interval="${interval[0]}"
              title="${t("ChatInput.citationPopoverTitle")}"
              data-bs-content='${hoverContextText}'>
              ${citation}
            </a>`;
            if (!replaceList.has(citation)) {
              replaceList.set(citation, hoverElement);
            }
          } else if (citationIndex > 99 && citationIndex < 999) {
            // Cite slides
            const slide_number = (citationIndex - 100).toString();
            const slide_index = (citationIndex - 101).toString();
            const uri = mediaStore.getSlidesImagesFolderUrnByUuid(props.video.uuid) + "/" + slide_number + ".png";
            loggerService.log(`ChatMessages:SlideContextUrn: ${uri}`);
            const hoverElement = `
            <a href="#"
              class="reference-link"
              data-bs-trigger="focus"
              data-bs-toggle="popover"
              data-slide="${slide_number}"
              title="${t("ChatInput.citationPopoverSlideTitle")} ${slide_number}"
              data-bs-content='<img src="${uri}" alt="Hover Image" class="img-fluid" />'>
              [${t("ChatInput.citationPopoverSlideLink")} ${slide_number}]
            </a>`;
            if (!replaceList.has(citation)) {
              replaceList.set(citation, hoverElement);
            }
          } else {
            // Cite snapshot
            const snapshot_number = (citationIndex - 999).toString();
            loggerService.log(`ChatMessages:SnapshotContextUrn: ${snapshot}`);
            const hoverElement = `
            <a href="#"
              class="reference-link"
              data-bs-trigger="focus"
              data-bs-toggle="popover"
              title="${t("ChatInput.citationPopoverSnapshotTitle")} ${snapshot_number}"
              data-bs-content='<img src="${snapshot}" alt="Hover Image" class="img-fluid" />'>
              [${t("ChatInput.citationPopoverSnapshotLink")} ${snapshot_number}]
            </a>`;
            if (!replaceList.has(citation)) {
              replaceList.set(citation, hoverElement);
            }
          }
        }
      });
    }
    replaceList.set("\\ n", "");
    replaceList.forEach((value, key) => {
      //loggerService.log(`Key: ${key}, Value: ${value}`);
      clean = clean.split(key).join(value);
    });
  }
  if (messageStore.getShowErrorMessage === true) {
    scrollChat();
  }
  return clean;
};

const getContentText = (element) => {
  let text = "";
  for (let child of element.children) {
    text += child.textContent + "\n";
  }
  return text;
};

const switchImageWithDelay = (elementId: string, newImageUrl: string, delayMilliseconds: number) => {
  // Find the <img> element by its id
  const imgElement = document.getElementById(elementId) as HTMLImageElement;

  if (imgElement) {
    // Save the original src attribute value
    const originalSrc = imgElement.src;

    // Change the src attribute to the new image URL
    imgElement.src = newImageUrl;

    // After the specified delay, revert back to the original image
    setTimeout(() => {
      imgElement.src = originalSrc;
    }, delayMilliseconds);
  } else {
    loggerService.error(`Element with id ${elementId} not found.`);
  }
};

const copyContentToClipboard = (elementId: string, copyImgId: string) => {
  const contentElement = document.getElementById(elementId);
  const contentText = getContentText(contentElement).trim();

  if (navigator.clipboard) {
    navigator.clipboard
      .writeText(contentText)
      .then(() => {
        loggerService.log("Content copied to clipboard");
        switchImageWithDelay(copyImgId, "/bootstrap-icons/check-circle-fill.svg", 5000);
      })
      .catch((error) => {
        loggerService.error("Failed to copy text to clipboard:", error);
      });
  } else {
    // Fallback for browsers that do not support the Clipboard API
    const tempTextArea = document.createElement("textarea");
    tempTextArea.value = contentText;
    document.body.appendChild(tempTextArea);
    tempTextArea.select();
    document.execCommand("copy");
    document.body.removeChild(tempTextArea);
    loggerService.log("Content copied to clipboard using fallback");
    switchImageWithDelay(copyImgId, "/bootstrap-icons/check-circle-fill.svg", 5000);
  }
};
</script>

<style scoped>
.btn-content {
  float: right;
  border-radius: 15px;
  width: 48px;
  height: 32px;
  margin-bottom: 1vw;
}
.btn-content-additional {
  float: right;
  border-radius: 15px;
  width: 48px;
  height: 32px;
  margin-bottom: 1vw;
}
.copy-img {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  width: 24px;
}
.additional-translation-img {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  width: 24px;
}
.chat-messages {
  display: flex;
  flex-direction: column;
  max-height: 40vh;
  margin-bottom: 3em;
  overflow-y: auto;
}
.bot-chat-messages-inner {
  display: flex;
  flex-direction: row;
  padding: 20px;
}
.user-chat-messages-inner {
  display: flex;
  flex-direction: column;
  padding: 20px;
}
.user-message {
  align-self: flex-end;
  background-color: #d4eaff;
  color: #000;
  border-radius: 15px;
  margin-bottom: 10px;
  position: relative; /* Position for the "tail" */
  text-align: right; /* Align text to the right */
}

.bot-message {
  align-self: flex-start;
  background-color: #f0f0f0;
  color: #000;
  border-radius: 15px;
  margin-bottom: 10px;
  position: relative; /* Position for the "tail" */
  text-align: left; /* Align text to the right */
}

.message-content {
  padding: 10px;
  word-wrap: break-word; /* Allow wrapping of long words */
  max-width: 100%;
}

/* User message "tail" */
.user-message::before {
  content: "";
  position: absolute;
  top: 50%;
  right: -10px; /* Adjust the right position for the tail */
  width: 0;
  height: 0;
  border-top: 10px solid transparent;
  border-bottom: 10px solid transparent;
  border-left: 10px solid #d4eaff; /* Use the same background color as the bubble */
  transform: translateY(-50%);
}

/* Bot message "tail" */
.bot-message::before {
  content: "";
  position: absolute;
  top: 50%;
  left: -10px; /* Adjust the left position for the tail */
  width: 0;
  height: 0;
  border-top: 10px solid transparent;
  border-bottom: 10px solid transparent;
  border-right: 10px solid #f0f0f0; /* Use the same background color as the bubble */
  transform: translateY(-50%);
}
.dropdown,
.dropdown-center,
.dropend,
.dropstart,
.dropup,
.dropup-center {
  position: relative;
  padding-top: 0.5em;
}
</style>
