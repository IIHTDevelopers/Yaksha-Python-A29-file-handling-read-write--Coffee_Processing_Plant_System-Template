import unittest
import os
import importlib
import sys
import io
import contextlib
import inspect
from test.TestUtils import TestUtils

# Helper functions for resilient testing
def check_file_exists(filename):
    """Check if a file exists in the current directory."""
    return os.path.exists(filename)

def safely_import_module(module_name):
    """Safely import a module, returning None if import fails."""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

def check_function_exists(module, function_name):
    """Check if a function exists in a module."""
    return hasattr(module, function_name) and callable(getattr(module, function_name))

def safely_call_function(module, function_name, *args, **kwargs):
    """Safely call a function, returning the result or None if it fails."""
    if not check_function_exists(module, function_name):
        return None
    try:
        # Suppress stdout to prevent unwanted output
        with contextlib.redirect_stdout(io.StringIO()):
            return getattr(module, function_name)(*args, **kwargs)
    except Exception:
        return None

def check_for_implementation(module, function_name):
    """Check if a function has a real implementation and not just 'pass'."""
    if not check_function_exists(module, function_name):
        return False
    try:
        source = inspect.getsource(getattr(module, function_name))
        # Check for actual implementation - look for meaningful code beyond just 'pass'
        lines = [line.strip() for line in source.split('\n') if line.strip()]
        non_trivial_lines = [line for line in lines if not line.startswith('#') and line not in ['pass', 'def ' + function_name]]
        return len(non_trivial_lines) > 3  # Function must have more than just def line, docstring, and return
    except Exception:
        return False

def load_module_dynamically():
    """Load the student's module for testing"""
    module_obj = safely_import_module("skeleton")
    if module_obj is None:
        module_obj = safely_import_module("solution")
    return module_obj

class TestAssignment(unittest.TestCase):
    def setUp(self):
        """Standard setup for all test methods"""
        self.test_obj = TestUtils()
        self.module_obj = load_module_dynamically()
    
    def test_boundary_scenarios(self):
        """Test boundary cases for coffee processing functions"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestBoundaryScenarios", False, "boundary")
                print("TestBoundaryScenarios = Failed")
                return
            
            # Check required functions
            required_functions = [
                "read_inventory",
                "read_processing_records",
                "find_batch_by_id",
                "add_bean_batch",
                "record_processing_stage",
                "update_batch_status",
                "calculate_inventory_summary",
                "calculate_processing_yields",
                "log_operation",
                "read_recent_logs",
                "create_sample_data"
            ]
            
            missing_functions = []
            for func_name in required_functions:
                if not check_function_exists(self.module_obj, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                self.test_obj.yakshaAssert("TestBoundaryScenarios", False, "boundary")
                print("TestBoundaryScenarios = Failed")
                return
            
            # Check for proper implementations
            unimplemented_functions = []
            for func_name in required_functions:
                if not check_for_implementation(self.module_obj, func_name):
                    unimplemented_functions.append(func_name)
            
            if unimplemented_functions:
                self.test_obj.yakshaAssert("TestBoundaryScenarios", False, "boundary")
                print("TestBoundaryScenarios = Failed")
                return
            
            # Create a list to collect errors
            errors = []
            
            # Create sample data for testing
            create_result = safely_call_function(self.module_obj, "create_sample_data")
            if create_result is None or create_result is False:
                errors.append("create_sample_data failed or returned False")
            
            # Test with empty files
            # Create empty files for testing
            with open("empty_inventory.txt", "w") as f:
                pass
                
            with open("empty_processing.txt", "w") as f:
                pass
                
            with open("empty_logs.txt", "w") as f:
                pass
            
            # Test reading empty inventory file
            empty_inventory = safely_call_function(self.module_obj, "read_inventory", "empty_inventory.txt")
            if empty_inventory is None:
                errors.append("read_inventory returned None for empty file")
            elif not isinstance(empty_inventory, list):
                errors.append("read_inventory should return a list")
            elif len(empty_inventory) != 0:
                errors.append("Empty inventory file should return empty list")
            
            # Test reading empty processing file
            empty_processing = safely_call_function(self.module_obj, "read_processing_records", "empty_processing.txt")
            if empty_processing is None:
                errors.append("read_processing_records returned None for empty file")
            elif not isinstance(empty_processing, list):
                errors.append("read_processing_records should return a list")
            elif len(empty_processing) != 0:
                errors.append("Empty processing file should return empty list")
            
            # Test reading empty logs file
            empty_logs = safely_call_function(self.module_obj, "read_recent_logs", 5, "empty_logs.txt")
            if empty_logs is None:
                errors.append("read_recent_logs returned None for empty file")
            elif not isinstance(empty_logs, list):
                errors.append("read_recent_logs should return a list")
            elif len(empty_logs) != 0:
                errors.append("Empty logs file should return empty list")
            
            # Test finding batch in empty file
            empty_batch = safely_call_function(self.module_obj, "find_batch_by_id", "B001", "empty_inventory.txt")
            if empty_batch is not None:
                errors.append("Finding batch in empty file should return None")
            
            # Test inventory summary with empty file
            empty_summary = safely_call_function(self.module_obj, "calculate_inventory_summary", "empty_inventory.txt")
            if empty_summary is not None:
                errors.append("Empty inventory should return None summary")
            
            # Test processing yields with empty files
            empty_yields = safely_call_function(self.module_obj, "calculate_processing_yields", "empty_inventory.txt", "empty_processing.txt")
            if empty_yields is None:
                errors.append("calculate_processing_yields returned None for empty files")
            elif not isinstance(empty_yields, dict):
                errors.append("calculate_processing_yields should return a dict")
            elif len(empty_yields) != 0:
                errors.append("Empty files should return empty yields dict")
            
            # Test with minimal single-record files
            # Create minimal files
            with open("single_inventory.txt", "w") as f:
                f.write("B999,2023-05-15,F999,Arabica,100,received\n")
                
            with open("single_processing.txt", "w") as f:
                f.write("B999,washing,2023-05-16,2023-05-17,98\n")
            
            # Test reading single-record inventory
            single_inventory = safely_call_function(self.module_obj, "read_inventory", "single_inventory.txt")
            if single_inventory is None:
                errors.append("read_inventory returned None for single record")
            elif not isinstance(single_inventory, list):
                errors.append("read_inventory should return a list for single record")
            elif len(single_inventory) != 1:
                errors.append("Single record inventory should return list with one item")
            elif single_inventory and single_inventory[0].get("batch_id") != "B999":
                errors.append("Should read the correct batch ID")
            
            # Test reading single-record processing
            single_processing = safely_call_function(self.module_obj, "read_processing_records", "single_processing.txt")
            if single_processing is None:
                errors.append("read_processing_records returned None for single record")
            elif not isinstance(single_processing, list):
                errors.append("read_processing_records should return a list for single record")
            elif len(single_processing) != 1:
                errors.append("Single record processing should return list with one item")
            elif single_processing and single_processing[0].get("batch_id") != "B999":
                errors.append("Should read the correct batch ID")
            
            # Test finding the single batch
            single_batch = safely_call_function(self.module_obj, "find_batch_by_id", "B999", "single_inventory.txt")
            if single_batch is None:
                errors.append("Should find the single batch")
            elif single_batch.get("batch_id") != "B999":
                errors.append("Should find the correct batch")
            
            # Test inventory summary with single record
            single_summary = safely_call_function(self.module_obj, "calculate_inventory_summary", "single_inventory.txt")
            if single_summary is None:
                errors.append("Should generate summary for single record")
            elif not isinstance(single_summary, dict):
                errors.append("calculate_inventory_summary should return a dict")
            elif single_summary.get("total_batches") != 1:
                errors.append("Summary should show one batch")
            elif single_summary.get("total_weight") != 100:
                errors.append("Summary should show correct weight")
            
            # Test processing yields with single record
            single_yields = safely_call_function(self.module_obj, "calculate_processing_yields", "single_inventory.txt", "single_processing.txt")
            if single_yields is None:
                errors.append("calculate_processing_yields returned None for single record")
            elif not isinstance(single_yields, dict):
                errors.append("calculate_processing_yields should return a dict")
            elif "washing" not in single_yields:
                errors.append("Should calculate yields for single record")
            elif single_yields.get("washing", {}).get("count") != 1:
                errors.append("Should show correct count in yields")
            
            # Test boundary cases for add_bean_batch
            # Test with minimal required fields
            minimal_batch = {
                "batch_id": "B100",
                "date": "2023-05-25",
                "farmer_id": "F100",
                "bean_type": "Arabica",
                "weight_kg": 100,
                "status": "received"
            }
            result = safely_call_function(self.module_obj, "add_bean_batch", minimal_batch, "test_inventory.txt")
            if result is None:
                errors.append("add_bean_batch returned None")
            elif result is not True:
                errors.append("Should successfully add minimal batch")
            
            # Test updating status
            update_result = safely_call_function(self.module_obj, "update_batch_status", "B100", "washing", "test_inventory.txt")
            if update_result is None:
                errors.append("update_batch_status returned None")
            elif update_result is not True:
                errors.append("Should successfully update batch status")
            
            updated_batch = safely_call_function(self.module_obj, "find_batch_by_id", "B100", "test_inventory.txt")
            if updated_batch is None:
                errors.append("Should find updated batch")
            elif updated_batch.get("status") != "washing":
                errors.append("Status should be updated correctly")
            
            # Test adding processing record
            minimal_processing = {
                "batch_id": "B100",
                "process_type": "washing",
                "start_date": "2023-05-26",
                "end_date": "2023-05-27",
                "weight_after": 98
            }
            process_result = safely_call_function(self.module_obj, "record_processing_stage", minimal_processing, "test_processing.txt")
            if process_result is None:
                errors.append("record_processing_stage returned None")
            elif process_result is not True:
                errors.append("Should successfully add processing record")
            
            # Test logging with minimal info
            log_result = safely_call_function(self.module_obj, "log_operation", "test", "minimal test", "test_log.txt")
            if log_result is None:
                errors.append("log_operation returned None")
            elif log_result is not True:
                errors.append("Should successfully log operation")
            
            # Clean up test files
            for file in ["empty_inventory.txt", "empty_processing.txt", "empty_logs.txt", 
                        "single_inventory.txt", "single_processing.txt", 
                        "test_inventory.txt", "test_processing.txt", "test_log.txt"]:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                    except:
                        pass  # Ignore cleanup errors
            
            # Final result checking
            if errors:
                self.test_obj.yakshaAssert("TestBoundaryScenarios", False, "boundary")
                print("TestBoundaryScenarios = Failed")
            else:
                self.test_obj.yakshaAssert("TestBoundaryScenarios", True, "boundary")
                print("TestBoundaryScenarios = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestBoundaryScenarios", False, "boundary")
            print("TestBoundaryScenarios = Failed")

if __name__ == '__main__':
    unittest.main()