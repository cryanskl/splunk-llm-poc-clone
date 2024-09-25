import azure.functions as func
import logging
import json
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from env import enviornment
from concurrent.futures import ThreadPoolExecutor, as_completed

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

gpt4_model = AzureChatOpenAI(
        openai_api_version=enviornment.api_version,
        # azure_deployment need at least 0125-Preview model for GPT4 with agent
        azure_deployment=enviornment.openai_deployment,
        max_tokens=enviornment.openAIResponseLimit
        )

@app.route(route="summary")
def summary(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    input_text = req.params.get('input')
    logging.info(input_text)
    if not input_text:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            input_text = req_body.get('input')

    if input_text: 
        result = getSummary(input_text)  
        return func.HttpResponse(result)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
        
@app.route(route="jsonsummary")
def jsonsummary(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    input_text = req.params.get('input')
    logging.info(input_text)
    if not input_text:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            input_text = req_body.get('input')

    if input_text: 
        result = {
            "answer":getSummary(input_text)  
            }
        return func.HttpResponse(json.dumps(result),mimetype="application/json")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

@app.route(route="qna", methods=(["POST"]))
def qna(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    req_body = req.get_json()
    input_text = req_body.get('input')
    ai_question_text = req_body.get('ai_question')
    logging.info(input_text)
    logging.info(ai_question_text)
        
    if input_text and ai_question_text: 
        result = getQna(ai_question_text, input_text)  
        return func.HttpResponse(result)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

@app.route(route="bulkqna", methods=(["POST"]))
def bulkqna(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    req_body = req.get_json()
    input = req_body.get('input')
    ai_question = req_body.get('ai_question')
    rows = req_body.get('rows')
        
    if input and ai_question and rows: 
        result = getBulkQna(ai_question, input, rows)  
        return func.HttpResponse(result)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
    
def getSummary(input_text:str) -> str:
    prompt = ChatPromptTemplate.from_template("Summarize below message within 50 words --------message-------------- {topic}")
    output_parser = StrOutputParser()
    chain = prompt|gpt4_model|output_parser
    return chain.invoke({"topic":input_text})
        
def getQna(ai_question_text:str, input_text:str) -> str:
    prompt = ChatPromptTemplate.from_template("As a professional network engineer, Please help to answer this question based on provided syslogs record : {question}  -------- syslogs record-------------- {topic}")
    output_parser = StrOutputParser()
    chain = prompt|gpt4_model|output_parser
    return chain.invoke(input={"question": ai_question_text, "topic": input_text})

def getBulkQna(ai_question:str, input_field:str, rows:object) -> str:
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_row = {
            executor.submit(getQna, result[ai_question].strip(), result[input_field].strip()): result
            for result in rows
        }

        for future in as_completed(future_to_row):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f'Row generated an exception: {exc}')
                continue
    
    s = ' '.join(results)
    return getSummary(s)

def getInterface(input_text:str) -> str:
    prompt = ChatPromptTemplate.from_template("Extract the IP, NE Name, Slot ID, Port ID, Interface ID, Channel ID from below log message, you should only return the extract result with pattern IP-NEName-SlotID-PortID-InterfaceID-ChannelID       --------message-------------- {topic}")
    output_parser = StrOutputParser()
    chain = prompt|gpt4_model|output_parser
    return chain.invoke({"topic":input_text})

@app.route(route="interface", auth_level=func.AuthLevel.FUNCTION)
def interface(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    input_text = req.params.get('input')
    logging.info(input_text)
    if not input_text:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            input_text = req_body.get('input')

    if input_text: 
        result = getInterface(input_text)  
        return func.HttpResponse(result)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
        
