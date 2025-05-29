from fastapi import FastAPI

from api_agent import app as api_agent_app
from retriever_agent import app as retriever_agent_app
from scraping_agent import app as scrapping_app
from language_agent import app as language_agent_app
from voice_agent import app as voice_agent_app

app = FastAPI()
# Include the sub-applications
app.include_router(api_agent_app,prefix="/api_agent")
app.include_router(retriever_agent_app,prefix="/retriever_agent")
app.include_router(scrapping_app,prefix="/scraping_agent")
app.include_router(language_agent_app,prefix="/language_agent")
app.include_router(voice_agent_app,prefix="/voice_agent")
