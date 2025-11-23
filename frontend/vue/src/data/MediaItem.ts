import type {SurveyItem} from "@/data/SurveyItem";
import type {LmsGatedAccessDetails} from "@/data/Protection";

class AirflowInfo {
  constructor(init?: Partial<AirflowInfo>) {
    Object.assign(this, init);
  }
  dag_id?: string;
  dag_version?: string;
  ended?: string;
  started?: string;
}

class History {
  constructor(init?: Partial<History>) {
    Object.assign(this, init);
  }
  datetime?: string;
  key?: string;
  value?: string;
}

class MediaItemDescription {
  constructor(init?: Partial<MediaItemDescription>) {
    Object.assign(this, init);
  }
  course?: string;
  course_acronym?: string;
  faculty?: string;
  faculty_acronym?: string;
  faculty_color?: string;
  lecturer?: string;
  semester?: string;
  university?: string;
  university_acronym?: string;
}

class MediaItemLicense {
  constructor(init?: Partial<MediaItemLicense>) {
    Object.assign(this, init);
  }
  acronym?: string;
  name?: string;
  type?: string;
  url?: string;
  value?: boolean;
}

class MediaItemPermission {
  constructor(init?: Partial<MediaItemPermission>) {
    Object.assign(this, init);
  }
  type?: string;
  value?: boolean;
}

class MediaItemThumbnails {
  constructor(init?: Partial<MediaItemThumbnails>) {
    Object.assign(this, init);
  }
  lecturer?: string;
  media?: string;
  timeline?: {[key: string]: string};
}

class MediaItemHighlights {
  constructor(init?: Partial<MediaItemHighlights>) {
    Object.assign(this, init);
  }
  asr_result_de?: Array<string>;
  asr_result_en?: Array<string>;
}

class MediaItemState {
  constructor(init?: Partial<MediaItemState>) {
    Object.assign(this, init);
  }
  overall_step?: "PROCESSING" | "EDITING" | "FINISHED";
  editing_progress?: number;
  published?: boolean;
  listed?: boolean;
}

class MediaItem {
  constructor(init?: Partial<MediaItem>) {
    Object.assign(this, init);
  }
  uuid?: string;
  asr_result?: string;
  audio?: string;
  description?: MediaItemDescription;
  language?: string;
  licenses?: Array<MediaItemLicense>;
  marker?: string;
  media?: string;
  media_hls?: string;
  permissions?: Array<MediaItemPermission>;
  slides?: string;
  subtitle?: string;
  subtitle_de?: string;
  subtitle_en?: string;
  thumbnails?: MediaItemThumbnails;
  title?: string;
  transcript?: string;
  search_score?: number;
  search_highlights?: MediaItemHighlights;
  state?: MediaItemState;
  surveys?: Array<SurveyItem>;
  asr_result_de?: string;
  asr_result_en?: string;
  transcript_de?: string;
  transcript_en?: string;
  short_summary_result_de?: string;
  short_summary_result_en?: string;
  summary_result_de?: string;
  summary_result_en?: string;
  topic_result_de?: string;
  topic_result_de_history?: Array<History>;
  topic_result_en?: string;
  topic_result_en_history?: Array<History>;
  search_trie_de?: string;
  search_trie_en?: string;
  airflow_info?: AirflowInfo;
  airflow_info_history?: Array<AirflowInfo>;
  questionnaire_curated?: boolean;
  questionnaire_result_de?: string;
  questionnaire_result_de_history?: Array<History>;
  questionnaire_result_en?: string;
  questionnaire_result_en_history?: Array<History>;
  slides_images_folder?: string;
  slides_images_meta?: string;
  keywords_result?: string;
  slides_trie?: string;
  lms_gated_access?: boolean;
  lms_gated_access_details: LmsGatedAccessDetails;

  private toObject() {
    return {
      uuid: this.uuid,
      asr_result: this.asr_result,
      audio: this.audio,
      description: this.description,
      language: this.language,
      licenses: this.licenses,
      marker: this.marker,
      media: this.media,
      media_hls: this.media_hls,
      permissions: this.permissions,
      slides: this.slides,
      subtitle: this.subtitle,
      subtitle_de: this.subtitle_de,
      subtitle_en: this.subtitle_en,
      thumbnails: this.thumbnails,
      title: this.title,
      transcript: this.transcript,
      search_score: this.search_score,
      search_highlights: this.search_highlights,
      state: this.state,
      surveys: this.surveys,
      asr_result_de: this.asr_result_de,
      asr_result_en: this.asr_result_en,
      transcript_de: this.transcript_de,
      transcript_en: this.transcript_en,
      short_summary_result_de: this.short_summary_result_de,
      short_summary_result_en: this.short_summary_result_en,
      summary_result_de: this.summary_result_de,
      summary_result_en: this.summary_result_en,
      topic_result_de: this.topic_result_de,
      topic_result_de_history: this.topic_result_de_history,
      topic_result_en: this.topic_result_en,
      topic_result_en_history: this.topic_result_en_history,
      search_trie_de: this.search_trie_de,
      search_trie_en: this.search_trie_en,
      airflow_info: this.airflow_info,
      airflow_info_history: this.airflow_info_history,
      questionnaire_curated: this.questionnaire_curated,
      questionnaire_result_de: this.questionnaire_result_de,
      questionnaire_result_de_history: this.questionnaire_result_de_history,
      questionnaire_result_en: this.questionnaire_result_en,
      questionnaire_result_en_history: this.questionnaire_result_en_history,
      slides_images_folder: this.slides_images_folder,
      slides_images_meta: this.slides_images_meta,
      slides_trie: this.slides_trie,
      keywords_result: this.keywords_result,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<MediaItem["toObject"]> = JSON.parse(serialized);
    const resultItem = new MediaItem();
    resultItem.uuid = item.uuid;
    resultItem.asr_result = item.asr_result;
    resultItem.audio = item.audio;
    resultItem.description = item.description;
    resultItem.language = item.language;
    resultItem.licenses = item.licenses;
    resultItem.marker = item.marker;
    resultItem.media = item.media;
    resultItem.media_hls = item.media_hls;
    resultItem.permissions = item.permissions;
    resultItem.slides = item.slides;
    resultItem.subtitle = item.subtitle;
    resultItem.subtitle_de = item.subtitle_de;
    resultItem.subtitle_en = item.subtitle_en;
    resultItem.thumbnails = item.thumbnails;
    resultItem.title = item.title;
    resultItem.transcript = item.transcript;
    resultItem.search_score = item.search_score;
    resultItem.search_highlights = item.search_highlights;
    resultItem.state = item.state;
    resultItem.surveys = item.surveys;
    resultItem.asr_result_de = item.asr_result_de;
    resultItem.asr_result_en = item.asr_result_en;
    resultItem.transcript_de = item.transcript_de;
    resultItem.transcript_en = item.transcript_en;
    resultItem.short_summary_result_de = item.short_summary_result_de;
    resultItem.short_summary_result_en = item.short_summary_result_en;
    resultItem.summary_result_de = item.summary_result_de;
    resultItem.summary_result_en = item.summary_result_en;
    resultItem.topic_result_de = item.topic_result_de;
    resultItem.topic_result_de_history = item.topic_result_de_history;
    resultItem.topic_result_en = item.topic_result_en;
    resultItem.topic_result_en_history = item.topic_result_en_history;
    resultItem.search_trie_de = item.search_trie_de;
    resultItem.search_trie_en = item.search_trie_en;
    resultItem.airflow_info = item.airflow_info;
    resultItem.airflow_info_history = item.airflow_info_history;
    resultItem.questionnaire_curated = item.questionnaire_curated;
    resultItem.questionnaire_result_de = item.questionnaire_result_de;
    resultItem.questionnaire_result_de_history = item.questionnaire_result_de_history;
    resultItem.questionnaire_result_en = item.questionnaire_result_en;
    resultItem.questionnaire_result_en_history = item.questionnaire_result_en_history;
    resultItem.slides_images_folder = item.slides_images_folder;
    resultItem.slides_images_meta = item.slides_images_meta;
    resultItem.slides_trie = item.slides_trie;
    resultItem.keywords_result = item.keywords_result;
    return resultItem;
  }
}

export {MediaItem};
