// store.ts
import {defineStore} from "pinia";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();

export interface History {
  position: number;
  duration: number;
  access: string;
}

// Define the store
export const useHistoryStore = defineStore("history", {
  state: () => ({
    // key is the media item uuid
    mediaHistory: new Map<string, History>(),
    historyLoading: false,
  }),
  // Define getters to access computed values based on the state
  getters: {
    getMediaHistory: (state) => {
      return state.mediaHistory;
    },
    getHistoryLoading: (state) => {
      return state.historyLoading;
    },
    getHistoryForMediaItem: (state) => (uuid: string) => {
      return state.mediaHistory.get(uuid);
    },
    isMediaItemInHistory: (state) => (uuid: string) => {
      const foundMedia = state.mediaHistory.get(uuid);
      if (foundMedia !== undefined && foundMedia !== null) {
        return true;
      }
      return false;
    },
  },
  // Define actions that can modify the state
  actions: {
    async storeHistory() {
      loggerService.log("storeHistory");
      // Serialize the Map to a JSON string
      const serializableObject: {[key: string]: History} = {};
      this.mediaHistory.forEach((value, key) => {
        serializableObject[key] = value;
      });
      const serializedMap = JSON.stringify(serializableObject);
      // Store the serialized Map in local storage
      localStorage.setItem("hans_history", serializedMap);
    },
    async loadHistory() {
      loggerService.log("loadHistory");
      this.historyLoading = true;
      // Retrieve the serialized Map from local storage
      const serializedMap = localStorage.getItem("hans_history");

      if (serializedMap) {
        // Deserialize the JSON string back into a Map
        const jsonObject = JSON.parse(serializedMap);
        const deserializedMap = new Map<string, History>();
        // Iterate through the properties of the JavaScript object and populate the Map
        for (const key in jsonObject) {
          if (jsonObject.hasOwnProperty(key)) {
            deserializedMap.set(key, jsonObject[key]);
          }
        }
        this.mediaHistory = deserializedMap;
      } else {
        loggerService.log("No data found in local storage.");
      }
      this.historyLoading = false;
    },
    addHistory(uuid: string, currPosition: number, currDuration: number) {
      loggerService.log("addHistory");
      this.mediaHistory.set(uuid, {
        position: currPosition,
        duration: currDuration,
        access: new Date().toString(),
      } as History);
      this.storeHistory();
    },
  },
});
