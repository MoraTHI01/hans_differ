class Answer {
  constructor(init?: Partial<Answer>) {
    Object.assign(this, init);
  }
  index?: number;
  answer?: string;

  private toObject() {
    return {
      index: this.index,
      answer: this.answer,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<Answer["toObject"]> = JSON.parse(serialized);
    const resultItem = new Answer();
    resultItem.index = item.index;
    resultItem.answer = item.answer;
    return resultItem;
  }
}

class MultipleChoiceQuestion {
  constructor(init?: Partial<MultipleChoiceQuestion>) {
    Object.assign(this, init);
  }
  question?: string;
  answers?: Array<Answer>;
  correct_answer_index?: number;
  correct_answer_explanation?: string;
  creator?: string;
  editor?: string;

  private toObject() {
    return {
      question: this.question,
      answers: this.answers,
      correct_answer_index: this.correct_answer_index,
      correct_answer_explanation: this.correct_answer_explanation,
      creator: this.creator,
      editor: this.editor,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<MultipleChoiceQuestion["toObject"]> = JSON.parse(serialized);
    const resultItem = new MultipleChoiceQuestion();
    resultItem.question = item.question;
    resultItem.answers = item.answers;
    resultItem.correct_answer_index = item.correct_answer_index;
    resultItem.correct_answer_explanation = item.correct_answer_explanation;
    resultItem.creator = item.creator;
    resultItem.editor = item.editor;
    return resultItem;
  }
}

class QuestionItem {
  constructor(init?: Partial<QuestionItem>) {
    Object.assign(this, init);
  }
  index?: number;
  type?: string;
  mcq?: MultipleChoiceQuestion;

  private toObject() {
    return {
      index: this.index,
      type: this.type,
      mcq: this.mcq,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<QuestionItem["toObject"]> = JSON.parse(serialized);
    const resultItem = new QuestionItem();
    resultItem.index = item.index;
    resultItem.type = item.type;
    resultItem.mcq = item.mcq;
    return resultItem;
  }
}

class QuestionnaireItem {
  constructor(init?: Partial<QuestionnaireItem>) {
    Object.assign(this, init);
  }
  easy?: Array<QuestionItem>;
  medium?: Array<QuestionItem>;
  difficult?: Array<QuestionItem>;

  private toObject() {
    return {
      easy: this.easy,
      medium: this.medium,
      difficult: this.difficult,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<QuestionnaireItem["toObject"]> = JSON.parse(serialized);
    const resultItem = new QuestionnaireItem();
    resultItem.easy = item.easy;
    resultItem.medium = item.medium;
    resultItem.difficult = item.difficult;
    return resultItem;
  }
}

class QuestionnaireResultItem {
  constructor(init?: Partial<QuestionnaireResultItem>) {
    Object.assign(this, init);
  }
  interval?: Array<number>;
  result_index?: number;
  questionnaire?: QuestionnaireItem;

  private toObject() {
    return {
      interval: this.interval,
      result_index: this.result_index,
      questionnaire: this.questionnaire,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<QuestionnaireResultItem["toObject"]> = JSON.parse(serialized);
    const resultItem = new QuestionnaireResultItem();
    resultItem.interval = item.interval;
    resultItem.result_index = item.result_index;
    resultItem.questionnaire = item.questionnaire;
    return resultItem;
  }
}

class QuestionnaireResult {
  constructor(init?: Partial<QuestionnaireResult>) {
    Object.assign(this, init);
  }
  result?: Array<QuestionnaireResultItem>;
  type?: string;
  language?: string;

  private toObject() {
    return {
      result: this.result,
      type: this.type,
      language: this.language,
    };
  }

  serialize() {
    return JSON.stringify(this.toObject());
  }

  static fromSerialized(serialized: string) {
    const item: ReturnType<QuestionnaireResult["toObject"]> = JSON.parse(serialized);
    const resultItem = new QuestionnaireResult();
    resultItem.result = item.result;
    resultItem.type = item.type;
    resultItem.language = item.language;
    return resultItem;
  }
}

class QuestionnaireResults {
  constructor(init?: Partial<QuestionnaireResults>) {
    Object.assign(this, init);
  }
  result?: string;
  data?: Array<QuestionnaireResult>;
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
    const item: ReturnType<QuestionnaireResults["toObject"]> = JSON.parse(serialized);
    const resultItem = new QuestionnaireResults();
    resultItem.result = item.result;
    resultItem.data = item.data;
    return resultItem;
  }
}

export {
  Answer,
  MultipleChoiceQuestion,
  QuestionItem,
  QuestionnaireItem,
  QuestionnaireResultItem,
  QuestionnaireResult,
  QuestionnaireResults,
};
