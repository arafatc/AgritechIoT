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
import json


# This class contains functions to load the data model from json files in S3
# It is intended to simulate a configuration database for devices, crops, users and threshold data
class DataModel:
    def __init__(self, deviceData, cropData, thresholdData):
        self._deviceData = json.loads(deviceData)
        self._cropData = json.loads(cropData)
        self._thresholdData = json.loads(thresholdData)

    def getSprinklerId(self, groupId):
        for device in self._deviceData['devicedata']:
            if device['groupId'] == groupId:
                if device['deviceType'] == 'water_sprinkler':
                    return device['deviceId']
        return False

    def getGroupId(self, deviceId):
        for device in self._deviceData['devicedata']:
            if device['deviceId'] == deviceId:
                return device['groupId']
        return False

    def getCropId(self, groupId):
        for device in self._deviceData['devicedata']:
            if device['groupId'] == groupId:
                return device['cropId']
        return False

    def getCropData(self, cropId):
        for crop in self._cropData['cropdata']:
            if crop['cropId'] == cropId:
                return crop['temp'], crop['moisture']
        return False, False

    def getThreshold(self, cropId, diff):
        for crop in self._thresholdData['thresholdata']:
            if crop['cropId'] == cropId:
                for cdata in crop['threshold']:
                    if cdata['diff'] == diff:
                        return cdata['irrigationTime']
        return False
