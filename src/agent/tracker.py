from agents import Agent, Runner
from src.config.settings import settings
from src.tools.all_tools import TOOLS
from src.tools.get_spreadsheet_schema import get_spreadsheet_schema_impl
from src.prompt.tracker_prompt import build_tracker_prompt
from src.agent.session import session   
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY
)

async def tracker_agent(query: str):

    schema = await get_spreadsheet_schema_impl(settings.SPREADSHEET_ID)
    TRACKER_PROMPT = build_tracker_prompt(schema)

    tracker = Agent(
        name="Tracker Agent",
        instructions=TRACKER_PROMPT,
        tools=TOOLS,
        model=settings.OPENAI_MODEL_NAME,
    )

    result = await Runner.run(
        tracker,
        query,
        session=session
    )

    print(result.final_output)

    return result.final_output