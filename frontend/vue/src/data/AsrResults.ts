class WordItem {
  interval!: [number, number];
  word!: string;
  index!: number;
  html?: string;
}

class AsrNormalizedResultItem {
  interval!: Array<number>;
  transcript_formatted!: string;
  words_formatted!: Array<WordItem>;
  result_index!: number;
}

class AsrNormalizedResult {
  result!: Array<AsrNormalizedResultItem>;
  type!: string;
}

class TranscriptSegment {
  words!: Array<WordItem>;
  transcript!: string;
  start!: number;
  stop!: number;
}

class SearchResultItem {
  term: string;
  index: number;
  diff: number;

  constructor(term: string, index: number) {
    this.term = term;
    this.index = index;
    this.diff = 0;
  }
}

class AsrResultsItem {
  constructor(init?: Partial<AsrResultsItem>) {
    Object.assign(this, init);
  }
  // Type AsrResult
  type?: string;
  language?: string;
  result?: AsrNormalizedResult;

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
    const item: ReturnType<AsrResultsItem["toObject"]> = JSON.parse(serialized);
    const resultItem = new AsrResultsItem();
    resultItem.type = item.type;
    resultItem.language = item.language;
    resultItem.result = item.result;
    return resultItem;
  }
}

class AsrResults {
  constructor(init?: Partial<AsrResults>) {
    Object.assign(this, init);
  }
  result?: string;
  data?: Array<AsrResultsItem>;
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
    const item: ReturnType<AsrResults["toObject"]> = JSON.parse(serialized);
    const resultItem = new AsrResults();
    resultItem.result = item.result;
    resultItem.data = item.data;
    return resultItem;
  }
}

export {
  WordItem,
  AsrNormalizedResult,
  AsrNormalizedResultItem,
  TranscriptSegment,
  SearchResultItem,
  AsrResultsItem,
  AsrResults,
};
