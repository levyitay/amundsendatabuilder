import json
import shutil
import tempfile
import unittest

from pyhocon import ConfigFactory  # noqa: F401
from typing import Any, List  # noqa: F401

from databuilder import Scoped
from databuilder.loader.file_system_elasticsearch_json_loader import FSElasticsearchJSONLoader
from databuilder.models.table_elasticsearch_document import TableESDocument


class TestFSElasticsearchJSONLoader(unittest.TestCase):

    def setUp(self):
        # type: () -> None
        self.temp_dir_path = tempfile.mkdtemp()
        self.dest_file_name = '{}/test_file.json'.format(self.temp_dir_path)
        self.file_mode = 'w'
        config_dict = {'loader.filesystem.elasticsearch.file_path': self.dest_file_name,
                       'loader.filesystem.elasticsearch.mode': self.file_mode}
        self.conf = ConfigFactory.from_dict(config_dict)

    def tearDown(self):
        # type: () -> None
        shutil.rmtree(self.temp_dir_path)

    def _check_results_helper(self, expected):
        # type: (List[str]) -> None
        """
        Helper function to compare results with expected outcome
        :param expected: expected result
        """
        with open(self.dest_file_name, 'r') as file:
            for e in expected:
                actual = file.readline().rstrip('\r\n')
                self.assertDictEqual(json.loads(e), json.loads(actual))
            self.assertFalse(file.readline())

    def test_empty_loading(self):
        # type: () -> None
        """
        Test loading functionality with no data
        """
        loader = FSElasticsearchJSONLoader()
        loader.init(conf=Scoped.get_scoped_conf(conf=self.conf,
                                                scope=loader.get_scope()))

        loader.load(None)  # type: ignore
        loader.close()

        self._check_results_helper(expected=[])

    def test_loading_with_different_object(self):
        # type: () -> None
        """
        Test Loading functionality with a python Dict object
        """
        loader = FSElasticsearchJSONLoader()
        loader.init(conf=Scoped.get_scoped_conf(conf=self.conf,
                                                scope=loader.get_scope()))

        data = dict(database='test_database',
                    cluster='test_cluster',
                    schema_name='test_schema',
                    name='test_table',
                    key='test_table_key',
                    last_updated_epoch=123456789,
                    description='test_description',
                    column_names=['test_col1', 'test_col2'],
                    column_descriptions=['test_comment1', 'test_comment2'],
                    total_usage=10,
                    unique_usage=5,
                    tags=['test_tag1', 'test_tag2'])

        with self.assertRaises(Exception) as context:
            loader.load(data)  # type: ignore
        self.assertTrue("Record not of type 'ElasticsearchDocument'!" in context.exception)

        loader.close()

    def test_loading_with_single_object(self):
        # type: () -> None
        """
        Test Loading functionality with single python object
        """
        loader = FSElasticsearchJSONLoader()
        loader.init(conf=Scoped.get_scoped_conf(conf=self.conf,
                                                scope=loader.get_scope()))

        data = TableESDocument(database='test_database',
                               cluster='test_cluster',
                               schema_name='test_schema',
                               name='test_table',
                               key='test_table_key',
                               last_updated_epoch=123456789,
                               description='test_description',
                               column_names=['test_col1', 'test_col2'],
                               column_descriptions=['test_comment1', 'test_comment2'],
                               total_usage=10,
                               unique_usage=5,
                               tags=['test_tag1', 'test_tag2'])
        loader.load(data)
        loader.close()

        expected = [
            ('{"key": "test_table_key", "column_descriptions": ["test_comment1", "test_comment2"], '
             '"schema_name": "test_schema", "database": "test_database", "cluster": "test_cluster", '
             '"column_names": ["test_col1", "test_col2"], "name": "test_table", '
             '"last_updated_epoch": 123456789,'
             '"description": "test_description", "unique_usage": 5, "total_usage": 10, '
             '"tags": ["test_tag1", "test_tag2"]}')
        ]

        self._check_results_helper(expected=expected)

    def test_loading_with_list_of_objects(self):
        # type: () -> None
        """
        Test Loading functionality with list of objects.
        Check to ensure all objects are added to file
        """
        loader = FSElasticsearchJSONLoader()
        loader.init(conf=Scoped.get_scoped_conf(conf=self.conf,
                                                scope=loader.get_scope()))

        data = [TableESDocument(database='test_database',
                                cluster='test_cluster',
                                schema_name='test_schema',
                                name='test_table',
                                key='test_table_key',
                                last_updated_epoch=123456789,
                                description='test_description',
                                column_names=['test_col1', 'test_col2'],
                                column_descriptions=['test_comment1', 'test_comment2'],
                                total_usage=10,
                                unique_usage=5,
                                tags=['test_tag1', 'test_tag2'])] * 5

        for d in data:
            loader.load(d)
        loader.close()

        expected = [
            ('{"key": "test_table_key", "column_descriptions": ["test_comment1", "test_comment2"], '
             '"schema_name": "test_schema", "database": "test_database", "cluster": "test_cluster", '
             '"column_names": ["test_col1", "test_col2"], "name": "test_table", '
             '"last_updated_epoch": 123456789,'
             '"description": "test_description", "unique_usage": 5, "total_usage": 10, '
             '"tags": ["test_tag1", "test_tag2"]}')
        ] * 5

        self._check_results_helper(expected=expected)
