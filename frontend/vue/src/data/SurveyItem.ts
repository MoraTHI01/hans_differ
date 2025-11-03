class SurveyItem {
  constructor(init?: Partial<SurveyItem>) {
    Object.assign(this, init);
  }
  type?: string;
  survey_title?: string;
  survey_language?: string;
  survey_url?: string;
  survey_status?: string;

  private toObject() {
    return {
      type: this.type,
      survey_title: this.survey_title,
      survey_language: this.survey_language,
      survey_url: this.survey_url,
      survey_status: this.survey_status,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<SurveyItem["toObject"]> = JSON.parse(serialized);
    const resultItem = new SurveyItem();
    resultItem.type = item.type;
    resultItem.survey_title = item.survey_title;
    resultItem.survey_language = item.survey_language;
    resultItem.survey_url = item.survey_url;
    resultItem.survey_status = item.survey_status;
    return resultItem;
  }
}

export {SurveyItem};
