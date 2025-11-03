import "bootstrap/dist/css/bootstrap.min.css";
import "video.js/dist/video-js.min.css";
import {createApp} from "vue";
import {createPinia} from "pinia";
import {createI18n} from "vue-i18n";
import {apiClient} from "./common/apiClient";

import App from "./App.vue";
import router from "./router";

import translationsComponentsDe from "./translations/components_de.json";
import translationsViewsDe from "./translations/views_de.json";
import translationsComponentsEn from "./translations/components_en.json";
import translationsViewsEn from "./translations/views_en.json";

// Use mitt as event bus
import mitt from "mitt";
const eventBus = mitt();

// Export common used components
//export default { apiClient, eventBus };

// i18n

const messages = {
  de: {...translationsComponentsDe, ...translationsViewsDe},
  en: {...translationsComponentsEn, ...translationsViewsEn},
};

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: "de", // set locale
  fallbackLocale: "en", // set fallback locale
  messages,
});

// Initialization

const app = createApp(App);

app.use(createPinia());
app.use(i18n);
app.use(router);
app.provide("apiClient", apiClient);
app.provide("eventBus", eventBus);
app.mount("#app");

import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "video.js/dist/video.min.js";
import "videojs-vtt.js/dist/vtt.min.js";
import "videojs-hotkeys/videojs.hotkeys.min.js";
import "marked/marked.min.js";
