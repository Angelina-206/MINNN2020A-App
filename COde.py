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
