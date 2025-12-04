<script setup lang="ts"></script>

<template>
  <router-view :key="$route.fullPath" />
</template>

<style>
:root {
  /*
   * Variables for the global color theme
   */
  --hans-dark: #000000;
  --hans-dark-gray: #6c757d;
  --hans-medium-gray: #aaaaaa;
  --hans-light-gray: #dddddd;
  --hans-light: #ffffff;

  --hans-ok: #86db2a;
  --hans-error: #d93025;

  --hans-dark-blue: #2950db;
  --hans-medium-blue: #5f9ceb;
  --hans-light-blue: #c8deff;

  --hans-red: #dc3545;
  --hans-dark-red: #c82333;
}

#app {
  margin: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  /*
   * Dynamic aspect ratio - width shouldn't exceed viewport width in portrait
   * resolutions and will try to maintain a 4/3 aspect ratio of the center content
   * for optimal readability but with a width that is no less the size of 100 `0` glyphs.
   */
  --container-width: min(100vw, max(100ch, 125vh));
}

.main-container {
  /*
   * Dynamically forces container to be no wider than a 4/3 aspect ratio and
   * fills the space between header and footer so the footer is always at the bottom
   */
  max-width: var(--container-width);
  flex: 1;
  /* Derived from the bootstrap container class */
  --bs-gutter-x: 1.5rem;
  --bs-gutter-y: 0;
  width: 100%;
  padding-right: calc(var(--bs-gutter-x) * 0.5);
  padding-left: calc(var(--bs-gutter-x) * 0.5);
  margin-right: auto;
  margin-left: auto;
  /* margin-bottom: 4em; */
}
.sub-container {
  position: relative;
  margin-top: 1em;
}
.popover .popover-header {
  background-color: var(--hans-dark-blue) !important;
  color: var(--hans-light) !important;
}
</style>
