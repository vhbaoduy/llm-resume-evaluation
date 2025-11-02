from langchain_core.language_models import BaseChatModel


class BaseAgent:
    def __init__(self, name: str, llm: BaseChatModel):
        self._name = name
        self.model = llm
        self.chain = None

    @property
    def name(self):
        return self._name

    def __call__(self, *args, **kwds):
        raise NotImplementedError
