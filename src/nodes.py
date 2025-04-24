from jupyter_client import KernelManager
from state import GraphState
import re
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from serpapi import GoogleSearch
llm = ChatGoogleGenerativeAI(model = 'gemini-1.5-flash',temperature = 0.1)
import wikipedia
import re
import ast
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import END
from dotenv import load_dotenv
load_dotenv()
import os 
from prompts import code_prompt,PLANNING_PROMPT,GRADE_PROMPT


SERP = os.environ["SERPAPI_API_KEY"]


def run_in_jupyter_kernel(code: str) -> str:
    """
    Executes Python code in a temporary Jupyter kernel and returns the output.
    
    Args:
        code (str): Python code to execute.
        
    Returns:
        str: Output from the execution (stdout or error).
    """
    # Start a kernel
    ##print('kernel')
    km = KernelManager()
    km.start_kernel()
    kc = km.client()
    kc.start_channels()

    try:
        # Send the code for execution
        kc.execute(code)

        # Collect output
        output = ""
        while True:
            msg = kc.get_iopub_msg()
            msg_type = msg['msg_type']

            if msg_type == 'stream':
                output += msg['content']['text']
            elif msg_type == 'execute_result':
                output += str(msg['content']['data']['text/plain'])
            elif msg_type == 'error':
                output += '\n'.join(msg['content']['traceback'])
            elif msg_type == 'status' and msg['content']['execution_state'] == 'idle':
                break

        return output.strip()

    finally:
        # Clean up kernel
        kc.stop_channels()
        km.shutdown_kernel()



def extract_code_from_aimessage(message) -> str:
    """
    Extracts and cleans Python code from an AIMessage, removing any markdown formatting such as triple backticks.
    
    Args:
        message (Any): The message object returned by the language model (e.g., AIMessage from LangChain).
        
    Returns:
        str: Clean Python code ready for execution.
    """
    code = re.sub(r"```(?:python)?", "", message.content)
    code = re.sub(r"```", "", code)
    return code.strip()
    
def code_generation(state: GraphState):
    """
    Tool to generate Python code for a task, execute it in a Jupyter kernel, and return the output.
    """

    task = state.tasks[state.current_task_index]
    prompt = ChatPromptTemplate.from_template(template=code_prompt)
    chain = prompt | llm 
    code_response = chain.invoke({'sub_task': task})
    code = extract_code_from_aimessage(code_response)
    output = run_in_jupyter_kernel(code)
    result = (
        f"Task: {task}\n"
        f"Generated Code:\n```python\n{code}\n```\n"
        f"Output:\n{output}"
    )

    return {'code': state.code + [result],'current_task_index':state.current_task_index+1}

tavily = TavilySearchResults()

def websearch(state: GraphState):
    '''Tool to perform web search'''
    #print('search')
    task = state.tasks[state.current_task_index]
    results = tavily.invoke(task)

    # Format each result
    formatted_results = []
    for i, res in enumerate(results[:5]):
        title = res.get("title", "No Title")
        url = res.get("url", "No URL")
        content = res.get("content", "No Content").split('\n')[0]  # Short snippet
        formatted_results.append(f"{i+1}. {title}\n   {url}\n   Snippet: {content}")

    # Append to final_output
    return {
        "final_output": state.final_output + ["Top Web Search Results:"] + formatted_results,
        'current_task_index':state.current_task_index+1
    }


def wiki_explainer_tool(state:GraphState):
    """Explains a topic using Wikipedia summary."""
    ##print("wiki")
    task = state.tasks[state.current_task_index]
    try:
        out = wikipedia.summary(task, sentences=5)
    except Exception as e:
       return {"final_output":state.final_output}
    return {"final_output":state.final_output+[f'The wikipedia says :: {out}'],'current_task_index':state.current_task_index+1}

def youtube_search_serpapi(state: GraphState):
    '''This tool is used to get the youtube links and other info regarding the topics'''
    ##print("yt")
    params = {
        "engine": "youtube",
        "search_query": state.tasks[state.current_task_index],
        "api_key": SERP
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    videos = results.get("video_results", [])[:5]
    ##print(videos)
    formatted_results = [
        f"{i + 1}. {v.get('title')}\n   {v.get('link')}"
        for i, v in enumerate(videos)
    ]

    return {
    'final_output': state.final_output + ["The YouTube videos suggested are:"]+  formatted_results,'current_task_index':state.current_task_index+1}


tools = [websearch,wiki_explainer_tool,code_generation,run_in_jupyter_kernel]

llm = llm.bind_tools(tools = tools)


def break_task(state: GraphState) :
    ##print("breaking task")
    planning_prompt = ChatPromptTemplate.from_template(PLANNING_PROMPT)
    planning_chain= planning_prompt | llm  


    tasks = planning_chain.invoke({"user_query": state.user_query})

    ##print("Planned Tasks:", tasks)  
    task_string = tasks.content
    ##print(task_string)
    match = re.search(r"\[.*\]", task_string, re.DOTALL)
    if not match:
        raise ValueError("No valid task list found in the string.")
    
    task_list_str = match.group(0)
    l =  ast.literal_eval(task_list_str)
    task = []
    tool = []
    for i in list(l):
        task.append(i['task'])
        tool.append(i['tool'])
    return {'tasks':task  , 'tool':tool}


def router_node(state):
    # Explicitly define task names
    task_names = [
        "websearch",
        "wiki_explainer_tool",
        "code_generation",
        "run_in_jupyter_kernel",
        "youtube_search_serpapi"
    ]
    
    # Select the task based on the current task index in the state
    current_task = task_names[state.current_task_index]
    return current_task

def continue_or_not(state):
    state.grade = 4  # Example grading logic (you can update this dynamically)
    if state.grade > 3:
        return END  # If the grade is greater than 3, end the flow
    else:
        return "break_task"  # Otherwise, loop back to "break_task"


# grading is remaining and also memory part

def grading(state: GraphState):
    prompt = ChatPromptTemplate.from_template(template=GRADE_PROMPT)
    chain = prompt | llm
    grade_response = chain.invoke({
        'userquery': state.user_query,
        'final_answer': state.final_output
    })
    
    # Extract number from LLM response
    match = re.search(r'\d+', grade_response.content)
    grade = int(match.group()) if match else 0

    return {'grade': grade}

