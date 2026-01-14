import json
from logic_model_HZO import Fab_Logic  

# 1. Load the device thickness database
with open('logic/fefet_devices.json', 'r') as f:
    devices = json.load(f)

# 2. Select the device to analyze
device_to_test = 'HZO_5'
device_params = devices[device_to_test]

print(f"--- Analyzing {device_to_test} ---")

# 3 & 4. Create a Fab_Logic instance and pass the overridden thickness values
fab_model = Fab_Logic(
    process_node=28,
    carbon_intensity="loc_taiwan",
    debug=True,
    # Pass the thickness values obtained from HZO_5
    override_thickness_hzo=device_params["Thickness_HZO"],
    override_thickness_al2o3=device_params["Thickness_AI2O3"]
)

# The fab_model instance will now use the thickness values of HZO_5 for all calculations
print(f"\nTotal Carbon per Area for {device_to_test}: {fab_model.get_cpa():.4f} kgCO2e/cm²")
