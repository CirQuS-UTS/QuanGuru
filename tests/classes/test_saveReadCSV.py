import tempfile
import os
import shutil
import numpy as np
import pytest
from quanguru.extensions.saveReadCSV import saveCSV, readCSV, saveQResCSV, _recursiveSaveList
from quanguru import qResults

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

def test_numpyIntegerTypes(testDir):
    """Test that various numpy integer types are properly saved using qResults and saveQResCSV"""
    # Test different numpy integer types
    testCases = [
        ([np.int8(1), np.int8(2), np.int8(3)], "int8"),
        ([np.int16(1), np.int16(2), np.int16(3)], "int16"), 
        ([np.int32(1), np.int32(2), np.int32(3)], "int32"),
        ([np.int64(1), np.int64(2), np.int64(3)], "int64"),
        ([np.intc(1), np.intc(2), np.intc(3)], "intc"),
        ([np.uint8(1), np.uint8(2), np.uint8(3)], "uint8"),
        ([np.uint16(1), np.uint16(2), np.uint16(3)], "uint16"),
        ([np.uint32(1), np.uint32(2), np.uint32(3)], "uint32"),
        ([np.uint64(1), np.uint64(2), np.uint64(3)], "uint64"),
    ]
    
    for testData, typeName in testCases:
        # Create qResults object and store data
        res = qResults()
        res.resultsDict[f'data_{typeName}'] = testData
        
        # Save using saveQResCSV
        saveQResCSV(res, path=testDir, fileNamePrefix=f'test_numpy_{typeName}_', dateTime=False)
        
        # Verify a file was created
        files = [f for f in os.listdir(testDir) if f.endswith('.txt') and typeName in f]
        assert len(files) > 0, f"File should be created for numpy {typeName}"
        
        # Verify content can be read back
        for fileName in files:
            fullFilePath = os.path.join(testDir, fileName)
            readData = readCSV(fullFilePath, datatype=int)
            
            # For single row data, readCSV returns a single numpy array
            # For multi-row data, it returns a list of numpy arrays
            if isinstance(readData, np.ndarray):
                # Single row case
                assert len(readData) == len(testData), f"Should read same number of elements for {typeName}"
                for i in range(len(testData)):
                    assert readData[i] == int(testData[i]), f"Value at [{i}] should match for {typeName}"
            else:
                # Multi-row case (shouldn't happen for this test, but just in case)
                assert len(readData) == 1, f"Should have single row for {typeName}"
                assert len(readData[0]) == len(testData), f"Should read same number of elements for {typeName}"
                for i in range(len(testData)):
                    assert readData[0][i] == int(testData[i]), f"Value at [{i}] should match for {typeName}"

def test_numpyFloatingTypes(testDir):
    """Test that various numpy floating types are properly saved using qResults and saveQResCSV"""
    # Use original intended values that are representable in all float types
    originalValues = [1.1, 2.2, 3.3]
    testCases = [
        ([np.float16(val) for val in originalValues], "float16", originalValues),
        ([np.float32(val) for val in originalValues], "float32", originalValues),
        ([np.float64(val) for val in originalValues], "float64", originalValues),
    ]
    
    for testData, typeName, expectedValues in testCases:
        # Create qResults object and store data
        res = qResults()
        res.resultsDict[f'data_{typeName}'] = testData
        
        # Save using saveQResCSV
        saveQResCSV(res, path=testDir, fileNamePrefix=f'test_numpy_{typeName}_', dateTime=False)
        
        # Verify a file was created - look specifically for files that contain our test data key
        files = [f for f in os.listdir(testDir) if f.endswith('.txt') and f'data_{typeName}' in f and f'test_numpy_{typeName}_' in f]
        assert len(files) > 0, f"File should be created for numpy {typeName}"
        
        # Verify content can be read back
        for fileName in files:
            fullFilePath = os.path.join(testDir, fileName)
            readData = readCSV(fullFilePath, datatype=float)
            
            # For single row data, readCSV returns a single numpy array
            if isinstance(readData, np.ndarray):
                # Single row case
                assert len(readData) == len(testData), f"Should read same number of elements for {typeName}"
                # Compare with the original intended values, not the imprecise numpy float representation
                for i in range(len(testData)):
                    assert abs(readData[i] - expectedValues[i]) < 1e-6, f"Value at [{i}] should match for {typeName}"
            else:
                # Multi-row case (shouldn't happen for this test, but just in case)
                assert len(readData) == 1, f"Should have single row for {typeName}"
                assert len(readData[0]) == len(testData), f"Should read same number of elements for {typeName}"
                # Compare with the original intended values, not the imprecise numpy float representation
                for i in range(len(testData)):
                    assert abs(readData[0][i] - expectedValues[i]) < 1e-6, f"Value at [{i}] should match for {typeName}"

def test_numpyIntegerMultipleRows(testDir):
    """Test that multiple rows with numpy integer types are properly saved using qResults and saveQResCSV"""
    testData = [
        [np.int32(1), np.int32(2), np.int32(3)],
        [np.int32(4), np.int32(5), np.int32(6)],
        [np.int32(7), np.int32(8), np.int32(9)]
    ]
    
    # Create qResults object and store data
    res = qResults()
    res.resultsDict['multi_row_data'] = testData
    
    # Save using saveQResCSV
    saveQResCSV(res, path=testDir, fileNamePrefix='test_numpy_int32_multi_row_', dateTime=False)
    
    # Verify a file was created - look specifically for files that contain our test data key
    files = [f for f in os.listdir(testDir) if f.endswith('.txt') and 'multi_row_data' in f and 'test_numpy_int32_multi_row_' in f]
    assert len(files) > 0, "File should be created for numpy int32 multi-row"
    
    # Verify content can be read back
    for fileName in files:
        fullFilePath = os.path.join(testDir, fileName)
        readData = readCSV(fullFilePath, datatype=int)
        assert len(readData) == len(testData), "Should read same number of rows"
        for i in range(len(testData)):
            assert len(readData[i]) == len(testData[i]), f"Row {i} should have same length"
            for j in range(len(testData[i])):
                assert readData[i][j] == int(testData[i][j]), f"Value at [{i}][{j}] should match"

def test_mixedNumpyAndPythonTypes(testDir):
    """Test that mixed numpy and Python types work together using qResults and saveQResCSV"""
    testData = [
        [1, np.int32(2), 3],  # Mixed int and np.int32
        [4.0, np.float32(5.5), 6.0],  # Mixed float and np.float32
    ]
    
    # Create qResults object and store data
    res = qResults()
    res.resultsDict['mixed_types_data'] = testData
    
    # Save using saveQResCSV
    saveQResCSV(res, path=testDir, fileNamePrefix='test_mixed_types_', dateTime=False)
    
    # Verify a file was created
    files = [f for f in os.listdir(testDir) if f.endswith('.txt') and 'mixed_types_data' in f]
    assert len(files) > 0, "File should be created with mixed types"
    
    # Verify content can be read back
    for fileName in files:
        fullFilePath = os.path.join(testDir, fileName)
        # Use float datatype since we have mixed int/float data
        readData = readCSV(fullFilePath, datatype=float)
        
        # readData should be a list of numpy arrays (one per row)
        assert isinstance(readData, list), "Read data should be a list"
        assert len(readData) == len(testData), f"Should read same number of rows, got {len(readData)}, expected {len(testData)}"
        
        # Check each row
        for i, row in enumerate(readData):
            assert len(row) == len(testData[i]), f"Row {i} should have same length"
            # Check values are approximately equal (allowing for float conversion)
            for j, val in enumerate(row):
                expected = float(testData[i][j])
                assert abs(val - expected) < 1e-6, f"Value at [{i}][{j}] should match: got {val}, expected {expected}"

def test_numpyComplexTypes(testDir):
    """Test that numpy complex types are handled using qResults and saveQResCSV"""
    testData = [np.complex64(1+2j), np.complex64(3+4j), np.complex64(5+6j)]
    
    # Create qResults object and store data
    res = qResults()
    res.resultsDict['complex_data'] = testData
    
    # Save using saveQResCSV
    saveQResCSV(res, path=testDir, fileNamePrefix='test_numpy_complex_', dateTime=False)
    
    # Verify a file was created
    files = [f for f in os.listdir(testDir) if f.endswith('.txt') and 'complex' in f]
    assert len(files) > 0, "File should be created for numpy complex64"
    
    # Verify content can be read back
    for fileName in files:
        fullFilePath = os.path.join(testDir, fileName)
        # Complex numbers will be written as strings, so we just verify the file has content
        with open(fullFilePath, 'r') as f:
            content = f.read().strip()
            assert len(content) > 0, "File should have content for complex numbers"