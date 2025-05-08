# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from google.cloud import secretmanager

import pymongo, os, time
import pika, json
from scrapy.exceptions import NotConfigured, DropItem
import ssl

class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_database):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_database
        self.client = None
        self.db = None

    @classmethod
    def __access_secret(cls, secret_id, project_id, version_id="latest"):
        if os.environ.get("LOCAL_DEBUG"):
            return json.dumps({"mongo_uri" : "mongodb+srv://autoblog-mongo:KcNjapi7vudFnGiP@ing-sis-dist.jsjoj8n.mongodb.net/?retryWrites=true&w=majority&appName=ing-sis-dist", "mongo_database": "automated-blog"})
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    
    @classmethod
    def from_crawler(cls, crawler):
        # Connessione al server MongoDB
        gcp_project_id = os.environ.get("GCP_PROJECT_ID", "gcp-automated-blog-test")
        mongodb_conn_secret = os.environ.get("GCP_MONGODB_SECRET", "mongodb-connection")
        
        mongodb_credentials = json.loads(cls.__access_secret(mongodb_conn_secret, gcp_project_id))

        return cls(**mongodb_credentials)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        for collection in ["rss-feed-items"]:
            if collection not in self.db.list_collection_names():
                spider.logger.info(f"Creazione collezione '{collection}'")
                self.db.create_collection(collection)
                
    def close_spider(self, spider):
        # Chiudi la connessione quando lo spider termina
        self.client.close()

    def process_item(self, item_dict, spider):
        # Inserisci o aggiorna il documento in MongoDB
        item_dict["processed"] = False
        
        result = self.db["rss-feed-items"].update_one(
            {'link': item_dict["link"]},  # Sostituisci con un campo univoco del tuo item
            {'$set': item_dict},
            upsert=True
        )
        
        # # Verifica se il documento è stato modificato
        # if not ( result.modified_count > 0 or result.upserted_id is not None ):
        #     raise DropItem("Missing specified keywords.")
            
        return item_dict

class RabbitMQPipeline:
    def __init__(self):
        self.connection = None
        self.channel = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def __access_secret(self, secret_id, project_id, version_id="latest"):
        if os.environ.get("LOCAL_DEBUG"):
            if secret_id == "rabbit-connection":
                return json.dumps({
                    "rabbitmq_protocol" : "amqp",
                    "rabbitmq_host" : "localhost",
                    "rabbitmq_queue" : "scrapy_items",
                    "rabbitmq_port" : "5672",
                    "rabbitmq_username" : "guest",
                    "rabbitmq_password" : "guest"
                })
            
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")

    def __create_rabbit_mq(
        self, 
        rabbitmq_protocol,
        rabbitmq_host,
        rabbitmq_queue,
        rabbitmq_port,
        rabbitmq_username,
        rabbitmq_password
    ):
        return f"{rabbitmq_protocol}://{rabbitmq_username}:{rabbitmq_password}@{rabbitmq_host}:{rabbitmq_port}"

    def open_spider(self, spider):
        # Leggi i parametri dalle variabili d'ambiente
        gcp_project_id = os.environ.get("GCP_PROJECT_ID", "gcp-automated-blog-test")
        rabbit_mq_conn_secret = os.environ.get("GCP_RABBIT_MQ_SECRET", "rabbit-connection")
        self.rabbit_mq_credentials = json.loads(self.__access_secret(rabbit_mq_conn_secret, gcp_project_id))


        url = self.__create_rabbit_mq(**self.rabbit_mq_credentials)
        parameters = pika.URLParameters(url)
        if os.environ.get("LOCAL_DEBUG") is None:
            # Connessione a RabbitMQ
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')
            parameters.ssl_options = pika.SSLOptions(context=ssl_context)

        max_retries = 5
        for attempt in range(max_retries):
            try:
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.rabbit_mq_credentials['rabbitmq_queue'], durable=True)
                break  # Successo, esci dal ciclo
            except pika.exceptions.AMQPConnectionError as e:
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    raise e  # Falliti tutti i tentativi

    def process_item(self, item, spider):
        # Converte il dizionario in una stringa JSON
        message = json.dumps(item)

        # Invia il messaggio a RabbitMQ
        self.channel.basic_publish(
            exchange='',
            routing_key=self.rabbit_mq_credentials['rabbitmq_queue'],
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ))
        spider.logger.info(f"Item sent to RabbitMQ: {message}")
        return item

    def close_spider(self, spider):
        # Chiudi la connessione con RabbitMQ
        if self.connection:
            self.connection.close()
