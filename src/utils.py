from pathlib import Path 
import yaml
from models import *






def add_messages(
    old:list[Message],
    new:list[Message])-> list[Message]:
    return old + new

def add_intent_history(
    old: list[IntentHistory],
    new: list[IntentHistory]
    ) -> list[IntentHistory]:

    for new_history in new:
        for old_history in old:
            if old_history.message_id == new_history.message_id:
                old_history.intents.extend(new_history.intents)
                break
        else:
            old.append(new_history)

    return old

def get_current_history(state)->tuple[IntentHistory, IntentState]:
    message_id = state["messages"][-1].id

    # Find the current history
    history = next(
        h
        for h in state["intent_histories"]
        if h.message_id == message_id
    )
    latest_intent = history.intents[-1] if history.intents else None
    return history,latest_intent

def read_context(filename:str)->str:

    PROJECT_PATH = Path(__file__).resolve().parent.parent
    FILE_PATH = PROJECT_PATH / filename
    with open(FILE_PATH,"r",encoding="utf-8") as f:
        return f.read()


def load_yaml(filename):
    PROJECT_PATH = Path(__file__).resolve().parent.parent
    PROMPT_PATH = PROJECT_PATH / "prompts" / filename

    with open(PROMPT_PATH,"r",encoding="utf-8") as f :
        prompt = yaml.safe_load(f)
    return(prompt["prompt"])

def intent_template_maker(state)-> str:

    # 1. Get the current message ID
    last_message = state["messages"][-1]
    user_query = last_message.HumanMessages
    message_id = last_message.id

    # getting the history 
    history, _ = get_current_history(state)

    # 3. Build the complete intent/feedback history

    if history.intents:

        intent_history_text = "\n\n".join(
            f"""
            Iteration {i}:

            Intent:
            {intent.interpretation}

            Question:
            {intent.clarification}
            
            Feedback:
            {intent.feedback if intent.feedback else "No feedback provided."}

            """
            for i, intent in enumerate(history.intents)
        )

    else:
        intent_history_text = "No previous intent iterations."


    # 5. Build the LLM input

    human_template = f"""
    Original user query:
    {user_query}

    Data context:
    {read_context("data_context.txt")}

    Intent refinement history:
    {intent_history_text}

    """
    return human_template
