import os
import sys
import subprocess
from pathlib import Path

def test_import(env_vars=None):
    if env_vars:
        for k, v in env_vars.items():
            os.environ[k] = v
            print(f"Setting {k}={v}")
    
    print(f"\nAttempting to import torch with environment: {env_vars}")
    try:
        import torch
        print(f"✅ SUCCESS: Torch imported successfully!")
        print(f"Torch version: {torch.__version__}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("--- Torch Import Diagnostic ---")
    print(f"Python Version: {sys.version}")
    
    # Check for c10.dll
    try:
        import torch
        torch_path = Path(torch.__file__).parent
    except:
        # Fallback to manual path check since import fails
        torch_path = Path(sys.executable).parent.parent / "Lib" / "site-packages" / "torch"
    
    c10_dll = torch_path / "lib" / "c10.dll"
    print(f"Looking for c10.dll at: {c10_dll}")
    if c10_dll.exists():
        print(f"✅ c10.dll exists (Size: {c10_dll.stat().st_size} bytes)")
    else:
        print(f"❌ c10.dll is MISSING!")

    # Test 1: Empty string fix
    if not test_import({"CUDA_VISIBLE_DEVICES": ""}):
        # Test 2: MKL Force fix
        if not test_import({"MKL_SERVICE_FORCE_INTEL": "1"}):
            # Test 3: Disable all GPU/MKL/OpenMP variables
            test_import({
                "CUDA_VISIBLE_DEVICES": "",
                "MKL_DEBUG_CPU_TYPE": "5",
                "OMP_NUM_THREADS": "1"
            })
