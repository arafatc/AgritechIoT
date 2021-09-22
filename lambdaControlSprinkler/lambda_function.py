"""
/*
 * This  File is created by Arafat Chaghtai for educational purposes.
 * The author could be contacted at: arafatc@gmail.com for any clarifications.
 *
 * Licensed under GNU General Public License v3.0
 *
 * This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS 
 * OF ANY KIND, either express or implied. See the License for the specific language
 * governing permissions and limitations under the License.
 */
 """
import os
from datetime import datetime, timedelta
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

queue = os.environ['QUEUE_NAME']
timeout = os.environ['VISIBILITY_TIMEOUT']


def get_queue_url():
    sqs_client = boto3.client("sqs")
    response = sqs_client.get_queue_url(
        QueueName=queue,
    )
    logger.info(f'From get_queue_url: {response}')
    return response["QueueUrl"]


def change_queue_attributes(sqs_client, delay_seconds, visibility_timeout):
    response = sqs_client.set_queue_attributes(
        QueueUrl=get_queue_url(),
        Attributes={
            "DelaySeconds": delay_seconds,
            "VisibilityTimeout": visibility_timeout,
        }
    )
    logger.info(f'From set_queue_attributes: {response}')


def process_message(sqs_client, message, visibility_timeout, delay_seconds='0', ):
    logger.info(f"processing message: {message}")
    msg = {}
    target_time = datetime.fromisoformat(message['Schedule'])
    stime = datetime.today()

    if (target_time - stime) <= timedelta(seconds=int(visibility_timeout)):
        msg = {"Timestamp": message['Schedule'], "UUID": message['UUID'],
               "SprinklerId": message['SprinklerId'], "State": message['State']}
        res = True
    else:
        change_queue_attributes(sqs_client, delay_seconds, visibility_timeout)
        res = False
    return res, msg


def delete_message(sqs_client, receipt_handle):
    response = sqs_client.delete_message(
        QueueUrl=get_queue_url(),
        ReceiptHandle=receipt_handle
    )
    logger.info(f'From delete_message: {response}')


def sendmessageIoT(iot_client, message):
    response = iot_client.publish(
        topic='iot/wateralarm',
        qos=1,
        payload=json.dumps(message))
    logger.info(f'From IoT publish: {response}')


def lambda_handler(event, context):
    #print(event)
    iot_client = boto3.client('iot-data')
    sqs_client = boto3.client('sqs')

    payload = json.loads(json.loads(event['Records'][0]['body']))
    #payload = event['Records'][0]['body']
    logger.info(f'payload: {payload}')
    #print(type(timeout))

    result, message = process_message(sqs_client, payload, timeout)
    if result is True:
        sendmessageIoT(iot_client, message)
        receipt_handle = event['Records'][0]['receiptHandle']
        delete_message(sqs_client, receipt_handle)
    else:
        raise Exception("timeout not reached")