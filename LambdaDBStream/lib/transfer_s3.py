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

# logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# This class contains the functions to retrieve/ store data in S3
# It is a wrapper class over AWS S3 API's
class TransferS3:
    def __init__(self, bucket, path):
        self._connect()
        self._bucket_name = bucket
        # self._file_name = file
        self._s3_path = path
        self._data = ''

    def _connect(self):
        self._s3 = boto3.client('s3')

    def _getObject(self):
        try:
            resp = self._s3.get_object(Bucket=self._bucket_name, Key=self._s3_path)
            logger.info(f's3.get_object is: {resp}')
        except Exception as e:
            logger.info(f'Error reading key {self._s3_path} from bucket {self._bucket_name}: {e}')
        else:
            self._data = resp.get('Body').read().decode('utf-8')

    def getFileData(self):
        self._getObject()
        return self._data

    def putObject(self, enc_str):
        resp = self._s3.put_object(Bucket=self._bucket_name, Key=self._s3_path, Body=enc_str)
        logger.info(f's3.put_object is: {resp}')
