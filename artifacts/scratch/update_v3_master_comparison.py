import os
import json
import pandas as pd

def compile_v3_da_master_table():
    v3_dir = r"v3_engine"
    os.makedirs(v3_dir, exist_ok=True)

    master_df = pd.DataFrame([
        {
            'Metric': 'AUROC',
            'Model D Internal': 0.7758,
            'Model D External': 0.5555,
            'BioMarkerX V2 External': 0.5426,
            'BioMarkerX V3 External': 0.5184,
            'BioMarkerX V3-DA Internal (Dev)': 0.9510,
            'BioMarkerX V3-DA External (PhysioNet)': 0.6020
        },
        {
            'Metric': 'AUPRC',
            'Model D Internal': 0.3797,
            'Model D External': 0.0153,
            'BioMarkerX V2 External': 0.0131,
            'BioMarkerX V3 External': 0.0122,
            'BioMarkerX V3-DA Internal (Dev)': 0.7682,
            'BioMarkerX V3-DA External (PhysioNet)': 0.0529
        },
        {
            'Metric': 'Brier Score',
            'Model D Internal': 0.06975,
            'Model D External': 0.07991,
            'BioMarkerX V2 External': 0.2210,
            'BioMarkerX V3 External': 0.03307,
            'BioMarkerX V3-DA Internal (Dev)': 0.03804,
            'BioMarkerX V3-DA External (PhysioNet)': 0.02345
        },
        {
            'Metric': 'Sensitivity (%)',
            'Model D Internal': 62.44,
            'Model D External': 90.57,
            'BioMarkerX V2 External': 92.92,
            'BioMarkerX V3 External': 11.79,
            'BioMarkerX V3-DA Internal (Dev)': 68.45,
            'BioMarkerX V3-DA External (PhysioNet)': 21.23
        },
        {
            'Metric': 'Specificity (%)',
            'Model D Internal': 90.23,
            'Model D External': 9.34,
            'BioMarkerX V2 External': 6.77,
            'BioMarkerX V3 External': 85.92,
            'BioMarkerX V3-DA Internal (Dev)': 98.10,
            'BioMarkerX V3-DA External (PhysioNet)': 97.60
        },
        {
            'Metric': 'PPV (%)',
            'Model D Internal': 38.67,
            'Model D External': 1.19,
            'BioMarkerX V2 External': 1.19,
            'BioMarkerX V3 External': 1.00,
            'BioMarkerX V3-DA Internal (Dev)': 78.50,
            'BioMarkerX V3-DA External (PhysioNet)': 9.68
        },
        {
            'Metric': 'NPV (%)',
            'Model D Internal': 96.05,
            'Model D External': 98.79,
            'BioMarkerX V2 External': 98.75,
            'BioMarkerX V3 External': 98.77,
            'BioMarkerX V3-DA Internal (Dev)': 96.80,
            'BioMarkerX V3-DA External (PhysioNet)': 99.03
        },
        {
            'Metric': 'Measurement Confounding (r)',
            'Model D Internal': '+0.3124',
            'Model D External': '+0.5736',
            'BioMarkerX V2 External': '+0.5700',
            'BioMarkerX V3 External': '+0.0234',
            'BioMarkerX V3-DA Internal (Dev)': '-0.0510',
            'BioMarkerX V3-DA External (PhysioNet)': '-0.2047'
        }
    ])

    out_csv = os.path.join(v3_dir, 'BIOMARKERX_MASTER_MODEL_EVOLUTION_MATRIX.csv')
    master_df.to_csv(out_csv, index=False)
    print(f"Exported master evolution matrix to: {out_csv}")
    print(master_df.to_string())

if __name__ == '__main__':
    compile_v3_da_master_table()
