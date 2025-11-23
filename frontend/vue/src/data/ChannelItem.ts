import type {SurveyItem} from "@/data/SurveyItem";
import type {LmsGatedAccessDetails} from "@/data/Protection";

class ChannelThumbnails {
  constructor(init?: Partial<ChannelThumbnails>) {
    Object.assign(this, init);
  }
  lecturer?: string;
}

class ChannelItem {
  constructor(init?: Partial<ChannelItem>) {
    Object.assign(this, init);
  }
  uuid?: string;
  course?: string;
  course_acronym?: string;
  faculty?: string;
  faculty_acronym?: string;
  faculty_color?: string;
  language?: string;
  lecturer?: string;
  license?: string;
  license_url?: string;
  semester?: string;
  tags?: Array<string>;
  thumbnails?: ChannelThumbnails;
  university?: string;
  university_acronym?: string;
  surveys?: Array<SurveyItem>;
  documents?: Array<string>;
  lms_gated_access?: boolean;
  lms_gated_access_details: LmsGatedAccessDetails;

  private toObject() {
    return {
      uuid: this.uuid,
      course: this.course,
      course_acronym: this.course_acronym,
      faculty: this.faculty,
      faculty_acronym: this.faculty_acronym,
      faculty_color: this.faculty_color,
      language: this.language,
      lecturer: this.lecturer,
      license: this.license,
      license_url: this.license_url,
      semester: this.semester,
      tags: this.tags,
      thumbnails: this.thumbnails,
      university: this.university,
      university_acronym: this.university_acronym,
      surveys: this.surveys,
      documents: this.documents,
      lms_gated_access: this.lms_gated_access,
      lms_gated_access_details: this.lms_gated_access_details,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<ChannelItem["toObject"]> = JSON.parse(serialized);
    const resultItem = new ChannelItem();
    resultItem.uuid = item.uuid;
    resultItem.course = item.course;
    resultItem.course_acronym = item.course_acronym;
    resultItem.faculty = item.faculty;
    resultItem.faculty_acronym = item.faculty_acronym;
    resultItem.faculty_color = item.faculty_color;
    resultItem.language = item.language;
    resultItem.lecturer = item.lecturer;
    resultItem.license = item.license;
    resultItem.license_url = item.license_url;
    resultItem.semester = item.semester;
    resultItem.tags = item.tags;
    resultItem.thumbnails = item.thumbnails;
    resultItem.university = item.university;
    resultItem.university_acronym = item.university_acronym;
    resultItem.surveys = item.surveys;
    resultItem.documents = item.documents;
    resultItem.lms_gated_access = item.lms_gated_access;
    resultItem.lms_gated_access_details = item.lms_gated_access_details;
    return resultItem;
  }
}

export {ChannelItem};
