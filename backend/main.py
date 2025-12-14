import uvicorn
from cerina.api import app

if __name__ == "__main__":
    uvicorn.run("cerina.api:app", host="127.0.0.1", port=8000, reload=True)
