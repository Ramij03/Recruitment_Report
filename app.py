import os
os.environ['PYTHONHASHSEED'] = '0'  # For consistent memory usage

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List, Tuple
import base64
import io
import json
import dash.dependencies
import sys


app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.js"
], suppress_callback_exceptions=True)
app.title = "Recruitment Analytics Dashboard"

# Fix for large file uploads
app.server.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB limit
app.server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
server = app.server

# Custom CSS with modern design
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

            :root {
                --primary-color: #6366f1;
                --secondary-color: #8b5cf6;
                --success-color: #10b981;
                --warning-color: #f59e0b;
                --danger-color: #ef4444;
                --info-color: #3b82f6;
                --dark-color: #1f2937;
                --light-color: #f8fafc;
                --border-radius: 16px;
                --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            }

            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
                color: var(--dark-color);
                line-height: 1.6;
            }

            .dashboard-container {
                padding: 2rem;
                min-height: 100vh;
            }

            .hero-section {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                color: white;
                padding: 3rem 2rem;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-lg);
                margin-bottom: 2rem;
                position: relative;
                overflow: hidden;
            }

            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                width: 200px;
                height: 200px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 50%;
                transform: translate(50%, -50%);
            }

            .hero-title {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                position: relative;
                z-index: 2;
            }

            .hero-subtitle {
                font-size: 1.25rem;
                font-weight: 400;
                opacity: 0.9;
                position: relative;
                z-index: 2;
            }

            .metric-card {
                background: white;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-sm);
                border: 1px solid #e5e7eb;
                transition: all 0.3s ease;
                height: 100%;
                position: relative;
                overflow: hidden;
            }

            .metric-card:hover {
                transform: translateY(-4px);
                box-shadow: var(--shadow-md);
                border-color: var(--primary-color);
            }

            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            }

            .metric-value {
                font-size: 2.5rem;
                font-weight: 800;
                margin: 0;
                line-height: 1;
            }

            .metric-label {
                font-size: 0.875rem;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: #6b7280;
                margin-top: 0.5rem;
            }

            .metric-subtitle {
                font-size: 0.875rem;
                color: #9ca3af;
                margin-top: 0.25rem;
                font-weight: 400;
            }

            .card-modern {
                background: white;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-sm);
                border: 1px solid #e5e7eb;
                overflow: hidden;
            }
            .stage-button-hover:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 15px rgba(0,0,0,0.2) !important;
            }
            .card-header-modern {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border-bottom: 1px solid #e5e7eb;
                padding: 1.5rem;
                font-weight: 600;
                color: var(--dark-color);
            }

            .upload-zone {
                border: 2px dashed #d1d5db;
                border-radius: var(--border-radius);
                background: #fafbfc;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
            }

            .upload-zone:hover {
                border-color: var(--primary-color);
                background: #f8fafc;
                transform: scale(1.02);
            }

            .upload-icon {
                color: var(--primary-color);
                font-size: 3rem;
                margin-bottom: 1rem;
            }

            .modern-tabs .nav-link {
                border: none;
                border-radius: var(--border-radius) var(--border-radius) 0 0;
                color: #6b7280;
                font-weight: 500;
                padding: 1rem 1.5rem;
                transition: all 0.3s ease;
                position: relative;
            }

            .modern-tabs .nav-link.active {
                background: white;
                color: var(--primary-color);
                box-shadow: var(--shadow-sm);
            }

            .modern-tabs .nav-link::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 50%;
                width: 0;
                height: 3px;
                background: var(--primary-color);
                transition: all 0.3s ease;
                transform: translateX(-50%);
            }

            .modern-tabs .nav-link.active::after {
                width: 100%;
            }

            .tab-content-modern {
                background: white;
                border-radius: 0 0 var(--border-radius) var(--border-radius);
                box-shadow: var(--shadow-sm);
                border: 1px solid #e5e7eb;
                border-top: none;
                padding: 2rem;
            }

            .insight-card {
                background: linear-gradient(135deg, #fefefe 0%, #f8fafc 100%);
                border: 1px solid #e5e7eb;
                border-radius: var(--border-radius);
                padding: 1.5rem;
                margin-bottom: 1rem;
                position: relative;
                overflow: hidden;
            }

            .insight-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: var(--primary-color);
            }

            .candidate-card {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: var(--border-radius);
                padding: 1rem;
                transition: all 0.3s ease;
                position: relative;
            }

            .candidate-card:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-md);
                border-color: var(--primary-color);
            }

            .status-badge {
                padding: 0.25rem 0.75rem;
                border-radius: 2rem;
                font-size: 0.875rem;
                font-weight: 500;
                display: inline-block;
            }

            .status-hired {
                background: #dcfce7;
                color: #166534;
            }

            .status-unqualified {
                background: #fef2f2;
                color: #b91c1c;
            }

            .status-interviewing {
                background: #dbeafe;
                color: #1d4ed8;
            }

            .filter-card {
                z-index: 100;
                background: white;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-sm);
                border: 1px solid #e5e7eb;
                overflow: visible; /* Changed from hidden to avoid dropdown menus being cut off */
                margin-bottom: 2rem;
            }

            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }

            .plotly-graph-div {
                border-radius: var(--border-radius);
                overflow: hidden;
                box-shadow: var(--shadow-sm);
                border: 1px solid #e5e7eb;
            }

            .table-modern {
                border-radius: var(--border-radius);
                overflow: hidden;
                box-shadow: var(--shadow-sm);
                border: 1px solid #e5e7eb;
            }

            .alert-modern {
                border-radius: var(--border-radius);
                border: none;
                box-shadow: var(--shadow-sm);
                padding: 1rem 1.5rem;
                font-weight: 500;
            }

            .loading-spinner {
                display: inline-block;
                width: 24px;
                height: 24px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid var(--primary-color);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .section-header {
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--dark-color);
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .section-description {
                color: #6b7280;
                margin-bottom: 2rem;
                font-size: 1.125rem;
            }

            /* Enhanced spacing for graph labels */
            .js-plotly-plot .subplot .xtick text,
            .js-plotly-plot .subplot .ytick text {
                font-size: 12px !important;
                font-weight: 500 !important;
            }

            /* Improved legend spacing */
            .js-plotly-plot .legend .traces {
                padding: 5px !important;
            }

            /* Fix dropdown z-index issue */
            .dash-dropdown .Select-menu-outer {
                z-index: 1000 !important;
            }

            /* Fix date picker z-index issue */
            .DateRangePicker, .DateRangePickerInput, .DateInput {
                z-index: 900 !important;
            }

            /* Ensure filter sections don't overlap */
            .filter-section-row {
                margin-bottom: 30px;
                position: relative;
                z-index: 10;
                overflow: visible !important;
            }

            /* Fix for the custom date picker */
            #custom-date-container {
                margin-top: 10px;
                position: relative;
                z-index: 900;
            }

            /* Ensure job title filter doesn't get overlapped */
            #job-title-filter-row {
                position: relative;
                z-index: 5;
                clear: both;
                padding-top: 25px;
                margin-top: 25px;
                border-top: 1px solid #f3f4f6;
            }

            /* Modify layout of filter components */
            #filter-section {
                margin-bottom: 30px;
                overflow: visible !important;
                padding-bottom: 30px;
            }

            /* Funnel comparison specific styles */
            .comparison-selector-card {
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border: 1px solid #bae6fd;
                border-radius: var(--border-radius);
                padding: 1.5rem;
                margin-bottom: 2rem;
            }

            .comparison-filter-row {
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .comparison-filter-label {
                font-weight: 600;
                color: #1f2937;
                min-width: 120px;
                font-size: 0.875rem;
            }

            .funnel-comparison-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 2rem;
                margin-top: 2rem;
                position: relative;
                z-index: 100;
                padding-bottom: 100px;
            }

            .funnel-comparison-item {
                background: white;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-sm);
                border: 1px solid #e5e7eb;
                overflow: hidden;
            }

            .funnel-comparison-header {
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                padding: 1rem 1.5rem;
                font-weight: 600;
                font-size: 1.125rem;
            }

            .comparison-metrics-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin: 1.5rem 0;
            }

            .comparison-metric-card {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
            }

            .comparison-metric-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: #1f2937;
                margin-bottom: 0.25rem;
            }

            .comparison-metric-label {
                font-size: 0.75rem;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 500;
            }
            
            /* Enhanced comparison filter styles */
            .comparison-form-group-enhanced {
                margin-bottom: 1.5rem;
                position: relative;
                z-index: 100;
            }
            
            .comparison-form-group-enhanced .dash-dropdown {
                min-height: 40px !important;
            }
            
            .comparison-form-group-enhanced .Select-control {
                min-height: 40px !important;
                border: 2px solid #e5e7eb !important;
                border-radius: 12px !important;
                transition: all 0.3s ease !important;
            }
            
            .comparison-form-group-enhanced .Select-control:hover {
                border-color: #6366f1 !important;
            }
            
            .comparison-form-group-enhanced .Select-menu-outer {
                max-height: 300px !important;
                border-radius: 12px !important;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
                border: 2px solid #e5e7eb !important;
                margin-top: 4px !important;
                z-index: 9999 !important;
                position: absolute !important;
            }
            
            .comparison-form-group-enhanced .Select {
                position: relative !important;
                z-index: 1000 !important;
            }
            
            .comparison-form-group-enhanced .Select.is-open {
                z-index: 9999 !important;
            }
            
            .comparison-form-group-enhanced .Select-menu {
                max-height: 280px !important;
                overflow-y: auto !important;
            }
            
            .comparison-form-group-enhanced .Select-value-label {
                font-size: 14px !important;
                color: #374151 !important;
            }
            
            .comparison-form-group-enhanced .Select-placeholder {
                font-size: 14px !important;
                color: #9ca3af !important;
            }
            
            .comparison-form-group-enhanced .Select-multi-value-wrapper {
                max-height: 100px !important;
                overflow-y: auto !important;
            }
            
            .comparison-form-group-enhanced .Select-multi-value {
                background-color: #6366f1 !important;
                border-radius: 8px !important;
                color: white !important;
                margin: 2px !important;
            }
            
            .comparison-form-group-enhanced .Select-multi-value__label {
                color: white !important;
                font-size: 13px !important;
                padding: 4px 8px !important;
            }
            
            .comparison-form-group-enhanced .Select-multi-value__remove {
                color: white !important;
                cursor: pointer !important;
                padding: 4px !important;
            }
            
            .comparison-form-group-enhanced .Select-multi-value__remove:hover {
                background-color: rgba(255, 255, 255, 0.2) !important;
                color: white !important;
            }
            
            .comparison-form-label-enhanced {
                display: block;
                font-weight: 600;
                color: #374151;
                margin-bottom: 0.75rem;
                font-size: 0.875rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                position: relative;
                padding-left: 1.5rem;
            }
            
            .comparison-form-label-enhanced::before {
                content: '▸';
                position: absolute;
                left: 0;
                color: #6366f1;
                font-weight: bold;
            }
            
            /* Date picker styles for comparison */
            .comparison-form-group-enhanced .DateRangePicker {
                width: 100% !important;
            }
            
            .comparison-form-group-enhanced .DateInput {
                width: 48% !important;
                display: inline-block !important;
            }
            
            .comparison-form-group-enhanced .DateRangePickerInput {
                border: 2px solid #e5e7eb !important;
                border-radius: 12px !important;
                padding: 8px !important;
                background-color: white !important;
            }
            
            .comparison-form-group-enhanced .DateRangePickerInput:hover {
                border-color: #6366f1 !important;
            }
            
            .comparison-form-group-enhanced .DateRangePickerInput__withBorder {
                border-radius: 12px !important;
            }
            
            .comparison-form-group-enhanced .DateInput_input {
                font-size: 14px !important;
                padding: 8px !important;
                font-family: 'Inter', sans-serif !important;
            }

            .comparison-setup-section {
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border: 2px solid #e2e8f0;
                border-radius: 20px;
                padding: 2rem;
                margin-bottom: 2rem;
                position: relative;
                overflow: hidden;
            }

            .comparison-setup-section::before {
                content: '';
                position: absolute;
                top: -50%;
                right: -20%;
                width: 300px;
                height: 300px;
                background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
                border-radius: 50%;
            }

            .comparison-config-header {
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                padding: 1.5rem 2rem;
                border-radius: 16px;
                margin-bottom: 2rem;
                box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.3);
                position: relative;
                overflow: hidden;
            }

            .comparison-config-header::after {
                content: '⚙️';
                position: absolute;
                right: 2rem;
                top: 50%;
                transform: translateY(-50%);
                font-size: 2rem;
                opacity: 0.7;
            }

            .comparison-controls-grid {
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 2rem;
                align-items: end;
                margin-bottom: 2rem;
            }

            .comparison-count-selector {
                background: white;
                padding: 1.5rem;
                border-radius: 16px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                border: 1px solid #e5e7eb;
            }

            .comparison-generate-button {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
                border: none !important;
                border-radius: 16px !important;
                padding: 1rem 2rem !important;
                color: white !important;
                font-weight: 600 !important;
                font-size: 1.125rem !important;
                box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.3) !important;
                transition: all 0.3s ease !important;
                position: relative !important;
                overflow: hidden !important;
            }

            .comparison-generate-button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 15px 35px -5px rgba(16, 185, 129, 0.4) !important;
            }

            .comparison-generate-button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }

            .comparison-generate-button:hover::before {
                left: 100%;
            }

            .comparison-filters-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 2rem;
                margin-top: 2rem;
            }

            .enhanced-comparison-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
                border: 2px solid #f1f5f9;
                overflow: visible !important;
                transition: all 0.3s ease;
                position: relative;
                margin-bottom: 2rem;
                z-index: 10;
                padding-bottom: 20px;
            }
            
            .enhanced-comparison-card .comparison-form-group-enhanced:last-child {
                margin-bottom: 100px !important;
            }

            .enhanced-comparison-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #6366f1, #8b5cf6, #3b82f6);
            }

            .comparison-card-header {
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                color: white;
                padding: 1.5rem 2rem;
                position: relative;
                overflow: hidden;
            }

            .comparison-card-header::after {
                content: attr(data-index);
                position: absolute;
                right: 2rem;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(255, 255, 255, 0.2);
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 1.25rem;
            }

            .comparison-card-body {
                padding: 2rem;
            }

            .comparison-form-group {
                margin-bottom: 1.5rem;
            }

            .comparison-form-label {
                display: block;
                font-weight: 600;
                color: #374151;
                margin-bottom: 0.75rem;
                font-size: 0.875rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                position: relative;
                padding-left: 1.5rem;
            }

            .comparison-form-label::before {
                content: '▸';
                position: absolute;
                left: 0;
                color: #6366f1;
                font-weight: bold;
            }

            .comparison-input-enhanced {
                width: 100%;
                padding: 0.75rem 1rem;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                font-family: 'Inter', sans-serif;
                transition: all 0.3s ease;
                background: #fafbfc;
            }

            .comparison-input-enhanced:focus {
                border-color: #6366f1;
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
                background: white;
            }

            .comparison-time-selector {
                display: flex;
                gap: 1rem;
                margin: 1rem 0;
                flex-wrap: wrap;
            }

            .comparison-time-option {
                background: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 0.75rem 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 500;
                font-size: 0.875rem;
            }

            .comparison-time-option:hover {
                border-color: #6366f1;
                background: #f0f9ff;
            }

            .comparison-time-option.active {
                background: #6366f1;
                color: white;
                border-color: #6366f1;
            }

            .comparison-results-section {
                margin-top: 3rem;
                padding-top: 2rem;
                border-top: 3px solid #f1f5f9;
                position: relative;
                z-index: 1;
            }

            .results-header {
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                color: white;
                padding: 2rem;
                border-radius: 20px;
                margin-bottom: 2rem;
                box-shadow: 0 10px 25px -5px rgba(5, 150, 105, 0.3);
                position: relative;
                overflow: hidden;
                z-index: 1;
            }

            .results-header::before {
                content: '📊';
                position: absolute;
                right: 2rem;
                top: 50%;
                transform: translateY(-50%);
                font-size: 3rem;
                opacity: 0.7;
            }

            .results-stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-top: 1rem;
            }

            .results-stat-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
                backdrop-filter: blur(10px);
            }

            .results-stat-value {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 0.25rem;
            }

            .results-stat-label {
                font-size: 0.875rem;
                opacity: 0.9;
            }

            .individual-funnels-section {
                margin: 3rem 0;
            }

            .section-divider {
                height: 3px;
                background: linear-gradient(90deg, #6366f1, #8b5cf6, #3b82f6);
                border-radius: 2px;
                margin: 3rem 0;
                box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
            }

            .enhanced-section-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 2rem;
                padding: 1.5rem 2rem;
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }

            .section-title {
                font-size: 1.75rem;
                font-weight: 700;
                color: #1f2937;
                margin: 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }

            .section-subtitle {
                color: #6b7280;
                font-size: 1rem;
                margin: 0;
                font-weight: 400;
            }

            .comparison-charts-grid {
                display: grid;
                grid-template-columns: 1fr;
                gap: 3rem;
            }

            .chart-container-enhanced {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
                border: 1px solid #e5e7eb;
                overflow: hidden;
                transition: all 0.3s ease;
            }

            .chart-container-enhanced:hover {
                transform: translateY(-2px);
                box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15);
            }

            .chart-header {
                background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
                color: white;
                padding: 1.5rem 2rem;
                font-weight: 600;
                font-size: 1.125rem;
                position: relative;
                overflow: hidden;
            }

            .chart-header::after {
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                width: 100px;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1));
                transform: skewX(-15deg);
            }

            .info-callout {
                background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                border: 1px solid #93c5fd;
                border-radius: 16px;
                padding: 1.5rem;
                margin: 2rem 0;
                position: relative;
                overflow: hidden;
            }

            .info-callout::before {
                content: '💡';
                position: absolute;
                top: 1rem;
                right: 1rem;
                font-size: 1.5rem;
                opacity: 0.7;
            }

            .info-callout-title {
                font-weight: 600;
                color: #1e40af;
                margin-bottom: 0.5rem;
                font-size: 1rem;
            }

            .info-callout-text {
                color: #1e3a8a;
                margin: 0;
                font-size: 0.875rem;
                line-height: 1.6;
            }

            .loading-state {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 4rem 2rem;
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border-radius: 20px;
                border: 2px dashed #cbd5e1;
            }

            .loading-spinner-enhanced {
                width: 60px;
                height: 60px;
                border: 4px solid #e5e7eb;
                border-top: 4px solid #6366f1;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 1rem;
            }

            .loading-text {
                color: #6b7280;
                font-size: 1.125rem;
                font-weight: 500;
            }
            
            #comparison-filters-container {
                position: relative;
                z-index: 1000;
                overflow: visible !important;
            }
            
            #comparison-results-container {
                position: relative;
                z-index: 1;
            }
            
            .tab-content-modern {
                overflow: visible !important;
            }
            
            /* Ensure dropdowns in comparison tab are not cut off */
            #main-tabs-content > div {
                overflow: visible !important;
            }
            
            /* Fix for funnel comparison tab specifically */
            #funnel_comparison {
                overflow: visible !important;
                min-height: 800px;
            }
            
            #comparison-filters-container .enhanced-comparison-card {
                min-height: 650px !important;
                padding-bottom: 150px !important;
            }
            
            #comparison-filters-container .comparison-form-group-enhanced:last-child {
                margin-bottom: 150px !important;
            }
            
            /* Ensure the tab content doesn't cut off dropdowns */
            .tab-content-modern[data-tab="funnel_comparison"] {
                overflow: visible !important;
                min-height: 1000px;
            }
            
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-20px); }
                100% { transform: translateY(0px); }
            }

            @keyframes pulse {
                0% { opacity: 0.6; }
                50% { opacity: 1; }
                100% { opacity: 0.6; }
            }

            .generate-btn-enhanced:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 15px 35px -5px rgba(102, 126, 234, 0.6) !important;
            }

            .generate-btn-enhanced::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }

            .generate-btn-enhanced:hover::before {
                left: 100%;
            }

            .modern-dropdown .Select-control {
                border-radius: 12px !important;
                border: 2px solid #e2e8f0 !important;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
            }

            .modern-dropdown .Select-control:hover {
                border-color: #667eea !important;
            }

            .enhanced-filter-card {
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
                border: 2px solid #f1f5f9;
                overflow: hidden;
                transition: all 0.3s ease;
                position: relative;
                margin-bottom: 2rem;
            }

            .enhanced-filter-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
            }

            .enhanced-filter-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15);
                border-color: #667eea;
            }

            .filter-card-header {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
                color: white;
                padding: 1.5rem 2rem;
                position: relative;
                overflow: hidden;
            }

            .filter-card-header::after {
                content: attr(data-index);
                position: absolute;
                right: 2rem;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(255, 255, 255, 0.2);
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 1.25rem;
            }

            .filter-form-group {
                margin-bottom: 1.5rem;
            }

            .filter-label-enhanced {
                display: block;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 0.75rem;
                font-size: 0.875rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                position: relative;
                padding-left: 1.5rem;
            }

            .filter-label-enhanced::before {
                content: '▸';
                position: absolute;
                left: 0;
                color: #667eea;
                font-weight: bold;
            }

            .time-period-options {
                display: flex;
                gap: 1rem;
                margin: 1rem 0;
                flex-wrap: wrap;
            }

            .time-period-option {
                background: #f7fafc;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 0.75rem 1.5rem;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 500;
                font-size: 0.875rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .time-period-option:hover {
                border-color: #667eea;
                background: #edf2f7;
                transform: translateY(-2px);
            }

            .time-period-option.active {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border-color: #667eea;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }
            /* Modal Styles */
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.75);
                backdrop-filter: blur(8px);
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2rem;
                animation: fadeIn 0.3s ease;
            }

            .modal-content {
                background: white;
                border-radius: 24px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
                max-width: 800px;
                width: 100%;
                max-height: 80vh;
                overflow: hidden;
                position: relative;
                animation: slideUp 0.3s ease;
            }

            .modal-header {
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                padding: 2rem;
                position: relative;
                overflow: hidden;
            }

            .modal-header::before {
                content: '';
                position: absolute;
                top: -50%;
                right: -20%;
                width: 300px;
                height: 300px;
                background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
                border-radius: 50%;
            }

            .modal-title {
                font-size: 2rem;
                font-weight: 700;
                margin: 0 0 0.5rem 0;
                position: relative;
                z-index: 2;
            }

            .modal-subtitle {
                font-size: 1.125rem;
                opacity: 0.9;
                margin: 0;
                position: relative;
                z-index: 2;
            }

            .modal-close {
                position: absolute;
                top: 1.5rem;
                right: 1.5rem;
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                color: white;
                font-size: 1.25rem;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 3;
            }

            .modal-close:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: scale(1.1);
            }

            .modal-body {
                padding: 2rem;
                max-height: 60vh;
                overflow-y: auto;
            }

            .modal-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }

            .modal-stat-card {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 1.5rem;
                text-align: center;
                transition: transform 0.2s ease;
            }

            .modal-stat-card:hover {
                transform: translateY(-2px);
            }

            .modal-stat-value {
                font-size: 2rem;
                font-weight: 800;
                color: #6366f1;
                margin: 0 0 0.5rem 0;
            }

            .modal-stat-label {
                font-size: 0.875rem;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 500;
            }

            .candidate-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1rem;
            }

            .candidate-item {
                background: white;
                border: 2px solid #f1f5f9;
                border-radius: 12px;
                padding: 1rem;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .candidate-item:hover {
                border-color: #6366f1;
                transform: translateY(-2px);
                box-shadow: 0 8px 25px -5px rgba(99, 102, 241, 0.2);
            }

            .candidate-item::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .candidate-item:hover::before {
                opacity: 1;
            }

            .candidate-name {
                font-size: 1.125rem;
                font-weight: 600;
                color: #1f2937;
                margin: 0 0 0.5rem 0;
            }

            .candidate-details {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-top: 0.75rem;
            }

            .candidate-tag {
                background: #f3f4f6;
                color: #374151;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 500;
            }

            .candidate-tag.hired {
                background: #dcfce7;
                color: #166534;
            }

            .candidate-tag.unqualified {
                background: #fef2f2;
                color: #b91c1c;
            }

            .candidate-tag.high-score {
                background: #fef3c7;
                color: #92400e;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes slideUp {
                from { 
                    opacity: 0;
                    transform: translateY(50px) scale(0.95);
                }
                to { 
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            .no-candidates-message {
                text-align: center;
                padding: 3rem 2rem;
                color: #6b7280;
            }

            .no-candidates-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                opacity: 0.5;
            }
            /* Enhanced Checkbox Styling for Comparison Filters */
            .comparison-form-group-enhanced .dash-checklist {
                font-family: 'Inter', sans-serif;
            }

            .comparison-form-group-enhanced .dash-checklist label {
                cursor: pointer !important;
                transition: all 0.2s ease !important;
                padding: 0.5rem !important;
                border-radius: 6px !important;
                margin: 0.25rem 0 !important;
                display: flex !important;
                align-items: center !important;
            }

            .comparison-form-group-enhanced .dash-checklist label:hover {
                background-color: #f3f4f6 !important;
                color: #1f2937 !important;
            }

            .comparison-form-group-enhanced .dash-checklist input[type="checkbox"] {
                width: 16px !important;
                height: 16px !important;
                margin-right: 0.75rem !important;
                margin-top: 0 !important;
                accent-color: #6366f1 !important;
                cursor: pointer !important;
            }

            .comparison-form-group-enhanced .dash-checklist input[type="checkbox"]:checked + span {
                color: #6366f1 !important;
                font-weight: 500 !important;
            }

            /* Scrollable checkbox container */
            .comparison-form-group-enhanced .dash-checklist {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                background: #fafbfc;
                padding: 1rem;
                max-height: 200px;
                overflow-y: auto;
            }

            /* Scrollbar styling for checkbox containers */
            .comparison-form-group-enhanced .dash-checklist::-webkit-scrollbar {
                width: 6px;
            }

            .comparison-form-group-enhanced .dash-checklist::-webkit-scrollbar-track {
                background: #f1f5f9;
                border-radius: 3px;
            }

            .comparison-form-group-enhanced .dash-checklist::-webkit-scrollbar-thumb {
                background: #cbd5e1;
                border-radius: 3px;
            }

            .comparison-form-group-enhanced .dash-checklist::-webkit-scrollbar-thumb:hover {
                background: #94a3b8;
            }

            /* Ensure proper spacing between checkbox sections */
            .comparison-form-group-enhanced {
                margin-bottom: 2.5rem !important;
                position: relative;
                clear: both;
            }

            /* Fix any remaining dropdown z-index issues for time periods */
            .comparison-form-group-enhanced .dash-dropdown .Select-menu-outer {
                z-index: 9999 !important;
                position: absolute !important;
                background: white !important;
                border: 1px solid #d1d5db !important;
                border-radius: 8px !important;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2) !important;
            }

            /* Enhanced comparison card spacing */
            .enhanced-comparison-card {
                margin-bottom: 3rem !important;
                overflow: visible !important;
            }

            .funnel-comparison-grid {
                gap: 3rem !important;
                padding-bottom: 200px !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

class RecruitmentDataProcessor:
    def __init__(self, df=None):
        self.raw_data = df
        self.cleaned_data = None
        self.candidate_master = None
        self.metrics = {}

    def create_composite_key(self, row):
        """Create a composite key for candidate identification"""
        name = str(row['Candidate Name']).strip() if pd.notna(row['Candidate Name']) else ''
        dob = str(row['Date of Birth']).strip() if pd.notna(row['Date of Birth']) else ''
        nationality = str(row['Nationality']).strip() if pd.notna(row['Nationality']) else ''
        country = str(row['Country of Residence']).strip() if pd.notna(row['Country of Residence']) else ''

        composite = f"{name}_{dob}_{nationality}_{country}"
        return hashlib.md5(composite.encode()).hexdigest()

    def calculate_age_from_dob(self, dob):
        """Calculate age from date of birth"""
        try:
            if pd.isna(dob):
                return None

            if isinstance(dob, str):
                dob = pd.to_datetime(dob, errors='coerce')

            if pd.isna(dob):
                return None

            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        except:
            return None
    def determine_disqualification_reason(self, row):
        """Determine the specific disqualification reason for UNQUALIFIED candidates only"""
        # Safe string conversion to handle NaN and float values
        application_status = str(row.get('Application Status', '')).strip() if pd.notna(row.get('Application Status')) else ''
        interview_status = str(row.get('Interview Status', '')).strip() if pd.notna(row.get('Interview Status')) else ''

        # NEW: Handle special case where Unqualified status is combined with rejection/test failure
        unqualified_with_rejection_or_test_failure = (
            application_status == 'Unqualified' and
            interview_status in ['Rejected', 'Reject Without Email', 'Failed at Test Business Analyst']
        )

        # If this special case, treat as unqualified regardless of other criteria
        if unqualified_with_rejection_or_test_failure:
            return 'Unqualified with Rejection/Test Failure'

        # EXISTING LOGIC: Continue with normal disqualification logic
        if application_status != 'Unqualified':
            return 'Not Unqualified'

        age = self.calculate_age_from_dob(row.get('Date of Birth'))
        country_of_residence = str(row.get('Country of Residence', '')).strip().lower()
        nationality = str(row.get('Nationality', '')).strip().lower()
        speak_arabic = str(row.get('Speak Arabic', '')).strip().lower()

        # Improved age validation - both too young and too old candidates are unqualified
        if age is not None and age >= 27:
            return 'Age >= 27'

        if age is not None and age < 18:
            return 'Age < 18'

        if age == 0 or age is None:
            return 'Age Missing or Invalid'

        if country_of_residence != 'lebanon':
            return 'Country of Residence not Lebanon'

        if speak_arabic not in ['yes', 'true', '1']:
            return 'Does not speak Arabic'

        if nationality != 'lebanon' and nationality != 'lebanese':
            return 'Nationality not Lebanon'

        return 'Unqualified - Unknown Reason'

    def clean_and_deduplicate(self):
        """Clean data and handle duplicate candidates"""
        df = self.raw_data.copy()

        date_columns = ['Created Time (Application)', 'Modified Time (Application)',
                       'Offer Sent On Date', 'Offer Accept Date', 'Date Hired (Application)',
                       'Created Time (Interview)', 'When TestGorilla Done', 'When Sparkhire Done',
                       'Date of Birth']

        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        df.loc[df['Offer Sent On Date'].notna(), 'Application Status'] = 'Hired'
        df['calculated_age'] = df['Date of Birth'].apply(self.calculate_age_from_dob)
        df['disqualification_reason'] = df.apply(self.determine_disqualification_reason, axis=1)
        df['composite_candidate_key'] = df.apply(self.create_composite_key, axis=1)
        df['application_id'] = df.index

        status_priority = {
            'Hired': 5, 'Interviewing': 4, 'Rejected': 3, 'Archived': 2, 'Unqualified': 1,
            'Failed at Test Business Analyst': 3, 'Failed department manager interview': 3,
            'Failed Department Manager Interview': 3, 'Never Booked an Interview': 2,
            'Applied': 1, 'Others': 0
        }

        df['status_priority'] = df['Application Status'].map(
            lambda x: status_priority.get(x, status_priority['Others'])
        )

        # Generate date range column for filtering
        if 'Created Time (Application)' in df.columns:
            df['application_month'] = df['Created Time (Application)'].dt.strftime('%Y-%m')
            # For quarter, convert directly to string to avoid Period object issues
            df['application_quarter'] = df['Created Time (Application)'].apply(
                lambda x: str(pd.Period(x, freq='Q')) if pd.notna(x) else ''
            )
            df['application_year'] = df['Created Time (Application)'].dt.year
            # Add application week
            df['application_week'] = df['Created Time (Application)'].dt.to_period('W').apply(
                lambda x: x.start_time.strftime('%Y-%m-%d') if pd.notna(x) else ''
            )

        self.cleaned_data = df
        return self

    def calculate_custom_funnel_stages(self, row):
        """Calculate custom funnel stages for each application"""
        stages = {'Applied': True}

        # Safe string conversion to handle NaN and float values
        application_status = str(row.get('Application Status', '')).strip() if pd.notna(row.get('Application Status')) else ''
        interview_status = str(row.get('Interview Status', '')).strip() if pd.notna(row.get('Interview Status')) else ''

        # First check if the application is hired or has an offer sent
        # If so, mark all stages as True and return immediately
        is_hired = (application_status == 'Hired' or pd.notna(row.get('Offer Sent On Date', '')))
        if is_hired:
            stages = {
                'Applied': True,
                'Received Test': True,
                'Did Test': True,
                'Passed Test': True,
                'Booked Interview': True,
                'Passed Interview': True,
                'Hired': True
            }
            return stages

        # If candidate has Application Status = "Unqualified", they should not appear in any funnel stage
        # regardless of test scores or other conditions
        immediately_unqualified = application_status == 'Unqualified'
        if immediately_unqualified:
            stages['Received Test'] = False
            stages['Did Test'] = False
            stages['Passed Test'] = False
            stages['Booked Interview'] = False
            stages['Passed Interview'] = False
            stages['Hired'] = False
            return stages

        # If not hired, calculate stages normally
        has_test_score = (pd.notna(row.get('Test Gorilla IQ Score')) or pd.notna(row.get('Maidscc IQ Score')))
        test_related_status = application_status in [
            'Failed at Test Business Analyst', 'Rejected', 'Interviewing',
            'Failed department manager interview', 'Failed Department Manager Interview',
            'Never Booked an Interview', "Mira's Call for Interview Booking"
        ]

        # Special cases for "Never did the test" and "Unqualified"
        never_did_test_with_rejection = (
            application_status == 'Never did the Test' and
            interview_status in ['Rejected', 'Reject Without Email']
        )

        unqualified_with_rejection_or_test_failure = (
            application_status == 'Unqualified' and
            interview_status in ['Rejected', 'Reject Without Email', 'Failed at Test Business Analyst']
        )

        # Rejected without test scores or interview data
        rejected_without_test_or_interview = (
            application_status == 'Rejected' and
            not pd.notna(row.get('Test Gorilla IQ Score')) and
            not pd.notna(row.get('Maidscc IQ Score')) and
            not pd.notna(row.get('Interviewer(s)')) and
            not pd.notna(row.get('Interview Feedback Type'))
        )

        never_did_test_status = application_status == 'Never did the Test'

        stages['Received Test'] = (has_test_score or
                                (test_related_status and not immediately_unqualified) or
                                never_did_test_status or
                                never_did_test_with_rejection or
                                rejected_without_test_or_interview)

        # DID TEST STAGE
        # Check if rejected with Mira's interview (with safe string handling)
        interview_feedback_by = str(row.get('Interview Feedback By', '')).strip() if pd.notna(row.get('Interview Feedback By')) else ''
        interviewer_names = str(row.get('Interviewer(s)', '')).strip() if pd.notna(row.get('Interviewer(s)', '')) else ''

        rejected_with_mira_interview = (
            (interview_status == 'Rejected' and
            interview_feedback_by in ['Mira Jradi', 'Ramzi Jamaleddine']) or
            (interview_status == 'Rejected' and
            any(name in interviewer_names for name in ['Mira Jradi', 'Ramzi Jamaleddine'])) or
            (application_status in ['Failed department manager interview', 'Failed Department Manager Interview'] and
            interview_feedback_by in ['Mira Jradi', 'Ramzi Jamaleddine'])
        )

        # Check if "Never booked an interview" but has Mira/Ramzi as interviewer
        never_booked_but_has_mira_ramzi = (
            application_status == 'Never Booked an Interview' and
            (interview_feedback_by in ['Mira Jradi', 'Ramzi Jamaleddine'] or
            any(name in interviewer_names for name in ['Mira Jradi', 'Ramzi Jamaleddine']))
        )

        # Special exclusion for "Never did the test" with rejection
        exclude_never_did_test_rejection = (
            application_status == 'Never did the Test' and
            interview_status in ['Rejected', 'Reject Without Email']
        )

        stages['Did Test'] = (
            is_hired or  # Already handled above, but keeping for clarity
            rejected_with_mira_interview or
            (application_status != 'Never did the Test' and
            not (application_status == 'Never Booked an Interview' and not never_booked_but_has_mira_ramzi) and
            not exclude_never_did_test_rejection and
            not unqualified_with_rejection_or_test_failure and
            not rejected_without_test_or_interview)
        ) and stages['Received Test']  # Must have received test first

        # PASSED TEST STAGE - FIXED LOGIC
        failed_test_conditions = [
            application_status == 'Failed at Test Business Analyst',
            application_status == 'Unqualified',
            application_status == 'Applied',
            application_status == 'Never did the Test',
            
            # FIXED: Only reject at test stage if score < 80 OR no score at all when rejected by Mira/Ramzi
            (interview_status == 'Rejected' and
            interview_feedback_by in ['Mira Jradi', 'Ramzi Jamaleddine'] and
            (not pd.notna(row.get('Test Gorilla IQ Score')) or row.get('Test Gorilla IQ Score', 0) < 80)),
            
            (interview_status == 'Rejected' and
            any(name in interviewer_names for name in ['Mira Jradi', 'Ramzi Jamaleddine']) and
            (not pd.notna(row.get('Test Gorilla IQ Score')) or row.get('Test Gorilla IQ Score', 0) < 80)),
            
            (interview_feedback_by in ['Mira Jradi', 'Ramzi Jamaleddine'] and
            application_status in ['Failed department manager interview', 'Failed Department Manager Interview']),
            
            (application_status == "Mira's Call for Interview Booking" and
            not (pd.notna(row.get('Test Gorilla IQ Score')) or pd.notna(row.get('Maidscc IQ Score')))),

            # Rejected with test score but no interviewer → Failed Test
            (application_status == 'Rejected' and
            (pd.notna(row.get('Test Gorilla IQ Score')) or pd.notna(row.get('Maidscc IQ Score'))) and
            not pd.notna(row.get('Interview Feedback By')) and
            not pd.notna(row.get('Interviewer(s)'))),

            # Only TestGorilla 60-80 by Mira/Ramzi → Failed Test (scores 80+ pass to interview stage)
            (application_status == 'Rejected' and
            pd.notna(row.get('Test Gorilla IQ Score')) and
            60 <= row.get('Test Gorilla IQ Score', 0) < 80 and
            (interview_feedback_by in ['Mira Jradi', 'Ramzi Jamaleddine'] or
            any(name in interviewer_names for name in ['Mira Jradi', 'Ramzi Jamaleddine'])))
        ]

        stages['Passed Test'] = stages['Did Test'] and not any(failed_test_conditions)

        # BOOKED INTERVIEW STAGE
        # Exclude Mira/Ramzi as they are test-phase, not interview-phase
        # BUT include special case for high TestGorilla scores rejected by Mira
        has_non_mira_ramzi_interviewer = False

        # Check Interview Feedback By field
        if pd.notna(row.get('Interview Feedback By', '')):
            if interview_feedback_by not in ['Mira Jradi', 'Ramzi Jamaleddine']:
                has_non_mira_ramzi_interviewer = True

        # Check Interviewer(s) field for other interviewers
        if pd.notna(row.get('Interviewer(s)', '')):
            # Check if there are any interviewers other than Mira/Ramzi
            interviewer_words = interviewer_names.split()
            has_other_interviewers = any(
                word not in ['Mira', 'Jradi', 'Ramzi', 'Jamaleddine', ',', 'and', '&']
                for word in interviewer_words
                if word.strip()
            )
            if has_other_interviewers:
                has_non_mira_ramzi_interviewer = True

        # Special case for TestGorilla >= 80 rejected by Mira → Booked Interview
        high_score_rejected_by_mira = (
            application_status == 'Rejected' and
            pd.notna(row.get('Test Gorilla IQ Score')) and
            row.get('Test Gorilla IQ Score', 0) >= 80 and
            interview_feedback_by == 'Mira Jradi'
        )

        stages['Booked Interview'] = ((has_non_mira_ramzi_interviewer or high_score_rejected_by_mira) and stages['Passed Test'])

        # PASSED INTERVIEW STAGE - FIXED LOGIC
        failed_interview_conditions = [
            # Regular rejections by non-Mira/Ramzi interviewers
            (interview_status == 'Rejected' and has_non_mira_ramzi_interviewer),
            
            (application_status in ['Failed department manager interview', 'Failed Department Manager Interview'] and has_non_mira_ramzi_interviewer),
            
            (application_status == 'Rejected' and has_non_mira_ramzi_interviewer),

            # FIXED: TestGorilla >= 80 rejected by Mira → Failed Interview (not test)
            high_score_rejected_by_mira,

            # Has test score, rejected, non-Mira/Ramzi interviewer → Failed Department Manager Interview
            (application_status == 'Rejected' and
            (pd.notna(row.get('Test Gorilla IQ Score')) or pd.notna(row.get('Maidscc IQ Score'))) and
            has_non_mira_ramzi_interviewer)
        ]

        stages['Passed Interview'] = stages['Booked Interview'] and not any(failed_interview_conditions)
        stages['Hired'] = False  # Already checked at the beginning and set to False if we reach here

        return stages

    def determine_disqualification_reason(self, row):
       """Determine the specific disqualification reason for UNQUALIFIED candidates only"""
       # Safe string conversion to handle NaN and float values
       application_status = str(row.get('Application Status', '')).strip() if pd.notna(row.get('Application Status')) else ''
       interview_status = str(row.get('Interview Status', '')).strip() if pd.notna(row.get('Interview Status')) else ''

       # NEW: Handle special case where Unqualified status is combined with rejection/test failure
       unqualified_with_rejection_or_test_failure = (
           application_status == 'Unqualified' and
           interview_status in ['Rejected', 'Reject Without Email', 'Failed at Test Business Analyst']
       )

       # If this special case, treat as unqualified regardless of other criteria
       if unqualified_with_rejection_or_test_failure:
           return 'Unqualified with Rejection/Test Failure'

       # EXISTING LOGIC: Continue with normal disqualification logic
       if application_status != 'Unqualified':
           return 'Not Unqualified'

       age = self.calculate_age_from_dob(row.get('Date of Birth'))
       country_of_residence = str(row.get('Country of Residence', '')).strip().lower()
       nationality = str(row.get('Nationality', '')).strip().lower()
       speak_arabic = str(row.get('Speak Arabic', '')).strip().lower()

       # Improved age validation - both too young and too old candidates are unqualified
       if age is not None and age >= 27:
           return 'Age >= 27'

       if age is not None and age < 18:
           return 'Age < 18'

       if age == 0 or age is None:
           return 'Age Missing or Invalid'

       if country_of_residence != 'lebanon':
           return 'Country of Residence not Lebanon'

       if speak_arabic not in ['yes', 'true', '1']:
           return 'Does not speak Arabic'

       if nationality != 'lebanon' and nationality != 'lebanese':
           return 'Nationality not Lebanon'

       return 'Unqualified - Unknown Reason'

    def handle_multiple_applications(self):
       """Handle candidates with multiple applications"""
       df = self.cleaned_data.copy()
       candidate_groups = df.groupby('composite_candidate_key')
       candidate_master = []

       # Calculate duplicate applications properly
       total_applications = len(df)
       unique_candidates = len(candidate_groups)
       duplicate_applications = total_applications - unique_candidates
       applications_per_candidate = round(total_applications / unique_candidates, 2) if unique_candidates > 0 else 0

       # Store key metrics
       self.metrics = {
           'total_applications': total_applications,
           'unique_candidates': unique_candidates,
           'duplicate_applications': duplicate_applications,
           'applications_per_candidate': applications_per_candidate
       }

       for key, group in candidate_groups:
           applications = group.to_dict('records')
           applications.sort(key=lambda x: x['Created Time (Application)'] if pd.notna(x['Created Time (Application)']) else datetime.min)

           # FIRST: Check if candidate was actually hired (has offer sent/accepted/withdrawn)
           is_hired = any([
               app.get('Application Status') == 'Hired' or
               pd.notna(app.get('Offer Sent On Date')) or
               pd.notna(app.get('Offer Accept Date')) or
               pd.notna(app.get('Date Hired (Application)')) or
               str(app.get('Application Status', '')).strip() in ['Offer Sent', 'Offer Accepted', 'Offer Withdrawn']
               for app in applications
           ])

           # SECOND: Check if any application is "Unqualified"
           has_unqualified_application = any([
               str(app.get('Application Status', '')).strip() == 'Unqualified'
               for app in applications
           ])

           # NEW LOGIC: If has unqualified application AND not actually hired, mark as unqualified
           if has_unqualified_application and not is_hired:
               # Force the candidate to be unqualified regardless of other applications
               # Find the unqualified application to use as the base
               unqualified_apps = [app for app in applications if str(app.get('Application Status', '')).strip() == 'Unqualified']
               best_status_row = unqualified_apps[0]  # Use the first unqualified application

               # Set funnel stages to all False for unqualified
               candidate_funnel_stages = {
                   'Applied': True,  # They did apply
                   'Received Test': False,
                   'Did Test': False,
                   'Passed Test': False,
                   'Booked Interview': False,
                   'Passed Interview': False,
                   'Hired': False
               }

               primary_status = 'Unqualified'

           else:
               # EXISTING LOGIC: Use the normal selection process
               def calculate_completeness_score(app):
                   important_fields = [
                       'Candidate Name', 'Date of Birth', 'Nationality', 'Country of Residence',
                       'Age Group', 'Speak Arabic', 'Application Status', 'Posting Title (Job Opening)',
                       'Application Source', 'Test Gorilla IQ Score', 'IQ Rating', 'Interview Feedback By',
                       'Interview Status', 'Interview Feedback', 'Created Time (Interview)',
                       'Offer Sent On Date', 'When TestGorilla Done', 'When Sparkhire Done',
                       'Maidscc IQ Score', 'Interviewer(s)'
                   ]

                   filled_count = 0
                   for field in important_fields:
                       if field in app and pd.notna(app[field]) and str(app[field]).strip() != '':
                           filled_count += 1

                   return filled_count

               for app in applications:
                   app['completeness_score'] = calculate_completeness_score(app)

               max_status_priority = max([app['status_priority'] for app in applications])
               best_status_apps = [app for app in applications if app['status_priority'] == max_status_priority]
               most_complete_app = max(best_status_apps, key=lambda x: x['completeness_score'])
               best_status_row = most_complete_app

               candidate_funnel_stages = {
                   'Applied': True, 'Received Test': False, 'Did Test': False,
                   'Passed Test': False, 'Booked Interview': False, 'Passed Interview': False, 'Hired': False
               }

               if is_hired:
                   candidate_funnel_stages = {
                       'Applied': True, 'Received Test': True, 'Did Test': True,
                       'Passed Test': True, 'Booked Interview': True, 'Passed Interview': True, 'Hired': True
                   }
               else:
                   app_stage_results = []
                   for app in applications:
                       app_stages = self.calculate_custom_funnel_stages(app)
                       app_stage_results.append(app_stages)

                   for stage in ['Received Test', 'Did Test', 'Passed Test', 'Booked Interview', 'Passed Interview']:
                       any_passed = any([app_stages[stage] for app_stages in app_stage_results])
                       candidate_funnel_stages[stage] = any_passed

               primary_status = str(best_status_row['Application Status'])

           # Continue with the rest of the existing logic for creating master record
           all_iq_scores = []
           for app in applications:
               if pd.notna(app.get('Test Gorilla IQ Score')):
                   all_iq_scores.append(app.get('Test Gorilla IQ Score'))
               if pd.notna(app.get('Maidscc IQ Score')):
                   all_iq_scores.append(app.get('Maidscc IQ Score'))

           # Get the best score from either test
           best_iq_score = max(all_iq_scores) if all_iq_scores else 0

           # For backward compatibility, still calculate best_maidscc_score individually
           all_maidscc_scores = [app.get('Maidscc IQ Score') for app in applications if pd.notna(app.get('Maidscc IQ Score'))]
           best_maidscc_score = max(all_maidscc_scores) if all_maidscc_scores else 0

           all_statuses = [app['Application Status'] for app in applications]
           has_conflicting_statuses = len(set(all_statuses)) > 1

           rejected_by_ramzi_mira = any([
               (app.get('Interview Status') == 'Rejected' and
               app.get('Interview Feedback By') in ['Mira Jradi', 'Ramzi Jamaleddine']) or
               (app.get('Application Status') in ['Failed Department Manager Interview', 'Failed department manager interview'] and
               app.get('Interview Feedback By') in ['Mira Jradi', 'Ramzi Jamaleddine']) or
               (app.get('Interview Status') == 'Rejected' and
               pd.notna(app.get('Interviewer(s)', '')) and
               any(name in str(app.get('Interviewer(s)', '')) for name in ['Mira Jradi', 'Ramzi Jamaleddine']))
               for app in applications
           ])

           has_any_test_score = best_iq_score > 0
           all_disqualification_reasons = [app['disqualification_reason'] for app in applications if app['disqualification_reason'] != 'Not Unqualified']
           primary_disqualification_reason = all_disqualification_reasons[0] if all_disqualification_reasons else 'Not Unqualified'
           calculated_age_from_dob = best_status_row.get('calculated_age')

           # Get application date information
           first_application_date = min([app['Created Time (Application)'] for app in applications if pd.notna(app['Created Time (Application)'])], default=None)
           last_application_date = max([app['Created Time (Application)'] for app in applications if pd.notna(app['Created Time (Application)'])], default=None)

           # Safe handling of date information
           application_month = first_application_date.strftime('%Y-%m') if first_application_date else ''
           # Convert Period directly to string to avoid astype error
           application_quarter = str(first_application_date.to_period('Q')) if first_application_date else ''
           application_year = first_application_date.year if first_application_date else None
           # Get week information for first application date
           application_week = first_application_date.to_period('W').start_time.strftime('%Y-%m-%d') if first_application_date else ''

           # Get all job titles applied for
           all_job_titles = [str(app.get('Posting Title (Job Opening)', '')).strip() for app in applications]
           job_titles = ', '.join([title for title in all_job_titles if title])
           earliest_source = str(applications[0]['Application Source']) if applications else ''

           master_record = {
               'composite_candidate_key': key,
               'candidate_name': str(best_status_row['Candidate Name']),
               'date_of_birth': str(best_status_row['Date of Birth']),
               'calculated_age': calculated_age_from_dob,
               'nationality': str(best_status_row['Nationality']),
               'country_of_residence': str(best_status_row['Country of Residence']),
               'age_group': str(best_status_row['Age Group']),
               'speak_arabic': str(best_status_row['Speak Arabic']),
               'disqualification_reason': primary_disqualification_reason,
               'num_applications': len(applications),
               'primary_status': primary_status,  # Use the determined primary_status
               'all_statuses': ', '.join([str(app['Application Status']) for app in applications]),
               'all_posting_titles': job_titles,
               'application_source': earliest_source,
               'application_sources': ', '.join(list(set([str(app['Application Source']) for app in applications]))),
               'first_application_date': str(first_application_date) if first_application_date else '',
               'last_application_date': str(last_application_date) if last_application_date else '',
               'application_month': application_month,
               'application_quarter': application_quarter,
               'application_year': application_year,
               'application_week': application_week,
               'iq_score': best_iq_score,
               'maidscc_score': best_maidscc_score,
               'iq_rating': str(best_status_row['IQ Rating']),
               'has_interview': any([pd.notna(app['Created Time (Interview)']) for app in applications]),
               'has_feedback': any([pd.notna(app['Interview Feedback']) for app in applications]),
               'has_offer': any([pd.notna(app['Offer Sent On Date']) for app in applications]),
               'is_hired': is_hired,
               'completeness_score': best_status_row.get('completeness_score', 0),
               'has_conflicting_statuses': has_conflicting_statuses,
               'rejected_by_ramzi_mira': rejected_by_ramzi_mira,
               'has_any_test_score': has_any_test_score,
               'applied': candidate_funnel_stages['Applied'],
               'received_test': candidate_funnel_stages['Received Test'],
               'did_test': candidate_funnel_stages['Did Test'],  # NEW FIELD
               'passed_test': candidate_funnel_stages['Passed Test'],
               'booked_interview': candidate_funnel_stages['Booked Interview'],
               'passed_interview': candidate_funnel_stages['Passed Interview'],
               'hired': candidate_funnel_stages['Hired']
           }
           candidate_master.append(master_record)

       self.candidate_master = pd.DataFrame(candidate_master)

       # Mark duplicate applications
       df['is_duplicate'] = False
       for key, group in candidate_groups:
           if len(group) > 1:
               # Sort applications by date
               sorted_apps = group.sort_values('Created Time (Application)')
               # Mark all but the first application as duplicates
               duplicate_indices = sorted_apps.index[1:]
               df.loc[duplicate_indices, 'is_duplicate'] = True

       # Add flags for same month reapplication and reapplication after a year
       df['same_month_reapplication'] = False
       df['reapplication_after_year'] = False

       for key, group in candidate_groups:
           if len(group) > 1:
               dates = group['Created Time (Application)'].dropna().sort_values()
               if len(dates) > 1:
                   for i in range(len(dates) - 1):
                       if (dates.iloc[i+1] - dates.iloc[i]).days <= 30:
                           idx = group[group['Created Time (Application)'] == dates.iloc[i+1]].index
                           df.loc[idx, 'same_month_reapplication'] = True

                   for i in range(len(dates) - 1):
                       if (dates.iloc[i+1] - dates.iloc[i]).days > 365:
                           idx = group[group['Created Time (Application)'] == dates.iloc[i+1]].index
                           df.loc[idx, 'reapplication_after_year'] = True

       self.cleaned_data = df
       return self

    def flag_missing_feedback(self):
      """Flag candidates with scheduled interviews but missing feedback"""
      df = self.cleaned_data.copy()
      df['interview_scheduled_no_feedback'] = (
          (df['Created Time (Interview)'].notna()) &
          (df['Interview Feedback'].isna())
      )
      self.cleaned_data = df
      return self

    def process_all(self):
      """Run all processing steps"""
      return (self.clean_and_deduplicate()
              .handle_multiple_applications()
              .flag_missing_feedback())


class RecruitmentAnalytics:
  def __init__(self, cleaned_data, candidate_master, metrics):
      self.cleaned_data = cleaned_data
      self.candidate_master = candidate_master
      self.base_metrics = metrics

  def filter_by_sources(self, selected_sources):
       """Filter candidate master by selected sources"""
       if not selected_sources or 'All Sources' in selected_sources:
           return self.candidate_master

       # Use the new application_source field which has only the earliest source
       filtered_master = self.candidate_master[
           self.candidate_master['application_source'].isin(selected_sources)
       ]
       return filtered_master

  def filter_by_job_titles(self, selected_job_titles, filtered_master=None):
      """Filter by job titles"""
      master = filtered_master if filtered_master is not None else self.candidate_master

      if not selected_job_titles or len(selected_job_titles) == 0:
          return master

      filtered = master[
          master['all_posting_titles'].apply(
              lambda x: any(title in str(x) for title in selected_job_titles)
          )
      ]
      return filtered

  def filter_by_date_range(self, date_range_type, selected_values, custom_date_range=None, filtered_master=None):
      """Filter by application date range"""
      master = filtered_master if filtered_master is not None else self.candidate_master

      # Handle empty master case
      if master is None or len(master) == 0:
          return master

      if date_range_type == 'custom' and custom_date_range:
          # Handle custom date range filtering
          start_date, end_date = custom_date_range
          if start_date and end_date:
              start_date = pd.to_datetime(start_date)
              end_date = pd.to_datetime(end_date)

              # Convert first_application_date to datetime for comparison
              master_dates = pd.to_datetime(master['first_application_date'], errors='coerce')

              filtered = master[
                  (master_dates.dt.date >= start_date.date()) &
                  (master_dates.dt.date <= end_date.date())
              ]
              return filtered
          return master

      if not selected_values or 'All' in selected_values:
          return master

      if date_range_type == 'week':
          # Convert date strings to week start dates for comparison
          filtered = master[master['application_week'].isin(selected_values)]
      elif date_range_type == 'month':
          filtered = master[master['application_month'].isin(selected_values)]
      elif date_range_type == 'quarter':
          filtered = master[master['application_quarter'].isin(selected_values)]
      elif date_range_type == 'year':
          # Convert years to integers for proper comparison
          year_values = [int(y) for y in selected_values if str(y).isdigit()]
          filtered = master[master['application_year'].isin(year_values)]
      else:
          filtered = master

      return filtered

  def calculate_funnel_metrics(self, filtered_master=None):
   """Calculate custom funnel conversion metrics for qualified candidates only"""
   master = filtered_master if filtered_master is not None else self.candidate_master
   qualified_master = master[master['primary_status'] != 'Unqualified']

   # Ensure we have at least empty dataframe with right structure
   if len(qualified_master) == 0:
       return {
           'funnel_data': {
               'Applied': 0, 'Received Test': 0, 'Did Test': 0,  # ADD Did Test
               'Passed Test': 0, 'Booked Interview': 0, 'Passed Interview': 0, 'Hired': 0
           },
           'conversions': {}
       }

   funnel_data = {
       'Applied': len(qualified_master),
       'Received Test': qualified_master['received_test'].sum(),
       'Did Test': qualified_master['did_test'].sum(),  # NEW STAGE
       'Passed Test': qualified_master['passed_test'].sum(),
       'Booked Interview': qualified_master['booked_interview'].sum(),
       'Passed Interview': qualified_master['passed_interview'].sum(),
       'Hired': qualified_master['hired'].sum()
   }

   conversions = {}
   stages = list(funnel_data.keys())
   for i in range(len(stages) - 1):
       from_stage = stages[i]
       to_stage = stages[i + 1]
       if funnel_data[from_stage] > 0:
           rate = (funnel_data[to_stage] / funnel_data[from_stage]) * 100
           conversions[f"{from_stage} → {to_stage}"] = round(rate, 2)

   return {'funnel_data': funnel_data, 'conversions': conversions}

  def get_candidates_by_stage(self, filtered_master=None):
       """Get candidate names for each funnel stage (qualified candidates only)"""
       master = filtered_master if filtered_master is not None else self.candidate_master
       qualified_master = master[master['primary_status'] != 'Unqualified']

       candidates_by_stage = {}
       stages = ['applied', 'received_test', 'did_test', 'passed_test', 'booked_interview', 'passed_interview', 'hired']  # ADD did_test
       stage_labels = ['Applied (Qualified)', 'Received Test', 'Did Test', 'Passed Test', 'Booked Interview', 'Passed Interview', 'Hired']  # ADD Did Test

       for stage, label in zip(stages, stage_labels):
           if stage == 'applied':
               candidates_in_stage = qualified_master['candidate_name'].tolist()
           else:
               candidates_in_stage = qualified_master[qualified_master[stage] == True]['candidate_name'].tolist()
           candidates_by_stage[label] = candidates_in_stage

       return candidates_by_stage

  def analyze_unqualified_candidates(self, selected_sources=None, filtered_master=None):
      """Analyze characteristics of unqualified candidates with detailed disqualification reasons"""
      if filtered_master is not None:
          filtered_keys = set(filtered_master['composite_candidate_key'])
          unqualified = self.cleaned_data[
              (self.cleaned_data['Application Status'] == 'Unqualified') &
              (self.cleaned_data['composite_candidate_key'].isin(filtered_keys))
          ]
      elif selected_sources and 'All Sources' not in selected_sources:
          unqualified = self.cleaned_data[
              (self.cleaned_data['Application Status'] == 'Unqualified') &
              (self.cleaned_data['Application Source'].isin(selected_sources))
          ]
      else:
          unqualified = self.cleaned_data[self.cleaned_data['Application Status'] == 'Unqualified']

      if len(unqualified) == 0:
          return {
              'by_age_group': {},
              'by_calculated_age': {},
              'by_country': {},
              'by_nationality': {},
              'by_arabic_speaking': {},
              'by_source': {},
              'by_disqualification_reason': {},
              'total_unqualified': 0,
              'percentage_of_total': 0
          }

      disqualification_breakdown = unqualified['disqualification_reason'].value_counts().to_dict()

      by_calculated_age = {}
      if 'calculated_age' in unqualified.columns:
          # Only process candidates with valid age data
          age_groups = unqualified['calculated_age'].dropna()
          if len(age_groups) > 0:
              age_bins = [0, 18, 22, 24, 26, 27, 30, 35, 100]
              age_labels = ['<18', '18-21', '22-23', '24-25', '26', '27-29', '30-34', '35+']
              age_categories = pd.cut(age_groups, bins=age_bins, labels=age_labels, right=False)
              by_calculated_age = age_categories.value_counts().to_dict()

      return {
          'by_age_group': unqualified['Age Group'].value_counts().to_dict() if 'Age Group' in unqualified.columns else {},
          'by_calculated_age': by_calculated_age,
          'by_country': unqualified['Country of Residence'].value_counts().to_dict() if 'Country of Residence' in unqualified.columns else {},
          'by_nationality': unqualified['Nationality'].value_counts().to_dict() if 'Nationality' in unqualified.columns else {},
          'by_arabic_speaking': unqualified['Speak Arabic'].value_counts().to_dict() if 'Speak Arabic' in unqualified.columns else {},
          'by_source': unqualified['Application Source'].value_counts().to_dict() if 'Application Source' in unqualified.columns else {},
          'by_disqualification_reason': disqualification_breakdown,
          'total_unqualified': len(unqualified),
          'percentage_of_total': (len(unqualified) / len(self.cleaned_data)) * 100 if len(self.cleaned_data) > 0 else 0
      }

  def analyze_age_distribution(self, selected_sources=None, filtered_master=None):
      """Analyze age distribution of candidates using calculated age from Date of Birth"""
      if filtered_master is not None:
          master = filtered_master
      elif selected_sources and 'All Sources' not in selected_sources:
          filtered_keys = set()
          for source in selected_sources:
              source_candidates = self.candidate_master[
                  self.candidate_master['application_sources'].str.contains(str(source), na=False)
              ]
              filtered_keys.update(source_candidates['composite_candidate_key'])

          master = self.candidate_master[
              self.candidate_master['composite_candidate_key'].isin(filtered_keys)
          ]
      else:
          master = self.candidate_master

      # Only process candidates with valid age data
      valid_ages = master[master['calculated_age'].notna()].copy()

      if len(valid_ages) == 0:
          return pd.DataFrame(columns=['age_group', 'total_candidates', 'unqualified', 'hired', 'qualified', 'unqualified_rate', 'hire_rate'])

      # Create age bins and labels
      age_bins = [0, 18, 22, 24, 26, 27, 30, 35, 100]
      age_labels = ['<18', '18-21', '22-23', '24-25', '26', '27-29', '30-34', '35+']

      # Create a completely new column instead of trying to modify an existing categorical
      # This avoids the "Cannot setitem on a Categorical with a new category" error
      valid_ages['age_group_temp'] = pd.cut(valid_ages['calculated_age'],
                                          bins=age_bins,
                                          labels=age_labels,
                                          right=False)

      # Convert categorical to string to avoid issues with aggregation
      valid_ages['age_group_calculated'] = valid_ages['age_group_temp'].astype(str)

      # Group by age and calculate metrics using the string version of the age group
      age_distribution = valid_ages.groupby('age_group_calculated').agg({
          'composite_candidate_key': 'count',  # Use a guaranteed column
          'primary_status': lambda x: (x == 'Unqualified').sum(),
          'hired': 'sum'
      }).reset_index()

      age_distribution.columns = ['age_group', 'total_candidates', 'unqualified', 'hired']

      # Fill NaN values with 0
      age_distribution = age_distribution.fillna(0)

      # Convert columns to numeric
      for col in ['total_candidates', 'unqualified', 'hired']:
          age_distribution[col] = pd.to_numeric(age_distribution[col], errors='coerce').fillna(0).astype(int)

      age_distribution['qualified'] = age_distribution['total_candidates'] - age_distribution['unqualified']

      # Calculate rates, avoiding division by zero
      age_distribution['unqualified_rate'] = age_distribution.apply(
          lambda row: (row['unqualified'] / row['total_candidates'] * 100) if row['total_candidates'] > 0 else 0,
          axis=1
      ).round(1)

      age_distribution['hire_rate'] = age_distribution.apply(
          lambda row: (row['hired'] / row['total_candidates'] * 100) if row['total_candidates'] > 0 else 0,
          axis=1
      ).round(1)

      # Sort by the defined age order
      age_order = {
          '<18': 0, '18-21': 1, '22-23': 2, '24-25': 3, '26': 4,
          '27-29': 5, '30-34': 6, '35+': 7
      }
      age_distribution['sort_order'] = age_distribution['age_group'].map(age_order)
      age_distribution = age_distribution.sort_values('sort_order').drop('sort_order', axis=1)

      return age_distribution

  def source_performance_analysis(self, selected_sources=None, filtered_master=None):
      """Analyze performance by application source with correct calculations"""
      source_analysis = []

      if filtered_master is not None:
          filtered_keys = set(filtered_master['composite_candidate_key'])
          filtered_data = self.cleaned_data[self.cleaned_data['composite_candidate_key'].isin(filtered_keys)]
          sources = filtered_data['Application Source'].dropna().unique() if 'Application Source' in filtered_data.columns else []
      elif selected_sources and 'All Sources' not in selected_sources:
          sources = selected_sources
          filtered_data = self.cleaned_data
      else:
          sources = self.cleaned_data['Application Source'].dropna().unique() if 'Application Source' in self.cleaned_data.columns else []
          filtered_data = self.cleaned_data

      # Return empty dataframe if no sources
      if len(sources) == 0:
          return pd.DataFrame(columns=[
              'source', 'total_applications', 'unique_candidates', 'qualified_candidates',
              'qualification_rate', 'hired', 'hire_rate', 'hire_rate_from_qualified',
              'avg_iq_score', 'avg_calculated_age', 'applications_per_candidate'
          ])

      for source in sources:
          # Get all applications for this source
          source_data = filtered_data[filtered_data['Application Source'] == source]

          if filtered_master is not None:
              source_data = source_data[source_data['composite_candidate_key'].isin(filtered_keys)]

          # Get unique candidates that applied through this source
          source_candidates = self.candidate_master[
              self.candidate_master['application_sources'].str.contains(str(source), na=False)
          ]

          if filtered_master is not None:
              source_candidates = source_candidates[source_candidates['composite_candidate_key'].isin(filtered_keys)]

          # Calculate metrics based on unique candidates, not applications
          total_apps = len(source_data)
          unique_candidates = len(source_candidates)
          qualified_candidates = len(source_candidates[source_candidates['primary_status'] != 'Unqualified'])
          hired = int(source_candidates['hired'].sum())

          # Improve IQ score calculation to use both Test Gorilla and Maidscc scores
          iq_scores = []
          if 'Test Gorilla IQ Score' in source_data.columns:
              test_gorilla_scores = source_data['Test Gorilla IQ Score'].dropna().tolist()
              iq_scores.extend(test_gorilla_scores)

          if 'Maidscc IQ Score' in source_data.columns:
              maidscc_scores = source_data['Maidscc IQ Score'].dropna().tolist()
              iq_scores.extend(maidscc_scores)

          avg_iq = np.mean(iq_scores) if iq_scores else None

          # Safely calculate averages
          avg_calculated_age = source_candidates['calculated_age'].mean() if 'calculated_age' in source_candidates.columns else None

          # Calculate source metrics safely - CORRECTED HIRE RATE CALCULATION
          qualification_rate = round(qualified_candidates / unique_candidates * 100, 1) if unique_candidates > 0 else 0
          hire_rate = round(hired / unique_candidates * 100, 1) if unique_candidates > 0 else 0
          hire_rate_from_qualified = round(hired / qualified_candidates * 100, 1) if qualified_candidates > 0 else 0

          source_analysis.append({
              'source': source,
              'total_applications': total_apps,
              'unique_candidates': unique_candidates,
              'qualified_candidates': qualified_candidates,
              'qualification_rate': qualification_rate,
              'hired': hired,
              'hire_rate': hire_rate,
              'hire_rate_from_qualified': hire_rate_from_qualified,
              'avg_iq_score': round(avg_iq, 1) if pd.notna(avg_iq) else 0,
              'avg_calculated_age': round(avg_calculated_age, 1) if pd.notna(avg_calculated_age) else 0,
              'applications_per_candidate': round(total_apps / unique_candidates, 2) if unique_candidates > 0 else 0
          })

      result_df = pd.DataFrame(source_analysis)
      if not result_df.empty:
          # Sort by unique candidates instead of qualification rate to show most popular sources
          result_df = result_df.sort_values('unique_candidates', ascending=False)
      return result_df

  def time_based_analysis(self, selected_sources=None, filtered_master=None, qualified_only=False):
      """Analyze application patterns over time"""
      if filtered_master is not None:
          filtered_keys = set(filtered_master['composite_candidate_key'])
          data = self.cleaned_data[self.cleaned_data['composite_candidate_key'].isin(filtered_keys)].copy()
      else:
          data = self.cleaned_data.copy()

      if selected_sources and 'All Sources' not in selected_sources:
          data = data[data['Application Source'].isin(selected_sources)]

      if qualified_only:
          data = data[data['Application Status'] != 'Unqualified']

      # Check if there's time data to analyze
      if 'Created Time (Application)' not in data.columns or len(data) == 0:
          return {
              'monthly_applications': {},
              'monthly_hiring_rate': {}
          }

      data['Created Time (Application)'] = pd.to_datetime(data['Created Time (Application)'], errors='coerce')
      data = data[data['Created Time (Application)'].notna()]

      if len(data) == 0:
          return {
              'monthly_applications': {},
              'monthly_hiring_rate': {}
          }

      data['application_month'] = data['Created Time (Application)'].dt.to_period('M')

      monthly_apps = data.groupby('application_month').size()

      # Group by month and status for hiring rate
      if 'Application Status' in data.columns:
          monthly_hiring = data.groupby(['application_month', 'Application Status']).size().unstack(fill_value=0)

          if 'Hired' in monthly_hiring.columns:
              monthly_hiring_rate = (monthly_hiring['Hired'] / monthly_hiring.sum(axis=1)) * 100
          else:
              monthly_hiring_rate = pd.Series()
      else:
          monthly_hiring_rate = pd.Series()

      return {
          'monthly_applications': {str(k): int(v) for k, v in monthly_apps.to_dict().items()},
          'monthly_hiring_rate': {str(k): float(v) for k, v in monthly_hiring_rate.to_dict().items()}
      }

  def get_date_range_options(self):
      """Get available date ranges for filtering"""
      date_options = {
          'week': [{'label': '🌟 All Weeks', 'value': 'All'}],
          'month': [{'label': '🌟 All Months', 'value': 'All'}],
          'quarter': [{'label': '🌟 All Quarters', 'value': 'All'}],
          'year': [{'label': '🌟 All Years', 'value': 'All'}],
          'custom': []  # No options needed for custom date range
      }

      # Check if data is available
      if self.candidate_master is None or len(self.candidate_master) == 0:
          return date_options

      # Get weeks
      if 'application_week' in self.candidate_master.columns:
          weeks = sorted(self.candidate_master['application_week'].dropna().unique())
          week_options = []
          for week_start in weeks:
              if week_start and pd.notna(week_start):
                  week_start_date = pd.to_datetime(week_start)
                  week_end_date = week_start_date + pd.Timedelta(days=6)
                  week_label = f"📅 {week_start_date.strftime('%Y-%m-%d')} to {week_end_date.strftime('%Y-%m-%d')}"
                  week_options.append({'label': week_label, 'value': week_start})
          date_options['week'].extend(week_options)

      # Get months - IMPROVED to ensure all months are captured
      if 'application_month' in self.candidate_master.columns:
          # Get unique months and ensure they're properly formatted
          months = self.candidate_master['application_month'].dropna().unique()
          # Convert to list and remove empty strings
          months = [str(m) for m in months if m and pd.notna(m) and str(m).strip() != '']
          # Sort chronologically
          months = sorted(set(months))
          month_options = [{'label': f"📅 {month}", 'value': month} for month in months]
          date_options['month'].extend(month_options)
      
      # Alternative: Get months from the cleaned_data if candidate_master doesn't have all months
      if hasattr(self, 'cleaned_data') and 'application_month' in self.cleaned_data.columns:
          additional_months = self.cleaned_data['application_month'].dropna().unique()
          additional_months = [str(m) for m in additional_months if m and pd.notna(m) and str(m).strip() != '']
          # Combine with existing months
          all_months = sorted(set(months + list(additional_months)) if 'months' in locals() else additional_months)
          month_options = [{'label': f"📅 {month}", 'value': month} for month in all_months]
          date_options['month'] = [{'label': '🌟 All Months', 'value': 'All'}] + month_options

      # Get quarters - IMPROVED to ensure all quarters are captured
      if 'application_quarter' in self.candidate_master.columns:
          quarters = self.candidate_master['application_quarter'].dropna().unique()
          quarters = [str(q) for q in quarters if q and pd.notna(q) and str(q).strip() != '']
          quarters = sorted(set(quarters))
          quarter_options = [{'label': f"📊 {quarter}", 'value': quarter} for quarter in quarters]
          date_options['quarter'].extend(quarter_options)
      
      # Alternative: Get quarters from the cleaned_data
      if hasattr(self, 'cleaned_data') and 'application_quarter' in self.cleaned_data.columns:
          additional_quarters = self.cleaned_data['application_quarter'].dropna().unique()
          additional_quarters = [str(q) for q in additional_quarters if q and pd.notna(q) and str(q).strip() != '']
          all_quarters = sorted(set(quarters + list(additional_quarters)) if 'quarters' in locals() else additional_quarters)
          quarter_options = [{'label': f"📊 {quarter}", 'value': quarter} for quarter in all_quarters]
          date_options['quarter'] = [{'label': '🌟 All Quarters', 'value': 'All'}] + quarter_options

      # Get years
      if 'application_year' in self.candidate_master.columns:
          years = sorted(self.candidate_master['application_year'].dropna().unique())
          # Convert years to int first to ensure proper sorting
          valid_years = [y for y in years if pd.notna(y)]
          year_options = [{'label': f"📆 {int(year)}", 'value': int(year)} for year in valid_years]
          date_options['year'].extend(year_options)

      return date_options
  def get_candidates_by_stage_detailed(self, filtered_master=None):
        """Get detailed candidate information for each funnel stage (qualified candidates only)"""
        master = filtered_master if filtered_master is not None else self.candidate_master
        qualified_master = master[master['primary_status'] != 'Unqualified']

        candidates_by_stage_detailed = {}
        stages = ['applied', 'received_test', 'did_test', 'passed_test', 'booked_interview', 'passed_interview', 'hired']
        stage_labels = ['Applied (Qualified)', 'Received Test', 'Did Test', 'Passed Test', 'Booked Interview', 'Passed Interview', 'Hired']

        for stage, label in zip(stages, stage_labels):
            if stage == 'applied':
                candidates_in_stage = qualified_master[['candidate_name', 'composite_candidate_key', 'calculated_age', 'primary_status', 'all_posting_titles']].to_dict('records')
            else:
                stage_candidates = qualified_master[qualified_master[stage] == True]
                candidates_in_stage = stage_candidates[['candidate_name', 'composite_candidate_key', 'calculated_age', 'primary_status', 'all_posting_titles']].to_dict('records')
            
            candidates_by_stage_detailed[label] = candidates_in_stage

        return candidates_by_stage_detailed

  def generate_summary_metrics(self, filtered_master=None):
      """Generate key summary metrics with accurate calculations"""
      master = filtered_master if filtered_master is not None else self.candidate_master

      # Handle empty dataframe case
      if master is None or len(master) == 0:
          return {
              'total_applications': 0,
              'unique_candidates': 0,
              'unique_applicants': 0,
              'applications_per_candidate': 0,
              'duplicate_applications': 0,
              'total_unqualified': 0,
              'unqualified_rate': 0,
              'qualified_candidates': 0,
              'qualification_rate': 0,
              'total_hired': 0,
              'overall_hire_rate': 0,
              'hire_rate_from_qualified': 0,
              'total_rejected': 0,
              'avg_calculated_age': 0,
              'interviews_without_feedback': 0,
              'reapplications_after_year': 0
          }

      if filtered_master is not None:
          filtered_keys = set(master['composite_candidate_key'])
          filtered_cleaned_data = self.cleaned_data[
              self.cleaned_data['composite_candidate_key'].isin(filtered_keys)
          ]
      else:
          filtered_cleaned_data = self.cleaned_data

      # Total applications from this filtered set
      total_apps = len(filtered_cleaned_data)

      # Unique candidates in this filtered set
      unique_candidates = len(master)

      # Count actual duplicate applications within this filtered set
      duplicate_apps = total_apps - unique_candidates

      # Count qualified and unqualified candidates correctly
      unqualified_count = (master['primary_status'] == 'Unqualified').sum()
      qualified_count = unique_candidates - unqualified_count

      # Calculate average age correctly
      avg_calculated_age = master['calculated_age'].mean() if 'calculated_age' in master.columns else None

      # Count interview feedback issues
      interview_no_feedback = filtered_cleaned_data['interview_scheduled_no_feedback'].sum() if 'interview_scheduled_no_feedback' in filtered_cleaned_data.columns else 0

      # Calculate actual hire rate correctly - based on unique candidates
      hired_count = master['hired'].sum() if 'hired' in master.columns else 0

      # Count rejected applications
      rejected_count = (filtered_cleaned_data['Application Status'] == 'Rejected').sum() if 'Application Status' in filtered_cleaned_data.columns else 0

       # Count reapplications
      reapplications = filtered_cleaned_data['reapplication_after_year'].sum() if 'reapplication_after_year' in filtered_cleaned_data.columns else 0

      return {
          'total_applications': int(total_apps),
          'unique_candidates': int(unique_candidates),
          'unique_applicants': int(unique_candidates),  # Added for clarity
          'applications_per_candidate': round(total_apps / unique_candidates, 2) if unique_candidates > 0 else 0,
          'duplicate_applications': int(duplicate_apps),
          'total_unqualified': int(unqualified_count),
          'unqualified_rate': round((unqualified_count / unique_candidates * 100), 1) if unique_candidates > 0 else 0,
          'qualified_candidates': int(qualified_count),
          'qualification_rate': round((qualified_count / unique_candidates * 100), 1) if unique_candidates > 0 else 0,
          'total_hired': int(hired_count),
          'overall_hire_rate': round((hired_count / unique_candidates * 100), 1) if unique_candidates > 0 else 0,
          'hire_rate_from_qualified': round((hired_count / qualified_count * 100), 1) if qualified_count > 0 else 0,
          'total_rejected': int(rejected_count),
          'avg_calculated_age': round(avg_calculated_age, 1) if pd.notna(avg_calculated_age) else 0,
          'interviews_without_feedback': int(interview_no_feedback),
          'reapplications_after_year': int(reapplications)
      }

  def calculate_comparison_funnel_metrics(self, comparison_filters):
    """Calculate funnel metrics for comparison across different dimensions - WITH ALL STAGES"""
    comparison_results = {}
    
    for comparison_name, filters in comparison_filters.items():
        # Apply filters to get the subset of data
        filtered_master = self.candidate_master.copy()
        
        # Apply source filter
        if filters.get('sources') and len(filters['sources']) > 0:
            filtered_master = filtered_master[
                filtered_master['application_source'].isin(filters['sources'])
            ]
        
        # Apply job title filter
        if filters.get('job_titles') and len(filters['job_titles']) > 0:
            filtered_master = filtered_master[
                filtered_master['all_posting_titles'].apply(
                    lambda x: any(title in str(x) for title in filters['job_titles'])
                )
            ]
        
        # Apply date range filter
        if filters.get('date_range_type') and filters.get('date_values'):
            filtered_master = self.filter_by_date_range(
                filters['date_range_type'], 
                filters['date_values'], 
                filters.get('custom_date_range'),
                filtered_master
            )
        
        # Calculate funnel metrics for this filtered set - THIS INCLUDES ALL 7 STAGES
        funnel_metrics = self.calculate_funnel_metrics(filtered_master)
        summary_metrics = self.generate_summary_metrics(filtered_master)
        
        comparison_results[comparison_name] = {
            'funnel_data': funnel_metrics['funnel_data'],  # This contains all 7 stages
            'conversions': funnel_metrics['conversions'],  # This contains all 6 conversions
            'summary_metrics': summary_metrics,
            'filter_description': self._format_filter_description(filters)
        }
    
    return comparison_results

  def _format_filter_description(self, filters):
      """Format filter description for display"""
      parts = []
      
      if filters.get('sources') and 'All Sources' not in filters['sources']:
          parts.append(f"Sources: {', '.join(filters['sources'])}")
      
      if filters.get('job_titles'):
          parts.append(f"Jobs: {', '.join(filters['job_titles'])}")
      
      if filters.get('date_range_type') and filters.get('date_values'):
          if filters['date_range_type'] == 'custom' and filters.get('custom_date_range'):
              start_date, end_date = filters['custom_date_range']
              parts.append(f"Date: {start_date} to {end_date}")
          elif filters.get('date_values') and 'All' not in filters['date_values']:
              date_str = ', '.join(map(str, filters['date_values']))
              parts.append(f"{filters['date_range_type'].title()}: {date_str}")
      
      return '; '.join(parts) if parts else 'All Data'

# Create helper functions for enhanced components
def create_modern_metric_card(title, value, icon, color, subtitle=None, trend=None):
  """Create a modern metric card with enhanced styling"""
  return html.Div([
      html.Div([
          html.Div([
              html.I(className=f"fas {icon}", style={
                  'fontSize': '2rem',
                  'color': f'var(--{color}-color)',
                  'marginBottom': '1rem'
              }),
              html.H2(str(value), className="metric-value", style={'color': f'var(--{color}-color)'}),
              html.P(title, className="metric-label"),
              html.P(subtitle, className="metric-subtitle") if subtitle else None,
              html.Div([
                  html.I(className=f"fas fa-arrow-{trend['direction']}", style={
                      'color': '#10b981' if trend['direction'] == 'up' else '#ef4444',
                      'marginRight': '0.5rem'
                  }),
                  html.Span(f"{trend['value']}%", style={
                      'color': '#10b981' if trend['direction'] == 'up' else '#ef4444',
                      'fontSize': '0.875rem',
                      'fontWeight': '500'
                  })
              ], style={'marginTop': '0.5rem'}) if trend else None
          ], style={'textAlign': 'center', 'padding': '2rem'})
      ], className="metric-card")
  ])

def create_enhanced_plotly_theme(fig, title):
  """Apply modern styling to Plotly figures with improved spacing"""
  fig.update_layout(
      title={
          'text': title,
          'x': 0.5,
          'xanchor': 'center',
          'y': 0.95,
          'font': {'size': 22, 'family': 'Inter', 'color': '#1f2937'}
      },
      font={'family': 'Inter', 'color': '#374151'},
      plot_bgcolor='rgba(0,0,0,0)',
      paper_bgcolor='rgba(0,0,0,0)',
      margin={'t': 80, 'b': 70, 'l': 70, 'r': 70},  # Increased margins for better spacing
      showlegend=True,
      legend={
          'orientation': 'h',
          'yanchor': 'bottom',
          'y': -0.25,  # Moved legend down for better separation
          'xanchor': 'center',
          'x': 0.5,
          'bgcolor': 'rgba(255,255,255,0.9)',
          'bordercolor': '#e5e7eb',
          'borderwidth': 1,
          'font': {'size': 12}
      },
      modebar={
          'bgcolor': 'rgba(255,255,255,0.8)',
          'color': '#6b7280',
          'activecolor': '#6366f1'
      }
  )

  # Update axes with modern styling and improved spacing
  fig.update_xaxes(
      gridcolor='#f3f4f6',
      linecolor='#e5e7eb',
      tickfont={'family': 'Inter', 'size': 12, 'color': '#6b7280'},
      titlefont={'family': 'Inter', 'size': 14, 'color': '#374151'},
      showgrid=True,
      gridwidth=1,
      tickangle=0,  # Horizontal tick labels by default
      title_standoff=15  # More space for title
  )
  fig.update_yaxes(
      gridcolor='#f3f4f6',
      linecolor='#e5e7eb',
      tickfont={'family': 'Inter', 'size': 12, 'color': '#6b7280'},
      titlefont={'family': 'Inter', 'size': 14, 'color': '#374151'},
      showgrid=True,
      gridwidth=1,
      title_standoff=15  # More space for title
  )

  return fig

def create_modern_table(df, table_id, color_scheme='primary'):
  """Create a modern styled data table"""
  # Handle empty dataframe case
  if df is None or len(df) == 0:
      empty_df = pd.DataFrame(columns=['No Data Available'])
      return dash_table.DataTable(
          id=table_id,
          data=[{'No Data Available': 'No data to display'}],
          columns=[{"name": 'No Data Available', "id": 'No Data Available'}],
          style_table={'overflowX': 'auto', 'borderRadius': '16px'},
          style_header={
              'backgroundColor': f'var(--{color_scheme}-color)',
              'color': 'white',
              'fontWeight': '600',
              'textAlign': 'center'
          },
          style_cell={'textAlign': 'center'}
      )

  return dash_table.DataTable(
      id=table_id,
      data=df.to_dict('records'),
      columns=[{"name": col.replace('_', ' ').title(), "id": col} for col in df.columns],
      style_table={
          'overflowX': 'auto',
          'borderRadius': '16px',
          'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          'border': '1px solid #e5e7eb'
      },
      style_header={
          'backgroundColor': f'var(--{color_scheme}-color)',
          'color': 'white',
          'fontWeight': '600',
          'fontSize': '14px',
          'fontFamily': 'Inter',
          'textAlign': 'center',
          'padding': '16px',
          'border': 'none'
      },
      style_cell={
          'textAlign': 'left',
          'padding': '12px 16px',
          'fontFamily': 'Inter',
          'fontSize': '14px',
          'border': '1px solid #f3f4f6',
          'backgroundColor': 'white',
          'overflow': 'hidden',
          'textOverflow': 'ellipsis',
          'maxWidth': 300,
      },
      style_data={
          'border': '1px solid #f3f4f6',
          'whiteSpace': 'normal',
          'height': 'auto',
      },
      style_data_conditional=[
          {
              'if': {'row_index': 'odd'},
              'backgroundColor': '#f9fafb'
          }
      ],
      page_size=15,
      sort_action="native",
      filter_action="native",
      style_filter={
          'backgroundColor': '#f3f4f6',
          'border': '1px solid #e5e7eb',
          'borderRadius': '8px',
          'padding': '8px'
      },
      tooltip_delay=0,
      tooltip_duration=None
  )

def create_funnel_comparison_chart(comparison_results):
    """Create a comparison chart for multiple funnels with ALL stages"""
    fig = go.Figure()
    
    colors = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b', '#06b6d4']
    
    # Define the complete stage order - SAME AS OVERVIEW TAB
    complete_stage_order = ['Applied', 'Received Test', 'Did Test', 'Passed Test', 'Booked Interview', 'Passed Interview', 'Hired']
    
    for i, (name, result) in enumerate(comparison_results.items()):
        funnel_data = result['funnel_data']
        color = colors[i % len(colors)]
        
        # Ensure all stages are present with the correct order
        ordered_values = []
        for stage in complete_stage_order:
            ordered_values.append(funnel_data.get(stage, 0))
        
        fig.add_trace(go.Scatter(
            x=complete_stage_order,  # Use complete stage order
            y=ordered_values,        # Use ordered values
            mode='lines+markers+text',
            name=name,
            line=dict(color=color, width=4),
            marker=dict(size=12, color=color, line=dict(width=2, color='white')),
            text=[f"{v:,}" for v in ordered_values],
            textposition="top center",
            textfont=dict(size=12, color=color, family='Inter'),
            hovertemplate=f'<b>{name}</b><br>' +
                         '<b>%{x}</b><br>' +
                         'Count: %{y:,}<extra></extra>'
        ))
    
    fig = create_enhanced_plotly_theme(fig, "Funnel Comparison - All Stages")
    fig.update_layout(
        height=600,
        xaxis_title="Funnel Stages",
        yaxis_title="Candidates",
        hovermode='x unified'
    )
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_conversion_comparison_chart(comparison_results):
    """Create a comparison chart for conversion rates with ALL stages"""
    fig = go.Figure()
    
    colors = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b', '#06b6d4']
    
    # Get all unique conversion stages - COMPLETE LIST
    all_conversions = set()
    for result in comparison_results.values():
        all_conversions.update(result['conversions'].keys())
    
    # Define the expected conversion order - SAME AS OVERVIEW TAB
    expected_conversions = [
        'Applied → Received Test',
        'Received Test → Did Test',      # ← This was missing!
        'Did Test → Passed Test',
        'Passed Test → Booked Interview',
        'Booked Interview → Passed Interview',
        'Passed Interview → Hired'
    ]
    
    # Use only the conversions that exist in the data, in the correct order
    conversion_stages = [conv for conv in expected_conversions if conv in all_conversions]
    
    for i, (name, result) in enumerate(comparison_results.items()):
        conversions = result['conversions']
        color = colors[i % len(colors)]
        
        y_values = [conversions.get(stage, 0) for stage in conversion_stages]
        
        fig.add_trace(go.Bar(
            x=conversion_stages,
            y=y_values,
            name=name,
            marker_color=color,
            text=[f"{v:.1f}%" for v in y_values],
            textposition='outside',
            textfont=dict(size=11),
            hovertemplate=f'<b>{name}</b><br>' +
                         '<b>%{x}</b><br>' +
                         'Conversion Rate: %{y:.1f}%<extra></extra>'
        ))
    
    fig = create_enhanced_plotly_theme(fig, "Conversion Rate Comparison - All Stages")
    fig.update_layout(
        height=500,
        xaxis_title="Conversion Stages",
        yaxis_title="Conversion Rate (%)",
        barmode='group'
    )
    fig.update_xaxes(tickangle=45)
    
    return fig
# Modal component for stage details
def create_stage_modal():
    return html.Div([
        html.Div([
            html.Div([
                html.Button([
                    html.I(className="fas fa-times")
                ], className="modal-close", id="modal-close-btn"),
                
                html.H2(id="modal-title", className="modal-title"),
                html.P(id="modal-subtitle", className="modal-subtitle")
            ], className="modal-header"),
            
            html.Div([
                html.Div(id="modal-stats", className="modal-stats"),
                html.Hr(style={'margin': '2rem 0', 'border': 'none', 'height': '1px', 'background': '#e5e7eb'}),
                html.Div(id="modal-candidates-list")
            ], className="modal-body")
        ], className="modal-content")
    ], className="modal-overlay", id="stage-modal", style={'display': 'none'})

# Main app layout with modern design - FIXED LAYOUT FOR FILTER ISSUES
app.layout = html.Div([
  html.Div([
      # Hero Section
      html.Div([
          html.H1("🚀 Recruitment Analytics Dashboard", className="hero-title"),
          html.P("Transform your hiring process with data-driven insights",
                  className="hero-subtitle")
      ], className="hero-section"),

      # File Upload Section
      html.Div([
          html.Div([
              html.H3([
                  html.I(className="fas fa-cloud-upload-alt me-2"),
                  "Upload Your Data"
              ], className="section-header"),
              html.P("Upload your recruitment data CSV file to begin analysis", className="section-description"),

              dcc.Upload(
                  id='upload-data',
                  children=html.Div([
                      html.I(className="fas fa-file-csv upload-icon"),
                      html.H4("Drop your CSV file here or click to browse", style={'margin': '0 0 1rem 0', 'color': '#374151'}),
                      html.P("Maximum file size: 50MB", style={'color': '#6b7280', 'margin': 0, 'fontSize': '0.875rem'})
                  ], style={'padding': '3rem', 'textAlign': 'center'}),
                  className="upload-zone",
                  multiple=False
              ),
              html.Div(id='upload-status', style={'marginTop': '1rem'})
          ], className="card-modern", style={'marginBottom': '2rem'})
      ]),

# Filter Section - IMPROVED LAYOUT
      html.Div([
          html.Div([
              html.H5([
                  html.I(className="fas fa-filter me-2"),
                  "Filter Data"
              ], style={'margin': 0, 'color': 'white'}),
          ], className="card-header-modern", style={'background': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)', 'color': 'white'}),
          html.Div([
              # First row - Source and Date Range Type filters
              html.Div([
                  html.Div([
                      html.Label("Application Source:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                      dcc.Dropdown(
                          id='source-filter',
                          placeholder="Select sources (leave empty for all)",
                          multi=True,
                          style={'fontFamily': 'Inter', 'zIndex': 1001}  # Increased z-index
                      )
                  ], className="col-md-4"),

                  html.Div([
                      html.Label("Date Range Type:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                      dcc.RadioItems(
                          id='date-range-type',
                          options=[
                              {'label': 'Week', 'value': 'week'},
                              {'label': 'Month', 'value': 'month'},
                              {'label': 'Quarter', 'value': 'quarter'},
                              {'label': 'Year', 'value': 'year'},
                              {'label': 'Custom', 'value': 'custom'}
                          ],
                          value='month',
                          inline=True,
                          style={'marginBottom': '10px'}
                      )
                  ], className="col-md-4"),

                  html.Div([
                      html.Label("Date Range:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                      html.Div([
                          dcc.Dropdown(
                              id='date-range-filter',
                              placeholder="Select date range",
                              multi=True,
                              style={'fontFamily': 'Inter', 'zIndex': 1001}  # Increased z-index
                          ),
                      ]),
                  ], className="col-md-4")
              ], className="row filter-section-row", style={'marginBottom': '30px', 'overflow': 'visible'}),  # Added overflow

              # Custom date picker in its own row
              html.Div([
                  html.Div([
                      html.Div([
                          dcc.DatePickerRange(
                              id='custom-date-range',
                              start_date_placeholder_text="Start Date",
                              end_date_placeholder_text="End Date",
                              display_format='YYYY-MM-DD',
                              style={'width': '100%', 'zIndex': 900}  # Added z-index
                          )
                      ], id='custom-date-container', style={'display': 'none', 'zIndex': 900})  # Added z-index
                  ], className="col-md-12"),
              ], className="row filter-section-row", style={'marginTop': '20px', 'marginBottom': '30px', 'overflow': 'visible'}),

              # Job title filter in its own row with added space
              html.Div([
                  html.Div([
                      html.Label("Job Title:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                      dcc.Dropdown(
                          id='job-title-filter',
                          placeholder="Select job titles",
                          multi=True,
                          style={'fontFamily': 'Inter', 'zIndex': 900}  # Increased z-index
                      )
                  ], className="col-md-12"),
              ], className="row", id="job-title-filter-row", style={'marginTop': '25px', 'paddingTop': '25px'}),

              html.Small("💡 Filter by source, date range, and job title to focus your analysis",
                        style={'color': '#6b7280', 'marginTop': '0.75rem', 'display': 'block'})
          ], style={'padding': '1.5rem', 'paddingBottom': '3rem', 'overflow': 'visible'})  # Added padding and overflow
      ], className="filter-card", id="filter-section", style={'display': 'none', 'overflow': 'visible', 'marginBottom': '40px'}),

      # Summary Metrics
      html.Div(id='summary-metrics', style={'marginBottom': '2rem'}),

      # Main Content
      html.Div(id='main-content', children=[
          html.Div([
              html.Div([
                  html.I(className="fas fa-info-circle", style={'fontSize': '4rem', 'color': '#6366f1', 'marginBottom': '1rem'}),
                  html.H3("Welcome to Advanced Recruitment Analytics", style={'marginBottom': '1rem', 'color': '#1f2937'}),
                  html.P("Get started by uploading your recruitment data CSV file. Our dashboard will provide comprehensive insights into your hiring funnel, candidate quality, and recruitment performance.",
                         style={'color': '#6b7280', 'fontSize': '1.125rem', 'lineHeight': '1.6', 'marginBottom': 0})
              ], style={'textAlign': 'center', 'padding': '4rem 2rem'})
          ], className="card-modern")
      ]),

      # Store components
      
      dcc.Store(id='stored-data', storage_type='memory'),
      dcc.Store(id='processed-data', storage_type='memory'),
      dcc.Store(id='date-options', storage_type='memory'),
      dcc.Store(id='funnel-comparison-data', storage_type='memory'),  # New store for comparison data
      dcc.Store(id='comparison-candidates-data', storage_type='memory'),  # NEW STORE
      # Modal component
      create_stage_modal()
  ], className="dashboard-container")
])

def parse_contents(contents, filename):
    """Parse uploaded file contents with better error handling"""
    try:
        print(f"Processing file: {filename}")
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Show file size
        file_size_mb = len(decoded) / 1024 / 1024
        print(f"File size: {file_size_mb:.2f} MB")
        
        if 'csv' in filename.lower():
            # Use more memory-efficient reading
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')),
                low_memory=False,          # Prevent mixed type warnings
                encoding='utf-8',          # Handle special characters
                na_filter=True,            # Handle NaN values properly
                keep_default_na=True       # Keep standard NaN representations
            )
            
            print(f"Successfully loaded: {len(df):,} rows, {len(df.columns)} columns")
            print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            
            # Show column names for debugging
            print(f"Columns: {list(df.columns)}")
            
            return df
        else:
            print("Error: File is not a CSV")
            return None
            
    except UnicodeDecodeError as e:
        print(f"Encoding error: {e}")
        # Try different encoding
        try:
            df = pd.read_csv(
                io.StringIO(decoded.decode('latin-1')),
                low_memory=False
            )
            print(f"Successfully loaded with latin-1 encoding: {len(df):,} rows")
            return df
        except Exception as e2:
            print(f"Failed with latin-1 too: {e2}")
            return None
    except MemoryError:
        print("Memory error - file too large")
        return None
    except Exception as e:
        print(f"General error parsing file: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.callback(
  [Output('stored-data', 'data'),
   Output('upload-status', 'children'),
   Output('source-filter', 'options'),
   Output('filter-section', 'style', allow_duplicate=True),
   Output('date-options', 'data'),
   Output('job-title-filter', 'options')],
  [Input('upload-data', 'contents'),
   Input('upload-data', 'filename')],
  prevent_initial_call=True
)
def update_output(contents, filename):
  if contents is None:
      return None, "", [], {'display': 'none'}, {}, []
  
  loading_status = html.Div([
        html.Div(className="loading-spinner-enhanced"),
        html.Span(f"Processing {filename}... Please wait for large files.", 
                 style={'marginLeft': '1rem', 'fontSize': '1rem', 'color': '#6366f1'})
    ], style={'display': 'flex', 'alignItems': 'center', 'padding': '1rem', 
              'background': '#f0f9ff', 'borderRadius': '12px', 'border': '1px solid #bae6fd'})  
  df = parse_contents(contents, filename)

  if df is None:
      return None, html.Div([
          html.I(className="fas fa-exclamation-triangle me-2"),
          "Error processing file. Please check the format and try again."
      ], className="alert-modern", style={'background': '#fef2f2', 'color': '#b91c1c', 'border': '1px solid #fecaca'}), [], {'display': 'none'}, {}, []

  stored_data = df.to_dict('records')

  # Process data to get dropdown options
  try:
      processor = RecruitmentDataProcessor(df)
      processor.process_all()
      analytics = RecruitmentAnalytics(processor.cleaned_data, processor.candidate_master, processor.metrics)
      date_options = analytics.get_date_range_options()

      # Source filter options
      if 'Application Source' in df.columns:
          unique_sources = sorted(df['Application Source'].dropna().unique())
          source_options = [{'label': f'🌟 All Sources', 'value': 'All Sources'}] + \
                          [{'label': f'📊 {source}', 'value': source} for source in unique_sources]
      else:
          source_options = [{'label': '🌟 All Sources', 'value': 'All Sources'}]

      # Job title filter options
      if 'Posting Title (Job Opening)' in df.columns:
          unique_job_titles = sorted(df['Posting Title (Job Opening)'].dropna().unique())
          job_title_options = [{'label': f'📋 {title}', 'value': title} for title in unique_job_titles]
      else:
          job_title_options = []

      status_message = html.Div([
          html.I(className="fas fa-check-circle me-2"),
          f"Successfully uploaded {filename}! Found {len(df):,} records with {len(df.columns)} columns."
      ], className="alert-modern", style={'background': '#f0fdf4', 'color': '#166534', 'border': '1px solid #bbf7d0'})

      return stored_data, status_message, source_options, {'display': 'block', 'overflow': 'visible', 'marginBottom': '40px'}, date_options, job_title_options
  except Exception as e:
      error_msg = f"Error processing data: {str(e)}"
      print(error_msg)

      return None, html.Div([
          html.I(className="fas fa-exclamation-triangle me-2"),
          f"Error processing file: {error_msg}. Please check the format and try again."
      ], className="alert-modern", style={'background': '#fef2f2', 'color': '#b91c1c', 'border': '1px solid #fecaca'}), [], {'display': 'none'}, {}, []

@app.callback(
  Output('date-range-filter', 'options'),
  [Input('date-range-type', 'value'),
   Input('date-options', 'data')],
  prevent_initial_call=True
)
def update_date_range_options(date_range_type, date_options):
  if not date_options:
      return []

  return date_options.get(date_range_type, [])

@app.callback(
  Output('custom-date-container', 'style'),
  [Input('date-range-type', 'value')],
  prevent_initial_call=True
)
def toggle_custom_date_picker(date_range_type):
  if date_range_type == 'custom':
      return {'display': 'block', 'zIndex': 900}
  return {'display': 'none'}

@app.callback(
  [Output('processed-data', 'data'),
   Output('summary-metrics', 'children'),
   Output('main-content', 'children'),
   Output('filter-section', 'style', allow_duplicate=True)],
  [Input('stored-data', 'data'),
   Input('source-filter', 'value'),
   Input('date-range-type', 'value'),
   Input('date-range-filter', 'value'),
   Input('custom-date-range', 'start_date'),
   Input('custom-date-range', 'end_date'),
   Input('job-title-filter', 'value')],
  prevent_initial_call=True
)
def process_data_and_create_dashboard(stored_data, selected_sources, date_range_type, selected_date_range, custom_start_date, custom_end_date, selected_job_titles):
  if stored_data is None:
      return None, "", html.Div([
          html.Div([
              html.I(className="fas fa-info-circle", style={'fontSize': '4rem', 'color': '#6366f1', 'marginBottom': '1rem'}),
              html.H3("Welcome to Advanced Recruitment Analytics", style={'marginBottom': '1rem', 'color': '#1f2937'}),
              html.P("Get started by uploading your recruitment data CSV file. Our dashboard will provide comprehensive insights into your hiring funnel, candidate quality, and recruitment performance.",
                     style={'color': '#6b7280', 'fontSize': '1.125rem', 'lineHeight': '1.6', 'marginBottom': 0})
          ], style={'textAlign': 'center', 'padding': '4rem 2rem'})
      ], className="card-modern"), {'display': 'none'}

  try:
      # Process data
      df = pd.DataFrame(stored_data)
      processor = RecruitmentDataProcessor(df)
      processor.process_all()

      analytics = RecruitmentAnalytics(processor.cleaned_data, processor.candidate_master, processor.metrics)

      # Apply filters sequentially - FIXED FILTER APPLICATION LOGIC
      # Start with full dataset
      filtered_master = analytics.candidate_master

      # Apply source filter first if selected
      if selected_sources and 'All Sources' not in selected_sources:
          filtered_master = analytics.filter_by_sources(selected_sources)

      # Apply date range filter next
      if date_range_type == 'custom' and custom_start_date and custom_end_date:
          custom_date_range = (custom_start_date, custom_end_date)
          filtered_master = analytics.filter_by_date_range(date_range_type, None, custom_date_range, filtered_master)
      elif date_range_type and selected_date_range and 'All' not in selected_date_range:
          filtered_master = analytics.filter_by_date_range(date_range_type, selected_date_range, None, filtered_master)

      # Apply job title filter if selected
      if selected_job_titles and len(selected_job_titles) > 0:
          filtered_master = analytics.filter_by_job_titles(selected_job_titles, filtered_master)

      # Generate all analytics based on final filtered data
      metrics = analytics.generate_summary_metrics(filtered_master)
      funnel_metrics = analytics.calculate_funnel_metrics(filtered_master)
      unqualified_analysis = analytics.analyze_unqualified_candidates(selected_sources, filtered_master)
      age_analysis = analytics.analyze_age_distribution(selected_sources, filtered_master)
      source_performance = analytics.source_performance_analysis(selected_sources, filtered_master)
      time_analysis = analytics.time_based_analysis(selected_sources, filtered_master, qualified_only=True)
      candidates_by_stage = analytics.get_candidates_by_stage(filtered_master)

      # Filter indicator
      filter_parts = []
      if selected_sources and 'All Sources' not in selected_sources:
          filter_parts.append(f"Sources: {', '.join(selected_sources)}")

      if date_range_type == 'custom' and custom_start_date and custom_end_date:
          filter_parts.append(f"Date Range: {custom_start_date} to {custom_end_date}")
      elif date_range_type and selected_date_range and 'All' not in selected_date_range:
          if date_range_type == 'week':
              filter_parts.append(f"Weeks: {', '.join(selected_date_range)}")
          elif date_range_type == 'month':
              filter_parts.append(f"Months: {', '.join(selected_date_range)}")
          elif date_range_type == 'quarter':
              filter_parts.append(f"Quarters: {', '.join(selected_date_range)}")
          elif date_range_type == 'year':
              filter_parts.append(f"Years: {', '.join(map(str, selected_date_range))}")

      if selected_job_titles and len(selected_job_titles) > 0:
          filter_parts.append(f"Job Titles: {', '.join(selected_job_titles)}")

      filter_indicator = f" (Filtered by: {'; '.join(filter_parts)})" if filter_parts else ""

      # Create modern metric cards for key performance indicators
      summary_cards = html.Div([
          html.H3([
              html.I(className="fas fa-chart-bar me-2"),
              "Key Performance Metrics"
          ], className="section-header"),
          html.Div([
              create_modern_metric_card("Applications", f"{metrics['total_applications']:,}", "fa-file-alt", "primary",
                                      f"From {metrics['unique_candidates']:,} candidates"),
              create_modern_metric_card("Unique Applicants", f"{metrics['unique_applicants']:,}", "fa-user", "info",
                                      f"{metrics['applications_per_candidate']:.1f} apps/candidate"),
              create_modern_metric_card("Qualified", f"{metrics['qualified_candidates']:,}", "fa-user-check", "success",
                                      f"{metrics['qualification_rate']:.1f}% qualification rate"),
              create_modern_metric_card("Hired", f"{metrics['total_hired']:,}", "fa-handshake", "primary",
                                      f"{metrics['hire_rate_from_qualified']:.1f}% from qualified"),
              create_modern_metric_card("Average Age", f"{metrics['avg_calculated_age']:.1f}", "fa-birthday-cake", "warning",
                                      "Calculated from DoB"),
              create_modern_metric_card("Missing Feedback", f"{metrics['interviews_without_feedback']:,}", "fa-comment-slash", "danger",
                                      "Scheduled interviews")
          ], className="summary-grid")
      ])

      # Create enhanced visualizations
    
      # 1. Qualified Candidates Funnel - UPDATED to show percent previous
      # Create clickable funnel chart


            # Create clickable funnel chart with invisible overlay
      # Create RELIABLE clickable funnel chart
     # Create WORKING clickable funnel using Waterfall chart
      # Your ORIGINAL beautiful funnel + invisible clickable overlay
      # Keep your ORIGINAL funnel exactly as it was
      funnel_data = funnel_metrics['funnel_data']
      fig_funnel = go.Figure(go.Funnel(
            y=list(funnel_data.keys()),
            x=list(funnel_data.values()),
            textinfo="value+percent previous",
            marker=dict(
                color=['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b'],
                line=dict(width=2, color='white')
            ),
            textfont=dict(size=15, color='white', family='Inter')
        ))
      fig_funnel = create_enhanced_plotly_theme(fig_funnel, f"Recruitment Funnel{filter_indicator}")
      fig_funnel.update_layout(height=650)

        # Create working buttons
      stage_buttons = []
      colors = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b']

      for i, (stage, count) in enumerate(funnel_data.items()):
            stage_buttons.append(
                html.Button([
                    html.I(className="fas fa-users", style={'marginRight': '8px'}),
                    html.Span(f"{stage} ({count:,})", style={'fontWeight': '600'})
                ], 
                id=f'btn-{stage.replace(" ", "").replace("→", "")}',
                **{'data-stage': stage},
                style={
                    'background': colors[i % len(colors)],
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '10px',
                    'padding': '12px 16px',
                    'margin': '4px 0',
                    'width': '100%',
                    'cursor': 'pointer',
                    'fontSize': '14px',
                    'transition': 'all 0.2s'
                }
            ))
      # 2. Source Performance Analysis
      if not source_performance.empty:
          fig_source = make_subplots(
              rows=2, cols=2,
              subplot_titles=(
                  'Unique Candidates',
                  'Qualification Rate',
                  'Hire Rate',
                  'Source Comparison'
              ),
              vertical_spacing=0.15,  # Increased for better separation
              horizontal_spacing=0.12  # Increased for better separation
          )

          # MODIFIED: Unique candidates instead of total applications
          fig_source.add_trace(
              go.Bar(
                  x=source_performance['source'],
                  y=source_performance['unique_candidates'],
                  name='Unique Candidates',
                  marker_color='#6366f1',
                  text=source_performance['unique_candidates'],
                  textposition='outside',
                  textfont=dict(size=12),
                  hovertemplate='<b>%{x}</b><br>Unique Candidates: %{y}<extra></extra>'
              ),
              row=1, col=1
          )

          # Qualification Rate
          fig_source.add_trace(
              go.Bar(
                  x=source_performance['source'],
                  y=source_performance['qualification_rate'],
                  name='Qualification %',
                  marker_color='#10b981',
                  text=[f"{x:.1f}%" for x in source_performance['qualification_rate']],
                  textposition='outside',
                  textfont=dict(size=12),
                  hovertemplate='<b>%{x}</b><br>Qualification Rate: %{y:.1f}%<extra></extra>'
              ),
              row=1, col=2
          )

          # Hire Rate (FIXED: Using hire_rate based on unique candidates)
          fig_source.add_trace(
              go.Bar(
                  x=source_performance['source'],
                  y=source_performance['hire_rate'],
                  name='Hire Rate %',
                  marker_color='#8b5cf6',
                  text=[f"{x:.1f}%" for x in source_performance['hire_rate']],
                  textposition='outside',
                  textfont=dict(size=12),
                  hovertemplate='<b>%{x}</b><br>Hire Rate: %{y:.1f}%<extra></extra>'
              ),
              row=2, col=1
          )

          # Source Comparison Scatter Plot - UPDATED to use hire_rate
          fig_source.add_trace(
              go.Scatter(
                  x=source_performance['qualification_rate'],
                  y=source_performance['hire_rate'],
                  mode='markers+text',
                  marker=dict(
                      size=source_performance['unique_candidates'],  # MODIFIED: Changed to unique_candidates
                      sizemode='diameter',
                      sizeref=max(source_performance['unique_candidates'].max()/35, 1),  # Prevent sizeref=0
                      color=source_performance['avg_iq_score'],  # UPDATED: Use avg_iq_score instead of avg_calculated_age
                      colorscale='Viridis',
                      colorbar=dict(title="Avg IQ Score", titlefont=dict(size=12)),  # UPDATED: Changed title
                      line=dict(width=2, color='white'),
                      opacity=0.8
                  ),
                  text=source_performance['source'],
                  textposition='top center',
                  textfont=dict(size=11),
                  name='Performance',
                  hovertemplate='<b>%{text}</b><br>' +
                               'Qualification: %{x:.1f}%<br>' +
                               'Hire Rate: %{y:.1f}%<br>' +
                               'Unique Candidates: %{marker.size}<br>' +  # MODIFIED: changed label
                               'Avg IQ Score: %{marker.color:.1f}<extra></extra>'  # UPDATED: Changed label
              ),
              row=2, col=2
          )

          # Update axis labels for clarity
          fig_source.update_xaxes(title_text="Source", row=1, col=1)
          fig_source.update_yaxes(title_text="Unique Candidates", row=1, col=1)  # MODIFIED: Updated label

          fig_source.update_xaxes(title_text="Source", row=1, col=2)
          fig_source.update_yaxes(title_text="Rate (%)", row=1, col=2)

          fig_source.update_xaxes(title_text="Source", row=2, col=1)
          fig_source.update_yaxes(title_text="Rate (%)", row=2, col=1)

          fig_source.update_xaxes(title_text="Qualification Rate (%)", row=2, col=2)
          fig_source.update_yaxes(title_text="Hire Rate (%)", row=2, col=2)

          # Set angle for x-axis labels to avoid overlapping
          fig_source.update_xaxes(tickangle=45, row=1, col=1)
          fig_source.update_xaxes(tickangle=45, row=1, col=2)
          fig_source.update_xaxes(tickangle=45, row=2, col=1)

          fig_source = create_enhanced_plotly_theme(fig_source, f"Source Performance{filter_indicator}")
          fig_source.update_layout(height=800, showlegend=False)
      else:
          fig_source = go.Figure()
          fig_source.add_annotation(
              text="No source data available",
              xref="paper", yref="paper", x=0.5, y=0.5,
              font=dict(size=18, color='#6b7280', family='Inter')
          )
          fig_source = create_enhanced_plotly_theme(fig_source, "Source Performance")

      # 3. Time Series Analysis
      monthly_apps = time_analysis['monthly_applications']
      monthly_hire = time_analysis['monthly_hiring_rate']

      fig_time = make_subplots(specs=[[{"secondary_y": True}]])

      if monthly_apps:
          fig_time.add_trace(
              go.Scatter(
                  x=list(monthly_apps.keys()),
                  y=list(monthly_apps.values()),
                  mode='lines+markers',
                  name='Applications',
                  line=dict(color='#6366f1', width=4),
                  marker=dict(size=10, color='#6366f1', line=dict(width=2, color='white')),
                  fill='tozeroy',
                  fillcolor='rgba(99, 102, 241, 0.1)',
                  hovertemplate='<b>%{x}</b><br>Applications: %{y}<extra></extra>'
              ),
              secondary_y=False
          )

      if monthly_hire:
          fig_time.add_trace(
              go.Scatter(
                  x=list(monthly_hire.keys()),
                  y=list(monthly_hire.values()),
                  mode='lines+markers',
                  name='Hire Rate',
                  line=dict(color='#10b981', width=4),
                  marker=dict(size=10, color='#10b981', line=dict(width=2, color='white')),
                  hovertemplate='<b>%{x}</b><br>Hire Rate: %{y:.1f}%<extra></extra>'
              ),
              secondary_y=True
          )

      fig_time.update_xaxes(title_text="Month", tickangle=45)  # Angle for better readability
      fig_time.update_yaxes(title_text="Applications", secondary_y=False)
      fig_time.update_yaxes(title_text="Hire Rate (%)", secondary_y=True)

      fig_time = create_enhanced_plotly_theme(fig_time, f"Application Timeline{filter_indicator}")
      fig_time.update_layout(height=500)

      # 4. IQ Score Analysis by Source Chart - NEW CHART
      if not source_performance.empty:
          fig_iq_score = go.Figure(
              data=[
                  go.Bar(
                      x=source_performance['source'],
                      y=source_performance['avg_iq_score'],
                      marker_color='#f59e0b',
                      text=[f"{x:.1f}" for x in source_performance['avg_iq_score']],
                      textposition='outside',
                      hovertemplate='<b>%{x}</b><br>Avg IQ Score: %{y:.1f}<extra></extra>'
                  )
              ]
          )

          fig_iq_score = create_enhanced_plotly_theme(fig_iq_score, f"Average IQ Score by Source{filter_indicator}")
          fig_iq_score.update_layout(
              height=400,
              xaxis_title="Source",
              yaxis_title="Average IQ Score"
          )
          fig_iq_score.update_xaxes(tickangle=45)
      else:
          fig_iq_score = go.Figure()
          fig_iq_score.add_annotation(
              text="No source data available for IQ score analysis",
              xref="paper", yref="paper", x=0.5, y=0.5,
              font=dict(size=18, color='#6b7280', family='Inter')
          )
          fig_iq_score = create_enhanced_plotly_theme(fig_iq_score, "IQ Score Analysis")

      # 5. Unqualified Analysis
      unqualified_reasons = unqualified_analysis['by_disqualification_reason']
      unqualified_reasons_filtered = {k: v for k, v in unqualified_reasons.items() if k != 'Not Unqualified'}

      if unqualified_reasons_filtered:
          fig_unqualified = go.Figure(data=[
              go.Pie(
                  labels=list(unqualified_reasons_filtered.keys()),
                  values=list(unqualified_reasons_filtered.values()),
                  hole=0.5,
                  marker=dict(
                      colors=['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#10b981', '#6366f1', '#64748b'],
                      line=dict(color='white', width=3)
                  ),
                  textinfo='label+percent',
                  textfont=dict(size=14, family='Inter'),
                  hovertemplate='<b>%{label}</b><br>' +
                               'Count: %{value}<br>' +
                               'Percentage: %{percent}<extra></extra>'
              )
          ])

          fig_unqualified.add_annotation(
              text=f"<b>{sum(unqualified_reasons_filtered.values()):,}</b><br><span style='font-size:14px'>Total Unqualified</span>",
              x=0.5, y=0.5,
              font=dict(size=18, color='#1f2937', family='Inter'),
              showarrow=False,
              align='center'
          )

          fig_unqualified = create_enhanced_plotly_theme(fig_unqualified, f"Disqualification Reasons{filter_indicator}")
          fig_unqualified.update_layout(height=500)
      else:
          fig_unqualified = go.Figure()
          fig_unqualified.add_annotation(
              text="No unqualified candidates found",
              xref="paper", yref="paper", x=0.5, y=0.5,
              font=dict(size=18, color='#10b981', family='Inter')
          )
          fig_unqualified = create_enhanced_plotly_theme(fig_unqualified, "Disqualification Analysis")

      # 6. Age Distribution Analysis
      fig_age = go.Figure()

      if not age_analysis.empty:
          # Add qualified candidates bar
          fig_age.add_trace(go.Bar(
              x=age_analysis['age_group'],
              y=age_analysis['qualified'],
              name='Qualified',
              marker_color='#10b981',
              text=age_analysis['qualified'],
              textposition='inside',
              textfont=dict(color='white', size=12),
              hovertemplate='<b>%{x}</b><br>Qualified: %{y}<extra></extra>'
          ))

          # Add unqualified candidates bar
          fig_age.add_trace(go.Bar(
              x=age_analysis['age_group'],
              y=age_analysis['unqualified'],
              name='Unqualified',
              marker_color='#ef4444',
              text=age_analysis['unqualified'],
              textposition='inside',
              textfont=dict(color='white', size=12),
              hovertemplate='<b>%{x}</b><br>Unqualified: %{y}<extra></extra>'
          ))

           # Add hire rate line
          fig_age.add_trace(go.Scatter(
              x=age_analysis['age_group'],
              y=age_analysis['hire_rate'],
              mode='lines+markers',
              name='Hire Rate',
              yaxis='y2',
              line=dict(color='#6366f1', width=3),
              marker=dict(size=8, color='#6366f1', line=dict(width=2, color='white')),
              hovertemplate='<b>%{x}</b><br>Hire Rate: %{y:.1f}%<extra></extra>'
          ))

          # Configure the layout with two y-axes
          fig_age.update_layout(
              yaxis2=dict(
                  title='Hire Rate (%)',
                  overlaying='y',
                  side='right',
                  range=[0, max(max(age_analysis['hire_rate']), 0.1) * 1.2]  # Ensure non-zero y2 range
              ),
              barmode='stack',
              legend=dict(
                  orientation="h",
                  yanchor="bottom",
                  y=-0.25,
                  xanchor="center",
                  x=0.5
              )
          )

      fig_age = create_enhanced_plotly_theme(fig_age, f"Age Distribution{filter_indicator}")
      fig_age.update_layout(height=500)
      fig_age.update_xaxes(title_text="Age Groups")
      fig_age.update_yaxes(title_text="Candidates")

      # Create enhanced data tables
      if len(filtered_master) > 0:
          candidate_table_data = filtered_master.head(50).copy()

          display_columns = [
              'candidate_name', 'calculated_age', 'nationality', 'country_of_residence',
              'speak_arabic', 'primary_status', 'disqualification_reason',
              'num_applications', 'application_sources', 'all_posting_titles', 'iq_score', 'received_test', 'hired'
          ]

          # Only include columns that exist in the dataframe
          available_columns = [col for col in display_columns if col in candidate_table_data.columns]

          for col in available_columns:
              if col in ['iq_score', 'calculated_age']:
                  candidate_table_data[col] = pd.to_numeric(candidate_table_data[col], errors='coerce').fillna(0)
              elif col in ['received_test', 'hired']:
                  candidate_table_data[col] = candidate_table_data[col].astype(str)
              else:
                  candidate_table_data[col] = candidate_table_data[col].astype(str)

          enhanced_candidate_table = create_modern_table(candidate_table_data[available_columns], 'candidate-table', 'primary')
          enhanced_candidate_table.style_data_conditional.extend([
              {
                  'if': {'filter_query': '{primary_status} = Unqualified', 'column_id': 'primary_status'},
                  'backgroundColor': '#fef2f2',
                  'color': '#b91c1c',
                  'fontWeight': '600'
              },
              {
                  'if': {'filter_query': '{hired} = True', 'column_id': 'hired'},
                  'backgroundColor': '#f0fdf4',
                  'color': '#166534',
                  'fontWeight': '600'
              },
              {
                  'if': {'filter_query': '{calculated_age} >= 27', 'column_id': 'calculated_age'},
                  'backgroundColor': '#fffbeb',
                  'color': '#d97706',
                  'fontWeight': '600'
              }
          ])
      else:
          enhanced_candidate_table = html.Div([
              html.I(className="fas fa-search", style={'fontSize': '3rem', 'color': '#6b7280', 'marginBottom': '1rem'}),
              html.H4("No candidate data available", style={'color': '#6b7280', 'marginBottom': '0.5rem'}),
              html.P("Try adjusting your filters or upload a different data file", style={'color': '#9ca3af'})
          ], style={'textAlign': 'center', 'padding': '3rem', 'background': '#f9fafb', 'borderRadius': '12px', 'border': '1px solid #e5e7eb'})

      # Source performance table
      enhanced_source_table = create_modern_table(source_performance, 'source-table', 'secondary')

      # Unqualified breakdown table
      if unqualified_reasons_filtered:
          unqualified_breakdown = pd.DataFrame([
              {'Reason': reason, 'Count': count, 'Percentage': f"{(count/unqualified_analysis['total_unqualified']*100):.1f}%"}
              for reason, count in unqualified_analysis['by_disqualification_reason'].items()
              if reason != 'Not Unqualified'
          ]).sort_values('Count', ascending=False)

          enhanced_unqualified_table = create_modern_table(unqualified_breakdown, 'unqualified-table', 'danger')
          enhanced_unqualified_table.style_data_conditional.append({
              'if': {'row_index': 0},
              'backgroundColor': '#fef2f2',
              'fontWeight': '600'
          })
      else:
          enhanced_unqualified_table = html.Div([
              html.I(className="fas fa-check-circle", style={'fontSize': '3rem', 'color': '#10b981', 'marginBottom': '1rem'}),
              html.H4("No unqualified candidates found!", style={'color': '#166534', 'marginBottom': '0.5rem'}),
              html.P("All candidates in the filtered data meet the qualification criteria", style={'color': '#6b7280'})
          ], style={'textAlign': 'center', 'padding': '3rem', 'background': '#f0fdf4', 'borderRadius': '16px', 'border': '1px solid #bbf7d0'})

      # Create comprehensive tabs
      tabs_content = html.Div([
          html.Div([
              html.H3([
                  html.I(className="fas fa-chart-line me-2"),
                  "Detailed Analytics"
              ], className="section-header"),

              dcc.Tabs(
                  id="main-tabs",
                  value='overview',
                  className="modern-tabs",
                  style={'marginBottom': '2rem'},
                  children=[
                      dcc.Tab(
                          label='🏠 Overview',
                          value='overview',
                          children=[
                              html.Div([
                                  html.Div([
                                      html.H4([
                                          html.I(className="fas fa-rocket me-2"),
                                          "Candidate Journey"
                                      ], style={'marginBottom': '1rem', 'color': '#1f2937'}),
                                      html.P("Focus on qualified candidates who passed initial screening criteria",
                                             style={'color': '#6b7280', 'marginBottom': '2rem'})
                                  ]),

                                  html.Div([
                                      html.Div([
                                          dcc.Graph(figure=fig_funnel, config={'displayModeBar': False}, id='overview-funnel-graph')
                                      ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 1rem'}),
                                      # Buttons
                                        html.Div([
                                            html.H5("📊 View Candidates by Stage", style={'marginBottom': '1rem', 'color': '#1f2937'}),
                                            html.Div(stage_buttons)
                                        ], style={'width': '30%', 'display': 'inline-block', 'padding': '0 1rem', 'verticalAlign': 'top'}),
                               
                                      html.Div([
                                          dcc.Graph(figure=fig_time, config={'displayModeBar': False})
                                      ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 1rem'})
                                  ], style={'marginBottom': '2rem'}),

                                  html.Div([
                                      dcc.Graph(figure=fig_source, config={'displayModeBar': False})
                                  ]),

                                  # IQ Score Analysis Chart - NEW SECTION
                                  html.Div([
                                      html.H4([
                                          html.I(className="fas fa-brain me-2"),
                                          "IQ Score Analysis by Source"
                                      ], style={'marginTop': '2rem', 'marginBottom': '1rem', 'color': '#1f2937'}),
                                      dcc.Graph(figure=fig_iq_score, config={'displayModeBar': False})
                                  ], style={'marginTop': '2rem'}),

                                  # Quick insights
                                  html.Hr(style={'margin': '3rem 0'}),
                                  html.H4([
                                      html.I(className="fas fa-lightbulb me-2"),
                                      "Key Insights"
                                  ], style={'marginBottom': '1.5rem', 'color': '#1f2937'}),

                                  html.Div([
                                      html.Div([
                                          html.Div([
                                              html.H5([
                                                  html.I(className="fas fa-trophy text-warning me-2"),
                                                  "Best Performing Stage"
                                              ]),
                                              html.P(f"Highest conversion: {max(funnel_metrics['conversions'].items(), key=lambda x: x[1])[0]} ({max(funnel_metrics['conversions'].values()):.1f}%)" if funnel_metrics['conversions'] else "No conversion data available",
                                                     style={'marginBottom': 0})
                                          ], className="insight-card")
                                      ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 1rem'}),

                                      html.Div([
                                          html.Div([
                                              html.H5([
                                                  html.I(className="fas fa-chart-line text-info me-2"),
                                                  "Improvement Opportunity"
                                              ]),
                                              html.P(f"Lowest conversion: {min(funnel_metrics['conversions'].items(), key=lambda x: x[1])[0]} ({min(funnel_metrics['conversions'].values()):.1f}%)" if funnel_metrics['conversions'] else "No conversion data available",
                                                     style={'marginBottom': 0})
                                          ], className="insight-card")
                                      ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 1rem'})
                                  ]) if funnel_metrics['conversions'] else html.P("No conversion data available", style={'textAlign': 'center', 'color': '#6b7280'})
                              ], className="tab-content-modern")
                          ]
                      ),

                      dcc.Tab(
                          label='❌ Disqualification Analysis',
                          value='unqualified',
                          children=[
                              html.Div([
                                  html.Div([
                                      html.H4([
                                          html.I(className="fas fa-user-times me-2"),
                                          "Unqualified Candidates"
                                      ], style={'marginBottom': '1rem', 'color': '#1f2937'}),
                                      html.P("Understand disqualification patterns to optimize sourcing",
                                             style={'color': '#6b7280', 'marginBottom': '2rem'})
                                  ]),

                                  html.Div([
                                      html.Div([
                                          dcc.Graph(figure=fig_unqualified, config={'displayModeBar': False})
                                      ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 1rem'}),
                                      html.Div([
                                          dcc.Graph(figure=fig_age, config={'displayModeBar': False})
                                      ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 1rem'})
                                  ], style={'marginBottom': '2rem'}),

                                  html.Div([
                                      html.H4([
                                          html.I(className="fas fa-table me-2"),
                                          "Detailed Breakdown"
                                      ], style={'marginBottom': '1.5rem', 'color': '#1f2937'}),
                                      enhanced_unqualified_table
                                  ])
                              ], className="tab-content-modern")
                          ]
                      ),

                      dcc.Tab(
                          label='📊 Source Performance',
                          value='source',
                          children=[
                              html.Div([
                                  html.Div([
                                      html.H4([
                                          html.I(className="fas fa-chart-bar me-2"),
                                          "Source Analysis"
                                      ], style={'marginBottom': '1rem', 'color': '#1f2937'}),
                                      html.P("Compare recruitment sources to identify top performers",
                                             style={'color': '#6b7280', 'marginBottom': '2rem'})
                                  ]),

                                  html.Div([
                                      enhanced_source_table
                                  ], style={'marginBottom': '2rem'}),

                                  # Top performers section - MODIFIED to include IQ Score metric
                                  html.H4([
                                      html.I(className="fas fa-medal me-2"),
                                      "Top Performers"
                                  ], style={'marginBottom': '1.5rem', 'color': '#1f2937'}),

                                  html.Div([
                                      html.Div([
                                          html.Div([
                                              html.H5("🥇 Best Qualification Rate"),
                                              html.H3(f"{source_performance.iloc[0]['qualification_rate']:.1f}%" if not source_performance.empty else "N/A",
                                                      style={'color': '#10b981', 'marginBottom': '0.5rem'}),
                                              html.P(source_performance.iloc[0]['source'] if not source_performance.empty else "N/A",
                                                    style={'color': '#6b7280', 'marginBottom': 0})
                                          ], style={'textAlign': 'center', 'padding': '1.5rem', 'background': '#f0fdf4', 'borderRadius': '16px', 'border': '1px solid #bbf7d0'})
                                      ], style={'width': '25%', 'display': 'inline-block', 'padding': '0 1rem'}),

                                      html.Div([
                                          html.Div([
                                              html.H5("🎯 Best Hire Rate"),
                                              html.H3(
                                                  f"{source_performance.sort_values('hire_rate', ascending=False).iloc[0]['hire_rate']:.1f}%"
                                                  if not source_performance.empty and source_performance['hire_rate'].max() > 0 else "N/A",
                                                  style={'color': '#3b82f6', 'marginBottom': '0.5rem'}
                                              ),
                                              html.P(
                                                  source_performance.sort_values('hire_rate', ascending=False).iloc[0]['source']
                                                  if not source_performance.empty and source_performance['hire_rate'].max() > 0 else "N/A",
                                                  style={'color': '#6b7280', 'marginBottom': 0}
                                              )
                                          ], style={'textAlign': 'center', 'padding': '1.5rem', 'background': '#eff6ff', 'borderRadius': '16px', 'border': '1px solid #bfdbfe'})
                                      ], style={'width': '25%', 'display': 'inline-block', 'padding': '0 1rem'}),

                                      html.Div([
                                          html.Div([
                                              html.H5("📈 Most Candidates"),
                                              html.H3(
                                                  f"{source_performance.sort_values('unique_candidates', ascending=False).iloc[0]['unique_candidates']:,}"
                                                  if not source_performance.empty else "N/A",
                                                  style={'color': '#8b5cf6', 'marginBottom': '0.5rem'}
                                              ),
                                              html.P(
                                                  source_performance.sort_values('unique_candidates', ascending=False).iloc[0]['source']
                                                  if not source_performance.empty else "N/A",
                                                  style={'color': '#6b7280', 'marginBottom': 0}
                                              )
                                          ], style={'textAlign': 'center', 'padding': '1.5rem', 'background': '#faf5ff', 'borderRadius': '16px', 'border': '1px solid #d8b4fe'})
                                      ], style={'width': '25%', 'display': 'inline-block', 'padding': '0 1rem'}),

                                      # New card for Highest IQ Score - ADDED
                                      html.Div([
                                          html.Div([
                                              html.H5("🧠 Highest Avg IQ Score"),
                                              html.H3(
                                                  f"{source_performance.sort_values('avg_iq_score', ascending=False).iloc[0]['avg_iq_score']:.1f}"
                                                  if not source_performance.empty and source_performance['avg_iq_score'].max() > 0 else "N/A",
                                                  style={'color': '#f59e0b', 'marginBottom': '0.5rem'}
                                              ),
                                              html.P(
                                                  source_performance.sort_values('avg_iq_score', ascending=False).iloc[0]['source']
                                                  if not source_performance.empty and source_performance['avg_iq_score'].max() > 0 else "N/A",
                                                  style={'color': '#6b7280', 'marginBottom': 0}
                                              )
                                          ], style={'textAlign': 'center', 'padding': '1.5rem', 'background': '#fffbeb', 'borderRadius': '16px', 'border': '1px solid #fcd34d'})
                                      ], style={'width': '25%', 'display': 'inline-block', 'padding': '0 1rem'})
                                  ]) if not source_performance.empty else html.P("No source data available", style={'textAlign': 'center', 'color': '#6b7280'})
                              ], className="tab-content-modern")
                          ]
                      ),

                      dcc.Tab(
                          label='👥 Candidate Details',
                          value='candidates',
                          children=[
                              html.Div([
                                  html.Div([
                                      html.H4([
                                          html.I(className="fas fa-users me-2"),
                                          "Candidate Database"
                                      ], style={'marginBottom': '1rem', 'color': '#1f2937'}),
                                      html.P("Detailed view of individual candidates",
                                             style={'color': '#6b7280', 'marginBottom': '1rem'})
                                  ]),

                                  html.Div([
                                      html.I(className="fas fa-info-circle me-2"),
                                      html.Strong("Legend: "),
                                      html.Span("Red = Unqualified, Green = Hired, Orange = Age ≥ 27", style={'fontSize': '0.875rem'})
                                  ], style={'padding': '1rem', 'background': '#f8fafc', 'borderRadius': '12px', 'border': '1px solid #e2e8f0', 'marginBottom': '1.5rem'}),

                                  enhanced_candidate_table
                              ], className="tab-content-modern")
                          ]
                      ),

                      dcc.Tab(
                          label='🏗️ Funnel Stages',
                          value='candidates_by_stage',
                          children=[
                              html.Div([
                                  html.Div([
                                      html.H4([
                                          html.I(className="fas fa-layer-group me-2"),
                                          "Candidates by Stage"
                                      ], style={'marginBottom': '1rem', 'color': '#1f2937'}),
                                      html.P("Explore candidates who reached each recruitment stage",
                                             style={'color': '#6b7280', 'marginBottom': '2rem'})
                                  ]),

                                  html.Div([
                                      html.Div([
                                          html.H5("Select Stage:", style={'marginBottom': '1rem', 'color': '#374151'}),
                                          dcc.Dropdown(
                                              id='stage-selector',
                                              options=[{'label': f"🎯 {stage}", 'value': stage} for stage in candidates_by_stage.keys()],
                                              value=list(candidates_by_stage.keys())[0] if candidates_by_stage else None,
                                              style={'fontFamily': 'Inter', 'marginBottom': '2rem', 'zIndex': 100}
                                          )
                                      ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'}),

                                      html.Div(id='stage-metrics', style={'width': '60%', 'display': 'inline-block', 'paddingLeft': '2rem'})
                                  ]),

                                  html.Hr(style={'margin': '2rem 0'}),
                                  html.Div(id='candidates-list')
                              ], className="tab-content-modern")
                          ]
                      ),

                      # NEW TAB: Funnel Comparison
                      dcc.Tab(
                        label='🔄 Funnel Comparison',
                        value='funnel_comparison',
                        children=[
                            html.Div([
                                # Hero Header with Gradient Background
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.H1([
                                                html.I(className="fas fa-balance-scale", style={
                                                    'fontSize': '3rem',
                                                    'marginRight': '1rem',
                                                    'background': 'linear-gradient(45deg, #fff, #e0e7ff)',
                                                    'webkitBackgroundClip': 'text',
                                                    'webkitTextFillColor': 'transparent',
                                                    'filter': 'drop-shadow(0 2px 4px rgba(255,255,255,0.3))'
                                                }),
                                                "Advanced Funnel Comparison"
                                            ], style={
                                                'fontSize': '2.5rem',
                                                'fontWeight': '800',
                                                'margin': '0 0 1rem 0',
                                                'color': 'white',
                                                'textShadow': '0 2px 10px rgba(0,0,0,0.3)',
                                                'display': 'flex',
                                                'alignItems': 'center'
                                            }),
                                            html.P([
                                                "🚀 Compare recruitment funnels across different sources, job titles, and time periods",
                                                html.Br(),
                                                "📊 Identify patterns and discover optimization opportunities with interactive analytics"
                                            ], style={
                                                'fontSize': '1.25rem',
                                                'margin': '0',
                                                'opacity': '0.95',
                                                'lineHeight': '1.6',
                                                'maxWidth': '800px'
                                            })
                                        ], style={
                                            'position': 'relative',
                                            'zIndex': '2'
                                        })
                                    ], style={
                                        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                        'padding': '4rem 3rem',
                                        'borderRadius': '24px',
                                        'color': 'white',
                                        'marginBottom': '3rem',
                                        'position': 'relative',
                                        'overflow': 'hidden',
                                        'boxShadow': '0 20px 40px -10px rgba(102, 126, 234, 0.4)'
                                    }),
                                    
                                    # Floating decorative elements
                                    html.Div([
                                        html.Div(style={
                                            'position': 'absolute',
                                            'top': '20%',
                                            'right': '10%',
                                            'width': '150px',
                                            'height': '150px',
                                            'background': 'rgba(255, 255, 255, 0.1)',
                                            'borderRadius': '50%',
                                            'animation': 'float 6s ease-in-out infinite'
                                        }),
                                        html.Div(style={
                                            'position': 'absolute',
                                            'bottom': '20%',
                                            'left': '15%',
                                            'width': '100px',
                                            'height': '100px',
                                            'background': 'rgba(255, 255, 255, 0.08)',
                                            'borderRadius': '50%',
                                            'animation': 'float 8s ease-in-out infinite reverse'
                                        }),
                                        html.Div(style={
                                            'position': 'absolute',
                                            'top': '60%',
                                            'right': '20%',
                                            'width': '80px',
                                            'height': '80px',
                                            'background': 'rgba(255, 255, 255, 0.06)',
                                            'borderRadius': '50%',
                                            'animation': 'float 7s ease-in-out infinite'
                                        })
                                    ], style={'position': 'absolute', 'top': '0', 'left': '0', 'right': '0', 'bottom': '0', 'zIndex': '1'})
                                ], style={'position': 'relative'}),

                                # Interactive Setup Card
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.H3([
                                                html.I(className="fas fa-rocket", style={
                                                    'fontSize': '1.5rem',
                                                    'marginRight': '1rem',
                                                    'color': '#667eea'
                                                }),
                                                "Quick Setup"
                                            ], style={
                                                'fontSize': '1.75rem',
                                                'fontWeight': '700',
                                                'margin': '0 0 0.5rem 0',
                                                'color': '#1a202c'
                                            }),
                                            html.P("Configure your comparison parameters in seconds", style={
                                                'color': '#718096',
                                                'fontSize': '1.1rem',
                                                'margin': '0 0 2rem 0'
                                            })
                                        ]),
                                        
                                        html.Div([
                                            # Number of comparisons with enhanced styling
                                            html.Div([
                                                html.Div([
                                                    html.Label([
                                                        html.I(className="fas fa-layer-group", style={
                                                            'marginRight': '0.5rem',
                                                            'color': '#667eea'
                                                        }),
                                                        "Number of Comparisons"
                                                    ], style={
                                                        'fontSize': '1rem',
                                                        'fontWeight': '600',
                                                        'color': '#2d3748',
                                                        'marginBottom': '1rem',
                                                        'display': 'block'
                                                    }),
                                                    dcc.Dropdown(
                                                        id='comparison-count',
                                                        options=[
                                                            {
                                                                'label': html.Div([
                                                                    html.I(className="fas fa-chart-bar", style={'marginRight': '0.5rem', 'color': '#667eea'}),
                                                                    "2 Comparisons"
                                                                ], style={'display': 'flex', 'alignItems': 'center'}), 
                                                                'value': 2
                                                            },
                                                            {
                                                                'label': html.Div([
                                                                    html.I(className="fas fa-chart-line", style={'marginRight': '0.5rem', 'color': '#764ba2'}),
                                                                    "3 Comparisons"
                                                                ], style={'display': 'flex', 'alignItems': 'center'}), 
                                                                'value': 3
                                                            },
                                                            {
                                                                'label': html.Div([
                                                                    html.I(className="fas fa-chart-area", style={'marginRight': '0.5rem', 'color': '#f093fb'}),
                                                                    "4 Comparisons"
                                                                ], style={'display': 'flex', 'alignItems': 'center'}), 
                                                                'value': 4
                                                            }
                                                        ],
                                                        value=2,
                                                        style={
                                                            'fontFamily': 'Inter',
                                                            'fontSize': '1rem',
                                                            'borderRadius': '12px'
                                                        },
                                                        className="modern-dropdown"
                                                    )
                                                ], style={
                                                    'background': 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)',
                                                    'padding': '2rem',
                                                    'borderRadius': '16px',
                                                    'border': '2px solid #e2e8f0',
                                                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                                                })
                                            ], style={'flex': '1', 'marginRight': '2rem'}),
                                            
                                            # Generate button with amazing styling
                                            html.Div([
                                                html.Button([
                                                    html.I(className="fas fa-magic", style={
                                                        'fontSize': '1.25rem',
                                                        'marginRight': '1rem'
                                                    }),
                                                    html.Span("Generate Analysis", style={'fontSize': '1.125rem', 'fontWeight': '600'})
                                                ], 
                                                id='generate-comparison-btn',
                                                style={
                                                    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                                    'border': 'none',
                                                    'borderRadius': '16px',
                                                    'padding': '1.5rem 3rem',
                                                    'color': 'white',
                                                    'fontSize': '1.125rem',
                                                    'fontWeight': '600',
                                                    'cursor': 'pointer',
                                                    'boxShadow': '0 10px 25px -5px rgba(102, 126, 234, 0.4)',
                                                    'transition': 'all 0.3s ease',
                                                    'position': 'relative',
                                                    'overflow': 'hidden',
                                                    'minWidth': '250px',
                                                    'height': '80px',
                                                    'display': 'flex',
                                                    'alignItems': 'center',
                                                    'justifyContent': 'center'
                                                },
                                                className="generate-btn-enhanced"
                                                )
                                            ], style={'display': 'flex', 'alignItems': 'end'})
                                        ], style={'display': 'flex', 'alignItems': 'end', 'gap': '2rem'})
                                    ], style={
                                        'background': 'white',
                                        'padding': '3rem',
                                        'borderRadius': '20px',
                                        'boxShadow': '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
                                        'border': '1px solid #e2e8f0',
                                        'marginBottom': '3rem'
                                    })
                                ]),

                                # Pro Tips Card
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-lightbulb", style={
                                            'fontSize': '2rem',
                                            'marginBottom': '1rem',
                                            'color': '#f6ad55'
                                        }),
                                        html.H4("💡 Pro Tips", style={
                                            'fontSize': '1.5rem',
                                            'fontWeight': '700',
                                            'marginBottom': '1rem',
                                            'color': '#2d3748'
                                        }),
                                        html.Ul([
                                            html.Li("🎯 Compare different time periods (Q1 vs Q2) to identify seasonal trends"),
                                            html.Li("📊 Analyze source performance (LinkedIn vs Indeed) to optimize ad spend"),
                                            html.Li("🔍 Filter by job titles to understand role-specific recruitment patterns"),
                                            html.Li("⚡ Use 2-3 comparisons for clearest insights")
                                        ], style={
                                            'lineHeight': '2',
                                            'fontSize': '1rem',
                                            'color': '#4a5568',
                                            'paddingLeft': '1.5rem'
                                        })
                                    ], style={
                                        'background': 'linear-gradient(135deg, #fff5b4 0%, #fef5e7 100%)',
                                        'padding': '2rem',
                                        'borderRadius': '16px',
                                        'border': '2px solid #f6ad55',
                                        'marginBottom': '3rem',
                                        'boxShadow': '0 4px 12px rgba(246, 173, 85, 0.2)'
                                    })
                                ]),

                                # Dynamic Filters Container
                                html.Div(id='comparison-filters-container'),

                                # Results Container with Enhanced Styling
                                html.Div(id='comparison-results-container', style={'paddingTop': '2rem'}, children=[
                                    html.Div([
                                        html.Div([
                                            html.I(className="fas fa-chart-line", style={
                                                'fontSize': '5rem',
                                                'color': '#cbd5e0',
                                                'marginBottom': '2rem',
                                                'animation': 'pulse 2s infinite'
                                            }),
                                            html.H3("🚀 Ready for Analysis", style={
                                                'fontSize': '2rem',
                                                'fontWeight': '700',
                                                'color': '#2d3748',
                                                'marginBottom': '1rem'
                                            }),
                                            html.P([
                                                "Configure your comparison filters above and click ",
                                                html.Strong("'Generate Analysis'", style={
                                                    'color': '#667eea',
                                                    'background': 'linear-gradient(135deg, #667eea, #764ba2)',
                                                    'webkitBackgroundClip': 'text',
                                                    'webkitTextFillColor': 'transparent',
                                                    'fontSize': '1.1rem'
                                                }),
                                                " to unlock powerful insights with interactive charts and detailed analytics."
                                            ], style={
                                                'fontSize': '1.25rem',
                                                'color': '#718096',
                                                'lineHeight': '1.6',
                                                'maxWidth': '600px',
                                                'margin': '0 auto'
                                            }),
                                            
                                            # Feature preview cards
                                            html.Div([
                                                html.Div([
                                                    html.I(className="fas fa-funnel-dollar", style={
                                                        'fontSize': '2rem',
                                                        'color': '#667eea',
                                                        'marginBottom': '1rem'
                                                    }),
                                                    html.H5("Individual Funnels", style={
                                                        'fontSize': '1.1rem',
                                                        'fontWeight': '600',
                                                        'color': '#2d3748',
                                                        'marginBottom': '0.5rem'
                                                    }),
                                                    html.P("Detailed breakdown for each comparison", style={
                                                        'fontSize': '0.9rem',
                                                        'color': '#718096',
                                                        'margin': '0'
                                                    })
                                                ], style={
                                                    'background': 'white',
                                                    'padding': '1.5rem',
                                                    'borderRadius': '12px',
                                                    'textAlign': 'center',
                                                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                                    'border': '1px solid #e2e8f0'
                                                }),
                                                
                                                html.Div([
                                                    html.I(className="fas fa-chart-bar", style={
                                                        'fontSize': '2rem',
                                                        'color': '#764ba2',
                                                        'marginBottom': '1rem'
                                                    }),
                                                    html.H5("Side-by-Side", style={
                                                        'fontSize': '1.1rem',
                                                        'fontWeight': '600',
                                                        'color': '#2d3748',
                                                        'marginBottom': '0.5rem'
                                                    }),
                                                    html.P("Direct performance comparison", style={
                                                        'fontSize': '0.9rem',
                                                        'color': '#718096',
                                                        'margin': '0'
                                                    })
                                                ], style={
                                                    'background': 'white',
                                                    'padding': '1.5rem',
                                                    'borderRadius': '12px',
                                                    'textAlign': 'center',
                                                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                                    'border': '1px solid #e2e8f0'
                                                }),
                                                
                                                html.Div([
                                                    html.I(className="fas fa-percentage", style={
                                                        'fontSize': '2rem',
                                                        'color': '#f093fb',
                                                        'marginBottom': '1rem'
                                                    }),
                                                    html.H5("Conversion Rates", style={
                                                        'fontSize': '1.1rem',
                                                        'fontWeight': '600',
                                                        'color': '#2d3748',
                                                        'marginBottom': '0.5rem'
                                                    }),
                                                    html.P("Stage-by-stage optimization insights", style={
                                                        'fontSize': '0.9rem',
                                                        'color': '#718096',
                                                        'margin': '0'
                                                    })
                                                ], style={
                                                    'background': 'white',
                                                    'padding': '1.5rem',
                                                    'borderRadius': '12px',
                                                    'textAlign': 'center',
                                                    'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                                    'border': '1px solid #e2e8f0'
                                                })
                                            ], style={
                                                'display': 'grid',
                                                'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                                                'gap': '1.5rem',
                                                'marginTop': '3rem',
                                                'maxWidth': '800px',
                                                'margin': '3rem auto 0 auto'
                                            })
                                        ], style={
                                            'textAlign': 'center',
                                            'padding': '4rem 2rem',
                                            'background': 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)',
                                            'borderRadius': '20px',
                                            'border': '2px dashed #cbd5e0'
                                        })
                                    ])
                                ])
                            ], className="tab-content-modern", style={'padding': '2rem'})
                        ]
                    ),
                      dcc.Tab(
                          label='📋 Executive Summary',
                          value='summary',
                          children=[
                              html.Div([
                                  html.Div([
                                      html.H4([
                                          html.I(className="fas fa-chart-line me-2"),
                                          "Executive Dashboard"
                                      ], style={'marginBottom': '1rem', 'color': '#1f2937'}),
                                      html.P("Comprehensive overview of recruitment performance",
                                             style={'color': '#6b7280', 'marginBottom': '2rem'})
                                  ]),

                                  html.Div([
                                      html.Div([
                                          html.Div([
                                              html.H5([
                                                  html.I(className="fas fa-chart-pie me-2"),
                                                  "Volume Metrics"
                                              ], style={'color': '#1f2937', 'marginBottom': '1rem'}),
                                              html.Ul([
                                                  html.Li(f"Total Applications: {metrics['total_applications']:,}"),
                                                  html.Li(f"Unique Applicants: {metrics['unique_applicants']:,}"),
                                                  html.Li(f"Applications per Candidate: {metrics['applications_per_candidate']:.1f}"),
                                                  html.Li(f"Average Age: {metrics['avg_calculated_age']:.1f} years"),
                                              ], style={'lineHeight': '1.8'})
                                          ], className="insight-card", style={'height': '100%'})
                                      ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 1rem', 'verticalAlign': 'top'}),

                                      html.Div([
                                          html.Div([
                                              html.H5([
                                                  html.I(className="fas fa-bullseye me-2"),
                                                  "Success Metrics"
                                              ], style={'color': '#1f2937', 'marginBottom': '1rem'}),
                                              html.Ul([
                                                  html.Li(f"Qualification Rate: {metrics['qualification_rate']:.1f}%"),
                                                  html.Li(f"Overall Hire Rate: {metrics['overall_hire_rate']:.1f}%"),
                                                  html.Li(f"Hire Rate (Qualified): {metrics['hire_rate_from_qualified']:.1f}%"),
                                                  html.Li(f"Total Hired: {metrics['total_hired']:,} candidates"),
                                              ], style={'lineHeight': '1.8'})
                                          ], className="insight-card", style={'height': '100%'})
                                      ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 1rem', 'verticalAlign': 'top'})
                                  ], style={'marginBottom': '2rem'}),

                                  html.Div([
                                      html.Div([
                                          html.Div([
                                              html.H5([
                                                  html.I(className="fas fa-funnel-dollar me-2"),
                                                  "Funnel Performance"
                                              ], style={'color': '#1f2937', 'marginBottom': '1rem'}),
                                              html.Ul([
                                                  html.Li(f"{conversion}: {rate}%")
                                                  for conversion, rate in funnel_metrics['conversions'].items()
                                              ], style={'lineHeight': '1.8'})
                                          ], className="insight-card", style={'height': '100%'})
                                      ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 1rem', 'verticalAlign': 'top'}),

                                      html.Div([
                                          html.Div([
                                              html.H5([
                                                  html.I(className="fas fa-exclamation-triangle me-2"),
                                                  "Areas for Improvement"
                                              ], style={'color': '#1f2937', 'marginBottom': '1rem'}),
                                              html.Ul([
                                                  html.Li(f"Unqualified: {metrics['total_unqualified']:,} ({metrics['unqualified_rate']:.1f}%)"),
                                                  html.Li(f"Missing Feedback: {metrics['interviews_without_feedback']:,}"),
                                                  html.Li(f"Duplicate Applications: {metrics['duplicate_applications']:,}"),
                                                  html.Li(f"Long-term Reapplications: {metrics['reapplications_after_year']:,}"),
                                              ], style={'lineHeight': '1.8'})
                                          ], className="insight-card", style={'height': '100%'})
                                      ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 1rem', 'verticalAlign': 'top'})
                                  ])
                              ], className="tab-content-modern")
                          ]
                      )
                  ]
              )
          ])
      ])

      # Store processed data
      processed_data_store = {
          'candidate_master': filtered_master.to_dict('records'),
          'cleaned_data': processor.cleaned_data.to_dict('records'),
          'source_performance': source_performance.to_dict('records') if not source_performance.empty else [],
          'metrics': metrics,
          'funnel_metrics': funnel_metrics,
          'unqualified_analysis': unqualified_analysis,
          'age_analysis': age_analysis.to_dict('records') if not age_analysis.empty else [],
          'time_analysis': time_analysis,
          'candidates_by_stage': candidates_by_stage,
          'selected_sources': selected_sources,
          'all_sources': df['Application Source'].dropna().unique().tolist() if 'Application Source' in df.columns else [],
          'all_job_titles': df['Posting Title (Job Opening)'].dropna().unique().tolist() if 'Posting Title (Job Opening)' in df.columns else []
      }

      return processed_data_store, summary_cards, tabs_content, {'display': 'block', 'overflow': 'visible', 'marginBottom': '40px'}

  except Exception as e:
      error_msg = f"Error processing data: {str(e)}"
      print(error_msg)
      import traceback
      traceback.print_exc()
      return None, "", html.Div([
          html.I(className="fas fa-exclamation-circle", style={'fontSize': '3rem', 'color': '#ef4444', 'marginBottom': '1rem'}),
          html.H3("Processing Error", style={'marginBottom': '1rem', 'color': '#b91c1c'}),
          html.P(f"We encountered an error while processing your data: {error_msg}",
                 style={'color': '#6b7280', 'marginBottom': '1rem'}),
          html.P("Please check your CSV file format and try again.",
                 style={'color': '#6b7280'})
      ], style={'textAlign': 'center', 'padding': '3rem', 'background': '#fef2f2', 'borderRadius': '16px', 'border': '1px solid #fecaca'}), {'display': 'none'}

@app.callback(
  [Output('candidates-list', 'children'),
   Output('stage-metrics', 'children')],
  [Input('stage-selector', 'value')],
  [State('processed-data', 'data')],
  prevent_initial_call=True
)
def update_candidates_list(selected_stage, processed_data):
  if not processed_data or not selected_stage:
      return "No data available", ""

  try:
      candidates_by_stage = processed_data.get('candidates_by_stage', {})

      if selected_stage in candidates_by_stage:
          candidates = candidates_by_stage[selected_stage]

          # Create stage metrics
          qualified_candidates = sum(1 for c in processed_data['candidate_master'] if c.get('primary_status') != 'Unqualified')
          qualified_candidates = max(qualified_candidates, 1)  # Avoid division by zero

          stage_metrics = html.Div([
              html.Div([
                  html.Div([
                      html.H2(f"{len(candidates):,}", style={'color': '#6366f1', 'margin': 0, 'fontSize': '2.5rem', 'fontWeight': '800'}),
                      html.P("Candidates", style={'color': '#6b7280', 'margin': 0, 'fontSize': '0.875rem', 'fontWeight': '500'})
                  ], style={'textAlign': 'center', 'padding': '1.5rem', 'background': '#f8fafc', 'borderRadius': '12px', 'border': '1px solid #e2e8f0'})
              ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 0.5rem'}),

              html.Div([
                  html.Div([
                      html.H2(f"{(len(candidates)/qualified_candidates*100):.1f}%", style={'color': '#10b981', 'margin': 0, 'fontSize': '2.5rem', 'fontWeight': '800'}),
                      html.P("Of Qualified Pool", style={'color': '#6b7280', 'margin': 0, 'fontSize': '0.875rem', 'fontWeight': '500'})
                  ], style={'textAlign': 'center', 'padding': '1.5rem', 'background': '#f0fdf4', 'borderRadius': '12px', 'border': '1px solid #bbf7d0'})
              ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 0.5rem'})
          ])

          if candidates:
              # Create modern candidate cards
              candidate_cards = []
              for i, candidate in enumerate(candidates, 1):
                  candidate_cards.append(
                      html.Div([
                          html.Div([
                              html.Div([
                                  html.Span(f"{i}", style={'background': '#6366f1', 'color': 'white', 'borderRadius': '50%', 'width': '30px', 'height': '30px', 'display': 'inline-flex', 'alignItems': 'center', 'justifyContent': 'center', 'fontSize': '0.875rem', 'fontWeight': '600'}),
                                  html.Span(candidate, style={'marginLeft': '1rem', 'fontSize': '1rem', 'fontWeight': '500', 'color': '#1f2937'})
                              ], style={'display': 'flex', 'alignItems': 'center'})
                          ], style={'padding': '1rem'})
                      ], className="candidate-card", style={'marginBottom': '0.75rem'})
                  )

              candidates_display = html.Div([
                  html.H4([
                      html.I(className="fas fa-users me-2"),
                      f"Candidates in {selected_stage}"
                  ], style={'marginBottom': '1.5rem', 'color': '#1f2937'}),
                  html.Div([
                      html.Div(candidate_cards[:len(candidate_cards)//2] if len(candidate_cards) > 10 else candidate_cards,
                               style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '1rem'}),
                      html.Div(candidate_cards[len(candidate_cards)//2:] if len(candidate_cards) > 10 else [],
                               style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '1rem'})
                  ] if len(candidate_cards) > 10 else candidate_cards)
              ])
          else:
              candidates_display = html.Div([
                  html.I(className="fas fa-search", style={'fontSize': '3rem', 'color': '#6b7280', 'marginBottom': '1rem'}),
                  html.H4(f"No candidates found in {selected_stage}", style={'color': '#6b7280', 'marginBottom': '0.5rem'}),
                  html.P("This stage is empty for the current filter selection", style={'color': '#9ca3af'})
              ], style={'textAlign': 'center', 'padding': '3rem', 'background': '#f9fafb', 'borderRadius': '12px', 'border': '1px solid #e5e7eb'})

          return candidates_display, stage_metrics
      else:
          return html.Div([
              html.I(className="fas fa-exclamation-triangle", style={'fontSize': '3rem', 'color': '#f59e0b', 'marginBottom': '1rem'}),
              html.H4("Stage not found", style={'color': '#92400e', 'marginBottom': '0.5rem'}),
              html.P("The selected stage could not be found in the data", style={'color': '#6b7280'})
          ], style={'textAlign': 'center', 'padding': '3rem', 'background': '#fffbeb', 'borderRadius': '12px', 'border': '1px solid #fed7aa'}), ""

  except Exception as e:
      error_display = html.Div([
          html.I(className="fas fa-bug", style={'fontSize': '3rem', 'color': '#ef4444', 'marginBottom': '1rem'}),
          html.H4("Error displaying candidates", style={'color': '#b91c1c', 'marginBottom': '0.5rem'}),
          html.P(f"Error details: {str(e)}", style={'color': '#6b7280'})
      ], style={'textAlign': 'center', 'padding': '3rem', 'background': '#fef2f2', 'borderRadius': '12px', 'border': '1px solid #fecaca'})

      return error_display, ""

# NEW CALLBACKS FOR FUNNEL COMPARISON

# First, let's create a simpler, working comparison system
# Replace the update_comparison_filters callback with this fixed version:

@app.callback(
    Output('comparison-filters-container', 'children'),
    [Input('comparison-count', 'value')],
    [State('processed-data', 'data'),
     State('date-options', 'data')],
    prevent_initial_call=True
)
def update_comparison_filters(comparison_count, processed_data, date_options):
    if not processed_data or not comparison_count:
        return html.Div()
    
    all_sources = processed_data.get('all_sources', [])
    all_job_titles = processed_data.get('all_job_titles', [])
    
    # Get unique countries and nationalities from the candidate master data
    candidate_master = processed_data.get('candidate_master', [])
    
    # Extract unique values and clean them
    all_countries = []
    all_nationalities = []
    
    for candidate in candidate_master:
        # Country of Residence
        country = candidate.get('country_of_residence', '')
        if country and str(country).strip() and str(country).strip().lower() not in ['nan', 'none', '']:
            all_countries.append(str(country).strip())
        
        # Nationality
        nationality = candidate.get('nationality', '')
        if nationality and str(nationality).strip() and str(nationality).strip().lower() not in ['nan', 'none', '']:
            all_nationalities.append(str(nationality).strip())
    
    # Get unique values and sort them
    unique_countries = sorted(list(set(all_countries)))
    unique_nationalities = sorted(list(set(all_nationalities)))
    
    # Create checkbox options
    source_options = [{'label': source, 'value': source} for source in all_sources]
    job_title_options = [{'label': title, 'value': title} for title in all_job_titles]
    country_options = [{'label': country, 'value': country} for country in unique_countries]
    nationality_options = [{'label': nationality, 'value': nationality} for nationality in unique_nationalities]
    
    # FIXED: Get month and year options correctly (keeping your existing logic)
    month_options = []
    year_options = []
    week_options = []
    quarter_options = []
    
    if date_options:
        # Get all date options - skip the first "All" option
        raw_week_options = date_options.get('week', [])
        week_options = [opt for opt in raw_week_options if opt.get('value') != 'All']
        
        raw_month_options = date_options.get('month', [])
        month_options = [opt for opt in raw_month_options if opt.get('value') != 'All']
        
        raw_quarter_options = date_options.get('quarter', [])
        quarter_options = [opt for opt in raw_quarter_options if opt.get('value') != 'All']
        
        raw_year_options = date_options.get('year', [])
        year_options = [opt for opt in raw_year_options if opt.get('value') != 'All']
    
    # DEBUG: Print to console to see what we have
    print(f"DEBUG: Available countries: {len(unique_countries)} - {unique_countries[:5]}...")
    print(f"DEBUG: Available nationalities: {len(unique_nationalities)} - {unique_nationalities[:5]}...")
    print(f"DEBUG: Available weeks: {len(week_options)}")
    print(f"DEBUG: Available months: {len(month_options)}")
    print(f"DEBUG: Available quarters: {len(quarter_options)}")
    print(f"DEBUG: Available years: {len(year_options)}")
    
    filters = []
    
    for i in range(comparison_count):
        filter_card = html.Div([
            html.Div([
                html.H6([
                    html.I(className="fas fa-filter me-2"),
                    f"Comparison {i+1} Configuration"
                ], style={'margin': 0, 'fontSize': '1.125rem', 'fontWeight': '600'})
            ], className="comparison-card-header-enhanced", **{'data-index': str(i+1)}),
            
            html.Div([
                # Comparison name
                html.Div([
                    html.Label("Comparison Name:", className="comparison-form-label-enhanced"),
                    dcc.Input(
                        id={'type': 'comparison-name', 'index': i},
                        placeholder=f"e.g., LinkedIn Q1 vs Indeed Q2",
                        value=f"Comparison {i + 1}",
                        style={'width': '100%', 'padding': '0.75rem', 'borderRadius': '12px', 'border': '2px solid #e5e7eb', 'fontFamily': 'Inter'}
                    )
                ], className="comparison-form-group-enhanced"),
                
                # Source filter - CHECKBOXES
                html.Div([
                    html.Label("Application Sources:", className="comparison-form-label-enhanced"),
                    html.Div([
                        dcc.Checklist(
                            id={'type': 'comparison-sources', 'index': i},
                            options=source_options,
                            style={
                                'maxHeight': '200px', 
                                'overflowY': 'auto',
                                'border': '1px solid #e5e7eb',
                                'borderRadius': '12px',
                                'padding': '1rem',
                                'background': '#fafbfc'
                            },
                            labelStyle={
                                'display': 'block',
                                'margin': '0.5rem 0',
                                'padding': '0.25rem 0',
                                'fontSize': '14px'
                            },
                            inputStyle={
                                'marginRight': '0.5rem'
                            }
                        )
                    ])
                ], className="comparison-form-group-enhanced"),
                
                # Job title filter - CHECKBOXES
                html.Div([
                    html.Label("Job Titles:", className="comparison-form-label-enhanced"),
                    html.Div([
                        dcc.Checklist(
                            id={'type': 'comparison-job-titles', 'index': i},
                            options=job_title_options,
                            style={
                                'maxHeight': '200px', 
                                'overflowY': 'auto',
                                'border': '1px solid #e5e7eb',
                                'borderRadius': '12px',
                                'padding': '1rem',
                                'background': '#fafbfc'
                            },
                            labelStyle={
                                'display': 'block',
                                'margin': '0.5rem 0',
                                'padding': '0.25rem 0',
                                'fontSize': '14px'
                            },
                            inputStyle={
                                'marginRight': '0.5rem'
                            }
                        )
                    ])
                ], className="comparison-form-group-enhanced"),
                
                # NEW: Country of Residence filter - CHECKBOXES
                html.Div([
                    html.Label("Country of Residence:", className="comparison-form-label-enhanced"),
                    html.Div([
                        dcc.Checklist(
                            id={'type': 'comparison-countries', 'index': i},
                            options=country_options,
                            style={
                                'maxHeight': '150px', 
                                'overflowY': 'auto',
                                'border': '1px solid #e5e7eb',
                                'borderRadius': '12px',
                                'padding': '1rem',
                                'background': '#f0f9ff'
                            },
                            labelStyle={
                                'display': 'block',
                                'margin': '0.5rem 0',
                                'padding': '0.25rem 0',
                                'fontSize': '14px'
                            },
                            inputStyle={
                                'marginRight': '0.5rem'
                            }
                        )
                    ])
                ], className="comparison-form-group-enhanced"),
                
                # NEW: Nationality filter - CHECKBOXES
                html.Div([
                    html.Label("Nationality:", className="comparison-form-label-enhanced"),
                    html.Div([
                        dcc.Checklist(
                            id={'type': 'comparison-nationalities', 'index': i},
                            options=nationality_options,
                            style={
                                'maxHeight': '150px', 
                                'overflowY': 'auto',
                                'border': '1px solid #e5e7eb',
                                'borderRadius': '12px',
                                'padding': '1rem',
                                'background': '#f0fdf4'
                            },
                            labelStyle={
                                'display': 'block',
                                'margin': '0.5rem 0',
                                'padding': '0.25rem 0',
                                'fontSize': '14px'
                            },
                            inputStyle={
                                'marginRight': '0.5rem'
                            }
                        )
                    ])
                ], className="comparison-form-group-enhanced"),
                
                # Time period selector - KEEPING YOUR EXISTING CODE EXACTLY AS IS
                html.Div([
                    html.Label("Time Period Selection:", className="comparison-form-label-enhanced"),
                    dcc.RadioItems(
                        id={'type': 'comparison-time-type', 'index': i},
                        options=[
                            {'label': '🌐 All Time', 'value': 'all'},
                            {'label': '📅 Weeks', 'value': 'weeks'},
                            {'label': '📅 Months', 'value': 'months'},
                            {'label': '📊 Quarters', 'value': 'quarters'},
                            {'label': '📆 Years', 'value': 'years'},
                            {'label': '🎯 Custom Range', 'value': 'custom'}
                        ],
                        value='all',
                        inline=True,
                        style={'marginBottom': '10px'},
                        inputStyle={'margin': '0 0.5rem 0 0'},
                        labelStyle={'display': 'flex', 'alignItems': 'center', 'margin': '0 1rem 0 0', 'padding': '0.5rem 1rem', 'background': '#f8fafc', 'borderRadius': '8px', 'border': '1px solid #e2e8f0'}
                    )
                ], className="comparison-form-group-enhanced"),
                
                # Week selector - KEEPING YOUR EXISTING CODE
                html.Div([
                    html.Label("Select Weeks:", className="comparison-form-label-enhanced"),
                    dcc.Dropdown(
                        id={'type': 'comparison-weeks', 'index': i},
                        options=week_options,
                        multi=True,
                        placeholder="Choose specific weeks for analysis",
                        style={'fontFamily': 'Inter', 'minHeight': '40px', 'maxHeight': '200px'}
                    )
                ], id={'type': 'comparison-weeks-container', 'index': i}, 
                   className="comparison-form-group-enhanced", 
                   style={'display': 'none'}),
                
                # Month selector - KEEPING YOUR EXISTING CODE
                html.Div([
                    html.Label("Select Months:", className="comparison-form-label-enhanced"),
                    dcc.Dropdown(
                        id={'type': 'comparison-months', 'index': i},
                        options=month_options,
                        multi=True,
                        placeholder="Choose specific months for analysis",
                        style={'fontFamily': 'Inter', 'minHeight': '40px', 'maxHeight': '200px'}
                    )
                ], id={'type': 'comparison-months-container', 'index': i}, 
                   className="comparison-form-group-enhanced", 
                   style={'display': 'none'}),
                
                # Quarter selector - KEEPING YOUR EXISTING CODE
                html.Div([
                    html.Label("Select Quarters:", className="comparison-form-label-enhanced"),
                    dcc.Dropdown(
                        id={'type': 'comparison-quarters', 'index': i},
                        options=quarter_options,
                        multi=True,
                        placeholder="Choose specific quarters for analysis",
                        style={'fontFamily': 'Inter', 'minHeight': '40px', 'maxHeight': '200px'}
                    )
                ], id={'type': 'comparison-quarters-container', 'index': i}, 
                   className="comparison-form-group-enhanced", 
                   style={'display': 'none'}),
                
                # Year selector - KEEPING YOUR EXISTING CODE
                html.Div([
                    html.Label("Select Years:", className="comparison-form-label-enhanced"),
                    dcc.Dropdown(
                        id={'type': 'comparison-years', 'index': i},
                        options=year_options,
                        multi=True,
                        placeholder="Choose specific years for analysis",
                        style={'fontFamily': 'Inter', 'minHeight': '40px', 'maxHeight': '200px'}
                    )
                ], id={'type': 'comparison-years-container', 'index': i}, 
                   className="comparison-form-group-enhanced", 
                   style={'display': 'none'}),
                
                # Custom date range picker - KEEPING YOUR EXISTING CODE
                html.Div([
                    html.Label("Select Date Range:", className="comparison-form-label-enhanced"),
                    dcc.DatePickerRange(
                        id={'type': 'comparison-custom-date', 'index': i},
                        start_date_placeholder_text="Start Date",
                        end_date_placeholder_text="End Date",
                        display_format='YYYY-MM-DD',
                        style={'width': '100%', 'zIndex': 900}
                    )
                ], id={'type': 'comparison-custom-container', 'index': i}, 
                   className="comparison-form-group-enhanced", 
                   style={'display': 'none'})
                
            ], style={'padding': '2rem'})
        ], className="enhanced-comparison-card")
        
        filters.append(filter_card)
    
    return html.Div([
        html.Div([
            html.H5([
                html.I(className="fas fa-sliders-h me-2"),
                "Filter Configurations"
            ], className="section-title-enhanced"),
            html.P("Configure unique filter combinations for each comparison", 
                   className="section-subtitle-enhanced")
        ], className="enhanced-section-header"),
        
        html.Div(filters, className="funnel-comparison-grid", style={'marginBottom': '4rem'})
    ], style={'marginBottom': '4rem', 'position': 'relative', 'zIndex': 1000})

# Callback to show/hide time period selectors using pattern-matching
@app.callback(
    [Output({'type': 'comparison-weeks-container', 'index': dash.dependencies.MATCH}, 'style'),
     Output({'type': 'comparison-months-container', 'index': dash.dependencies.MATCH}, 'style'),
     Output({'type': 'comparison-quarters-container', 'index': dash.dependencies.MATCH}, 'style'),
     Output({'type': 'comparison-years-container', 'index': dash.dependencies.MATCH}, 'style'),
     Output({'type': 'comparison-custom-container', 'index': dash.dependencies.MATCH}, 'style')],
    [Input({'type': 'comparison-time-type', 'index': dash.dependencies.MATCH}, 'value')],
    prevent_initial_call=True
)
def toggle_time_period_selectors(time_type):
    if time_type == 'weeks':
        return {'display': 'block', 'marginBottom': '150px'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
    elif time_type == 'months':
        return {'display': 'none'}, {'display': 'block', 'marginBottom': '150px'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
    elif time_type == 'quarters':
        return {'display': 'none'}, {'display': 'none'}, {'display': 'block', 'marginBottom': '150px'}, {'display': 'none'}, {'display': 'none'}
    elif time_type == 'years':
        return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'block', 'marginBottom': '150px'}, {'display': 'none'}
    elif time_type == 'custom':
        return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'block', 'marginBottom': '400px'}
    else:
        return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
def create_comparison_funnel_with_buttons(name, result, index):
    """Create a comparison funnel with clickable buttons"""
    funnel_data = result['funnel_data']
    
    # Create the funnel chart
    fig_funnel = go.Figure(go.Funnel(
        y=list(funnel_data.keys()),
        x=list(funnel_data.values()),
        textinfo="value+percent previous",
        marker=dict(
            color=['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b'],
            line=dict(width=2, color='white')
        ),
        textfont=dict(size=14, color='white', family='Inter')
    ))
    
    fig_funnel = create_enhanced_plotly_theme(fig_funnel, name)
    fig_funnel.update_layout(height=500)
    
    # Create buttons with UNIQUE IDs that include the comparison index
    stage_buttons = []
    colors = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b']
    
    for i, (stage, count) in enumerate(funnel_data.items()):
        # IMPORTANT: Use unique button IDs that include the comparison index
        stage_key = stage.replace(" ", "").replace("→", "")
        button_id = f'comp-btn-{index}-{stage_key}'
        
        stage_buttons.append(
            html.Button([
                html.I(className="fas fa-users", style={'marginRight': '6px'}),
                html.Span(f"{stage} ({count:,})", style={'fontWeight': '600', 'fontSize': '12px'})
            ], 
            id=button_id,
            **{'data-comparison': index, 'data-stage': stage},  # Store data attributes
            style={
                'background': colors[i % len(colors)],
                'color': 'white',
                'border': 'none',
                'borderRadius': '8px',
                'padding': '8px 12px',
                'margin': '3px 0',
                'width': '100%',
                'cursor': 'pointer',
                'fontSize': '12px'
            }
        ))
    
    return html.Div([
        html.Div([
            html.H6(name, style={'color': 'white', 'margin': 0, 'fontSize': '1.1rem', 'fontWeight': '600'})
        ], className="chart-header-enhanced"),
        
        html.Div([
            html.Div([
                html.I(className="fas fa-filter me-2"),
                html.Small(result['filter_description'], style={'fontSize': '0.8rem', 'color': '#6b7280'})
            ], style={'marginBottom': '1rem', 'padding': '0.5rem', 'background': '#f8fafc', 'borderRadius': '6px'}),
            
            html.Div([
                html.Div([dcc.Graph(figure=fig_funnel, config={'displayModeBar': False})], 
                        style={'width': '70%', 'display': 'inline-block'}),
                html.Div(stage_buttons, 
                        style={'width': '30%', 'display': 'inline-block', 'padding': '0 0 0 10px', 'verticalAlign': 'top'})
            ])
        ], style={'padding': '1.5rem'})
    ], className="chart-container-enhanced")

@app.callback(
    [Output('comparison-results-container', 'children'),
     Output('comparison-candidates-data', 'data')],
    [Input('generate-comparison-btn', 'n_clicks')],
    [State('comparison-count', 'value'),
     State('processed-data', 'data'),
     State({'type': 'comparison-name', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'comparison-sources', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'comparison-job-titles', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'comparison-countries', 'index': dash.dependencies.ALL}, 'value'),  # NEW
     State({'type': 'comparison-nationalities', 'index': dash.dependencies.ALL}, 'value'),  # NEW
     State({'type': 'comparison-time-type', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'comparison-weeks', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'comparison-months', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'comparison-quarters', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'comparison-years', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'comparison-custom-date', 'index': dash.dependencies.ALL}, 'start_date'),
     State({'type': 'comparison-custom-date', 'index': dash.dependencies.ALL}, 'end_date')],
    prevent_initial_call=True
)
def generate_funnel_comparison_with_new_filters(n_clicks, comparison_count, processed_data, 
                              names, sources_list, job_titles_list, 
                              countries_list, nationalities_list,  # NEW PARAMETERS
                              time_types, weeks_list, months_list, 
                              quarters_list, years_list, custom_start_dates, custom_end_dates):
    if not n_clicks or not processed_data or not comparison_count:
        return html.Div([
            html.Div([
                html.I(className="fas fa-info-circle me-2"),
                html.Strong("Ready to Compare: "),
                html.Span("Set up your comparison filters above and click 'Generate Comparison' to see the results.", 
                         style={'fontSize': '0.875rem'})
            ], className="info-callout-enhanced")
        ]), {}
    
    try:
        print("🔍 DEBUG: Starting comparison generation with new filters...")
        
        # Reconstruct analytics from processed data
        df = pd.DataFrame(processed_data['cleaned_data'])
        candidate_master = pd.DataFrame(processed_data['candidate_master'])
        analytics = RecruitmentAnalytics(df, candidate_master, processed_data['metrics'])
        
        comparison_results = {}
        comparison_candidates = {}
        
        for i in range(comparison_count):
            print(f"\n🔍 DEBUG: Processing comparison {i}...")
            
            # Get values for this comparison
            comparison_name = names[i] if i < len(names) and names[i] else f"Comparison {i+1}"
            selected_sources = sources_list[i] if i < len(sources_list) and sources_list[i] else []
            selected_job_titles = job_titles_list[i] if i < len(job_titles_list) and job_titles_list[i] else []
            selected_countries = countries_list[i] if i < len(countries_list) and countries_list[i] else []  # NEW
            selected_nationalities = nationalities_list[i] if i < len(nationalities_list) and nationalities_list[i] else []  # NEW
            time_type = time_types[i] if i < len(time_types) and time_types[i] else 'all'
            selected_months = months_list[i] if i < len(months_list) and months_list[i] else []
            selected_years = years_list[i] if i < len(years_list) and years_list[i] else []
            
            # Apply filters step by step
            filtered_master = candidate_master.copy()
            print(f"🔍 DEBUG: Starting with {len(filtered_master)} candidates")
            
            # Apply source filter
            if selected_sources and len(selected_sources) > 0:
                filtered_master = analytics.filter_by_sources(selected_sources)
                print(f"🔍 DEBUG: After source filter: {len(filtered_master)} candidates")
            
            # Apply job title filter  
            if selected_job_titles and len(selected_job_titles) > 0:
                filtered_master = analytics.filter_by_job_titles(selected_job_titles, filtered_master)
                print(f"🔍 DEBUG: After job title filter: {len(filtered_master)} candidates")
            
            # NEW: Apply country filter
            if selected_countries and len(selected_countries) > 0:
                filtered_master = filtered_master[
                    filtered_master['country_of_residence'].isin(selected_countries)
                ]
                print(f"🔍 DEBUG: After country filter: {len(filtered_master)} candidates")
            
            # NEW: Apply nationality filter
            if selected_nationalities and len(selected_nationalities) > 0:
                filtered_master = filtered_master[
                    filtered_master['nationality'].isin(selected_nationalities)
                ]
                print(f"🔍 DEBUG: After nationality filter: {len(filtered_master)} candidates")
            
            # Apply time filter
            if time_type == 'months' and selected_months:
                filtered_master = analytics.filter_by_date_range('month', selected_months, None, filtered_master)
                print(f"🔍 DEBUG: After time filter: {len(filtered_master)} candidates")
            elif time_type == 'years' and selected_years:
                filtered_master = analytics.filter_by_date_range('year', selected_years, None, filtered_master)
                print(f"🔍 DEBUG: After time filter: {len(filtered_master)} candidates")
            
            # Calculate funnel metrics
            funnel_metrics = analytics.calculate_funnel_metrics(filtered_master)
            summary_metrics = analytics.generate_summary_metrics(filtered_master)
            
            # Get candidates by stage
            comparison_candidates_by_stage = analytics.get_candidates_by_stage(filtered_master)
            
            print(f"🔍 DEBUG: Candidates by stage for comparison {i}:")
            for stage, candidates in comparison_candidates_by_stage.items():
                print(f"🔍 DEBUG:   {stage}: {len(candidates)} candidates")
            
            # Create filter description - UPDATED with new filters
            filter_parts = []
            if selected_sources:
                filter_parts.append(f"Sources: {', '.join(selected_sources)}")
            if selected_job_titles:
                filter_parts.append(f"Jobs: {', '.join(selected_job_titles)}")
            if selected_countries:  # NEW
                filter_parts.append(f"Countries: {', '.join(selected_countries)}")
            if selected_nationalities:  # NEW
                filter_parts.append(f"Nationalities: {', '.join(selected_nationalities)}")
            if time_type == 'months' and selected_months:
                filter_parts.append(f"Months: {', '.join(selected_months)}")
            elif time_type == 'years' and selected_years:
                filter_parts.append(f"Years: {', '.join(map(str, selected_years))}")
            
            filter_description = '; '.join(filter_parts) if filter_parts else 'All Data'
            
            comparison_results[comparison_name] = {
                'funnel_data': funnel_metrics['funnel_data'],
                'conversions': funnel_metrics['conversions'],
                'summary_metrics': summary_metrics,
                'filter_description': filter_description
            }
            
            # Store candidates using STRING keys
            comparison_candidates[str(i)] = comparison_candidates_by_stage
            print(f"🔍 DEBUG: Stored candidates for comparison '{i}' with {len(comparison_candidates_by_stage)} stages")
        
        print(f"\n🔍 DEBUG: Final comparison_candidates keys: {list(comparison_candidates.keys())}")
        for key, stages in comparison_candidates.items():
            print(f"🔍 DEBUG: Comparison {key} has stages: {list(stages.keys())}")
        
        if not comparison_results:
            return html.Div([
                html.H4("No comparison results generated", style={'color': '#ef4444'})
            ]), {}
        
        # Create individual funnel charts (same as before)
        individual_funnels = []
        
        for idx, (name, result) in enumerate(comparison_results.items()):
            funnel_data = result['funnel_data']
            
            # Create the funnel chart
            fig_funnel = go.Figure(go.Funnel(
                y=list(funnel_data.keys()),
                x=list(funnel_data.values()),
                textinfo="value+percent previous",
                marker=dict(
                    color=['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b'],
                    line=dict(width=2, color='white')
                ),
                textfont=dict(size=14, color='white', family='Inter')
            ))
            
            fig_funnel = create_enhanced_plotly_theme(fig_funnel, name)
            fig_funnel.update_layout(height=500)
            
            # Create buttons
            stage_buttons = []
            colors = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b']
            
            for i, (stage, count) in enumerate(funnel_data.items()):
                stage_key = stage.replace(" ", "").replace("→", "")
                button_id = f'comp-btn-{idx}-{stage_key}'
                
                stage_buttons.append(
                    html.Button([
                        html.I(className="fas fa-users", style={'marginRight': '6px'}),
                        html.Span(f"{stage} ({count:,})", style={'fontWeight': '600', 'fontSize': '12px'})
                    ], 
                    id={'type': 'comp-btn', 'index': button_id},
                    style={
                        'background': colors[i % len(colors)],
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '8px',
                        'padding': '8px 12px',
                        'margin': '3px 0',
                        'width': '100%',
                        'cursor': 'pointer',
                        'fontSize': '12px'
                    }))
            
            # Create the funnel container
            individual_funnels.append(
                html.Div([
                    html.Div([
                        html.H6(name, style={'color': 'white', 'margin': 0, 'fontSize': '1.1rem', 'fontWeight': '600'})
                    ], style={'background': '#374151', 'padding': '1rem'}),
                    
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-filter me-2"),
                            html.Small(result['filter_description'], style={'fontSize': '0.8rem', 'color': '#6b7280'})
                        ], style={'marginBottom': '1rem', 'padding': '0.5rem', 'background': '#f8fafc', 'borderRadius': '6px'}),
                        
                        html.Div([
                            html.Div([dcc.Graph(figure=fig_funnel, config={'displayModeBar': False})], 
                                    style={'width': '70%', 'display': 'inline-block'}),
                            html.Div([
                                html.H6("📊 View Candidates", style={'marginBottom': '1rem', 'color': '#374151'}),
                                html.Div(stage_buttons)
                            ], style={'width': '30%', 'display': 'inline-block', 'padding': '0 0 0 10px', 'verticalAlign': 'top'})
                        ])
                    ], style={'padding': '1.5rem'})
                ], style={'background': 'white', 'borderRadius': '16px', 'marginBottom': '2rem', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
            )
        
        # Create results HTML
        results_html = html.Div([
            html.H4([
                html.I(className="fas fa-check-circle me-2"),
                f"✅ Generated {len(comparison_results)} Comparisons Successfully!"
            ], style={'color': '#059669', 'marginBottom': '2rem'}),
            
            html.Div([
                html.H5("Individual Funnel Analysis", style={'marginBottom': '1rem'}),
                html.Div(individual_funnels)
            ])
        ])
        
        print(f"🔍 DEBUG: Returning candidates data with keys: {list(comparison_candidates.keys())}")
        return results_html, comparison_candidates
        
    except Exception as e:
        error_msg = f"Error generating comparison: {str(e)}"
        print(f"🔍 DEBUG ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        
        return html.Div([
            html.H4("Processing Error", style={'color': '#ef4444'}),
            html.P(f"Error: {error_msg}")
        ]), {}
# Remove all the old manual comparison callbacks and replace them with the above
# Also, make sure to add the necessary import at the top of your file:
import dash.dependencies
def create_manual_comparison_section(index, processed_data):
    """Create a manual comparison section with working dropdowns"""
    all_sources = processed_data.get('all_sources', [])
    all_job_titles = processed_data.get('all_job_titles', [])
    
    source_options = [{'label': f'📊 {source}', 'value': source} for source in all_sources]
    job_title_options = [{'label': f'📋 {title}', 'value': title} for title in all_job_titles]
    
    # Get date options from processed data
    candidate_master = pd.DataFrame(processed_data['candidate_master'])
    
    # Get available months
    if 'application_month' in candidate_master.columns:
        months = sorted(candidate_master['application_month'].dropna().unique())
        month_options = [{'label': f'📅 {month}', 'value': month} for month in months if month != '']
    else:
        month_options = []
    
    # Get available years  
    if 'application_year' in candidate_master.columns:
        years = sorted(candidate_master['application_year'].dropna().unique())
        year_options = [{'label': f'📆 {int(year)}', 'value': int(year)} for year in years if pd.notna(year)]
    else:
        year_options = []
    
    return html.Div([
        html.Div([
            html.H5([
                html.I(className="fas fa-filter me-2"),
                f"Comparison {index + 1}"
            ], style={'color': 'white', 'margin': 0})
        ], className="funnel-comparison-header"),
        
        html.Div([
            # Comparison name
            html.Div([
                html.Label("Comparison Name:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Input(
                    id=f'manual-comparison-name-{index}',
                    placeholder=f"e.g., LinkedIn Q1 2024",
                    value=f"Comparison {index + 1}",
                    style={'width': '100%', 'padding': '8px', 'borderRadius': '6px', 'border': '1px solid #d1d5db'}
                )
            ], style={'marginBottom': '1rem'}),
            
            # Sources
            html.Div([
                html.Label("Sources:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Dropdown(
                    id=f'manual-sources-{index}',
                    options=source_options,
                    multi=True,
                    placeholder="Select sources to include",
                    style={'fontFamily': 'Inter'}
                )
            ], style={'marginBottom': '1rem'}),
            
            # Job titles
            html.Div([
                html.Label("Job Titles:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Dropdown(
                    id=f'manual-job-titles-{index}',
                    options=job_title_options,
                    multi=True,
                    placeholder="Select job titles to include",
                    style={'fontFamily': 'Inter'}
                )
            ], style={'marginBottom': '1rem'}),
            
            # Time period
            html.Div([
                html.Label("Time Period:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.RadioItems(
                    id=f'manual-time-type-{index}',
                    options=[
                        {'label': 'Specific Months', 'value': 'months'},
                        {'label': 'Specific Years', 'value': 'years'},
                        {'label': 'All Time', 'value': 'all'}
                    ],
                    value='all',
                    inline=True,
                    style={'marginBottom': '10px'}
                )
            ], style={'marginBottom': '1rem'}),
            
            # Month selector
            html.Div([
                html.Label("Select Months:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Dropdown(
                    id=f'manual-months-{index}',
                    options=month_options,
                    multi=True,
                    placeholder="Select specific months",
                    style={'fontFamily': 'Inter'}
                )
            ], id=f'manual-months-container-{index}', style={'display': 'none', 'marginBottom': '1rem'}),
            
            # Year selector
            html.Div([
                html.Label("Select Years:", style={'fontWeight': '600', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Dropdown(
                    id=f'manual-years-{index}',
                    options=year_options,
                    multi=True,
                    placeholder="Select specific years",
                    style={'fontFamily': 'Inter'}
                )
            ], id=f'manual-years-container-{index}', style={'display': 'none', 'marginBottom': '1rem'})
            
        ], style={'padding': '1.5rem'})
    ], className="funnel-comparison-item", style={'marginBottom': '1.5rem'})

# Add callbacks to show/hide time period selectors
for i in range(4):  # Support up to 4 comparisons
    @app.callback(
        [Output(f'manual-months-container-{i}', 'style'),
         Output(f'manual-years-container-{i}', 'style')],
        [Input(f'manual-time-type-{i}', 'value')],
        prevent_initial_call=True
    )
    def toggle_time_selectors(time_type, comparison_index=i):
        if time_type == 'months':
            return {'display': 'block', 'marginBottom': '1rem'}, {'display': 'none'}
        elif time_type == 'years':
            return {'display': 'none'}, {'display': 'block', 'marginBottom': '1rem'}
        else:
            return {'display': 'none'}, {'display': 'none'}

# Main callback to process the manual comparisons
@app.callback(
    Output('manual-comparison-results', 'children'),
    [Input('apply-manual-comparison-btn', 'n_clicks')],
    [State('comparison-count', 'value'),
     State('processed-data', 'data')] +
    # Manual comparison states
    [State(f'manual-comparison-name-{i}', 'value') for i in range(4)] +
    [State(f'manual-sources-{i}', 'value') for i in range(4)] +
    [State(f'manual-job-titles-{i}', 'value') for i in range(4)] +
    [State(f'manual-time-type-{i}', 'value') for i in range(4)] +
    [State(f'manual-months-{i}', 'value') for i in range(4)] +
    [State(f'manual-years-{i}', 'value') for i in range(4)],
    prevent_initial_call=True
)
def process_manual_comparisons(n_clicks, comparison_count, processed_data, *args):
    if not n_clicks or not processed_data or not comparison_count:
        return html.Div()
    
    try:
        # Parse the arguments
        names = args[0:4]
        sources_list = args[4:8]
        job_titles_list = args[8:12]
        time_types = args[12:16]
        months_list = args[16:20]
        years_list = args[20:24]
        
        # Reconstruct analytics - SAME AS OVERVIEW TAB
        df = pd.DataFrame(processed_data['cleaned_data'])
        candidate_master = pd.DataFrame(processed_data['candidate_master'])
        analytics = RecruitmentAnalytics(df, candidate_master, processed_data['metrics'])
        
        comparison_results = {}
        
        for i in range(comparison_count):
            comparison_name = names[i] if names[i] else f"Comparison {i+1}"
            selected_sources = sources_list[i] if sources_list[i] else []
            selected_job_titles = job_titles_list[i] if job_titles_list[i] else []
            time_type = time_types[i] if time_types[i] else 'all'
            selected_months = months_list[i] if months_list[i] else []
            selected_years = years_list[i] if years_list[i] else []
            
            # Apply filters step by step - SAME LOGIC AS MAIN DASHBOARD
            filtered_master = analytics.candidate_master.copy()
            
            # Apply source filter
            if selected_sources and len(selected_sources) > 0:
                filtered_master = analytics.filter_by_sources(selected_sources)
            
            # Apply job title filter  
            if selected_job_titles and len(selected_job_titles) > 0:
                filtered_master = analytics.filter_by_job_titles(selected_job_titles, filtered_master)
            
            # Apply time filter
            if time_type == 'months' and selected_months:
                filtered_master = analytics.filter_by_date_range('month', selected_months, None, filtered_master)
            elif time_type == 'years' and selected_years:
                filtered_master = analytics.filter_by_date_range('year', selected_years, None, filtered_master)
            
            # Calculate funnel metrics - EXACT SAME AS OVERVIEW TAB
            funnel_metrics = analytics.calculate_funnel_metrics(filtered_master)
            summary_metrics = analytics.generate_summary_metrics(filtered_master)
            
            # Create filter description
            filter_parts = []
            if selected_sources:
                filter_parts.append(f"Sources: {', '.join(selected_sources)}")
            if selected_job_titles:
                filter_parts.append(f"Jobs: {', '.join(selected_job_titles)}")
            if time_type == 'months' and selected_months:
                filter_parts.append(f"Months: {', '.join(selected_months)}")
            elif time_type == 'years' and selected_years:
                filter_parts.append(f"Years: {', '.join(map(str, selected_years))}")
            
            filter_description = '; '.join(filter_parts) if filter_parts else 'All Data'
            
            comparison_results[comparison_name] = {
                'funnel_data': funnel_metrics['funnel_data'],
                'conversions': funnel_metrics['conversions'],
                'summary_metrics': summary_metrics,
                'filter_description': filter_description
            }
        
        if not comparison_results:
            return html.Div([
                html.I(className="fas fa-exclamation-triangle", style={'fontSize': '3rem', 'color': '#f59e0b', 'marginBottom': '1rem'}),
                html.H4("No comparison data", style={'color': '#92400e', 'marginBottom': '0.5rem'}),
                html.P("Please set up at least one comparison above", style={'color': '#6b7280'})
            ], style={'textAlign': 'center', 'padding': '3rem', 'background': '#fffbeb', 'borderRadius': '16px', 'border': '1px solid #fed7aa'})
        
        # Create individual funnel charts - EXACT SAME AS OVERVIEW TAB
        funnel_charts = []
        
        for name, result in comparison_results.items():
            funnel_data = result['funnel_data']
            
            # Create individual funnel chart - IDENTICAL TO OVERVIEW TAB
            fig_funnel = go.Figure(go.Funnel(
                y=list(funnel_data.keys()),
                x=list(funnel_data.values()),
                textinfo="value+percent previous",  # SAME AS OVERVIEW TAB
                marker=dict(
                    color=['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b'],
                    line=dict(width=2, color='white')
                ),
                textfont=dict(size=14, color='white', family='Inter')
            ))
            
            fig_funnel = create_enhanced_plotly_theme(fig_funnel, f"{name}")
            fig_funnel.update_layout(height=500)
            fig_funnel.update_layout(clickmode='event+select')
            funnel_charts.append(
                html.Div([
                    html.Div([
                        html.H6(name, style={'color': 'white', 'margin': 0, 'fontSize': '1.125rem', 'fontWeight': '600'})
                    ], className="funnel-comparison-header"),
                    
                    html.Div([
                        html.P(result['filter_description'], style={
                            'fontSize': '0.875rem', 
                            'color': '#6b7280', 
                            'marginBottom': '1rem',
                            'fontStyle': 'italic'
                        }),
                        
                        # Summary metrics
                        html.Div([
                            html.Div([
                                html.Div(f"{result['summary_metrics']['unique_candidates']:,}", className="comparison-metric-value"),
                                html.Div("Candidates", className="comparison-metric-label")
                            ], className="comparison-metric-card"),
                            
                            html.Div([
                                html.Div(f"{result['summary_metrics']['qualification_rate']:.1f}%", className="comparison-metric-value"),
                                html.Div("Qualified", className="comparison-metric-label")
                            ], className="comparison-metric-card"),
                            
                            html.Div([
                                html.Div(f"{result['summary_metrics']['total_hired']:,}", className="comparison-metric-value"),
                                html.Div("Hired", className="comparison-metric-label")
                            ], className="comparison-metric-card"),
                            
                            html.Div([
                                html.Div(f"{result['summary_metrics']['hire_rate_from_qualified']:.1f}%", className="comparison-metric-value"),
                                html.Div("Hire Rate", className="comparison-metric-label")
                            ], className="comparison-metric-card")
                        ], className="comparison-metrics-row", style={'marginBottom': '1rem'}),
                        
                        dcc.Graph(figure=fig_funnel, config={'displayModeBar': False}, id='overview-funnel-graph')
                    ], style={'padding': '1rem'})
                ], className="funnel-comparison-item", style={'marginBottom': '2rem'})
            )
        
        # Create side-by-side comparison chart
        fig_comparison = go.Figure()
        colors = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b']
        
        stage_order = ['Applied', 'Received Test', 'Did Test', 'Passed Test', 'Booked Interview', 'Passed Interview', 'Hired']
        
        for i, (name, result) in enumerate(comparison_results.items()):
            funnel_data = result['funnel_data']
            color = colors[i % len(colors)]
            
            ordered_values = [funnel_data.get(stage, 0) for stage in stage_order]
            
            fig_comparison.add_trace(go.Scatter(
                x=stage_order,
                y=ordered_values,
                mode='lines+markers+text',
                name=name,
                line=dict(color=color, width=4),
                marker=dict(size=12, color=color, line=dict(width=2, color='white')),
                text=[f"{v:,}" for v in ordered_values],
                textposition="top center",
                textfont=dict(size=10, color=color, family='Inter'),
                hovertemplate=f'<b>{name}</b><br>' +
                             '<b>%{x}</b><br>' +
                             'Count: %{y:,}<extra></extra>'
            ))
        
        fig_comparison = create_enhanced_plotly_theme(fig_comparison, "Custom Funnel Comparison")
        fig_comparison.update_layout(height=600, xaxis_title="Funnel Stages", yaxis_title="Candidates")
        fig_comparison.update_xaxes(tickangle=45)
        
        return html.Div([
            html.Hr(style={'margin': '2rem 0'}),
            
            html.Div([
                html.I(className="fas fa-check-circle me-2"),
                html.Strong("Custom Comparison Complete! "),
                html.Span(f"Showing {len(comparison_results)} custom funnel comparisons with your selected filters.", 
                         style={'fontSize': '0.875rem'})
            ], style={'padding': '1rem', 'background': '#d4edda', 'borderRadius': '12px', 'border': '1px solid #c3e6cb', 'marginBottom': '2rem', 'color': '#155724'}),
            
            # Individual funnels
            html.H4([
                html.I(className="fas fa-chart-area me-2"),
                "Individual Funnels"
            ], style={'marginBottom': '1.5rem', 'color': '#1f2937'}),
            
            html.Div(funnel_charts, style={'marginBottom': '2rem'}),
            
            # Side-by-side comparison
            html.H4([
                html.I(className="fas fa-chart-line me-2"),
                "Side-by-Side Comparison"
            ], style={'marginBottom': '1.5rem', 'color': '#1f2937'}),
            
            dcc.Graph(figure=fig_comparison, config={'displayModeBar': False})
        ])
        
    except Exception as e:
        error_msg = f"Error processing comparisons: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        
        return html.Div([
            html.I(className="fas fa-exclamation-circle", style={'fontSize': '3rem', 'color': '#ef4444', 'marginBottom': '1rem'}),
            html.H4("Processing Error", style={'color': '#b91c1c', 'marginBottom': '0.5rem'}),
            html.P(f"Error details: {error_msg}", style={'color': '#6b7280'})
        ], style={'textAlign': 'center', 'padding': '3rem', 'background': '#fef2f2', 'borderRadius': '16px', 'border': '1px solid #fecaca'})
# Also add the updated chart functions with ALL 7 STAGES:
def create_funnel_comparison_chart(comparison_results):
    """Create a comparison chart for multiple funnels with ALL 7 stages"""
    fig = go.Figure()
    
    colors = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b', '#06b6d4']
    
    # Define the complete stage order - SAME AS OVERVIEW TAB
    complete_stage_order = ['Applied', 'Received Test', 'Did Test', 'Passed Test', 'Booked Interview', 'Passed Interview', 'Hired']
    
    for i, (name, result) in enumerate(comparison_results.items()):
        funnel_data = result['funnel_data']
        color = colors[i % len(colors)]
        
        # Ensure all stages are present with the correct order
        ordered_values = []
        for stage in complete_stage_order:
            ordered_values.append(funnel_data.get(stage, 0))
        
        fig.add_trace(go.Scatter(
            x=complete_stage_order,  # Use complete stage order
            y=ordered_values,        # Use ordered values
            mode='lines+markers+text',
            name=name,
            line=dict(color=color, width=4),
            marker=dict(size=12, color=color, line=dict(width=2, color='white')),
            text=[f"{v:,}" for v in ordered_values],
            textposition="top center",
            textfont=dict(size=12, color=color, family='Inter'),
            hovertemplate=f'<b>{name}</b><br>' +
                         '<b>%{x}</b><br>' +
                         'Count: %{y:,}<extra></extra>'
        ))
    
    fig = create_enhanced_plotly_theme(fig, "Funnel Comparison - All 7 Stages")
    fig.update_layout(
        height=600,
        xaxis_title="Funnel Stages",
        yaxis_title="Candidates",
        hovermode='x unified'
    )
    fig.update_xaxes(tickangle=45)
    
    return fig

def create_conversion_comparison_chart(comparison_results):
    """Create a comparison chart for conversion rates with ALL conversion stages"""
    fig = go.Figure()
    
    colors = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#64748b', '#06b6d4']
    
    # Get all unique conversion stages
    all_conversions = set()
    for result in comparison_results.values():
        all_conversions.update(result['conversions'].keys())
    
    # Define the expected conversion order - INCLUDING "Did Test" stage
    expected_conversions = [
        'Applied → Received Test',
        'Received Test → Did Test',           # ← This is now included!
        'Did Test → Passed Test',
        'Passed Test → Booked Interview',
        'Booked Interview → Passed Interview',
        'Passed Interview → Hired'
    ]
    
    # Use only the conversions that exist in the data, in the correct order
    conversion_stages = [conv for conv in expected_conversions if conv in all_conversions]
    
    for i, (name, result) in enumerate(comparison_results.items()):
        conversions = result['conversions']
        color = colors[i % len(colors)]
        
        y_values = [conversions.get(stage, 0) for stage in conversion_stages]
        
        fig.add_trace(go.Bar(
            x=conversion_stages,
            y=y_values,
            name=name,
            marker_color=color,
            text=[f"{v:.1f}%" for v in y_values],
            textposition='outside',
            textfont=dict(size=11),
            hovertemplate=f'<b>{name}</b><br>' +
                         '<b>%{x}</b><br>' +
                         'Conversion Rate: %{y:.1f}%<extra></extra>'
        ))
    
    fig = create_enhanced_plotly_theme(fig, "Conversion Rate Comparison - All Stages")
    fig.update_layout(
        height=500,
        xaxis_title="Conversion Stages",
        yaxis_title="Conversion Rate (%)",
        barmode='group'
    )
    fig.update_xaxes(tickangle=45)
    
    return fig
# Individual date range callbacks - SAFE IMPLEMENTATION
@app.callback(
    [Output('comparison-date-values-0', 'options'),
     Output('comparison-date-dropdown-0', 'style'),
     Output('comparison-custom-date-0', 'style')],
    [Input('comparison-date-type-0', 'value')],
    [State('date-options', 'data')],
    prevent_initial_call=True
)
def update_comparison_date_options_0(date_type, date_options):
    if not date_options or not date_type:
        return [], {'display': 'block'}, {'display': 'none'}
    
    if date_type == 'custom':
        return [], {'display': 'none'}, {'display': 'block'}
    else:
        options = date_options.get(date_type, [])
        return options, {'display': 'block'}, {'display': 'none'}

@app.callback(
    [Output('comparison-date-values-1', 'options'),
     Output('comparison-date-dropdown-1', 'style'),
     Output('comparison-custom-date-1', 'style')],
    [Input('comparison-date-type-1', 'value')],
    [State('date-options', 'data')],
    prevent_initial_call=True
)
def update_comparison_date_options_1(date_type, date_options):
    if not date_options or not date_type:
        return [], {'display': 'block'}, {'display': 'none'}
    
    if date_type == 'custom':
        return [], {'display': 'none'}, {'display': 'block'}
    else:
        options = date_options.get(date_type, [])
        return options, {'display': 'block'}, {'display': 'none'}

@app.callback(
    [Output('comparison-date-values-2', 'options'),
     Output('comparison-date-dropdown-2', 'style'),
     Output('comparison-custom-date-2', 'style')],
    [Input('comparison-date-type-2', 'value')],
    [State('date-options', 'data')],
    prevent_initial_call=True
)
def update_comparison_date_options_2(date_type, date_options):
    if not date_options or not date_type:
        return [], {'display': 'block'}, {'display': 'none'}
    
    if date_type == 'custom':
        return [], {'display': 'none'}, {'display': 'block'}
    else:
        options = date_options.get(date_type, [])
        return options, {'display': 'block'}, {'display': 'none'}
# Modal callbacks
# Modal callbacks
# Modal callbacks with debugging
# Modal callback for stage buttons
@app.callback(
    [Output('stage-modal', 'style'),
     Output('modal-title', 'children'),
     Output('modal-subtitle', 'children'),
     Output('modal-stats', 'children'),
     Output('modal-candidates-list', 'children')],
    [Input('btn-Applied', 'n_clicks'),
     Input('btn-ReceivedTest', 'n_clicks'),
     Input('btn-DidTest', 'n_clicks'),
     Input('btn-PassedTest', 'n_clicks'),
     Input('btn-BookedInterview', 'n_clicks'),
     Input('btn-PassedInterview', 'n_clicks'),
     Input('btn-Hired', 'n_clicks'),
     Input('modal-close-btn', 'n_clicks')],
    [State('processed-data', 'data')],
    prevent_initial_call=True
)
def show_stage_modal(btn1, btn2, btn3, btn4, btn5, btn6, btn7, close_btn, processed_data):
    ctx = dash.callback_context
    
    if not ctx.triggered or not processed_data:
        return {'display': 'none'}, "", "", [], []
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Check if any button was actually clicked (not just created)
    button_clicks = [btn1, btn2, btn3, btn4, btn5, btn6, btn7]
    
    # If close button was clicked, hide modal
    if trigger == 'modal-close-btn':
        return {'display': 'none'}, "", "", [], []
    
    # Check if this is a real button click (not just initialization)
    trigger_value = ctx.triggered[0]['value']
    if trigger_value is None or trigger_value == 0:
        return {'display': 'none'}, "", "", [], []
    
    # Map button to stage
    stage_map = {
        'btn-Applied': 'Applied (Qualified)',
        'btn-ReceivedTest': 'Received Test',
        'btn-DidTest': 'Did Test',
        'btn-PassedTest': 'Passed Test',
        'btn-BookedInterview': 'Booked Interview',
        'btn-PassedInterview': 'Passed Interview',
        'btn-Hired': 'Hired'
    }
    
    stage_name = stage_map.get(trigger)
    if not stage_name:
        return {'display': 'none'}, "", "", [], []
    
    candidates_by_stage = processed_data.get('candidates_by_stage', {})
    candidates = candidates_by_stage.get(stage_name, [])
    
    if not candidates:
        return {'display': 'none'}, "", "", [], []
    
    # Stats
    stats = [
        html.Div([
            html.Div(f"{len(candidates):,}", className="modal-stat-value"),
            html.Div("Total Candidates", className="modal-stat-label")
        ], className="modal-stat-card")
    ]
    
    # Candidate list
    candidate_items = []
    for i, name in enumerate(candidates):
        candidate_items.append(
            html.Div([
                html.Span(f"#{i+1}", style={
                    'background': '#6366f1', 'color': 'white', 'borderRadius': '50%',
                    'width': '28px', 'height': '28px', 'display': 'inline-flex',
                    'alignItems': 'center', 'justifyContent': 'center',
                    'fontSize': '12px', 'marginRight': '12px'
                }),
                html.Span(name, style={'fontSize': '16px'})
            ], className="candidate-item", style={
                'display': 'flex', 'alignItems': 'center', 'padding': '12px',
                'margin': '8px 0', 'background': 'white', 'borderRadius': '8px',
                'border': '1px solid #e5e7eb'
            })
        )
    
    candidates_list = html.Div([
        html.H4(f"All {len(candidates)} Candidates in {stage_name}", 
                style={'marginBottom': '1rem', 'color': '#1f2937'}),
        html.Div(candidate_items, style={'maxHeight': '400px', 'overflowY': 'auto'})
    ])
    
    return (
        {'display': 'flex'},
        f"📊 {stage_name}",
        f"Complete list of candidates in this stage",
        stats,
        candidates_list
    )
@app.callback(
    [Output('stage-modal', 'style', allow_duplicate=True),
     Output('modal-title', 'children', allow_duplicate=True),
     Output('modal-subtitle', 'children', allow_duplicate=True),
     Output('modal-stats', 'children', allow_duplicate=True),
     Output('modal-candidates-list', 'children', allow_duplicate=True)],
    [Input('comp-btn-0-Applied', 'n_clicks'),
     Input('comp-btn-0-ReceivedTest', 'n_clicks'),
     Input('comp-btn-0-DidTest', 'n_clicks'),
     Input('comp-btn-0-PassedTest', 'n_clicks'),
     Input('comp-btn-0-BookedInterview', 'n_clicks'),
     Input('comp-btn-0-PassedInterview', 'n_clicks'),
     Input('comp-btn-0-Hired', 'n_clicks'),
     Input('comp-btn-1-Applied', 'n_clicks'),
     Input('comp-btn-1-ReceivedTest', 'n_clicks'),
     Input('comp-btn-1-DidTest', 'n_clicks'),
     Input('comp-btn-1-PassedTest', 'n_clicks'),
     Input('comp-btn-1-BookedInterview', 'n_clicks'),
     Input('comp-btn-1-PassedInterview', 'n_clicks'),
     Input('comp-btn-1-Hired', 'n_clicks'),
     Input('comp-btn-2-Applied', 'n_clicks'),
     Input('comp-btn-2-ReceivedTest', 'n_clicks'),
     Input('comp-btn-2-DidTest', 'n_clicks'),
     Input('comp-btn-2-PassedTest', 'n_clicks'),
     Input('comp-btn-2-BookedInterview', 'n_clicks'),
     Input('comp-btn-2-PassedInterview', 'n_clicks'),
     Input('comp-btn-2-Hired', 'n_clicks'),
     Input('comp-btn-3-Applied', 'n_clicks'),
     Input('comp-btn-3-ReceivedTest', 'n_clicks'),
     Input('comp-btn-3-DidTest', 'n_clicks'),
     Input('comp-btn-3-PassedTest', 'n_clicks'),
     Input('comp-btn-3-BookedInterview', 'n_clicks'),
     Input('comp-btn-3-PassedInterview', 'n_clicks'),
     Input('comp-btn-3-Hired', 'n_clicks')],
    [State('funnel-comparison-data', 'data')],  # Use the new comparison data store
    prevent_initial_call=True
)
def show_comparison_modal_fixed(*args):
    funnel_comparison_data = args[-1]  # Last argument is the State
    button_clicks = args[:-1]  # All other arguments are button clicks
    
    ctx = dash.callback_context
    if not ctx.triggered or not any(button_clicks) or not funnel_comparison_data:
        return {'display': 'none'}, "", "", [], []
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Check if this is a real button click (not just initialization)
    trigger_value = ctx.triggered[0]['value']
    if trigger_value is None or trigger_value == 0:
        return {'display': 'none'}, "", "", [], []
    
    # Extract comparison index and stage from button ID
    parts = trigger.split('-')
    if len(parts) < 4:
        return {'display': 'none'}, "", "", [], []
        
    comp_index = int(parts[2])
    stage_part = parts[3]
    
    # Map stage parts to full stage names
    stage_map = {
        'Applied': 'Applied (Qualified)',
        'ReceivedTest': 'Received Test',
        'DidTest': 'Did Test',
        'PassedTest': 'Passed Test',
        'BookedInterview': 'Booked Interview',
        'PassedInterview': 'Passed Interview',
        'Hired': 'Hired'
    }
    
    stage_name = stage_map.get(stage_part)
    if not stage_name:
        return {'display': 'none'}, "", "", [], []
    
    # *** FIXED: Get the correct comparison data ***
    if str(comp_index) not in funnel_comparison_data:
        return {'display': 'none'}, "", "", [], []
    
    comparison_data = funnel_comparison_data[str(comp_index)]
    candidates_by_stage = comparison_data.get('candidates_by_stage', {})
    candidates = candidates_by_stage.get(stage_name, [])
    
    if not candidates:
        return (
            {'display': 'flex'},
            f"📊 {stage_name}",
            f"No candidates found in this stage for {comparison_data.get('name', f'Comparison {comp_index + 1}')}",
            [html.Div([
                html.Div("0", className="modal-stat-value"),
                html.Div("Candidates", className="modal-stat-label")
            ], className="modal-stat-card")],
            [html.Div([
                html.I(className="fas fa-search", style={'fontSize': '3rem', 'color': '#6b7280', 'marginBottom': '1rem'}),
                html.H4("No candidates in this stage", style={'color': '#6b7280'}),
                html.P("This stage is empty for the selected comparison filters", style={'color': '#9ca3af'})
            ], className="no-candidates-message")]
        )
    
    # Create enhanced candidate list with more details
    candidate_items = []
    for i, candidate in enumerate(candidates):
        candidate_name = candidate.get('candidate_name', f'Candidate {i+1}')
        candidate_age = candidate.get('calculated_age', 'N/A')
        candidate_status = candidate.get('primary_status', 'Unknown')
        job_titles = candidate.get('all_posting_titles', 'N/A')
        
        # Determine status color
        status_color = '#10b981' if candidate_status == 'Hired' else '#6366f1' if candidate_status != 'Unqualified' else '#ef4444'
        
        candidate_items.append(
            html.Div([
                html.Div([
                    html.Span(f"#{i+1}", style={
                        'background': '#6366f1', 'color': 'white', 'borderRadius': '50%',
                        'width': '32px', 'height': '32px', 'display': 'inline-flex',
                        'alignItems': 'center', 'justifyContent': 'center',
                        'fontSize': '14px', 'fontWeight': '600', 'marginRight': '12px'
                    }),
                    html.Div([
                        html.H6(candidate_name, style={
                            'margin': '0 0 4px 0', 'fontSize': '16px', 
                            'fontWeight': '600', 'color': '#1f2937'
                        }),
                        html.Div([
                            html.Span(f"Age: {candidate_age}", className="candidate-tag"),
                            html.Span(candidate_status, className=f"candidate-tag {candidate_status.lower()}"),
                        ], className="candidate-details"),
                        html.Small(f"Applied for: {job_titles[:50]}{'...' if len(str(job_titles)) > 50 else ''}", 
                                 style={'color': '#6b7280', 'fontSize': '12px'})
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'alignItems': 'flex-start'})
            ], className="candidate-item")
        )
    
    candidates_list = html.Div([
        html.H4(f"All {len(candidates)} Candidates in {stage_name}", 
                style={'marginBottom': '0.5rem', 'color': '#1f2937'}),
        html.P([
            f"From: ",
            html.Strong(comparison_data.get('name', f'Comparison {comp_index + 1}')),
            html.Br(),
            html.Small(comparison_data.get('filter_description', 'No filters applied'), 
                      style={'color': '#6b7280', 'fontStyle': 'italic'})
        ], style={'fontSize': '14px', 'color': '#4b5563', 'marginBottom': '1.5rem'}),
        html.Div(candidate_items, className="candidate-grid")
    ])
    
    # Enhanced stats
    stats = [
        html.Div([
            html.Div(f"{len(candidates):,}", className="modal-stat-value"),
            html.Div("Total Candidates", className="modal-stat-label")
        ], className="modal-stat-card"),
        
        html.Div([
            html.Div(f"{len([c for c in candidates if c.get('primary_status') == 'Hired']):,}", className="modal-stat-value"),
            html.Div("Hired", className="modal-stat-label")
        ], className="modal-stat-card"),
        
        html.Div([
            html.Div(f"{np.mean([c.get('calculated_age', 0) for c in candidates if c.get('calculated_age')]):.1f}", className="modal-stat-value"),
            html.Div("Avg Age", className="modal-stat-label")
        ], className="modal-stat-card") if any(c.get('calculated_age') for c in candidates) else html.Div()
    ]
    
    return (
        {'display': 'flex'},
        f"📊 {stage_name}",
        f"Detailed breakdown for {comparison_data.get('name', f'Comparison {comp_index + 1}')}",
        stats,
        candidates_list
    )
@app.callback(
    [Output('stage-modal', 'style', allow_duplicate=True),
     Output('modal-title', 'children', allow_duplicate=True),
     Output('modal-subtitle', 'children', allow_duplicate=True),
     Output('modal-stats', 'children', allow_duplicate=True),
     Output('modal-candidates-list', 'children', allow_duplicate=True)],
    [Input({'type': 'comp-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State('comparison-candidates-data', 'data')],
    prevent_initial_call=True
)
def show_comparison_stage_modal(button_clicks, comparison_candidates_data):
    print(f"\n🔍 MODAL DEBUG: Callback triggered")
    print(f"🔍 MODAL DEBUG: Button clicks: {button_clicks}")
    print(f"🔍 MODAL DEBUG: Candidates data: {comparison_candidates_data}")
    
    ctx = dash.callback_context
    
    if not ctx.triggered or not any(button_clicks) or not comparison_candidates_data:
        print("🔍 MODAL DEBUG: Early exit - no trigger, clicks, or data")
        return {'display': 'none'}, "", "", [], []
    
    # Get the triggered button info
    triggered_button = ctx.triggered[0]
    button_id = triggered_button['prop_id'].split('.')[0]
    
    print(f"🔍 MODAL DEBUG: Button ID: {button_id}")
    print(f"🔍 MODAL DEBUG: Button value: {triggered_button['value']}")
    
    # Check if this is a real button click
    if triggered_button['value'] is None or triggered_button['value'] == 0:
        print("🔍 MODAL DEBUG: Not a real click")
        return {'display': 'none'}, "", "", [], []
    
    try:
        # Parse the button ID
        button_info = eval(button_id)
        full_id = button_info['index']
        
        print(f"🔍 MODAL DEBUG: Full ID: {full_id}")
        
        # Extract comparison index and stage
        parts = full_id.split('-')
        comparison_index = parts[2]  # Keep as string!
        stage_part = parts[3]
        
        print(f"🔍 MODAL DEBUG: Comparison index (string): '{comparison_index}'")
        print(f"🔍 MODAL DEBUG: Stage part: '{stage_part}'")
        
        # Map stage parts to full stage names
        stage_map = {
            'Applied': 'Applied (Qualified)',
            'ReceivedTest': 'Received Test',
            'DidTest': 'Did Test',
            'PassedTest': 'Passed Test',
            'BookedInterview': 'Booked Interview',
            'PassedInterview': 'Passed Interview',
            'Hired': 'Hired'
        }
        
        stage_name = stage_map.get(stage_part)
        print(f"🔍 MODAL DEBUG: Mapped stage name: '{stage_name}'")
        
        if not stage_name:
            print("🔍 MODAL DEBUG: Invalid stage name")
            return {'display': 'none'}, "", "", [], []
        
        # Get the candidates for this specific comparison and stage
        print(f"🔍 MODAL DEBUG: Available comparison keys: {list(comparison_candidates_data.keys())}")
        
        comparison_candidates = comparison_candidates_data.get(comparison_index, {})
        print(f"🔍 MODAL DEBUG: Comparison candidates keys: {list(comparison_candidates.keys())}")
        
        candidates = comparison_candidates.get(stage_name, [])
        print(f"🔍 MODAL DEBUG: Found {len(candidates)} candidates")
        
        if len(candidates) > 0:
            print(f"🔍 MODAL DEBUG: Sample candidates: {candidates[:3]}")
        
        # Create candidate list
        if not candidates:
            candidates_list = html.Div([
                html.Div([
                    html.I(className="fas fa-search", style={'fontSize': '3rem', 'color': '#6b7280', 'marginBottom': '1rem'}),
                    html.H4("No candidates found", style={'color': '#6b7280', 'marginBottom': '0.5rem'}),
                    html.P(f"No candidates reached {stage_name} stage in this comparison", style={'color': '#9ca3af'}),
                    html.Hr(),
                    html.H6("🐛 Debug Info:", style={'color': '#ef4444', 'marginTop': '2rem'}),
                    html.P(f"Comparison index: '{comparison_index}'", style={'fontSize': '12px', 'color': '#6b7280'}),
                    html.P(f"Stage name: '{stage_name}'", style={'fontSize': '12px', 'color': '#6b7280'}),
                    html.P(f"Available comparisons: {list(comparison_candidates_data.keys())}", style={'fontSize': '12px', 'color': '#6b7280'}),
                    html.P(f"Available stages in this comparison: {list(comparison_candidates.keys())}", style={'fontSize': '12px', 'color': '#6b7280'}),
                ], style={'textAlign': 'center', 'padding': '3rem'})
            ])
        else:
            # SUCCESS! Create candidate list
            candidate_items = []
            for i, name in enumerate(candidates):
                candidate_items.append(
                    html.Div([
                        html.Span(f"#{i+1}", style={
                            'background': '#10b981', 'color': 'white', 'borderRadius': '50%',
                            'width': '30px', 'height': '30px', 'display': 'inline-flex',
                            'alignItems': 'center', 'justifyContent': 'center',
                            'fontSize': '12px', 'marginRight': '12px', 'fontWeight': 'bold'
                        }),
                        html.Span(name, style={'fontSize': '16px', 'fontWeight': '500'})
                    ], style={
                        'display': 'flex', 'alignItems': 'center', 'padding': '14px',
                        'margin': '6px 0', 'background': '#f0fdf4', 'borderRadius': '12px',
                        'border': '1px solid #bbf7d0', 'transition': 'all 0.2s ease'
                    })
                )
            
            candidates_list = html.Div([
                html.H4([
                    html.I(className="fas fa-users", style={'marginRight': '8px', 'color': '#10b981'}),
                    f"Found {len(candidates)} Candidates in {stage_name}"
                ], style={'marginBottom': '1.5rem', 'color': '#059669', 'fontSize': '1.5rem'}),
                html.Div(candidate_items, style={'maxHeight': '400px', 'overflowY': 'auto'})
            ])
        
        # Stats
        stats = [
            html.Div([
                html.Div(f"{len(candidates):,}", style={
                    'fontSize': '3rem', 'fontWeight': '800', 'color': '#10b981',
                    'lineHeight': '1', 'marginBottom': '0.5rem'
                }),
                html.Div("Total Candidates", style={
                    'fontSize': '0.875rem', 'color': '#6b7280', 'textTransform': 'uppercase',
                    'letterSpacing': '0.05em', 'fontWeight': '500'
                })
            ], style={
                'textAlign': 'center', 'padding': '2rem', 'background': '#f0fdf4',
                'borderRadius': '16px', 'border': '1px solid #bbf7d0'
            })
        ]
        
        return (
            {'display': 'flex'},
            f"📊 {stage_name}",
            f"Candidates from Comparison {int(comparison_index) + 1}",
            stats,
            candidates_list
        )
        
    except Exception as e:
        print(f"🔍 MODAL DEBUG ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        error_info = html.Div([
            html.H4("🐛 Debug Error", style={'color': '#ef4444'}),
            html.P(f"Error: {str(e)}", style={'color': '#6b7280'}),
            html.P(f"Button ID: {button_id}", style={'fontSize': '12px', 'color': '#6b7280'}),
            html.Hr(),
            html.P("Raw candidates data:", style={'fontWeight': 'bold'}),
            html.Pre(str(comparison_candidates_data)[:500] + "...", style={
                'fontSize': '10px', 'background': '#f5f5f5', 'padding': '1rem',
                'borderRadius': '8px', 'overflow': 'auto', 'maxHeight': '200px'
            })
        ], style={'padding': '2rem'})
        
        return (
            {'display': 'flex'},
            "🐛 Debug Error",
            "Error in modal callback",
            [],
            error_info
        )    
if __name__ == '__main__':
  app.run(debug=True, port=8052)


