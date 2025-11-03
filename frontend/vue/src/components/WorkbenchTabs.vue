<template>
  <div class="nav nav-tabs" role="tablist">
    <!-- loop over the tabsmap, the syntax unpacks the map in key and value, the value is a object which is destructured -->
    <WorkbenchTab
      v-for="([uuid, {tabname, tabheadings, tabId, closeable, hint, hinttext}], index) in props.tabsmap"
      :tabname="tabname"
      :tabheadings="tabheadings"
      :tab-id="tabId"
      :uuid="uuid"
      :closeable="closeable"
      :hint="hint"
      :hinttext="hinttext"
      :index="index"
      :active="active === index"
      @delete-tab="$emit('deleteTab', $event)"
      @switch-tab="switchTab"
      :key="index"
    />
  </div>
</template>

<script lang="ts">
/**
 * A single named tab with an optional id to separate tabs into different
 * categories such as, e.g., search results and slide tabs.
 * Both closeable and not manually closeable tabs are supported.
 */
export class Tab {
  tabId: string;
  tabname: string;
  tabheadings: Array<TabHeading>;
  closeable: boolean;
  hint: boolean;
  hinttext: string;

  /**
   * Constructs a new tab from a name, an optional separate ID and a boolean indicating whether it's closeable
   *
   * @param {string} tabname - The name used for indexing
   * @param {Array<TabHeading>} tabheadings - The names to be displayed in the tab bar
   * @param {string?} tabId - An optional tab ID to use as a unique identifier.
   *                          If no tab ID is provided, `tabname` is used as the ID.
   *                          This is only recommended, if there is only one tab category to avoid naming conflicts.
   * @param {boolean} closeable - If true, tabs can be manually closed by the user
   * @param {boolean} hint - If true, add asterix hint
   * @param {boolean} hinttext - Add hint text to be shown on hovering of the ButtonHint
   */
  constructor(
    tabname: string,
    tabheadings: Array<TabHeading>,
    tabId?: string,
    closeable: boolean = true,
    hint: boolean = false,
    hinttext: string = "",
  ) {
    this.tabId = tabId === undefined ? tabname : tabId;
    this.tabname = tabname;
    this.tabheadings =
      tabheadings === undefined
        ? [
            new TabHeading(tabname === undefined ? tabId : tabname, "de"),
            new TabHeading(tabname === undefined ? tabId : tabname, "en"),
          ]
        : tabheadings;
    this.closeable = closeable;
    this.hint = hint;
    this.hinttext = hinttext;
  }

  /**
   * Convenience function for creating a new (optionally closeable) tab with a custom ID from a tab name and a category
   *
   * @param {string} tabname - The name used for indexing
   * @param {Array<TabHeading>} tabheadings - The names to be displayed in the tab bar
   * @param {string} tabType - The category the given tab belongs to which acts as a namespace for the ID to avoid naming conflicts
   * @param {boolean} closeable - If true, tabs can be manually closed by the user
   * @param {boolean} hint - If true, add asterix hint
   * @param {boolean} hinttext - Add hint text to be shown on hovering of the ButtonHint
   *
   * @return {Tab} The newly constructed tab with a unique id based on the tab name and the tab type
   */
  static withType(
    tabname: string,
    tabheadings: Array<TabHeading>,
    tabType: string,
    closeable: boolean = true,
    hint: boolean = false,
    hinttext: string = "",
  ): Tab {
    return new Tab(tabname, tabheadings, `${tabType}-${tabname}`, closeable, hint, hinttext);
  }
}
</script>

<script setup lang="ts">
import {ref, watch} from "vue";
import WorkbenchTab from "@/components/WorkbenchTab.vue";
import {TabHeading} from "@/common/tabHeading";

const emit = defineEmits<{
  (e: "deleteTab", event: {uuid: string; index: number}): void;
  (e: "switchTab", event: number): void;
}>();

const props = defineProps<{
  tabsmap: Map<string, Tab>;
}>();

const active = ref(0);

watch(props.tabsmap, (tabsmap) => {
  // If the currently active index is out of range for the new tabsmap,
  // move it back to the new last index
  const lastIndex = tabsmap.size - 1;
  if (active.value > lastIndex) {
    active.value = lastIndex;
    emit("switchTab", active.value);
  }
});

/**
 * Switches to a new tab and emits a `switchTab` event
 *
 * @param {number} index - index of the tab to switch to
 */
function switchTab(index: number) {
  active.value = index;
  emit("switchTab", index);
}

defineExpose({
  /**
   * Switches to a new tab and emits a `switchTab` event.
   * If the provided index is out of range, an error is raised instead.
   *
   * @param {number} index - index of the tab to switch to
   */
  switchTo(index: number) {
    if (index < 0 || index > props.tabsmap.size) {
      throw Error(`Tab index out of range: ${index}, should be in [0,${props.tabsmap.size}]`);
    }
    switchTab(index);
  },
});
</script>

<style scoped></style>
