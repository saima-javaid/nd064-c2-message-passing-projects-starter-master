from datetime import datetime

from app.udaconnect.models import  Location
from app.udaconnect.schemas import (
    LocationSchema,
  
)
from app.udaconnect.services import  LocationService
from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource
from typing import Optional, List

DATE_FORMAT = "%Y-%m-%d"

api = Namespace("UdaConnect", description="Connections via geolocation.")  # noqa




class LocationResource(Resource):
    # post location
    @api.route("/location")
    @accepts(schema=LocationSchema)
    @responds(schema=LocationSchema)   
    def post(self) -> Location:
        request.get_json()
        location: Location = LocationService.create(request.get_json())
        return location

    # get location by ID
    @api.route("/location/<location_id>")
    @api.param("location_id", "Unique ID for a given Location", _in="query") 
    @responds(schema=LocationSchema)
    def get(self, location_id) -> Location:
        location: Location = LocationService.retrieve(location_id)
        return location

    #get all locations
    @api.route("/locations")
    @responds(schema=LocationSchema, many=True)
    def get(self) -> List[Location]:
        locations: List[Location] = LocationService.retrieve_all()
        return locations    



