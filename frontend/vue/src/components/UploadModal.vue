<template>
  <div class="modal fade" tabindex="-1" role="dialog" :class="{show: enabled}">
    <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">{{ props.title }}</h1>
          <button type="button" class="btn-close modal-close" @click="enabled = false" aria-label="schließen"></button>
        </div>
        <div class="modal-body">
          <p>{{ props.content }}</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="enabled = false">{{ t("UploadModal.close") }}</button>
          <button type="button" class="btn btn-danger" @click="submit">{{ t("UploadModal.confirm") }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, watch, defineProps, defineEmits} from "vue";
import {useI18n} from "vue-i18n";

const {t} = useI18n({useScope: "global"});
const enabled = defineModel<boolean>({required: true});

const props = defineProps<{
  title: string;
  content: string;
  modelValue: boolean;
}>();

// Define emits
const emit = defineEmits<{
  (event: "submit"): void;
}>();

function submit() {
  emit("submit");
  enabled.value = false;
}
</script>

<style scoped>
.modal-header {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
}
.modal-title {
  color: var(--hans-light);
}
.modal.show {
  background-color: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  display: block;
}
.modal-close {
  color: var(--hans-light);
  filter: invert(calc(1 - var(--button-dark-mode, 0)));
}
</style>
