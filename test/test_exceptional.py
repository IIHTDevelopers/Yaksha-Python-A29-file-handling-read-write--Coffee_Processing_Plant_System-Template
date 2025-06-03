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

def check_exception_raised(module, function_name, expected_exceptions, *args, **kwargs):
    """Check if a function raises the expected exception."""
    if not check_function_exists(module, function_name):
        return False
    
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            getattr(module, function_name)(*args, **kwargs)
        return False  # No exception raised
    except Exception as e:
        # Check if the exception is one of the expected types
        return any(isinstance(e, exc) for exc in expected_exceptions)

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
    
    def test_exceptional_cases(self):
        """Test error handling and invalid inputs across all functions"""
        try:
            # Check if module can be imported
            if self.module_obj is None:
                self.test_obj.yakshaAssert("TestExceptionalCases", False, "exception")
                print("TestExceptionalCases = Failed")
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
                self.test_obj.yakshaAssert("TestExceptionalCases", False, "exception")
                print("TestExceptionalCases = Failed")
                return
            
            # Check for proper implementations
            unimplemented_functions = []
            for func_name in required_functions:
                if not check_for_implementation(self.module_obj, func_name):
                    unimplemented_functions.append(func_name)
            
            if unimplemented_functions:
                self.test_obj.yakshaAssert("TestExceptionalCases", False, "exception")
                print("TestExceptionalCases = Failed")
                return
            
            # Create a list to collect errors
            errors = []
            
            # Create sample data for testing
            create_result = safely_call_function(self.module_obj, "create_sample_data")
            if create_result is None or create_result is False:
                errors.append("create_sample_data failed or returned False")
            
            # ------------ PART 1: File Not Found Handling ------------
            
            # Test with non-existent files
            nonexistent_file = "nonexistent_file.txt"
            
            # Each function should handle nonexistent files gracefully
            inventory = safely_call_function(self.module_obj, "read_inventory", nonexistent_file)
            if inventory is None:
                errors.append("read_inventory returned None for nonexistent file")
            elif not isinstance(inventory, list):
                errors.append("read_inventory should return a list for nonexistent file")
            elif len(inventory) != 0:
                errors.append("Should handle nonexistent inventory file")
            
            processing = safely_call_function(self.module_obj, "read_processing_records", nonexistent_file)
            if processing is None:
                errors.append("read_processing_records returned None for nonexistent file")
            elif not isinstance(processing, list):
                errors.append("read_processing_records should return a list for nonexistent file")
            elif len(processing) != 0:
                errors.append("Should handle nonexistent processing file")
            
            batch = safely_call_function(self.module_obj, "find_batch_by_id", "B001", nonexistent_file)
            if batch is not None:
                errors.append("Should handle nonexistent file in find_batch_by_id")
            
            summary = safely_call_function(self.module_obj, "calculate_inventory_summary", nonexistent_file)
            if summary is not None:
                errors.append("Should handle nonexistent file in calculate_inventory_summary")
            
            yields = safely_call_function(self.module_obj, "calculate_processing_yields", nonexistent_file, nonexistent_file)
            if yields is None:
                errors.append("calculate_processing_yields returned None for nonexistent files")
            elif not isinstance(yields, dict):
                errors.append("calculate_processing_yields should return a dict for nonexistent files")
            elif len(yields) != 0:
                errors.append("Should handle nonexistent files in processing yields")
            
            logs = safely_call_function(self.module_obj, "read_recent_logs", 5, nonexistent_file)
            if logs is None:
                errors.append("read_recent_logs returned None for nonexistent file")
            elif not isinstance(logs, list):
                errors.append("read_recent_logs should return a list for nonexistent file")
            elif len(logs) != 0:
                errors.append("Should handle nonexistent log file")
            
            # ------------ PART 2: Invalid Input Data Handling ------------
            
            # Test with invalid batch data (missing required fields)
            invalid_batch = {
                "batch_id": "B200"
                # Missing other required fields
            }
            
            result = safely_call_function(self.module_obj, "add_bean_batch", invalid_batch, "test_inventory.txt")
            if result is None:
                errors.append("add_bean_batch returned None for invalid data")
            elif result is not False:
                errors.append("Should reject incomplete batch data")
            
            # Test with invalid processing data (missing required fields)
            invalid_processing = {
                "batch_id": "B001"
                # Missing other required fields
            }
            
            result = safely_call_function(self.module_obj, "record_processing_stage", invalid_processing, "test_processing.txt")
            if result is None:
                errors.append("record_processing_stage returned None for invalid data")
            elif result is not False:
                errors.append("Should reject incomplete processing data")
            
            # Test updating non-existent batch
            result = safely_call_function(self.module_obj, "update_batch_status", "NonExistentBatch", "washing", "bean_inventory.txt")
            if result is None:
                errors.append("update_batch_status returned None for nonexistent batch")
            elif result is not False:
                errors.append("Should handle non-existent batch in update")
            
            # Test with invalid data types
            test_cases = [
                ("read_inventory", (123,)),
                ("read_processing_records", (123,)),
                ("find_batch_by_id", ("B001", 123)),
                ("calculate_inventory_summary", (123,)),
                ("calculate_processing_yields", (123, 123)),
                ("read_recent_logs", ("not a number", "logs.txt"))
            ]
            
            for func_name, args in test_cases:
                result = safely_call_function(self.module_obj, func_name, *args)
                # Even with invalid types, functions should return appropriate default values without crashing
                if func_name in ["read_inventory", "read_processing_records", "read_recent_logs"]:
                    if result is None:
                        errors.append(f"{func_name} returned None with invalid input")
                    elif not isinstance(result, list):
                        errors.append(f"{func_name} should return a list even with invalid input")
                elif func_name == "find_batch_by_id":
                    if result is not None:
                        errors.append(f"{func_name} should return None with invalid input")
                elif func_name == "calculate_inventory_summary":
                    if result is not None:
                        errors.append(f"{func_name} should return None with invalid input")
                elif func_name == "calculate_processing_yields":
                    if result is None:
                        errors.append(f"{func_name} returned None with invalid input")
                    elif not isinstance(result, dict):
                        errors.append(f"{func_name} should return a dict even with invalid input")
            
            # ------------ PART 3: Corrupted Data Handling ------------
            
            # Create files with corrupted data
            with open("corrupted_inventory.txt", "w") as f:
                f.write("This is not a valid CSV format\n")
                f.write("B001,incomplete line\n")
                f.write(",,,,,\n")  # Empty fields
                f.write("B002,2023-05-16,F036,Robusta,invalid_weight,washing\n")  # Invalid weight
            
            with open("corrupted_processing.txt", "w") as f:
                f.write("This is not a valid CSV format\n")
                f.write("B001,washing,2023-05-16\n")  # Incomplete line
                f.write("B002,washing,2023-05-17,2023-05-18,invalid_weight\n")  # Invalid weight
            
            # Test reading corrupted files
            corrupted_inventory = safely_call_function(self.module_obj, "read_inventory", "corrupted_inventory.txt")
            if corrupted_inventory is None:
                errors.append("read_inventory returned None for corrupted file")
            elif not isinstance(corrupted_inventory, list):
                errors.append("Should handle corrupted inventory gracefully")
            
            corrupted_processing = safely_call_function(self.module_obj, "read_processing_records", "corrupted_processing.txt")
            if corrupted_processing is None:
                errors.append("read_processing_records returned None for corrupted file")
            elif not isinstance(corrupted_processing, list):
                errors.append("Should handle corrupted processing gracefully")
            
            # Test calculating summary and yields with corrupted files
            corrupted_summary = safely_call_function(self.module_obj, "calculate_inventory_summary", "corrupted_inventory.txt")
            # Either None or a valid summary with partial data is acceptable
            if corrupted_summary is not None and not isinstance(corrupted_summary, dict):
                errors.append("Should return valid summary or None for corrupted data")
            
            corrupted_yields = safely_call_function(self.module_obj, "calculate_processing_yields", "corrupted_inventory.txt", "corrupted_processing.txt")
            if corrupted_yields is None:
                errors.append("calculate_processing_yields returned None for corrupted files")
            elif not isinstance(corrupted_yields, dict):
                errors.append("Should handle corrupted files in yields calculation")
            
            # ------------ PART 4: Edge Case Handling ------------
            
            # Test with duplicate batch IDs
            duplicate_batch = {
                "batch_id": "B001",  # Already exists in sample data
                "date": "2023-05-25",
                "farmer_id": "F100",
                "bean_type": "Arabica",
                "weight_kg": 100,
                "status": "received"
            }
            
            result = safely_call_function(self.module_obj, "add_bean_batch", duplicate_batch, "bean_inventory.txt")
            if result is None:
                errors.append("add_bean_batch returned None for duplicate batch")
            elif result is not False:
                errors.append("Should reject duplicate batch ID")
            
            # Test with zero or negative weights
            zero_weight_batch = {
                "batch_id": "B300",
                "date": "2023-05-25",
                "farmer_id": "F100",
                "bean_type": "Arabica",
                "weight_kg": 0,
                "status": "received"
            }
            
            result = safely_call_function(self.module_obj, "add_bean_batch", zero_weight_batch, "test_inventory.txt")
            if result is None:
                errors.append("add_bean_batch returned None for zero weight")
            elif not isinstance(result, bool):
                errors.append("Should handle zero weight appropriately")
            
            negative_weight_batch = {
                "batch_id": "B301",
                "date": "2023-05-25",
                "farmer_id": "F100",
                "bean_type": "Arabica",
                "weight_kg": -100,
                "status": "received"
            }
            
            result = safely_call_function(self.module_obj, "add_bean_batch", negative_weight_batch, "test_inventory.txt")
            if result is not None and not isinstance(result, bool):
                errors.append("Should handle negative weight appropriately")
            
            # Test with invalid file paths (directories, etc.)
            if not os.path.exists("test_dir"):
                os.mkdir("test_dir")
                
            try:
                result = safely_call_function(self.module_obj, "read_inventory", "test_dir")
                # Should handle directory path gracefully
            except Exception:
                # Exception is also acceptable
                pass
            
            # Clean up test files
            for file in ["corrupted_inventory.txt", "corrupted_processing.txt", "test_inventory.txt"]:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                    except:
                        pass  # Ignore cleanup errors
                    
            if os.path.exists("test_dir"):
                try:
                    os.rmdir("test_dir")
                except:
                    pass  # Ignore cleanup errors
            
            # Final result checking
            if errors:
                self.test_obj.yakshaAssert("TestExceptionalCases", False, "exception")
                print("TestExceptionalCases = Failed")
            else:
                self.test_obj.yakshaAssert("TestExceptionalCases", True, "exception")
                print("TestExceptionalCases = Passed")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestExceptionalCases", False, "exception")
            print("TestExceptionalCases = Failed")

if __name__ == '__main__':
    unittest.main()