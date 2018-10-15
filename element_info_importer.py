import csv
import json

import boto3

with open('elements_list.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Elements')
        table.put_item(
            Item={
                "num": row[0],
                "name": row[1],
                "yomi": row[2],
                "symbol": row[3]
            }
        )
