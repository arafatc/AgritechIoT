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
import uuid
from datetime import datetime, timedelta
import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
queue = os.environ['QUEUE_NAME']


def create_queue(sqs_client):
    response = sqs_client.create_queue(
        QueueName=queue,
        Attributes={
            "DelaySeconds": "0",
            "VisibilityTimeout": "30",  #default
        }
    )
    logger.info(f'From create_queue: {response}')


def get_queue_url():
    sqs_client = boto3.client("sqs")
    response = sqs_client.get_queue_url(
        QueueName=queue,
    )
    logger.info(f'From get_queue_url: {response}')
    return response["QueueUrl"]


def send_message(sqs_client, message):
    # message = {"key": "value"}

    response = sqs_client.send_message(
        QueueUrl=get_queue_url(),
        MessageBody=json.dumps(message)
    )
    logger.info(f'From send_message: {response}')


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info(f'From SNS: {message}')

    sprinklerId = message['SprinklerId']
    irrigation_delay = message['Duration']

    sqs_client = boto3.client("sqs")
    create_queue(sqs_client)

    stime = datetime.today()
    etime = stime + timedelta(seconds=irrigation_delay)
    msgid = str(uuid.uuid4())

    message1 = json.dumps({"UUID": msgid, "SprinklerId": sprinklerId, "State": "ON", "Schedule": stime.isoformat()})
    message2 = json.dumps({"UUID": msgid, "SprinklerId": sprinklerId, "State": "OFF", "Schedule": etime.isoformat()})
    logger.info(f'message1: {message1}')
    logger.info(f'message2: {message2}')

    send_message(sqs_client, message1)
    send_message(sqs_client, message2)
