import axios from "axios";
import {defineStore} from "pinia";
import {apiClient} from "@/common/apiClient";
import {MarkerResult, MarkerResultItem} from "@/data/MarkerResult";
import type {MediaItem} from "@/data/MediaItem";
import {Transcript, TranscriptResults, TranscriptResultsItem} from "@/data/Transcript";
import {QuestionnaireResults, QuestionnaireResult, QuestionnaireResultItem} from "@/data/QuestionnaireResult";
import {RemoteData} from "@/data/RemoteData";
import {SummaryResult, Summary} from "@/data/Summary";
import {TopicsResult, Topic, TopicItem} from "@/data/Topics";
import {AsrResults, AsrResultsItem} from "@/data/AsrResults";
import {SearchTrieResult, SearchTrie} from "@/data/SearchTrie";
import {Alignment, SlidesImagesMeta, SlidesImagesMetaResults, UrlClasses} from "@/data/SlidesImagesMeta";
import {Keywords, KeywordsResult, KeywordsResults} from "@/data/Keywords";
import {LoggerService} from "@/common/loggerService";
import {useAuthStore} from "@/stores/auth";

const loggerService = new LoggerService();

export const useMediaStore = defineStore({
  id: "mediaStore",
  state: () => ({
    // Key is the uuid of the meta data
    recentMedia: new RemoteData(new Map<string, MediaItem>()),
    uploadedMedia: new RemoteData(new Map<string, MediaItem>()),
    foundMedia: new RemoteData(new Map<string, MediaItem>()),
    transcripts: new RemoteData(new Map<string, Transcript>()),
    asrResults: new RemoteData(new Map<string, AsrResults>()),
    transcriptResults: new RemoteData(new Map<string, TranscriptResults>()),
    shortSummaries: new RemoteData(new Map<string, SummaryResult>()),
    summaries: new RemoteData(new Map<string, SummaryResult>()),
    searchTries: new RemoteData(new Map<string, SearchTrieResult>()),
    searchTriesSlides: new RemoteData(new Map<string, SearchTrieResult>()),
    topics: new RemoteData(new Map<string, TopicsResult>()),
    markers: new RemoteData(new Map<string, MarkerResult>()),
    questionnaireResults: new RemoteData(new Map<string, QuestionnaireResults>()),
    slidesImagesMetaResults: new RemoteData(new Map<string, SlidesImagesMetaResults>()),
    keywordsResults: new RemoteData(new Map<string, KeywordsResults>()),
    // Current single items in media view
    slides: "",
    alignment: null,
    externalLinks: new UrlClasses(),
    keywords: null,
    keywordsResult: new KeywordsResult(),
    slidesImageMeta: new SlidesImagesMeta(),
    asrResult: new AsrResults(),
    transcriptResult: new TranscriptResults(),
    shortSummary: new SummaryResult(),
    summary: new SummaryResult(),
    transcript: new Transcript(),
    topic: new TopicsResult(),
    marker: new MarkerResult(),
    searchTrie: new SearchTrieResult(),
    searchTrieSlides: new SearchTrieResult(),
    questionnaire: new QuestionnaireResults(),
    lastGlobalSearchterms: [] as string[],
    lastSearchMediaSearchterms: [] as string[],
    lastSearchMediaSortBy: [] as string[],
  }),
  getters: {
    getRecentMedia: (state) => state.recentMedia.data.values(),
    getRecentMediaLoading: (state) => state.recentMedia.loading,
    getUploadedMedia: (state) => state.uploadedMedia.data.values(),
    getUploadedMediaLoading: (state) => state.uploadedMedia.loading,
    getFoundMedia: (state) => state.foundMedia.data.values(),
    getFoundMediaLoading: (state) => state.foundMedia.loading,
    getMediaItemByUuid: (state) => (uuid: string) => {
      const foundMedia = state.foundMedia.data.get(uuid);
      if (foundMedia === undefined) {
        return state.recentMedia.data.get(uuid);
      }
      return foundMedia;
    },
    getSlidesByUuid: (state) => (uuid: string) => {
      const foundMedia = state.foundMedia.data.get(uuid);
      if (foundMedia === undefined) {
        return state.recentMedia.data.get(uuid)?.slides;
      }
      return foundMedia?.slides;
    },
    getSlidesImagesFolderUrnByUuid: (state) => (uuid: string) => {
      const foundMedia = state.foundMedia.data.get(uuid);
      if (foundMedia === undefined) {
        return state.recentMedia.data.get(uuid)?.slides_images_folder;
      }
      return foundMedia?.slides_images_folder;
    },
    getSlidesImagesMetaResultsByUuid: (state) => (uuid: string) => state.slidesImagesMetaResults.data.get(uuid),
    getSlidesImagesMetaResultsLoading: (state) => state.slidesImagesMetaResults.loading,
    getAlignment: (state) => state.alignment,
    getExternalLinks: (state) => state.externalLinks,
    getKeywords: (state) => state.keywords,
    getAsrResultsByUuid: (state) => (uuid: string) => state.asrResults.data.get(uuid),
    getAsrResultsLoading: (state) => state.asrResults.loading,
    getTranscriptResultsByUuid: (state) => (uuid: string) => state.transcriptResults.data.get(uuid),
    getTranscriptResultsLoading: (state) => state.transcriptResults.loading,
    getCurrentTranscriptText: (state) => (locale: string) => {
      loggerService.log("getCurrentTranscriptText");
      let found = false;
      let comp_transcript = "";
      for (const item of state.transcriptResult.data) {
        loggerService.log("item");
        loggerService.log(item);
        if (item.language === locale) {
          const result = item.result;
          found = true;
          loggerService.log("result");
          loggerService.log(result);
          for (const subItem of result.result) {
            comp_transcript = comp_transcript + subItem.transcript_formatted + " ";
          }
          loggerService.log("comp_transcript");
          loggerService.log(comp_transcript);
        }
      }
      if (found === true) {
        return comp_transcript.trim();
      }
      return undefined;
    },
    getIntervalFromCurrentTranscriptText: (state) => (locale: string, match_text: string) => {
      loggerService.log("getIntervalFromCurrentTranscriptText");
      for (const item of state.transcriptResult.data) {
        loggerService.log("item");
        loggerService.log(item);
        if (item.language === locale) {
          const result = item.result;
          let start_interval_set = false;
          //let curr_start_interval = -1.0;
          let curr_end_interval = -1.0;
          let start_interval = -1.0;
          let end_interval = -1.0;
          for (const subItem of result.result) {
            if (match_text.includes(subItem.transcript_formatted)) {
              if (start_interval_set === false) {
                // use the end interval before the utterance
                start_interval = curr_end_interval;
                start_interval_set = true;
              }
              //curr_start_interval = subItem.interval[0];
              end_interval = subItem.interval[1];
            }
            curr_end_interval = subItem.interval[1];
          }
          if (start_interval < 0) {
            start_interval = 0;
          }
          loggerService.log("Matching interval");
          loggerService.log([start_interval, end_interval]);
          return [start_interval, end_interval];
        }
      }
      return undefined;
    },
    getCurrentTranscriptTextInInterval: (state) => (locale: string, interval: [number, number]) => {
      loggerService.log("getCurrentTranscriptTextInInterval");
      let found = false;
      let comp_transcript = "";
      for (const item of state.transcriptResult.data) {
        loggerService.log("item");
        loggerService.log(item);
        if (item.language === locale) {
          const result = item.result;
          found = true;
          loggerService.log("result");
          loggerService.log(result);
          for (const subItem of result.result) {
            if (subItem.interval[0] >= interval[0] && subItem.interval[1] <= interval[1]) {
              comp_transcript = comp_transcript + subItem.transcript_formatted + " ";
            }
          }
          loggerService.log("comp_transcript_from_interval");
          loggerService.log(comp_transcript);
        }
      }
      if (found === true) {
        return comp_transcript.trim();
      }
      return undefined;
    },
    getShortSummaryByUuid: (state) => (uuid: string) => state.shortSummaries.data.get(uuid),
    getShortSummariesLoading: (state) => state.shortSummaries.loading,
    getSummaryByUuid: (state) => (uuid: string) => state.summaries.data.get(uuid),
    getSummariesLoading: (state) => state.summaries.loading,
    getTopicsByUuid: (state) => (uuid: string) => state.topics.data.get(uuid),
    getTopicsLoading: (state) => state.topics.loading,
    getTranscriptByUuid: (state) => (uuid: string) => state.transcripts.data.get(uuid),
    getTranscriptLoading: (state) => state.transcripts.loading,
    getMarkerByUuid: (state) => (uuid: string) => state.markers.data.get(uuid),
    getMarkersLoading: (state) => state.markers.loading,
    getSearchTrieByUuid: (state) => (uuid: string) => state.searchTries.data.get(uuid),
    getSearchTrieLoading: (state) => state.searchTries.loading,
    getSearchTrieSlidesByUuid: (state) => (uuid: string) => state.searchTriesSlides.data.get(uuid),
    getSearchTrieSlidesLoading: (state) => state.searchTriesSlides.loading,
    getSlides: (state) => state.slides,
    getTranscript: (state) => state.transcript,
    getMarker: (state) => state.marker.result,
    getSearchTrie: (state) => state.searchTrie.data,
    getSearchTrieSlides: (state) => state.searchTrieSlides.data,
    getLastGlobalSearchterms: (state) => state.lastGlobalSearchterms,
    getQuestionnaireResultsByUuid: (state) => (uuid: string) => state.questionnaireResults.data.get(uuid),
    getQuestionnaireResultsLoading: (state) => state.questionnaireResults.loading,
    getKeywordsResultsByUuid: (state) => (uuid: string) => state.keywordsResults.data.get(uuid),
    getKeywordsResultsLoading: (state) => state.keywordsResults.loading,
  },
  actions: {
    getSwitchSlidesAndVideo() {
      const authStore = useAuthStore();
      const user_id = authStore.getUserId();
      const value = localStorage.getItem("hans_switchSlidesVideo_" + user_id);
      if (value === undefined || value === null) {
        return false;
      }
      return value;
    },
    setSwitchSlidesAndVideo(value: boolean) {
      const authStore = useAuthStore();
      const user_id = authStore.getUserId();
      if (value === true) {
        localStorage.setItem("hans_switchSlidesVideo_" + user_id, value);
      } else {
        localStorage.removeItem("hans_switchSlidesVideo_" + user_id);
      }
    },
    async setLastGlobalSearchterms(globalsearchterms: string[]) {
      this.lastGlobalSearchterms = globalsearchterms;
    },
    async redoLastSearchMedia() {
      await this.searchMedia(this.lastSearchMediaSearchterms, this.lastSearchMediaSortBy);
    },
    async searchMedia(searchterms: string[], fieldterms: string[], sortby: Array<string>) {
      loggerService.log("searchMedia");
      this.lastSearchMediaSearchterms = searchterms;
      if (sortby === undefined) {
        sortby = this.lastSearchMediaSortBy;
      }
      this.lastSearchMediaSortBy = sortby;
      this.foundMedia.startLoading(new Map());
      const {data} = await apiClient.get("/search?q=" + searchterms + "&f=" + fieldterms);
      loggerService.log(data);
      // Stores all recent videos in a map for fast lookup
      // Note that the Javascript Map preserves insertion order
      if ("result" in data === true && Object.keys(data.result).length > 0) {
        let foundMedia: Map<string, MediaItem> = data.result.reduce(
          (mediaItems: Map<string, MediaItem>, currentValue: MediaItem) =>
            mediaItems.set(currentValue.uuid, currentValue),
          new Map(),
        );
        if (sortby !== undefined && sortby.length > 0) {
          loggerService.log("SortBy");
          loggerService.log(sortby);
          // Sort by course, lecturer and title
          const sortedMedia = Array.from(foundMedia).sort(([_keyA, valueA], [_keyB, valueB]): number => {
            return (
              valueA.description.course.localeCompare(valueB.description.course) ||
              valueA.description.lecturer.localeCompare(valueB.description.lecturer) ||
              valueA.title.localeCompare(valueB.title)
            );
          });
          this.foundMedia.complete(new Map(sortedMedia));
        }
        // Load additonal meta data by url
        // this.foundMedia.data.forEach((value: MediaItem, key: string) => {
        //  // Currently only short summary is displayed in SearchResultsView
        //  this.loadShortSummary(key);
        //  //this.loadSummary(key);
        //});
      } else {
        // No media was found
        this.foundMedia.loading = false;
      }
    },
    async loadRecentMedia(n = 32) {
      loggerService.log("loadRecentMedia");
      this.recentMedia.startLoading(new Map());
      const {data} = await apiClient.get("/recent?n=" + n);
      loggerService.log(data);
      // Stores all recent videos in a map for fast lookup
      // Note that the Javascript Map preserves insertion order
      if ("result" in data === true && Object.keys(data.result).length > 0) {
        this.recentMedia.data = data.result.reduce(
          (items: Map<string, MediaItem>, currentValue: MediaItem) => items.set(currentValue.uuid, currentValue),
          new Map(),
        );
        // Load additonal meta data by url, skipped here not needed for HomeView
        //this.recentMedia.data.forEach((value: MediaItem, key: string) => {
        //  this.loadShortSummary(key);
        //  this.loadSummary(key);
        //});
      }

      // Finish loading after successful or failed requests
      this.recentMedia.loading = false;
    },
    async loadUploadedMedia(channel_uuid: string, channel_course_acronym: string) {
      loggerService.log("loadUploadedMedia");
      this.uploadedMedia.loading = true;
      this.uploadedMedia.startLoading(new Map());
      const {data} = await apiClient.get(
        "/my-lectures?uuid=" + channel_uuid + "&course_acronym=" + channel_course_acronym,
      );
      loggerService.log(data);
      // Stores all uploaded videos in a map for fast lookup
      // Note that the Javascript Map preserves insertion order
      if ("result" in data && Object.keys(data.result).length > 0) {
        this.uploadedMedia.data = data.result.reduce(
          (items: Map<string, MediaItem>, currentValue: MediaItem) => items.set(currentValue.uuid!, currentValue),
          new Map(),
        );
      }
      this.uploadedMedia.loading = false;
    },
    async getMedia(uuid: string, forceReload: boolean = false) {
      loggerService.log("getMedia");
      try {
        let mediaitem = this.getMediaItemByUuid(uuid);
        // If the media item is not in the store already, get it from the API directly
        if (forceReload || mediaitem === undefined) {
          loggerService.log("getMedia:apiClient");
          this.foundMedia.loading = true;
          const data = await apiClient.get("/getMedia?uuid=" + uuid);
          loggerService.log("data");
          // Expects getMedia API result to be a list with a single item
          const [media] = data.data.result;
          this.foundMedia.data.set(media.uuid, media);
          mediaitem = media;
          this.foundMedia.loading = false;
        }
        return mediaitem;
      } catch (error: any) {
        loggerService.error(error);
        // Handle 404 errors gracefully
        if (error.response.status == 404) {
          return undefined;
        }
        alert(error);
      }
    },
    async loadSlides(uuid: string) {
      loggerService.log("loadSlides");
      this.slides = "";
      try {
        let currentSlides = this.getSlidesByUuid(uuid);
        // If the transcript is not in the store already, get it from the mediaItem and load it
        if (!currentSlides) {
          let mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem) {
            // If no media item was found, load the transcript from the API directly
            loggerService.log("loadSlides:getSlidesUseGetMedia");
            await this.getMedia(uuid);
            mediaitem = this.getMediaItemByUuid(uuid);
          }
          loggerService.log("loadTranscript:getTranscriptFromMediaItem");
          loggerService.log(mediaitem);
          currentSlides = mediaitem?.slides;
        }
        if (!currentSlides) {
          loggerService.error("loadSlides: currentSlides empty!");
          return;
        }
        this.slides = currentSlides;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return;
      }
    },
    async loadSlidesImagesMeta(uuid: string, forceReload: boolean = false) {
      loggerService.log("loadSlidesImagesMetaResults");
      try {
        let currentSlidesImagesMeta = this.getSlidesImagesMetaResultsByUuid(uuid);
        // If the questionnaires (de + en) are not in the store already, get it from the mediaItem and load it
        if (!currentSlidesImagesMeta || forceReload) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem || forceReload) {
            // If no questionnaire item was found, load the  summary from the API directly
            loggerService.log("loadSlidesImagesMetaResults:getSlidesImagesMetaFromApi");
            this.slidesImagesMetaResults.loading = true;
            const {data} = await apiClient.get("/getSlidesImagesMeta?uuid=" + uuid);
            //console.log(data);
            loggerService.log(data);
            if ("result" in data && "data" in data.result && Object.keys(data.result.data).length > 0) {
              this.slidesImagesMetaResults.complete(new Map([[uuid, data.result]]));
              currentSlidesImagesMeta = this.getSlidesImagesMetaResultsByUuid(uuid);
              const curr_align: Alignment = data.result.data[0].alignment;
              loggerService.log("loadSlidesImagesMetaResults:alignment:");
              this.alignment = curr_align;
              loggerService.log(this.alignment);

              this.externalLinks = data.result.data[0].urls_by_class;
              loggerService.log("loadSlidesImagesMetaResults:externalLinks:");
              loggerService.log(this.externalLinks);
            } else {
              this.slidesImagesMetaResults.loading = false;
            }
          } else {
            loggerService.log("loadSlidesImagesMetaResults:getSlidesImagesMetaFromMediaItem");
            loggerService.log(`loadSlidesImagesMetaResults:url: ${mediaitem.slides_images_meta}`);

            this.slidesImagesMetaResults.loading = true;

            const currentSlidesImagesMetaResults = new SlidesImagesMetaResults();
            currentSlidesImagesMetaResults.data = [];
            const response_slides_meta = await axios.get(mediaitem.slides_images_meta, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            loggerService.log("loadSlidesImagesMetaResults:response:");
            loggerService.log(response_slides_meta.data);

            const curr_align: Alignment = response_slides_meta.data.alignment;
            loggerService.log("loadSlidesImagesMetaResults:alignment:");
            this.alignment = curr_align;
            loggerService.log(this.alignment);

            this.externalLinks = response_slides_meta.data.urls_by_class;
            loggerService.log("loadSlidesImagesMetaResults:externalLinks:");
            loggerService.log(this.externalLinks);

            //currentSlidesImagesMetaResults.data?.push(response_slides_meta.data);
            //currentSlidesImagesMetaResults.result = "success";
            //// Store current transcript with the others for future retrieval
            //this.slidesImagesMetaResults.data.set(mediaitem.uuid, currentSlidesImagesMetaResults);
            //loggerService.log(currentSlidesImagesMeta);
            currentSlidesImagesMeta = response_slides_meta.data;
            this.slidesImagesMetaResults.loading = false;
          }
        }
        if (!currentSlidesImagesMeta || !this.alignment || !this.externalLinks) {
          loggerService.error("loadSlidesImagesMetaResults: currentSlidesImagesMeta empty!");
          return undefined;
        }
        this.slidesImageMeta = currentSlidesImagesMeta;
        return currentSlidesImagesMeta;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadTranscript(uuid: string) {
      loggerService.log("loadTranscript");
      try {
        let currentTranscript = this.getTranscriptByUuid(uuid);
        // If the transcript is not in the store already, get it from the mediaItem and load it
        if (!currentTranscript) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem) {
            // If no media item was found, load the transcript from the API directly
            loggerService.log("loadTranscript:getTranscriptFromApi");
            this.transcripts.loading = true;
            const {data} = await apiClient.get("/getTranscript?uuid=" + uuid);
            if ("data" in data && "result" in data.data && Object.keys(data.data.result).length > 0) {
              this.transcripts.complete(
                data.data.result.reduce(
                  (transcripts: Map<string, Transcript>, currentValue: Transcript) =>
                    transcripts.set(uuid, currentValue),
                  new Map(),
                ),
              );
              currentTranscript = this.getTranscriptByUuid(uuid);
            } else {
              this.transcripts.loading = false;
            }
          } else {
            loggerService.log("loadTranscript:getTranscriptFromMediaItem");
            loggerService.log(mediaitem);
            this.transcripts.loading = true;
            const response = await axios.get(mediaitem.transcript, {headers: {"Access-Control-Allow-Origin": "*"}});
            currentTranscript = new Transcript(response.data);
            // Store current transcript with the others for future retrieval
            this.transcripts.data.set(mediaitem.uuid, currentTranscript);
            this.transcripts.loading = false;
          }
        }
        if (!currentTranscript) {
          loggerService.error("loadTranscript: currentTranscript empty!");
          return undefined;
        }
        this.transcript = currentTranscript;
        return currentTranscript;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadMarker(uuid: string) {
      loggerService.log("loadMarker");
      this.marker = new MarkerResult();
      try {
        let currentMarker = this.getMarkerByUuid(uuid);
        // If the marker is not in the store already, get it from the mediaItem and load it
        if (!currentMarker) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem) {
            // If no media item was found, load the marker from the API directly
            loggerService.log("loadMarker:getMarkerFromApi");
            const {data} = await apiClient.get("/getMarker?uuid=" + uuid);
            if ("data" in data === true && "result" in data.data === true && Object.keys(data.data.result).length > 0) {
              this.markers.complete(
                data.data.result.reduce(
                  (markers: Map<string, MarkerResult>, currentValue: MarkerResult) => markers.set(uuid, currentValue),
                  new Map(),
                ),
              );
              currentMarker = this.getMarkerByUuid(uuid);
            }
          } else {
            loggerService.log("loadMarker:getMarkerFromMediaItem");
            loggerService.log(mediaitem);
            this.markers.loading = true;
            const response = await axios.get(mediaitem.marker, {headers: {"Access-Control-Allow-Origin": "*"}});
            currentMarker = new MarkerResult(response.data);
            // Store current marker with the others for future retrieval
            this.markers.data.set(mediaitem.uuid, currentMarker);
            this.markers.loading = false;
          }
        }
        if (!currentMarker) {
          loggerService.error("loadMarker: currentMarker empty!");
          return;
        }
        this.marker = currentMarker;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return;
      }
    },
    async loadAsrResults(uuid: string) {
      loggerService.log("loadAsrResults");
      try {
        let currentAsrResults = this.getAsrResultsByUuid(uuid);
        // If the short summary (de + en) is not in the store already, get it from the mediaItem and load it
        if (!currentAsrResults) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem) {
            // If no media item was found, load the short summary from the API directly
            loggerService.log("loadAsrResults:getAsrResultsFromApi");
            this.asrResults.loading = true;
            const {data} = await apiClient.get("/getAsrResults?uuid=" + uuid);
            loggerService.log(data);
            if ("data" in data && "result" in data.data && Object.keys(data.data.result).length > 0) {
              this.asrResults.complete(
                data.data.result.reduce(
                  (asrResults: Map<string, AsrResults>, currentValue: AsrResults) => asrResults.set(uuid, currentValue),
                  new Map(),
                ),
              );
              currentAsrResults = this.getAsrResultsByUuid(uuid);
            } else {
              this.asrResults.loading = false;
            }
          } else {
            loggerService.log("loadAsrResults:getAsrResultsFromMediaItem");
            loggerService.log(mediaitem);
            this.asrResults.loading = true;

            currentAsrResults = new AsrResults();
            currentAsrResults.data = [];
            const response_de = await axios.get(mediaitem.asr_result_de, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentAsrResults.data?.push(
              new AsrResultsItem({type: "AsrResult", language: "de", result: response_de.data}),
            );
            const response_en = await axios.get(mediaitem.asr_result_en, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentAsrResults.data?.push(
              new AsrResultsItem({type: "AsrResult", language: "en", result: response_en.data}),
            );
            currentAsrResults.result = "success";

            // Store current asr results with the others for future retrieval
            this.asrResults.data.set(mediaitem.uuid, currentAsrResults);
            loggerService.log(currentAsrResults.data);
            this.asrResults.loading = false;
          }
        }
        if (!currentAsrResults) {
          loggerService.error("loadAsrResults: currentAsrResults empty!");
          return undefined;
        }
        this.asrResult = currentAsrResults;
        return currentAsrResults;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadTranscriptResults(uuid: string) {
      loggerService.log("loadTranscriptResults");
      try {
        let currentTranscriptResults = this.getTranscriptResultsByUuid(uuid);
        // If the short summary (de + en) is not in the store already, get it from the mediaItem and load it
        if (!currentTranscriptResults) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem) {
            // If no media item was found, load the short summary from the API directly
            loggerService.log("loadTranscriptResults:getTranscriptResultsFromApi");
            this.transcriptResults.loading = true;
            const {data} = await apiClient.get("/getTranscriptResults?uuid=" + uuid);
            loggerService.log(data);
            if ("data" in data && "result" in data.data && Object.keys(data.data.result).length > 0) {
              this.transcriptResults.complete(
                data.data.result.reduce(
                  (transcriptResults: Map<string, TranscriptResults>, currentValue: TranscriptResults) =>
                    transcriptResults.set(uuid, currentValue),
                  new Map(),
                ),
              );
              currentTranscriptResults = this.getTranscriptResultsByUuid(uuid);
            } else {
              this.transcriptResults.loading = false;
            }
          } else {
            loggerService.log("loadTranscriptResults:getTranscriptResultsFromMediaItem");
            loggerService.log(mediaitem);
            this.transcriptResults.loading = true;

            currentTranscriptResults = new TranscriptResults();
            currentTranscriptResults.data = [];
            const response_de = await axios.get(mediaitem.transcript_de, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentTranscriptResults.data?.push(
              new TranscriptResultsItem({type: "TranscriptResult", language: "de", result: response_de.data}),
            );
            const response_en = await axios.get(mediaitem.transcript_en, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentTranscriptResults.data?.push(
              new TranscriptResultsItem({type: "TranscriptResult", language: "en", result: response_en.data}),
            );
            currentTranscriptResults.result = "success";

            // Store current transcript results with the others for future retrieval
            this.transcriptResults.data.set(mediaitem.uuid, currentTranscriptResults);
            loggerService.log(currentTranscriptResults.data);
            this.transcriptResults.loading = false;
          }
        }
        if (!currentTranscriptResults) {
          loggerService.error("loadTranscriptResults: currentTranscriptResults empty!");
          return undefined;
        }
        this.transcriptResult = currentTranscriptResults;
        return currentTranscriptResults;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadShortSummary(uuid: string, forceReload: boolean = false) {
      loggerService.log("loadShortSummary");
      try {
        let currentShortSummary = this.getShortSummaryByUuid(uuid);
        // If the short summary (de + en) is not in the store already, get it from the mediaItem and load it
        if (!currentShortSummary || forceReload) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem || forceReload) {
            // If no media item was found, load the short summary from the API directly
            loggerService.log("loadShortSummary:getShortSummaryFromApi");
            this.shortSummaries.loading = true;
            const {data} = await apiClient.get("/getShortSummary?uuid=" + uuid);
            loggerService.log(data);
            if ("result" in data && "data" in data.result && Object.keys(data.result.data).length > 0) {
              this.shortSummaries.complete(new Map([[uuid, data.result]]));
              currentShortSummary = this.getShortSummaryByUuid(uuid);
            } else {
              this.shortSummaries.loading = false;
            }
          } else {
            loggerService.log("loadShortSummary:getShortSummaryFromMediaItem");
            loggerService.log(mediaitem);
            this.shortSummaries.loading = true;

            currentShortSummary = new SummaryResult();
            currentShortSummary.data = [];
            const response_de = await axios.get(mediaitem.short_summary_result_de, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentShortSummary.data?.push(new Summary(response_de.data));
            const response_en = await axios.get(mediaitem.short_summary_result_en, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentShortSummary.data?.push(new Summary(response_en.data));
            currentShortSummary.result = "success";

            // Store current transcript with the others for future retrieval
            this.shortSummaries.data.set(mediaitem.uuid, currentShortSummary);
            loggerService.log(currentShortSummary.data);
            this.shortSummaries.loading = false;
          }
        }
        if (!currentShortSummary) {
          loggerService.error("loadShortSummary: currentShortSummary empty!");
          return undefined;
        }
        this.shortSummary = currentShortSummary;
        return currentShortSummary;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadSummary(uuid: string, forceReload: boolean = false) {
      loggerService.log("loadSummary");
      try {
        let currentSummary = this.getSummaryByUuid(uuid);
        // If the summary (de + en) is not in the store already, get it from the mediaItem and load it
        if (!currentSummary || forceReload) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem || forceReload) {
            // If no media item was found, load the  summary from the API directly
            loggerService.log("loadSummary:getSummaryFromApi");
            this.summaries.loading = true;
            const {data} = await apiClient.get("/getSummary?uuid=" + uuid);
            loggerService.log(data);
            if ("result" in data && "data" in data.result && Object.keys(data.result.data).length > 0) {
              this.summaries.complete(new Map([[uuid, data.result]]));
              currentSummary = this.getSummaryByUuid(uuid);
            } else {
              this.summaries.loading = false;
            }
          } else {
            loggerService.log("loadSummary:getSummaryFromMediaItem");
            loggerService.log(mediaitem);
            this.summaries.loading = true;

            currentSummary = new SummaryResult();
            currentSummary.data = [];
            const response_de = await axios.get(mediaitem.summary_result_de, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentSummary.data?.push(new Summary(response_de.data));
            const response_en = await axios.get(mediaitem.summary_result_en, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentSummary.data?.push(new Summary(response_en.data));
            currentSummary.result = "success";

            // Store current transcript with the others for future retrieval
            this.summaries.data.set(mediaitem.uuid, currentSummary);
            loggerService.log(currentSummary.data);
            this.summaries.loading = false;
          }
        }
        if (!currentSummary) {
          loggerService.error("loadSummary: currentSummary empty!");
          return undefined;
        }
        this.summary = currentSummary;
        return currentSummary;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadTopics(uuid: string, forceReload: boolean = false) {
      loggerService.log("loadTopics");
      try {
        let currentTopics = this.getTopicsByUuid(uuid);
        // If the topics (de + en) are not in the store already, get it from the mediaItem and load it
        if (!currentTopics || forceReload) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem || forceReload) {
            // If no media item was found, load the  summary from the API directly
            loggerService.log("loadTopics:getTopicsFromApi");
            this.summaries.loading = true;
            const {data} = await apiClient.get("/getTopics?uuid=" + uuid);
            //console.log(data);
            loggerService.log(data);
            if ("result" in data && "data" in data.result && Object.keys(data.result.data).length > 0) {
              this.topics.complete(new Map([[uuid, data.result]]));
              currentTopics = this.getTopicsByUuid(uuid);
            } else {
              this.topics.loading = false;
            }
          } else {
            loggerService.log("loadTopics:getTopicsFromMediaItem");
            loggerService.log(mediaitem);
            this.topics.loading = true;

            currentTopics = new TopicsResult();
            currentTopics.data = [];
            const response_de = await axios.get(mediaitem.topic_result_de, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentTopics.data?.push(new Topic(response_de.data));
            const response_en = await axios.get(mediaitem.topic_result_en, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentTopics.data?.push(new Topic(response_en.data));
            currentTopics.result = "success";

            // Store current transcript with the others for future retrieval
            this.topics.data.set(mediaitem.uuid, currentTopics);
            loggerService.log(currentTopics.data);
            this.topics.loading = false;
          }
        }
        if (!currentTopics) {
          loggerService.error("loadTopics: currentTopics empty!");
          return undefined;
        }
        this.topic = currentTopics;
        return currentTopics;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadMarkersFromTopics(uuid: string, locale: string) {
      loggerService.log("loadMarkersFromTopics");
      const secondsToTimeString = (seconds: number): string => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const remainingSeconds = Math.floor(seconds % 60);

        const hoursStr = hours < 10 ? `0${hours}` : `${hours}`;
        const minutesStr = minutes < 10 ? `0${minutes}` : `${minutes}`;
        const secondsStr = remainingSeconds < 10 ? `0${remainingSeconds}` : `${remainingSeconds}`;

        return `${hoursStr}:${minutesStr}:${secondsStr}`;
      };
      try {
        let currentTopics = this.getTopicsByUuid(uuid);
        // If the topics (de + en) are not in the store already, get it from the mediaItem and load it
        if (!currentTopics) {
          currentTopics = await this.loadTopics(uuid);
        }
        if (!currentTopics || currentTopics.data?.length < 1) {
          loggerService.error("loadMarkersFromTopics: currentTopics empty!");
          return undefined;
        }

        let currentMarker = new MarkerResult();
        currentMarker.result = [];
        let tempTitleList = Array<string>();
        loggerService.log(currentTopics.data);

        for (const item in currentTopics.data) {
          const topic = currentTopics.data[item] as Topic;
          loggerService.log(topic);
          if (topic.language === locale) {
            loggerService.log(locale);
            for (const tItem in topic.result) {
              const topicItem = topic.result[tItem] as TopicItem;
              loggerService.log(topicItem);
              // Avoid duplicate entries
              if (!tempTitleList.includes(topicItem.title)) {
                const markerItem = new MarkerResultItem();
                markerItem.type = "Chapter";
                markerItem.result_index = topicItem.result_index;
                markerItem.interval = topicItem.interval;
                markerItem.value = topicItem.title;
                markerItem.title = topicItem.title;
                markerItem.summary = topicItem.summary;
                markerItem.time = secondsToTimeString(topicItem.interval[0]);
                currentMarker.result.push(markerItem);
                tempTitleList.push(topicItem.title);
              }
            }
          }
        }
        if (!currentMarker || currentMarker.result.length < 1) {
          loggerService.error("loadMarkersFromTopics: currentMarker empty!");
          return undefined;
        }
        loggerService.log(currentMarker.result);
        // Store current markers with the others for future retrieval
        this.markers.data.set(uuid, currentMarker);
        this.marker = currentMarker;
        return currentMarker;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadSearchTrie(uuid: string) {
      loggerService.log("loadSearchTrie");
      try {
        let currentSearchTrie = this.getSearchTrieByUuid(uuid);
        // If the short search trie (de + en) is not in the store already, get it from the mediaItem and load it
        if (!currentSearchTrie) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem) {
            // If no media item was found, load the search trie from the API directly
            loggerService.log("loadSearchTrie:getSearchTrieFromApi");
            this.searchTries.loading = true;
            const {data} = await apiClient.get("/getSearchTrie?uuid=" + uuid);
            loggerService.log(data);
            if ("data" in data && "result" in data.data && Object.keys(data.data.result).length > 0) {
              this.searchTries.complete(
                data.data.result.reduce(
                  (searchTries: Map<string, SearchTrieResult>, currentValue: SearchTrieResult) =>
                    searchTries.set(uuid, currentValue),
                  new Map(),
                ),
              );
              currentSearchTrie = this.getSearchTrieByUuid(uuid);
            } else {
              this.searchTries.loading = false;
            }
          } else {
            loggerService.log("loadSearchTrie:getSearchTrieFromMediaItem");
            loggerService.log(mediaitem);
            this.searchTries.loading = true;

            currentSearchTrie = new SearchTrieResult();
            currentSearchTrie.data = [];
            const response_de = await axios.get(mediaitem.search_trie_de, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            loggerService.log("loadSearchTrie:response_de");
            loggerService.log(response_de.data);
            currentSearchTrie.data?.push(new SearchTrie(response_de.data));
            const response_en = await axios.get(mediaitem.search_trie_en, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            loggerService.log("loadSearchTrie:response_en");
            loggerService.log(response_en.data);
            currentSearchTrie.data?.push(new SearchTrie(response_en.data));
            currentSearchTrie.result = "success";
            loggerService.log("loadSearchTrie:currentSearchTrie");
            loggerService.log(currentSearchTrie);

            // Store current transcript with the others for future retrieval
            this.searchTries.data.set(mediaitem.uuid, currentSearchTrie);
            loggerService.log(currentSearchTrie.data);
            this.searchTries.loading = false;
          }
        }
        if (!currentSearchTrie) {
          loggerService.error("loadSearchTrie: currentSearchTrie empty!");
          return undefined;
        }
        this.searchTrie = currentSearchTrie;
        return currentSearchTrie;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadSearchTrieSlides(uuid: string) {
      loggerService.log("loadSearchTrieSlides");
      try {
        let currentSearchTrieSlides = this.getSearchTrieSlidesByUuid(uuid);
        // If the short search trie (de + en) is not in the store already, get it from the mediaItem and load it
        if (!currentSearchTrieSlides) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem) {
            // If no media item was found, load the search trie from the API directly
            loggerService.log("loadSearchTrieSlides:getSearchTrieSlidesFromApi");
            this.searchTriesSlides.loading = true;
            const {data} = await apiClient.get("/getSearchTrieSlides?uuid=" + uuid);
            loggerService.log(data);
            if ("data" in data && "result" in data.data && Object.keys(data.data.result).length > 0) {
              this.searchTriesSlides.complete(
                data.data.result.reduce(
                  (searchTriesSlides: Map<string, SearchTrieResult>, currentValue: SearchTrieResult) =>
                    searchTriesSlides.set(uuid, currentValue),
                  new Map(),
                ),
              );
              currentSearchTrieSlides = this.getSearchTrieSlidesByUuid(uuid);
            } else {
              this.searchTriesSlides.loading = false;
            }
          } else {
            loggerService.log("loadSearchTrieSlides:getSearchTrieSlidesFromMediaItem");
            loggerService.log(mediaitem);
            this.searchTriesSlides.loading = true;

            currentSearchTrieSlides = new SearchTrieResult();
            currentSearchTrieSlides.data = [];
            const response_trie = await axios.get(mediaitem.slides_trie, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            loggerService.log("loadSearchTrieSlides:response_trie");
            loggerService.log(response_trie.data);
            currentSearchTrieSlides.data?.push(new SearchTrie(response_trie.data));
            currentSearchTrieSlides.result = "success";
            loggerService.log("loadSearchTrieSlides:currentSearchTrieSlides");
            loggerService.log(currentSearchTrieSlides);

            // Store current transcript with the others for future retrieval
            this.searchTriesSlides.data.set(mediaitem.uuid, currentSearchTrieSlides);
            loggerService.log(currentSearchTrieSlides.data);
            this.searchTriesSlides.loading = false;
          }
        }
        if (!currentSearchTrieSlides) {
          loggerService.error("loadSearchTrieSlides: currentSearchTrieSlides empty!");
          return undefined;
        }
        this.searchTrieSlides = currentSearchTrieSlides;
        return currentSearchTrieSlides;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadQuestionnaire(uuid: string, forceReload: boolean = false) {
      loggerService.log("loadQuestionnaire");
      try {
        let currentQuestionnaire = this.getQuestionnaireResultsByUuid(uuid);
        // If the questionnaires (de + en) are not in the store already, get it from the mediaItem and load it
        if (!currentQuestionnaire || forceReload) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem || forceReload) {
            // If no questionnaire item was found, load the  summary from the API directly
            loggerService.log("loadQuestionnaire:getQuestionnaireFromApi");
            this.questionnaireResults.loading = true;
            const {data} = await apiClient.get("/getQuestionnaire?uuid=" + uuid);
            //console.log(data);
            loggerService.log(data);
            if ("result" in data && "data" in data.result && Object.keys(data.result.data).length > 0) {
              this.questionnaireResults.complete(new Map([[uuid, data.result]]));
              currentQuestionnaire = this.getQuestionnaireResultsByUuid(uuid);
            } else {
              this.questionnaireResults.loading = false;
            }
          } else {
            loggerService.log("loadQuestionnaire:getQuestionnaireFromMediaItem");
            loggerService.log(mediaitem);
            this.questionnaireResults.loading = true;

            currentQuestionnaire = new QuestionnaireResults();
            currentQuestionnaire.data = [];
            const response_de = await axios.get(mediaitem.questionnaire_result_de, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentQuestionnaire.data?.push(new QuestionnaireResult(response_de.data));
            const response_en = await axios.get(mediaitem.questionnaire_result_en, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            currentQuestionnaire.data?.push(new QuestionnaireResult(response_en.data));
            currentQuestionnaire.result = "success";

            // Store current transcript with the others for future retrieval
            this.questionnaireResults.data.set(mediaitem.uuid, currentQuestionnaire);
            loggerService.log(currentQuestionnaire.data);
            this.questionnaireResults.loading = false;
          }
        }
        if (!currentQuestionnaire) {
          loggerService.error("loadQuestionnaire: currentQuestionnaire empty!");
          return undefined;
        }
        this.questionnaire = currentQuestionnaire;
        return currentQuestionnaire;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
    async loadKeywords(uuid: string, forceReload: boolean = false) {
      loggerService.log("loadKeywords");
      try {
        let currentKeywords = this.getKeywordsResultsByUuid(uuid);
        // If the questionnaires (de + en) are not in the store already, get it from the mediaItem and load it
        if (!currentKeywords || forceReload) {
          const mediaitem = this.getMediaItemByUuid(uuid);
          if (!mediaitem || forceReload) {
            // If no questionnaire item was found, load the  summary from the API directly
            loggerService.log("loadKeywords:getKeywordsFromApi");
            this.keywordsResults.loading = true;
            const {data} = await apiClient.get("/getKeywords?uuid=" + uuid);
            //console.log(data);
            loggerService.log(data);
            if ("result" in data && "data" in data.result && Object.keys(data.result.data).length > 0) {
              this.keywordsResults.complete(new Map([[uuid, data.result]]));
              currentKeywords = this.getKeywordsResultsByUuid(uuid);

              const curr_keywords: Keywords = data.result.data[0].keywords;
              loggerService.log("loadKeywords:keywords:");
              this.keywords = curr_keywords;
              loggerService.log(this.keywords);
            } else {
              this.keywordsResults.loading = false;
            }
          } else {
            loggerService.log("loadKeywords:getKeywordsFromMediaItem");
            loggerService.log(`loadKeywords:url: ${mediaitem.keywords_result}`);

            this.keywordsResults.loading = true;

            const currentKeywordsResults = new KeywordsResults();
            currentKeywordsResults.data = [];
            const response_keywords = await axios.get(mediaitem.keywords_result, {
              headers: {"Access-Control-Allow-Origin": "*"},
            });
            loggerService.log("loadKeywords:response:");
            loggerService.log(response_keywords.data);

            const curr_keywords: Keywords = response_keywords.data.keywords;
            loggerService.log("loadKeywords:keywords:");
            this.keywords = curr_keywords;
            loggerService.log(this.keywords);

            //currentKeywordsResults.data?.push(response_slides_meta.data);
            //currentKeywordsResults.result = "success";
            //this.keywordsResults.data.set(mediaitem.uuid, currentKeywordsResults);
            //loggerService.log(currentSlidesImagesMeta);
            currentKeywords = response_keywords.data;
            this.keywordsResults.loading = false;
          }
        }
        if (!currentKeywords || !this.keywords) {
          loggerService.error("loadKeywords: currentKeywords empty!");
          return undefined;
        }
        this.keywordsResult = currentKeywords;
        return currentKeywords;
      } catch (error) {
        alert(error);
        loggerService.error(error);
        return undefined;
      }
    },
  },
});
