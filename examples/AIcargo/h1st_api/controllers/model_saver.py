from urllib.parse import urlparse

import os
import boto3

import logging
logger = logging.getLogger(__name__)


class ModelSaver():
    def get_saver(file_system='local'):
        return {'local': LocalModelSaver(), 's3': S3ModelSaver()}[file_system]
    
    def save(self, local_directory, destination):
        raise NotImplementedError('Please inherit and implement this method')


class LocalModelSaver(ModelSaver):
    def exists(self, path):
        return os.path.exists(path)
    def save(self, local_directory, destination):
        raise NotImplementedError('Not supported yet!!!')

class S3ModelSaver(ModelSaver):
    def __init__(self):
        self.client = boto3.client('s3')

    def exists(self, path):
        o = urlparse(path)
        bucket, key = o.netloc, o.path[1:]
        logger.info(bucket, key)
        ret = self.client.list_objects(Bucket=bucket, Prefix=key)
        return 'Contents' in ret

    def save(self, local_directory, destination, overwrite=True):
        logger.info('Copy model content from {} to {}'.format(local_directory, destination))
        if not os.path.isdir(local_directory):
            raise RuntimeError('{} is not a directory'.format(local_directory))

        o = urlparse(destination)
        bucket, path = o.netloc, o.path[1:]
        
        if self.exists(destination):
            logger.debug("Target existed. %s..." % destination)
            if overwrite:
                logger.debug("Overwrite is True. Deleting %s..." % destination)
                try:
                    self.client.delete_object(Bucket=bucket, Key=path)
                except:
                    logger.debug("Unable to delete %s..." % destination)
                    return {'success': False, 'message': 'Fail to save model'}
            else:
                logger.debug('Overwrite is False. Do nothing!!!')
                return {'success': True, 'message': 'Destination existed!!!'}
        
        # enumerate local files recursively
        for root, dirs, files in os.walk(local_directory):
            for filename in files:
                # construct the full local path
                local_path = os.path.join(root, filename)
                logger.debug('local path: {}'.format(local_path))

                relative_path = os.path.relpath(local_path, local_directory)
                logger.debug('relative path: {}'.format(relative_path))
                s3_path = os.path.join(path, relative_path)

                try:
                    logger.debug("Uploading %s..." % s3_path)
                    self.client.upload_file(local_path, bucket, s3_path)
                except:
                    return {'success': False, 'message': 'Fail to save model'}

        return {'success': True, 'message': ''}
