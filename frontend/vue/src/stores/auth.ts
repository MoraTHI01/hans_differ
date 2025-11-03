import {defineStore} from "pinia";
import {apiClient} from "@/common/apiClient";
import axios from "axios";
import router from "@/router/index";
import {JWTAccess, User} from "@/data/Authorization";
import {RemoteData} from "@/data/RemoteData";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();

export const useAuthStore = defineStore({
  id: "authStore",
  state: () => ({
    // User data
    user: null as User | null,
    // Login status
    loggedIn: new RemoteData(false),
    // JWT access and refresh tokens
    jwtAccess: new JWTAccess(),
    // Is a JWT refresh active
    refreshActive: false,
    // redirect URL
    returnUrl: null as string | null,
    // indicate if oidc login was used
    oidcUsed: false,
  }),
  getters: {
    // initialize state from local storage to enable user to stay logged in
    getPreferedLocale: (state) => () => {
      return state.user?.preferedLanguage;
    },
    getLoggedIn: (state) => () => {
      return state.loggedIn.data;
    },
    getLoginInProgress: (state) => () => {
      return state.loggedIn.loading;
    },
    getUsername: (state) => () => {
      return state.user?.username;
    },
    getRole: (state) => () => {
      return state.user?.role;
    },
    getOidcUsed: (state) => () => {
      return state.oidcUsed;
    },
    getDisplayName: (state) => () => {
      return state.user === null ? "" : state.user.firstName + " " + state.user.lastName;
    },
    getAccessToken: (state) => () => {
      return state.jwtAccess.token;
    },
    getRefreshToken: (state) => () => {
      return state.jwtAccess.refreshToken;
    },
    getRefreshActive: (state) => () => {
      return state.refreshActive;
    },
  },
  actions: {
    storeTokenInStorage(key: string, token: string) {
      localStorage.setItem(key, JSON.stringify({token: token}));
    },
    loadTokenFromStorage(key: string) {
      const tokenData = localStorage.getItem(key);
      if (tokenData === undefined || tokenData === null) {
        return null;
      }
      const token = JSON.parse(tokenData).token;
      return token;
    },
    setAccessToken(accessToken: string, store: boolean) {
      this.jwtAccess.token = accessToken;
      const tokenJson = JSON.parse(window.atob(accessToken.split(".")[1]));
      this.jwtAccess.expiration = tokenJson.exp;
      this.user = new User(
        tokenJson.sub.username,
        tokenJson.sub.firstName,
        tokenJson.sub.lastName,
        tokenJson.sub.preferedLanguage,
        tokenJson.sub.university,
        tokenJson.sub.faculty,
        tokenJson.sub.role,
      );
      if (store) {
        this.storeTokenInStorage(this.jwtAccess.key, this.jwtAccess.token);
      }
      this.loggedIn.complete(true);
    },
    setRefreshToken(refreshToken: string, store: boolean) {
      this.jwtAccess.refreshToken = refreshToken;
      const refreshTokenJson = JSON.parse(window.atob(refreshToken.split(".")[1]));
      this.jwtAccess.expiration = refreshTokenJson.exp;
      if (store) {
        this.storeTokenInStorage(this.jwtAccess.refreshKey, this.jwtAccess.refreshToken);
      }
    },
    update() {
      const accessToken = this.loadTokenFromStorage(this.jwtAccess.key);
      const refreshToken = this.loadTokenFromStorage(this.jwtAccess.refreshKey);
      if (accessToken !== undefined && accessToken !== null && refreshToken !== undefined && refreshToken !== null) {
        this.setAccessToken(accessToken, false);
        this.setRefreshToken(refreshToken, false);
      } else {
        loggerService.log("No user is logged in!");
        this.loggedIn.complete(false);
      }
    },
    resetLoading() {
      this.loggedIn.loading = false;
    },
    async loginOidc(provider_id: string) {
      this.loggedIn.loading = true;
      console.log(`Login with SSO via provider: ${provider_id}`);
      try {
        const response = await apiClient.post("/login/" + provider_id);
        const redirectUrl = decodeURIComponent(response.headers.location);
        //console.log("Redirect url:");
        //console.log(redirectUrl);
        window.location.href = redirectUrl;
        return true;
      } catch (error) {
        console.error("loginOidc Request error:", error);
        return false;
      }
    },
    async handleOidc(redirect_url_path) {
      this.loggedIn.loading = true;
      //console.log("Handle OIDC redirect");
      //console.log(redirect_url_path);
      const finalPath = decodeURIComponent(redirect_url_path);
      return apiClient
        .get(finalPath)
        .then((response) => {
          if (response.status === 200) {
            this.setAccessToken(response.data.access_token, true);
            this.setRefreshToken(response.data.refresh_token, true);
            console.log("Logged in via OIDC!");
            //redirect to previous url or default to home page
            this.oidcUsed = true;
            return this.returnUrl || "/";
          }
          this.loggedIn.complete(false);
        })
        .catch((error) => {
          console.error("Error during login process!");
          //console.error(error);

          this.loggedIn.complete(false);
        });
    },
    async login(username: string, password: string) {
      this.loggedIn.loading = true;
      console.log("Login " + username);
      return apiClient
        .post(
          "/login",
          {},
          {
            auth: {
              username,
              password,
            },
          },
        )
        .then((response) => {
          if (response.status === 200) {
            this.setAccessToken(response.data.access_token, true);
            this.setRefreshToken(response.data.refresh_token, true);
            console.log(username + " logged in!");
            //redirect to previous url or default to home page
            router.push(this.returnUrl || "/");
            return this.loggedIn.data;
          }

          this.loggedIn.complete(false);
          return false;
        })
        .catch((error) => {
          console.error("Error during login process!");
          //console.error(error);

          this.loggedIn.complete(false);
          return false;
        });
    },
    async refresh() {
      // Skip refresh call if a refresh is already active
      if (this.refreshActive) {
        return true;
      }

      loggerService.log("Refresh token");
      this.refreshActive = true;
      return apiClient
        .post("/refresh", {})
        .then((response) => {
          if (response.status === 200) {
            this.setAccessToken(response.data.access_token, true);
            //this.setRefreshToken(response.data.refresh_token, true);
            this.refreshActive = false;
            loggerService.log("Token refreshed!");
            router.go();
            return true;
          }
          return false;
        })
        .catch((error) => {
          loggerService.error("Error during refresh token process!");
          //loggerService.error(error);
          this.refreshActive = false;
          if (this.oidcUsed === true) {
            this.logout().catch((error) => {
              loggerService.error("Error during refresh token process logout!");
              this.localLogout();
            });
          } else {
            this.localLogout();
          }
          return false;
        });
    },
    localLogout() {
      this.user = null;
      this.jwtAccess = new JWTAccess();
      localStorage.removeItem(this.jwtAccess.key);
      localStorage.removeItem(this.jwtAccess.refreshKey);
      this.loggedIn.complete(false);
      loggerService.log("Local logout successful!");
      router.push("/login");
    },
    async logout() {
      // Logout in progress
      this.loggedIn.loading = true;
      if (this.oidcUsed === true) {
        console.log("Logout via OIDC");
        try {
          const response = await apiClient.post("/logout");
          const redirectUrl = decodeURIComponent(response.headers.location);
          //console.log("Redirect url:");
          //console.log(redirectUrl);
          // First go to login page with localLogout
          this.localLogout();
          // Then enter the idp logout page
          window.location.href = redirectUrl;
        } catch (error) {
          loggerService.warn("Remote OIDC logout failed!");
          //loggerService.error(error);
          this.localLogout();
        }
      } else {
        return apiClient
          .post("/logout")
          .then(() => {
            loggerService.log("Remote logout successful!");
            this.localLogout();
          })
          .catch((error) => {
            loggerService.warn("Remote logout failed!");
            //loggerService.error(error);
            this.localLogout();
          });
      }
    },
    async getSSOProviders() {
      loggerService.log("getSSOProviders");
      try {
        const {data} = await apiClient.get("/sso-providers");
        loggerService.log(data);
        return data.sso_provider;
      } catch (error: any) {
        loggerService.error("getSSOProviders:Error");
        return {};
      }
    },
  },
});
