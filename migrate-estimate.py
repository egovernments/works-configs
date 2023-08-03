from kafka import KafkaProducer
from json import dumps
from kafka.errors import KafkaError
import logging
from elasticsearch import Elasticsearch
import requests

es = Elasticsearch('http://localhost:9200')


expense_resp = es.search(index="estimate-inbox-v3" , body={"size": 10000})
ex_hits = expense_resp['hits']['hits']
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

estimateNumbers = []
for hit in ex_hits:
    estimateNumbers.append(hit['_source']['Data']['estimateNumber'])

print (estimateNumbers)

searchRequest = {
    "RequestInfo": {
        "apiId": "Rainmaker",
        "authToken": "e4a02753-68f9-402b-83aa-26f5f8859c2c",
        "msgId": "1690971020980|en_IN",
        "plainAccessRequest": {}
    }
}
#print (searchBillRequest)

insertRequest = {
    "RequestInfo": {
        "apiId": "Rainmaker",
        "authToken": "e4a02753-68f9-402b-83aa-26f5f8859c2c",
        "msgId": "1690971020980|en_IN",
        "plainAccessRequest": {}
    },
    "estimate": None,
    "workflow":  {
        "action": "",
        "assignees": [],
        "comment": ""
    }
}

for i in range(len(estimateNumbers)):
    uri = "https://works-qa.digit.org/estimate/v1/_search?tenantId=pg.citya&estimateNumber="+estimateNumbers[i]+"&_=1691032860673"
    resp = requests.post(uri, json = searchRequest, headers = {"Content-Type": "application/json"})
    Response = resp.json()
    print (Response)
    if len(Response['estimates']) > 0:
        insertRequest['estimate'] = Response['estimates'][0]
        future=producer.send('migrate-estimate',insertRequest)
        try:
            record_metadata = future.get(timeout=1)
        except KafkaError:
            # Decide what to do if produce request failed...
            logging.exception("message")
            pass

        # Successful result returns assigned partition and offset
        print (record_metadata.topic)
        print (record_metadata.partition)
        print (record_metadata.offset)

