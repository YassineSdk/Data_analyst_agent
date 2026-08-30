from typing import TypedDict, NotRequired, Annotated , Literal
from models import (
        Message,
        SQLState,
        AuditState,
        ExecutionState,
        Response,
        IntentHistory,
        AllPlots
    )

from utils import add_messages,add_intent_history
import pandas as pd 



class AgentState(TypedDict):
    messages: Annotated[list[Message],add_messages]
    mode : Literal["Automatic","Ask for clarification"]
    data : NotRequired[pd.DataFrame | None]
    intent_histories:Annotated[list[IntentHistory],add_intent_history]
    sql: NotRequired[SQLState | None ]
    audit: NotRequired[AuditState | None ]
    execution: NotRequired[ExecutionState | None ]
    response: NotRequired[Response  | None ] 
    plots_enabled : bool 
    allplots : NotRequired[AllPlots | None]