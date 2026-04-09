def length_score(output):
    return len(output)

def keyword_score(output, keyword):
    return keyword.lower() in output.lower()

def basic_evaluation(output, prompt):
    return {
        "length": length_score(output),
        "contains_prompt_word": keyword_score(output, prompt.split()[0])
    }