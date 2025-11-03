<template>
  <div class="links">
    <button
      class="previous"
      v-if="step !== 1"
      :disabled="loading == true || disableNav == true"
      @click="router.push(`/upload/${step - 1}?uuid=${uuid}`)"
    >
      {{ t("UploadNavigation.previousStep") }}
    </button>
    <button
      v-if="step !== 5"
      class="save"
      :disabled="loading == true || disableNav == true"
      @click="$emit('save', '/upload/overview')"
    >
      {{ t("UploadNavigation.saveAndClose") }}
    </button>
    <div class="next">
      <div class="loading" v-if="loading == true">
        <div class="loading-text">{{ t("UploadNavigation.translating") }}</div>
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden"></span>
        </div>
      </div>
      <button
        v-if="step !== 5"
        class="primary"
        :disabled="loading == true || disableNav == true"
        @click="$emit('save', `/upload/${step + 1}?uuid=${uuid}`)"
      >
        {{ t("UploadNavigation.nextStep") }}
      </button>
      <button
        v-else
        class="primary"
        :disabled="loading == true || disableNav == true"
        @click="$emit('save', '/upload/overview')"
      >
        {{ t("UploadNavigation.saveAndFinish") }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed, defineExpose, ref} from "vue";
import {useI18n} from "vue-i18n";
import router from "@/router";

defineProps<{
  step: number;
  uuid: string;
}>();

defineEmits(["save"]);

const loading = defineModel("loading", {required: false});
const disableNav = defineModel("disableNav", {required: false});

const {t} = useI18n({useScope: "global"});

function toggleNavigationClickable(clickable: boolean) {
  disableNav.value = !clickable;
}
defineExpose({toggleNavigationClickable});
</script>

<style scoped>
.links {
  margin-top: 2rem;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  width: 100%;
  bottom: 1rem;
  position: relative;
}

.previous {
  justify-self: start;
  grid-column: 1;
}

.save {
  justify-self: center;
  grid-column: 2;
  background-color: var(--hans-medium-blue);
  color: var(--hans-light);
}

.save:hover {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
}

.next {
  justify-self: end;
  grid-column: 3;
  display: flex;
  gap: 1rem;
}

.loading {
  grid-column: 2;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .links {
    grid-template-columns: auto;
  }

  .previous {
    justify-self: center;
    grid-column: 1;
  }

  .save {
    justify-self: center;
    grid-column: 1;
  }

  .next {
    justify-self: center;
    grid-column: 1;
  }

  .loading {
    justify-self: center;
    grid-column: 1;
  }
}

.loading span {
  text-align: center;
}

button {
  background-color: var(--hans-light-gray);
  color: var(--hans-dark);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  width: fit-content;
  border: none;
}

button:hover {
  background-color: var(--hans-medium-gray);
}

button:disabled {
  background-color: var(--hans-light-gray);
  color: var(--hans-dark-gray);
}

.primary {
  background-color: var(--hans-dark-blue);
  color: var(--hans-light);
}

.primary:hover {
  background-color: var(--hans-medium-blue);
}
</style>
