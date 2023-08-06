
from aerisweather.utils import AerisDateTime


class RiversCrestsHistoric:
    """ Defines an object for the Aeris API rivers historic crests data returned in an Aeris API responses """
    
    data = {}

    def __init__(self, json_data):
        """Constructor"""
        self.data = json_data

    @property
    def timestamp(self):
        """Returns the unix timestamp of the date of the crest"""
        return self.data["timestamp"]

    @property
    def dateTimeISO(self):
        """Returns the a Python DateTime date of the crest"""
        return AerisDateTime.AerisDateTime().get_datetime_from_aeris_iso(self.data["dateTimeISO"])

    @property
    def heightFT(self):
        """Returns the height in feet of the crest"""
        return self.data["heightFT"]

    @property
    def heightM(self):
        """Returns the height in meters of the crest"""
        return self.data["heightM"]
