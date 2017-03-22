"""
Unit tests for resdk/resources/relation.py file.
"""
# pylint: disable=missing-docstring, protected-access
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import MagicMock

from resdk.resources.collection import Collection
from resdk.resources.relation import Relation


class TestRelation(unittest.TestCase):

    def test_samples(self):
        relation = Relation(id=1, resolwe=MagicMock())

        relation.resolwe.sample.filter = MagicMock(return_value=['sample_1', 'sample_2'])
        relation.entities = [
            {'entity': 1, 'position': None},
            {'entity': 2, 'position': None},
        ]
        self.assertEqual(relation.samples, ['sample_1', 'sample_2'])
        relation.resolwe.sample.filter.assert_called_with(id__in='1,2')

        # test caching
        self.assertEqual(relation.samples, ['sample_1', 'sample_2'])
        self.assertEqual(relation.resolwe.sample.filter.call_count, 1)

        # cache is cleared at update
        relation._samples = ['sample']
        relation.update()
        self.assertEqual(relation._samples, None)

    def test_collection(self):
        relation = Relation(id=1, resolwe=MagicMock())
        collection = Collection(id=3, resolwe=MagicMock())
        collection.id = 3  # this is overriden when initialized

        # get collection
        relation.resolwe.collection.get = MagicMock(return_value='collection')
        relation._collection = 1
        self.assertEqual(relation.collection, 'collection')

        # set collection
        relation.collection = 2
        self.assertEqual(relation._collection, 2)
        relation.collection = collection
        self.assertEqual(relation._collection, 3)

    def test_repr(self):
        relation = Relation(id=1, resolwe=MagicMock())
        relation.id = 1  # this is overriden when initialized

        # `name` cannot be mocked in another way
        sample_1 = MagicMock()
        sample_1.configure_mock(name='sample_1')
        sample_2 = MagicMock()
        sample_2.configure_mock(name='sample_2')

        relation.type = 'compare'
        relation.label = None
        relation._samples = [sample_1, sample_2]
        relation.positions = None
        self.assertEqual(
            str(relation),
            "Relation <id:1 type: 'compare', samples: [sample_1, sample_2]>"
        )

        relation.type = 'compare'
        relation.label = 'background'
        relation._samples = [sample_1, sample_2]
        relation.positions = None
        self.assertEqual(
            str(relation),
            "Relation <id:1 type: 'compare', label: 'background', samples: [sample_1, sample_2]>"
        )

        relation.type = 'compare'
        relation.label = 'background'
        relation._samples = [sample_1, sample_2]
        relation.positions = ['sample', 'background']
        self.assertEqual(
            str(relation),
            "Relation <id:1 type: 'compare', label: 'background', "
            "samples: {sample: sample_1, background: sample_2}>"
        )


if __name__ == '__main__':
    unittest.main()