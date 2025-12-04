<template>
  <!--  menu banner -->
  <div class="col">
    <div class="d-flex align-items-start">
      <div v-if="props.submenu === false">
        <div v-if="props.hint_before" class="menu rounded border">
          <ButtonHint
            route="generalnotes"
            :hovertext="props.hinttext"
            :hint_before="props.hint_before"
            :hint_after="false"
          />&nbsp;{{ props.menutext }}
        </div>
        <div v-else-if="props.hint_after" class="menu rounded border">
          {{ props.menutext }}&nbsp;<ButtonHint
            route="generalnotes"
            :hovertext="props.hinttext"
            :hint_before="false"
            :hint_after="props.hint_after"
          />
        </div>
        <div v-else class="menu rounded border">
          {{ props.menutext }}
        </div>
      </div>
      <div v-else>
        <router-link
          @click="matomo_clicktracking('click_button', props.menutext)"
          :to="{name: props.menuroute}"
          class="submenu-router"
        >
          <div class="menu rounded border submenu-container">
            <span class="menu-text">{{ props.menutext }}</span>
          </div>
        </router-link>
      </div>
      <div v-if="props.submenu === true">
        <div class="menu rounded border">
          {{ props.submenutext }}
        </div>
      </div>
      <AnnouncementBanner></AnnouncementBanner>
    </div>
  </div>
  <!--  menu banner end -->
</template>

<script setup lang="ts">
import AnnouncementBanner from "@/components/AnnouncementBanner.vue";
import ButtonHint from "@/components/ButtonHint.vue";
import {matomo_clicktracking} from "@/common/matomo_utils";

const props = withDefaults(
  defineProps<{
    menutext: string;
    hint_before: boolean;
    hint_after: boolean;
    hinttext: string;
    submenu: boolean;
    menuroute: string;
    submenutext: string;
  }>(),
  {
    hint_before: false,
    hint_after: false,
    hinttext: "",
    submenu: false,
    menuroute: "",
    submenutext: "",
  },
);
</script>

<style scoped>
.menu {
  display: inline-block;
  padding: 0.5em;
  text-wrap-mode: nowrap;
}

.my-1 {
  margin-top: 0.25rem !important;
  margin-bottom: 0.75rem !important;
}

.submenu-container {
  color: var(--hans-light);
  cursor: pointer;
  background-color: var(--hans-light-blue);
}

.submenu-router {
  color: var(--hans-light);
  text-decoration: none;
}

.submenu-container:hover {
  color: var(--button-background-hover, var(--hans-light));
}

.submenu-container:hover {
  background-color: var(--hans-dark-blue);
}

.menu-text {
  color: var(--button-color, var(--hans-dark));
}

.submenu-container:hover > .menu-text {
  color: var(--button-color-hover, var(--hans-light));
}
</style>
