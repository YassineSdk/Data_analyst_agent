from typing import TypedDict, NotRequired, Annotated
from models import (
        Message,
        SQLState,
        AuditState,
        ExecutionState,
        Response,
        IntentHistory
    )


def add_messages(
    old:list[Message],
    new:list[Message])-> list[Message]:
    return old + new



class AgentState(TypedDict):
    messages: Annotated[list[Message],add_messages]
    current_message_id:str
    intent_histories:list[IntentHistory]
    sql: NotRequired[SQLState | None ]
    audit: NotRequired[AuditState | None ]
    execution: NotRequired[ExecutionState | None ]
    response: NotRequired[Response  | None ] 
