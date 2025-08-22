import json
import re

def extract_json_from_string(text):
    """
    Extracts and loads a JSON object from a string that contains
    a JSON code block.
    """
    # Regular expression to find content between ```json and ```
    match = re.search(r'```json\s*(\{.*\})\s*```', text, re.DOTALL)
    if match:
        json_string = match.group(1)
        try:
            # Attempt to parse the found string as JSON
            return json.loads(json_string)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON"}
    else:
        return {"error": "No JSON block found"}