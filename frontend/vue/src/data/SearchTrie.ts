import {WordItem} from "./AsrResults";

class SearchTrie {
  children?: {[key: string]: SearchTrie};
  word?: string;
  occurrences?: Array<WordItem>;

  constructor(init?: Partial<SearchTrie>) {
    Object.assign(this, init);
  }

  private toObject() {
    return {
      children: this.children,
      word: this.word,
      occurrences: this.occurrences,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: Partial<SearchTrie> = JSON.parse(serialized);
    const resultItem = new SearchTrie();

    if (item.children) {
      // Convert children back to a dictionary of SearchTrie objects
      resultItem.children = {};
      for (const key in item.children) {
        if (item.children.hasOwnProperty(key)) {
          resultItem.children[key] = SearchTrie.fromSerialized(JSON.stringify(item.children[key]));
        }
      }
    }
    if (item.word) {
      resultItem.word = item.word;
    }
    if (item.occurrences) {
      resultItem.occurrences = item.occurrences;
    }

    return resultItem;
  }
}

class SearchTrieResult {
  constructor(init?: Partial<SearchTrieResult>) {
    Object.assign(this, init);
  }
  result?: string;
  data?: Array<SearchTrie>;
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
    const item: ReturnType<SearchTrieResult["toObject"]> = JSON.parse(serialized);
    const resultItem = new SearchTrieResult();
    resultItem.result = item.result;
    resultItem.data = item.data;
    return resultItem;
  }
}
export {SearchTrieResult, SearchTrie};
