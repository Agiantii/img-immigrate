# -*- coding: utf-8 -*-
import oss2
from itertools import islice
import logging
import time
import random
import json
from abc import ABC, abstractmethod
import os
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CloudManager(ABC):
    @abstractmethod
    def create_bucket(self):
        pass

    @abstractmethod
    def upload_file(self, object_name, data):
        pass

    @abstractmethod
    def download_file(self, object_name):
        pass

    @abstractmethod
    def list_objects(self):
        pass

    @abstractmethod
    def delete_objects(self):
        pass

    @abstractmethod
    def delete_bucket(self):
        pass

class OSSManager(CloudManager):
    def __init__(self, access_key_id=None, access_key_secret=None, endpoint=None, region=None, bucket_name=None, config_path=None):
        """
        @param access_key_id: str, Access Key ID 
        @param access_key_secret: str, Access Key Secret
        @param endpoint: str, OSS endpoint like 
          https://oss-cn-hangzhou.aliyuncs.com
        @param region: str, OSS region like 
            cn-hangzhou
        @param bucket_name: str, OSS bucket name like
            agiantii-oss-local
        @param config_path: str, path to the configuration file 
        """
        if config_path:
            if(os.path.exists(config_path) == False):
                raise Exception(f"Config file not found: {config_path}")
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.access_key_id = config['access_key_id']
                self.access_key_secret = config['access_key_secret']
                self.endpoint = config['endpoint']
                self.region = config['region']
                self.bucket_name = config['bucket_name']
        else:
            self.access_key_id = access_key_id
            self.access_key_secret = access_key_secret
            self.endpoint = endpoint
            self.region = region
            self.bucket_name = bucket_name

        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name, region=self.region)
    def get_bucket(self):
        return self.bucket
    def generate_unique_bucket_name(self):
        timestamp = int(time.time())
        random_number = random.randint(0, 9999)
        bucket_name = f"ablog-{timestamp}-{random_number}"
        return bucket_name

    def create_bucket(self,pubilc=True):
        """
        @param pubilc: bool, whether the bucket is public or not 
        """
        try:
            if(pubilc):
                self.bucket.create_bucket(oss2.models.BUCKET_ACL_PUBLIC_READ)
            else:
                self.bucket.create_bucket(oss2.models.BUCKET_ACL_PRIVATE)
            logging.info("Bucket created successfully")
        except oss2.exceptions.OssError as e:
            logging.error(f"Failed to create bucket: {e}")

    def upload_file(self, object_name, data):
        try:
            result = self.bucket.put_object(object_name, data)
            logging.info(f"File uploaded successfully, status code: {result.status}")
            return result
        except oss2.exceptions.OssError as e:
            logging.error(f"Failed to upload file: {e}")

    def download_file(self, object_name):
        try:
            file_obj = self.bucket.get_object(object_name)
            content = file_obj.read().decode('utf-8')
            logging.info("File content:")
            logging.info(content)
            return content
        except oss2.exceptions.OssError as e:
            logging.error(f"Failed to download file: {e}")

    def list_objects(self):
        try:
            objects = list(islice(oss2.ObjectIterator(self.bucket), 10))
            for obj in objects:
                logging.info(obj.key)
        except oss2.exceptions.OssError as e:
            logging.error(f"Failed to list objects: {e}")

    def delete_objects(self):
        try:
            objects = list(islice(oss2.ObjectIterator(self.bucket), 100))
            if objects:
                for obj in objects:
                    self.bucket.delete_object(obj.key)
                    logging.info(f"Deleted object: {obj.key}")
            else:
                logging.info("No objects to delete")
        except oss2.exceptions.OssError as e:
            logging.error(f"Failed to delete objects: {e}")

    def delete_bucket(self):
        try:
            self.bucket.delete_bucket()
            logging.info("Bucket deleted successfully")
        except oss2.exceptions.OssError as e:
            logging.error(f"Failed to delete bucket: {e}")

# 主流程
if __name__ == '__main__':
    config_path = r"E:\root\oss\oss-config.json"
    oss_manager = OSSManager(config_path=config_path)
    
    # 1. 创建Bucket
    oss_manager.create_bucket()
    # 2. 上传文件
    oss_manager.upload_file('test/test-string-file', b'Hello OSS, this is a test string.')
    # 3. 下载文件
    # oss_manager.download_file('test-string-file')
    # 4. 列出Bucket中的对象
    # oss_manager.list_objects()
    # 5. 删除Bucket中的对象
    # oss_manager.delete_objects()
    # 6. 删除Bucket
    # oss_manager.delete_bucket()