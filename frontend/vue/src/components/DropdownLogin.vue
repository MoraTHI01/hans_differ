<template>
  <!-- dropdown -->
  <div v-if="loggedIn === false" class="logged-out-button">
    <!-- login button -->
    <router-link :to="{name: 'login'}" class="btn btn-container">
      <img src="/bootstrap-icons/person.svg" alt="person" class="img-fluid img-btn" />
      <span class="btn-text login-prompt">{{ t("DropdownLogin.login") }}</span>
    </router-link>
    <!-- login button end -->
  </div>
  <div v-else-if="currUser?.role === 'admin'" class="dropdown">
    <!-- login button -->
    <button
      class="btn btn-container dropdown-toggle"
      type="button"
      id="dropdownMenuButton"
      data-bs-toggle="dropdown"
      aria-expanded="false"
    >
      <img src="/bootstrap-icons/person.svg" alt="person" class="img-fluid img-btn" />
      <span class="btn-text username">{{ currUser?.uname }}</span>
    </button>
    <!-- login button end -->

    <!-- dropdown menu -->
    <div class="dropdown-menu" aria-labelledby="dropdownMenuButton" role="menu">
      <div class="dropdown-item username-dropdown">{{ currUser?.uname }}</div>
      <!-- divider -->
      <div class="username-dropdown dropdown-divider dropdown-item"></div>
      <!-- divider end -->

      <!-- api button -->
      <ButtonDark
        class="dropdown-item"
        src="/bootstrap-icons/x-diamond-fill.svg"
        route="openapi"
        :btntext="t('DropdownLogin.api')"
      />
      <!-- api button end -->

      <!-- create button -->
      <ButtonDark
        class="dropdown-item"
        src="/bootstrap-icons/plus-circle.svg"
        route="create"
        :btntext="t('DropdownLogin.channel')"
      />
      <!-- create button end -->

      <!-- upload button -->
      <ButtonDark
        class="dropdown-item"
        src="/bootstrap-icons/question.svg"
        route="survey"
        :btntext="t('DropdownLogin.survey')"
      />
      <!-- upload button end -->

      <!-- upload button -->
      <ButtonDark
        class="dropdown-item"
        src="/bootstrap-icons/megaphone.svg"
        route="announcement"
        :btntext="t('DropdownLogin.announcement')"
      />
      <!-- upload button end -->

      <!-- upload button -->
      <ButtonDark
        class="dropdown-item"
        src="/bootstrap-icons/box-arrow-up.svg"
        route="upload"
        :btntext="t('DropdownLogin.upload')"
      />
      <!-- upload button end -->

      <!-- upload flow button -->
      <ButtonDark
        class="dropdown-item"
        src="/bootstrap-icons/ui-checks.svg"
        route="upload-overview"
        :btntext="t('DropdownLogin.yourMedia')"
      />
      <!-- upload flow button end -->

      <!-- upload button -->
      <ToggleDark
        class="dropdown-item toggle-item"
        :value="evalActive"
        v-on:change="toggleEval()"
        :tgltext="t('DropdownLogin.evaluation')"
      />
      <!-- upload button end -->

      <!-- divider -->
      <div class="dropdown-divider dropdown-item"></div>
      <!-- divider end -->

      <!-- logout button -->
      <ButtonDark
        class="dropdown-item"
        src="/bootstrap-icons/box-arrow-right.svg"
        v-on:click="performLogout()"
        :btntext="t('DropdownLogin.logout')"
      />
      <!-- logout button end -->
    </div>
    <!-- dropdown menu end -->
  </div>
  <div v-else-if="currUser?.role === 'lecturer' || currUser?.role === 'developer'" class="dropdown">
    <!-- login button -->
    <button
      class="btn btn-container dropdown-toggle"
      type="button"
      id="dropdownMenuButton"
      data-bs-toggle="dropdown"
      aria-expanded="false"
    >
      <img src="/bootstrap-icons/person.svg" alt="person" class="img-fluid img-btn" />
      <span class="btn-text username">{{ currUser?.uname }}</span>
    </button>
    <!-- login button end -->

    <!-- dropdown menu -->
    <div class="dropdown-menu" aria-labelledby="dropdownMenuButton" role="menu">
      <div class="dropdown-item username-dropdown">{{ currUser?.uname }}</div>

      <!-- upload flow button -->
      <ButtonDark
        v-if="!authStore.getOidcUsed()"
        class="dropdown-item"
        src="/bootstrap-icons/ui-checks.svg"
        route="upload-overview"
        :btntext="t('DropdownLogin.yourMedia')"
      />
      <!-- upload flow button end -->

      <!-- upload button -->
      <ToggleDark
        class="dropdown-item toggle-item"
        :value="evalActive"
        v-on:change="toggleEval()"
        :tgltext="t('DropdownLogin.evaluation')"
      />
      <!-- upload button end -->

      <!-- divider -->
      <div class="username-dropdown dropdown-divider dropdown-item"></div>
      <!-- divider end -->

      <!-- logout button -->
      <ButtonDark
        class="dropdown-item"
        src="/bootstrap-icons/box-arrow-right.svg"
        v-on:click="performLogout()"
        :btntext="t('DropdownLogin.logout')"
      />
      <!-- logout button end -->
    </div>
    <!-- dropdown menu end -->
  </div>
  <div v-else-if="currUser?.role === 'everybody'" class="dropdown">
    <!-- login button -->
    <button
      class="btn btn-container dropdown-toggle"
      type="button"
      id="dropdownMenuButton"
      data-bs-toggle="dropdown"
      aria-expanded="false"
    >
      <img src="/bootstrap-icons/person.svg" alt="person" class="img-fluid img-btn" />
      <span class="btn-text username">{{ currUser?.uname }}</span>
    </button>
    <!-- login button end -->

    <!-- dropdown menu -->
    <div class="dropdown-menu" aria-labelledby="dropdownMenuButton" role="menu">
      <div class="dropdown-item username-dropdown">{{ currUser?.uname }}</div>

      <!-- upload button -->
      <ToggleDark
        class="dropdown-item toggle-item"
        :value="evalActive"
        v-on:change="toggleEval()"
        :tgltext="t('DropdownLogin.evaluation')"
      />
      <!-- upload button end -->

      <!-- divider -->
      <div class="username-dropdown dropdown-divider dropdown-item"></div>
      <!-- divider end -->

      <!-- logout button -->
      <ButtonDark
        class="dropdown-item"
        src="/bootstrap-icons/box-arrow-right.svg"
        v-on:click="performLogout()"
        :btntext="t('DropdownLogin.logout')"
      />
      <!-- logout button end -->
    </div>
    <!-- dropdown menu end -->
  </div>
  <!-- dropdown end -->
</template>

<script setup lang="ts">
import ButtonDark from "./ButtonDark.vue";
import ToggleDark from "./ToggleDark.vue";
import {onUpdated, onMounted} from "vue";
import {useAuthStore} from "@/stores/auth";
import {useEvalStore} from "@/stores/eval";
import {useI18n} from "vue-i18n";
import {LoggerService} from "@/common/loggerService";
import {matomo_clicktracking} from "@/common/matomo_utils";

const loggerService = new LoggerService();
const {t} = useI18n({useScope: "global"});
const authStore = useAuthStore();
const evalStore = useEvalStore();
//authStore.update();
let evalActive = false;
updateEval();
let loggedIn = authStore.getLoggedIn();
let currUser = {
  uname: "",
  role: "",
};

if (loggedIn === true) {
  currUser = {
    uname: authStore.getDisplayName(),
    role: authStore.getRole(),
  };
  loggerService.log(currUser);
}

async function performLogout() {
  matomo_clicktracking("logout", "start");
  return authStore.logout().catch((error) => loggerService.error("Error on perform logout!"));
}

function updateEval() {
  evalActive = evalStore.getEvalActive();
  //evalStore.printStatus();
}

function toggleEval() {
  loggerService.log("Toggle EvalSession");
  let mode = !evalStore.getEvalActive();
  evalStore.setEvalMode(mode);
  if (mode === true) {
    matomo_clicktracking("eval", "active");
  } else {
    matomo_clicktracking("eval", "inactive");
  }
  updateEval();
}

onMounted(() => {
  loggerService.log("UpdateOnMounted DropdownLogin");
  updateEval();
});

onUpdated(() => {
  loggerService.log("Update DropdownLogin");
  //authStore.update();
  updateEval();
  loggedIn = authStore.getLoggedIn();
  currUser = {
    uname: "",
    role: "",
  };
  if (loggedIn === true) {
    currUser = {
      uname: authStore.getDisplayName(),
      role: authStore.getRole(),
    };
    loggerService.log(currUser);
  }
});
</script>

<style scoped>
.toggle-item {
  left: 2em;
}

.btn-container {
  display: flex;
  align-items: center;
  float: left;
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

.dropdown {
  display: flex;
}

.dropdown-divider {
  height: 0;
  margin-top: 4.5rem;
  overflow: hidden;
  border-top: 1px solid rgba(0, 0, 0, 0.15);
  padding-bottom: 0;
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

.dropdown-menu {
  /* Ensure dropdown menus are right aligned - important to override programatically set inline style */
  right: 0 !important;
}

.username-dropdown {
  display: none;
}

.logged-out-button {
  display: flex;
}

@media (max-aspect-ratio: 3/5) {
  .username,
  .login-prompt {
    display: none;
  }

  .username-dropdown {
    display: block;
    margin-top: 0;
  }
}
</style>
