from typing import Any
import board
import busio
import math
from adafruit_htu21d import HTU21D
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


def map(x, in_min, in_max, out_min, out_max):
    out = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if out < out_min:
        return out_min
    elif out > out_max:
        return out_max
    else:
        return out


class AQS_ADS:
    def __init__(self, i2c):
        self.AQS_chan = AnalogIn(ADS.ADS1115(i2c), ADS.P0)
        # The load resistance on the board
        self.RLOAD = 4.2
        # Calibration resistance at atmospheric CO2 level
        self.RZERO = 76.63
        # self.PARAmeters for calculating ppm of CO2 from sensor resistance
        self.PARA = 116.6020682
        self.PARB = 2.769034857

        # self.PARAmeters to model temperature and humidity dependence
        self.CORA = 0.00035
        self.CORB = 0.02718
        self.CORC = 1.39538
        self.CORD = 0.0018
        self.CORE = -0.003333333
        self.CORF = -0.001923077
        self.CORG = 1.130128205

        # Atmospheric CO2 level for calibration purposes
        self.ATMOCO2 = 397.13

    """
    @brief  Get the self.CORrection factor to self.CORrect for temperature and humidity

    @self.PARAm[in] t  The ambient air temperature
    @self.PARAm[in] h  The relative humidity

    @return The calculated self.CORrection factor
    """

    def __getattribute__(self, __name: str) -> Any:
        try:
            return object.__getattribute__(self, __name)
        except AttributeError:
            if __name == "value":
                return self.getPPM()
            else:
                raise AttributeError(f"'AQS_ADS' has no attribute '{__name}'")

    def getCORrectionFactor(self, t, h):
        # Linearization of the temperature dependency curve under and above 20 degree C
        # below 20degC: fact = a * t * t - b * t - (h - 33) * d
        # above 20degC: fact = a * t + b * h + c
        # this assumes a linear dependency on humidity
        if t < 20:
            return (
                self.CORA * t * t - self.CORB * t + self.CORC - (h - 33.0) * self.CORD
            )
        else:
            return self.CORE * t + self.CORF * h + self.CORG

    """
    @brief  Get the resistance of the sensor, ie. the measurement value

    @return The sensor resistance in kOhm
    """

    def getResistance(self):
        return (
            (1023.0 / (map(self.AQS_chan.value, 110, 23797, 0, 1023) - 0.0)) - 1.0
        ) * self.RLOAD

    """
    @brief  Get the resistance of the sensor, ie. the measurement value self.CORrected
            for temp/hum

    @self.PARAm[in] t  The ambient air temperature
    @self.PARAm[in] h  The relative humidity

    @return The self.CORrected sensor resistance kOhm
    """

    def getCORrectedResistance(self, t, h):
        return self.getResistance() / self.getCORrectionFactor(t, h)

    """
    @brief  Get the ppm of CO2 sensed (assuming only CO2 in the air)

    @return The ppm of CO2 in the air
    """

    def getPPM(self):
        return self.PARA * math.pow((self.getResistance() / self.RZERO), -self.PARB)

    """
    @brief  Get the ppm of CO2 sensed (assuming only CO2 in the air), self.CORrected
            for temp/hum

    @self.PARAm[in] t  The ambient air temperature
    @self.PARAm[in] h  The relative humidity

    @return The ppm of CO2 in the air
    """

    def getCORrectedPPM(self, t, h):
        return self.PARA * math.pow(
            (self.getCORrectedResistance(t, h) / self.RZERO),
            -self.PARB,
        )

    """
    @brief  Get the resistance self.RZERO of the sensor for calibration purposes

    @return The sensor resistance self.RZERO in kOhm
    """

    def getRZERO(self):
        return self.getResistance() * math.pow(
            (self.ATMOCO2 / self.PARA), (1.0 / self.PARB)
        )

    """
    @brief  Get the self.CORrected resistance self.RZERO of the sensor for calibration
            purposes

    @self.PARAm[in] t  The ambient air temperature
    @self.PARAm[in] h  The relative humidity

    @return The self.CORrected sensor resistance self.RZERO in kOhm
    """

    def getCORrectedRZERO(self, t, h):
        return self.getCORrectedResistance(t, h) * math.pow(
            (self.ATMOCO2 / self.PARA), (1.0 / self.PARB)
        )

    """
    Re-maps a number from one range to another. That is, a value of fromLow would get mapped to toLow, 
    a value of fromHigh to toHigh, values in-between to values in-between, etc.

    # Arduino: (0 a 1023)
    # Raspberry Pi: (0 a 26690)

    More Info: https://www.arduino.cc/reference/en/language/functions/math/map/
    """


i2c = busio.I2C(board.SCL, board.SDA)
Temp_hum = HTU21D(i2c)
AQS = AQS_ADS(i2c)
