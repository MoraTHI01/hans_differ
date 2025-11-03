<template>
  <div class="wrapper">
    <draggable v-model="list" item-key="name" class="list" ghost-class="ghost" handle=".chapter" :move="checkMove">
      <template #item="{element}: {element: Block}">
        <div class="chapter-wrapper">
          <div v-if="element.chapter === true && element.draggable === true" class="chapter">
            <div class="grab">
              <img width="20" height="20" src="/bootstrap-icons/grip-vertical.svg" alt="grip" />
            </div>
            <span class="chapter-name">{{ t("TranscriptChapterSelection.topic") }}</span>
            <div class="actions">
              <button @click="addAbove(element)">
                <img width="16" height="16" src="/bootstrap-icons/plus.svg" alt="plus" />
                {{ t("TranscriptChapterSelection.addAbove") }}
              </button>
              <button @click="addBelow(element)">
                <img width="16" height="16" src="/bootstrap-icons/plus.svg" alt="plus" />
                {{ t("TranscriptChapterSelection.addBelow") }}
              </button>
              <button @click="remove(element)">
                <img width="18" height="18" src="/bootstrap-icons/trash.svg" alt="trash" />
                {{ t("TranscriptChapterSelection.deleteTopic") }}
              </button>
            </div>
          </div>
          <div v-else-if="element.chapter === true && element.draggable === false" class="chapter">
            <div class="grab">
              <img width="20" height="20" src="/bootstrap-icons/grip-vertical.svg" alt="grip" />
            </div>
            <span class="chapter-name">{{ t("TranscriptChapterSelection.topic") }}</span>
            <div class="actions">
              <button @click="addBelow(element)">
                <img width="16" height="16" src="/bootstrap-icons/plus.svg" alt="plus" />
                {{ t("TranscriptChapterSelection.addBelow") }}
              </button>
            </div>
          </div>
          <div v-else class="no-chapter">
            {{ element.text }}
          </div>
        </div>
      </template>
    </draggable>
    <div class="add-wrapper">
      <button class="add" @click="add(getPositionOfFirstVisible())">
        {{ t("TranscriptChapterSelection.addTopic") }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import draggable from "vuedraggable";
import type {Block} from "@/views/upload/UploadTranscript.vue";
import {useI18n} from "vue-i18n";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const {t} = useI18n({useScope: "global"});

const list = defineModel<Block[]>({required: true});

function getPositionOfFirstVisible() {
  const elements = document.querySelectorAll(".chapter-wrapper");
  for (let i = 1; i < elements.length; i++) {
    if (elements[i].getBoundingClientRect().top > 0) {
      return i;
    }
  }
  return 1;
}

function checkMove(evt) {
  // Prevent non draggable elements from moving
  // in our case the first element
  //console.log("checkMove")
  //console.log(evt.draggedContext.element)
  return evt.draggedContext.element.draggable === true;
}

function add(idx: number) {
  list.value.splice(idx > 0 ? idx : 0, 0, {chapter: true, chapterId: crypto.randomUUID(), draggable: true} as Block);
  matomo_clicktracking("click_button", `Added new chapter`);
}

function addAbove(elem: Block) {
  const idx = list.value.indexOf(elem) - 1;
  add(idx);
}

function addBelow(elem: Block) {
  const idx = list.value.indexOf(elem) + 2;
  add(idx);
}

function remove(elem: Block) {
  if (!elem.chapterId) return;
  list.value = list.value.filter((e: Block) => e.chapterId != elem.chapterId);
  matomo_clicktracking("click_button", `Removed chapter`);
}
</script>

<style scoped>
button {
  border: 0;
}

.no-chapter {
  margin-left: 0.25rem;
}

.wrapper {
  display: flex;
  flex-direction: column;
  padding: 2rem 2rem 1rem;
  gap: 1rem;
}

.add-wrapper {
  position: sticky;
  bottom: 76px;
  width: 100%;
  background-color: var(--hans-light);
  padding: 1rem 0;
}

@media (min-width: 539px) {
  .add-wrapper {
    bottom: 0px;
  }
}

.add {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
  padding: 0.5rem 0.75rem;
  border-radius: 0.25rem;
}

.add:hover {
  background-color: var(--hans-medium-blue);
}

.list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.chapter {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  scroll-margin-top: 1rem;
  border-left: 0.25rem solid var(--hans-dark-blue);
  background-color: var(--hans-light-gray);
  border-radius: 0.25rem;
}

.chapter .grab {
  background-color: var(--hans-medium-blue);
  display: flex;
  align-items: center;
  padding: 0.625rem 0.25rem;
}

.chapter-name {
  flex: 1;
}

.actions {
  display: flex;
  align-items: center;
}

.chapter:hover {
  background-color: var(--hans-medium-blue);
  color: var(--hans-light);
}

.actions > button:hover {
  color: var(--hans-light);
}

.actions > button:hover > img {
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}

.actions > button {
  padding: 0 1rem;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-right: 1px solid black;
  background-color: transparent;
}

.actions > button:last-child {
  border-right: none;
}

.actions > button:hover {
  text-decoration: underline;
}

.list > div:first-child .chapter {
  padding-top: 0;
}

.list > div:last-child .chapter {
  padding-bottom: 0;
}

.ghost {
  opacity: 0;
}
</style>
