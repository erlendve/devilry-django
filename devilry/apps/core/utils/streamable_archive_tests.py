#!/usr/bin/env python
"""
Tests the StreamableZip and StreamableTar implementations.
"""

from django.test import TestCase

from ...core.models import (Assignment, AssignmentGroup)
from ...core.utils.delivery_collection import create_archive_from_assignmentgroups
from ...core.utils.stream_archives import StreamableZip, StreamableTar, \
                                               UnsupportedOperation, FileStreamException

from django.utils import unittest

from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
import tarfile, copy

import sys
import os
import random

class TestStreamableArchive(TestCase):

    def __init__(self):
        self.testfile = "testfile.zip"
        self.file1_name = "TestFile1"
        self.file1_content = u"This is the content of testfile 1 ------------------"
        self.file2_name = "dir1/TestFile2"
        self.file2_content = u"This is the content of testfile 2 ++++++++++++++++++"
        self.file3_name = "dir1/dir2/TestFile3"
        self.file3_content = u"This is the content of testfile 3 ******************"
        
    def add_files_to_archive(self, archive):
        archive.add_file(self.file1_name, self.file1_content)
        archive.add_file(self.file2_name, self.file2_content)
        archive.add_file(self.file3_name, self.file3_content)
        
    def stream_file_to_archive(self, archive, filename, bytes):
        archive.open_filestream(filename, len(bytes))
        i = 0
        while i < len(bytes):
            chunk_size = random.randint(1, 5)
            if (i + chunk_size) > len(bytes):
                chunk_size = len(bytes) - i
            archive.append_file_chunk(bytes[i:i+chunk_size], chunk_size)
            i += chunk_size
        archive.close_filestream()
    
    def stream_files_to_archive(self, archive):
        self.stream_file_to_archive(archive, self.file1_name, self.file1_content)
        self.stream_file_to_archive(archive, self.file2_name, self.file2_content)
    
    def do_zip_filestream(self):
        self.stream_files_to_archive(StreamableZip())

    def tar_add_file_with_active_file_stream(self):
        """
        Open a StreamableTar, and add a file after opening a filestream. 
        This should produce a UnsupportedException.
        """
        arc = StreamableTar()
        arc.open_filestream("test", 5)
        arc.add_file("test", "testcontent")

    def tar_close_stream_with_no_active_stream(self):
        """
        Open a StreamableTar, and close a file stream without opening "\
        "a file stream first.
        This should produce a UnsupportedException.
        """
        arc = StreamableTar()
        arc.close_filestream()

    def tar_close_stream_without_appending_data(self):
        """
        Open a StreamableTar, and close a file stream without appending any data.
        This should produce a UnsupportedException.
        """
        arc = StreamableTar()
        arc.open_filestream("test", 5)
        arc.close_filestream()
        
    def test_tar_incorrect_filestream(self):
        """
        Test that attempting to open a filestream on a StreamableZip
        produces a UnsupportedOpertation exception.
        """
        self.assertRaises(FileStreamException, self.tar_add_file_with_active_file_stream)
        self.assertRaises(FileStreamException, self.tar_close_stream_with_no_active_stream) 
        self.assertRaises(FileStreamException, self.tar_close_stream_without_appending_data)
            
    def to_file(self, filename, bytes):
        f = open(filename, "w")
        f.write(bytes)
        f.close
    
    def test_tar_add_file(self):
        """
        Test adding files to a StreamableTar.
        """
        archive = StreamableTar()
        self.add_files_to_archive(archive)
        archive.close()
        self.to_file(self.testfile, archive.read())

        tfile = tarfile.open(name=self.testfile, mode="r")
        
        f = tfile.extractfile(tfile.getmember(self.file1_name))
        content = f.read()
        self.assertEquals(self.file1_content, content)

        f = tfile.extractfile(tfile.getmember(self.file2_name))
        content = f.read()
        self.assertEquals(self.file2_content, content)

        tfile.close()
        os.remove(self.testfile)
        
    def test_tar_filestream(self):
        """
        Test file stream functionality on a StreamableTar file.
        """
        archive = StreamableTar()
        self.stream_files_to_archive(archive)
        archive.close()
        self.to_file(self.testfile, archive.read())

        tfile = tarfile.open(name=self.testfile, mode="r")
        
        f = tfile.extractfile(tfile.getmember(self.file1_name))
        content = f.read()
        self.assertEquals(self.file1_content, content)

        f = tfile.extractfile(tfile.getmember(self.file2_name))
        content = f.read()
        self.assertEquals(self.file2_content, content)

        tfile.close()
        os.remove(self.testfile)
    
    def test_zip_filestream(self):
        """
        Test that attempting to open a filestream on a StreamableZip
        produces a UnsupportedOpertation exception.
        """
        self.assertRaises(UnsupportedOperation, self.do_zip_filestream) 

    def test_zip_archive(self):
        """
        Test adding files to a StreamableZip archive.
        """
        archive = StreamableZip()
        self.add_files_to_archive(archive)
        archive.close()
        self.to_file(self.testfile, archive.read())

        zfile = ZipFile(open(self.testfile, "r"), "r")
        content1 = zfile.read(self.file1_name)
        content2 = zfile.read(self.file2_name)
        content3 = zfile.read(self.file3_name)
        self.assertEquals(self.file1_content, content1)
        self.assertEquals(self.file2_content, content2)
        self.assertEquals(self.file3_content, content3)
        
        os.remove(self.testfile)

    
if __name__ == '__main__':

    tests = TestStreamableArchive()
    tests.test_zip_archive()
    tests.test_tar_add_file()
    tests.test_tar_filestream()
    tests.test_zip_filestream()
    tests.test_tar_incorrect_filestream()