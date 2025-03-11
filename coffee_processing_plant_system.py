"""
Coffee Processing Plant Management System

This module provides functions for tracking coffee bean inventory,
processing stages, and generating reports using file-based storage.
"""

def create_sample_data():
    """
    Creates sample data files for demonstration purposes.
    
    Creates bean_inventory.txt and processing_records.txt with sample data.
    """
    try:
        # Create bean inventory file
        with open("bean_inventory.txt", "w") as f:
            f.write("B001,2023-05-15,F042,Arabica,250,received\n")
            f.write("B002,2023-05-16,F036,Robusta,300,washing\n")
            f.write("B003,2023-05-17,F042,Arabica,175,drying\n")
        
        # Create processing records file
        with open("processing_records.txt", "w") as f:
            f.write("B001,washing,2023-05-16,2023-05-17,245\n")
            f.write("B002,washing,2023-05-17,2023-05-18,294\n")
            f.write("B003,drying,2023-05-18,2023-05-20,160\n")
            
        return True
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return False

# File Reading Functions
def read_inventory(file_path="bean_inventory.txt"):
    """
    Reads all coffee bean batch records from the inventory file.
    
    Args:
        file_path (str): Path to the inventory file
        
    Returns:
        list: List of dictionaries containing batch information
    """
    inventory = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    parts = line.strip().split(",")
                    if len(parts) >= 6:
                        batch = {
                            "batch_id": parts[0],
                            "date": parts[1],
                            "farmer_id": parts[2],
                            "bean_type": parts[3],
                            "weight_kg": float(parts[4]),
                            "status": parts[5]
                        }
                        inventory.append(batch)
        return inventory
    except FileNotFoundError:
        print(f"Inventory file not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading inventory: {e}")
        return []

def read_processing_records(file_path="processing_records.txt"):
    """
    Reads all processing stage records from the processing file.
    
    Args:
        file_path (str): Path to the processing records file
        
    Returns:
        list: List of dictionaries containing processing information
    """
    records = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    parts = line.strip().split(",")
                    if len(parts) >= 5:
                        record = {
                            "batch_id": parts[0],
                            "process_type": parts[1],
                            "start_date": parts[2],
                            "end_date": parts[3],
                            "weight_after": float(parts[4])
                        }
                        records.append(record)
        return records
    except FileNotFoundError:
        print(f"Processing records file not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading processing records: {e}")
        return []

def find_batch_by_id(batch_id, file_path="bean_inventory.txt"):
    """
    Locates a specific batch record in the inventory.
    
    Args:
        batch_id (str): The ID of the batch to find
        file_path (str): Path to the inventory file
        
    Returns:
        dict: Batch information if found, None otherwise
    """
    try:
        inventory = read_inventory(file_path)
        for batch in inventory:
            if batch["batch_id"] == batch_id:
                return batch
        return None
    except Exception as e:
        print(f"Error finding batch: {e}")
        return None

# File Writing Functions
def add_bean_batch(batch_data, file_path="bean_inventory.txt"):
    """
    Adds a new bean batch to the inventory file.
    
    Args:
        batch_data (dict): Dictionary containing batch information
        file_path (str): Path to the inventory file
        
    Returns:
        bool: True if the batch was added successfully
    """
    # Validate required fields
    required_fields = ["batch_id", "date", "farmer_id", "bean_type", "weight_kg", "status"]
    for field in required_fields:
        if field not in batch_data:
            print(f"Missing required field: {field}")
            return False
    
    try:
        # Check if batch ID already exists
        existing = find_batch_by_id(batch_data["batch_id"], file_path)
        if existing:
            print(f"Batch ID already exists: {batch_data['batch_id']}")
            return False
        
        # Format batch data as CSV line
        line = (f"{batch_data['batch_id']},{batch_data['date']},"
                f"{batch_data['farmer_id']},{batch_data['bean_type']},"
                f"{batch_data['weight_kg']},{batch_data['status']}\n")
        
        # Append to file
        with open(file_path, "a") as f:
            f.write(line)
        
        # Log the operation
        log_operation("add_batch", f"Added batch {batch_data['batch_id']}")
        
        return True
    except Exception as e:
        print(f"Error adding batch: {e}")
        return False

def record_processing_stage(processing_data, file_path="processing_records.txt"):
    """
    Adds a new processing record to the processing records file.
    
    Args:
        processing_data (dict): Dictionary containing processing information
        file_path (str): Path to the processing records file
        
    Returns:
        bool: True if the record was added successfully
    """
    # Validate required fields
    required_fields = ["batch_id", "process_type", "start_date", "end_date", "weight_after"]
    for field in required_fields:
        if field not in processing_data:
            print(f"Missing required field: {field}")
            return False
    
    try:
        # Format processing data as CSV line
        line = (f"{processing_data['batch_id']},{processing_data['process_type']},"
                f"{processing_data['start_date']},{processing_data['end_date']},"
                f"{processing_data['weight_after']}\n")
        
        # Append to file
        with open(file_path, "a") as f:
            f.write(line)
        
        # Update batch status
        update_batch_status(processing_data['batch_id'], processing_data['process_type'])
        
        # Log the operation
        log_operation("record_processing", 
                     f"Recorded {processing_data['process_type']} for batch {processing_data['batch_id']}")
        
        return True
    except Exception as e:
        print(f"Error recording processing stage: {e}")
        return False

def update_batch_status(batch_id, new_status, file_path="bean_inventory.txt"):
    """
    Updates the status of a batch in the inventory file.
    
    Args:
        batch_id (str): ID of the batch to update
        new_status (str): New status for the batch
        file_path (str): Path to the inventory file
        
    Returns:
        bool: True if the batch was updated successfully
    """
    try:
        # Read all batches
        inventory = read_inventory(file_path)
        
        # Find and update the batch
        batch_found = False
        for batch in inventory:
            if batch["batch_id"] == batch_id:
                batch["status"] = new_status
                batch_found = True
                break
        
        if not batch_found:
            print(f"Batch not found: {batch_id}")
            return False
        
        # Write back to file
        with open(file_path, "w") as f:
            for batch in inventory:
                line = (f"{batch['batch_id']},{batch['date']},"
                        f"{batch['farmer_id']},{batch['bean_type']},"
                        f"{batch['weight_kg']},{batch['status']}\n")
                f.write(line)
        
        # Log the operation
        log_operation("update_status", f"Updated batch {batch_id} status to {new_status}")
        
        return True
    except Exception as e:
        print(f"Error updating batch status: {e}")
        return False

# Analysis Functions
def calculate_inventory_summary(file_path="bean_inventory.txt"):
    """
    Generates a summary of the current inventory.
    
    Args:
        file_path (str): Path to the inventory file
        
    Returns:
        dict: Dictionary containing inventory summary information
    """
    try:
        inventory = read_inventory(file_path)
        
        if not inventory:
            return None
            
        # Calculate totals
        total_batches = len(inventory)
        total_weight = sum(batch["weight_kg"] for batch in inventory)
        
        # Group by bean type
        bean_types = {}
        for batch in inventory:
            bean_type = batch["bean_type"]
            if bean_type not in bean_types:
                bean_types[bean_type] = 0
            bean_types[bean_type] += batch["weight_kg"]
        
        # Group by processing stage
        stages = {}
        for batch in inventory:
            stage = batch["status"]
            if stage not in stages:
                stages[stage] = 0
            stages[stage] += batch["weight_kg"]
        
        return {
            "total_batches": total_batches,
            "total_weight": total_weight,
            "bean_types": bean_types,
            "stages": stages
        }
    except Exception as e:
        print(f"Error calculating inventory summary: {e}")
        return None

def calculate_processing_yields(inventory_path="bean_inventory.txt", processing_path="processing_records.txt"):
    """
    Calculates yield percentages through different processing stages.
    
    Args:
        inventory_path (str): Path to the inventory file
        processing_path (str): Path to the processing records file
        
    Returns:
        dict: Dictionary containing yield statistics by process type
    """
    try:
        records = read_processing_records(processing_path)
        
        # Group records by process type
        process_types = {}
        for record in records:
            process_type = record["process_type"]
            if process_type not in process_types:
                process_types[process_type] = []
            process_types[process_type].append(record)
        
        # Calculate statistics for each process type
        yields = {}
        
        for process_type, type_records in process_types.items():
            total_yield_pct = 0
            count = 0
            
            for record in type_records:
                # Find original weight from inventory
                batch_id = record["batch_id"]
                batch = find_batch_by_id(batch_id, inventory_path)
                
                if batch:
                    original_weight = batch["weight_kg"]
                    after_weight = record["weight_after"]
                    yield_pct = (after_weight / original_weight) * 100
                    
                    total_yield_pct += yield_pct
                    count += 1
            
            if count > 0:
                avg_yield = total_yield_pct / count
                
                yields[process_type] = {
                    "average_yield_percentage": round(avg_yield, 2),
                    "count": count
                }
        
        return yields
    except Exception as e:
        print(f"Error calculating processing yields: {e}")
        return {}

# Logging Functions
def log_operation(operation, details, log_file_path="operations_log.txt"):
    """
    Logs an operation to the log file with timestamp.
    
    Args:
        operation (str): Type of operation
        details (str): Details of the operation
        log_file_path (str): Path to the log file
        
    Returns:
        bool: True if the log was written successfully
    """
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"{timestamp},{operation},{details}\n"
        
        with open(log_file_path, "a") as f:
            f.write(log_entry)
        
        return True
    except Exception as e:
        print(f"Error logging operation: {e}")
        return False

def read_recent_logs(count=5, log_file_path="operations_log.txt"):
    """
    Retrieves the most recent log entries.
    
    Args:
        count (int): Number of log entries to retrieve
        log_file_path (str): Path to the log file
        
    Returns:
        list: List of the most recent log entries, with newest first
    """
    try:
        with open(log_file_path, "r") as f:
            lines = f.readlines()
        
        # Return the last 'count' lines in reverse order (newest first)
        recent_logs = []
        for line in lines[-count:]:  # Get the last 'count' lines
            parts = line.strip().split(",", 2)
            if len(parts) >= 3:
                log = {
                    "timestamp": parts[0],
                    "operation": parts[1],
                    "details": parts[2]
                }
                recent_logs.append(log)
        
        # Reverse to get newest first
        recent_logs.reverse()  # Add this line to reverse the order
        
        return recent_logs
    except FileNotFoundError:
        print(f"Log file not found: {log_file_path}")
        return []
    except Exception as e:
        print(f"Error reading logs: {e}")
        return []
    

def display_inventory_summary(summary):
    """
    Displays the inventory summary in a readable format.
    
    Args:
        summary (dict): Inventory summary dictionary
    """
    if not summary:
        print("No inventory data available.")
        return
    
    print("\n=== INVENTORY SUMMARY ===")
    print(f"Total Batches: {summary['total_batches']}")
    print(f"Total Weight: {summary['total_weight']:.1f} kg\n")
    
    print("By Bean Type:")
    for bean_type, weight in summary['bean_types'].items():
        percentage = (weight / summary['total_weight']) * 100
        print(f"{bean_type}: {weight:.1f} kg ({percentage:.1f}%)")
    
    print("\nBy Processing Stage:")
    for stage, weight in summary['stages'].items():
        percentage = (weight / summary['total_weight']) * 100
        print(f"{stage}: {weight:.1f} kg ({percentage:.1f}%)")

def main():
    """
    Main function demonstrating the coffee processing system.
    """
    print("===== COFFEE PROCESSING SYSTEM =====")
    
    # Create sample data if needed
    create_data = input("Create sample data? (y/n): ").lower()
    if create_data == 'y':
        if create_sample_data():
            print("Sample data created successfully.")
        else:
            print("Failed to create sample data.")
    
    while True:
        print("\nOptions:")
        print("1. View inventory summary")
        print("2. Add new batch")
        print("3. Record processing stage")
        print("4. View processing yields")
        print("5. View recent logs")
        print("0. Exit")
        
        choice = input("\nEnter option: ")
        
        if choice == '1':
            summary = calculate_inventory_summary()
            display_inventory_summary(summary)
            
        elif choice == '2':
            batch_id = input("Enter batch ID: ")
            date = input("Enter date (YYYY-MM-DD): ")
            farmer_id = input("Enter farmer ID: ")
            bean_type = input("Enter bean type: ")
            
            try:
                weight = float(input("Enter weight in kg: "))
                batch_data = {
                    "batch_id": batch_id,
                    "date": date,
                    "farmer_id": farmer_id,
                    "bean_type": bean_type,
                    "weight_kg": weight,
                    "status": "received"
                }
                
                if add_bean_batch(batch_data):
                    print("Batch added successfully.")
                else:
                    print("Failed to add batch.")
            except ValueError:
                print("Invalid weight value. Please enter a number.")
            
        elif choice == '3':
            batch_id = input("Enter batch ID: ")
            process_type = input("Enter process type (washing/drying/roasting): ")
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            
            try:
                weight_after = float(input("Enter weight after processing in kg: "))
                processing_data = {
                    "batch_id": batch_id,
                    "process_type": process_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "weight_after": weight_after
                }
                
                if record_processing_stage(processing_data):
                    print("Processing stage recorded successfully.")
                else:
                    print("Failed to record processing stage.")
            except ValueError:
                print("Invalid weight value. Please enter a number.")
            
        elif choice == '4':
            yields = calculate_processing_yields()
            
            if not yields:
                print("No processing yield data available.")
            else:
                print("\n=== PROCESSING YIELDS ===")
                for process_type, stats in yields.items():
                    print(f"{process_type.upper()}:")
                    print(f"  Average Yield: {stats['average_yield_percentage']}%")
                    print(f"  Number of Batches: {stats['count']}")
            
        elif choice == '5':
            logs = read_recent_logs()
            
            if not logs:
                print("No log entries found.")
            else:
                print("\n=== RECENT OPERATIONS ===")
                for log in logs:
                    print(f"{log['timestamp']} - {log['operation']} - {log['details']}")
            
        elif choice == '0':
            print("Exiting program. Goodbye!")
            break
            
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()