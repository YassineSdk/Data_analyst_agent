from typing import TypedDict, NotRequired, Annotated , Literal
from models import (
        Message,
        SQLState,
        AuditState,
        ExecutionState,
        AnalystResponse,
        IntentHistory,
        AllPlots
    )

from utils import add_messages,add_intent_history
import pandas as pd 



class AgentState(TypedDict):
    messages: Annotated[list[Message],add_messages]
    mode : Literal["Automatic","Ask for clarification"]
    intent_histories:Annotated[list[IntentHistory],add_intent_history]
    sql: NotRequired[SQLState | None ]
    audit: NotRequired[AuditState | None ]
    execution: NotRequired[ExecutionState | None ]
    response: NotRequired[AnalystResponse  | None ] 
    plots_enabled : bool = False
    allplots : NotRequired[AllPlots | None]
