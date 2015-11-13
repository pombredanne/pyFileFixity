from __future__ import print_function

import itertools
import hashlib

import sys

import shutil

from pyFileFixity import structural_adaptive_ecc as saecc
from .aux_tests import check_eq_files, check_eq_dir, path_input, path_results, path_output, tamper_file, find_next_entry, create_dir_if_not_exist

def setup_module():
    """ Initialize the tests by emptying the out directory """
    outfolder = path_output()
    shutil.rmtree(outfolder, ignore_errors=True)
    create_dir_if_not_exist(outfolder)

def test_one_file():
    """ saecc: test creation and verification of database for one file """
    filein = path_input('tuxsmall.jpg')
    filedb = path_output('saecc_file.db')
    fileout = path_output('tuxsmall.jpg')
    fileres = path_results('test_structural_adaptive_ecc_test_one_file.db')
    # Generate an ecc file
    assert saecc.main('-i "%s" -d "%s" --ecc_algo=3 -g -f --silent' % (filein, filedb)) == 0
    # Check that generated ecc file is correct
    startpos1 = find_next_entry(filedb, "\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF").next() # need to skip the comments, so we detect where the first entrymarker begins
    startpos2 = find_next_entry(fileres, "\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF").next()
    assert check_eq_files(filedb, fileres, startpos1=startpos1, startpos2=startpos2)

def test_one_file_tamper():
    """ saecc: test file repair """
    filein = path_input('tuxsmall.jpg')
    filedb = path_output('saecc_tamper.db')
    fileout = path_output('tuxsmall.jpg')
    fileout2 = path_output('repaired/tuxsmall.jpg')
    fileout2_dir = path_output('repaired')
    fileres = path_results('test_structural_adaptive_ecc_test_one_file_tamper.db')
    create_dir_if_not_exist(fileout2_dir)
    # Generate an ecc file
    assert saecc.main('-i "%s" -d "%s" --ecc_algo=3 -g -f --silent' % (filein, filedb)) == 0
    # Tamper the file
    shutil.copyfile(filein, fileout) # Copy it to avoid tampering the original
    tamper_file(fileout, 4, r'abcde')
    tamper_file(fileout, 1100, r'abcde') # tamper outside the range of header
    tamper_file(fileout, -5, r'abcde') # tamper end of file
    # Repair the file
    assert saecc.main('-i "%s" -d "%s" -o "%s" --ecc_algo=3 -c --silent' % (fileout, filedb, fileout2_dir)) == 0
    # Check that the file was completely repaired
    assert check_eq_files(filein, fileout2)

def test_dir():
    """ saecc: test creation and verification of database for a full directory """
    filein = path_input()
    filedb = path_output('saecc_dir.db')
    fileout = path_output()
    fileres = path_results('test_structural_adaptive_ecc_test_dir.db')
    # Generate an ecc file
    assert saecc.main('-i "%s" -d "%s" --ecc_algo=3 -g -f --silent' % (filein, filedb)) == 0
    # Check that generated ecc file is correct
    startpos1 = find_next_entry(filedb, "\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF").next() # need to skip the comments, so we detect where the first entrymarker begins
    startpos2 = find_next_entry(fileres, "\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF").next()
    assert check_eq_files(filedb, fileres, startpos1=startpos1, startpos2=startpos2)

def test_algo():
    """ saecc: test algorithms equivalence """
    filein = path_input('tuxsmall.jpg')
    filedb = [path_output('saecc_algo1.db'),
                path_output('saecc_algo2.db'),
                path_output('saecc_algo3.db'),
                ]
    fileres = path_results('test_structural_adaptive_ecc_test_algo.db')
    # For each algorithm
    for i in range(len(filedb)):
        # Generate an ecc file
        assert saecc.main('-i "%s" -d "%s" --ecc_algo=%i -g -f --silent' % (filein, filedb[i], i+1)) == 0
    # Check that all generated ecc are the same, whatever the algo (up to 3)
    startpos1 = find_next_entry(filedb[0], "\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF").next() # need to skip the comments, so we detect where the first entrymarker begins
    for i in range(1, len(filedb)):
        startpos2 = find_next_entry(filedb[i], "\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF").next()
        assert check_eq_files(filedb[0], filedb[i], startpos1=startpos1, startpos2=startpos2)
    # Check against expected ecc file
    startpos1 = find_next_entry(filedb[0], "\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF").next()
    startpos2 = find_next_entry(fileres, "\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF\xFE\xFF").next()
    assert check_eq_files(filedb[0], fileres, startpos1=startpos1, startpos2=startpos2)