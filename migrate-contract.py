from kafka import KafkaProducer
from json import dumps
from kafka.errors import KafkaError
import logging
from elasticsearch import Elasticsearch
import requests

es = Elasticsearch('http://localhost:9200')


expense_resp = es.search(index="contract-inbox" , body={"size": 10000})
ex_hits = expense_resp['hits']['hits']
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

contractNumbers = []
for hit in ex_hits:
    contractNumbers.append(hit['_source']['Data']['contractNumber'])

print (contractNumbers)

searchRequest = {
    "tenantId": "pg.citya",
    "contractNumber": "",
    "RequestInfo": {
        "apiId": "Rainmaker",
        "authToken": "e4a02753-68f9-402b-83aa-26f5f8859c2c",
        "userInfo": {
            "id": 261,
            "uuid": "1b348954-c257-4d18-afac-1b19fc3d86da",
            "userName": "EMP33",
            "name": "Jagankumar",
            "mobileNumber": "8877006677",
            "emailId": "abcd9890@dev.com",
            "locale": None,
            "type": "EMPLOYEE",
            "roles": [
                {
                    "name": "Employee",
                    "code": "EMPLOYEE",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "HRMS Admin",
                    "code": "HRMS_ADMIN",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "BILL_VERIFIER",
                    "code": "BILL_VERIFIER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "ESTIMATE VERIFIER",
                    "code": "ESTIMATE_VERIFIER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "WORK ORDER CREATOR",
                    "code": "WORK_ORDER_CREATOR",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "ESTIMATE APPROVER",
                    "code": "ESTIMATE_APPROVER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "WORK ORDER VERIFIER",
                    "code": "WORK_ORDER_VERIFIER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "PROJECT VIEWER",
                    "code": "PROJECT_VIEWER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "BILL_APPROVER",
                    "code": "BILL_APPROVER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "MUSTER ROLL VERIFIER",
                    "code": "MUSTER_ROLL_VERIFIER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "PROJECT CREATOR",
                    "code": "PROJECT_CREATOR",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "Employee Common",
                    "code": "EMPLOYEE_COMMON",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "BILL_VIEWER",
                    "code": "BILL_VIEWER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "TECHNICAL SANCTIONER",
                    "code": "TECHNICAL_SANCTIONER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "BILL_CREATOR",
                    "code": "BILL_CREATOR",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "MUSTER ROLL APPROVER",
                    "code": "MUSTER_ROLL_APPROVER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "WORK ORDER APPROVER",
                    "code": "WORK_ORDER_APPROVER",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "ESTIMATE CREATOR",
                    "code": "ESTIMATE_CREATOR",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "State Dashboard Admin",
                    "code": "STADMIN",
                    "tenantId": "pg.citya"
                },
                {
                    "name": "MUKTA Admin",
                    "code": "MUKTA_ADMIN",
                    "tenantId": "pg.citya"
                }
            ],
            "active": True,
            "tenantId": "pg.citya",
            "permanentCity": None
        },
        "msgId": "1691044911204|en_IN",
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
    "contract": None,
    "workflow":  {
        "action": "",
        "assignees": [],
        "comment": ""
    }
}

for i in range(len(contractNumbers)):
    uri = "https://works-qa.digit.org/contract/v1/_search?tenantId=pg.citya&_=1691044911204"
    searchRequest['contractNumber']=contractNumbers[i]
    resp = requests.post(uri, json = searchRequest, headers = {"Content-Type": "application/json"})
    Response = resp.json()
    #print (Response)
    if len(Response['contracts']) > 0:
        insertRequest['contract'] = Response['contracts'][0]
        print ("insertRequest ",insertRequest)
        future=producer.send('migrate-contract',insertRequest)
        try:
            record_metadata = future.get(timeout=2)
        except KafkaError:
            # Decide what to do if produce request failed...
            logging.exception("message")
            pass

        # Successful result returns assigned partition and offset
        print (record_metadata.topic)
        print (record_metadata.partition)
        print (record_metadata.offset)
