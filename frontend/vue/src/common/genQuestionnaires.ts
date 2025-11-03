import {useMessageStore} from "@/stores/message";
import {LoggerService} from "./loggerService";
import type {Message, MessageContent, TextContent} from "@/data/Message";

/*
 * QuestionnaireGenerator
 **/
export class QuestionnaireGenerator {
  myLogger: LoggerService;
  public difficulties: string[];
  public default_difficulty: string;

  constructor() {
    this.myLogger = new LoggerService();
    this.difficulties = ["easy", "medium", "difficult"];
    this.default_difficulty = "easy";
  }

  public async generateMcq(
    difficulty: string,
    avoid: string[],
    language: string,
    prompt_context: string | undefined,
    prompt_context_uuid: string | undefined,
  ): Promise<object> {
    let prompt_en = `Create a single ${difficulty} difficult multiple choice question (max. 240 chars) with 4 short answers (max. 120 chars) with unique index from 0 to 3. Provide the correct answers associated index and a short explanation (max. 512 chars) as valid JSON without any newlines.`;
    if (avoid && avoid.length > 0) {
      prompt_en += ` Avoid the following already generated questions: '${avoid.join("\n")}'.`;
    }
    let prompt_de = `Erstelle eine einzelne Multiple-Choice-Frage mit Schwierigkeitsgrad ${difficulty} (max. 240 Zeichen) mit 4 kurzen Antworten (max. 120 Zeichen) mit eindeutigen Indexen von 0 bis 3. Gib die richtigen Antworten mit zugehörigem Index und einer kurzen Erläuterung (max. 512 Zeichen) als gültiges JSON ohne Zeilenumbrüche zurück.`;
    if (avoid && avoid.length > 0) {
      prompt_de += ` Vermeide die folgenden bereits generierten Fragen: '${avoid.join("\n")}'.`;
    }

    let prompt = prompt_en;
    if (language === "en") {
      prompt = prompt_en;
    } else if (language === "de") {
      prompt = prompt_de;
    }
    const msgTextItem = {
      type: "text",
      text: prompt,
    } as TextContent;
    const item = {
      language: language,
      content: [msgTextItem],
    } as MessageContent;
    const requestMessage = {
      content: [item],
      isUser: true,
      context: prompt_context,
      contextUuid: prompt_context_uuid,
      useContext: true,
      useContextAndCite: false,
      useTranslate: false,
      history: [],
      stream: false,
    } as Message;
    this.myLogger.log("sendMultipleChoiceQuestionRequest");
    this.myLogger.log(requestMessage);
    const responseMessage = await useMessageStore().transferMessage(
      "/sendMultipleChoiceQuestionRequest",
      requestMessage,
    );
    if (responseMessage === undefined) {
      return;
    }
    this.myLogger.log("Questionnaire");
    let my_content = responseMessage.content[0].content[0].text;
    my_content = my_content.replaceAll('\\\\\\\\"', '"');
    my_content = my_content.replaceAll("\\\n", "");
    my_content = my_content.replaceAll("\\n", "");
    my_content = my_content.replaceAll("\n", "");
    const count_open = (my_content.match(/{/g) || []).length;
    const count_closed = (my_content.match(/}/g) || []).length;
    if (count_open > count_closed) {
      for (let index = count_closed; index < count_open; index++) {
        my_content += "}";
      }
    }
    this.myLogger.log(my_content);
    try {
      return JSON.parse(my_content);
    } catch (e) {
      this.myLogger.error("Questionnaire format error!");
    }
  }
}
