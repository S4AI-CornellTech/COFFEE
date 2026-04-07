import json
import os
import sys

# Add the project root to the system path to ensure relative imports work correctly
# Assuming this script is located in COFFEE/src/
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.logic_model_HZO import Fab_Logic  

def main():
    # 1. Define the path to the device thickness database based on the new structure
    db_path = os.path.join(project_root, 'archs', 'fefet_extensions', 'fefet_devices.json')

    # Load the JSON file
    try:
        with open(db_path, 'r') as f:
            devices = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the device database at {db_path}.")
        print("Please ensure your project structure is set up correctly.")
        sys.exit(1)

    # 2. Select the specific FeFET device configuration to analyze
    device_to_test = 'HZO_5'
    
    if device_to_test not in devices:
        print(f"Error: Device '{device_to_test}' not found in the database.")
        sys.exit(1)
        
    device_params = devices[device_to_test]

    print(f"--- Analyzing Configuration: {device_to_test} ---")

    # 3. Create a Fab_Logic instance
    # Note: Area efficiency is automatically loaded from fefet_ald.json by default.
    fab_model = Fab_Logic(
        process_node=28,
        carbon_intensity="loc_taiwan",
        debug=True, # Set to False if you want to hide the detailed process breakdown
        # Pass the thickness values obtained from the specific device (e.g., HZO_5)
        override_thickness_hzo=device_params["Thickness_HZO"],
        override_thickness_al2o3=device_params["Thickness_AI2O3"]
    )

    # 4. Output the final aggregated results
    # Utilizing the updated, clearer terminology (FEL and FeFET)
    print("\n================ Final Carbon Report ================")
    print(f"Target Device        : {device_to_test}")
    print(f"FEL Process Energy   : {fab_model.get_fel_energy():.4f} kWh")
    print(f"Total EPA (CMOS+FEL) : {fab_model.get_fefet_epa():.4f} kWh/cm²")
    print(f"Total Carbon per Area: {fab_model.get_cpa():.4f} kgCO2e/cm²")
    print("=====================================================")

if __name__ == "__main__":
    main()