<template>
  <!-- ChatContextWindow -->
  <div v-if="props.isUser === false && props.useContext === true">
    <button
      :class="['btn', 'btn-primary', 'btn-sm', props.cssClass, 'stack-button']"
      :title="t('ChatContextWindow.tooltipContextButton')"
      @click="openModal"
    >
      <img
        :id="props.indexSuffix + '_CWStackButton_' + props.index"
        src="/bootstrap-icons/stack.svg"
        alt="api-btn"
        class="img-fluid stack-img"
      />
    </button>
    <div class="modal fade" tabindex="-1" role="dialog" ref="myModal">
      <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5">{{ t("ChatContextWindow.title") }}</h1>
            <button
              type="button"
              class="btn-close modal-close"
              @click="closeModal"
              :aria-label="t('ChatContextWindow.closeButton')"
            ></button>
          </div>
          <div class="modal-body">
            <!-- Bootstrap Tabs for switching between contextList and contextListSlides -->
            <ul class="nav nav-tabs" :id="props.indexSuffix + '_ContextTab_' + props.index" role="tablist">
              <li class="nav-item" role="presentation">
                <button
                  class="nav-link active"
                  :id="props.indexSuffix + '_ContextTranscriptTab_' + props.index"
                  data-bs-toggle="tab"
                  :data-bs-target="'#' + props.indexSuffix + '_ContextTranscriptContent_' + props.index"
                  type="button"
                  role="tab"
                  :aria-controls="props.indexSuffix + '_ContextTranscriptContent_' + props.index"
                  aria-selected="true"
                >
                  {{ t("ChatContextWindow.transcript") }}
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button
                  class="nav-link"
                  :id="props.indexSuffix + '_ContextSlidesTab_' + props.index"
                  data-bs-toggle="tab"
                  :data-bs-target="'#' + props.indexSuffix + '_ContextSlidesContent_' + props.index"
                  type="button"
                  role="tab"
                  :aria-controls="props.indexSuffix + '_ContextSlidesContent_' + props.index"
                  aria-selected="false"
                >
                  {{ t("ChatContextWindow.slides") }}
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button
                  class="nav-link"
                  :id="props.indexSuffix + '_ContextSnapshotsTab_' + props.index"
                  data-bs-toggle="tab"
                  :data-bs-target="'#' + props.indexSuffix + '_ContextSnapshotsContent_' + props.index"
                  type="button"
                  role="tab"
                  :aria-controls="props.indexSuffix + '_ContextSnapshotsContent_' + props.index"
                  aria-selected="false"
                >
                  {{ t("ChatContextWindow.snapshots") }}
                </button>
              </li>
            </ul>
            <!-- Tab Content -->
            <div class="tab-content mt-3" :id="props.indexSuffix + '_ContextTabContent_' + props.index">
              <!-- First Tab: Context List -->
              <div
                class="tab-pane fade show active"
                :id="props.indexSuffix + '_ContextTranscriptContent_' + props.index"
                role="tabpanel"
                :aria-labelledby="props.indexSuffix + '_ContextTranscriptTab_' + props.index"
              >
                <div v-if="contextList.size > 0">
                  <ol class="list-group list-group-flush">
                    <template v-for="(item, index) in contextList" :key="index">
                      <li class="list-group-item d-flex justify-content-between align-items-start">
                        <div class="ms-2 me-auto">
                          <div class="fw-bold">{{ item[0] }}</div>
                          <p>{{ item[1] }}</p>
                        </div>
                      </li>
                    </template>
                  </ol>
                </div>
                <div v-else>
                  <ol class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                      <div class="ms-2 me-auto">
                        {{ t("ChatContextWindow.transcriptContextEmpty") }}
                      </div>
                    </li>
                  </ol>
                </div>
              </div>
              <!-- Second Tab: Slides -->
              <div
                class="tab-pane fade"
                :id="props.indexSuffix + '_ContextSlidesContent_' + props.index"
                role="tabpanel"
                :aria-labelledby="props.indexSuffix + '_ContextSlidesTab_' + props.index"
              >
                <div v-if="contextListSlides.size > 0">
                  <ol class="list-group list-group-flush">
                    <template v-for="(slide, index) in contextListSlides" :key="index">
                      <li class="list-group-item d-flex justify-content-between align-items-start">
                        <div class="ms-2 me-auto">
                          <div class="fw-bold">{{ t("ChatContextWindow.slide") }} {{ slide[0] }}</div>
                          <img :src="slide[1]" alt="Slide Image" class="img-fluid mt-2" />
                        </div>
                      </li>
                    </template>
                  </ol>
                </div>
                <div v-else>
                  <ol class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                      <div class="ms-2 me-auto">
                        {{ t("ChatContextWindow.slideContextEmpty") }}
                      </div>
                    </li>
                  </ol>
                </div>
              </div>
              <!-- Third Tab: Slides -->
              <div
                class="tab-pane fade"
                :id="props.indexSuffix + '_ContextSnapshotsContent_' + props.index"
                role="tabpanel"
                :aria-labelledby="props.indexSuffix + '_ContextSnapshotsTab_' + props.index"
              >
                <div v-if="contextListSnapshots.size > 0">
                  <ol class="list-group list-group-flush">
                    <template v-for="(snapshot, index) in contextListSnapshots" :key="index">
                      <li class="list-group-item d-flex justify-content-between align-items-start">
                        <div class="ms-2 me-auto">
                          <div class="fw-bold">{{ t("ChatContextWindow.snapshot") }} {{ snapshot[0] }}</div>
                          <img :src="snapshot[1]" alt="Snapshot Image" class="img-fluid mt-2" />
                        </div>
                      </li>
                    </template>
                  </ol>
                </div>
                <div v-else>
                  <ol class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                      <div class="ms-2 me-auto">
                        {{ t("ChatContextWindow.snapshotContextEmpty") }}
                      </div>
                    </li>
                  </ol>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" @click="closeModal">
              {{ t("ChatContextWindow.closeButton") }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- ChatContextWindow end -->
</template>

<script setup lang="ts">
import {ref} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {useMediaStore} from "@/stores/media";
import {apiClient} from "@/common/apiClient";
import {useMessageStore} from "@/stores/message";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const props = defineProps<{
  isUser: boolean;
  context: string;
  contextUuid: string;
  useContext: boolean;
  cssClass: string;
  index: number;
  indexSuffix: string;
  videoUuid: string;
}>();

const mediaStore = useMediaStore();
const contextList = ref(new Map<string, string>());
const contextListSlides = ref(new Map<string, string>());
const contextListSnapshots = ref(new Map<string, string>());

const parseContext = async () => {
  loggerService.log("ContextWindow:parseContext");
  const currContextArr = props.context.split("\\n");
  loggerService.log(currContextArr);
  currContextArr.forEach((contextItem) => {
    if (contextItem !== "") {
      const currContextItem = contextItem.trim();
      loggerService.log(currContextItem);
      const regex = /(\[[0-9]+\])/g; // Add 'g' flag for global matching
      const match = regex.exec(currContextItem);
      loggerService.log(match);
      if (match !== null) {
        // The captured citation, e.g., "[0]", "[1]", "[2]", "[3]"
        // for slides the ids are starting with "[100]", "[101]", "[102]", "[103]"
        const citation = match[1];
        loggerService.log(citation);
        const citationId = citation.replace("[", "").replace("]", "");
        const citationIndex = parseInt(citationId, 10);
        loggerService.log(citationIndex);
        const splitQuote = "- " + citation;
        const contextArr = currContextItem.split(splitQuote);
        loggerService.log(contextArr);
        if (contextArr !== undefined && contextArr.length > 0) {
          const hoverContextTextEnOrig = contextArr[1].trim();
          let hoverContextText = hoverContextTextEnOrig;
          if (citationIndex < 100) {
            // Cite transcript
            if (locale.value === "de") {
              const intervalEn = mediaStore.getIntervalFromCurrentTranscriptText("en", hoverContextTextEnOrig);
              hoverContextText = mediaStore.getCurrentTranscriptTextInInterval("de", intervalEn);
            }
            if (!contextList.value.has(citation)) {
              contextList.value.set(citation, hoverContextText);
            }
          } else if (citationIndex > 99 && citationIndex < 999) {
            // Cite slides
            const slide_number = (citationIndex - 100).toString();
            const uri = mediaStore.getSlidesImagesFolderUrnByUuid(props.videoUuid) + "/" + slide_number + ".png";
            loggerService.log(`ChatContextWindow:SlideContextUrnFirstPass: ${uri}`);
            if (!contextListSlides.value.has(slide_number)) {
              contextListSlides.value.set(slide_number, uri);
            }
          } else {
            // Cite snapshot
            const snapshot_number = (citationIndex - 999).toString();
            const uri = useMessageStore().getVideoSnapshot;
            loggerService.log(`ChatContextWindow:SnapshotContextUrn: ${uri}`);
            if (!contextListSnapshots.value.has(snapshot_number)) {
              contextListSnapshots.value.set(snapshot_number, uri);
            }
          }
        }
      }
    }
  });
  for (const [slideNumber, imageUrn] of contextListSlides.value) {
    loggerService.log(`Processing slide: ${slideNumber}`);
    loggerService.log(`ChatContextWindow:SlideContextUrnSecondPass: ${imageUrn}`);
    if (imageUrn?.length > 0 && !imageUrn.includes("http")) {
      const {data} = await apiClient.get("/getThumbnail?urn=" + imageUrn);
      if ("data" in data && Object.keys(data.data).length > 0) {
        loggerService.log(`ChatContextWindow:SlideContextUrl: ${data.data}`);
        contextListSlides.value.set(slideNumber, data.data);
      } else {
        loggerService.error("Error fetching slide image url from urn!");
      }
    } else {
      loggerService.log("Warning: imageUrn is empty or already loaded and an url.");
    }
  }
};

const myModal = ref(null);

const openModal = async () => {
  if (myModal.value) {
    loggerService.log("ContextWindow:Open");
    await parseContext();
    myModal.value.classList.add("show");
    myModal.value.style.display = "block";
    matomo_clicktracking("click_button", "Show message context");
  }
};

const closeModal = () => {
  if (myModal.value) {
    loggerService.log("ContextWindow:Close");
    myModal.value.classList.remove("show");
    myModal.value.style.display = "none";
    matomo_clicktracking("click_button", "Close message context");
  }
};
</script>

<style scoped>
.stack-button {
  float: right;
  border-radius: 15px;
  width: 48px;
  height: 32px;
  margin-bottom: 1vw;
}
.stack-img {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  width: 24px;
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
