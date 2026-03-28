import importlib
import os
import sys

REQUIRED_MODULES = ["streamlit", "google.generativeai"]


def check_modules() -> bool:
    all_ok = True
    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
            print(f"[OK] Module installed: {module}")
        except Exception:
            all_ok = False
            print(f"[MISSING] Module not found: {module}")
    return all_ok


def check_api_key() -> bool:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        print("[OK] GEMINI_API_KEY is set for this session.")
        return True
    print("[WARN] GEMINI_API_KEY is not set.")
    print("       Set it in PowerShell with:")
    print("       $env:GEMINI_API_KEY=\"your_api_key_here\"")
    return False


def print_next_steps(modules_ok: bool, key_ok: bool) -> int:
    if modules_ok and key_ok:
        print("\nSetup looks good. Run:")
        print("python -m streamlit run app.py")
        return 0

    print("\nNext steps:")
    if not modules_ok:
        print("1) Install dependencies:")
        print("   python -m pip install -r requirements.txt")
    if not key_ok:
        print("2) Set API key:")
        print("   $env:GEMINI_API_KEY=\"your_api_key_here\"")
    print("3) Start app:")
    print("   python -m streamlit run app.py")
    return 1


def main() -> int:
    print("Checking local setup for AI Shopping Assistant...\n")
    modules_ok = check_modules()
    key_ok = check_api_key()
    return print_next_steps(modules_ok, key_ok)


if __name__ == "__main__":
    sys.exit(main())
