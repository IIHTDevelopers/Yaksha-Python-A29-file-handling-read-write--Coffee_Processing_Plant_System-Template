import pytest
import inspect
import os
import sys
import importlib
from test.TestUtils import TestUtils

# Utility functions for resilient testing
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
    """Safely call a function, returning None if it fails."""
    if not check_function_exists(module, function_name):
        return None
    try:
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

class TestFunctional:
    """Test class for functional tests of the Coffee Processing System."""
    
    def setup_method(self):
        """Setup test data before each test method."""
        # Try to import the module under test
        self.module_obj = safely_import_module("skeleton")
        
        # Test object for assertions
        self.test_obj = TestUtils()
    
    def test_implementation_requirements(self):
        """Test function existence and implementation requirements"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestImplementationRequirements", False, "functional")
            pytest.fail("Could not import skeleton module")
            return
        
        # Create a list to collect errors
        errors = []
        
        try:
            # List of required function names
            required_functions = [
                "read_inventory", "read_processing_records", "find_batch_by_id",
                "add_bean_batch", "record_processing_stage", "update_batch_status",
                "calculate_inventory_summary", "calculate_processing_yields",
                "log_operation", "read_recent_logs", "create_sample_data", "main"
            ]
            
            # Check each required function exists
            missing_functions = []
            for func_name in required_functions:
                if not check_function_exists(self.module_obj, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                error_msg = f"Missing required functions: {', '.join(missing_functions)}"
                errors.append(error_msg)
                self.test_obj.yakshaAssert("TestImplementationRequirements", False, "functional")
                pytest.fail(error_msg)
                return
            
            # Check for proper implementations
            unimplemented_functions = []
            for func_name in required_functions:
                if not check_for_implementation(self.module_obj, func_name):
                    unimplemented_functions.append(func_name)
            
            if unimplemented_functions:
                error_msg = f"Functions not implemented (just 'pass'): {', '.join(unimplemented_functions)}"
                errors.append(error_msg)
                self.test_obj.yakshaAssert("TestImplementationRequirements", False, "functional")
                pytest.fail(error_msg)
                return
            
            # Check docstrings for all functions (optional but good practice)
            for func_name in required_functions:
                func = getattr(self.module_obj, func_name)
                if not func.__doc__:
                    errors.append(f"Function '{func_name}' is missing a docstring")
            
            # Ensure create_sample_data creates required files
            create_result = safely_call_function(self.module_obj, "create_sample_data")
            if create_result is None or create_result is False:
                errors.append("create_sample_data failed or returned False")
            
            # Check if files were created
            if not os.path.exists("bean_inventory.txt"):
                errors.append("bean_inventory.txt was not created")
            if not os.path.exists("processing_records.txt"):
                errors.append("processing_records.txt was not created")
            
            # Final result checking
            if errors:
                self.test_obj.yakshaAssert("TestImplementationRequirements", False, "functional")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestImplementationRequirements", True, "functional")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestImplementationRequirements", False, "functional")
            pytest.fail(f"Implementation requirements test failed: {str(e)}")
    
    def test_file_reading_operations(self):
        """Test reading operations from data files"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestFileReadingOperations", False, "functional")
            pytest.fail("Could not import skeleton module")
            return
        
        # Check required functions
        required_functions = [
            "create_sample_data",
            "read_inventory",
            "read_processing_records",
            "find_batch_by_id"
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not check_function_exists(self.module_obj, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            error_msg = f"Missing required functions: {', '.join(missing_functions)}"
            self.test_obj.yakshaAssert("TestFileReadingOperations", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Check for proper implementations
        unimplemented_functions = []
        for func_name in required_functions:
            if not check_for_implementation(self.module_obj, func_name):
                unimplemented_functions.append(func_name)
        
        if unimplemented_functions:
            error_msg = f"Functions not implemented (just 'pass'): {', '.join(unimplemented_functions)}"
            self.test_obj.yakshaAssert("TestFileReadingOperations", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Create a list to collect errors
        errors = []
        
        try:
            # Create sample data for testing
            create_result = safely_call_function(self.module_obj, "create_sample_data")
            if create_result is None or create_result is False:
                errors.append("create_sample_data failed or returned False")
            
            # Test reading inventory
            inventory = safely_call_function(self.module_obj, "read_inventory")
            if inventory is None:
                errors.append("read_inventory returned None")
            elif not isinstance(inventory, list):
                errors.append("read_inventory should return a list")
            elif len(inventory) == 0:
                errors.append("read_inventory should return a non-empty list")
            
            # Verify sample inventory data structure
            if inventory and len(inventory) > 0:
                first_batch = inventory[0]
                required_fields = ["batch_id", "date", "farmer_id", "bean_type", "weight_kg", "status"]
                for field in required_fields:
                    if field not in first_batch:
                        errors.append(f"Inventory record missing required field: {field}")
            
            # Test reading processing records
            records = safely_call_function(self.module_obj, "read_processing_records")
            if records is None:
                errors.append("read_processing_records returned None")
            elif not isinstance(records, list):
                errors.append("read_processing_records should return a list")
            elif len(records) == 0:
                errors.append("read_processing_records should return a non-empty list")
            
            # Verify sample processing data structure
            if records and len(records) > 0:
                first_record = records[0]
                required_fields = ["batch_id", "process_type", "start_date", "end_date", "weight_after"]
                for field in required_fields:
                    if field not in first_record:
                        errors.append(f"Processing record missing required field: {field}")
            
            # Test finding batch by ID
            batch_b001 = safely_call_function(self.module_obj, "find_batch_by_id", "B001")
            if batch_b001 is None:
                errors.append("Should find batch B001")
            elif batch_b001.get("batch_id") != "B001":
                errors.append("Should return the correct batch")
            
            # Test finding non-existent batch
            nonexistent_batch = safely_call_function(self.module_obj, "find_batch_by_id", "NonExistentBatch")
            if nonexistent_batch is not None:
                errors.append("Should return None for non-existent batch")
            
            # Final result checking
            if errors:
                self.test_obj.yakshaAssert("TestFileReadingOperations", False, "functional")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestFileReadingOperations", True, "functional")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestFileReadingOperations", False, "functional")
            pytest.fail(f"File reading operations test failed: {str(e)}")
    
    def test_file_writing_operations(self):
        """Test writing operations to data files"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestFileWritingOperations", False, "functional")
            pytest.fail("Could not import skeleton module")
            return
        
        # Check required functions
        required_functions = [
            "create_sample_data",
            "add_bean_batch",
            "find_batch_by_id",
            "record_processing_stage",
            "read_processing_records",
            "update_batch_status"
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not check_function_exists(self.module_obj, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            error_msg = f"Missing required functions: {', '.join(missing_functions)}"
            self.test_obj.yakshaAssert("TestFileWritingOperations", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Check for proper implementations
        unimplemented_functions = []
        for func_name in required_functions:
            if not check_for_implementation(self.module_obj, func_name):
                unimplemented_functions.append(func_name)
        
        if unimplemented_functions:
            error_msg = f"Functions not implemented (just 'pass'): {', '.join(unimplemented_functions)}"
            self.test_obj.yakshaAssert("TestFileWritingOperations", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Create a list to collect errors
        errors = []
        
        try:
            # Create sample data for testing
            create_result = safely_call_function(self.module_obj, "create_sample_data")
            if create_result is None or create_result is False:
                errors.append("create_sample_data failed or returned False")
            
            # Test adding a new batch
            new_batch = {
                "batch_id": "B999",
                "date": "2023-06-01",
                "farmer_id": "F050",
                "bean_type": "Robusta",
                "weight_kg": 275,
                "status": "received"
            }
            
            add_result = safely_call_function(self.module_obj, "add_bean_batch", new_batch)
            if add_result is None:
                errors.append("add_bean_batch returned None")
            elif add_result is not True:
                errors.append("Should successfully add new batch")
            
            # Verify batch was added
            added_batch = safely_call_function(self.module_obj, "find_batch_by_id", "B999")
            if added_batch is None:
                errors.append("Should find newly added batch")
            elif added_batch.get("batch_id") != "B999":
                errors.append("Should have correct batch ID")
            elif added_batch.get("bean_type") != "Robusta":
                errors.append("Should have correct bean type")
            
            # Test recording a processing stage
            new_processing = {
                "batch_id": "B999",
                "process_type": "washing",
                "start_date": "2023-06-02",
                "end_date": "2023-06-03",
                "weight_after": 270
            }
            
            process_result = safely_call_function(self.module_obj, "record_processing_stage", new_processing)
            if process_result is None:
                errors.append("record_processing_stage returned None")
            elif process_result is not True:
                errors.append("Should successfully record processing stage")
            
            # Verify processing record by reading all records
            all_records = safely_call_function(self.module_obj, "read_processing_records")
            if all_records is None:
                errors.append("read_processing_records returned None")
            elif not isinstance(all_records, list):
                errors.append("read_processing_records should return a list")
            else:
                found_record = False
                for record in all_records:
                    if record.get("batch_id") == "B999" and record.get("process_type") == "washing":
                        found_record = True
                        if record.get("weight_after") != 270:
                            errors.append("Should have correct weight after processing")
                        break
                
                if not found_record:
                    errors.append("Should find newly added processing record")
            
            # Verify batch status was updated
            updated_batch = safely_call_function(self.module_obj, "find_batch_by_id", "B999")
            if updated_batch is None:
                errors.append("Should find updated batch")
            elif updated_batch.get("status") != "washing":
                errors.append("Batch status should be updated after processing")
            
            # Test updating batch status directly
            update_result = safely_call_function(self.module_obj, "update_batch_status", "B999", "drying")
            if update_result is None:
                errors.append("update_batch_status returned None")
            elif update_result is not True:
                errors.append("Should successfully update batch status")
            
            # Verify status update
            updated_batch = safely_call_function(self.module_obj, "find_batch_by_id", "B999")
            if updated_batch is None:
                errors.append("Should find batch after status update")
            elif updated_batch.get("status") != "drying":
                errors.append("Batch status should be updated correctly")
            
            # Final result checking
            if errors:
                self.test_obj.yakshaAssert("TestFileWritingOperations", False, "functional")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestFileWritingOperations", True, "functional")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestFileWritingOperations", False, "functional")
            pytest.fail(f"File writing operations test failed: {str(e)}")
    
    def test_analysis_operations(self):
        """Test analysis operations on coffee data"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestAnalysisOperations", False, "functional")
            pytest.fail("Could not import skeleton module")
            return
        
        # Check required functions
        required_functions = [
            "create_sample_data",
            "calculate_inventory_summary",
            "calculate_processing_yields"
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not check_function_exists(self.module_obj, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            error_msg = f"Missing required functions: {', '.join(missing_functions)}"
            self.test_obj.yakshaAssert("TestAnalysisOperations", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Check for proper implementations
        unimplemented_functions = []
        for func_name in required_functions:
            if not check_for_implementation(self.module_obj, func_name):
                unimplemented_functions.append(func_name)
        
        if unimplemented_functions:
            error_msg = f"Functions not implemented (just 'pass'): {', '.join(unimplemented_functions)}"
            self.test_obj.yakshaAssert("TestAnalysisOperations", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Create a list to collect errors
        errors = []
        
        try:
            # Create sample data for testing
            create_result = safely_call_function(self.module_obj, "create_sample_data")
            if create_result is None or create_result is False:
                errors.append("create_sample_data failed or returned False")
            
            # Test calculating inventory summary
            summary = safely_call_function(self.module_obj, "calculate_inventory_summary")
            if summary is None:
                errors.append("Should generate inventory summary")
            elif not isinstance(summary, dict):
                errors.append("calculate_inventory_summary should return a dict")
            else:
                if "total_batches" not in summary:
                    errors.append("Summary should include total batches")
                if "total_weight" not in summary:
                    errors.append("Summary should include total weight")
                if "bean_types" not in summary:
                    errors.append("Summary should include bean types breakdown")
                if "stages" not in summary:
                    errors.append("Summary should include processing stages breakdown")
                
                # Verify summary calculations
                if summary.get("total_batches", 0) < 3:
                    errors.append("Should count at least 3 batches")
                if summary.get("total_weight", 0) <= 0:
                    errors.append("Total weight should be positive")
                
                # Test inventory by bean type
                bean_types = summary.get("bean_types", {})
                if "Arabica" not in bean_types:
                    errors.append("Should include Arabica beans")
                if "Robusta" not in bean_types:
                    errors.append("Should include Robusta beans")
                
                # Test inventory by processing stage
                stages = summary.get("stages", {})
                for stage in ["received", "washing", "drying"]:
                    if stage in stages and stages[stage] < 0:
                        errors.append(f"Should have valid weight for {stage} stage")
            
            # Test calculating processing yields
            yields = safely_call_function(self.module_obj, "calculate_processing_yields")
            if yields is None:
                errors.append("calculate_processing_yields returned None")
            elif not isinstance(yields, dict):
                errors.append("Should return a dictionary of yields")
            
            # Test yields for washing process
            if yields and "washing" in yields:
                washing_yields = yields["washing"]
                if "average_yield_percentage" not in washing_yields:
                    errors.append("Should include average yield percentage")
                elif washing_yields["average_yield_percentage"] <= 90:
                    errors.append("Washing yield should typically be above 90%")
            
            # Test displaying inventory summary - ensure it doesn't crash
            if check_function_exists(self.module_obj, "display_inventory_summary") and summary:
                try:
                    safely_call_function(self.module_obj, "display_inventory_summary", summary)
                    display_worked = True
                except Exception:
                    display_worked = False
                
                if not display_worked:
                    errors.append("Display inventory summary should work without errors")
            
            # Final result checking
            if errors:
                self.test_obj.yakshaAssert("TestAnalysisOperations", False, "functional")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestAnalysisOperations", True, "functional")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestAnalysisOperations", False, "functional")
            pytest.fail(f"Analysis operations test failed: {str(e)}")
    
    def test_logging_operations(self):
        """Test logging operations"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestLoggingOperations", False, "functional")
            pytest.fail("Could not import skeleton module")
            return
        
        # Check required functions
        required_functions = [
            "log_operation",
            "read_recent_logs"
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not check_function_exists(self.module_obj, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            error_msg = f"Missing required functions: {', '.join(missing_functions)}"
            self.test_obj.yakshaAssert("TestLoggingOperations", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Check for proper implementations
        unimplemented_functions = []
        for func_name in required_functions:
            if not check_for_implementation(self.module_obj, func_name):
                unimplemented_functions.append(func_name)
        
        if unimplemented_functions:
            error_msg = f"Functions not implemented (just 'pass'): {', '.join(unimplemented_functions)}"
            self.test_obj.yakshaAssert("TestLoggingOperations", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Create a list to collect errors
        errors = []
        
        try:
            # Clean log file
            if os.path.exists("operations_log.txt"):
                try:
                    os.remove("operations_log.txt")
                except:
                    pass  # Ignore removal errors
            
            # Test logging operations
            log_result = safely_call_function(self.module_obj, "log_operation", "test", "Test operation details")
            if log_result is None:
                errors.append("log_operation returned None")
            elif log_result is not True:
                errors.append("Should successfully log operation")
            
            # Verify log was written
            logs = safely_call_function(self.module_obj, "read_recent_logs", 1)
            if logs is None:
                errors.append("read_recent_logs returned None")
            elif not isinstance(logs, list):
                errors.append("Should return a list of logs")
            elif len(logs) != 1:
                errors.append("Should have one log entry")
            elif logs and logs[0].get("operation") != "test":
                errors.append("Should have correct operation type")
            elif logs and logs[0].get("details") != "Test operation details":
                errors.append("Should have correct details")
            
            # Test logging multiple operations
            safely_call_function(self.module_obj, "log_operation", "add", "Added test batch")
            safely_call_function(self.module_obj, "log_operation", "update", "Updated test batch")
            
            # Test reading multiple logs
            multiple_logs = safely_call_function(self.module_obj, "read_recent_logs", 3)
            if multiple_logs is None:
                errors.append("read_recent_logs returned None for multiple logs")
            elif not isinstance(multiple_logs, list):
                errors.append("read_recent_logs should return a list")
            elif len(multiple_logs) != 3:
                errors.append("Should return 3 most recent logs")
            
            # Verify logs are returned in correct order (newest first)
            if multiple_logs and len(multiple_logs) >= 3:
                if multiple_logs[0].get("operation") != "update":
                    errors.append("Most recent log should be first")
                if multiple_logs[1].get("operation") != "add":
                    errors.append("Second most recent log should be second")
                if multiple_logs[2].get("operation") != "test":
                    errors.append("Third most recent log should be third")
            
            # Final result checking
            if errors:
                self.test_obj.yakshaAssert("TestLoggingOperations", False, "functional")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestLoggingOperations", True, "functional")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestLoggingOperations", False, "functional")
            pytest.fail(f"Logging operations test failed: {str(e)}")
    
    def test_integration(self):
        """Test integration of multiple functions together"""
        # Check if module exists
        if self.module_obj is None:
            self.test_obj.yakshaAssert("TestIntegration", False, "functional")
            pytest.fail("Could not import skeleton module")
            return
        
        # Check required functions
        required_functions = [
            "create_sample_data",
            "add_bean_batch",
            "record_processing_stage",
            "calculate_inventory_summary",
            "calculate_processing_yields"
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not check_function_exists(self.module_obj, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            error_msg = f"Missing required functions: {', '.join(missing_functions)}"
            self.test_obj.yakshaAssert("TestIntegration", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Check for proper implementations
        unimplemented_functions = []
        for func_name in required_functions:
            if not check_for_implementation(self.module_obj, func_name):
                unimplemented_functions.append(func_name)
        
        if unimplemented_functions:
            error_msg = f"Functions not implemented (just 'pass'): {', '.join(unimplemented_functions)}"
            self.test_obj.yakshaAssert("TestIntegration", False, "functional")
            pytest.fail(error_msg)
            return
        
        # Create a list to collect errors
        errors = []
        
        try:
            # Create sample data for testing
            create_result = safely_call_function(self.module_obj, "create_sample_data")
            if create_result is None or create_result is False:
                errors.append("create_sample_data failed or returned False")
            
            # Test complete workflow: add batch -> process -> update -> analyze
            test_batch = {
                "batch_id": "B500",
                "date": "2023-06-10",
                "farmer_id": "F100",
                "bean_type": "Arabica",
                "weight_kg": 300,
                "status": "received"
            }
            
            # Step 1: Add batch
            add_result = safely_call_function(self.module_obj, "add_bean_batch", test_batch)
            if add_result is None or add_result is not True:
                errors.append("Failed to add test batch")
            
            # Step 2: Record processing stage (washing)
            process_washing = {
                "batch_id": "B500",
                "process_type": "washing",
                "start_date": "2023-06-11",
                "end_date": "2023-06-12",
                "weight_after": 295
            }
            wash_result = safely_call_function(self.module_obj, "record_processing_stage", process_washing)
            if wash_result is None or wash_result is not True:
                errors.append("Failed to record washing stage")
            
            # Step 3: Record next processing stage (drying)
            process_drying = {
                "batch_id": "B500",
                "process_type": "drying",
                "start_date": "2023-06-13",
                "end_date": "2023-06-15",
                "weight_after": 240
            }
            dry_result = safely_call_function(self.module_obj, "record_processing_stage", process_drying)
            if dry_result is None or dry_result is not True:
                errors.append("Failed to record drying stage")
            
            # Step 4: Analyze inventory
            summary = safely_call_function(self.module_obj, "calculate_inventory_summary")
            if summary is None:
                errors.append("Failed to calculate inventory summary")
            elif not isinstance(summary, dict):
                errors.append("Inventory summary should be a dict")
            else:
                # Verify our test batch is included in the summary
                if summary.get("total_weight", 0) < 240:
                    errors.append("Total weight should include our test batch")
                
                bean_types = summary.get("bean_types", {})
                if "Arabica" not in bean_types:
                    errors.append("Bean types should include our test batch")
                
                stages = summary.get("stages", {})
                if "drying" not in stages:
                    errors.append("Processing stages should include our test batch")
            
            # Step 5: Analyze processing yields
            yields = safely_call_function(self.module_obj, "calculate_processing_yields")
            if yields is None:
                errors.append("Failed to calculate processing yields")
            elif not isinstance(yields, dict):
                errors.append("Processing yields should be a dict")
            else:
                # Verify washing and drying yields are calculated
                if "washing" not in yields:
                    errors.append("Should calculate washing yields")
                if "drying" not in yields:
                    errors.append("Should calculate drying yields")
                
                # Verify expected yields (with some tolerance)
                if "washing" in yields:
                    washing_yield = process_washing["weight_after"] / test_batch["weight_kg"] * 100
                    actual_yield = yields["washing"].get("average_yield_percentage", 0)
                    if abs(actual_yield - washing_yield) > 10:
                        errors.append("Washing yield calculation should be reasonable")
                
                if "drying" in yields:
                    drying_yield = process_drying["weight_after"] / process_washing["weight_after"] * 100
                    actual_yield = yields["drying"].get("average_yield_percentage", 0)
                    if abs(actual_yield - drying_yield) > 10:
                        errors.append("Drying yield calculation should be reasonable")
            
            # Final result checking
            if errors:
                self.test_obj.yakshaAssert("TestIntegration", False, "functional")
                pytest.fail("\n".join(errors))
            else:
                self.test_obj.yakshaAssert("TestIntegration", True, "functional")
                
        except Exception as e:
            self.test_obj.yakshaAssert("TestIntegration", False, "functional")
            pytest.fail(f"Integration test failed: {str(e)}")


if __name__ == '__main__':
    pytest.main(['-v'])