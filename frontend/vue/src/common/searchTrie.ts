import {SearchTrie} from "@/data/SearchTrie";

class SearchTrieClass {
  trie: SearchTrie;

  constructor(trie: SearchTrie) {
    this.trie = trie as SearchTrie;
  }

  search(word: string) {
    let word_lower = word.toLowerCase();
    let current = this.trie;

    for (let i = 0; i < word_lower.length; i++) {
      let char = word_lower[i];
      let j = i + 1;
      if (char in current["children"]) {
        current = current["children"][char];
        if (j === word_lower.length) {
          return current;
        }
      } else {
        console.log("Word not found");
        break;
      }
    }
  }

  get_next_words(node, arr) {
    let keys = Object.keys(node["children"]);
    for (let key of keys) {
      let occurences = node["children"][key]["occurences"];
      if (occurences.length) {
        arr.push(occurences[0]);
      } else {
        this.get_next_words(node["children"][key], arr);
      }
    }
    return arr;
  }

  get_all_words(node, arr) {
    let keys = Object.keys(node["children"]);
    for (let key of keys) {
      let current = node["children"][key];
      if ("word" in current) {
        arr.push(current);
      }
      this.get_all_words(current, arr);
    }
    return arr;
  }

  get_synonyms(node) {
    let words_with_occurence = [];
    if ("synonyms" in node) {
      for (const synonym of node["synonyms"]) {
        let word_with_occurence = structuredClone(this.search(synonym));
        word_with_occurence["is_syn"] = true;
        words_with_occurence.push(word_with_occurence);
      }
    }
    return words_with_occurence;
  }

  get_size(node) {
    let count = 1;
    for (let key of Object.keys(node["children"])) {
      count += this.get_size(node["children"][key]);
    }
    return count;
  }

  get_all_occurences(node, arr = []) {
    let keys = Object.keys(node["children"]);

    if ("occurences" in node && node["occurences"].length) {
      for (const occurence of node["occurences"]) {
        arr.push(occurence["interval"]);
      }
    }

    for (const key of keys) {
      this.get_all_occurences(node["children"][key], arr);
    }
    return arr;
  }
}

export {SearchTrieClass};
