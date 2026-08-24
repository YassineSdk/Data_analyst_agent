from pathlib import Path 
import yaml



def load_yaml(filename):
    PROJECT_PATH = Path(__file__).resolve().parent.parent
    PROMPT_PATH = PROJECT_PATH / "prompts" / filename

    with open(PROMPT_PATH,"r",encoding="utf-8") as f :
        prompt = yaml.safe_load(f)
    return(prompt["prompt"])
