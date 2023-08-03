from kafka import KafkaProducer
from json import dumps
from kafka.errors import KafkaError
import logging
from elasticsearch import Elasticsearch
import requests

es = Elasticsearch('http://localhost:9200')


expense_resp = es.search(index="expense-bill-index" , body={"size": 10000})
ex_hits = expense_resp['hits']['hits']
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

billNumbers = []
for hit in ex_hits:
    billNumbers.append(hit['_source']['Data']['billNumber'])

print (billNumbers)

searchBillRequest = {
    "billCriteria": {
        "tenantId": "pg.citya",
        "billNumbers": billNumbers,
        "businessService": "  "
    },
    "pagination": {
        "limit": 10,
        "offSet": 0,
        "sortBy": "",
        "order": "ASC"
    },
    "RequestInfo": {
        "apiId": "Rainmaker",
        "authToken": "e4a02753-68f9-402b-83aa-26f5f8859c2c",
        "msgId": "1690971020980|en_IN",
        "plainAccessRequest": {}
    }
}
#print (searchBillRequest)

resp = requests.post("https://works-qa.digit.org/expense/bill/v1/_search?_=1690971020980", json = searchBillRequest, headers = {"Content-Type": "application/json"})
billResponse = resp.json()
print (len(billResponse['bills']))

insertBillRequest = {
    "RequestInfo": {
        "apiId": "Rainmaker",
        "authToken": "e4a02753-68f9-402b-83aa-26f5f8859c2c",
        "msgId": "1690971020980|en_IN",
        "plainAccessRequest": {}
    },
    "bill": None,
    "workflow":  {
        "action": "",
        "assignees": [],
        "comment": ""
    }
}
for i in range(len(billResponse['bills'])):
    insertBillRequest['bill'] = billResponse['bills'][i]
    future=producer.send('migrate-expense-bill',insertBillRequest)
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
