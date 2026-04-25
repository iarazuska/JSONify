import json


def format_json(text):
    try:
        parsed = json.loads(text)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        return formatted, None
    except json.JSONDecodeError as e:
        return None, f"Error en línea {e.lineno}, columna {e.colno}: {e.msg}"


def load_json_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read(), None
    except Exception as e:
        return None, str(e)


def save_json_file(filepath, content):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, None
    except Exception as e:
        return False, str(e)


def get_stats(text):
    lines = text.count("\n") + 1 if text.strip() else 0
    chars = len(text)
    return lines, chars