from flask import Flask, jsonify,g
from flask_cors import CORS
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from kafka import KafkaProducer,KafkaConsumer
from json import dumps, loads
db = SQLAlchemy()


def create_app(env=None):
    from app.config import config_by_name
    from app.routes import register_routes

    app = Flask(__name__)
    app.config.from_object(config_by_name[env or "test"])
    api = Api(app, title="UdaConnect Location API", version="0.1.0")

    CORS(app, supports_credentials=True)  # Set CORS for development

    register_routes(api, app)
    db.init_app(app)

    @app.before_request
    def before_request():
        # Set up a Kafka producer and consumer
        TOPIC_NAME = 'locations'
        KAFKA_SERVER = 'kafka-headless:9092'
        #producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER,api_version=(0,10,2),value_serializer=lambda x: dumps(x).encode())
        #consumer = KafkaConsumer(TOPIC_NAME,bootstrap_servers=KAFKA_SERVER,api_version=(0,10,2),auto_offset_reset='earliest',enable_auto_commit=True,group_id='my-group',value_deserializer=lambda x: loads(x.decode()))
        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER,api_version=(0,10,2))
        consumer = KafkaConsumer(TOPIC_NAME,bootstrap_servers=KAFKA_SERVER,api_version=(0,10,2),auto_offset_reset='earliest',enable_auto_commit=True,group_id='my-group',value_deserializer=lambda x: loads(x.decode()))
        # Setting Kafka to g and use in other parts of application
        g.kafka_producer = producer
        g.kafka_consumer=consumer

    @app.route("/health")
    def health():
        return jsonify("healthy")

    return app
