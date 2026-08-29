from pathlib import Path 
import yaml



def load_yaml(filename):
    PROJECT_PATH = Path(__file__).resolve().parent.parent
    PROMPT_PATH = PROJECT_PATH / "prompts" / filename

    with open(PROMPT_PATH,"r",encoding="utf-8") as f :
        prompt = yaml.safe_load(f)
    return(prompt["prompt"])


def intent_template_maker(state)-> str:

    # 1. Get the current message ID
    last_message = state["conversation"].message[-1]
    user_query = last_message.HumanMessages
    message_id = last_message.id

    # 2. Find the intent history belonging to this message
    history = next(
        (
            history
            for history in state["intent_histories"]
            if history.message_id == message_id
        ),
        None,
    )

    if history is None:
        raise ValueError(
            f"No intent history found for message_id={message_id}"
        )

    # 3. Build the complete intent/feedback history

    if history.iterations:

        intent_history_text = "\n\n".join(
            f"""
            Iteration {i}:

            Intent:
            {iteration.interpretation}

            Feedback:
            {iteration.feedback if iteration.feedback else "No feedback provided."}

            Approved:
            {iteration.approved}
            """
            for i, iteration in enumerate(history.iterations)
        )

    else:
        intent_history_text = "No previous intent iterations."


    # 5. Build the LLM input

    human_template = f"""
    Original user query:
    {user_query}

    Data context:
    {state["data_context"]}

    Intent refinement history:
    {intent_history_text}

    """
    return human_template
