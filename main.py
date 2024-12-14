import requests
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO


from api.handlers import events_router

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app = FastAPI(title="Events API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_api_router = APIRouter()

main_api_router.include_router(events_router, prefix="/events", tags=["events"])
app.include_router(main_api_router)


@app.get("/")
async def root():
    r = requests.get("https://afisha7.ru/uploads/gallery/films/rb_15105.webp")
    im = Image.open(BytesIO(r.content))
    width, height = im.size
    return {"width": width,
            "height": height}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)