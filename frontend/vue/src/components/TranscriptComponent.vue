<template>
  <div class="card-body transcript-container">
    <div class="transcript-button-bar">
      {{ t("TranscriptComponent.transcript")
      }}<ButtonHint route="generalnotes" :hovertext="t('TranscriptComponent.hint')" :hint_after="true" />
      <button
        type="button"
        class="btn btn-primary font-size-btn"
        @click="decreaseFontSize"
        :title="t('TranscriptComponent.decreaseFontSize')"
      >
        Aˇ
      </button>
      <button
        type="button"
        class="btn btn-primary font-size-btn"
        @click="increaseFontSize"
        :title="t('TranscriptComponent.increaseFontSize')"
      >
        Aˆ
      </button>
      <ExportTranscriptWindow class="btn btn-primary font-size-btn" :uuid="props.uuid" :disableComp="exportDisabled" />
    </div>
    <div
      class="transcript border"
      ref="transcriptElement"
      @mouseup="handleMouseUpTranscript"
      @scroll="handleScrollTranscript"
    >
      <LoadingBar v-if="store.getTranscriptLoading" />
      <div class="transcript-error" v-if="transcriptLoadingError">Transcript failed to load</div>
      <div
        class="segment-words"
        :id="'segment' + index"
        v-for="(segment, index) in store.getTranscript.segments"
        :key="segment.start"
      >
        <!-- Explicit breaking space preceded by a template tag that's never rendered to circumvent template compiler whitespace trimming between words -->
        <template v-for="item in segment.words" :key="item.index">
          <template v-if="false" />&#32;<span
            :id="item.index?.toString()"
            class="textitem"
            @click="sendPosition(item)"
            >{{ item.word }}</span
          ></template
        >
      </div>
      <div
        v-if="showOverlay"
        class="overlay"
        :style="{
          top: overlayTop + 'px',
          left: overlayLeft + 'px',
          width: overlayWidth + 'px',
          height: overlayHeight + 'px',
        }"
      >
        <img
          class="img-fluid clear-btn"
          :src="imageUrl"
          @mouseover="handleMouseOverClearBtn"
          @mouseleave="handleMouseLeaveClearBtn"
          alt="Clear Selection"
          @click="clearTranscriptSelection(true)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {inject, watch, ref, onMounted, onUnmounted} from "vue";
import {useMediaStore} from "@/stores/media";
import {IntervalTree} from "@/common/discreteIntervalTree";
import LoadingBar from "@/components/LoadingBarComponent.vue";
import ButtonHint from "@/components/ButtonHint.vue";
import ExportTranscriptWindow from "@/components/ExportTranscriptWindow.vue";
import type {Emitter, EventType} from "mitt";
import type {WordItem} from "@/data/AsrResults";
import {SetPositionEvent} from "@/common/events";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {useMessageStore} from "@/stores/message";
import {useAuthStore} from "@/stores/auth";

const {t} = useI18n({useScope: "global"});
const messageStore = useMessageStore();
const SELECTED_CLASS = "selected";

const eventBus: Emitter<Record<EventType, unknown>> = inject("eventBus")!;
const transcriptElement = ref();

const props = defineProps<{
  uuid: string;
  videoPlaying: boolean;
}>();
const emit = defineEmits(["transcriptLoaded"]);

/**
 * Send the start of the interval and index of the given text item as `setPositionEvent` for synchronization
 *
 * @param {} textItem - The text item which the event is created from
 */
function sendPosition(textItem: WordItem) {
  matomo_clicktracking(
    "click_transcript_word",
    "word: " + textItem.word + " - pos: " + textItem.interval[0] + " - index: " + textItem.index,
  );
  eventBus.emit("setPositionEvent", new SetPositionEvent(textItem.interval[0], "transcript", textItem.index));
}

const store = useMediaStore();
const transcriptLoadingError = ref(false);

let oldWordId: string | null = null;
let oldSegmentId: string | null = null;
let segmentMode = props.videoPlaying;

/**
 * Deselects an element with the given ID
 *
 * @param {string | null | undefined} id - The ID of the to be deselected
 */
function deselect(id?: string | null) {
  if (id != null) {
    document.getElementById(id)?.classList.remove(SELECTED_CLASS);
  }
}

// Load the transcript and prepare the interval tree and add synchronization
// events once the promise resolves after loading is complete
store.loadTranscript(props.uuid).then((transcript) => {
  // Display an error and exit if the transcript couldn't be loaded
  if (transcript === undefined) {
    transcriptLoadingError.value = true;
    return;
  }
  const tree = new IntervalTree(transcript.allWords.map((word) => word.interval));

  eventBus.on("setPositionEvent", (event: SetPositionEvent) => {
    // Fall back to a time-based search if the index is not already given explicitly
    if (event.index === undefined) {
      event.index = tree.findIndex(event.position);
      // Handles the timestamp being out of range (before the first word or after the last word in the transcript)
      if (event.index === undefined) {
        return;
      }
    }
    scrollToElementById(event.index.toString());
  });

  eventBus.on("videoPlaying", (position: number) => {
    const index = tree.findIndex(position);
    if (index !== undefined) {
      scrollToSegmentByWordId(index.toString());
    }
  });
  emit("transcriptLoaded");
});

/**
 * Gets the HTML element for the given word ID and checks that it exists
 *
 * @param {string} id - A word ID to look up
 *
 * @return {HTMLElement} The HTML element for the given `id`
 */
function getWordElement(id: string): HTMLElement {
  const word = document.getElementById(id);
  if (word === null) {
    throw Error(`Transcript word "${word}" not found`);
  }

  return word;
}

/**
 * Scrolls to the segment which contains the given word ID and highlights the entire segment.
 * If the segment is shorter than the transcript container, the whole containing segment is kept at the bottom for ease of readability.
 * Otherwise, the given word is positioned at the bottom of the container to keep as much prior context visible as possible.
 *
 * @param {string} id - The ID to scroll into view and for which the segment it is contained in will be highlighted
 */
function scrollToSegmentByWordId(id: string) {
  // Doesn't scroll if the transcript is not yet loaded
  // or the previous word Id and segment mode are the same to avoid selecting the same word multiple times
  if (transcriptElement.value === null || (segmentMode && id === oldWordId)) {
    return;
  }
  segmentMode = true;
  // Deselects both on the word and segment level since the previous selection mode could have been different
  deselect(oldWordId);
  deselect(oldSegmentId);

  // Add selection
  const word = getWordElement(id);
  // The found word should always have a parent element
  const segment = word.parentElement as HTMLElement;
  segment.classList.add(SELECTED_CLASS);
  oldWordId = id;
  oldSegmentId = segment.id;

  const segmentTopOffset = segment.offsetTop;
  const transcriptHeight = transcriptElement.value.clientHeight;
  const segmentHeight = segment.clientHeight;

  // Scroll distance that the segment is positioned at the bottom edge
  const segmentBottomOffset = segmentTopOffset + segmentHeight - transcriptHeight;
  // Scroll either to the bottom edge of the current segment or keep the
  // current word at the bottom if the segment is too long to be moved to the bottom
  // without the word being hidden. This way prior context stays in view, with
  // the entire segment being visible whenever possible
  transcriptElement.value.scrollTop =
    segmentHeight > transcriptHeight
      ? word.offsetTop + word.getBoundingClientRect().height - transcriptHeight
      : segmentBottomOffset;
}

/**
 * Selects the given word and highlights it
 *
 * @param {string} id - The ID of the word to select and highlight
 *
 * @return {HTMLElement} The HTML element of the newly selected word
 */
function selectWord(id: string): HTMLElement {
  segmentMode = false;
  // Deselects both on the segment and word level since the previous selection mode could have been different
  deselect(oldSegmentId);
  deselect(oldWordId);
  const word = getWordElement(id);
  word.classList.add(SELECTED_CLASS);
  oldWordId = id;
  return word;
}

/**
 * Scrolls the word with the given ID with positioning and highlighting dependent on the currently active `segmentMode`
 * If `segmentMode` is active, {@link scrollToSegmentByWordId} is called.
 * Otherwise, the chosen word is scrolled to the center of the transcript for maximum surrounding context and highlighted.
 *
 * @param {string} id - The ID of the word to either scroll to or highlight directly, or to do so in segment mode
 */
function scrollToElementById(id: string) {
  if (segmentMode) {
    scrollToSegmentByWordId(id);
    return;
  }

  // Doesn't scroll if the previous word Id and segment mode are the same to
  // avoid selecting the same word multiple times
  if (id === oldWordId) {
    return;
  }

  const word = selectWord(id);
  // Scroll the word to the middle of the container for maximum surrounding context
  transcriptElement.value.scrollTop =
    word.offsetTop - transcriptElement.value.clientHeight / 2 + word.getBoundingClientRect().height / 2;
}

// Switch between word and segment mode dynamically as soon as a video is played or paused
watch(
  () => props.videoPlaying,
  (playing) => {
    // Don't select anything if there was no previous selection to change
    if (oldWordId === null) {
      return;
    }

    if (!playing) {
      selectWord(oldWordId);
    } else if (playing) {
      // If a video has started to play this will only have a small impact since
      // next timeupdate event will also scroll to the nearest segment
      scrollToSegmentByWordId(oldWordId);
      clearTranscriptSelection(false);
    }
  },
);

// TODO: move to message store? chat available
const authRole = useAuthStore().getRole();
const exportDisabled = authRole !== undefined && authRole === "everybody";
const chatEnabled =
  authRole !== undefined &&
  (authRole === "admin" || authRole === "developer" || authRole === "lecturer" || authRole === "everybody");

const showOverlay = ref(false);
const overlayTop = ref(0);
const overlayLeft = ref(0);
const overlayWidth = ref(0);
const overlayHeight = ref(0);

const imageUrl = ref("/bootstrap-icons/arrow-down-circle-fill.svg"); // Provide the path to the original image
const hoverImageUrl = "/bootstrap-icons/x-circle.svg"; // Provide the path to the hover image

const handleMouseOverClearBtn = () => {
  imageUrl.value = hoverImageUrl;
};

const handleMouseLeaveClearBtn = () => {
  imageUrl.value = "/bootstrap-icons/arrow-down-circle-fill.svg"; // Reset to the original image on mouse leave
};

const handleMouseUpTranscript = () => {
  const selection = window.getSelection();
  if (selection && selection.toString().trim() !== "" && !props.videoPlaying && chatEnabled) {
    matomo_clicktracking(
      "select_transcript_text_for_llm_context",
      "Use selected transcript text as context for chat messages",
    );
    messageStore.setCurrentTranscriptSelection(selection.toString());
    const range = selection.getRangeAt(0);
    const boundingRect = range.getBoundingClientRect();
    const surroundingRect = transcriptElement.value.getBoundingClientRect();
    overlayTop.value = boundingRect.top - surroundingRect.top + transcriptElement.value.scrollTop - 5;
    overlayLeft.value = 5;
    overlayWidth.value = surroundingRect.width - (surroundingRect.width / 100.0) * 2;
    overlayHeight.value = boundingRect.height + 10;
    imageUrl.value = "/bootstrap-icons/arrow-down-circle-fill.svg";
    showOverlay.value = true;
  }
};

const clearTranscriptSelection = (clicked: boolean) => {
  if (clicked === true) {
    matomo_clicktracking(
      "clear_transcript_text_for_llm_context",
      "Clear selected transcript text as context for chat messages",
    );
  }
  messageStore.setCurrentTranscriptSelection("");
  showOverlay.value = false;
};

onMounted(() => {
  if (transcriptElement.value) {
    transcriptElement.value.addEventListener("scroll", handleScrollTranscript);
  }
});

onUnmounted(() => {
  if (transcriptElement.value) {
    transcriptElement.value.removeEventListener("scroll", handleScrollTranscript);
  }
});

const handleScrollTranscript = () => {
  if (props.videoPlaying) {
    clearTranscriptSelection(false);
  }
};

const decreaseFontSize = () => {
  if (transcriptElement.value) {
    const currentFontSize = parseFloat(window.getComputedStyle(transcriptElement.value).fontSize);
    if (currentFontSize > 6) {
      transcriptElement.value.style.fontSize = `${currentFontSize - 2}px`;
    }
  }
};

const increaseFontSize = () => {
  if (transcriptElement.value) {
    const currentFontSize = parseFloat(window.getComputedStyle(transcriptElement.value).fontSize);
    transcriptElement.value.style.fontSize = `${currentFontSize + 2}px`;
  }
};
</script>

<style scoped>
.transcript-container {
  padding-top: 10px;
}

.transcript {
  /* Relative positioning for offsetTop calculations */
  position: relative;
  height: 200px;
  padding: 10px;
  overflow-y: scroll;
  word-break: break-word;
  scroll-behavior: smooth;
}

.textitem:hover {
  background-color: var(--hans-medium-gray);
}

.textitem.selected {
  background-color: var(--hans-medium-blue);
}

.segment-words:hover {
  background-color: var(--hans-light-gray);
}

.segment-words.selected {
  background-color: var(--hans-light-blue);
}

.transcript-error {
  color: var(--hans-error);
  font-weight: bold;
}

.overlay {
  position: absolute;
  background-color: rgba(91, 152, 232, 0.4); /* Blue semi-transparent overlay */
  z-index: 2; /* Ensure the overlay is above other content */
  border: var(--bs-border-width) solid var(--bs-btn-border-color);
  border-radius: var(--bs-border-radius);
}

.clear-btn {
  position: relative;
  top: 0.1em;
  left: 97.9%;
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  height: 24px;
  width: 32px;
}

.clear-btn:hover {
  filter: invert(calc(var(--button-dark-mode, 0) - 0));
}

.font-size-btn {
  background-color: transparent;
  color: black;
  border-color: transparent;
  padding: 0.2em;
  left: 1em;
  top: -2px;
  position: relative;
}

.transcript-button-bar {
  display: block;
  padding-bottom: 0.5em;
  columns: 5;
}
</style>
