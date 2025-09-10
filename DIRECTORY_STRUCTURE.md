# Directory Structure for Figures

After running the analysis, the following directory structure will be created:

```
Figures/
├── standard/                          # Standard Analysis (0.5 to 0.9999999...)
│   ├── jointTopologies/               # All topologies on same graph per node count
│   │   ├── CostVsReliability_5nodes.png
│   │   ├── CostVsReliability_6nodes.png
│   │   └── CostVsReliability_11nodes.png
│   │
│   ├── NodesJointByTopology/          # Different node counts on same graph per topology
│   │   ├── series/
│   │   │   └── costVsReliability_series.png
│   │   ├── mesh/
│   │   │   └── costVsReliability_mesh.png
│   │   └── hybrid/
│   │       └── costVsReliability_hybrid.png
│   │
│   └── individual_topologies/         # Individual plots by topology
│       ├── Series/
│       │   ├── costVsReliability_Series_5.png
│       │   ├── costVsReliability_Series_6.png
│       │   ├── costVsReliability_Series_11.png
│       │   └── stacked_Series.png     # (if generated)
│       ├── Mesh/
│       │   ├── costVsReliability_Mesh_5.png
│       │   ├── costVsReliability_Mesh_6.png
│       │   ├── costVsReliability_Mesh_11.png
│       │   └── stacked_Mesh.png       # (if generated)
│       └── Hybrid/
│           ├── costVsReliability_Hybrid_5.png
│           ├── costVsReliability_Hybrid_6.png
│           ├── costVsReliability_Hybrid_11.png
│           └── stacked_Hybrid.png     # (if generated)
│
└── high_reliability/                  # High Reliability Analysis (0.99998 to 0.9999999...)
    ├── NodesJointByTopology/          # Different node counts on same graph per topology
    │   ├── series/
    │   │   └── costVsReliability_series.png
    │   ├── mesh/
    │   │   ├── costVsReliability_mesh.png
    │   │   └── costVsReliability_mesh_zoom.png    # (if zoom function is used)
    │   └── hybrid/
    │       ├── costVsReliability_hybrid.png
    │       └── costVsReliability_hybrid_zoom.png  # (if zoom function is used)
    │
    └── individual_topologies/         # Individual plots by topology (high reliability focus)
        ├── Series/
        │   ├── costVsReliability_Series_5.png
        │   ├── costVsReliability_Series_6.png
        │   ├── costVsReliability_Series_11.png
        │   └── stacked_Series.png     # (if generated)
        ├── Mesh/
        │   ├── costVsReliability_Mesh_5.png     # (focused on 0.99998+)
        │   ├── costVsReliability_Mesh_6.png
        │   ├── costVsReliability_Mesh_11.png
        │   └── stacked_Mesh.png       # (if generated)
        └── Hybrid/
            ├── costVsReliability_Hybrid_5.png   # (focused on 0.99998+)
            ├── costVsReliability_Hybrid_6.png
            ├── costVsReliability_Hybrid_11.png
            └── stacked_Hybrid.png     # (if generated)
```

## Key Benefits of This Structure:

1. **Clear Separation**: Standard vs High Reliability analysis results are completely separated
2. **Logical Grouping**: 
   - `jointTopologies/`: Compare all topologies for each node count
   - `NodesJointByTopology/`: Compare node counts for each topology 
   - `individual_topologies/`: Individual analysis per topology and node count
3. **Easy Navigation**: Find specific analysis results quickly
4. **Scalable**: Easy to add new analysis types or topologies
5. **Self-Documenting**: Directory names clearly indicate content type

## Analysis Types:

- **Standard Analysis**: Full range (0.5 to 0.9999999...) with 200 samples
- **High Reliability Analysis**: Focused range (0.99998 to 0.9999999...) with 50 samples for mesh/hybrid

Note: High reliability analysis doesn't generate jointTopologies plots since series topology 
becomes impractical at very high reliability requirements.
