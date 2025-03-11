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

class TestExceptional:
    """Exception handling tests for coffee processing system functions."""
    
    def test_exceptional_cases(self):
        """Test error handling and invalid inputs across all functions"""
        try:
            # Create sample data for testing
            create_sample_data()
            
            # ------------ PART 1: File Not Found Handling ------------
            
            # Test with non-existent files
            nonexistent_file = "nonexistent_file.txt"
            
            # Each function should handle nonexistent files gracefully
            inventory = read_inventory(nonexistent_file)
            assert isinstance(inventory, list) and len(inventory) == 0, "Should handle nonexistent inventory file"
            
            processing = read_processing_records(nonexistent_file)
            assert isinstance(processing, list) and len(processing) == 0, "Should handle nonexistent processing file"
            
            batch = find_batch_by_id("B001", nonexistent_file)
            assert batch is None, "Should handle nonexistent file in find_batch_by_id"
            
            summary = calculate_inventory_summary(nonexistent_file)
            assert summary is None, "Should handle nonexistent file in calculate_inventory_summary"
            
            yields = calculate_processing_yields(nonexistent_file, nonexistent_file)
            assert isinstance(yields, dict) and len(yields) == 0, "Should handle nonexistent files in processing yields"
            
            logs = read_recent_logs(5, nonexistent_file)
            assert isinstance(logs, list) and len(logs) == 0, "Should handle nonexistent log file"
            
            # ------------ PART 2: Invalid Input Data Handling ------------
            
            # Test with invalid batch data (missing required fields)
            invalid_batch = {
                "batch_id": "B200"
                # Missing other required fields
            }
            
            result = add_bean_batch(invalid_batch, "test_inventory.txt")
            assert result is False, "Should reject incomplete batch data"
            
            # Test with invalid processing data (missing required fields)
            invalid_processing = {
                "batch_id": "B001"
                # Missing other required fields
            }
            
            result = record_processing_stage(invalid_processing, "test_processing.txt")
            assert result is False, "Should reject incomplete processing data"
            
            # Test updating non-existent batch
            result = update_batch_status("NonExistentBatch", "washing", "bean_inventory.txt")
            assert result is False, "Should handle non-existent batch in update"
            
            # Test with invalid data types
            for func_name, func, args in [
                ("read_inventory", read_inventory, (123,)),
                ("read_processing_records", read_processing_records, (123,)),
                ("find_batch_by_id", find_batch_by_id, ("B001", 123)),
                ("calculate_inventory_summary", calculate_inventory_summary, (123,)),
                ("calculate_processing_yields", calculate_processing_yields, (123, 123)),
                ("read_recent_logs", read_recent_logs, ("not a number", "logs.txt"))
            ]:
                try:
                    result = func(*args)
                    # Even with invalid types, functions should return appropriate default values without crashing
                    if func_name == "read_inventory" or func_name == "read_processing_records" or func_name == "read_recent_logs":
                        assert isinstance(result, list), f"{func_name} should return a list even with invalid input"
                    elif func_name == "find_batch_by_id":
                        assert result is None, f"{func_name} should return None with invalid input"
                    elif func_name == "calculate_inventory_summary":
                        assert result is None, f"{func_name} should return None with invalid input"
                    elif func_name == "calculate_processing_yields":
                        assert isinstance(result, dict), f"{func_name} should return a dict even with invalid input"
                except Exception:
                    # If an exception is thrown, that's acceptable too
                    pass
            
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
            corrupted_inventory = read_inventory("corrupted_inventory.txt")
            assert isinstance(corrupted_inventory, list), "Should handle corrupted inventory gracefully"
            
            corrupted_processing = read_processing_records("corrupted_processing.txt")
            assert isinstance(corrupted_processing, list), "Should handle corrupted processing gracefully"
            
            # Test calculating summary and yields with corrupted files
            corrupted_summary = calculate_inventory_summary("corrupted_inventory.txt")
            # Either None or a valid summary with partial data is acceptable
            if corrupted_summary is not None:
                assert isinstance(corrupted_summary, dict), "Should return valid summary or None for corrupted data"
            
            corrupted_yields = calculate_processing_yields("corrupted_inventory.txt", "corrupted_processing.txt")
            assert isinstance(corrupted_yields, dict), "Should handle corrupted files in yields calculation"
            
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
            
            result = add_bean_batch(duplicate_batch, "bean_inventory.txt")
            assert result is False, "Should reject duplicate batch ID"
            
            # Test with zero or negative weights
            zero_weight_batch = {
                "batch_id": "B300",
                "date": "2023-05-25",
                "farmer_id": "F100",
                "bean_type": "Arabica",
                "weight_kg": 0,
                "status": "received"
            }
            
            result = add_bean_batch(zero_weight_batch, "test_inventory.txt")
            assert isinstance(result, bool), "Should handle zero weight appropriately"
            
            negative_weight_batch = {
                "batch_id": "B301",
                "date": "2023-05-25",
                "farmer_id": "F100",
                "bean_type": "Arabica",
                "weight_kg": -100,
                "status": "received"
            }
            
            try:
                result = add_bean_batch(negative_weight_batch, "test_inventory.txt")
                # Either accepting or rejecting negative weights is acceptable,
                # as long as the function doesn't crash
                assert isinstance(result, bool), "Should handle negative weight appropriately"
            except ValueError:
                # Raising ValueError for negative weight is also acceptable
                pass
            
            # Test with invalid file paths (directories, etc.)
            import os
            if not os.path.exists("test_dir"):
                os.mkdir("test_dir")
                
            try:
                result = read_inventory("test_dir")
                # Should handle directory path gracefully
            except Exception:
                # Exception is also acceptable
                pass
            
            # Clean up test files
            for file in ["corrupted_inventory.txt", "corrupted_processing.txt", "test_inventory.txt"]:
                if os.path.exists(file):
                    os.remove(file)
                    
            if os.path.exists("test_dir"):
                os.rmdir("test_dir")
            
            TestUtils.yakshaAssert("TestExceptionalCases", True, "exception")
        except Exception as e:
            TestUtils.yakshaAssert("TestExceptionalCases", False, "exception")
            pytest.fail(f"Exception testing failed: {str(e)}")


if __name__ == '__main__':
    pytest.main(['-v'])