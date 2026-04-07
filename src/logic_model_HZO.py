# Copyright (c) Meta Platforms, Inc. and affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# MODIFIED to include FeFET ALD process energy calculations
# MODIFIED to load FeFET parameters from a JSON config file.
# MODIFIED to accept thickness overrides for HZO and AI2O3
# NOTE: FeFET area efficiency is loaded directly from fefet_ald.json. 
#       Users can modify this value in the JSON file directly using 
#       the extraction results from NVMExplorer for specific configurations.

import json
import sys
import os

class Fab_Logic():
    def __init__(self, process_node=28,
                       gpa="97",
                       carbon_intensity="loc_taiwan",
                       debug=False,
                       fab_yield=0.875,
                       fefet_config_path=None, 
                       override_thickness_hzo=None,  
                       override_thickness_al2o3=None   
                       ):

        self.debug = debug

        # Set up dynamic paths based on the new project structure
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
        ARCHS_DIR = os.path.join(PROJECT_ROOT, 'archs')
        
        if fefet_config_path is None:
            fefet_config_path = os.path.join(ARCHS_DIR, 'fefet_extensions', 'fefet_ald.json')

        ###############################
        # Energy per unit area (CMOS)
        ###############################
        with open(os.path.join(ARCHS_DIR, 'CMOS_logic', 'epa.json'), 'r') as f:
            epa_config = json.load(f)

        ###############################
        # Raw materials per unit area (CMOS)
        ###############################
        with open(os.path.join(ARCHS_DIR, 'CMOS_logic', 'materials.json'), 'r') as f:
            materials_config = json.load(f)

        ###############################
        # Gasses per unit area (CMOS)
        ###############################
        gpa_dir = os.path.join(ARCHS_DIR, 'CMOS_logic')
        if gpa == "95":
            with open(os.path.join(gpa_dir, 'gpa_95.json'), 'r') as f:
                gpa_config = json.load(f)
        elif gpa == "99":
            with open(os.path.join(gpa_dir, 'gpa_99.json'), 'r') as f:
                gpa_config = json.load(f)
        elif gpa == "97":
            with open(os.path.join(gpa_dir, 'gpa_95.json'), 'r') as f:
                gpa_95_config = json.load(f)
            with open(os.path.join(gpa_dir, 'gpa_99.json'), 'r') as f:
                gpa_99_config = json.load(f)

            gpa_config = {}
            for c in gpa_95_config.keys():
                gas = (gpa_95_config[c] + gpa_99_config[c]) / 2.
                gpa_config[c] = gas
        else:
            print("Error: Unsupported GPA value for FAB logic")
            sys.exit()
            
        ###############################
        # FeFET ALD Parameters (Loaded from JSON)
        ###############################
        try:
            with open(fefet_config_path, 'r') as f:
                fefet_config = json.load(f)
        except FileNotFoundError:
            print(f"Error: FeFET config file not found at {fefet_config_path}")
            sys.exit()
        except json.JSONDecodeError:
            print(f"Error: Failed to parse JSON in {fefet_config_path}")
            sys.exit()

        ###############################
        # Carbon intensity of fab
        ###############################
        ci_dir = os.path.join(ARCHS_DIR, 'carbon_intensity')
        if "loc" in carbon_intensity:
            with open(os.path.join(ci_dir, 'location.json'), 'r') as f:
                loc_configs = json.load(f)
            loc = carbon_intensity.replace("loc_", "")
            assert loc in loc_configs.keys()
            fab_ci = loc_configs[loc]

        elif "src" in carbon_intensity:
            with open(os.path.join(ci_dir, 'source.json'), 'r') as f:
                src_configs = json.load(f)
            src = carbon_intensity.replace("src_", "")
            assert src in src_configs.keys()
            fab_ci = src_configs[src]
        else:
            print("Error: Carbon intensity must either be loc | src dependent")
            sys.exit()

        ###############################
        # Energy per unit area (Ferroelectric Layer - FEL)
        ###############################
        
        # Check for thickness overrides
        thickness_hzo = override_thickness_hzo if override_thickness_hzo is not None else fefet_config['Thickness_HZO']
        thickness_al2o3 = override_thickness_al2o3 if override_thickness_al2o3 is not None else fefet_config['Thickness_AI2O3']

        if self.debug and (override_thickness_hzo is not None or override_thickness_al2o3 is not None):
            print(f"[Fab Logic] Overriding thickness. HZO: {thickness_hzo} (was {fefet_config['Thickness_HZO']}), AI2O3: {thickness_al2o3} (was {fefet_config['Thickness_AI2O3']})")

        # Use the (potentially overridden) thickness values in calculations
        Time_AI2O3 = (thickness_al2o3 / fefet_config['RateAI2O3']) * fefet_config['CycleTime_AI2O3']
        Time_HZO = (thickness_hzo / fefet_config['RateHZO']) * fefet_config['CycleTime_HZO']
        
        total_ald_process_time = Time_AI2O3 + Time_HZO + fefet_config['PreheatTime'] + fefet_config['StableTime']
        
        # Power for ALD process (AI2O3, HZO) and stable process is 'ALD_Power_Stable'
        process_energy_kwh = (fefet_config['ALD_Power_Preheat'] * fefet_config['PreheatTime'] +
                              (Time_AI2O3 + Time_HZO + fefet_config['StableTime']) * fefet_config['ALD_Power_Stable']) / 3600.0

        # Changed to fel_total_energy_kwh
        self.fel_total_energy_kwh = process_energy_kwh / fefet_config['tool_efficiency'] / fefet_config['fab_overhead_factor']
        
        # Changed to fel_epa
        fel_epa = self.fel_total_energy_kwh / fefet_config['Area_Wafer']  # (kWh / cm^2)


        ###############################
        # Aggregating model (CMOS + FEL = FeFET)
        ###############################
        process_node_str = str(process_node) + "nm"
        assert process_node_str in epa_config.keys()
        assert process_node_str in gpa_config.keys()
        assert process_node_str in materials_config.keys()

        cmos_epa = epa_config[process_node_str]
        cmos_gpa = gpa_config[process_node_str]
        cmos_materials = materials_config[process_node_str]

        # Use fefet_area_efficiency directly from fefet_config. 
        # Changed total_epa_die to self.fefet_epa
        self.fefet_epa = cmos_epa + (fel_epa * fefet_config['fefet_area_efficiency'])

        carbon_energy    = fab_ci * self.fefet_epa
        carbon_gas       = cmos_gpa
        carbon_materials = cmos_materials

        self.carbon_per_area = (carbon_energy + carbon_gas + carbon_materials)
        self.carbon_per_area = self.carbon_per_area / fab_yield

        if self.debug:
            print("--- [Fab Logic Debug] ---")
            print(f"[Fab CMOS] Process Node: {process_node_str}")
            print(f"[Fab CMOS] EPA (die): {cmos_epa:.4f} kWh/cm²")
            print(f"[Fab FEL] Area Efficiency: {fefet_config['fefet_area_efficiency']:.4f}")
            print(f"[Fab FEL] AI2O3 Deposition Time: {Time_AI2O3:.2f} s")
            print(f"[Fab FEL] HZO Deposition Time: {Time_HZO:.2f} s")
            print(f"[Fab FEL] Total ALD Process Time: {total_ald_process_time:.2f} s")
            print(f"[Fab FEL] Total ALD Energy (fab): {self.fel_total_energy_kwh:.4f} kWh")
            print(f"[Fab FEL] FEL EPA (wafer): {fel_epa:.4f} kWh/cm²")
            print(f"[Fab Aggregate] FeFET EPA (scaled, die): {self.fefet_epa:.4f} kWh/cm²")
            print("--- [Carbon Breakdown (per die area, pre-yield)] ---")
            print(f"[Fab Carbon] Energy: {carbon_energy:.4f} kgCO2e/cm²")
            print(f"[Fab Carbon] Gas: {carbon_gas:.4f} kgCO2e/cm²")
            print(f"[Fab Carbon] Materials: {carbon_materials:.4f} kgCO2e/cm²")
            print("--- [Final Output] ---")
            print(f"[Fab Logic] Carbon/area aggregate (post-yield): {self.carbon_per_area:.4f} kgCO2e/cm²")

        self.carbon = 0
        return


    def get_cpa(self):
        """Returns the total carbon per unit area (kgCO2e/cm^2)."""
        return self.carbon_per_area

    def set_area(self, area):
        """Sets the die area and calculates the total carbon for that die."""
        self.area = area
        self.carbon = self.area * self.carbon_per_area

    def get_carbon(self):
        """Returns the total carbon (kgCO2e) for the set area."""
        return self.carbon

    def get_fefet_epa(self):
        """Returns the total combined EPA (CMOS + FEL) per die area."""
        return self.fefet_epa

    def get_fel_energy(self):
        """Returns the total fab energy (kWh) for the FEL ALD step."""
        return self.fel_total_energy_kwh