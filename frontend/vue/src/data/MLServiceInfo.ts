class ModelInfo {
  constructor(init?: Partial<ModelInfo>) {
    Object.assign(this, init);
  }
  model_id?: string;
  model_sha?: string;
  model_dtype?: string;
  max_new_tokens?: number;
  max_total_tokens?: number;

  private toObject() {
    return {
      model_id: this.model_id,
      model_sha: this.model_sha,
      model_dtype: this.model_dtype,
      max_new_tokens: this.max_new_tokens,
      max_total_tokens: this.max_total_tokens,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<ModelInfo["toObject"]> = JSON.parse(serialized);
    const resultItem = new ModelInfo();
    resultItem.model_id = item.model_id;
    resultItem.model_sha = item.model_sha;
    resultItem.model_dtype = item.model_dtype;
    resultItem.max_new_tokens = item.max_new_tokens;
    resultItem.max_total_tokens = item.max_total_tokens;
    return resultItem;
  }
}

class ServiceInfo {
  constructor(init?: Partial<ServiceInfo>) {
    Object.assign(this, init);
  }
  type?: string;
  result_index?: number;
  info?: ModelInfo;

  private toObject() {
    return {
      type: this.type,
      result_index: this.result_index,
      info: this.info,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<ServiceInfo["toObject"]> = JSON.parse(serialized);
    const resultItem = new ServiceInfo();
    resultItem.type = item.type;
    resultItem.result_index = item.result_index;
    resultItem.info = item.info;
    return resultItem;
  }
}

class MLServiceInfoResult {
  constructor(init?: Partial<MLServiceInfoResult>) {
    Object.assign(this, init);
  }
  type?: string;
  services?: Array<ServiceInfo>;

  private toObject() {
    return {
      type: this.type,
      services: this.services,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<MLServiceInfoResult["toObject"]> = JSON.parse(serialized);
    const resultItem = new MLServiceInfoResult();
    resultItem.type = item.type;
    resultItem.services = item.services;
    return resultItem;
  }
}

export {ServiceInfo, MLServiceInfoResult};
