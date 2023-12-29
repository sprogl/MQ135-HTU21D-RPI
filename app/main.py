#!/usr/bin/env python3
# Got some parts of the code from
# https://github.com/danielcshn/MQ135-ADS1115-Python

import uvicorn
from core.sensors import Temp_hum, AQS
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {
        "temperature": Temp_hum.temperature,
        "humidity": Temp_hum.relative_humidity,
        "air quality": AQS.getCORrectedPPM(
            Temp_hum.temperature, Temp_hum.relative_humidity
        ),
    }


@app.get("/temp")
async def temp():
    return f"The current temperature is {round(Temp_hum.temperature, 1)} ℃."


@app.get("/hum")
async def hum():
    return f"The current humidity level is {round(Temp_hum.relative_humidity, 1)} %."


@app.get("/aqs")
async def aqs():
    return f"The current CO₂ concentration is {round(AQS.getCORrectedPPM(Temp_hum.temperature, Temp_hum.relative_humidity), 1)} ppm."


if __name__ == "__main__":
    config = uvicorn.Config("main:app", port=80, log_level="info")
    server = uvicorn.Server(config)
    server.run()
