class MarkerResultItem {
  constructor(init?: Partial<MarkerResultItem>) {
    Object.assign(this, init);
  }
  interval?: Array<number>;
  result_index?: number;
  type?: string;
  value?: string;
  time?: string;
  title?: string;
  summary?: string;
}

class MarkerResult {
  constructor(init?: Partial<MarkerResult>) {
    Object.assign(this, init);
  }
  result?: Array<MarkerResultItem>;
  type?: string;
}

export {MarkerResultItem, MarkerResult};
