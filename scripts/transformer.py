import re
import json

def normalize_text(text: str) -> str:
    # normalize unicode quotes
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')

    replacements = {
        "don't": "do not",
        "doesn't": "does not",
        "can't": "cannot",
        "it's": "it is",
        "you're": "you are",
        "aren't": "are not",
        "won't": "will not",
    }
    for k, v in replacements.items():
        text = re.sub(rf"\b{k}\b", v, text, flags=re.IGNORECASE)
    return text.strip()


def split_sentences(text: str):
    # basic sentence splitter (we improve later)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def transform_script(raw_text: str):
    normalized = normalize_text(raw_text)
    sentences = split_sentences(normalized)

    output = []
    for i, sentence in enumerate(sentences):
        role = "lore"

        if i == 0 or sentence.isupper():
            role = "hook"
        elif sentence.endswith("?"):
            role = "beat"
        elif any(word in sentence.lower() for word in ["wait", "listen", "stop"]):
            role = "hook"
        elif any(word in sentence.lower() for word in ["subscribe", "follow", "like", "comment"]):
            role = "cta"
            
        output.append({
        "type": role,
        "intent": "emphasis" if role in ["hook", "cta"] else "normal",
        "energy": classify_energy(sentence, role),
        "text": sentence
    })

    return output
def classify_energy(sentence: str, role: str) -> str:
    s = sentence.lower()

    if role in ["hook", "cta"]:
        return "high"

    if any(word in s for word in ["wait", "listen", "stop", "now"]):
        return "high"

    if sentence.endswith("?"):
        return "medium"

    return "medium"


if __name__ == "__main__":
    raw = """
    WAIT, there is no way you don't know why we don't fall off the Earth.
    Is it a skill issue?
    No, it’s just gravity, and it’s actually cracked.
    """

    transformed = transform_script(raw)

    print(json.dumps(transformed, indent=2))
