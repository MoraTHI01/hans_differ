class TopicItem {
  constructor(init?: Partial<TopicItem>) {
    Object.assign(this, init);
  }
  result_index?: number;
  interval!: [number, number];
  title?: string;
  summary?: string;
}

class Topic {
  constructor(init?: Partial<Topic>) {
    Object.assign(this, init);
  }
  type?: string;
  language?: string;
  result?: Array<TopicItem>;

  private toObject() {
    return {
      type: this.type,
      language: this.language,
      result: this.result,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<Topic["toObject"]> = JSON.parse(serialized);
    const resultItem = new Topic();
    resultItem.type = item.type;
    resultItem.language = item.language;
    resultItem.result = item.result;
    return resultItem;
  }
}

class TopicsResult {
  constructor(init?: Partial<TopicsResult>) {
    Object.assign(this, init);
  }
  result?: string;
  data?: Array<Topic>;
  private toObject() {
    return {
      result: this.result,
      data: this.data,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<TopicsResult["toObject"]> = JSON.parse(serialized);
    const resultItem = new TopicsResult();
    resultItem.result = item.result;
    resultItem.data = item.data;
    return resultItem;
  }
}
export {TopicsResult, Topic, TopicItem};
