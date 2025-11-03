<template>
  <!-- VideoPlayerInfo -->
  <div class="modal fade" tabindex="-1" role="dialog" ref="infoModal">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">{{ t("VideoPlayerInfo.title") }}</h1>
          <button
            type="button"
            class="btn-close modal-close"
            @click="closeModal"
            :aria-label="t('VideoPlayerInfo.closeButton')"
          ></button>
        </div>
        <div class="modal-body">
          <div class="ms-2 me-auto">
            <div class="fw-bold">
              <p>
                {{ t("VideoPlayerInfo.text") }} <br />
                <a
                  v-if="streamType === 'dash'"
                  class="link-text"
                  href="https://videojs.github.io/videojs-contrib-dash"
                  target="_blank"
                  >{{ t("VideoPlayerInfo.testDASH") }}</a
                >
                <a
                  v-if="streamType === 'hls'"
                  class="link-text"
                  href="https://videojs.github.io/videojs-contrib-hls"
                  target="_blank"
                  >{{ t("VideoPlayerInfo.testHLS") }}</a
                >
              </p>
            </div>
          </div>
          <div v-if="quality && qualityUpdated">
            <div class="ms-2 me-auto">
              <div class="fw-bold">
                <p>Video</p>
              </div>
              <p>
                {{ streamType }}
              </p>
              <p>
                {{ quality.width }} x {{ quality.height }}, {{ quality.height }} p, {{ quality.frameRate }} FPS,
                {{ (quality.bitrate / 1000000).toFixed(2) }} Mbps
              </p>
            </div>
          </div>
          <div v-if="stats && statsUpdated">
            <!-- https://github.com/videojs/http-streaming?tab=readme-ov-file#vhsstats -->
            <div class="ms-2 me-auto">
              <div class="fw-bold">
                <p>
                  {{ t("VideoPlayerInfo.statistics") }}
                </p>
              </div>
            </div>
            <ol class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                  <div class="fw-bold">{{ t("VideoPlayerInfo.bandwidth") }}</div>
                  <p>{{ (stats.bandwidth / 1000000).toFixed(2) }} Mbps</p>
                </div>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                  <div class="fw-bold">{{ t("VideoPlayerInfo.currentTime") }}</div>
                  <p>
                    {{ stats.currentTime }}
                  </p>
                </div>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                  <div class="fw-bold">{{ t("VideoPlayerInfo.duration") }}</div>
                  <p>
                    {{ stats.duration }}
                  </p>
                </div>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                  <div class="fw-bold">{{ t("VideoPlayerInfo.mediaRequests") }}</div>
                  <p>
                    {{ stats.mediaRequests }}
                  </p>
                </div>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                  <div class="fw-bold">{{ t("VideoPlayerInfo.mediaRequestsAborted") }}</div>
                  <p>
                    {{ stats.mediaRequestsAborted }}
                  </p>
                </div>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                  <div class="fw-bold">{{ t("VideoPlayerInfo.mediaRequestsErrored") }}</div>
                  <p>
                    {{ stats.mediaRequestsErrored }}
                  </p>
                </div>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                  <div class="fw-bold">{{ t("VideoPlayerInfo.mediaRequestsTimedout") }}</div>
                  <p>
                    {{ stats.mediaRequestsTimedout }}
                  </p>
                </div>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                  <div class="fw-bold">
                    <a class="link-text" href="https://w3c.github.io/media-playback-quality" target="_blank">{{
                      t("VideoPlayerInfo.playbackQuality")
                    }}</a>
                  </div>
                  <ol class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                      <div class="ms-2 me-auto">
                        <div class="fw-bold">{{ t("VideoPlayerInfo.creationTime") }}</div>
                        <p>
                          {{ stats.videoPlaybackQuality.creationTime }}
                        </p>
                      </div>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                      <div class="ms-2 me-auto">
                        <div class="fw-bold">{{ t("VideoPlayerInfo.totalVideoFrames") }}</div>
                        <p>
                          {{ stats.videoPlaybackQuality.totalVideoFrames }}
                        </p>
                      </div>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                      <div class="ms-2 me-auto">
                        <div class="fw-bold">{{ t("VideoPlayerInfo.droppedVideoFrames") }}</div>
                        <p>
                          {{ stats.videoPlaybackQuality.droppedVideoFrames }}
                        </p>
                      </div>
                    </li>
                  </ol>
                </div>
              </li>
            </ol>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" @click="closeModal">
            {{ t("VideoPlayerInfo.closeButton") }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <!-- VideoPlayerInfo end -->
</template>

<script setup lang="ts">
import {defineExpose, ref, watch} from "vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

const infoModal = ref(null);
const quality = ref(null);
const qualityUpdated = ref(false);
const stats = ref();
const statsUpdated = ref(false);
const displayed = ref(false);
const streamType = ref("");

const updateQualityLevel = (m_qualitylevel, m_streamType) => {
  loggerService.log("VideoPlayerInfo:updateQualityLevel");
  loggerService.log(m_qualitylevel);
  qualityUpdated.value = false;
  quality.value = m_qualitylevel;
  qualityUpdated.value = true;
  streamType.value = m_streamType;
};

const updateStats = (m_stats) => {
  loggerService.log("VideoPlayerInfo:updateStats");
  loggerService.log(m_stats);
  statsUpdated.value = false;
  stats.value = m_stats;
  statsUpdated.value = true;
};

const playerInfoOpenModal = () => {
  if (infoModal.value) {
    loggerService.log("VideoPlayerInfo:Open");
    infoModal.value.classList.add("show");
    infoModal.value.style.display = "block";
    matomo_clicktracking("click_button", "Show video player info");
    displayed.value = true;
  }
};

const closeModal = () => {
  if (infoModal.value) {
    loggerService.log("VideoPlayerInfo:Close");
    infoModal.value.classList.remove("show");
    infoModal.value.style.display = "none";
    matomo_clicktracking("click_button", "Close video player info");
    displayed.value = false;
  }
};

const isPlayerInfoDisplayed = () => {
  return displayed.value;
};

defineExpose({
  updateQualityLevel,
  updateStats,
  playerInfoOpenModal,
  isPlayerInfoDisplayed,
});
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
