"""Точка входа — FastAPI + Uvicorn."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.db import Database
from core.sheet import Sheet

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

db = Database("data/sheet.db")
sheet = Sheet(db)


class CellInput(BaseModel):
    value: str


@app.get("/")
async def root():
    return {"message": "Open http://localhost:8000/static/index.html"}


@app.get("/api/sheet")
async def get_sheet():
    return sheet.to_dict()


@app.get("/api/cell/{addr}")
async def get_cell(addr: str):
    return sheet.get_cell(addr)


@app.post("/api/cell/{addr}")
async def set_cell(addr: str, data: CellInput):
    sheet.set(addr, data.value)
    return {"ok": True, "sheet": sheet.to_dict()}


@app.delete("/api/clear")
async def clear_sheet():
    sheet.clear()
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
