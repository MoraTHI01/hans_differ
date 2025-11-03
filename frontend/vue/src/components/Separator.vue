<template>
  <div v-if="props.viewportWidth >= 768" class="separator" @mousedown="sepStartResize" @touchstart="sepStartResize">
    <div v-if="props.activeIndex == 0 && slideSyncActive === true">
      <button
        type="button"
        @click="toggleSlideSync()"
        class="btn btn-primary slide-link-mode"
        :title="slideSyncButtonTooltip"
      >
        <img src="/bootstrap-icons/link.svg" alt="api-btn" class="img-fluid img-slide-link-mode" />
      </button>
      <button
        type="button"
        @click="toggleLocalSwitchSlidesAndVideo()"
        class="btn btn-primary switch-slide-and-video"
        :title="t('Separator.tooltipSwitchSlidesAndVideoButton')"
      >
        <img src="/bootstrap-icons/arrow-left-right.svg" alt="api-btn" class="img-fluid img-switch-slide-and-video" />
      </button>
    </div>
    <div v-else-if="props.activeIndex == 0 && slideSyncActive === false">
      <button
        type="button"
        @click="toggleSlideSync()"
        class="btn btn-primary slide-link-mode-inactive"
        :title="slideSyncButtonTooltip"
      >
        <img
          src="/bootstrap-icons/unlink.svg"
          alt="slide synchronisation switch"
          class="img-fluid img-slide-link-mode-inactive"
        />
      </button>
      <button
        type="button"
        @click="toggleLocalSwitchSlidesAndVideo()"
        class="btn btn-primary switch-slide-and-video"
        :title="t('Separator.tooltipSwitchSlidesAndVideoButton')"
      >
        <img
          src="/bootstrap-icons/arrow-left-right.svg"
          alt="switch slides and video switch"
          class="img-fluid img-switch-slide-and-video"
        />
      </button>
    </div>
    <div v-if="props.activeIndex == 4 && chatStore.isSwitchVisionSnapshotEnabled">
      <button
        type="button"
        @click="takeSnapshot()"
        class="btn btn-primary btn-snapshot"
        :title="t('Separator.tooltipSnapshotButton')"
      >
        <img src="/bootstrap-icons/camera.svg" alt="video snapshot button" class="img-fluid img-snapshot" />
      </button>
    </div>
  </div>
  <div v-else class="separator-horizontal">
    <div v-if="props.activeIndex == 0 && slideSyncActive === true">
      <button
        type="button"
        @click="toggleSlideSync()"
        class="btn btn-primary slide-link-mode-horizontal"
        :title="slideSyncButtonTooltip"
      >
        <img src="/bootstrap-icons/link.svg" alt="api-btn" class="img-fluid img-slide-link-mode" />
      </button>
      <button
        type="button"
        @click="toggleLocalSwitchSlidesAndVideo()"
        class="btn btn-primary switch-slide-and-video-horizontal"
        :title="t('Separator.tooltipSwitchSlidesAndVideoButton')"
      >
        <img src="/bootstrap-icons/arrow-down-up.svg" alt="api-btn" class="img-fluid img-switch-slide-and-video" />
      </button>
    </div>
    <div v-else-if="props.activeIndex == 0 && slideSyncActive === false">
      <button
        type="button"
        @click="toggleSlideSync()"
        class="btn btn-primary slide-link-mode-inactive-horizontal"
        :title="slideSyncButtonTooltip"
      >
        <img src="/bootstrap-icons/unlink.svg" alt="api-btn" class="img-fluid img-slide-link-mode-inactive" />
      </button>
      <button
        type="button"
        @click="toggleLocalSwitchSlidesAndVideo()"
        class="btn btn-primary switch-slide-and-video-horizontal"
        :title="t('Separator.tooltipSwitchSlidesAndVideoButton')"
      >
        <img src="/bootstrap-icons/arrow-down-up.svg" alt="api-btn" class="img-fluid img-switch-slide-and-video" />
      </button>
    </div>
    <div v-if="props.activeIndex == 4 && chatStore.isSwitchVisionSnapshotEnabled">
      <button
        type="button"
        @click="takeSnapshot()"
        class="btn btn-primary btn-snapshot-horizontal"
        :title="t('Separator.tooltipSnapshotButton')"
      >
        <img src="/bootstrap-icons/camera.svg" alt="video snapshot button" class="img-fluid img-snapshot-horizontal" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import {defineProps, defineEmits, nextTick, ref, watch, onMounted} from "vue";
import {useI18n} from "vue-i18n";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";
import {useMediaStore} from "@/stores/media";
import {useChatStore} from "@/stores/chat";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const store = useMediaStore();
const chatStore = useChatStore();

const props = defineProps<{
  viewportWidth: number;
  activeIndex: number;
}>();

const emit = defineEmits(["startResizeBySeparator", "setSyncActiveSeparator", "takeVideoSnapshot"]);

const sepStartResize = (event: MouseEvent) => {
  emit("startResizeBySeparator", event);
};

const takeSnapshot = () => {
  loggerService.log("Separator:takeSnapshot:Start");
  matomo_clicktracking("click_button", "Take video snapshot");
  emit("takeVideoSnapshot");
  loggerService.log("Separator:takeSnapshot:Finished");
};

const slideSyncButtonTooltip = ref(t("Separator.tooltipSlideSyncButtonOn"));
const slideSyncActive = ref(true);
const currSwitchSlidesAndVideo = ref(store.getSwitchSlidesAndVideo());

const updateSlideSyncTooltip = () => {
  if (slideSyncActive.value === true) {
    slideSyncButtonTooltip.value = t("Separator.tooltipSlideSyncButtonOn");
  } else {
    slideSyncButtonTooltip.value = t("Separator.tooltipSlideSyncButtonOff");
  }
};

const toggleSlideSync = () => {
  slideSyncActive.value = !slideSyncActive.value;
  emit("setSyncActiveSeparator", slideSyncActive.value);
  updateSlideSyncTooltip();
  matomo_clicktracking("click_button", "Slide sync mode toggled");
};

const toggleLocalSwitchSlidesAndVideo = async () => {
  currSwitchSlidesAndVideo.value = !currSwitchSlidesAndVideo.value;
  matomo_clicktracking("click_button", "Switch slides and video toggled");
  store.setSwitchSlidesAndVideo(currSwitchSlidesAndVideo.value);
  matomo_clicktracking("click_button", "Use images as context with vllm, triggered by switch slide and video");
  chatStore.toggleSwitchVision(true);
  chatStore.storeChatSettings();
  //router.push(router.currentRoute.value);
  nextTick(() => {
    window.location.reload();
  });
};

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {
  updateSlideSyncTooltip();
});
</script>
<style scoped>
.separator {
  cursor: col-resize;
  width: 10px;
  background-color: #f1f1f1;
  /* Set a wider separator for touch devices */
  @media (pointer: coarse) {
    width: 20px;
  }
  touch-action: none; /* Disable browser touch gestures to allow proper touch handling */
}

.separator-horizontal {
  top: 15px;
  height: 10px;
  background-color: #f1f1f1;
  touch-action: none;
  position: relative;
  padding: 1em;
}

.img-switch-slide-and-video {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  width: 72%;
  height: 72%;
  position: absolute;
  left: 15%;
  top: 10%;
}

.img-slide-link-mode {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  width: 72%;
  height: 72%;
  position: absolute;
  left: 15%;
  top: 10%;
}

.img-slide-link-mode-inactive {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  width: 72%;
  height: 72%;
  position: absolute;
  left: 15%;
  top: 10%;
}

.switch-slide-and-video {
  color: var(--hans-light);
  border-radius: 24px;
  position: absolute;
  top: 45%;
  height: 24px;
  width: 12px;
  box-sizing: content-box;
  transform: translate(-36%, -40%);
}

.switch-slide-and-video-horizontal {
  color: var(--hans-light);
  border-radius: 24px;
  position: absolute;
  top: 0.75em;
  height: 24px;
  width: 12px;
  box-sizing: content-box;
  transform: translate(-36%, -40%);
  left: 40%;
}

.slide-link-mode {
  color: var(--hans-light);
  border-radius: 24px;
  position: absolute;
  top: 55%;
  height: 24px;
  width: 12px;
  box-sizing: content-box;
  transform: translate(-36%, -40%);
}

.slide-link-mode-horizontal {
  color: var(--hans-light);
  border-radius: 24px;
  position: absolute;
  top: 0.75em;
  height: 24px;
  width: 12px;
  box-sizing: content-box;
  transform: translate(-36%, -40%);
  left: 55%;
}

.slide-link-mode-inactive {
  color: var(--hans-light);
  border-radius: 24px;
  position: absolute;
  top: 55%;
  height: 24px;
  width: 12px;
  box-sizing: content-box;
  transform: translate(-36%, -40%);
}

.slide-link-mode-inactive-horizontal {
  color: var(--hans-light);
  border-radius: 24px;
  position: absolute;
  top: 0.75em;
  height: 24px;
  width: 12px;
  box-sizing: content-box;
  transform: translate(-36%, -40%);
  left: 55%;
}

.slide-link-mode:hover > .img-slide-link-mode {
  filter: invert(calc(var(--button-dark-mode, 0) - 0));
}

.btn-snapshot {
  color: var(--hans-light);
  border-radius: 24px;
  position: absolute;
  top: 45%;
  height: 24px;
  width: 12px;
  box-sizing: content-box;
  transform: translate(-36%, -40%);
}

.btn-snapshot-horizontal {
  color: var(--hans-light);
  border-radius: 24px;
  position: absolute;
  top: 0.75em;
  height: 24px;
  width: 12px;
  box-sizing: content-box;
  transform: translate(-36%, -40%);
  left: 45%;
}

.img-snapshot {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  width: 72%;
  height: 72%;
  position: absolute;
  left: 15%;
  top: 10%;
}

.img-snapshot-horizontal {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  width: 72%;
  height: 72%;
  position: absolute;
  left: 15%;
  top: 10%;
}
</style>
