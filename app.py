from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
from uvicorn import run as app_run

from typing import Optional

from rain_prediction.constants import APP_HOST, APP_PORT
from rain_prediction.pipeline.prediction_pipeline import RainData, RainClassifier
from rain_prediction.pipeline.training_pipeline import TrainPipeline

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

class DataForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.Rainfall: Optional[float] = None
        self.WindGustSpeed: Optional[float] = None
        self.WindSpeed9am: Optional[float] = None
        self.WindSpeed3pm: Optional[float] = None
        self.Humidity9am: Optional[float] = None
        self.Humidity3pm: Optional[float] = None
        self.WindGustDir: Optional[float] = None
        self.WindDir9am: Optional[float] = None
        self.WindDir3pm: Optional[float] = None
        self.Location: Optional[str] = None
    
    async def get_rain_data(self):
        form = await self.request.form()
        self.Rainfall = form.get("Rainfall")
        self.WindGustSpeed  = form.get("WindGustSpeed")
        self.WindSpeed9am = form.get("WindSpeed9am")
        self.WindSpeed3pm = form.get("WindSpeed3pm")
        self.Humidity9am = form.get("Humidity9am")
        self.Humidity3pm = form.get("Humidity3pm")
        self.WindGustDir = form.get("WindGustDir")
        self.WindDir9am = form.get("WindDir9am")
        self.WindDir3pm = form.get("WindDir3pm")
        self.Location = form.get("Location")

@app.get("/", tags=["authentication"])
async def index(request: Request):
    return templates.TemplateResponse("rain.html", {"request": request, "context": "rendering"})

@app.get("/train")
async def trainRouteClient():
    try:
        train_pipeline = TrainPipeline()
        
        train_pipeline.run_pipeline()
        return Response("Training successful!.")
    
    except Exception as e:
        raise Response(f"Error Occured: {e}.")

@app.post("/")
async def predictRouteClient(request: Request):
    try:
        form = DataForm(request)
        await form.get_rain_data()
        
        rain_data = RainData(Rainfall = form.Rainfall,
                             WindGustSpeed  = form.WindGustSpeed,
                             WindSpeed9am = form.WindSpeed9am,
                             WindSpeed3pm = form.WindSpeed3pm,
                             Humidity9am = form.Humidity9am,
                             Humidity3pm = form.Humidity3pm,
                             WindGustDir = form.WindGustDir,
                             WindDir9am = form.WindDir9am,
                             WindDir3pm = form.WindDir3pm,
                             Location = form.Location)
        
        rain_df = rain_data.get_rain_input_dataframe()
        
        model_predictor = RainClassifier()
        
        value = model_predictor.predict(dataframe=rain_df)[0]
        
        status = None
        if value == 1:
            status = "Yes"
        else:
            status = "No"
        
        return templates.TemplateResponse(
            "rain.html",
            {"request": request, "context": status}
        )
    
    except Exception as e:
        return {"status": False, "error": f"{e}"}


if __name__=="__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)