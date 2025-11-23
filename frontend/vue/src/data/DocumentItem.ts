class DocumentItem {
  constructor(init?: Partial<DocumentItem>) {
    Object.assign(this, init);
  }
  uuid?: string;
  filename?: string;
  mime_type?: string;
  url?: string;
  channel_uuid?: string;
  status?: string;
  visible?: boolean;

  private toObject() {
    return {
      uuid: this.uuid,
      filename: this.filename,
      mime_type: this.mime_type,
      url: this.url,
      channel_uuid: this.channel_uuid,
      status: this.status,
      visible: this.visible,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<DocumentItem["toObject"]> = JSON.parse(serialized);
    const resultItem = new DocumentItem();
    resultItem.uuid = item.uuid;
    resultItem.filename = item.filename;
    resultItem.mime_type = item.mime_type;
    resultItem.url = item.url;
    resultItem.channel_uuid = item.channel_uuid;
    resultItem.status = item.status;
    resultItem.visible = item.visible;
    return resultItem;
  }
}

export {DocumentItem};
