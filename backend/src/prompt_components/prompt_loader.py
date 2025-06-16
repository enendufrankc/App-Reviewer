def load_text(file_path: str) -> str:
    with open(file_path, 'r', encoding="utf-8") as file:
        text = file.read()
    return text
    
def load_prompt(file_path) -> str:
    # file_path = r"src\prompt_components\templates\system_prompt.txt"
    prompt = load_text(file_path)
    return prompt