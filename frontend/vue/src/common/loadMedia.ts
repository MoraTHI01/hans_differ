import type {RouteLocationNormalized} from "vue-router";
import {useMediaStore} from "@/stores/media";
import {useAuthStore} from "@/stores/auth";
import router from "@/router/index";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
/**
 * Attempts to fetch a media item with a UUID in the query string from the media store and attaches the media item and UUID as route parameters.
 * If the media item is not in the store, it is fetched via a `getMedia` api.
 * If the uuid query parameter is missing or the media item is neither in the store nor accessible in the database the returned promise resolves to false.
 *
 * @param {RouteLocationNormalized} to - Location for a request which should contain a UUID query parameter
 *
 * @returns {Promise<boolean>} A promise which resolves to true if the media item could be loaded
 */
export async function routeToMedia(to: RouteLocationNormalized): Promise<boolean> {
  const uuid = to.query.uuid;
  // Stop processing and allow routing to display an error
  if (!uuid || Array.isArray(uuid)) {
    return true;
  }

  const auth = useAuthStore();
  if (!auth.getLoggedIn()) {
    auth.returnUrl = to.fullPath;
    router.push("/login");
    return false;
  }

  loggerService.log("routeToMedia:getMediaItemByUuid");
  const store = useMediaStore();
  let mediaitem = store.getMediaItemByUuid(uuid);
  // If the media item is not in the store already, load it from the API directly
  if (mediaitem === undefined) {
    loggerService.log("routeToMedia:getMedia");
    mediaitem = await store.getMedia(uuid);
    // Stop processing and allow routing to display an error
    if (mediaitem === undefined) {
      return true;
    }
  }

  to.params.uuid = uuid;
  return true;
}

export async function routeToRefreshMedia(to: RouteLocationNormalized): Promise<boolean> {
  const uuid = to.query.uuid;
  // Stop processing and allow routing to display an error
  if (!uuid || Array.isArray(uuid)) {
    return true;
  }

  const auth = useAuthStore();
  if (!auth.getLoggedIn()) {
    auth.returnUrl = to.fullPath;
    router.push("/login");
    return false;
  }

  const store = useMediaStore();
  loggerService.log("routeToMedia:getMedia");
  const mediaitem = await store.getMedia(uuid, true);
  // Stop processing and allow routing to display an error
  if (mediaitem === undefined) {
    return true;
  }

  to.params.uuid = uuid;
  return true;
}
