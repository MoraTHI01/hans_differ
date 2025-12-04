<template>
  <!-- LayoutOptions -->
  <button
    id="btnGroupDrop2"
    type="button"
    class="btn btn-primary form-control option-toggle"
    data-bs-toggle="dropdown"
    aria-expanded="false"
    :disabled="false"
  >
    <span class="layout-text">{{ t("LayoutOptions.view") }}</span>
    <img :src="layoutImg" alt="api-btn" class="img-fluid layout-active-img" />
  </button>
  <ul class="dropdown-menu btn-container" aria-labelledby="btnGroupDrop2">
    <li>
      <a class="dropdown-item" href="#" @click="setActiveLayout('combined')"
        ><img src="/bootstrap-icons/grid-1x2-rotated.svg" alt="api-btn" class="img-fluid layout-img" />{{
          t("LayoutOptions.combined")
        }}</a
      >
    </li>
    <li v-if="!props.channelmode">
      <a class="dropdown-item" href="#" @click="setActiveLayout('transcript')"
        ><img src="/bootstrap-icons/card-text.svg" alt="api-btn" class="img-fluid layout-img" />{{
          t("LayoutOptions.transcript")
        }}</a
      >
    </li>
    <li v-if="!props.channelmode">
      <a class="dropdown-item" href="#" @click="setActiveLayout('slides')"
        ><img src="/bootstrap-icons/file-earmark-slides.svg" alt="api-btn" class="img-fluid layout-img" />{{
          t("LayoutOptions.slides")
        }}</a
      >
    </li>
    <li v-if="!props.channelmode">
      <a class="dropdown-item" href="#" @click="setActiveLayout('player')"
        ><img src="/bootstrap-icons/play-btn.svg" alt="api-btn" class="img-fluid layout-img" />{{
          t("LayoutOptions.player")
        }}</a
      >
    </li>
    <li v-if="!props.channelmode">
      <a class="dropdown-item" href="#" @click="setActiveLayout('questionnaire')"
        ><img src="/bootstrap-icons/question-circle.svg" alt="api-btn" class="img-fluid layout-img" />{{
          t("LayoutOptions.questionnaire")
        }}</a
      >
    </li>
    <li>
      <a class="dropdown-item" href="#" @click="setActiveLayout('chat')"
        ><img src="/bootstrap-icons/chat.svg" alt="api-btn" class="img-fluid layout-img" />{{
          t("LayoutOptions.chat")
        }}</a
      >
    </li>
  </ul>
  <!-- LayoutOptions end -->
</template>

<script setup lang="ts">
import {defineProps, ref, watch, onMounted} from "vue";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {useLayoutStore} from "@/stores/layout";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const layoutStore = useLayoutStore();

const props = defineProps<{
  channelmode: boolean;
}>();

const layoutImg = ref("/bootstrap-icons/grid-1x2-rotated.svg");

const setActiveLayout = (val) => {
  loggerService.log("Set active layout");
  layoutStore.setLayout(val);
  updateLayoutImg();
};

const updateLayoutImg = () => {
  loggerService.log("Update active layout image");
  const layoutname = layoutStore.getLayout;
  switch (layoutname) {
    case "combined":
      layoutImg.value = "/bootstrap-icons/grid-1x2-rotated.svg";
      break;
    case "transcript":
      layoutImg.value = "/bootstrap-icons/card-text.svg";
      break;
    case "slides":
      layoutImg.value = "/bootstrap-icons/file-earmark-slides.svg";
      break;
    case "player":
      layoutImg.value = "/bootstrap-icons/play-btn.svg";
      break;
    case "questionnaire":
      layoutImg.value = "/bootstrap-icons/question-circle.svg";
      break;
    case "chat":
      layoutImg.value = "/bootstrap-icons/chat.svg";
      break;
    default:
      layoutImg.value = "/bootstrap-icons/grid-1x2-rotated.svg";
      break;
  }
};

onMounted(() => {
  updateLayoutImg();
});

// Watch the locale to register for language changes
watch(locale, async (newText) => {});
</script>
<style scoped>
.option-toggle {
  border-radius: 25px;
  width: fit-content;
  height: fit-content;
  margin-left: auto;
}
.dropdown-item {
  border-radius: 25px;
  padding-inline: 2em;
  margin-top: 0.4vh;
}
.btn-container {
  color: var(--hans-light);
  padding: 5px;
  border-radius: 25px;
}
.btn-container:hover {
  color: var(--hans-dark);
  background-color: var(--hans-light);
}
.layout-img {
  filter: invert(calc(var(--button-light-mode, 0) - 0));
  height: 24px;
  width: 32px;
}
.layout-active-img {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
  height: 24px;
  width: 32px;
}
.layout-text {
  padding-right: 0.5em;
}
@media (max-width: 600px) {
  .layout-text {
    display: none;
  }
  .layout-img {
    font-size: 20px; /* Adjust icon size */
  }
  .layout-active-img {
    font-size: 20px; /* Adjust icon size */
  }
}
</style>
