from flask import Flask, request, redirect, url_for, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import os, csv
import plotly.express as px
import folium
from datetime import timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = "Group7"
app.permanent_session_lifetime = timedelta(hours=2)


# --- File Paths ---
USER_FILE = "users.csv"
MINERAL_FILE = "minerals.csv"
DEPOSITS_FILE = "sites.csv"
COUNTRY_FILE = "countries.csv"
PROD_TS_FILE = "production_stats.csv"
ROLES_FILE = "roles.csv"

# --- Ensure CSVs Exist ---
def ensure_csv(filename, header, default_rows=None):
    if not os.path.exists(filename):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            if default_rows:
                writer.writerows(default_rows)

# Initialize files with comprehensive African mineral data
ensure_csv(
    ROLES_FILE,
    ["RoleID", "RoleName", "Permissions"],
    [
        ["1", "Administrator", "all"],
        ["2", "Investor", "market_data,charts"],
        ["3", "Researcher", "view_data,charts"]
    ]
)

ensure_csv(USER_FILE, ["UserID","Username","PasswordHash","RoleID","Email"])
ensure_csv(MINERAL_FILE, ["MineralID","MineralName","Description","MarketPriceUSD_per_tonne"])
ensure_csv(DEPOSITS_FILE, ["SiteID","SiteName","CountryID","MineralID","Latitude","Longitude","Production_tonnes"])
ensure_csv(COUNTRY_FILE, ["CountryID","CountryName","GDP_BillionUSD","MiningRevenue_BillionUSD","KeyProjects","Population_Millions","MiningContribution_GDP"])
ensure_csv(PROD_TS_FILE, ["StatID","Year","CountryID","MineralID","Production_tonnes","ExportValue_BillionUSD"])

# Add comprehensive African mineral data
def add_african_mineral_data():
    # Sample minerals
    minerals_df = pd.read_csv(MINERAL_FILE) if os.path.exists(MINERAL_FILE) else pd.DataFrame()
    if minerals_df.empty:
        sample_minerals = [
            [1, "Copper", "Industrial metal used in electrical wiring and electronics", 8500.50],
            [2, "Gold", "Precious metal for jewelry and investment", 58000000.00],
            [3, "Iron Ore", "Primary raw material for steel production", 120.75],
            [4, "Diamonds", "Precious gemstone for jewelry and industrial use", 150000000.00],
            [5, "Cobalt", "Critical mineral for batteries and electronics", 33000.00],
            [6, "Platinum", "Precious metal for catalytic converters and jewelry", 30000000.00],
            [7, "Phosphates", "Essential for fertilizer production", 450.00],
            [8, "Bauxite", "Primary ore for aluminum production", 55.00]
        ]
        minerals_df = pd.DataFrame(sample_minerals, columns=["MineralID", "MineralName", "Description", "MarketPriceUSD_per_tonne"])
        minerals_df.to_csv(MINERAL_FILE, index=False)

    # Major African mining sites with real coordinates
    sites_df = pd.read_csv(DEPOSITS_FILE) if os.path.exists(DEPOSITS_FILE) else pd.DataFrame()
    if sites_df.empty:
        african_mines = [
            [1, "Kamoto Copper Mine", 1, 1, -10.7167, 25.4667, 450000],
            [2, "Tenke Fungurume", 1, 5, -10.5833, 26.1667, 22000],
            [3, "Kibali Gold Mine", 1, 2, 3.1667, 29.4667, 800000],
            [4, "Mponeng Gold Mine", 2, 2, -26.4000, 27.5000, 250000],
            [5, "Bushveld Complex", 2, 6, -25.2000, 28.5000, 4200000],
            [6, "Sishen Iron Ore Mine", 2, 3, -27.7667, 22.9833, 35000000],
            [7, "Orapa Diamond Mine", 3, 4, -21.3333, 25.3667, 24000000],
            [8, "Jwaneng Diamond Mine", 3, 4, -24.5219, 24.6931, 12600000],
            [9, "Mufulira Mine", 4, 1, -12.5500, 28.2333, 320000],
            [10, "Tarkwa Gold Mine", 5, 2, 5.3000, -2.0000, 600000],
            [11, "Sangaredi Mine", 6, 8, 11.0833, -13.9000, 18500000],
            [12, "Simandou Iron Ore", 6, 3, 8.5500, -8.9500, 100000000],
            [13, "Geita Gold Mine", 7, 2, -2.8667, 32.1667, 550000],
            [14, "Phosboucraa Mine", 8, 7, 26.1667, -12.8333, 2800000]
        ]
        sites_df = pd.DataFrame(african_mines, columns=["SiteID", "SiteName", "CountryID", "MineralID", "Latitude", "Longitude", "Production_tonnes"])
        sites_df.to_csv(DEPOSITS_FILE, index=False)

    # Comprehensive African countries data - FIXED: Added MiningContribution_GDP column
    countries_df = pd.read_csv(COUNTRY_FILE) if os.path.exists(COUNTRY_FILE) else pd.DataFrame()
    if countries_df.empty:
        african_countries = [
            [1, "DR Congo", 58.0, 8.5, "World's largest cobalt producer, major copper and diamond producer", 95.0, 15.2],
            [2, "South Africa", 380.0, 25.3, "World's largest platinum producer, major gold and diamond producer", 59.0, 7.8],
            [3, "Botswana", 18.7, 4.1, "World's largest diamond producer by value", 2.4, 25.0],
            [4, "Zambia", 22.5, 3.2, "Second largest copper producer in Africa", 19.5, 12.1],
            [5, "Ghana", 75.0, 6.8, "Largest gold producer in Africa, significant bauxite reserves", 32.0, 8.5],
            [6, "Guinea", 15.8, 2.1, "World's second largest bauxite producer, massive iron ore reserves", 13.5, 15.2],
            [7, "Tanzania", 75.0, 2.8, "Fourth largest gold producer in Africa, growing mining sector", 63.0, 4.1],
            [8, "Morocco", 126.0, 2.4, "World's largest phosphate exporter, controls 75% of global reserves", 37.5, 4.0]
        ]
        countries_df = pd.DataFrame(african_countries, columns=["CountryID", "CountryName", "GDP_BillionUSD", "MiningRevenue_BillionUSD", "KeyProjects", "Population_Millions", "MiningContribution_GDP"])
        countries_df.to_csv(COUNTRY_FILE, index=False)
        print("Created countries.csv with MiningContribution_GDP column")

    # Generate comprehensive production data
    production_df = pd.read_csv(PROD_TS_FILE) if os.path.exists(PROD_TS_FILE) else pd.DataFrame()
    if production_df.empty:
        production_data = []
        stat_id = 1
        
        # Define realistic production ranges for each country-mineral combination
        production_ranges = {
            # CountryID: {MineralID: (min_production, max_production, export_value_multiplier)}
            1: {1: (400000, 500000, 0.003), 2: (70000, 90000, 40), 5: (18000, 25000, 0.8)},  # DR Congo
            2: {2: (200000, 280000, 45), 3: (30000000, 40000000, 0.0001), 6: (4000000, 5000000, 0.6)},  # South Africa
            3: {4: (20000000, 26000000, 6)},  # Botswana
            4: {1: (300000, 400000, 0.003)},  # Zambia
            5: {2: (500000, 700000, 42), 8: (800000, 1200000, 0.05)},  # Ghana
            6: {3: (80000000, 120000000, 0.00008), 8: (15000000, 20000000, 0.05)},  # Guinea
            7: {2: (400000, 600000, 41)},  # Tanzania
            8: {7: (2500000, 3500000, 0.2)}  # Morocco
        }
        
        # Generate data for 2020-2023
        for year in range(2020, 2024):
            for country_id, minerals in production_ranges.items():
                for mineral_id, (min_prod, max_prod, export_multiplier) in minerals.items():
                    # Generate realistic production with some variation
                    production = int(min_prod + (hash(f"{year}{country_id}{mineral_id}") % (max_prod - min_prod)))
                    export_value = production * export_multiplier
                    
                    production_data.append([
                        stat_id, year, country_id, mineral_id, production, export_value
                    ])
                    stat_id += 1
        
        production_df = pd.DataFrame(production_data, columns=["StatID", "Year", "CountryID", "MineralID", "Production_tonnes", "ExportValue_BillionUSD"])
        production_df.to_csv(PROD_TS_FILE, index=False)
        print(f"Generated {len(production_data)} production records")

# Initialize data
add_african_mineral_data()

# --- Helper Functions ---
def load_df(filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            return pd.read_csv(filename)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return pd.DataFrame()
    return pd.DataFrame()
