import json
import re


def extract_json_from_string(text):
    """
    Extracts and loads a JSON object or list from a string that contains
    a JSON code block.
    """
    # Use a more flexible regular expression to find content between ```json and ```
    # It now captures content starting with either { or [
    match = re.search(r"```json\s*(\[.*\]|\{.*\})\s*```", text, re.DOTALL)

    if match:
        json_string = match.group(1)
        try:
            # Attempt to parse the found string as JSON
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            # Return a detailed error message if parsing fails
            return {"error": f"Failed to parse JSON: {e}"}
    else:
        # Return an error if no JSON block is found
        return {"error": "No JSON block found"}
