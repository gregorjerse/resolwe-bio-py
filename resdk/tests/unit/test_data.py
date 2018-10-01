"""
Unit tests for resdk/resources/data.py file.
"""
# pylint: disable=missing-docstring, protected-access
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import six
from mock import MagicMock, patch

from resdk.resources.collection import Collection
from resdk.resources.data import Data
from resdk.resources.descriptor import DescriptorSchema
from resdk.resources.sample import Sample


class TestData(unittest.TestCase):

    @patch('resdk.resources.data.Data', spec=True, annotation={})
    def test_update_fields(self, data_mock):
        payload = {
            'id': 42,
            'slug': 'foo',
            'process_input_schema': [
                {
                    'name': "x",
                    'type': "basic:integer:",
                    'label': "Input X",
                },
                {
                    'name': "group_input",
                    'group': [
                        {
                            'name': "y1",
                            'type': "basic:string:",
                            'label': "Input Y1",
                        },
                    ],
                }
            ],
            'input': {
                'x': 123,
                'group_input': {
                    'y1': 'bar',
                },
            },
        }
        Data._update_fields(data_mock, payload)
        expected = {
            'input.x': {
                'name': 'x',
                'type': 'basic:integer:',
                'label': 'Input X',
                'value': 123
            },
            'input.group_input.y1': {
                'name': 'y1',
                'type': 'basic:string:',
                'label': 'Input Y1',
                'value': 'bar'
            }
        }
        self.assertEqual(data_mock.annotation, expected)

    def test_no_sample(self):
        data = Data(id=1, resolwe=MagicMock())

        # Data object does not belong to any sample:
        data.api(data.id).get = MagicMock(return_value={'entities': []})
        self.assertEqual(data.sample, None)

    def test_sample(self):
        data = Data(id=1, resolwe=MagicMock())

        data.api(data.id).get = MagicMock(return_value={'entities': [5]})
        data.resolwe.sample.get = MagicMock(
            return_value=Sample(data.resolwe, **{'id': 5, 'name': 'XYZ'}))
        self.assertEqual(data.sample.id, 5)
        self.assertEqual(data.sample.name, 'XYZ')
        # test caching
        self.assertEqual(data.sample.id, 5)
        self.assertEqual(data.resolwe.sample.get.call_count, 1)

        # cache is cleared at update
        data.update()
        self.assertEqual(data._sample, None)

        # raising error if data object is not saved
        data.id = None
        with self.assertRaises(ValueError):
            _ = data.sample

    def test_collections(self):
        data = Data(id=1, resolwe=MagicMock())

        # test getting collections attribute
        data.api(data.id).get = MagicMock(return_value={'collections': [5]})
        data.resolwe.collection.filter = MagicMock(return_value=[
            Collection(data.resolwe, **{'id': 5, 'name': 'XYZ'})
        ])

        self.assertEqual(len(data.collections), 1)
        self.assertEqual(data.collections[0].id, 5)
        self.assertEqual(data.collections[0].name, 'XYZ')

        # test caching collections attribute
        self.assertEqual(len(data.collections), 1)
        self.assertEqual(data.resolwe.collection.filter.call_count, 1)

        # cache is cleared at update
        data.update()
        self.assertEqual(data._collections, None)

        # raising error if data object is not saved
        data.id = None
        with self.assertRaises(ValueError):
            _ = data.collections

    def test_descriptor_schema(self):
        data = Data(id=1, resolwe=MagicMock())
        data._descriptor_schema = 1

        # test getting descriptor schema attribute
        data.resolwe.descriptor_schema.get = MagicMock(return_value='descriptor_schema')
        self.assertEqual(data.descriptor_schema, 'descriptor_schema')
        _, get_kwargs = data.resolwe.descriptor_schema.get.call_args
        self.assertEqual(get_kwargs['id'], 1)

        # descriptor schema is not set
        data._descriptor_schema = None
        self.assertEqual(data.descriptor_schema, None)

        # cache is cleared at update
        data._hydrated_descriptor_schema = 'descriptor_schema'
        data.update()
        self.assertEqual(data._hydrated_descriptor_schema, None)

        # new data object
        data = Data(resolwe=MagicMock())

        data.descriptor_schema = 'my-schema'
        self.assertEqual(data._descriptor_schema, 'my-schema')

        data.resolwe.descriptor_schema.get = MagicMock(return_value='descriptor_schema')
        self.assertEqual(data.descriptor_schema, 'descriptor_schema')
        _, get_kwargs = data.resolwe.descriptor_schema.get.call_args
        self.assertEqual(get_kwargs['slug'], 'my-schema')

        # hidrated descriptor schema
        descriptor_schema = {
            "slug": "test-schema",
            "name": "Test schema",
            "version": "1.0.0",
            "schema": [
                {
                    "default": "56G",
                    "type": "basic:string:",
                    "name": "description",
                    "label": "Object description"
                }
            ],
            "id": 1,
        }
        data = Data(id=1, descriptor_schema=descriptor_schema, resolwe=MagicMock())
        self.assertTrue(isinstance(data.descriptor_schema, DescriptorSchema))
        # pylint: disable=no-member
        self.assertEqual(data.descriptor_schema.slug, 'test-schema')
        # pylint: enable=no-member

    def test_parents(self):
        # Data with no id should fail.
        data = Data(id=None, resolwe=MagicMock())
        with six.assertRaisesRegex(self, ValueError, 'Instance must be saved *'):
            data.parents  # pylint: disable=pointless-statement

        # Core functionality should be checked with e2e tests.

        # Check that cache is cleared at update.
        data = Data(id=42, resolwe=MagicMock())
        data._parents = 'foo'
        data.update()
        self.assertEqual(data._parents, None)

    def test_children(self):
        # Data with no id should fail.
        data = Data(id=None, resolwe=MagicMock())
        with six.assertRaisesRegex(self, ValueError, 'Instance must be saved *'):
            data.children  # pylint: disable=pointless-statement

        # Core functionality should be checked with e2e tests.

        # Check that cache is cleared at update.
        data = Data(id=42, resolwe=MagicMock())
        data._children = 'foo'
        data.update()
        self.assertEqual(data._children, None)

    def test_files(self):
        data = Data(id=123, resolwe=MagicMock())
        data._get_dir_files = MagicMock(
            side_effect=[['first_dir/file1.txt'], ['fastq_dir/file2.txt']])

        data.annotation = {
            'output.list': {'value': [{'file': "element.gz"}], 'type': 'list:basic:file:'},
            'output.dir_list': {'value': [{'dir': "first_dir"}], 'type': 'list:basic:dir:'},
            'output.fastq': {'value': {'file': "file.fastq.gz"}, 'type': 'basic:file:fastq'},
            'output.fastq_archive': {'value': {'file': "archive.gz"}, 'type': 'basic:file:'},
            'output.fastq_dir': {'value': {'dir': "fastq_dir"}, 'type': 'basic:dir:'},
            'input.fastq_url': {'value': {'file': "blah"}, 'type': 'basic:url:'},
            'input.blah': {'value': "blah.gz", 'type': 'basic:file:'}
        }

        file_list = data.files()
        six.assertCountEqual(self, file_list, [
            'element.gz',
            'archive.gz',
            'file.fastq.gz',
            'first_dir/file1.txt',
            'fastq_dir/file2.txt'
        ])
        file_list = data.files(file_name='element.gz')
        self.assertEqual(file_list, ['element.gz'])
        file_list = data.files(field_name='output.fastq')
        self.assertEqual(file_list, ['file.fastq.gz'])

        data.annotation = {
            'output.list': {'value': [{'no_file_field_here': "element.gz"}],
                            'type': 'list:basic:file:'},
        }
        with six.assertRaisesRegex(self, KeyError, "does not contain 'file' key."):
            data.files()

        data = Data(resolwe=MagicMock(), id=None)
        with six.assertRaisesRegex(self, ValueError, "must be saved before"):
            data.files()

    @patch('resdk.resources.data.requests')
    def test_dir_files(self, requests_mock):
        data = Data(id=123, resolwe=MagicMock(url='http://resolwe.url'))
        requests_mock.get = MagicMock(side_effect=[
            MagicMock(content=b'[{"type": "file", "name": "file1.txt"}, '
                              b'{"type": "directory", "name": "subdir"}]'),
            MagicMock(content=b'[{"type": "file", "name": "file2.txt"}]'),
        ])

        files = data._get_dir_files('test_dir')

        self.assertEqual(files, ['test_dir/file1.txt', 'test_dir/subdir/file2.txt'])

    @patch('resdk.resources.data.Data', spec=True)
    def test_download_fail(self, data_mock):
        message = "Only one of file_name or field_name may be given."
        with six.assertRaisesRegex(self, ValueError, message):
            Data.download(data_mock, file_name="a", field_name="b")

    @patch('resdk.resources.data.Data', spec=True)
    def test_download_ok(self, data_mock):
        data_mock.configure_mock(id=123, **{'resolwe': MagicMock()})
        data_mock.configure_mock(**{
            'files.return_value': ['file1.txt', 'file2.fq.gz'],
        })

        Data.download(data_mock)
        data_mock.resolwe._download_files.assert_called_once_with(
            ['123/file1.txt', '123/file2.fq.gz'], None)

        data_mock.reset_mock()
        Data.download(data_mock, download_dir="/some/path/")
        data_mock.resolwe._download_files.assert_called_once_with(
            ['123/file1.txt', '123/file2.fq.gz'], '/some/path/')

    @patch('resdk.resources.data.Data', spec=True)
    def test_add_output(self, data_mock):
        data_mock.configure_mock(
            annotation={'output.fastq': {'type': 'basic:file:', 'value': {'file': 'reads.fq'}},
                        'output.fasta': {'type': 'basic:file:', 'value': {'file': 'genome.fa'}}}
        )

        files_list = Data._files_dirs(data_mock, 'file', field_name="output.fastq")
        self.assertEqual(files_list, ['reads.fq'])

        files_list = Data._files_dirs(data_mock, 'file', field_name="fastq")
        self.assertEqual(files_list, ['reads.fq'])

    @patch('resdk.resources.data.requests')
    @patch('resdk.resources.data.urljoin')
    @patch('resdk.resources.data.Data', spec=True)
    def test_stdout_ok(self, data_mock, urljoin_mock, requests_mock):
        # Configure mocks:
        data_mock.configure_mock(id=123, resolwe=MagicMock(url="a", auth="b"))
        urljoin_mock.return_value = "some_url"

        # If response.ok = True:
        response = MagicMock(ok=True, **{'iter_content.return_value': [b"abc", b"def"]})
        requests_mock.configure_mock(**{'get.return_value': response})

        out = Data.stdout(data_mock)

        self.assertEqual(out, "abcdef")
        urljoin_mock.assert_called_once_with("a", 'data/123/stdout.txt')
        requests_mock.get.assert_called_once_with("some_url", stream=True, auth="b")

        # If response.ok = False:
        response = MagicMock(ok=False)
        requests_mock.configure_mock(**{'get.return_value': response})

        out = Data.stdout(data_mock)

        self.assertEqual(response.raise_for_status.call_count, 1)


if __name__ == '__main__':
    unittest.main()
