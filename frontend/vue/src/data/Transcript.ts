import {AsrNormalizedResult, WordItem, TranscriptSegment} from "./AsrResults";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();

const initialAndFinalPunctuation = /([.,!?:-]+$|^[.,!?:-]+)/g;

/**
 * Lowercases a word and removes and initial or trailing punctuation. Note that
 * punctuation in the middle of words like hyphens are kept
 *
 * @param {string} word - Any word
 *
 * @returns {string} The word in lowercase without any initial or final punctuation
 */
function lowercaseAndStrip(word: string): string {
  return word.toLowerCase().replace(initialAndFinalPunctuation, "");
}

class Transcript {
  asrResult: AsrNormalizedResult;
  allWords: Array<WordItem>;
  reverseIndex: Map<string, Array<number>>;
  segments: Array<TranscriptSegment>;

  constructor(asrResultInput?: AsrNormalizedResult) {
    this.asrResult = new AsrNormalizedResult();
    this.allWords = new Array<WordItem>();
    this.reverseIndex = new Map<string, Array<number>>();

    this.segments = new Array<TranscriptSegment>();
    if (asrResultInput !== undefined) {
      this.asrResult = asrResultInput;
      this.makeAllWords();
      this.makeReverseIndex();
      this.makeSegments();
    }
  }

  /**
   * Method to make reverse index (words are keys, values are arrays of occurences of words)
   */
  makeReverseIndex() {
    // for every word
    for (const wordItem of this.allWords) {
      const word = lowercaseAndStrip(wordItem.word);
      // Try getting an existing index array from the reverse index
      // for the lowercased word
      const indexArray = this.reverseIndex.get(word);
      // if the word is already in the reverse index
      if (indexArray !== undefined) {
        // add the occurrence (position index) to the array (of occurrences)
        indexArray.push(wordItem.index);
      } else {
        // Otherwise, add a new array with the first occurrence of the word to the reverse index
        this.reverseIndex.set(word, [wordItem.index]);
      }
    }
  }

  /**
   * Method to make list of segments
   */
  makeSegments() {
    // for every segment in the transcript
    for (const segment of this.asrResult.result) {
      // add new segment to the segments array
      this.segments.push({
        words: segment.words_formatted,
        transcript: segment.transcript_formatted,
        start: segment.interval[0],
        stop: segment.interval[1],
      });
    }
  }

  makeAllWords() {
    for (const segment of this.asrResult.result) {
      for (const wordItem of segment.words_formatted) {
        this.allWords.push(wordItem);
      }
    }
  }

  /**
   * Method to look up a word in the reverse index and get it`s occurences
   * @param {string} term - The term to look up
   * @param {boolean} verbose - Be verbose
   */
  lookupReverseIndex(term: string, verbose: boolean = false): Array<number> {
    const word_lc = lowercaseAndStrip(term);
    // lookup the lowercased `word_lc` in the reverse index
    let result = this.reverseIndex.get(word_lc);
    // Return an empty array if there is no result
    if (result === undefined) {
      return [];
    }

    if (verbose) {
      loggerService.log(`Transcript::searchWord Word '${term}' in reverse index found! Result ${result}`);
    }
    return result;
  }
}

class TranscriptResultsItem {
  constructor(init?: Partial<TranscriptResultsItem>) {
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
    const item: ReturnType<TranscriptResultsItem["toObject"]> = JSON.parse(serialized);
    const resultItem = new TranscriptResultsItem();
    resultItem.type = item.type;
    resultItem.language = item.language;
    resultItem.result = item.result;
    return resultItem;
  }
}

class TranscriptResults {
  constructor(init?: Partial<TranscriptResults>) {
    Object.assign(this, init);
  }
  result?: string;
  data?: Array<TranscriptResultsItem>;
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
    const item: ReturnType<TranscriptResults["toObject"]> = JSON.parse(serialized);
    const resultItem = new TranscriptResults();
    resultItem.result = item.result;
    resultItem.data = item.data;
    return resultItem;
  }
}

export {Transcript, TranscriptResults, TranscriptResultsItem};
