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
import boto3
import json
import logging
import os
from datetime import datetime
from decimal import Decimal

from LambdaDBStream.lib.data_model import DataModel
from LambdaDBStream.lib.transfer_db import TransferDB
from LambdaDBStream.lib.transfer_s3 import TransferS3
from LambdaDBStream.lib.weather_data import Weatherdata

# Openweather constants
lat = os.environ['LAT']
lon = os.environ['LON']
api_key = os.environ['API_KEY']
url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)

# S3 data
bucket_name = os.environ['BUCKET_NAME']
devicedata_file = os.environ['DEVICEDATA']
cropdata_file = os.environ['CROPDATA']
thresholdata_file = os.environ['THRESHOLDATA']

# SNS Topic
topic_arn = os.environ['TOPIC_ARN']
sns_client = boto3.client('sns')

# logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Threshold calculation
totalTemp = 0
totalMoisture = 0
count = 0
irrigationTime = 0
table = 'statedata'


def getDataModel(filename):
    s3_path = "config/" + filename
    get_s3 = TransferS3(bucket_name, s3_path)
    filedata = get_s3.getFileData()
    return filedata


def writeToS3(sprinkler_id, irrigation_time):
    # Get weather data for the location
    weather_data = Weatherdata(url)
    timestamp = datetime.today()
    local_data = '\n' + str(timestamp) + ',' + str(weather_data.getTemp()) + ',' \
                 + str(weather_data.getHumidity()) + ',' + str(irrigation_time)

    # Get s3 object for storing data
    s3_path = "Plot001/" + sprinkler_id + ".csv"
    write_s3 = TransferS3(bucket_name, s3_path)
    data = write_s3.getFileData()
    if not data:
        local_data = 'timestamp' + ',' + 'Temp' + ',' + 'Humidity' + ',' + \
                     'irrigationTime' + local_data
    else:
        local_data = data + local_data

    encoded_string = local_data.encode('utf-8')
    write_s3.putObject(encoded_string)
    return True


def lambda_handler(event, context):
    global totalTemp
    global totalMoisture
    global count
    global irrigationTime

    devicedata = getDataModel(devicedata_file)
    cropdata = getDataModel(cropdata_file)
    thresholdata = getDataModel(thresholdata_file)
    data_model = DataModel(devicedata, cropdata, thresholdata)

    for record in event['Records']:
        # Get Temp, Humidity and deviceid from IoT device
        deviceid = record['dynamodb']['Keys']['deviceid']['S']
        temperature = record['dynamodb']['NewImage']['Temperature']['N']
        moisture = record['dynamodb']['NewImage']['MoistureSensor']['N']

        groupId = data_model.getGroupId(deviceid)
        db_tran = TransferDB(table, groupId)

        # Count, TotalTemp and TotalHumidity are stored as state values in DynamoDB
        # This is to compensate for the 'stateless' behavior of lambda invocations
        count = db_tran.getCount()
        totalTemp = db_tran.getTotalTemp()
        totalMoisture = db_tran.getTotalMoisture()

        if count < 5:
            totalTemp = Decimal(totalTemp) + Decimal(temperature)
            totalMoisture = Decimal(totalMoisture) + Decimal(moisture)
            count = count + 1
            db_tran.store(totalTemp, totalMoisture, count)

        if count == 5:
            avgTemp = totalTemp / 5
            avgMoisture = totalMoisture / 5

            cropId = data_model.getCropId(groupId)
            idealtemp, idealmoist = data_model.getCropData(cropId)
            sprinklerId = data_model.getSprinklerId(groupId)

            if abs(avgTemp - idealtemp) <= 5 or abs(avgMoisture - idealmoist) <= 10:
                irrigationTime = data_model.getThreshold(cropId, diff=5)

            if abs(avgTemp - idealtemp) > 5 or abs(avgMoisture - idealmoist) > 10:
                irrigationTime = data_model.getThreshold(cropId, diff=10)

            payload = json.dumps({'default': json.dumps({"SprinklerId": sprinklerId,
                                                         "Duration": irrigationTime})})
            response = sns_client.publish(
                TopicArn=topic_arn,
                Message=payload,
                MessageStructure='json'
            )
            logger.info(f'response is: {response}')

            # Write data to s3 for analytics purpose
            writeToS3(sprinklerId, irrigationTime)

            # initialize Counter values to zero
            db_tran.delete()
