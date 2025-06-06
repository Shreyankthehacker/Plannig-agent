from typing import List, Optional, Any,Annotated
from pydantic import BaseModel, Field
import operator

class GraphState(BaseModel):
    user_query: str = Field(..., description="The original input question or request from the user.")
    tasks: List[str] = Field(default_factory=list, description="List of sub-tasks generated from the user query.")
    tool: List[str] = Field(default_factory=list, description="List of the tools to be used for the particular task.")
    current_task_index: Annotated[int, operator.add] = Field(default=0, description="Index of the task currently being processed.")
    final_output: Annotated[List[str], operator.add]= Field(default=None, description="Final result to be returned to the user.")
    grade:int 
    code:Annotated[List[str], operator.add] = Field(default_factory=list, description="Code generated by the AI")