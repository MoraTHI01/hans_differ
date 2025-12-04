import {defineStore} from "pinia";
import {api_base_url, apiClient} from "@/common/apiClient";
import {LoggerService} from "@/common/loggerService";
import {v4} from "uuid";
import axios from "axios";
import type {Message, MessageContent, MessageHistory, ContentItem, TextContent} from "@/data/Message";
import {MLServiceInfoResult} from "@/data/MLServiceInfo";
import {useAuthStore} from "@/stores/auth";

const loggerService = new LoggerService();

export const useMessageStore = defineStore({
  id: "messageStore",
  state: () => ({
    messages: new Map<string, Message[]>(),
    requestOngoing: false,
    requestWasCanceled: false,
    requestTimeoutError: false,
    requestError: false,
    showErrorMessage: false,
    errorMessageText: "",
    currentTranscriptSelection: "",
    servicesAvailable: false,
    servicesAlive: false,
    lastAliveCheckTime: new Date(),
    servicesRequired: false,
    videoSnapshot: "",
  }),
  getters: {
    isInitialized: (state) => () => {
      if (state.messages.entries.length > 0) {
        return true;
      }
      return false;
    },
    isMessagesEmpty: (state) => (uuid: string) => {
      const foundMessages = state.messages.get(uuid);
      if (foundMessages === undefined) {
        return true;
      }
      return foundMessages.length < 1;
    },
    getMessages: (state) => (uuid: string) => {
      return state.messages.get(uuid);
    },
    getLastMessage: (state) => (uuid: string) => {
      const allMessages = state.messages.get(uuid);
      if (allMessages !== undefined) {
        const lastElement = allMessages[allMessages.length - 1];
        return lastElement;
      }
      return undefined;
    },
    isRequestOngoing: (state) => state.requestOngoing,
    getRequestWasCanceled: (state) => state.requestWasCanceled,
    getRequestTimeoutError: (state) => state.requestTimeoutError,
    getRequestError: (state) => state.requestTimeoutError,
    getShowErrorMessage: (state) => state.showErrorMessage,
    getErrorMessageText: (state) => state.errorMessageText,
    getCurrentTranscriptSelection: (state) => state.currentTranscriptSelection,
    getServicesAvailable: (state) => state.servicesAvailable,
    getServicesAlive: (state) => state.servicesAlive,
    getVideoSnapshot: (state) => state.videoSnapshot,
  },
  actions: {
    setCurrentTranscriptSelection(text: string) {
      loggerService.log("setCurrentTranscriptSelection: " + text);
      this.currentTranscriptSelection = text;
    },
    setVideoSnapshot(img: string) {
      loggerService.log("setVideoSnapshot: " + img);
      this.videoSnapshot = img;
    },
    createMessageHistory(uuid: string) {
      loggerService.log("createMessageHistory");
      const allMessages = this.messages.get(uuid);
      const result = new Array<MessageHistory>();
      if (allMessages !== undefined) {
        loggerService.log("createMessageHistory:iterate");
        for (const item of allMessages) {
          const isUser = item.isUser;
          if (item.content.length > 0) {
            if (item.content.length < 2) {
              loggerService.log("createMessageHistory:push");
              result.push({
                isUser: isUser,
                language: item.content[0].language,
                content: [
                  {
                    type: "text",
                    text: item.content[0].content[0].text,
                  },
                ],
                mediaContextUuids: item.mediaContextUuids,
                documentContextUuids: item.documentContextUuids,
              });
            } else {
              for (const contentItem of item.content) {
                if (contentItem.language === "en") {
                  loggerService.log("createMessageHistory:push");
                  result.push({
                    isUser: isUser,
                    language: contentItem.language,
                    content: [
                      {
                        type: "text",
                        text: contentItem.content[0].text,
                      },
                    ],
                    mediaContextUuids: item.mediaContextUuids,
                    documentContextUuids: item.documentContextUuids,
                  });
                }
              }
            }
          }
        }
      }
      loggerService.log("createMessageHistory:result");
      loggerService.log(result);
      return result;
    },
    async storeMessages() {
      loggerService.log("storeMessages");
      // Serialize the Map to a JSON string
      const serializableObject: {[key: string]: Message[]} = {};
      this.messages.forEach((value, key) => {
        serializableObject[key] = value;
      });
      const serializedMap = JSON.stringify(serializableObject);
      // Store messages with uuid of user
      const authStore = useAuthStore();
      const user_id = authStore.getUserId();
      // Store the serialized Map in local storage
      localStorage.setItem("hans_messages_" + user_id, serializedMap);
    },
    async loadMessages() {
      if (this.messages.entries.length === 0) {
        loggerService.log("loadMessages");
        const authStore = useAuthStore();
        const user_id = authStore.getUserId();
        // Retrieve the serialized Map from local storage
        const serializedMap = localStorage.getItem("hans_messages_" + user_id);

        if (serializedMap) {
          // Deserialize the JSON string back into a Map
          const jsonObject = JSON.parse(serializedMap);
          const deserializedMap = new Map<string, Message[]>();
          // Iterate through the properties of the JavaScript object and populate the Map
          for (const key in jsonObject) {
            if (jsonObject.hasOwnProperty(key)) {
              deserializedMap.set(key, jsonObject[key]);
            }
          }
          this.messages = deserializedMap;
        } else {
          //console.log("No data found in local storage.");
          loggerService.log("No data found in local storage.");
        }
      }
    },
    removeLastBotMessages(uuid: string) {
      const mediaItemMessages = this.messages.get(uuid);
      while (mediaItemMessages?.at(-1)?.isUser === false) {
        mediaItemMessages?.pop();
      }
    },
    addMessage(uuid: string, message: Message) {
      loggerService.log("addMessageForUuid");
      loggerService.log("useContext");
      loggerService.log(message.useContext);
      loggerService.log("useContextAndCite");
      loggerService.log(message.useContextAndCite);
      loggerService.log("useTranslate");
      loggerService.log(message.useTranslate);
      loggerService.log("content");
      loggerService.log(message.content);
      loggerService.log("context");
      loggerService.log(message.context);
      loggerService.log("contextUuid");
      loggerService.log(message.contextUuid);
      let itemMessages = this.getMessages(uuid);
      if (itemMessages === undefined) {
        itemMessages = [message];
      } else {
        itemMessages?.push(message);
      }
      this.messages.set(uuid, itemMessages);
      this.storeMessages();
    },
    clearMessages(uuid: string) {
      loggerService.log("clearMessagesForUuid");
      this.messages.delete(uuid);
      this.storeMessages();
    },
    async transferMessage(api_sub_url: string, message: Message) {
      const params = {
        message_uuid: v4(),
        data: message,
      };
      loggerService.log("transferMessage");
      loggerService.log(message);
      try {
        this.requestWasCanceled = false;
        this.requestTimeoutError = false;
        this.requestError = false;
        const {data} = await apiClient.post(api_sub_url, params, {
          headers: {
            "Content-type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
          // Adjust timeout as needed, currently 600 seconds, aka 10 min for reasoning
          timeout: 600000,
        });
        loggerService.log(data);
        if ("data" in data && "result" in data.data[0]) {
          return data.data[0].result[0] as Message;
        }
      } catch (error: any) {
        if (axios.isCancel(error)) {
          // Handle request cancellation (if you need to)
          loggerService.log("transferMessage: Request was canceled: " + error.message);
          this.requestWasCanceled = true;
        } else if (error.code === "ECONNABORTED") {
          // Handle timeout error
          loggerService.log("transferMessage: Request timed out");
          this.requestTimeoutError = true;
        } else {
          // Handle other errors
          loggerService.log("transferMessage: An error occurred: " + error.message);
        }
        this.requestError = true;
        this.requestOngoing = false;
        return undefined;
      }
      this.requestOngoing = false;
      return undefined;
    },
    async adaptMessageContext(uuid: string, message: Message) {
      loggerService.log("adaptMessageContext");
      this.requestOngoing = true;
      return await this.transferMessage("/adaptMessageContext", message);
    },
    async translateMessage(uuid: string, message: Message) {
      loggerService.log("translateMessage");
      this.requestOngoing = true;
      return await this.transferMessage("/translateMessage", message);
    },
    async sendMessage(uuid: string, message: Message) {
      loggerService.log("sendMessage");
      this.requestOngoing = true;
      return await this.transferMessage("/sendMessage", message);
    },
    async sendMessageStream(uuid: string, message: Message, translate: boolean) {
      loggerService.log("sendMessageStream:Start");
      this.requestOngoing = true;
      message.stream = true;
      const params = {
        message_uuid: v4(),
        data: message,
      };
      try {
        this.requestWasCanceled = false;
        this.requestTimeoutError = false;
        this.requestError = false;
        const authStore = useAuthStore();
        const bearerToken = authStore.getRefreshActive() ? authStore.getRefreshToken() : authStore.getAccessToken();
        const response = await fetch(api_base_url + "/sendMessageStream", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            Authorization: `Bearer ${bearerToken}`, // Include Bearer token in headers
          },
          body: JSON.stringify(params),
        });

        // Check if the response is OK (status in the range 200-299)
        if (!response.ok) {
          loggerService.error(`transferMessageStream: HTTP error! status: ${response.status}`);
          this.requestError = true;
          this.requestOngoing = false;
          return undefined;
        }

        const response_message = {
          content: [
            {
              language: translate ? message.content[1].language : message.content[0].language,
              content: [
                {
                  type: "text",
                  text: "",
                } as TextContent,
              ] as ContentItem[],
            } as MessageContent,
          ] as MessageContent[],
          isUser: false,
          context: message.context,
          contextUuid: message.contextUuid,
          useContext: message.useContext,
          useContextAndCite: message.useContextAndCite,
          useTranslate: message.useTranslate,
          history: [] as MessageHistory[],
          actAsTutor: message.actAsTutor,
          useVision: message.useVision,
          useVisionSurroundingSlides: message.useVisionSurroundingSlides,
          useVisionSnapshot: message.useVisionSnapshot,
          snapshot: message.snapshot,
          stream: message.stream,
          reasoning: message.reasoning,
          mediaContextUuids: message.mediaContextUuids,
          documentContextUuids: message.documentContextUuids,
        } as Message;
        loggerService.log(response_message);
        let itemMessages = this.getMessages(uuid);
        if (itemMessages === undefined) {
          itemMessages = [response_message];
        } else {
          itemMessages?.push(response_message);
        }
        this.messages.set(uuid, itemMessages);
        const curr_msg_index = itemMessages.length - 1;

        const reader = response.body.getReader(); // ReadableStream API
        const decoder = new TextDecoder("utf-8"); // TextDecoder to decode UTF-8 text

        function readStream() {
          reader
            .read()
            .then(async ({done, value}) => {
              if (done) {
                loggerService.log("transferMessageStream:StreamFinished");
                if (translate === true) {
                  loggerService.log("transferMessageStream:translateMessage:Start");
                  const params = {
                    message_uuid: v4(),
                    data: itemMessages[curr_msg_index],
                  };
                  const {data} = await apiClient.post("/translateMessage", params, {
                    headers: {
                      "Content-type": "application/json",
                      "Access-Control-Allow-Origin": "*",
                    },
                    // Adjust timeout as needed, currently 360 seconds
                    timeout: 360000,
                  });
                  if ("data" in data && "result" in data.data[0]) {
                    const msg_transl_rsp = data.data[0].result[0] as Message;
                    //loggerService.log("transferMessageStream:translateMessage:Translated:");
                    //loggerService.log(msg_transl_rsp);
                    //loggerService.log("transferMessageStream:translateMessage:Original:");
                    //loggerService.log(itemMessages[curr_msg_index]);
                    itemMessages[curr_msg_index] = msg_transl_rsp;
                  }
                  loggerService.log("transferMessageStream:translateMessage:Finished");
                }
                itemMessages[curr_msg_index].stream = false;
                loggerService.log("transferMessageStream:Finished");
                return;
              }
              const chunk = decoder.decode(value, {stream: true});
              loggerService.log(chunk);
              itemMessages[curr_msg_index].content[0].content[0].text += chunk;
              readStream(); // Continue reading the stream
            })
            .catch((error) => {
              loggerService.error("Error reading stream: " + error);
            });
        }
        readStream(); // Start reading the stream
      } catch (error: any) {
        if (axios.isCancel(error)) {
          // Handle request cancellation (if you need to)
          loggerService.log("transferMessageStream: Request was canceled: " + error.message);
          this.requestWasCanceled = true;
        } else if (error.code === "ECONNABORTED") {
          // Handle timeout error
          loggerService.log("transferMessageStream: Request timed out");
          this.requestTimeoutError = true;
        } else {
          // Handle other errors
          loggerService.log("transferMessageStream: An error occurred: " + error.message);
        }
        this.requestError = true;
        this.requestOngoing = false;
        return undefined;
      }
    },
    setAllRequestsFinished() {
      this.requestOngoing = false;
    },
    activateErrorMessage(errorText: string) {
      this.errorMessageText = errorText;
      this.showErrorMessage = true;
    },
    deactivateErrorMessage() {
      this.errorMessageText = "";
      this.showErrorMessage = false;
    },
    async queryServiceInfoFromApi() {
      loggerService.log("queryServiceInfoFromApi");
      try {
        const {data} = await apiClient.get("/ml-service-info");
        loggerService.log(data);
        return data;
      } catch (error: any) {
        loggerService.error("queryServiceInfoFromApi:Error");
        return {};
      }
    },
    async queryServiceStatusFromApi() {
      loggerService.log("queryServiceStatusFromApi");
      try {
        const {data} = await apiClient.get("/ml-service-status");
        loggerService.log(data);
        if ("status" in data) {
          loggerService.log(data.status);
          if (data.status === "STARTUP") {
            loggerService.log("ML SERVICES STARTING UP");
            return false;
          } else if (data.status === "RUNNING") {
            loggerService.log("ML SERVICES RUNNING");
            return true;
          }
        } else {
          return false;
        }
      } catch (error: any) {
        return false;
      }
      return false;
    },
    setServicesRequired(value: boolean) {
      this.servicesRequired = value;
    },
    sleep(ms: number) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    },
    isMoreThan5MinutesOlder(date1: Date, date2: Date): boolean {
      // Calculate the difference in milliseconds
      const differenceInMs = date2.getTime() - date1.getTime();

      // Calculate the number of milliseconds in 5 minutes
      const fiveMinutesInMs = 5 * 60 * 1000;

      // Compare the difference with the number of milliseconds in 5 minutes
      return differenceInMs > fiveMinutesInMs;
    },
    async fetchServiceStatus() {
      loggerService.log("fetchServiceStatus");
      this.servicesAlive = false;
      this.servicesAvailable = false;
      //await this.sleep(1000);
      while (this.servicesAvailable === false && this.servicesRequired === true) {
        this.servicesAvailable = await this.queryServiceStatusFromApi();
        if (this.servicesAvailable === false) {
          await this.sleep(30000);
        }
        this.servicesAlive = true;
        this.lastAliveCheckTime = new Date();
      }
    },
    async fetchServiceAlive() {
      loggerService.log("fetchServiceAlive");
      const now = new Date();
      if (this.isMoreThan5MinutesOlder(this.lastAliveCheckTime, now) === true) {
        this.servicesAlive = false;
        while (this.servicesAlive === false && this.servicesRequired === true) {
          this.servicesAlive = await this.queryServiceStatusFromApi();
          if (this.servicesAlive === false) {
            await this.sleep(30000);
          }
        }
        this.lastAliveCheckTime = new Date();
      }
    },
  },
});
