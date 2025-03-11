# System Requirements Specification

# Coffee Processing Plant Management System (File Handling Focus)

Version 1.0

## TABLE OF CONTENTS

1. Project Abstract
2. Business Requirements
3. Code Requirements
4. Template Code Structure
5. Execution Steps to Follow

## 1. PROJECT ABSTRACT

Highland Coffee Cooperative needs a simple system to track coffee bean inventory and processing stages. This assignment focuses on implementing basic file handling operations to read, write, and analyze coffee processing data stored in text files.

## 2. BUSINESS REQUIREMENTS

1. System must track coffee bean batches from farmers
2. Tool must record basic processing stages (washing, drying, roasting)
3. System must generate simple reports on inventory and processing status

## 3. CODE REQUIREMENTS

### File Structure:
- Inventory data stored in "bean_inventory.txt"
- Processing records stored in "processing_records.txt"
- Operations log in "operations_log.txt"

### File Formats:
- Bean inventory records: "batch_id,date,farmer_id,bean_type,weight_kg,status"
  - Example: "B001,2023-05-15,F042,Arabica,250,received"
- Processing records: "batch_id,process_type,start_date,end_date,weight_after"
  - Example: "B001,washing,2023-05-16,2023-05-17,245"

### Function Requirements:
- Each function must include proper file opening and closing
- Each function must include error handling for file operations
- Each function must include a docstring describing its purpose and parameters

## 4. TEMPLATE CODE STRUCTURE

1. **File Reading Functions:**
   - `read_inventory(file_path)` - reads all bean batch records
   - `read_processing_records(file_path)` - reads all processing stage records
   - `find_batch_by_id(batch_id, file_path)` - locates a specific batch

2. **File Writing Functions:**
   - `add_bean_batch(batch_data, file_path)` - adds a new batch to inventory
   - `record_processing_stage(processing_data, file_path)` - adds a processing record
   - `update_batch_status(batch_id, new_status, file_path)` - updates a batch status

3. **Analysis Functions:**
   - `calculate_inventory_summary(file_path)` - summarizes current inventory
   - `calculate_processing_yields(inventory_path, processing_path)` - analyzes processing yields

4. **Helper Functions:**
   - `log_operation(operation, details, log_file_path)` - logs system operations
   - `create_sample_data()` - creates sample data for testing

5. **Main Function:**
   - `main()` - demonstrates all functionality with a command-line interface

## 5. EXECUTION STEPS TO FOLLOW

1. Implement the required file handling functions according to specifications
2. Create sample coffee batch and processing records for testing
3. Test each function with basic error handling
4. Create a simple command-line interface to demonstrate the functionality

