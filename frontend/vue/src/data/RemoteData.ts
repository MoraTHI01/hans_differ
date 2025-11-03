/**
 * Contains data that is loaded from a remote API alongside a loading status
 */
class RemoteData<Data> {
  loading: boolean;
  data: Data;

  /**
   * Creates new RemoteData either with fully loaded data or a default
   *
   * @param {Data} data - Default or fully loaded data
   * @param {boolean} loaded - Whether the data is already loaded or loading is still in progress
   */
  constructor(data: Data, loaded: boolean = false) {
    this.data = data;
    this.loading = loaded;
  }

  /**
   * Finish loading data and set loaded to false
   *
   * @param {Data} data - the fully loaded data
   */
  complete(data: Data) {
    this.data = data;
    this.loading = false;
  }

  /**
   * Starts loading data while keeping a default value
   *
   * @param {Data} defaultData - default data to use while new data is loading
   */
  startLoading(defaultData: Data) {
    this.data = defaultData;
    this.loading = true;
  }
}

export {RemoteData};
