from langchain_openai import ChatOpenAI
from src.config.settings import settings

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY
)

result = llm.invoke("Reply 'test successful'")
print(result)