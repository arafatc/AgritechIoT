"""
/*
 * This  File is created by Arafat Chaghtai for the educational purposes.
 * The author could be contacted at: arafatc@gmail.com for any clarifications.
 *
 * Licensed under GNU General Public License v3.0
 *
 * This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS 
 * OF ANY KIND, either express or implied. See the License for the specific language
 * governing permissions and limitations under the License.
 */
 """
import logging
import boto3
from boto3.dynamodb.conditions import Key, Attr

# logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# This class contains the functions to retrieve/ store data in DynamoDB
# It is a wrapper class over AWS DynamoDB API's
# It is used to store / retrieve state values between Lambda invocations
class TransferDB:
    def __init__(self, table_name, gId):
        self._dynamodb = boto3.resource('dynamodb')
        self._table = self._dynamodb.Table(table_name)
        self._groupId = gId
        self._totalTemp = 0
        self._totalMoist = 0
        self._count = 0
        self._retrieve()

    def _retrieve(self):
        # Read latest value of sort key from dynamoDB
        try:
            response = self._table.query(
                KeyConditionExpression=Key('groupid').eq(self._groupId), ScanIndexForward=False, Limit=1
            )
        except Exception as e:
            logger.info(f'dynamodb._table.put_item exception is: {e}')
        else:
            if response['Count'] > 0:
                self._totalTemp = response['Items'][0]['totaltemp']
                self._totalMoist = response['Items'][0]['totalmoisture']
                self._count = response['Items'][0]['count']

    def store(self, tTemp, tMoisture, cnt):
        # Write to dynamoDB
        try:
            response = self._table.put_item(
                Item={'groupid': self._groupId, 'totaltemp': tTemp, 'totalmoisture': tMoisture, 'count': cnt}
            )
        except Exception as e:
            logger.info(f'dynamodb._table.put_item exception is: {e}')

    def delete(self):
        # Delete from dynamoDB
        try:
            response = self._table.scan(
                FilterExpression=Attr('groupid').eq(self._groupId)
            )
            if response['Count'] > 0:
                for i in range(response['Count']):
                    # pprint(response['Items'])
                    try:
                        resp = self._table.delete_item(
                            Key={
                                'groupid': self._groupId,
                                'count': response['Items'][i]['count']
                            }
                        )
                        i += 1
                    except Exception as e:
                        print(f'dynamodb exception is: {e}')
        except Exception as e:
            print(f'dynamodb exception is: {e}')

    def getCount(self):
        return self._count

    def getTotalTemp(self):
        return self._totalTemp

    def getTotalMoisture(self):
        return self._totalMoist
