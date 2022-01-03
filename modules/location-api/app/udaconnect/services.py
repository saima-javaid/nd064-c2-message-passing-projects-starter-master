import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List

from app import db, g
from app.udaconnect.models import Location
from app.udaconnect.schemas import LocationSchema
from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.sql import text

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-location-api")



class LocationService:
    @staticmethod
    def retrieve(location_id) -> Location:
        location, coord_text = (
            db.session.query(Location, Location.coordinate.ST_AsText())
            .filter(Location.id == location_id)
            .one()
        )

        # Rely on database to return text form of point to reduce overhead of conversion in app code
        location.wkt_shape = coord_text
        return location

    @staticmethod
    def create(location: Dict) -> Location:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logger.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")
        curr_data = Location()
        curr_data.person_id = location["person_id"]
        curr_data.creation_time = location["creation_time"]
        curr_data.coordinate = ST_Point(location["latitude"], location["longitude"])

        # Kafka Producer - Section to push new locations into the Kafka
        kafka_data = json.dumps(location).encode()
        kafka_producer = g.kafka_producer
        kafka_producer.send("locations", kafka_data)
        #kafka_producer.flush()
        # end Kafka Producer

        #Kafka Consumer
        consumer=g.kafka_consumer
        for message_location in consumer:
            kafka_data = message_location.value
            new_location = Location()
            new_location.person_id = kafka_data["person_id"]
            new_location.creation_time = kafka_data["creation_time"]
            new_location.coordinate = ST_Point(kafka_data["latitude"], kafka_data["longitude"])           
            db.session.add(new_location)
            db.session.commit()
            logger.warning(f"Kafka Consumes: {new_location.person_id},{new_location.creation_time},{new_location.coordinate}")
        #end Kafka Consumer
 
        return curr_data


    @staticmethod
    def retrieve_all() -> List[Location]:
        """Get all locations"""
        return db.session.query(Location).all()

