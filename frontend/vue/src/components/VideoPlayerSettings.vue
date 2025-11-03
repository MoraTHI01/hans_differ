<template>
  <div id="videoPlayerSettingsContainer" class="vjs-menu container player-settings-container">
    <div class="col-12">
      <ul class="vjs-menu-content" role="menu">
        <li class="vjs-menu-item" tabindex="-1" role="menuitem" aria-disabled="false" @click="displayPlayerInfo">
          <div class="col-3">
            <img
              src="/bootstrap-icons/info-circle-fill.svg"
              alt="info"
              class="img-fluid img-info"
              style="filter: invert(1)"
            />
          </div>
          <div class="col-4">
            <span class="vjs-menu-item-text fw-bold">{{ infoMenuName }}</span>
          </div>
          <div class="col-5">
            <span class="vjs-menu-item-text">&nbsp;</span>
          </div>
        </li>
        <li class="vjs-menu-item" tabindex="-1" role="menuitem" aria-disabled="true">
          <div class="col-3">
            <img
              src="/bootstrap-icons/sliders2.svg"
              alt="quality"
              class="img-fluid img-info"
              style="filter: invert(1)"
            />
          </div>
          <div class="col-4">
            <span class="vjs-menu-item-text fw-bold">{{ qualityMenuName }}</span>
          </div>
          <div class="col-5">
            <span class="vjs-menu-item-text">{{ currRes }}</span>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import {defineProps, ref, watch} from "vue";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();

const props = defineProps<{
  playerInstance: any;
  playerInfoInstanceRef: any;
  t: any;
  locale: any;
  streamType: any;
}>();

const qualityLevels = props.playerInstance.qualityLevels();
const currRes = ref("Auto");
const infoMenuName = ref(props.t("VideoPlayerSettings.controlBarInfoMenu"));
const qualityMenuName = ref(props.t("VideoPlayerSettings.controlBarQualityMenu"));

// Listen to change events when the player selects a new quality level
qualityLevels.on("change", () => {
  loggerService.log("Quality Level changed!");
  const currQualityLevels = props.playerInstance.qualityLevels();
  const currQual = currQualityLevels[currQualityLevels.selectedIndex];
  loggerService.log(currQual);
  if (props.playerInfoInstanceRef.value && props.playerInfoInstanceRef.value.isPlayerInfoDisplayed()) {
    props.playerInfoInstanceRef.value.updateQualityLevel(currQual);
  }
  currRes.value = "Auto (" + currQual.height.toString() + "p)";
});

const displayPlayerInfo = () => {
  loggerService.log("VideoPlayerSettings:displayPlayerInfo");
  const currQualityLevels = props.playerInstance.qualityLevels();
  props.playerInfoInstanceRef.value.updateQualityLevel(
    currQualityLevels[currQualityLevels.selectedIndex],
    props.streamType,
  );
  props.playerInfoInstanceRef.value.updateStats(props.playerInstance.tech().vhs.stats);
  props.playerInfoInstanceRef.value.playerInfoOpenModal();
};

watch(props.locale, async (newText) => {
  infoMenuName.value = props.t("VideoPlayerSettings.controlBarInfoMenu");
  qualityMenuName.value = props.t("VideoPlayerSettings.controlBarQualityMenu");
});
</script>

<style scoped>
.player-settings-container {
  width: 18em;
  left: -12em;
}
</style>
