
# COFFEE: A Carbon-Modeling and Optimization Framework for HZO-based FeFET eNVMs

**COFFEE** is a carbon modeling framework designed to enable carbon-aware design space exploration for hafnium–zirconium-oxide (HZO) Ferroelectric FET (FeFET) based on-chip memory systems. Built upon the foundational methodology of **ACT**, this tool extends analytical boundaries from standard CMOS to emerging ferroelectric technologies.

This framework bridges the gap between **process-level parameters** (e.g., ALD deposition rates, HZO thickness) and **architecture-level metrics** (e.g., area efficiency, dynamic energy), providing a holistic Life Cycle Analysis (LCA) for HZO FeFET hardware.

---

## 1. Carbon Modeling Methodology

Central to this framework is an enhanced analytical model that estimates carbon emissions by combining the manufacturing overhead of the ferroelectric layer with baseline CMOS data.

### A. Embodied Carbon 
To accurately model manufacturing overhead, we adopt an area-weighted formulation that separates conventional CMOS contributions from FeFET-specific ferroelectric layers:

$$EPA_{FeFET} = EPA_{CMOS} + EPA_{FE-layer} \cdot AE$$
$$GPA_{FeFET} = GPA_{CMOS} + GPA_{FE-layer} \cdot AE$$

**Where:**
* **$AE$ (Area Efficiency):** The ratio of the ferroelectric deposition area (memory array) to the total chip area.
* **$EPA/GPA_{CMOS}$:** Baseline metrics from standard logic processes (e.g., 28nm data from ACT).
* **$EPA/GPA_{FE-layer}$:** The additional footprint derived from the Atomic Layer Deposition (ALD) of HZO/Al2O3 stacks.

### B. Lifetime Analysis 
The lifetime for HZO FeFET is limited by device write endurance:

$$Lifetime = \frac{Endurance \cdot C_{mem}}{t_{write} \cdot W_{data}}$$

**Where:**
* **$C_{mem}$:** The total capacity of the memory array.
* **$t_{write}$:** Potential write traffic (number of write operations per day).
* **$W_{data}$:** The array data width (size of each access).
* **$Endurance$:** The intrinsic endurance limit of the specific FeFET device.

---

## 2. Architecture Metrics Extraction

To bridge architecture-level simulations with our LCA model, we extract dynamic energy, latency, and area efficiency metrics directly from NVMExplorer outputs.

**Run Extraction Script:**
```bash
python src/nvm_utils.py --nvm_dir NVMExplorer/output/results --output inputs/nvm_output_example.csv
```

---

## 3. File Structure

```text
.
├── archs/                          # Hardware Configuration Data
│   ├── CMOS_logic/                 # Standard CMOS EPA/GPA data (from ACT)
│   ├── carbon_intensity/           # Global grid carbon intensity data
│   └── fefet_extensions/           # FeFET-specific process extensions
│       ├── fefet_ald.json          # ALD process parameters (HZO/Al2O3)
│       └── fefet_devices.json      # Database of FeFET device geometries
│
├── src/                            # Source Code
│   ├── logic_model_HZO.py          # Extended carbon model for HZO FeFET
│   ├── lifetime_HZO.py             # Operational lifetime calculator
│   ├── nvm_utils.py                # Result collector for NVMExplorer
│   └── model_HZO.py                # Main embodied carbon calculation
│
└── inputs/                         # Formatted NVMExplorer output CSVs
```

---

## 4. Getting Started

### Prerequisites
* **Python:** 3.7+
* **Pandas:** 2.3.3+

### Usage 
To analyze the carbon footprint of a specific FeFET configuration, run the following command from the project root:

```bash
python src/model_HZO.py
``` 

---

## 5. Citation

If you use this tool in your research, please cite our work:

```bibtex
@misc{wu2026coffee,
  title={COFFEE: A Carbon-Modeling and Optimization Framework for HZO-based FeFET eNVMs},
  author={Hongbang Wu and Xuesi Chen and Shubham Jadhav and Amit Lal and Lillian Pentecost and Udit Gupta},
  year={2026},
  eprint={2602.05018},
  archivePrefix={arXiv},
  primaryClass={cs.AR},
  url={[https://doi.org/10.48550/arXiv.2602.05018](https://doi.org/10.48550/arXiv.2602.05018)}
}
```

---

## License 
COFFEE is licensed under the **MIT License**.
