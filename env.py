import os
from typing import Final


class enviornment:
    openAIResponseLimit: Final[int] = int(
        os.environ["OPENAI_RESPONSE_LIMIT"])  # 500
    api_version: Final[str] = os.environ["AZURE_OPENAI_API_VERSION"]
    api_key: Final[str] = os.environ["AZURE_OPENAI_API_KEY"]
    openai_deployment: Final[str] = os.environ["AZURE_OPENAI_DEPLOYMENT"]
