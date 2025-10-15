import re
import json

class JSONOutputParser:
    """
    Handles code fences like ```json or ````json.
    """

    CODE_BLOCK_REGEX = re.compile(r"^\s*`{3,4}json\s*|\s*`{3,4}\s*$" ,flags=re.DOTALL)

    @staticmethod
    def parse(llm_output: str) -> object:
        cleaned = JSONOutputParser.CODE_BLOCK_REGEX.sub("", llm_output.strip())
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON: {str(e)}\nRaw output:\n{llm_output}")
        return data
