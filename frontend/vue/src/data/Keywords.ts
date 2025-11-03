class Keywords {
  [word: string]: number;
}

class KeywordsResult {
  constructor(init?: Partial<KeywordsResult>) {
    Object.assign(this, init);
  }
  type?: string;
  language?: string;
  keywords?: Keywords;

  private toObject() {
    return {
      type: this.type,
      language: this.language,
      keywords: this.keywords,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<KeywordsResult["toObject"]> = JSON.parse(serialized);
    const resultItem = new KeywordsResult();
    resultItem.type = item.type;
    resultItem.language = item.language;
    resultItem.keywords = item.keywords;
    return resultItem;
  }
}

class KeywordsResults {
  constructor(init?: Partial<KeywordsResults>) {
    Object.assign(this, init);
  }
  result?: string;
  data?: Array<KeywordsResult>;
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
    const item: ReturnType<KeywordsResults["toObject"]> = JSON.parse(serialized);
    const resultItem = new KeywordsResults();
    resultItem.result = item.result;
    resultItem.data = item.data;
    return resultItem;
  }
}
export {KeywordsResults, KeywordsResult, Keywords};
