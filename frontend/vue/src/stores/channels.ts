import {defineStore} from "pinia";
import {apiClient} from "@/common/apiClient";
import type {ChannelItem} from "@/data/ChannelItem";
import {useAuthStore} from "@/stores/auth";
import {RemoteData} from "@/data/RemoteData";
import {LoggerService} from "@/common/loggerService";
import {DocumentItem} from "@/data/DocumentItem";

const loggerService = new LoggerService();
export const useChannelStore = defineStore({
  id: "channelStore",
  state: () => ({
    // Key is the uuid of the meta data
    currentChannels: new RemoteData(new Map<string, ChannelItem>()),
    userChannels: new RemoteData(new Map<string, ChannelItem>()),
    currentUserChannel: null as ChannelItem | null,
    channelDocuments: new RemoteData(new Map<string, DocumentItem>()),
    currentChannelDocuments: <DocumentItem[]>[],
  }),
  getters: {
    getChannels: (state) => state.currentChannels.data.values(),
    getChannelsLoading: (state) => state.currentChannels.loading,
    getChannelItemByUuid: (state) => (uuid: string) => {
      return state.currentChannels.data.get(uuid);
    },
    getUserChannels: (state) => state.userChannels.data.values(),
    getChannelDocumentsByUuid: (state) => (uuid: string) => state.channelDocuments.data.get(uuid),
    getChannelDocumentsLoading: (state) => state.channelDocuments.loading,
  },
  actions: {
    async loadChannels(n = 4096) {
      loggerService.log("loadChannels");
      // Start loading channel data
      this.currentChannels.startLoading(new Map());
      const {data} = await apiClient.get("/channels?n=" + n);
      loggerService.log(data);
      // Stores all channels in a map for fast lookup
      // Note that the Javascript Map preserves insertion order
      if ("result" in data && Object.keys(data.result).length > 0) {
        this.currentChannels.data = data.result.reduce(
          (map: Map<string, ChannelItem>, channel: ChannelItem) => map.set(channel.uuid, channel),
          new Map(),
        );
      }

      // Finish loading after successful or failed requests
      this.currentChannels.loading = false;
    },
    async loadUserChannels() {
      loggerService.log("loadUserChannels");
      this.userChannels.loading = true;
      this.userChannels.startLoading(new Map());
      const {data} = await apiClient.get("/my-channels");
      loggerService.log(data);
      // Stores all uploaded videos in a map for fast lookup
      // Note that the Javascript Map preserves insertion order
      if ("result" in data && Object.keys(data.result).length > 0) {
        this.userChannels.data = data.result.reduce(
          (map: Map<string, ChannelItem>, channel: ChannelItem) => map.set(channel.uuid, channel),
          new Map(),
        );
      }
      this.userChannels.loading = false;
    },
    setCurrentUserChannel(channel: ChannelItem) {
      this.currentUserChannel = channel;
      const serializedMap = JSON.stringify(this.currentUserChannel);
      const authStore = useAuthStore();
      const user_id = authStore.getUserId();
      sessionStorage.setItem("hans_current_channel_" + user_id, serializedMap);
    },
    getCurrentUserChannel() {
      if (this.currentUserChannel !== null) {
        return this.currentUserChannel;
      } else {
        const authStore = useAuthStore();
        const user_id = authStore.getUserId();
        // Retrieve the serialized Map from local storage
        const serializedMap = sessionStorage.getItem("hans_current_channel_" + user_id);
        if (serializedMap) {
          // Deserialize the JSON string back into a Map
          this.currentUserChannel = JSON.parse(serializedMap);
          return this.currentUserChannel;
        }
        return null;
      }
    },
    async loadChannelDocuments(channel_uuid: string) {
      console.log("loadChannelDocuments");
      this.channelDocuments.loading = true;
      this.channelDocuments.startLoading(new Map());
      const {data} = await apiClient.get("/getDocuments?uuid=" + channel_uuid);
      console.log(data);
      // Stores all uploaded videos in a map for fast lookup
      // Note that the Javascript Map preserves insertion order
      if ("result" in data && "data" in data.result && Object.keys(data.result.data).length > 0) {
        this.channelDocuments.complete(new Map([[channel_uuid, data.result]]));
        this.currentChannelDocuments = data.result.data;
      }
      console.log(this.channelDocuments.data);
      this.channelDocuments.loading = false;
      return this.currentChannelDocuments;
    },
  },
});
