import os
import glob
import time
import pandas as pd

def inspect_scripts_timeframe():
    py_files = glob.glob('scratch/*.py')
    records = []
    for f in py_files:
        mtime = os.path.getmtime(f)
        mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        records.append({
            'file': f,
            'mtime': mtime_str,
            'timestamp': mtime
        })
    df = pd.DataFrame(records).sort_values(by='timestamp')
    print("Scratch scripts sorted by modification time:")
    print(df.to_string())

if __name__ == '__main__':
    inspect_scripts_timeframe()
