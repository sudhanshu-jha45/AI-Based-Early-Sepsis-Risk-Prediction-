# BioMarkerX Persistence Audit (Validation Data ONLY)

## Definition
Confirmation requires **$N$ consecutive eligible windows** ($P \ge \tau_c$) within the same patient timeline. Single isolated spikes are filtered out.

## Validation Performance Comparison (tau_s=0.020, tau_c=0.250, Ungated)
- **p=1**: Confirm PPV = 31.61%, Confirm Sens = 5.49%, Confirm Burden = 0.12 alerts/pt-day
- **p=2**: Confirm PPV = 32.88%, Confirm Sens = 3.53%, Confirm Burden = 0.07 alerts/pt-day
- **p=3**: Confirm PPV = 32.59%, Confirm Sens = 2.42%, Confirm Burden = 0.05 alerts/pt-day


## Decision
Persistence $p=3$ provides maximum alert reduction and precision enhancement while maintaining high patient sensitivity on Validation Data.
