<template>
  <div class="card-body p-1">
    <div v-if="!loading" class="col-12 accordion accordion-flush" id="accordionExternalLinks">
      <div v-for="(key, ind) of Object.keys(links)" :key="ind" class="accordion-item">
        <h2 class="accordion-header" :id="'flush-heading-' + key">
          <button
            class="accordion-button collapsed"
            type="button"
            @click="categorySelected(key)"
            data-bs-toggle="collapse"
            :data-bs-target="'#flush-collapse-' + key"
            aria-expanded="false"
            :aria-controls="'flush-collapse-' + key"
          >
            {{ key }}
          </button>
        </h2>
        <div
          :id="'flush-collapse-' + key"
          class="accordion-collapse collapse"
          :aria-labelledby="'flush-heading-' + key"
          data-bs-parent="#accordionExternalLinks"
        >
          <ul id="result-list" class="list-group">
            <li
              v-for="(item, index) in links[key]"
              :key="index"
              class="list-group-item d-flex justify-content-between align-items-center"
            >
              <a :href="item.url" class="link" target="_blank" rel="noopener noreferrer" v-html="item.title"></a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, watch, onMounted} from "vue";
import type {MediaItem} from "@/data/MediaItem.js";
import {useMediaStore} from "@/stores/media";
import type {SlidesImagesMeta} from "@/data/SlidesImagesMeta";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import axios from "axios";

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const store = useMediaStore();

const props = defineProps<{
  video: MediaItem;
}>();

const loading = ref(true);

interface LinkInfo {
  title?: string;
  url?: string;
}

const links = ref<{[key: string]: Array<LinkInfo>}>({});

const updateSlidesImagesMeta = async (): Promise<T> => {
  loggerService.log("updateSlidesImagesMeta: Start");
  loading.value = true;
  await store.loadSlidesImagesMeta(props.video?.uuid, true);
  links.value = {};
  // Iterate over external links from the store
  for (const [key, value] of Object.entries(store.getExternalLinks)) {
    const currentCategory = t("VideoExternalLinks." + key);
    loggerService.log(`updateSlidesImagesMeta: Category ${currentCategory}`);

    // Ensure the category array is initialized
    if (!(currentCategory in links.value)) {
      links.value[currentCategory] = [];
    }

    // If value is an array of URLs, iterate over each URL
    if (Array.isArray(value)) {
      for (const url of value) {
        // Fetch the page title for the current URL
        const title = url as string; //await fetchPageTitle(url as string);

        // Create a new LinkInfo object for the current title and URL
        const resLinkInfo: LinkInfo = {
          title: title?.trim(),
          url: url as string,
        };

        // Check if the URL already exists in the current category
        const urlExists = links.value[currentCategory].some((link) => link.url === resLinkInfo.url);
        if (!urlExists) {
          // Push the new LinkInfo object into the category array
          links.value[currentCategory].push(resLinkInfo);
          loggerService.log(`Added: ${resLinkInfo.title} - ${resLinkInfo.url}`);
        } else {
          loggerService.log(`Duplicate URL found, skipping: ${resLinkInfo.url}`);
        }
      }
    } else {
      // If the value is not an array, just handle it as a single URL
      const title = url as string; // await fetchPageTitle(value as string);

      const resLinkInfo: LinkInfo = {
        title: title?.trim(),
        url: value as string,
      };

      // Check if the URL already exists in the current category
      const urlExists = links.value[currentCategory].some((link) => link.url === resLinkInfo.url);
      if (!urlExists) {
        // Push the new LinkInfo object into the category array
        links.value[currentCategory].push(resLinkInfo);
        loggerService.log(`Added: ${resLinkInfo.title} - ${resLinkInfo.url}`);
      } else {
        loggerService.log(`Duplicate URL found, skipping: ${resLinkInfo.url}`);
      }
    }
  }
  loggerService.log("updateSlidesImagesMeta: End");
  loading.value = false;
  return;
};

async function fetchPageTitle(url: string): Promise<string> {
  try {
    // Make a GET request to the external webpage
    const response = await axios.get(url, {
      headers: {
        "Access-Control-Allow-Origin": "*",
      },
      responseType: "document",
    });

    // Extract the HTML content as a string
    const htmlString = response.data as string;

    // Parse the HTML using DOMParser
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, "text/html");

    // Extract the title from the parsed document
    const title = doc.querySelector("title")?.innerText || null;
    if (title === null) {
      return url;
    }

    return title;
  } catch (error) {
    loggerService.error("Error fetching the webpage title:", error);
    return url;
  }
}

onMounted(async () => {
  await updateSlidesImagesMeta();
});

// Watch the locale to register for language changes and switch summary dep. on locale
watch(locale, async (newText) => {
  await updateSlidesImagesMeta();
});

const categorySelected = (category: string) => {
  matomo_clicktracking("click_button", "External link category selected: " + category);
};
</script>

<style scoped>
.list-group-item {
  margin-top: 0.2em;
}
</style>
