from app import create_app
import uvicorn
from app.config import get_settings

settings = get_settings()

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        workers=1
    )
