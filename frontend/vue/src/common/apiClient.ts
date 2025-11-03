import axios from "axios";
import {useAuthStore} from "@/stores/auth";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
const host_url = import.meta.env.VITE_HANS_FRONTEND_HOST_URL;
const protocol = import.meta.env.VITE_HANS_FRONTEND_PROTOCOL;
export const api_base_url = protocol + "://" + host_url + "/api";

export const apiClient = axios.create({
  baseURL: api_base_url,
  headers: {
    "Content-type": "application/json",
    "Access-Control-Allow-Origin": "*",
  },
});

// Adjust timeout as needed, currently 90 seconds
apiClient.defaults.timeout = 90000;

// Request interceptor for API calls
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    // Do something before request is sent
    if (authStore.getLoggedIn()) {
      config.headers["Authorization"] =
        "Bearer " + (authStore.getRefreshActive() ? authStore.getRefreshToken() : authStore.getAccessToken());
    }
    return config;
  },
  (error) => {
    Promise.reject(error);
  },
);

apiClient.interceptors.response.use(
  (res) => {
    return res;
  },
  async (err) => {
    const originalConfig = err.config;
    const authStore = useAuthStore();

    if (originalConfig.url !== "/login" && err.response && authStore.getLoggedIn()) {
      if (err.response.status === 401 && !originalConfig._retry) {
        originalConfig._retry = true;
        try {
          const rs = await authStore.refresh();

          if (rs === true) {
            return apiClient(originalConfig);
          } else {
            loggerService.log("Refresh token no longer valid, requesting login!");
          }
        } catch (_error) {
          loggerService.error("Error during refresh. Refresh token no longer valid, requesting login!");
        }
      }
    }
    return Promise.reject(err);
  },
);
