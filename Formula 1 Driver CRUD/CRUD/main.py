from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
import models
from database import engine, sessionlocal
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def mostrar_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Rota para a página index.html
@app.get("/index", response_class=HTMLResponse)
async def mostrar_index(request: Request, db: Session = Depends(get_db)):
    # Buscar os pilotos do banco de dados
    drivers = db.query(models.Driver).all()
    return templates.TemplateResponse("index.html", {"request": request, "drivers": drivers})

@app.post("/add")
async def add(request: Request, name: str = Form(...), team: str = Form(...), nationality: str = Form(...), db: Session = Depends(get_db)):
    driver = models.Driver(name=name, team=team, nationality=nationality)
    db.add(driver)
    db.commit()
    # Redirecionar para a página "index.html" após adicionar um novo piloto
    return RedirectResponse(url="/index", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/addnew")
async def addnew(request: Request):
    return templates.TemplateResponse("addnew.html", {"request": request})

@app.get("/edit/{driver_id}")
async def edit(request: Request, driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "driver": driver})

@app.post("/update/{driver_id}")
async def update(request: Request, driver_id: int, name: str = Form(...), team: str = Form(...), nationality: str = Form(...), db: Session = Depends(get_db)):
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    driver.name = name
    driver.team = team
    driver.nationality = nationality
    db.commit()
    return RedirectResponse(url="/index", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/delete/{driver_id}")
async def delete(request: Request, driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    db.delete(driver)
    db.commit()
    return RedirectResponse(url="/index", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=7777)
