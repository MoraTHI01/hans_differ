<template>
  <div class="dropdown">
    <!-- login button -->
    <button
      class="btn btn-container"
      type="button"
      id="dropdownMenuButton"
      data-bs-toggle="dropdown"
      aria-expanded="false"
    >
      <img src="/bootstrap-icons/globe2.svg" alt="globe" class="img-fluid img-btn" />
      <span class="btn-text">{{ $i18n.locale.toUpperCase() }}</span>
    </button>
    <!-- login button end -->

    <!-- dropdown menue -->
    <!-- <div class="dropdown-menu form-inline" aria-labelledby="dropdownMenuButton" role="menu"> -->
    <div class="dropdown-menu" aria-labelledby="dropdownMenuButton" role="menu">
      <div v-if="$i18n.locale === 'de'" @click="toggleChange()" class="dropdown-item">
        <input class="btn-check" type="radio" id="radioEn" value="en" v-model="$i18n.locale" />
        <label for="radioEn" class="radio-text form-check-label">EN</label>
      </div>
      <div v-else class="dropdown-item" @click="toggleChange()">
        <input class="btn-check" type="radio" id="radioDe" value="de" v-model="$i18n.locale" />
        <label for="radioDe" class="radio-text form-check-label">DE</label>
      </div>
    </div>
    <!-- </div>-->
  </div>
</template>
<script setup lang="ts">
import {onUpdated, watch} from "vue";
import {useI18n} from "vue-i18n";
import {useRoute} from "vue-router";
import {useAuthStore} from "@/stores/auth";
import {useMediaStore} from "@/stores/media";
import {useChannelStore} from "@/stores/channels";

const authStore = useAuthStore();
const mediaStore = useMediaStore();
const channelStore = useChannelStore();
const {t, locale} = useI18n({useScope: "global"});

// Set prefered locale as soon as user is logged in
if (authStore.getLoggedIn() === true) {
  let prefSet = localStorage.getItem("hans_pref_locale_set");
  if (prefSet === undefined || prefSet == null || prefSet == "") {
    locale.value = authStore.getPreferedLocale().toLowerCase();
    localStorage.setItem("hans_pref_locale_set", "true");
    // Update the locale in storage
    localStorage.setItem("hans_locale", locale.value);
  }
}

// Get the locale from storage
locale.value = localStorage.getItem("hans_locale");
if (locale.value === null) {
  locale.value = "de";
}
let languageChanged = false;

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {
  // Update the locale in storage
  if (languageChanged == true) {
    localStorage.setItem("hans_locale", locale.value);
    languageChanged = false;
  }
});

const toggleChange = () => {
  languageChanged = true;
};

// Refresh dynamic content on locale change
onUpdated(() => {
  if (authStore.getLoggedIn() === true) {
    const location = useRoute();
    if (location.name === "home") {
      mediaStore.loadRecentMedia();
    } else if (location.name === "channels") {
      channelStore.loadChannels();
    } else if (location.name === "SearchResults") {
      mediaStore.redoLastSearchMedia();
    }
  }
});
</script>

<style scoped>
.btn-container {
  display: flex;
  align-items: center;
  color: var(--hans-light);
}

.btn-container:hover {
  color: var(--hans-dark);
}

.btn-container:hover .img-btn {
  filter: invert(0);
}

.btn-container:hover {
  background-color: var(--hans-light);
  color: var(--hans-dark);
}

.btn-text {
  margin-left: 5px;
}

.radio-text {
  display: block;
  cursor: pointer;
}

.dropdown-item {
  color: var(--hans-dark);
}

.dropdown-item:hover {
  color: var(--hans-light);
  background-color: var(--hans-dark-blue);
}

.img-btn {
  filter: invert(1);
  max-width: unset;
}
</style>
