# Navigation Systems Exercises

This workspace contains a simple NMEA parsing library `NavSysLib` used in the
course exercises.  

## Using `NavSysLib` as a library

You have three main options:

1. **Run scripts from the workspace root**. Python automatically finds
   `NavSysLib` if the current working directory is the root of the repository:
   ```bash
   cd "c:/Users/magnu/OneDrive/Studie/Elsys/8. Semester/Navigation Systems/Exercises"
   python -m E1.E1  # or python E1/E1.py
   ```

2. **Install the package in editable mode** with pip. This makes
   `import NavSysLib` available anywhere on your system and keeps the
   code editable:
   ```bash
   pip install -e .
   # later you can uninstall with `pip uninstall NavSysLib`
   ```
   (requires the `setup.py` file in the workspace root, which is already
   provided.)

3. **Add the workspace to `PYTHONPATH`** or modify `sys.path` manually from
   your script, e.g.:
   ```python
   import sys
   sys.path.insert(0, r"c:/Users/magnu/OneDrive/Studie/Elsys/8. Semester/Navigation Systems/Exercises")
   import NavSysLib
   ```

Option 2 is the most robust for treating the code as a reusable library.

Once installed or importable, you can do:

```python
from NavSysLib import NMEALog, GGASentence, safe_float
```

and the package will be available wherever your Python environment is active.
