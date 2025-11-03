class UrlClasses {
  constructor(init?: Partial<UrlClasses>) {
    Object.assign(this, init);
  }
  videos?: Array<string>;
  science?: Array<string>;
  news?: Array<string>;
  wiki?: Array<string>;
  pictures?: Array<string>;
  social?: Array<string>;
  other?: Array<string>;
  private toObject() {
    return {
      videos: this.videos,
      science: this.science,
      news: this.news,
      wiki: this.wiki,
      pictures: this.pictures,
      social: this.social,
      other: this.other,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<UrlClasses["toObject"]> = JSON.parse(serialized);
    const resultItem = new UrlClasses();
    resultItem.videos = item.videos;
    resultItem.science = item.science;
    resultItem.news = item.news;
    resultItem.wiki = item.wiki;
    resultItem.pictures = item.pictures;
    resultItem.social = item.social;
    resultItem.other = item.other;
    return resultItem;
  }
}

class PageItem {
  constructor(init?: Partial<PageItem>) {
    Object.assign(this, init);
  }
  start?: number;
  end?: number;
  private toObject() {
    return {
      start: this.start,
      end: this.end,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<PageItem["toObject"]> = JSON.parse(serialized);
    const resultItem = new PageItem();
    resultItem.start = item.start;
    resultItem.end = item.end;
    return resultItem;
  }
}

class Alignment {
  [time: string]: number;
}

class SlidesImagesMeta {
  constructor(init?: Partial<SlidesImagesMeta>) {
    Object.assign(this, init);
  }
  timestamp: string;
  title: string;
  course: string;
  course_acronym: string;
  faculty: string;
  faculty_acronym: string;
  university: string;
  university_acronym: string;
  language: string;
  tags: Array<string>;
  lecturer: string;
  semester: string;
  filename: string;
  page: PageItem;
  urls: Array<string>;
  urls_by_class: UrlClasses;
  words: Array<string>;
  text: string;
  alignment: Alignment;

  private toObject() {
    return {
      timestamp: this.timestamp,
      title: this.title,
      course: this.course,
      course_acronym: this.course_acronym,
      faculty: this.faculty,
      faculty_acronym: this.faculty_acronym,
      university: this.university,
      university_acronym: this.university_acronym,
      language: this.language,
      tags: this.tags,
      lecturer: this.lecturer,
      semester: this.semester,
      filename: this.filename,
      page: this.page,
      urls: this.urls,
      urls_by_class: this.urls_by_class,
      words: this.words,
      text: this.text,
      alignment: this.alignment,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<SlidesImagesMeta["toObject"]> = JSON.parse(serialized);
    const resultItem = new SlidesImagesMeta();
    resultItem.timestamp = item.timestamp;
    resultItem.title = item.title;
    resultItem.course = item.course;
    resultItem.course_acronym = item.course_acronym;
    resultItem.faculty = item.faculty;
    resultItem.faculty_acronym = item.faculty_acronym;
    resultItem.university = item.university;
    resultItem.university_acronym = item.university_acronym;
    resultItem.language = item.language;
    resultItem.tags = item.tags;
    resultItem.lecturer = item.lecturer;
    resultItem.semester = item.semester;
    resultItem.filename = item.filename;
    resultItem.page = item.page;
    resultItem.urls = item.urls;
    resultItem.urls_by_class = item.urls_by_class;
    resultItem.words = item.words;
    resultItem.text = item.text;
    resultItem.alignment = item.alignment;

    return resultItem;
  }
}

class SlidesImagesMetaResults {
  constructor(init?: Partial<SlidesImagesMetaResults>) {
    Object.assign(this, init);
  }
  result?: string;
  data?: Array<SlidesImagesMeta>;
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
    const item: ReturnType<SlidesImagesMetaResults["toObject"]> = JSON.parse(serialized);
    const resultItem = new SlidesImagesMetaResults();
    resultItem.result = item.result;
    resultItem.data = item.data;
    return resultItem;
  }
}

export {Alignment, UrlClasses, PageItem, SlidesImagesMeta, SlidesImagesMetaResults};
