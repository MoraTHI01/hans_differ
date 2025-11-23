export interface TextContent {
  type: "text";
  text: string;
}

export interface ImageContent {
  type: "image_url";
  image_url: {
    url: string;
  };
}

export type ContentItem = TextContent; //| ImageContent;

export interface MessageContent {
  language: string;
  content: ContentItem[];
}

export interface MessageHistory {
  isUser: boolean;
  language: string;
  content: ContentItem[];
  mediaContextUuids: string[];
  documentContextUuids: string[];
}

export interface Message {
  content: MessageContent[];
  isUser: boolean;
  context: string;
  contextUuid: string;
  useContext: boolean;
  useContextAndCite: boolean;
  useChannelContext: boolean;
  useTranslate: boolean;
  history: MessageHistory[];
  actAsTutor: boolean;
  useVision: boolean;
  useVisionSurroundingSlides: boolean;
  useVisionSnapshot: boolean;
  snapshot: string;
  stream: boolean;
  reasoning: boolean;
  mediaContextUuids: string[];
  documentContextUuids: string[];
}
