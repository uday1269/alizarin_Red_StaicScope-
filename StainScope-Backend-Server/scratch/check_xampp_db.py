import os

xampp_data = r"C:\xampp\mysql\data"
print("XAMPP data dir exists:", os.path.exists(xampp_data))
if os.path.exists(xampp_data):
    print("Databases in XAMPP:", os.listdir(xampp_data))
