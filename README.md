# Network Reliability Optimization Model

This project implements mathematical optimization models for network reliability analysis using different topologies. The models are designed to minimize deployment costs while meeting reliability requirements using Gurobi optimization solver.

## 🚀 Quick Start

```bash
# 1. Ensure Gurobi license is properly configured
# 2. Install dependencies (gurobipy, matplotlib, pandas, numpy)
# 3. Run complete analysis
python main.py

# 4. View results in the Figures/ directory
```

## 📁 Project Structure

```
optimization_model/
├── Models/                    # Optimization model implementations
│   ├── base_model.py         # Base optimization model with binary variables
│   ├── series_model.py       # Series topology model
│   ├── mesh_model.py         # Mesh topology model (high redundancy)
│   └── hybrid_model.py       # Hybrid topology model (series + mesh subnets)
├── utils/                     # Utility functions and plotting
│   ├── utils.py              # Data processing, plotting, and advanced visualizations
│   └── validation.py         # Input validation functions
├── config.py                  # Configuration parameters and analysis settings
├── main.py                    # Main execution script with standard and high reliability analysis
├── examples.py                # Custom analysis examples and usage patterns
├── main.ipynb                 # Jupyter notebook for interactive analysis
├── DIRECTORY_STRUCTURE.md     # Documentation of output directory organization
└── README.md                  # This file
```

## 🏗️ Network Topologies

### 1. Series Topology
- **Configuration**: Nodes connected in series (sequential)
- **Reliability**: Product of individual node reliabilities
- **Cost**: Lower due to minimal links
- **Use Case**: Cost-sensitive applications with acceptable reliability trade-offs

### 2. Mesh Topology
- **Configuration**: Nodes with multiple redundant connections
- **Reliability**: High due to path redundancy (1 - product of unreliabilities)
- **Cost**: Higher due to additional links
- **Use Case**: Mission-critical applications requiring high reliability

### 3. Hybrid Topology
- **Configuration**: Combination of series and mesh subnets
- **Reliability**: Complex calculation balancing both topologies
- **Cost**: Balanced between series and mesh
- **Use Case**: Applications requiring reliability optimization with cost constraints

## 🔧 Analysis Types

### Standard Analysis
- **Reliability Range**: 0.5 to 0.9999999999999999
- **Samples**: 200 points per topology
- **Purpose**: Complete overview of all topologies across full reliability spectrum
- **Execution Time**: ~3-5 minutes (depending on hardware)

### High Reliability Analysis
- **Reliability Range**:
  - Series: 0.5 to 0.9999999999999999 (full range)
  - Mesh: 0.99998 to 0.9999999999999999 (focused)
  - Hybrid: 0.99998 to 0.9999999999999999 (focused)
- **Samples**: 50 points for mesh/hybrid (75% faster)
- **Purpose**: Detailed analysis for mission-critical applications
- **Execution Time**: ~2-3 minutes

## 📊 Output Structure

Results are automatically organized in the `Figures/` directory:

```
Figures/
├── standard/                          # Standard Analysis Results
│   ├── jointTopologies/               # All topologies compared per node count
│   ├── NodesJointByTopology/          # Node counts compared per topology
│   └── individual_topologies/         # Individual topology results
│       ├── Series/
│       ├── Mesh/
│       └── Hybrid/
└── high_reliability/                  # High Reliability Analysis Results  
    ├── NodesJointByTopology/          # Focused high reliability comparisons
    └── individual_topologies/         # Individual high reliability results
        ├── Series/
        ├── Mesh/
        └── Hybrid/
```

## ⚙️ Configuration & Customization

### Basic Configuration (`config.py`)

```python
# Node costs (in SCU - Standard Cost Units)
COST_BY_NODE_TYPE = {
    0: 24.2,    # Low reliability node
    1: 91.82,   # Medium reliability node  
    2: 227.06   # High reliability node
}

# Node reliabilities
RELIABILITY_BY_NODE_TYPE = [0.9, 0.95, 0.99]

# Link cost
LINK_COST = 7.69

# Analysis settings
DEFAULT_NODE_COUNTS = [5, 6, 11]           # Node counts to analyze
NUM_EQUIDISTANT_VALUES = 200               # Samples for standard analysis
NUM_HIGH_RELIABILITY_VALUES = 50           # Samples for high reliability analysis
```

### 🎯 How to Run Custom Tests

#### 1. **Modify Node Counts**
```python
# In config.py, change:
DEFAULT_NODE_COUNTS = [4, 5, 6, 7, 8]  # Test different network sizes
```

#### 2. **Adjust Analysis Precision**
```python
# In config.py:
NUM_EQUIDISTANT_VALUES = 100        # Faster execution, less precision
NUM_HIGH_RELIABILITY_VALUES = 25    # Even faster high reliability analysis
```

#### 3. **Customize Reliability Ranges**
```python
# In config.py:
SERIES_RELIABILITY_RANGE = (0.6, 0.95)              # Focus on mid-range
HIGH_RELIABILITY_MESH_RANGE = (0.999, MAX_RELIABILITY)  # Ultra-high reliability
```

#### 4. **Run Specific Analysis Types**
```python
# Run only standard analysis
from main import run_standard_analysis
run_standard_analysis([4, 5, 6])

# Run only high reliability analysis  
from main import run_high_reliability_analysis
run_high_reliability_analysis([6, 8, 10])
```

#### 5. **Custom Analysis Examples**
```python
# Run examples.py for advanced patterns
python examples.py

# Or create custom analysis:
from examples import single_topology_analysis
single_topology_analysis("mesh", [4, 6, 8], (0.95, 0.99))
```

### 🔬 Advanced Customization

#### Custom Cost Functions
Modify `COST_BY_NODE_TYPE` and `LINK_COST` in `config.py` to test different economic scenarios:

```python
# High-cost scenario
COST_BY_NODE_TYPE = {0: 50, 1: 150, 2: 350}
LINK_COST = 15

# Low-cost scenario  
COST_BY_NODE_TYPE = {0: 10, 1: 40, 2: 100}
LINK_COST = 3
```

#### Custom Reliability Requirements
```python
# Ultra-reliable nodes
RELIABILITY_BY_NODE_TYPE = [0.95, 0.98, 0.999]

# Lower reliability nodes (cost-focused)
RELIABILITY_BY_NODE_TYPE = [0.85, 0.90, 0.95]
```

## 🧮 Model Formulation

### Decision Variables
- **x[u,i]**: Binary variable (1 if node u uses type i, 0 otherwise)
- **y[u,j]**: Binary variable for hybrid model subnet assignment

### Objective Function
```
Minimize: Σ(node_costs) + Σ(link_costs)
```

### Constraints
1. **Node Uniqueness**: Each node must have exactly one type
2. **Reliability Requirements**: Network reliability ≥ required reliability
3. **Topology-Specific**: Additional constraints per topology type

## 📈 Usage Examples

### Basic Usage
```python
# Complete analysis with default settings
python main.py
```

### Custom Node Analysis
```python
from main import run_standard_analysis
from config import DEFAULT_NODE_COUNTS

# Test with different node counts
custom_nodes = [4, 7, 9, 12]
run_standard_analysis(custom_nodes)
```

### Single Topology Focus
```python
from Models.base_model import base_model
from Models.mesh_model import mesh_model

# Analyze specific scenario
base = base_model(6)
cost, variables, model = mesh_model(base, 6, 0.95)
print(f"Cost for 6-node mesh with 95% reliability: {cost}")
```

### Performance Testing
```python
# Quick test with reduced samples
# In config.py, set:
NUM_EQUIDISTANT_VALUES = 50
NUM_HIGH_RELIABILITY_VALUES = 20
# Then run: python main.py
```

## 🔧 Dependencies

```bash
pip install gurobipy matplotlib pandas numpy
```

**Note**: Gurobi requires a valid license. Academic licenses are available for free.

## 📝 Output Interpretation

### Cost vs Reliability Plots
- **X-axis**: Required reliability (0.5 to 0.999...)
- **Y-axis**: Minimized cost (SCU)
- **Curves**: Show optimal cost for each reliability level

### Topology Comparisons
- **Series**: Steep cost increase at high reliability
- **Mesh**: More gradual cost increase, better for high reliability
- **Hybrid**: Balanced performance between series and mesh

### Node Count Analysis
- Higher node counts generally increase cost
- Redundancy benefits more apparent with more nodes
- Optimal topology choice may vary by network size

## 🚨 Troubleshooting

### Common Issues
1. **Gurobi License Error**: Ensure license file is properly configured
2. **Long Execution Time**: Reduce sample counts in config.py
3. **Memory Issues**: Reduce node counts or use fewer samples
4. **Plot Generation Errors**: Check matplotlib backend and permissions

### Performance Optimization
```python
# Fast testing configuration
NUM_EQUIDISTANT_VALUES = 25
NUM_HIGH_RELIABILITY_VALUES = 10
DEFAULT_NODE_COUNTS = [4, 5]
```

## 📜 License

This project is part of academic research on network optimization and reliability analysis. Developed for thesis research in network reliability optimization.