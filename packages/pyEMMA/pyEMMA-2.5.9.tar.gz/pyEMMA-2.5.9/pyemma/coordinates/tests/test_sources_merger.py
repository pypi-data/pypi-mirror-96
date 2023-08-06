import unittest
import pkg_resources
import os
from glob import glob
import numpy as np

from pyemma.coordinates import source, tica
from pyemma.coordinates.data.sources_merger import SourcesMerger


class TestSourcesMerger(unittest.TestCase):

    def setUp(self):
        self.readers = []
        data_dir = pkg_resources.resource_filename('pyemma.coordinates.tests', 'data')
        # three md trajs
        trajs = glob(data_dir + "/bpti_0*.xtc")
        top = os.path.join(data_dir, 'bpti_ca.pdb')
        self.readers.append(source(trajs, top=top))
        self.readers[0].featurizer.add_all()
        ndim = self.readers[0].ndim
        # three random arrays
        lengths = self.readers[0].trajectory_lengths()
        arrays = [np.random.random( (length, ndim) ) for length in lengths]
        self.readers.append(source(arrays))

        self.readers.append(tica(self.readers[-1], dim=20))

    def _get_output_compare(self, joiner, stride=1, chunk=0, skip=0):
        out = joiner.get_output(stride=stride, chunk=chunk, skip=skip)
        assert len(out) == 3  # 3 trajs
        assert joiner.ndim == sum(r.dimension() for r in self.readers)
        np.testing.assert_equal(joiner.trajectory_lengths(), self.readers[0].trajectory_lengths())

        from collections import defaultdict
        outs = defaultdict(list)
        for r in self.readers:
            for i, x in enumerate(r.get_output(stride=stride, chunk=chunk, skip=skip)):
                outs[i].append(x)
        combined = [np.hstack(outs[i]).astype(np.float32) for i in range(3)]
        np.testing.assert_equal([o.astype(np.float32) for o in out], combined)

    def test_combined_output(self):
        j = SourcesMerger(self.readers)
        self._get_output_compare(j, stride=1, chunk=0, skip=0)
        self._get_output_compare(j, stride=2, chunk=1, skip=0)
        self._get_output_compare(j, stride=3, chunk=2, skip=7)
        self._get_output_compare(j, stride=5, chunk=9, skip=3)

    def test_ra_stride(self):
        ra_indices = np.array([[0,7], [0, 23], [1, 30], [2, 9]])
        j = SourcesMerger(self.readers)
        self._get_output_compare(j, stride=ra_indices)

    def test_non_matching_lengths(self):
        data = self.readers[1].data
        data = [data[0], data[1], data[2][:20]]
        self.readers.append(source(data))
        with self.assertRaises(ValueError) as ctx:
            SourcesMerger(self.readers)
        self.assertIn('matching', ctx.exception.args[0])

    def test_fragmented_trajs(self):
        """ build two fragmented readers consisting out of two fragments each and check if they are merged properly."""
        segment_0 = np.arange(20)
        segment_1 = np.arange(20, 40)

        s1 = source([(segment_0, segment_1)])
        s2 = source([(segment_0, segment_1)])

        sm = SourcesMerger((s1, s2))

        out = sm.get_output()
        x = np.atleast_2d(np.arange(40))
        expected = [np.concatenate((x, x), axis=0).T]

        np.testing.assert_equal(out, expected)
