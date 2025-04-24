from nodes import websearch,youtube_search_serpapi,break_task,code_generation,continue_or_not,llm,router_node,wiki_explainer_tool,run_in_jupyter_kernel,grading
import os 
from  state import GraphState

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
long_memory = InMemoryStore()
short_memory = MemorySaver()
from state import GraphState




def router_node(state:GraphState):
    
    if state.tasks[state.current_task_index]=="code_generation":
        return "code_generation"

    return END

def continue_or_not(state):
    state.grade = 4  
    if state.grade > 3:
        return END  
    else:
        return "break_task"  


builder = StateGraph(GraphState)


builder.add_node(websearch)
builder.add_node(wiki_explainer_tool)
builder.add_node(code_generation)
builder.add_node(run_in_jupyter_kernel)
builder.add_node(youtube_search_serpapi)
builder.add_node(grading)
builder.add_node(break_task)


builder.add_edge(START, "break_task")  
builder.add_conditional_edges("break_task", router_node)  
builder.add_edge("break_task","youtube_search_serpapi")
builder.add_edge("break_task","wiki_explainer_tool")
builder.add_edge("break_task","websearch")
builder.add_edge("break_task","code_generation")
builder.add_edge("websearch", "grading")
builder.add_edge("wiki_explainer_tool", "grading")
builder.add_edge("youtube_search_serpapi", "grading")
builder.add_edge("code_generation", "grading")
builder.add_edge("run_in_jupyter_kernel", "grading")
builder.add_conditional_edges("grading", continue_or_not)  


graph = builder.compile(checkpointer=short_memory,store=long_memory)


def plan(query):
    state = GraphState(user_query=query,current_task_index=0,tasks = [],final_output=[],task_outputs=[],grade = 0)
    return graph.invoke(state)

state = GraphState(user_query="Writing a code for sorting the array",current_task_index=0,tasks = [],final_output=[],task_outputs=[],grade = 0)
config = {"configurable": {"thread_id": "1", "user_id": "1"}}
state = graph.invoke(state,config=config)


print(state)
