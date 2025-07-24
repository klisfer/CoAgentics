import uvicorn
import logging
from fastapi import FastAPI, Body, HTTPException

from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part
from financial_advisor import root_agent as finance_agent

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session_service = InMemorySessionService()


# --- FastAPI App ---
app = FastAPI(
    title="Financial Advisor API",
    version="1.0.0",
)

# --- Endpoint ---
@app.post("/chat")
async def chat(user_message: str) -> dict:
    """Get a response from the finance advisor agent."""
    try:
        app_name, user_id, session_id = "finance_advisor_app", "user1", "session1"

        runner = Runner(
            agent=finance_agent,
            app_name=app_name,
            session_service=session_service
        )

        session = await session_service.create_session(app_name=app_name,
                                    user_id=user_id,
                                    session_id=session_id)
        print(f"Initial state: {session.state}")
        user_message = Content(role="User", parts=[Part(text=user_message)])
        print("******************************")
        print(user_message)
        for event in runner.run(user_id=user_id,
                                session_id=session_id,
                                new_message=user_message):
            # --- Check Updated State ---
            updated_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
            print(f"State after agent run: {updated_session.state}")
            print("####################################")
            print(event.content.parts[0].text)
        return {"response": event.content.parts[0].text}
    except Exception as e:
        logger.error("Chat error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# --- Server Startup ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
