class SummaryItem {
  constructor(init?: Partial<SummaryItem>) {
    Object.assign(this, init);
  }
  result_index?: number;
  // Title available only for type SummaryResult
  title?: string;
  summary?: string;
}

class Summary {
  constructor(init?: Partial<Summary>) {
    Object.assign(this, init);
  }
  // Type SummaryResult or ShortSummaryResult
  type?: string;
  language?: string;
  result?: Array<SummaryItem>;

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
    const item: ReturnType<Summary["toObject"]> = JSON.parse(serialized);
    const resultItem = new Summary();
    resultItem.type = item.type;
    resultItem.language = item.language;
    resultItem.result = item.result;
    return resultItem;
  }
}

class SummaryResult {
  constructor(init?: Partial<SummaryResult>) {
    Object.assign(this, init);
  }
  result?: string;
  data?: Array<Summary>;
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
    const item: ReturnType<SummaryResult["toObject"]> = JSON.parse(serialized);
    const resultItem = new SummaryResult();
    resultItem.result = item.result;
    resultItem.data = item.data;
    return resultItem;
  }
}
export {SummaryResult, Summary, SummaryItem};
