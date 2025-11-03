import {defineStore} from "pinia";
import {apiClient} from "@/common/apiClient";
import type {ChannelItem} from "@/data/ChannelItem";
import {RemoteData} from "@/data/RemoteData";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
export const useChannelStore = defineStore({
  id: "channelStore",
  state: () => ({
    // Key is the uuid of the meta data
    currentChannels: new RemoteData(new Map<string, ChannelItem>()),
  }),
  getters: {
    getChannels: (state) => state.currentChannels.data.values(),
    getChannelsLoading: (state) => state.currentChannels.loading,
  },
  actions: {
    async loadChannels(n = 64) {
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
  },
});
