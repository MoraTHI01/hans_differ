<template>
  <!-- searchbar column -->
  <div class="col-7 d-flex justify-content-center">
    <div class="form search-bar" ref="searchbar">
      <SearchButton :search="search" :localSearch="true" />
      <input
        class="form-control form-input"
        v-on:keyup.enter="search"
        v-model="searchterms"
        :placeholder="t('VideoSearchBar.searchtext')"
        @input="searchbar.classList"
        @keydown="inputHandler"
      />
      <div v-if="notfound" class="not-found-container">
        <p>{{ t("VideoSearchBar.notfound") }}</p>
      </div>
      <div v-if="resultList !== undefined && resultList.length > 0" class="result-container">
        <ul id="result-list" class="list-group">
          <ResultItem
            class="list-group-item d-flex justify-content-between align-items-center"
            v-for="(item, index) in resultList"
            :resultItem="item"
            :id="`result-${index}`"
            @click="handleClick"
            @mouseover="handleHover"
          >
          </ResultItem>
        </ul>
      </div>
    </div>
  </div>
  <!-- searchbar column end -->
</template>

<script setup lang="ts">
import {defineProps, ref, watch, computed, onMounted} from "vue";
import SearchButton from "./SearchButton.vue";
import ResultItem from "@/components/ResultItem.vue";
import {matomo_clicktracking} from "@/common/matomo_utils";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {useMediaStore} from "@/stores/media";
import {SearchTrie, SearchTrieResult} from "@/data/SearchTrie";
import {SearchTrieClass} from "@/common/searchTrie";

// media item as prop similar to other or uuid

const loggerService = new LoggerService();
const {t, locale} = useI18n({useScope: "global"});
const store = useMediaStore();

//const props = defineProps<{
//  useSearchTrieSlides: boolean
//}>();

const searchterms = ref("");
const searchbar = ref();
const emit = defineEmits([]);
const searchTrie = ref();
const resultList = ref();
const index = ref(false);
const notfound = ref(false);

//const placeholder = ref(t('VideoSearchBar.searchtext'));
//if (props.useSearchTrieSlides === true)
//{
//  placeholder.value = t('VideoSearchBar.searchSlidestext');
//}
//else
//{
//  placeholder.value = t('VideoSearchBar.searchtext');
//}

function display(index) {
  const resultList = document.getElementById("result-list");

  for (let i = 0; i < resultList.children.length; i++) {
    let result = resultList.children[i];
    if (result !== undefined && result.classList !== undefined) {
      result.classList.remove("active");
    }
  }

  const result = document.getElementById(`result-${index}`);
  if (result !== undefined && result.classList !== undefined) {
    result.classList.add("active");
  }
}

function splitInput(event) {
  let input = event.key === "Backspace" ? event.target.value.slice(0, -1) : event.target.value + event.key;

  let words = input.split(" ");

  return words[words.length - 1];
}

function clearInput(event) {
  notfound.value = false;
  if (!splitInput(event)) {
    resultList.value = [];
  }

  if ((event.keyCode > 46 && event.keyCode < 90) || event.keyCode === 8) {
    index.value = false;
    return true;
  }

  if (event.key === "Enter") {
    search();
    searchterms.value = "";
    resultList.value = [];
    index.value = false;
  }

  if (event.key === "Space") {
    resultList.value = [];
    index.value = false;
  }

  if (event.key === "ArrowUp") {
    event.preventDefault();

    if (!resultList.value.length) {
      return;
    }

    if (index.value === false) {
      index.value = resultList.value.length - 1;
    } else {
      index.value -= 1;
      if (index.value < 0) {
        index.value = resultList.value.length - 1;
      }
    }

    display(index.value);

    let word = resultList.value[index.value];
    let words = event.target.value.split(" ");
    words.pop();
    words.push(word.word);
    searchterms.value = words.join(" ");
    return;
  }

  if (event.key === "ArrowDown") {
    event.preventDefault();

    if (!resultList.value.length) {
      return;
    }

    if (index.value === false) {
      index.value = 0;
    } else {
      index.value += 1;
      index.value = index.value % resultList.value.length;
    }

    display(index.value);

    let word = resultList.value[index.value];
    let words = event.target.value.split(" ");
    words.pop();
    words.push(word.word);
    searchterms.value = words.join(" ");

    return;
  }
}

function inputHandler(event) {
  notfound.value = false;
  handleTrie();

  if (!clearInput(event)) {
    return;
  }

  let lastWord = splitInput(event);

  let resultWords = searchTrie.value.search(lastWord);

  if (!resultWords) {
    notfound.value = true;
    return;
  }

  let nextWords = searchTrie.value.get_all_words(resultWords, []);

  if (!nextWords) {
    index.value = false;
    resultList.value = [];
    notfound.value = true;
    return;
  }

  nextWords = nextWords.sort((a, b) => b.occurences.length - a.occurences.length);

  resultList.value = nextWords;
}

function handleTrie() {
  loggerService.log("VideoSearchBar:handleTrie");
  //if (props.useSearchTrieSlides === true)
  //{
  //  loggerService.log("VideoSearchBar:handleTrie:UseSlidesTrie");
  //  searchTrie.value = new SearchTrieClass(store.getSearchTrieSlides[0] as SearchTrie);
  //}
  //else {
  loggerService.log("VideoSearchBar:handleTrie:UseTranscriptTries");
  if (locale.value === "de") {
    searchTrie.value = new SearchTrieClass(store.getSearchTrie[0] as SearchTrie);
  } else if (locale.value === "en") {
    searchTrie.value = new SearchTrieClass(store.getSearchTrie[1] as SearchTrie);
  }
  //}
}

function handleClick(event) {
  let id = Number(event.target.id.split("-")[1]);
  let word = resultList.value[id];

  let words = searchterms.value.split(" ");
  words.pop();
  words.push(word.word);
  searchterms.value = words.join(" ") + " ";
  index.value = false;
  resultList.value = [];

  let el = document.getElementsByClassName("form-input")[0] as HTMLElement;
  el.focus();
}

function handleHover(event) {
  let id = Number(event.target.id.split("-")[1]);
  index.value = id;
  let word = resultList.value[id];
  display(id);
}

/**
 * Emits a `searchterms` event for the first searchterm in the input after splitting it on space
 */
function search() {
  const local_searchterms = typeof searchterms.value === "string" ? searchterms.value.split(" ") : searchterms.value;
  loggerService.log("Local search: " + local_searchterms);
  emit("searchterms", local_searchterms);
  matomo_clicktracking("in_media_search", local_searchterms.map((_) => _).join(" "));
}

// Watch the locale to register for language changes and switch summary dep. on locale
//watch(locale, async (newText) => {
//  if (props.useSearchTrieSlides === true)
//  {
//    placeholder.value = ref(t('VideoSearchBar.searchtext'));
//  }
//  else
//  {
//    placeholder.value = ref(t('VideoSearchBar.searchtext'));
//  }
//});

defineExpose({
  /**
   * Clears the search bar text
   */
  clearSearch() {
    searchterms.value = "";
  },
  /**
   * Enables a message near the search bar indicating that no search result was found for the given query.
   * The message will disappear on any further input.
   */
  setNotFound() {
    if (searchterms.value.length > 0) {
      loggerService.log("Not found!");
      notfound.value = true;
    }
  },
  /**
   * Search
   */
  search(searchterms: string) {
    const local_searchterms = typeof searchterms === "string" ? searchterms.split(" ") : searchterms;
    loggerService.log("Local search: " + local_searchterms);
    emit("searchterms", local_searchterms);
    matomo_clicktracking("in_media_search", local_searchterms.map((_) => _).join(" "));
  },
});
</script>

<style scoped>
.list-group {
  margin-bottom: 10px;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.list-group-item {
  width: 100%;
}

.search-bar {
  width: 300px;
  position: relative;
  display: flex;
  align-items: center;
  min-width: 200px;
}

.search-bar:after {
  position: relative;
  left: 0;
  color: var(--hans-dark-gray);
  bottom: -1.5em;
}

#result-list {
  position: relative;
  z-index: 1;
  cursor: pointer;
  width: 100%;
}

.result-container {
  position: absolute;
  width: 100%;
  top: 42px;
  height: 30vh;
  z-index: 999;
  left: 0;
  overflow: auto;
}

.not-found-container {
  position: absolute;
  width: 100%;
  top: 42px;
  height: 2em;
  z-index: 998;
  left: 0.8em;
}
</style>
