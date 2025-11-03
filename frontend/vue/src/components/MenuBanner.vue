<template>
  <!--  menu banner -->
  <div class="row">
    <div>
      <div class="menu p-2 my-1 rounded border" style="display: inline-block">
        <div v-if="props.hint_before">
          <ButtonHint
            route="generalnotes"
            :hovertext="props.hinttext"
            :hint_before="props.hint_before"
            :hint_after="false"
          />&nbsp;{{ menutext }}
        </div>
        <div v-else-if="props.hint_after">
          {{ menutext }}&nbsp;<ButtonHint
            route="generalnotes"
            :hovertext="props.hinttext"
            :hint_before="false"
            :hint_after="props.hint_after"
          />
        </div>
        <div v-else>
          {{ menutext }}
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

const props = withDefaults(
  defineProps<{
    menutext: string;
    hint_before: boolean;
    hint_after: boolean;
    hinttext: string;
  }>(),
  {
    hint_before: false,
    hint_after: false,
    hinttext: "",
  },
);
</script>

<style scoped>
.my-1 {
  margin-top: 0.25rem !important;
  margin-bottom: 0.75rem !important;
}
</style>
