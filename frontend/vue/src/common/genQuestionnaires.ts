import {useMessageStore} from "@/stores/message";
import {LoggerService} from "./loggerService";
import {apiClient} from "@/common/apiClient";
import type {Message, MessageContent, TextContent} from "@/data/Message";

export interface McqRequest {
  uuid: string;
  language: string;
  difficulty: string;
  context: string;
  contextUuid: string;
  avoid: boolean;
  avoidQuestions: string;
  reasoning: boolean;
}

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
    do_reasoning: boolean = false,
  ): Promise<object> {
    this.myLogger.log("sendMultipleChoiceQuestionRequest");
    const params = {
      uuid: prompt_context_uuid,
      language: language,
      difficulty: difficulty,
      context: prompt_context,
      contextUuid: prompt_context_uuid,
      avoid: avoid && avoid.length > 0,
      avoidQuestions: avoid?.join("\n"),
      reasoning: do_reasoning,
    } as McqRequest;
    const {data} = await apiClient.post("/sendMultipleChoiceQuestionRequest", params, {
      headers: {
        "Content-type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      // Adjust timeout as needed, currently 600 seconds, aka 5 min for questions
      timeout: 600000,
    });
    this.myLogger.log(data);
    let responseMessage = undefined;
    if ("data" in data && "result" in data.data[0]) {
      responseMessage = data.data[0].result[0] as Message;
    }
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
