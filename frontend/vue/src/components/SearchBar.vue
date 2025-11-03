<template>
  <!-- searchbar column -->
  <div class="col-7 d-flex justify-content-center">
    <div class="form search-bar" style="position: relative; display: flex; align-items: center">
      <input
        type="search"
        class="form-control form-input"
        v-on:keyup.enter="forwardToSearchResults"
        v-model="searchterms"
        :placeholder="placeholder"
      />
      <SearchButton :search="forwardToSearchResults" :localSearch="false" />
    </div>
  </div>
  <!-- searchbar column end -->
</template>

<script setup lang="ts">
import {useRouter} from "vue-router";
import {ref} from "vue";
import SearchButton from "./SearchButton.vue";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
let searchterms = ref("");
const router = useRouter();
defineProps({placeholder: String});

function forwardToSearchResults() {
  const global_searchterms = searchterms.value.split(" ").filter((n) => n);
  loggerService.log("Global search:");
  loggerService.log(global_searchterms);
  router.push({
    name: "SearchResults",
    query: {q: global_searchterms, f: []},
  });
  // reset form input text
  searchterms.value = "";
}
</script>

<style scoped>
.search-bar {
  width: 300px;
}
</style>
