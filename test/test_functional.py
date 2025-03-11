import pytest
import inspect
from test.TestUtils import TestUtils
from coffee_processing_plant_system import (
    read_inventory,
    read_processing_records,
    find_batch_by_id,
    add_bean_batch,
    record_processing_stage,
    update_batch_status,
    calculate_inventory_summary,
    calculate_processing_yields,
    log_operation,
    read_recent_logs,
    create_sample_data,
    display_inventory_summary,
    main
)

class TestFunctional:
    """Test class for functional tests of the Coffee Processing System."""
    
    def test_implementation_requirements(self):
        """Test function existence and implementation requirements"""
        try:
            # List of required function names
            required_functions = [
                "read_inventory", "read_processing_records", "find_batch_by_id",
                "add_bean_batch", "record_processing_stage", "update_batch_status",
                "calculate_inventory_summary", "calculate_processing_yields",
                "log_operation", "read_recent_logs", "create_sample_data", "main"
            ]
            
            # Get all function names from the imported module
            module_functions = [name for name, obj in globals().items() 
                               if callable(obj) and not name.startswith('__') and not name.startswith('Test')]
            
            # Check each required function exists
            for func_name in required_functions:
                assert func_name in module_functions, f"Required function '{func_name}' is missing"
            
            # Check docstrings for all functions
            for func_name in required_functions:
                func = globals()[func_name]
                assert func.__doc__, f"Function '{func_name}' is missing a docstring"
            
            # Ensure create_sample_data creates required files
            create_sample_data()
            
            # Check if files were created
            import os
            assert os.path.exists("bean_inventory.txt"), "bean_inventory.txt was not created"
            assert os.path.exists("processing_records.txt"), "processing_records.txt was not created"
            
            TestUtils.yakshaAssert("TestImplementationRequirements", True, "functional")
        except Exception as e:
            TestUtils.yakshaAssert("TestImplementationRequirements", False, "functional")
            pytest.fail(f"Implementation requirements test failed: {str(e)}")
    
    def test_file_reading_operations(self):
        """Test reading operations from data files"""
        try:
            # Create sample data for testing
            create_sample_data()
            
            # Test reading inventory
            inventory = read_inventory()
            assert isinstance(inventory, list) and len(inventory) > 0, "read_inventory should return a non-empty list"
            
            # Verify sample inventory data structure
            first_batch = inventory[0]
            required_fields = ["batch_id", "date", "farmer_id", "bean_type", "weight_kg", "status"]
            for field in required_fields:
                assert field in first_batch, f"Inventory record missing required field: {field}"
            
            # Test reading processing records
            records = read_processing_records()
            assert isinstance(records, list) and len(records) > 0, "read_processing_records should return a non-empty list"
            
            # Verify sample processing data structure
            first_record = records[0]
            required_fields = ["batch_id", "process_type", "start_date", "end_date", "weight_after"]
            for field in required_fields:
                assert field in first_record, f"Processing record missing required field: {field}"
            
            # Test finding batch by ID
            batch_b001 = find_batch_by_id("B001")
            assert batch_b001 is not None, "Should find batch B001"
            assert batch_b001["batch_id"] == "B001", "Should return the correct batch"
            
            # Test finding non-existent batch
            nonexistent_batch = find_batch_by_id("NonExistentBatch")
            assert nonexistent_batch is None, "Should return None for non-existent batch"
            
            TestUtils.yakshaAssert("TestFileReadingOperations", True, "functional")
        except Exception as e:
            TestUtils.yakshaAssert("TestFileReadingOperations", False, "functional")
            pytest.fail(f"File reading operations test failed: {str(e)}")
    
    def test_file_writing_operations(self):
        """Test writing operations to data files"""
        try:
            # Create sample data for testing
            create_sample_data()
            
            # Test adding a new batch
            new_batch = {
                "batch_id": "B999",
                "date": "2023-06-01",
                "farmer_id": "F050",
                "bean_type": "Robusta",
                "weight_kg": 275,
                "status": "received"
            }
            
            add_result = add_bean_batch(new_batch)
            assert add_result is True, "Should successfully add new batch"
            
            # Verify batch was added
            added_batch = find_batch_by_id("B999")
            assert added_batch is not None, "Should find newly added batch"
            assert added_batch["batch_id"] == "B999", "Should have correct batch ID"
            assert added_batch["bean_type"] == "Robusta", "Should have correct bean type"
            
            # Test recording a processing stage
            new_processing = {
                "batch_id": "B999",
                "process_type": "washing",
                "start_date": "2023-06-02",
                "end_date": "2023-06-03",
                "weight_after": 270
            }
            
            process_result = record_processing_stage(new_processing)
            assert process_result is True, "Should successfully record processing stage"
            
            # Verify processing record by reading all records
            all_records = read_processing_records()
            found_record = False
            for record in all_records:
                if record["batch_id"] == "B999" and record["process_type"] == "washing":
                    found_record = True
                    assert record["weight_after"] == 270, "Should have correct weight after processing"
                    break
            
            assert found_record, "Should find newly added processing record"
            
            # Verify batch status was updated
            updated_batch = find_batch_by_id("B999")
            assert updated_batch["status"] == "washing", "Batch status should be updated after processing"
            
            # Test updating batch status directly
            update_result = update_batch_status("B999", "drying")
            assert update_result is True, "Should successfully update batch status"
            
            # Verify status update
            updated_batch = find_batch_by_id("B999")
            assert updated_batch["status"] == "drying", "Batch status should be updated correctly"
            
            TestUtils.yakshaAssert("TestFileWritingOperations", True, "functional")
        except Exception as e:
            TestUtils.yakshaAssert("TestFileWritingOperations", False, "functional")
            pytest.fail(f"File writing operations test failed: {str(e)}")
    
    def test_analysis_operations(self):
        """Test analysis operations on coffee data"""
        try:
            # Create sample data for testing
            create_sample_data()
            
            # Test calculating inventory summary
            summary = calculate_inventory_summary()
            assert summary is not None, "Should generate inventory summary"
            assert "total_batches" in summary, "Summary should include total batches"
            assert "total_weight" in summary, "Summary should include total weight"
            assert "bean_types" in summary, "Summary should include bean types breakdown"
            assert "stages" in summary, "Summary should include processing stages breakdown"
            
            # Verify summary calculations
            assert summary["total_batches"] >= 3, "Should count at least 3 batches"
            assert summary["total_weight"] > 0, "Total weight should be positive"
            
            # Test inventory by bean type
            assert "Arabica" in summary["bean_types"], "Should include Arabica beans"
            assert "Robusta" in summary["bean_types"], "Should include Robusta beans"
            
            # Test inventory by processing stage
            for stage in ["received", "washing", "drying", "roasting"]:
                if stage in summary["stages"]:
                    assert summary["stages"][stage] >= 0, f"Should have valid weight for {stage} stage"
            
            # Test calculating processing yields
            yields = calculate_processing_yields()
            assert isinstance(yields, dict), "Should return a dictionary of yields"
            
            # Test yields for washing process
            if "washing" in yields:
                assert "average_yield_percentage" in yields["washing"], "Should include average yield percentage"
                assert yields["washing"]["average_yield_percentage"] > 90, "Washing yield should typically be above 90%"
            
            # Test displaying inventory summary - ensure it doesn't crash
            try:
                display_inventory_summary(summary)
                display_worked = True
            except Exception:
                display_worked = False
            
            assert display_worked, "Display inventory summary should work without errors"
            
            TestUtils.yakshaAssert("TestAnalysisOperations", True, "functional")
        except Exception as e:
            TestUtils.yakshaAssert("TestAnalysisOperations", False, "functional")
            pytest.fail(f"Analysis operations test failed: {str(e)}")
    
    def test_logging_operations(self):
        """Test logging operations"""
        try:
            # Clean log file
            import os
            if os.path.exists("operations_log.txt"):
                os.remove("operations_log.txt")
            
            # Test logging operations
            log_result = log_operation("test", "Test operation details")
            assert log_result is True, "Should successfully log operation"
            
            # Verify log was written
            logs = read_recent_logs(1)
            assert isinstance(logs, list), "Should return a list of logs"
            assert len(logs) == 1, "Should have one log entry"
            assert logs[0]["operation"] == "test", "Should have correct operation type"
            assert logs[0]["details"] == "Test operation details", "Should have correct details"
            
            # Test logging multiple operations
            log_operation("add", "Added test batch")
            log_operation("update", "Updated test batch")
            
            # Test reading multiple logs
            multiple_logs = read_recent_logs(3)
            assert len(multiple_logs) == 3, "Should return 3 most recent logs"
            
            # Verify logs are returned in correct order (newest first)
            assert multiple_logs[0]["operation"] == "update", "Most recent log should be first"
            assert multiple_logs[1]["operation"] == "add", "Second most recent log should be second"
            assert multiple_logs[2]["operation"] == "test", "Third most recent log should be third"
            
            TestUtils.yakshaAssert("TestLoggingOperations", True, "functional")
        except Exception as e:
            TestUtils.yakshaAssert("TestLoggingOperations", False, "functional")
            pytest.fail(f"Logging operations test failed: {str(e)}")
    
    def test_integration(self):
        """Test integration of multiple functions together"""
        try:
            # Create sample data for testing
            create_sample_data()
            
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
            add_bean_batch(test_batch)
            
            # Step 2: Record processing stage (washing)
            process_washing = {
                "batch_id": "B500",
                "process_type": "washing",
                "start_date": "2023-06-11",
                "end_date": "2023-06-12",
                "weight_after": 295
            }
            record_processing_stage(process_washing)
            
            # Step 3: Record next processing stage (drying)
            process_drying = {
                "batch_id": "B500",
                "process_type": "drying",
                "start_date": "2023-06-13",
                "end_date": "2023-06-15",
                "weight_after": 240
            }
            record_processing_stage(process_drying)
            
            # Step 4: Analyze inventory
            summary = calculate_inventory_summary()
            
            # Verify our test batch is included in the summary
            assert summary["total_weight"] >= 240, "Total weight should include our test batch"
            assert "Arabica" in summary["bean_types"], "Bean types should include our test batch"
            assert "drying" in summary["stages"], "Processing stages should include our test batch"
            
            # Step 5: Analyze processing yields
            yields = calculate_processing_yields()
            
            # Verify washing and drying yields are calculated
            assert "washing" in yields, "Should calculate washing yields"
            assert "drying" in yields, "Should calculate drying yields"
            
            # Verify expected yields
            washing_yield = process_washing["weight_after"] / test_batch["weight_kg"] * 100
            assert abs(yields["washing"]["average_yield_percentage"] - washing_yield) < 10, "Washing yield calculation should be reasonable"
            
            drying_yield = process_drying["weight_after"] / process_washing["weight_after"] * 100
            assert abs(yields["drying"]["average_yield_percentage"] - drying_yield) < 10, "Drying yield calculation should be reasonable"
            
            TestUtils.yakshaAssert("TestIntegration", True, "functional")
        except Exception as e:
            TestUtils.yakshaAssert("TestIntegration", False, "functional")
            pytest.fail(f"Integration test failed: {str(e)}")


if __name__ == '__main__':
    pytest.main(['-v'])