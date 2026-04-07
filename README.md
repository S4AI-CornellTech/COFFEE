# COFFEE: A Carbon-Modeling and Optimization Framework for HZO-based FeFET eNVMs

COFFEE is a  carbon modeling framework designed to enable carbon-aware design space exploration for hafnium–zirconium-oxide (HZO) Ferroelectric FET (FeFET) based on chip memory systems. Built upon the foundational methodology of ACT, this tool extends the analytical boundaries from standard CMOS to emerging ferroelectric technologies.

This framework bridges the gap between process-level parameters (e.g., ALD deposition rates, HZO thickness) and architecture-level metrics (e.g., area efficiency, dynamic energy from NVMExplorer), providing a holistic Life Cycle Analysis (LCA) for HZO FeFET hardware.



# Carbon modeling model

Central to this framework is an enhanced analytical model that estimates carbon emissions by combining the manufacturing overhead of the ferroelectric layer with baseline CMOS data.

We highlight the key governing equations from the COFFEE paper below:

1. Embodied Carbon 

To accurately model the manufacturing overhead, we adopt an area-weighted formulation. This separates the contributions from the conventional CMOS baseline and the FeFET-specific ferroelectric layers.

The total Energy Per Area (EPA) and Gas Per Area (GPA) for the FeFET process are calculated as:

$$EPA_{FeFET} = EPA_{CMOS} + EPA_{FE-layer} \cdot AE$$

$$GPA_{FeFET} = GPA_{CMOS} + GPA_{FE-layer} \cdot AE$$

Where:
$AE$ (Area Efficiency): The ratio of the ferroelectric deposition area (memory array) to the total chip area.

$EPA/GPA_{CMOS}$: Baseline metrics from standard logic processes (e.g., 28nm data from ACT).

$EPA/GPA_{FE-layer}$: The additional footprint derived specifically from the Atomic Layer Deposition (ALD) of HZO/Al2O3 stacks.

2. Lifetime & Operational CarbonTo complete the LCA, we combine the embodied carbon with operational energy:
Operational:

$$OP_{access} = CI_{location} \times Energy_{read/write}$$

$Lifetime: The effective lifespan is limited by NVM write endurance:

$$
  Lifetime = \frac{Endurance \cdot C_{mem}}{t_{write} \cdot W_{data}}
  $$

Where:
$C_{mem}$: The total capacity of the memory array.
$t_{write}$: The potential write traffic (number of write operations per day).
$W_{data}$: The array data width (size of each access).
$Endurance$: The intrinsic endurance limit of the specific FeFET device.

3. Architecture Metrics Extraction
To bridge the architecture-level simulations with our LCA model, we extract dynamic energy, latency, and area efficiency metrics directly from NVMExplorer outputs:

**Extraction:**
```bash
python src/nvm_utils.py --nvm_dir NVMExplorer/output/results --output inputs/nvm_output_example.csv

# File structure
```
.
│
├── archs/                          # 
│   ├── Cmos_logic/                 # Standard CMOS EPA/GPA data
│   ├── carbon_intensity/           # Prior Work: Global grid carbon intensity
│   └── fefet_extensions/           # Our Contribution: 
│       ├── fefet_ald.json          # ALD process parameters (HZO/Al2O3)
│       └── fefet_devices.json      # Database of specific FeFET device geometries
│
├── src/                            # 
│   ├── logic_model_HZO.py          # Extended model for HZO FeFET
│   ├── lifetime_HZO.py             # Lifetime model for HZO FeFET
│   ├── nvm_utils.py                # Result collection for NVMExplorer
│   └── model_HZO.py                # Embodied carboon calculation for HZO FeFET
│
└──inputs/                          # NVMExplorer output CSVs

```

# Getting Started

## Prerequisites


1. python 3.7
2. Pandas 2.3.3


## Usage 

Run the program using the command line:

```bash
python src/model_HZO.py
``` 

If you use this tool, please cite our work:

```
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

# License 
COFFEE is licensed under the MIT License.