import pytest
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
    create_sample_data
)

class TestBoundary:
    """Boundary tests for coffee processing system functions."""
    
    def test_boundary_scenarios(self):
        """Test boundary cases for coffee processing functions"""
        try:
            # Create sample data for testing
            create_sample_data()
            
            # Test with empty files
            # Create empty files for testing
            with open("empty_inventory.txt", "w") as f:
                pass
                
            with open("empty_processing.txt", "w") as f:
                pass
                
            with open("empty_logs.txt", "w") as f:
                pass
            
            # Test reading empty inventory file
            empty_inventory = read_inventory("empty_inventory.txt")
            assert len(empty_inventory) == 0, "Empty inventory file should return empty list"
            
            # Test reading empty processing file
            empty_processing = read_processing_records("empty_processing.txt")
            assert len(empty_processing) == 0, "Empty processing file should return empty list"
            
            # Test reading empty logs file
            empty_logs = read_recent_logs(5, "empty_logs.txt")
            assert len(empty_logs) == 0, "Empty logs file should return empty list"
            
            # Test finding batch in empty file
            empty_batch = find_batch_by_id("B001", "empty_inventory.txt")
            assert empty_batch is None, "Finding batch in empty file should return None"
            
            # Test inventory summary with empty file
            empty_summary = calculate_inventory_summary("empty_inventory.txt")
            assert empty_summary is None, "Empty inventory should return None summary"
            
            # Test processing yields with empty files
            empty_yields = calculate_processing_yields("empty_inventory.txt", "empty_processing.txt")
            assert len(empty_yields) == 0, "Empty files should return empty yields dict"
            
            # Test with minimal single-record files
            # Create minimal files
            with open("single_inventory.txt", "w") as f:
                f.write("B999,2023-05-15,F999,Arabica,100,received\n")
                
            with open("single_processing.txt", "w") as f:
                f.write("B999,washing,2023-05-16,2023-05-17,98\n")
            
            # Test reading single-record inventory
            single_inventory = read_inventory("single_inventory.txt")
            assert len(single_inventory) == 1, "Single record inventory should return list with one item"
            assert single_inventory[0]["batch_id"] == "B999", "Should read the correct batch ID"
            
            # Test reading single-record processing
            single_processing = read_processing_records("single_processing.txt")
            assert len(single_processing) == 1, "Single record processing should return list with one item"
            assert single_processing[0]["batch_id"] == "B999", "Should read the correct batch ID"
            
            # Test finding the single batch
            single_batch = find_batch_by_id("B999", "single_inventory.txt")
            assert single_batch is not None, "Should find the single batch"
            assert single_batch["batch_id"] == "B999", "Should find the correct batch"
            
            # Test inventory summary with single record
            single_summary = calculate_inventory_summary("single_inventory.txt")
            assert single_summary is not None, "Should generate summary for single record"
            assert single_summary["total_batches"] == 1, "Summary should show one batch"
            assert single_summary["total_weight"] == 100, "Summary should show correct weight"
            
            # Test processing yields with single record
            single_yields = calculate_processing_yields("single_inventory.txt", "single_processing.txt")
            assert "washing" in single_yields, "Should calculate yields for single record"
            assert single_yields["washing"]["count"] == 1, "Should show correct count in yields"
            
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
            result = add_bean_batch(minimal_batch, "test_inventory.txt")
            assert result is True, "Should successfully add minimal batch"
            
            # Test updating status
            update_result = update_batch_status("B100", "washing", "test_inventory.txt")
            assert update_result is True, "Should successfully update batch status"
            
            updated_batch = find_batch_by_id("B100", "test_inventory.txt")
            assert updated_batch["status"] == "washing", "Status should be updated correctly"
            
            # Test adding processing record
            minimal_processing = {
                "batch_id": "B100",
                "process_type": "washing",
                "start_date": "2023-05-26",
                "end_date": "2023-05-27",
                "weight_after": 98
            }
            process_result = record_processing_stage(minimal_processing, "test_processing.txt")
            assert process_result is True, "Should successfully add processing record"
            
            # Test logging with minimal info
            log_result = log_operation("test", "minimal test", "test_log.txt")
            assert log_result is True, "Should successfully log operation"
            
            # Clean up test files
            import os
            for file in ["empty_inventory.txt", "empty_processing.txt", "empty_logs.txt", 
                        "single_inventory.txt", "single_processing.txt", 
                        "test_inventory.txt", "test_processing.txt", "test_log.txt"]:
                if os.path.exists(file):
                    os.remove(file)
            
            TestUtils.yakshaAssert("TestBoundaryScenarios", True, "boundary")
        except Exception as e:
            TestUtils.yakshaAssert("TestBoundaryScenarios", False, "boundary")
            pytest.fail(f"Boundary scenarios test failed: {str(e)}")


if __name__ == '__main__':
    pytest.main(['-v'])