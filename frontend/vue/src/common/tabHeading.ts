class TabHeading {
  constructor(name: string, language: string) {
    this.name = name;
    this.language = language;
  }
  name?: string;
  language?: string;
  private toObject() {
    return {
      name: this.name,
      language: this.language,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<TabHeading["toObject"]> = JSON.parse(serialized);
    const resultItem = new TabHeading(item.name, item.language);
    return resultItem;
  }
}
export {TabHeading};
