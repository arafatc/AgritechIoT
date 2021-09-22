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
import requests
import logging

# logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# This class contains the functions to retrieve weather data fro a lat/ long
# It is a wrapper class over OpenAPI 
class Weatherdata:
    def __init__(self, url):
        self._temp = 0
        self._humidity = 0
        self._getData(url)

    def _getData(self, url):
        response = requests.get(url)
        logger.info(f'OpenWeather response is: {response}')
        data = json.loads(response.text)
        self._temp = data["current"]["temp"]
        self._humidity = data["current"]["humidity"]

    def getTemp(self):
        return self._temp

    def getHumidity(self):
        return self._humidity
