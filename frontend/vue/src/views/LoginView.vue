<template>
  <HeaderRow />
  <LogoRow />
  <div class="main-container">
    <MenuBanner :menutext="t('LoginView.menutext')" />
    <div class="row justify-content-center sub-container login-container">
      <div class="col login-menu">
        <div class="btn-group mb-3" role="group">
          <button
            type="button"
            :class="{
              'btn btn-primary button-login-active': mode === 'sso',
              'btn btn-secondary button-login-inactive': mode !== 'sso',
            }"
            @click="toggleMode('sso')"
          >
            <img src="/bootstrap-icons/key-fill.svg" alt="api-btn" class="img-fluid img-btn" />&nbsp;{{
              t("LoginView.sso")
            }}&nbsp;
          </button>
          <button
            type="button"
            :class="{
              'btn btn-primary button-login-active': mode === 'local',
              'btn btn-secondary button-login-inactive': mode !== 'local',
            }"
            @click="toggleMode('local')"
          >
            <img src="/bootstrap-icons/key.svg" alt="api-btn" class="img-fluid img-btn" />&nbsp;{{
              t("LoginView.local")
            }}&nbsp;
          </button>
        </div>
        <div v-if="mode === 'local'" class="border login-form-container">
          <h5 class="card-title">{{ t("LoginView.localtitle") }}</h5>
          <form class="d-grid gap-2 login-form-local" @submit.prevent="loginLocal">
            <div class="form-group">
              <label>{{ t("LoginView.username") }}</label>
              <input
                name="username"
                type="text"
                class="form-control form-control-lg"
                @keyup.enter="loginLocal()"
                v-model="inputUsername"
                :placeholder="t('LoginView.username')"
                required
                autofocus
              />
            </div>
            <div class="form-group">
              <label>{{ t("LoginView.password") }}</label>
              <input
                id="inputPassword"
                name="password"
                type="password"
                class="form-control form-control-lg"
                @keyup.enter="loginLocal()"
                v-model="inputPassword"
                :placeholder="t('LoginView.password')"
                autocomplete="on"
                minlength="8"
                required
              />
            </div>
            <button
              type="button"
              @click="loginLocal()"
              class="btn btn-primary btn-block"
              :disabled="authStore.getLoginInProgress()"
            >
              {{ t(authStore.getLoginInProgress() ? loginLoadingText : loginText) }}
            </button>
            <p v-if="displayLoginError" class="login-error-text">
              {{ t("LoginView.error") }}<br />{{ t("LoginView.errordetail") }}
            </p>
          </form>
        </div>
        <div v-if="mode === 'sso'" class="border login-form-container">
          <h5 class="card-title">{{ t("LoginView.ssotitle") }}</h5>
          <div class="d-grid gap-2 login-form-sso">
            <p>
              {{ t("LoginView.ssodesc") }}
            </p>
            <select name="ssoProviderSelect" class="select-sso" id="ssoProviders" v-model="ssoSelectedProviderValues">
              <option v-for="option in ssoOptions" :key="option.value" :value="option.value">
                {{ option.text }}
              </option>
            </select>
            <button
              class="btn btn-primary btn-block btn-sso"
              @click="loginSSO"
              :disabled="authStore.getLoginInProgress()"
            >
              {{ t(authStore.getLoginInProgress() ? loginLoadingText : "LoginView.login") }}&nbsp;<img
                src="/bootstrap-icons/box-arrow-up-right.svg"
                alt="api-btn"
                class="img-fluid img-btn"
              />
            </button>
            <p v-if="displayLoginError" class="login-error-text">
              {{ t("LoginView.error") }}<br />{{ t("LoginView.errordetail") }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <BottomRow />
</template>

<script setup lang="ts">
import HeaderRow from "@/components/HeaderRow.vue";
import BottomRow from "@/components/BottomRow.vue";
import LogoRow from "@/components/LogoRow.vue";
import MenuBanner from "@/components/MenuBanner.vue";
import {useAuthStore} from "@/stores/auth";
import {onMounted, ref} from "vue";
import {useI18n} from "vue-i18n";
import {matomo_trackpageview, matomo_clicktracking} from "@/common/matomo_utils";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
matomo_trackpageview();

const {t} = useI18n({useScope: "global"});
const props = defineProps<{
  username: string[] | string;
  password: string[] | string;
  mode: string;
}>();

const loginText = "LoginView.login";
const loginLoadingText = "LoginView.loggingin";

const authStore = useAuthStore();
props.mode = "local";

// Important file data
let inputUsername = ref("");
let inputPassword = ref("");

const ssoSelectedProviderValues = ref();
const ssoOptions = ref<{value: string; text: string}[]>([]);

const displayLoginError = ref(false);

const toggleMode = (name) => {
  props.mode = name;
};

async function loginSSO() {
  // Set the login status to loading, making the button not clickable
  // multiple times while the login is still in progress
  displayLoginError.value = false;

  return authStore
    .loginOidc(ssoSelectedProviderValues.value)
    .then((loggedIn) => {
      if (loggedIn) {
        matomo_clicktracking("login", "success");
      } else {
        // Clear the password, display an error, focus the password field
        // and reset the login button to default if the login failed
        inputPassword.value = "";
        displayLoginError.value = true;
      }
    })
    .catch((error) => loggerService.error(error));
}

async function loginLocal() {
  // Set the login status to loading, making the button not clickable
  // multiple times while the login is still in progress
  displayLoginError.value = false;

  return authStore
    .login(inputUsername.value, inputPassword.value)
    .then((loggedIn) => {
      if (loggedIn) {
        // Complete login by clearing the form and resetting the login button to default
        inputUsername.value = "";
        inputPassword.value = "";
        loggerService.log("Input form cleared!");
        matomo_clicktracking("login", "success");
      } else {
        // Clear the password, display an error, focus the password field
        // and reset the login button to default if the login failed
        inputPassword.value = "";
        displayLoginError.value = true;
        document.getElementById("inputPassword")?.focus();
      }
    })
    .catch((error) => loggerService.error(error));
}

if (
  props.username !== undefined &&
  props.username !== null &&
  props.username !== "" &&
  props.password !== undefined &&
  props.password !== null &&
  props.password !== ""
) {
  inputUsername.value = props.username;
  inputPassword.value = props.password;
}

onMounted(async () => {
  authStore.resetLoading();
  const ssoProviderData = await authStore.getSSOProviders();
  for (const entry of ssoProviderData) {
    ssoOptions.value.push({value: entry.id, text: entry.o});
  }
  ssoSelectedProviderValues.value = ssoOptions.value[0].value;
});
</script>

<style>
.login-form-container {
  padding: calc(var(--bs-gutter-x) * 0.5);
}
.login-error-text {
  color: var(--hans-error);
}
.button-login-active {
  --button-background-hover: var(--hans-dark);
  --button-color: var(--hans-light);
  --button-color-hover: var(--hans-dark);
  --button-dark-mode: 0;
}
.button-login-inactive {
  --button-background-hover: var(--hans-dark);
  --button-color: var(--hans-light);
  --button-color-hover: var(--hans-dark);
  --button-dark-mode: 0;
}

@media (max-aspect-ratio: 3/5) {
  .login-form-container {
    width: 100%;
  }
}

.btn-sso {
  margin-top: 1em;
}

.login-container {
  position: relative;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 1px 1px 8px #999999;
  border-radius: 13px;
  overflow: hidden;
  padding: 18px;
  width: 430px;
  margin-top: 10px;
  margin-bottom: 10px;
}

@media only screen and (max-width: 799px) {
  .login-container {
    width: auto;
    box-shadow: none;
    border-radius: 0;
    padding: 0;
  }
}

.login-menu {
  align-content: center;
  text-align: center;
  max-width: 390px;
}

.login-form-local {
  text-align: left;
  margin-top: 1em;
}

.login-form-sso {
  margin-top: 1em;
}
</style>
