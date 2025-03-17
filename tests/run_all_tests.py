# Run Command: python Test_scripts/run_all_tests.py
import subprocess
import os
import sys

def run_test_script(script_name):
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True, env=os.environ)
    return result.returncode, result.stdout, result.stderr

def main():
    test_scripts = [
        'calibrate_gaze.py',
        'compute_transformation_matrix.py',
        'create_heatmap.py',
        'display_heatmap.py',
        'get_screen_resolution.py',
        'map_gaze_to_grid.py',
        'show_ad.py',
        'update_heatmap.py'
    ]

    results = []

    for script in test_scripts:
        returncode, stdout, stderr = run_test_script(script)
        results.append({
            'script': script,
            'status': 'Passed' if returncode == 0 else 'Failed',
            'output': stdout if returncode == 0 else stderr
        })

    with open('Test_Results.txt', 'w') as f:
        f.write(f"{'Script':<30} {'Status':<10} {'Output':<50}\n")
        f.write("="*90 + "\n")
        for result in results:
            f.write(f"{result['script']:<30} {result['status']:<10} {result['output']}\n")

if __name__ == "__main__":
    main()