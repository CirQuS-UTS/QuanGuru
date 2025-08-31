import tempfile
import os
import csv
import shutil
from pathlib import Path
import numpy as np
import pytest
from quanguru.extensions.saveReadCSV import saveCSV, readCSV

@pytest.fixture
def testDir():
    """Set up temporary directory for test files"""
    tempDir = tempfile.mkdtemp()
    yield tempDir
    # Cleanup after test
    shutil.rmtree(tempDir)

def test_NoEmptyLinesBetweenRows(testDir):
    """Test that saveCSV doesn't add empty lines between rows"""
    # Test data with multiple rows
    testData = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ]
    
    fileName = "test_no_empty_lines"
    filePath = saveCSV(testData, path=testDir, fileName=fileName, dateTime=False)
    
    # Read the raw file content to check for empty lines
    fullFilePath = os.path.join(filePath, fileName + '.txt')
    with open(fullFilePath, 'r') as file:
        lines = file.readlines()
    
    # Should have exactly 3 lines (no empty lines between)
    assert len(lines) == 3, "Should have exactly 3 lines with no empty lines between"
    
    # Each line should end with only one newline character
    for i, line in enumerate(lines):
        assert line.endswith('\n'), f"Line {i} should end with newline"
        assert not line.endswith('\n\n'), f"Line {i} should not have double newline"

def test_singleRowData(testDir):
    """Test that single row data doesn't have extra newlines"""
    testData = [1.0, 2.0, 3.0, 4.0]
    
    fileName = "test_single_row"
    filePath = saveCSV(testData, path=testDir, fileName=fileName, dateTime=False)
    
    fullFilePath = os.path.join(filePath, fileName + '.txt')
    with open(fullFilePath, 'r') as file:
        content = file.read()
    
    # Should have exactly one line with one newline at the end
    lines = content.split('\n')
    assert len(lines) == 2, "Should have content line plus one empty line from final newline"
    assert lines[1] == "", "Second element should be empty (from final newline)"

def test_saveAndReadCSVCompatibility(testDir):
    """Test that the saved file is read properly by readCSV"""
    testData = [
        [1.1, 2.2, 3.3],
        [4.4, 5.5, 6.6],
        [7.7, 8.8, 9.9]
    ]
    
    fileName = "test_csv_compatibility"
    filePath = saveCSV(testData, path=testDir, fileName=fileName, dateTime=False)
    
    # Read back using csv.reader
    fullFilePath = os.path.join(filePath, fileName + '.txt')

    readData = readCSV(fullFilePath)

    # Should match original data
    assert len(readData) == len(testData), "Should read same number of rows"
    for i in range(len(testData)):
        assert len(readData[i]) == len(testData[i]), f"Row {i} should have same length"
        for j in range(len(testData[i])):
            assert abs(readData[i][j] - testData[i][j]) < 1e-6, f"Value at [{i}][{j}] should match"