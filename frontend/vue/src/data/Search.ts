import type {Transcript} from "@/data/Transcript";
import {SearchResultItem, WordItem} from "@/data/AsrResults";
import {LoggerService} from "@/common/loggerService";

const loggerService = new LoggerService();
class Search {
  /**
   * Method to search for multiple terms in transcript
   * @param {Array<string>} terms - The searchterms
   * @param {Transcript} transcript - The transcript in which terms are searched
   * @param {boolean} verbose - Be verbose or not
   * @return {Array<Array<number>>} - An array of sorted indices
   */
  searchTerms(terms: Array<string>, transcript: Transcript, verbose: boolean = false): Array<SearchResultItem> {
    // an array to store the indices of found terms
    let resultIndices = [];
    // loop over all searchterms
    for (const term of terms) {
      // look up their indices in the reverse index
      let result = transcript.lookupReverseIndex(term);
      // if term in reverse index
      if (result !== undefined) {
        if (verbose) {
          loggerService.log(`Search::searchTerms: Term ${term} in reverse index found`);
        }
        // add the indices as to the result array
        for (const resultElement of result) {
          resultIndices.push(new SearchResultItem(term, resultElement));
        }
      } else {
        if (verbose) {
          loggerService.log(`Search::searchTerms: Term ${term} not in reverse index`);
        }
      }
    }
    // sort the result array
    return resultIndices.sort((n1, n2) => n1.index - n2.index);
  }

  /**
   * Method to cluster search results
   *
   * @param {Array<SearchResultItem>} searchResults - The input array of search results, obtained by `Transcript::searchTerms`
   * @param {number} threshold - How far apart the words can be
   * @param {boolean} sorted - Sort the resulting array
   * @return {Array<Array<SearchResultItem>>} - An array of clusters, sorted descending by length
   */
  clusterSearchResults(
    searchResults: Array<SearchResultItem>,
    threshold: number,
    sorted: boolean = true,
  ): Array<Array<SearchResultItem>> {
    const lastIndex = searchResults.length - 1;
    let a = searchResults.slice(0, lastIndex);
    let b = searchResults.slice(1, searchResults.length);
    let srcArr = a.map((wordItem, i) => {
      wordItem.diff = b[i].index - wordItem.index;
      return wordItem;
    });

    if (lastIndex >= 0) {
      // Add last item with a difference to the next word of 0
      const lastItem = searchResults[lastIndex];
      lastItem.diff = 0;
      srcArr.push(lastItem);
    }

    let clusters: Array<Array<SearchResultItem>> = [];

    while (srcArr.length) {
      let cluster: Array<SearchResultItem> = [];

      // Checks if shift succeeds to see if the array has a length larger
      // than 0 to avoid typescript error since the return value of shift
      // might be undefined
      let currentElement = srcArr.shift();
      while (currentElement !== undefined) {
        cluster.push(currentElement);
        if (currentElement.diff > threshold) {
          break;
        }
        currentElement = srcArr.shift();
      }
      clusters.push(cluster);
    }
    if (sorted) {
      return clusters.sort((a, b) => b.length - a.length);
    }
    return clusters;
  }

  /**
   * Method to get context around search results
   * @param {number} num - The number of total words of the resulting element to display
   * @param {Array<Array<SearchResultItem>>} srcArr - The array of search results
   * @param {Transcript} transcript - The transcript
   */
  getContext(num: number, srcArr: Array<Array<SearchResultItem>>, transcript: Transcript) {
    let contextArray = [];
    for (const cluster of srcArr) {
      let firstIdx = cluster[0].index;
      let lastIdx = cluster[cluster.length - 1].index;

      let span = lastIdx - firstIdx;
      let diff = num - span;
      let contextSpan = Math.round(diff / 2);
      // If the span starts before the first word, start from index 0 instead
      const contextStartIndex = Math.max(firstIdx - contextSpan, 0);
      // Slice from the start of the context to the end
      // Extracts raw copies of the word items to avoid highlights in one tab
      // overwriting highlights in a similar context in a previous tab
      let context = transcript.allWords.slice(contextStartIndex, lastIdx + contextSpan).map((item) => {
        // Manual copy of the word item to avoid a vue dependency
        // since it may be a vue proxy which cannot be cloned with
        // the JS structured cloning algorithm otherwise
        const copied = new WordItem();
        // Copies the interval to avoid the underlying interval being accidentally modified
        copied.interval = [...item.interval];
        copied.word = item.word;
        copied.index = item.index;
        // Doesn't copy the html since it would be overwritten by the following word anyway

        return copied;
      });
      // Get the relative indices of the search terms to highlight
      const relativeSearchTermIndices = cluster.map((term) => term.index - contextStartIndex);

      for (let i = 0; i < context.length; i++) {
        const wordItem = context[i];
        // Highlight the word if there is a next search term index and it matches
        if (relativeSearchTermIndices.length && i == relativeSearchTermIndices[0]) {
          wordItem.html = `<b class="searchTerm">${wordItem.word}</b> `;
          // Continue to the next search term index
          relativeSearchTermIndices.shift();
        } else {
          wordItem.html = `${wordItem.word} `;
        }
      }
      contextArray.push(context);
    }
    return contextArray;
  }

  /**
   * Wrapper method to search for multiple searchterms
   *
   * @param {Array<string>} terms - The searchterms
   * @param {number} threshold - The distance between words
   * @param {number} contextNum - The number of context words
   * @param {Transcript} transcript - The transcript
   */
  search(terms: Array<string>, threshold: number, contextNum: number, transcript: Transcript): WordItem[][] {
    let searchResults = this.searchTerms(terms, transcript);
    let clusters = this.clusterSearchResults(searchResults, threshold);
    let context = this.getContext(contextNum, clusters, transcript);
    return context;
  }
}

export {Search};
