# TabuLink Final Testing

## Windows PowerShell

From the project folder:

```powershell
# If .venv already exists:
.\.venv\Scripts\Activate.ps1

# If PowerShell blocks the script, use the venv Python directly instead:
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py runserver
```

If `.venv` does not exist, create it first:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

The final package does not include a virtual environment; `.venv` is machine-specific and should remain local.

## Final verification sequence

1. `manage.py check` must complete without traceback.
2. `manage.py test` must complete without URL/import errors.
3. Start the server and test login.
4. Test Coordinator verification and Verify All.
5. Test Administrator verification and Verify All.
6. Test sports finalization before equivalent points appear.
7. Test judging and Academic-Literary/Special finalization.
8. Test Public Results only after publication is enabled.
9. Resize browser through desktop, tablet, and phone widths; no horizontal page overflow or overlapping controls should occur. Tables may scroll horizontally inside their table containers when their required columns cannot fit.
