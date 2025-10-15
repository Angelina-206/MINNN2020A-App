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

# Helper Functions 
def load_df(filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            return pd.read_csv(filename)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def load_users():
    users = {}
    df = load_df(USER_FILE)
    for _, row in df.iterrows():
        users[row['Username']] = {
            "password_hash": row['PasswordHash'],
            "role": int(row['RoleID']),
            "email": row['Email'],
            "id": row['UserID']
        }
    return users

def get_role_name(role_id):
    roles = load_df(ROLES_FILE)
    if not roles.empty:
        match = roles[roles["RoleID"] == role_id]
        if not match.empty:
            return match.iloc[0]["RoleName"]
    return "Researcher"

def get_country_name(country_id):
    countries = load_df(COUNTRY_FILE)
    if not countries.empty:
        match = countries[countries["CountryID"] == country_id]
        if not match.empty:
            return match.iloc[0]["CountryName"]
    return f"Country_{country_id}"

def get_mineral_name(mineral_id):
    minerals = load_df(MINERAL_FILE)
    if not minerals.empty:
        match = minerals[minerals["MineralID"] == mineral_id]
        if not match.empty:
            return match.iloc[0]["MineralName"]
    return f"Mineral_{mineral_id}"

def get_mineral_color(mineral_name):
    color_map = {
        "Copper": "orange",
        "Gold": "gold",
        "Iron Ore": "darkred",
        "Diamonds": "lightblue",
        "Cobalt": "blue",
        "Platinum": "lightgray",
        "Phosphates": "green",
        "Bauxite": "red"
    }
    return color_map.get(mineral_name, "purple")

def get_country_production_data(country_id):
    """Get comprehensive production data for a country"""
    production_df = load_df(PROD_TS_FILE)
    sites_df = load_df(DEPOSITS_FILE)
    
    country_production = production_df[production_df['CountryID'] == country_id]
    country_sites = sites_df[sites_df['CountryID'] == country_id]
    
    mineral_production = {}
    
    if not country_production.empty:
        # Get latest year data
        latest_year = country_production['Year'].max()
        latest_data = country_production[country_production['Year'] == latest_year]
        
        for _, row in latest_data.iterrows():
            mineral_name = get_mineral_name(row['MineralID'])
            if mineral_name not in mineral_production:
                mineral_production[mineral_name] = {
                    'production': 0,
                    'export_value': 0,
                    'sites': []
                }
            mineral_production[mineral_name]['production'] += row['Production_tonnes']
            mineral_production[mineral_name]['export_value'] += row['ExportValue_BillionUSD']
    
    # Add site information
    for _, site in country_sites.iterrows():
        mineral_name = get_mineral_name(site['MineralID'])
        if mineral_name not in mineral_production:
            mineral_production[mineral_name] = {
                'production': site['Production_tonnes'],
                'export_value': 0,
                'sites': []
            }
        mineral_production[mineral_name]['sites'].append({
            'name': site['SiteName'],
            'production': site['Production_tonnes'],
            'mineral': mineral_name
        })
    
    return mineral_production

def get_production_trends():
    """Get production trends for charts"""
    production_df = load_df(PROD_TS_FILE)
    minerals_df = load_df(MINERAL_FILE)
    
    if production_df.empty:
        return None
    
    # Merge with mineral names
    merged_df = production_df.merge(minerals_df[['MineralID', 'MineralName']], on='MineralID')
    return merged_df

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "Administrator":
            return "Access denied. Administrator role required.", 403
        return f(*args, **kwargs)
    return wrapper

#  Authentication Routes 
@app.route("/register", methods=["GET","POST"])
def register():
    if "username" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        email = request.form["email"].strip()
        role_id = int(request.form.get("role", "3"))
        
        users = load_users()
        if username in users:
            return "Username already exists", 400
        
        pwd_hash = generate_password_hash(password)
        df = load_df(USER_FILE)
        next_id = df["UserID"].max() + 1 if not df.empty else 1
        new_user = pd.DataFrame([{
            "UserID": next_id,
            "Username": username,
            "PasswordHash": pwd_hash,
            "RoleID": role_id,
            "Email": email
        }])
        pd.concat([df, new_user], ignore_index=True).to_csv(USER_FILE, index=False)
        return redirect(url_for("login"))

    return '''
    <h2>Register</h2>
    <form method="post">
      Username: <input name="username" required><br>
      Password: <input name="password" type="password" required><br>
      Email: <input name="email" type="email"><br>
      Role:<br>
      <input type="radio" name="role" value="1"> Administrator<br>
      <input type="radio" name="role" value="2"> Investor<br>
      <input type="radio" name="role" value="3" checked> Researcher<br>
      <button type="submit">Register</button>
    </form>
    <a href="/login">Already have an account? Login</a>
    '''

@app.route("/login", methods=["GET","POST"])
def login():
    if "username" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        users = load_users()
        
        if username in users and check_password_hash(users[username]["password_hash"], password):
            user_data = users[username]
            session["username"] = username
            session["role"] = get_role_name(user_data["role"])
            return redirect(url_for("dashboard"))
        
        return "Invalid credentials", 401

    return '''
    <h2>Login</h2>
    <form method="post">
      Username: <input name="username" required><br>
      Password: <input name="password" type="password" required><br>
      <button type="submit">Login</button>
    </form>
    <a href="/register">Need an account? Register</a>
    '''
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Home & Dashboard 
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>African Mining Data Portal</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .container { max-width: 600px; margin: 0 auto; }
            .button { display: inline-block; padding: 15px 30px; margin: 10px; 
                     background: #007bff; color: white; text-decoration: none; 
                     border-radius: 5px; font-size: 18px; }
            .button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>African Mining Data Portal</h1>
            <p>Explore major mineral deposits and production sites across Africa</p>
            <div>
                <a href="/login" class="button">Login</a>
                <a href="/register" class="button">Register</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route("/dashboard")
@login_required
def dashboard():
    user = session["username"]
    role = session["role"]
    
    # Generate mineral price chart for dashboard
    minerals_df = load_df(MINERAL_FILE)
    if not minerals_df.empty:
        fig = px.bar(minerals_df, x='MineralName', y='MarketPriceUSD_per_tonne',
                    title='Mineral Market Prices', color='MineralName',
                    labels={'MarketPriceUSD_per_tonne': 'Price per tonne (USD)', 'MineralName': 'Mineral'})
        price_chart = fig.to_html(full_html=False, include_plotlyjs='cdn')
    else:
        price_chart = "<p>No mineral data available</p>"
    
    # Generate African mineral map for dashboard
    sites_df = load_df(DEPOSITS_FILE)
    if not sites_df.empty:
        africa_map = folium.Map(location=[-8, 28], zoom_start=4)
        
        for _, site in sites_df.iterrows():
            mineral_name = get_mineral_name(site['MineralID'])
            country_name = get_country_name(site['CountryID'])
            color = get_mineral_color(mineral_name)
            
            popup_text = f"""
            <div style='min-width: 250px;'>
                <h4 style='margin: 0; color: #333;'>{site['SiteName']}</h4>
                <hr style='margin: 5px 0;'>
                <p style='margin: 2px 0;'><strong>Country:</strong> {country_name}</p>
                <p style='margin: 2px 0;'><strong>Mineral:</strong> {mineral_name}</p>
                <p style='margin: 2px 0;'><strong>Annual Production:</strong> {site['Production_tonnes']:,.0f} tonnes</p>
            </div>
            """
            
            folium.Marker(
                [site['Latitude'], site['Longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{site['SiteName']} - {mineral_name}",
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(africa_map)
        
        map_html = africa_map._repr_html_()
    else:
        map_html = "<p>No mining site data available</p>"


# Dashboard links
    links = [
        ("View Minerals", "/minerals"),
        ("African Mineral Map", "/map"),
        ("Country Profiles", "/countries"),
        ("Production Charts", "/charts")
    ]
    
    if role == "Administrator":
        links.extend([
            ("Admin Panel", "/admin"),
            ("Add Mineral", "/minerals/add")
        ])
    
    if role in ["Investor", "Administrator"]:
        links.append(("Market Data", "/market"))
    
    links_html = "".join(f'<li><a href="{url}">{text}</a></li>' for text, url in links)
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>African Mining Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .dashboard-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
            .chart-container, .map-container {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .links {{ list-style: none; padding: 0; }}
            .links li {{ margin: 10px 0; }}
            .links a {{ display: block; padding: 15px; background: #28a745; color: white; 
                      text-decoration: none; border-radius: 5px; }}
            .links a:hover {{ background: #218838; }}
            .logout {{ margin-top: 30px; }}
            .logout a {{ background: #dc3545; padding: 10px 20px; color: white; 
                       text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>African Mining Dashboard</h1>
            <p>Welcome, <strong>{user}</strong> | Role: <strong>{role}</strong></p>
        </div>
        
        <div class="dashboard-grid">
            <div class="chart-container">
                <h3>Mineral Market Prices</h3>
                <div id="price-chart">{price_chart}</div>
            </div>
            
            <div class="map-container">
                <h3>African Mineral Deposits</h3>
                <div id="africa-map" style="height: 400px;">{map_html}</div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <h3>Quick Access</h3>
                <ul class="links">{links_html}</ul>
            </div>
            <div>
                <h3>African Mining Overview</h3>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                    <p><strong>14 Major Mining Sites</strong> across 8 African countries</p>
                    <p><strong>8 Mineral Types</strong> including strategic resources</p>
                    <p><strong>Real Production Data</strong> from actual mining operations</p>
                    <p><strong>Interactive Map</strong> with detailed site information</p>
                </div>
            </div>
        </div>
        
        <div class="logout">
            <a href="/logout">Logout</a>
        </div>
    </body>
    </html>
    '''
# --- Country Profiles ---
@app.route("/countries")
@login_required
def list_countries():
    countries_df = load_df(COUNTRY_FILE)
    
    if countries_df.empty:
        return "<h2>Country Profiles</h2><p>No country data available</p><a href='/dashboard'>Back to Dashboard</a>"
    
    html = """
    <h1>African Mining Country Profiles</h1>
    <p style="color: #666; margin-bottom: 30px;">
        Comprehensive overview of major mineral-producing countries in Africa with production statistics, 
        economic data, and key mining projects.
    </p>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px;">
    """
    
    for _, country in countries_df.iterrows():
        # Safe access to country data with fallbacks
        country_name = country.get('CountryName', 'Unknown Country')
        gdp = country.get('GDP_BillionUSD', 0)
        mining_revenue = country.get('MiningRevenue_BillionUSD', 0)
        population = country.get('Population_Millions', 0)
        mining_contribution = country.get('MiningContribution_GDP', 0)
        key_projects = country.get('KeyProjects', 'No information available')
        
        production_data = get_country_production_data(country['CountryID'])
        total_minerals = len(production_data) if production_data else 0
        
        html += f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #2c3e50;">{country_name}</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                <div>
                    <strong>GDP:</strong><br>
                    <span style="color: #27ae60;">${gdp}B</span>
                </div>
                <div>
                    <strong>Mining Revenue:</strong><br>
                    <span style="color: #e74c3c;">${mining_revenue}B</span>
                </div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <strong>Mining Contribution to GDP:</strong> {mining_contribution}%<br>
                <strong>Population:</strong> {population}M<br>
                <strong>Key Minerals:</strong> {total_minerals} types
            </div>
            
            <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 15px;">
                <strong>Global Significance:</strong><br>
                <small>{key_projects}</small>
            </div>
            
            <a href="/country/{country['CountryID']}" style="display: block; text-align: center; background: #3498db; color: white; padding: 10px; text-decoration: none; border-radius: 4px;">
                View Detailed Profile
            </a>
        </div>
        """
    
    html += "</div>"
    
    back_btn = "<div style='margin-top: 30px;'><a href='/dashboard' style='padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px;'>Back to Dashboard</a></div>"
    return html + back_btn

@app.route("/country/<int:country_id>")
@login_required
def country_profile(country_id):
    countries_df = load_df(COUNTRY_FILE)
    country = countries_df[countries_df['CountryID'] == country_id]
    
    if country.empty:
        return "Country not found", 404
    
    country_data = country.iloc[0]
    production_data = get_country_production_data(country_id)
    
    # Safe access to country data
    country_name = country_data.get('CountryName', 'Unknown Country')
    gdp = country_data.get('GDP_BillionUSD', 0)
    mining_revenue = country_data.get('MiningRevenue_BillionUSD', 0)
    population = country_data.get('Population_Millions', 0)
    mining_contribution = country_data.get('MiningContribution_GDP', 0)
    key_projects = country_data.get('KeyProjects', 'No information available')
    
    # Build production overview
    production_html = "<h3>Mineral Production Overview</h3>"
    if production_data:
        production_html += "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;'>"
        
        for mineral, data in production_data.items():
            production_html += f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 6px; padding: 15px; background: #fafafa;">
                <h4 style="margin: 0 0 10px 0; color: #2c3e50;">{mineral}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.9em;">
                    <div>
                        <strong>Annual Production:</strong><br>
                        {data['production']:,.0f} tonnes
                    </div>
                    <div>
                        <strong>Export Value:</strong><br>
                        ${data.get('export_value', 0):,.2f}B
                    </div>
                </div>
            </div>
            """
        production_html += "</div>"
        
        # Add major mining sites
        production_html += "<h3 style='margin-top: 30px;'>Major Mining Operations</h3>"
        production_html += "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 15px;'>"
        
        for mineral, data in production_data.items():
            for site in data.get('sites', []):
                production_html += f"""
                <div style="border-left: 4px solid {get_mineral_color(mineral)}; padding: 12px; background: white; border-radius: 4px;">
                    <strong>{site['name']}</strong><br>
                    <span style="color: #666; font-size: 0.9em;">
                        {mineral} - {site['production']:,.0f} tonnes/year
                    </span>
                </div>
                """
        production_html += "</div>"
    else:
        production_html += "<p>No production data available for this country.</p>"
    
    profile_content = f"""
    <h1>{country_name} - Mining Profile</h1>
    
    <div style="background: #e8f4f8; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
        <h3 style="margin-top: 0;">Country Overview</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div>
                <strong>Total GDP:</strong> ${gdp} Billion<br>
                <strong>Mining Revenue:</strong> ${mining_revenue} Billion<br>
                <strong>Mining Contribution:</strong> {mining_contribution}% of GDP
            </div>
            <div>
                <strong>Population:</strong> {population} Million<br>
                <strong>Key Minerals:</strong> {', '.join(production_data.keys()) if production_data else 'N/A'}
            </div>
        </div>
        <div style="margin-top: 15px;">
            <strong>Key Projects & Significance:</strong><br>
            {key_projects}
        </div>
    </div>
    
    {production_html}
    """
    
    back_btn = "<div style='margin-top: 30px;'><a href='/countries' style='padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px;'>Back to Countries</a></div>"
    return profile_content + back_btn

