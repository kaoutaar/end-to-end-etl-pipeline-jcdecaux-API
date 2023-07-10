import logging
import urllib.request
import time
from kafka import KafkaProducer


logging.basicConfig(filename="producer_kafka.log", level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

key = "c1d0cfc0377b8d04d9179d1c3f7a80e2491b30c3"
stations_url = f"https://api.jcdecaux.com/vls/v1/stations?&apiKey={key}" #all stations of all available cities
server = 'kafka'
client = "JCDecaux API"
topic = "velib_data"

logging.info(f"Data stream from {client} to Kafka topic {topic}", exc_info=True)


def send_api_data():
    try:
        producer = KafkaProducer(bootstrap_servers=[f'{server}:9092'], 
                                 client_id=client,
                                 acks=1)
        resp_stations = urllib.request.urlopen(stations_url)
        if resp_stations.getcode()==200:
            msg = resp_stations.read()
            producer.send(topic, msg)
            print("msg sent")
        else:
            stations_info = {"status_code":resp_stations.getcode(), 'headers':resp_stations.headers}
            logging.debug(stations_info, exc_info=True)

    except Exception as e:
        logging.error(e, exc_info=True)
        producer.close()

# while True:
#     send_msg()
#     time.sleep(2)
    