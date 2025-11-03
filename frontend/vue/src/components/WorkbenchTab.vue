<template>
  <div class="tab-button">
    <button
      v-if="finished_loading"
      class="nav-link"
      :class="{active: props.active}"
      :id="id"
      data-bs-toggle="pill"
      :data-bs-target="databstarget"
      type="button"
      role="tab"
      :aria-controls="ariacontrols"
      aria-selected="true"
      style="position: relative"
      @click="$emit('switchTab', props.index)"
    >
      {{ tabheading }}<ButtonHint v-if="props.hint" route="generalnotes" :hovertext="hinttext" :hint_after="true" />
    </button>
    <input
      v-if="props.closeable"
      type="image"
      src="/bootstrap-icons/x-circle.svg"
      alt="Delete Button"
      id="delete-button"
      @click="$emit('deleteTab', {uuid: props.uuid, index: props.index})"
    />
  </div>
</template>

<script setup lang="ts">
import {computed, ref, watch} from "vue";
import ButtonHint from "@/components/ButtonHint.vue";
import type {TabHeading} from "@/common/tabHeading";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});

defineEmits<{
  (e: "deleteTab", event: {uuid: string; index: number}): void;
  (e: "switchTab", event: number): void;
}>();

const props = withDefaults(
  defineProps<{
    tabId: string;
    tabname?: string;
    tabheadings?: Array<TabHeading>;
    uuid: string;
    index: number;
    active: boolean;
    closeable?: boolean;
    hint?: boolean;
    hinttext?: string;
  }>(),
  {
    closeable: true,
    hint: false,
    hinttext: "",
  },
);

const id = computed(() => `pills-${props.tabId}-tab`);
const databstarget = computed(() => `#pills-${props.tabId}`);
const ariacontrols = computed(() => `pills-${props.tabId}`);

const finished_loading = ref(true);

function getHeadingText() {
  loggerService.log("getHeadingText");
  loggerService.log(props.tabheadings);
  for (const item in props.tabheadings) {
    const heading = props.tabheadings[item] as TabHeading;
    if (heading.language === locale.value) {
      return heading.name;
    }
  }
  return props.tabname === undefined ? props.tabId : props.tabname;
}

let tabheading = getHeadingText();

// Watch the locale to register for language changes and switch markers dep. on locale
watch(locale, async (newText) => {
  finished_loading.value = false;
  tabheading = getHeadingText();
  finished_loading.value = true;
});
</script>

<style scoped>
.tab-button {
  position: relative;
}

.nav-link {
  border: initial;
  border-bottom: 0.2em solid transparent;
}

.nav-link:hover {
  color: var(--hans-dark-blue);
  border-color: currentColor;
}

.nav-link.active:hover {
  color: inherit;
}

.nav-link:active:focus:hover {
  border-style: none;
}

.nav-link.active {
  border-color: currentColor;
}

#delete-button {
  position: absolute;
  width: 0.75em;
  top: 0.15em;
  right: 0.15em;
}

.nav-link,
.nav-link.active {
  background-color: transparent;
}
</style>
@/common/tabHeading
