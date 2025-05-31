from src.main import app
import os


application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "application:application",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENV") == "dev"
    )
