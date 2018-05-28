#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Description:  Unit tests for the modular benchmark (Python Clustering Algorithms BenchMarking Framework).

:Authors: (c) Artem Lutov <artem@exascale.info>
:Organizations: eXascale Infolab <http://exascale.info/>, Lumais <http://www.lumais.com/>
:Date: 2018-06
"""

from __future__ import print_function, division  # Required for stderr output, must be the first import
import unittest
import os
import glob
import tempfile
import shutil
import tarfile
from benchutils import SyncValue, nameVersion, tobackup, _ORIGDIR
from benchapps import preparePath


class TestUtils(unittest.TestCase):
	"""Tests for the Benchmark utilities"""
	# __bdir = None  # Base directory for the tests


	# @classmethod
	# def setUpClass(cls):
	# 	cls.__bdir = tempfile.mkdtemp(prefix='tmp_bmtests')


	# @classmethod
	# def tearDownClass(cls):
	# 	if cls.__bdir is not None:
	# 		shutil.rmtree(cls.__bdir)


	def test_nameVersion(self):
		"""nameVersion() tests"""
		# Test for the non-existent name
		randname = 's;35>.ds8u9'
		stval0 = None
		synctime = SyncValue(stval0)
		suffix = 'suf'  # Versioning suffix
		self.assertFalse(os.path.exists(randname))
		self.assertEqual(nameVersion(randname, False), randname)
		self.assertEqual(nameVersion(randname, False, suffix='suf'), '_'.join((randname, suffix)))
		# Consider path expansion with for the non-existent path
		self.assertRaises(StopIteration, next, glob.iglob(randname + '*'))
		self.assertEqual(nameVersion(randname, True), randname)
		# Check with Synctime
		self.assertEqual(nameVersion(randname, True, synctime), randname)
		self.assertEqual(synctime.value, stval0
			, 'synctime.value should not be changed for the non-existent path')
		# Check path expansion to the existent path
		path = next(glob.iglob('*'))
		self.assertNotEqual(nameVersion(path, True), path
			, 'Unexistent versioned name is expected for the existent path')
		# Check with Synctime
		# None value
		self.assertNotEqual(nameVersion(path, True, synctime), path)
		self.assertNotEqual(synctime.value, stval0
			, 'synctime.value should be initialized for the existent path')
		self.assertIn('_' + suffix, nameVersion(path, True, synctime, suffix=suffix))
		# Non None value
		stval = synctime.value  # Non None stval should be permanent
		self.assertNotEqual(nameVersion(path, True, synctime), path)
		self.assertEqual(synctime.value, stval, 'synctime.value should be permanent')


	# $ python -m unittest benchtests.TestUtils.test_tobackup
	def test_tobackup(self):
		"""tobackup() tests"""
		# Create tmp dir to test backuping
		bdir = tempfile.mkdtemp(prefix='tmp_bmtests')
		try:
			clspref = 'cls1'  # Prefix of the items being backed up
			bcksuf = 'k123'  # Backup name suffix
			clsdir = tempfile.mkdtemp(prefix=clspref, dir=bdir)
			clsf1 = tempfile.mkstemp(suffix='.cls', prefix=clspref, dir=clsdir, text=True)
			os.write(clsf1[0], 'Some content\n')
			os.close(clsf1[0])
			clslog = tempfile.mkstemp(suffix='.log', prefix=clspref, dir=bdir)
			bckarch = tobackup(clsdir, expand=False, xsuffix=bcksuf, move=False)
			# print('bckarch: ' + bckarch)
			self.assertTrue(bckarch.startswith(bdir) and os.path.exists(bckarch)
				, 'The backup archive should exist')
			self.assertTrue(os.path.exists(clsdir) and os.path.exists(clslog[1]))

			# Move paths to the origdir and create symlinks instead of the former paths
			origdir = '/'.join((bdir, _ORIGDIR))
			os.mkdir(origdir)
			for p in glob.iglob(''.join((bdir, '/', clspref, '*'))):
				shutil.move(p, origdir)
				newpath = origdir + os.path.split(p)[1]
				newpath = os.path.relpath(newpath, bdir)
				os.symlink(newpath, os.path.split(newpath)[1])
			# Back up target symlinks with their origins
			bckarch = tobackup(bdir + '/' + clspref, expand=True, xsuffix=bcksuf, move=True)
			self.assertIn('_' + bcksuf, bckarch)
			self.assertTrue(bckarch.startswith(bdir) and os.path.exists(bckarch)
				, 'The backup archive should exist')
			self.assertFalse(os.path.exists(clsdir) or os.path.exists(clslog[1]))
			baf = tarfile.open(bckarch, 'r')
			self.assertNotEqual(len(filter(lambda name: _ORIGDIR in name, baf.getnames())), 0)

			# Test back up with symlinks
		finally:
			shutil.rmtree(bdir)




if __name__ == '__main__':
	unittest.main()
	# if unittest.main().result:  # verbosity=2
	# 	print('Try to re-execute the tests (hot run) or set x2-3 larger TEST_LATENCY')
