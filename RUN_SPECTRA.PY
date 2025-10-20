# Installera beroenden
pip install -r requirements.txt

# Kör tester
python test_spectra.py
python test_aeprs_integration.py

# Eller använd pytest
pytest tests/ -v