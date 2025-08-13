import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
APP_NAME = "Patient Records System"
DATABASE_FILE = "patients.db"

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            docket_number TEXT,
            modality TEXT,
            procedure TEXT,
            phone_number TEXT,
            dob TEXT,
            coming_from TEXT,
            health_card TEXT,
            clinic_appointment TEXT,
            scheduled_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# In a real-world scenario, this would be in a separate .html file
# and the CSS/JS in their own asset files.
INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{{ app_name }}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<style>
  /* Hospital-Grade Design System */
  :root {
    --primary-color: #0066CC; /* Hospital Calming Blue */
    --primary-hover: #0052A3;
    --primary-light: #E3F2FD;
    --secondary-color: #28A745; /* Medical Green */
    --secondary-hover: #218838;
    --secondary-light: #E8F5E8;
    --accent-color: #17A2B8; /* Medical Teal */
    --warning-color: #FFC107;
    --danger-color: #DC3545;
    --success-color: #28A745;
    --background-color: #F8FAFE; /* Softer Medical Blue-tinted Gray */
    --card-background: #FFFFFF;
    --text-primary: #1A202C;
    --text-secondary: #4A5568;
    --text-muted: #718096;
    --border-color: #E2E8F0;
    --border-light: #F1F5F9;
    --shadow-light: 0 1px 3px 0 rgba(0, 102, 204, 0.06);
    --shadow-medium: 0 4px 6px -1px rgba(0, 102, 204, 0.08);
    --shadow-large: 0 10px 25px -3px rgba(0, 102, 204, 0.1);
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;
    --border-radius-sm: 6px;
    --border-radius-md: 8px;
    --border-radius-lg: 12px;
    --transition-fast: 0.15s ease-in-out;
    --transition-normal: 0.2s ease-in-out;
    --transition-slow: 0.3s ease-in-out;
  }
  body {
    font-family: 'Inter', sans-serif;
    background-color: var(--background-color);
    color: var(--text-primary);
    line-height: 1.6;
    letter-spacing: -0.01em;
  }
  
  /* Enhanced Card Styles */
  .card {
    background-color: var(--card-background);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-medium);
    transition: var(--transition-normal);
  }
  
  .card:hover {
    box-shadow: var(--shadow-large);
    transform: translateY(-1px);
  }
  
  /* Medical-themed Statistics Cards */
  .stat-card {
    background: linear-gradient(135deg, var(--card-background) 0%, #FAFBFF 100%);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-medium);
    padding: var(--spacing-lg);
    position: relative;
    overflow: hidden;
    transition: var(--transition-normal);
  }
  
  .stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  }
  
  .stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-large);
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: var(--border-radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: var(--spacing-md);
  }
  
  .stat-icon.primary {
    background-color: var(--primary-light);
    color: var(--primary-color);
  }
  
  .stat-icon.secondary {
    background-color: var(--secondary-light);
    color: var(--secondary-color);
  }
  
  .stat-icon.accent {
    background-color: #E0F7FA;
    color: var(--accent-color);
  }
  .table-responsive-wrapper {
    overflow-x: auto;
  }
  /* Enhanced Navigation */
  .navbar {
    background: linear-gradient(135deg, var(--card-background) 0%, #FAFBFF 100%);
    border-bottom: 1px solid var(--border-light);
    box-shadow: var(--shadow-light);
    backdrop-filter: blur(10px);
  }
  
  .navbar-brand {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-weight: 700;
    font-size: 1.25rem;
    color: var(--text-primary);
  }
  
  .navbar-icon {
    width: 32px;
    height: 32px;
    color: var(--primary-color);
  }
  
  /* Enhanced Button Styles */
  .button-primary {
    background: linear-gradient(135deg, var(--primary-color) 0%, #0052A3 100%);
    color: white;
    font-weight: 600;
    padding: var(--spacing-sm) var(--spacing-lg);
    border-radius: var(--border-radius-md);
    border: none;
    transition: var(--transition-normal);
    box-shadow: var(--shadow-light);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
  }
  
  .button-primary:hover { 
    background: linear-gradient(135deg, var(--primary-hover) 0%, #003d7a 100%);
    box-shadow: var(--shadow-medium);
    transform: translateY(-1px);
  }
  
  .button-primary:active {
    transform: translateY(0);
  }
  
  .button-secondary {
    background-color: var(--card-background);
    color: var(--text-secondary);
    border: 2px solid var(--border-color);
    font-weight: 500;
    padding: var(--spacing-sm) var(--spacing-lg);
    border-radius: var(--border-radius-md);
    transition: var(--transition-normal);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
  }
  
  .button-secondary:hover { 
    background-color: var(--primary-light);
    border-color: var(--primary-color);
    color: var(--primary-color);
    box-shadow: var(--shadow-light);
  }
  /* Enhanced Form Inputs */
  .form-input {
    width: 100%;
    border: 2px solid var(--border-color);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-sm) var(--spacing-md);
    transition: var(--transition-normal);
    background-color: var(--card-background);
    font-size: 0.95rem;
    line-height: 1.5;
  }
  
  .form-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
    background-color: #FAFBFF;
  }
  
  .form-input:hover:not(:focus) {
    border-color: var(--text-muted);
  }
  
  /* Form Group Enhancement */
  .form-group {
    margin-bottom: var(--spacing-lg);
  }
  
  .form-label {
    display: block;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--spacing-xs);
    font-size: 0.9rem;
  }
  
  .form-label.required::after {
    content: '*';
    color: var(--danger-color);
    margin-left: var(--spacing-xs);
  }
  
  /* Progress Indicator */
  .progress-bar {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--spacing-xl);
    position: relative;
  }
  
  .progress-bar::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 2px;
    background-color: var(--border-color);
    z-index: 1;
  }
  
  .progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    z-index: 2;
    background-color: var(--background-color);
    padding: 0 var(--spacing-sm);
  }
  
  .progress-step-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: var(--border-color);
    color: var(--text-muted);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.875rem;
    margin-bottom: var(--spacing-xs);
    transition: var(--transition-normal);
  }
  
  .progress-step.active .progress-step-number {
    background-color: var(--primary-color);
    color: white;
  }
  
  .progress-step.completed .progress-step-number {
    background-color: var(--secondary-color);
    color: white;
  }
  
  .progress-step-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-muted);
    text-align: center;
  }
  
  .progress-step.active .progress-step-label {
    color: var(--primary-color);
    font-weight: 600;
  }
  /* Enhanced Table Styles */
  .table-header {
    background: linear-gradient(135deg, #F8FAFE 0%, #F1F5F9 100%);
    color: var(--text-primary);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.75rem;
    cursor: pointer;
    border-bottom: 2px solid var(--primary-color);
    transition: var(--transition-normal);
  }
  
  .table-header:hover {
    background: linear-gradient(135deg, var(--primary-light) 0%, #E3F2FD 100%);
    color: var(--primary-color);
  }
  
  .table-header .sort-icon {
    opacity: 0.4;
    transition: var(--transition-normal);
    margin-left: var(--spacing-xs);
  }
  
  .table-header:hover .sort-icon { 
    opacity: 1; 
    color: var(--primary-color);
  }
  
  .table-row {
    border-bottom: 1px solid var(--border-light);
    transition: var(--transition-fast);
  }
  
  .table-row:hover {
    background-color: var(--primary-light);
    transform: scale(1.001);
  }
  
  .table-row:nth-child(even) {
    background-color: #FAFBFF;
  }
  
  .table-row:nth-child(even):hover {
    background-color: var(--primary-light);
  }
  
  /* Action Buttons in Tables */
  .action-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: var(--border-radius-sm);
    border: none;
    cursor: pointer;
    transition: var(--transition-fast);
    margin-right: var(--spacing-xs);
  }
  
  .action-button.edit {
    background-color: #E3F2FD;
    color: var(--primary-color);
  }
  
  .action-button.edit:hover {
    background-color: var(--primary-color);
    color: white;
    transform: scale(1.1);
  }
  
  .action-button.delete {
    background-color: #FFEBEE;
    color: var(--danger-color);
  }
  
  .action-button.delete:hover {
    background-color: var(--danger-color);
    color: white;
    transform: scale(1.1);
  }

  /* Responsive Table styling for mobile */
  @media (max-width: 768px) {
    .responsive-table thead { display: none; }
    .responsive-table tr {
        display: block;
        margin-bottom: var(--spacing-md);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-md);
        padding: var(--spacing-md);
        background: var(--card-background);
        box-shadow: var(--shadow-light);
    }
    .responsive-table td {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--spacing-xs) 0;
        border-bottom: 1px solid var(--border-light);
    }
    .responsive-table td:last-child { border-bottom: none; }
    .responsive-table td::before {
        content: attr(data-label);
        font-weight: 600;
        margin-right: var(--spacing-md);
        color: var(--text-primary);
        flex-shrink: 0;
        min-width: 100px;
    }
    
    .stat-card {
      margin-bottom: var(--spacing-md);
    }
    
    .modal-content {
      margin: var(--spacing-sm);
      max-height: 95vh;
    }
    
    .form-group {
      margin-bottom: var(--spacing-md);
    }
    
    .tab-navigation {
      padding: 0 var(--spacing-sm);
    }
    
    .navbar-brand span {
      font-size: 1.1rem;
    }
  }
  
  /* Focus and Accessibility Improvements */
  .form-input:focus,
  .button-primary:focus,
  .button-secondary:focus,
  .tab-btn:focus,
  .action-button:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
  }
  
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }
  
  /* High contrast mode support */
  @media (prefers-contrast: high) {
    :root {
      --border-color: #000000;
      --text-secondary: #000000;
    }
  }
  
  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
  
  /* Validation styles */
  .validation-message {
    margin-top: var(--spacing-xs);
    font-size: 0.875rem;
    color: var(--danger-color);
    display: none;
  }
  
  .form-input.error {
    border-color: var(--danger-color);
    box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
  }
  
  .form-input.error + .validation-message {
    display: block;
  }
  
  .form-input.success {
    border-color: var(--success-color);
    box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
  }
  /* Enhanced Modal Styles */
  .modal-overlay {
    position: fixed; 
    top: 0; 
    left: 0; 
    right: 0; 
    bottom: 0;
    background: rgba(26, 32, 44, 0.6);
    display: none; 
    align-items: center; 
    justify-content: center; 
    z-index: 1000;
    backdrop-filter: blur(8px);
    animation: fadeIn var(--transition-normal) ease-out;
  }
  
  .modal-content {
    background-color: var(--card-background);
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-large);
    width: 100%;
    max-width: 48rem;
    margin: var(--spacing-lg);
    max-height: 90vh;
    overflow-y: auto;
    animation: slideUp var(--transition-normal) ease-out;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  @keyframes slideUp {
    from { 
      opacity: 0;
      transform: translateY(20px) scale(0.95);
    }
    to { 
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }
  
  /* Tab Navigation Enhancement */
  .tab-navigation {
    border-bottom: 2px solid var(--border-light);
    background-color: var(--card-background);
    border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
    padding: 0 var(--spacing-lg);
  }
  
  .tab-btn {
    border: none;
    background: none;
    padding: var(--spacing-md) var(--spacing-lg);
    font-weight: 600;
    color: var(--text-muted);
    border-bottom: 3px solid transparent;
    transition: var(--transition-normal);
    cursor: pointer;
    font-size: 0.9rem;
  }
  
  .tab-btn:hover {
    color: var(--primary-color);
    background-color: var(--primary-light);
  }
  
  .tab-btn.active {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
    background-color: var(--primary-light);
  }
  
  /* Loading States */
  .loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-color);
    border-radius: 50%;
    border-top-color: var(--primary-color);
    animation: spin 1s ease-in-out infinite;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .skeleton {
    background: linear-gradient(90deg, var(--border-light) 25%, var(--border-color) 50%, var(--border-light) 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
  }
  
  @keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
  /* Form Wizard */
  .form-step { display: none; }
  .form-step.active { display: block; }
</style>
</head>
<body onload="initApp()">
  <div class="min-h-screen">
    <nav class="navbar sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="navbar-brand">
            <svg class="navbar-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <span>{{ app_name }}</span>
          </div>
          <div class="flex items-center space-x-4">
            <div class="text-sm text-gray-600">
              <span id="current-time"></span>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-4 sm:px-0">
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div class="stat-card">
            <div class="stat-icon primary">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
            <dt class="text-sm font-semibold text-gray-600 uppercase tracking-wide">Total Patients</dt>
            <dd class="mt-2 flex items-baseline">
              <span id="stat-total" class="text-3xl font-bold text-gray-900">0</span>
              <span class="ml-2 text-sm font-medium text-green-600">+12%</span>
            </dd>
            <p class="mt-1 text-sm text-gray-500">from last month</p>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon secondary">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.611L5 14.5" />
              </svg>
            </div>
            <dt class="text-sm font-semibold text-gray-600 uppercase tracking-wide">Active Modalities</dt>
            <dd class="mt-2 flex items-baseline">
              <span id="stat-modalities" class="text-3xl font-bold text-gray-900">0</span>
              <span class="ml-2 text-sm font-medium text-blue-600">4 types</span>
            </dd>
            <p class="mt-1 text-sm text-gray-500">imaging services</p>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon accent">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5m-9-6h2.25m-2.25 3h2.25m-3.75 3h3.75m-3.75-6h3.75" />
              </svg>
            </div>
            <dt class="text-sm font-semibold text-gray-600 uppercase tracking-wide">Upcoming Appointments</dt>
            <dd class="mt-2 flex items-baseline">
              <span id="stat-appointments" class="text-3xl font-bold text-gray-900">0</span>
              <span class="ml-2 text-sm font-medium text-orange-600">next 7 days</span>
            </dd>
            <p class="mt-1 text-sm text-gray-500">scheduled procedures</p>
          </div>
        </div>
      </div>
      
      <div class="mt-6">
          <div class="sm:hidden">
              <label for="tabs" class="sr-only">Select a tab</label>
              <select id="tabs" name="tabs" class="form-input" onchange="showTab(this.value)">
                  <option value="manage" selected>Add Patient</option>
                  <option value="patients">Patient List</option>
                  <option value="upcoming">Upcoming Appointments</option>
              </select>
          </div>
          <div class="hidden sm:block tab-navigation">
              <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                  <button class="tab-btn active" onclick="showTab('manage')">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                    </svg>
                    Add Patient
                  </button>
                  <button class="tab-btn" onclick="showTab('patients')">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h6a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                    </svg>
                    Patient List
                  </button>
                  <button class="tab-btn" onclick="showTab('upcoming')">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Upcoming Appointments
                  </button>
              </nav>
          </div>
      </div>
      
      <div class="mt-6">
        <div id="tab-manage" class="tab-content active">
          <div class="card p-6 lg:p-8">
            <!-- Progress Indicator -->
            <div class="progress-bar">
              <div class="progress-step active" id="progress-step-1">
                <div class="progress-step-number">1</div>
                <div class="progress-step-label">Patient Info</div>
              </div>
              <div class="progress-step" id="progress-step-2">
                <div class="progress-step-number">2</div>
                <div class="progress-step-label">Examination</div>
              </div>
              <div class="progress-step" id="progress-step-3">
                <div class="progress-step-number">3</div>
                <div class="progress-step-label">Scheduling</div>
              </div>
            </div>
            
            <form id="patientForm" onsubmit="handlePatientSubmit(event)">
              <div id="patient-form-step-1" class="form-step active">
                <div class="mb-8">
                  <h3 class="text-2xl font-bold text-gray-900 mb-2">Patient Information</h3>
                  <p class="text-gray-600">Enter the patient's personal and contact details.</p>
                </div>
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div class="form-group">
                      <label class="form-label required">Patient Name</label>
                      <input type="text" id="patient_name" class="form-input" required placeholder="Enter full name">
                      <div class="validation-message" id="patient_name_error"></div>
                    </div>
                    <div class="form-group">
                      <label class="form-label">Date of Birth</label>
                      <input type="date" id="dob" class="form-input">
                    </div>
                    <div class="form-group">
                      <label class="form-label">Phone Number</label>
                      <input type="tel" id="phone_number" class="form-input" placeholder="(000) 000-0000">
                    </div>
                    <div class="form-group">
                      <label class="form-label">Docket Number</label>
                      <input type="text" id="docket_number" class="form-input" placeholder="Auto-generated if left blank">
                    </div>
                </div>
                <div class="mt-8 flex justify-end">
                    <button type="button" class="button-primary" onclick="navigateFormStep(2)">
                      Next Step
                      <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                      </svg>
                    </button>
                </div>
              </div>

              <div id="patient-form-step-2" class="form-step">
                <div class="mb-8">
                  <h3 class="text-2xl font-bold text-gray-900 mb-2">Examination Details</h3>
                  <p class="text-gray-600">Provide information about the medical examination and imaging requirements.</p>
                </div>
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div class="form-group">
                      <label class="form-label">Medical Imaging Modality</label>
                      <select id="modality" class="form-input">
                        <option value="">Select imaging type...</option>
                        <option value="US">Ultrasound (US)</option>
                        <option value="CT">Computed Tomography (CT)</option>
                        <option value="DX/CR">Digital X-Ray (DX/CR)</option>
                        <option value="MAMMO">Mammography (MAMMO)</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label class="form-label">Procedure/Examination</label>
                      <input type="text" id="procedure" class="form-input" placeholder="e.g., Chest X-Ray, Abdominal US">
                    </div>
                    <div class="form-group">
                      <label class="form-label">Referring Source</label>
                      <input type="text" id="coming_from" class="form-input" placeholder="Doctor, clinic, or department">
                    </div>
                    <div class="form-group">
                      <label class="form-label">Insurance Provider</label>
                      <select id="health_card" class="form-input">
                        <option value="">Select insurance...</option>
                        <option value="Sagicor">Sagicor Health Insurance</option>
                        <option value="Canopy">Canopy Insurance</option>
                        <option value="Guardian Life">Guardian Life Insurance</option>
                        <option value="Other">Other Provider</option>
                      </select>
                    </div>
                </div>
                <div class="mt-8 flex justify-between">
                    <button type="button" class="button-secondary" onclick="navigateFormStep(1)">
                      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                      </svg>
                      Back
                    </button>
                    <button type="button" class="button-primary" onclick="navigateFormStep(3)">
                      Next Step
                      <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                      </svg>
                    </button>
                </div>
              </div>

              <div id="patient-form-step-3" class="form-step">
                <div class="mb-8">
                  <h3 class="text-2xl font-bold text-gray-900 mb-2">Appointment Scheduling</h3>
                  <p class="text-gray-600">Set dates and times for the procedure and follow-up appointments.</p>
                </div>
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div class="form-group">
                      <label class="form-label">Scheduled Procedure Date</label>
                      <input type="date" id="scheduled_date" class="form-input">
                    </div>
                    <div class="form-group">
                      <label class="form-label">Clinic Appointment</label>
                      <input type="datetime-local" id="clinic_appointment" class="form-input">
                    </div>
                </div>
                <div class="mt-8 flex justify-between items-center">
                    <button type="button" class="button-secondary" onclick="navigateFormStep(2)">
                      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                      </svg>
                      Back
                    </button>
                    <div class="flex items-center space-x-4">
                        <div id="patientStatus" class="text-sm font-medium"></div>
                        <button type="submit" class="button-primary">
                          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                          </svg>
                          Add Patient Record
                        </button>
                    </div>
                </div>
              </div>
            </form>
          </div>
        </div>

        <div id="tab-patients" class="tab-content">
          <div class="card">
            <div class="p-6 border-b border-gray-200">
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div class="relative flex-1 max-w-md">
                        <div class="pointer-events-none absolute inset-y-0 left-0 pl-3 flex items-center">
                            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                              <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <input type="search" id="patientSearch" class="form-input pl-10" placeholder="Search patients by name or docket number...">
                    </div>
                    <div class="flex items-center space-x-4">
                        <div id="patient-pagination-controls" class="flex items-center space-x-2 text-sm"></div>
                        <button class="button-secondary" onclick="exportPatientData()">
                          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                          </svg>
                          Export
                        </button>
                    </div>
                </div>
            </div>
            <div class="table-responsive-wrapper">
                <table class="min-w-full responsive-table">
                    <thead class="table-header">
                        <tr>
                            <th class="p-4 text-left font-semibold" onclick="sortPatients('patient_name')">
                              <div class="flex items-center cursor-pointer hover:text-blue-600">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                                </svg>
                                Patient Name 
                                <span class="sort-icon ml-1">↕</span>
                              </div>
                            </th>
                            <th class="p-4 text-left font-semibold" onclick="sortPatients('docket_number')">
                              <div class="flex items-center cursor-pointer hover:text-blue-600">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                                Docket # 
                                <span class="sort-icon ml-1">↕</span>
                              </div>
                            </th>
                            <th class="p-4 text-left font-semibold">
                              <div class="flex items-center">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
                                </svg>
                                Modality
                              </div>
                            </th>
                            <th class="p-4 text-left font-semibold">
                              <div class="flex items-center">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h6a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                                </svg>
                                Procedure
                              </div>
                            </th>
                            <th class="p-4 text-left font-semibold">
                              <div class="flex items-center">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                                </svg>
                                Phone
                              </div>
                            </th>
                            <th class="p-4 text-left font-semibold" onclick="sortPatients('dob')">
                              <div class="flex items-center cursor-pointer hover:text-blue-600">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                                Date of Birth 
                                <span class="sort-icon ml-1">↕</span>
                              </div>
                            </th>
                            <th class="p-4 text-left font-semibold" onclick="sortPatients('scheduled_date')">
                              <div class="flex items-center cursor-pointer hover:text-blue-600">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                Scheduled 
                                <span class="sort-icon ml-1">↕</span>
                              </div>
                            </th>
                            <th class="p-4 text-left font-semibold">
                              <div class="flex items-center">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                                </svg>
                                Actions
                              </div>
                            </th>
                        </tr>
                    </thead>
                    <tbody id="patientTbody" class="divide-y divide-gray-100 bg-white"></tbody>
                </table>
            </div>
          </div>
        </div>

        <div id="tab-upcoming" class="tab-content">
          <div class="card">
              <div class="table-responsive-wrapper">
                  <table class="min-w-full responsive-table">
                      <thead class="table-header">
                          <tr>
                              <th class="p-3 text-left">Name</th>
                              <th class="p-3 text-left">Modality</th>
                              <th class="p-3 text-left">Appointment Time</th>
                              <th class="p-3 text-left">Phone</th>
                              <th class="p-3 text-left">Actions</th>
                          </tr>
                      </thead>
                      <tbody id="upcomingTbody" class="divide-y divide-gray-200 bg-white"></tbody>
                  </table>
              </div>
          </div>
        </div>
      </div>
    </main>
  </div>

  <div id="editModal" class="modal-overlay" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="modal-content">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 id="modal-title" class="text-2xl font-bold text-gray-900 flex items-center">
            <svg class="w-6 h-6 mr-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Edit Patient Record
          </h2>
          <button type="button" class="text-gray-400 hover:text-gray-600 transition-colors" onclick="closeEditModal()">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>
      <div class="p-6">
        <form id="editPatientForm" onsubmit="handleUpdateSubmit(event)">
          <input type="hidden" id="edit_patient_id">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div class="form-group">
              <label class="form-label required">Patient Name</label>
              <input type="text" id="edit_patient_name" class="form-input" required>
            </div>
            <div class="form-group">
              <label class="form-label">Docket Number</label>
              <input type="text" id="edit_docket_number" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">Medical Imaging Modality</label>
              <select id="edit_modality" class="form-input">
                <option value="">Select imaging type...</option>
                <option value="US">Ultrasound (US)</option>
                <option value="CT">Computed Tomography (CT)</option>
                <option value="DX/CR">Digital X-Ray (DX/CR)</option>
                <option value="MAMMO">Mammography (MAMMO)</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Procedure/Examination</label>
              <input type="text" id="edit_procedure" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">Phone Number</label>
              <input type="tel" id="edit_phone_number" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">Date of Birth</label>
              <input type="date" id="edit_dob" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">Referring Source</label>
              <input type="text" id="edit_coming_from" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">Insurance Provider</label>
              <select id="edit_health_card" class="form-input">
                <option value="">Select insurance...</option>
                <option value="Sagicor">Sagicor Health Insurance</option>
                <option value="Canopy">Canopy Insurance</option>
                <option value="Guardian Life">Guardian Life Insurance</option>
                <option value="Other">Other Provider</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Scheduled Procedure Date</label>
              <input type="date" id="edit_scheduled_date" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">Clinic Appointment</label>
              <input type="datetime-local" id="edit_clinic_appointment" class="form-input">
            </div>
          </div>
          <div class="mt-8 flex justify-end items-center space-x-4 pt-4 border-t border-gray-200">
            <div id="editStatus" class="text-sm font-medium"></div>
            <button type="button" class="button-secondary" onclick="closeEditModal()">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
              Cancel
            </button>
            <button type="submit" class="button-primary">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              Update Patient
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

<script>
const patientFormFields = ['patient_name', 'docket_number', 'modality', 'procedure', 'phone_number', 'dob', 'coming_from', 'health_card', 'clinic_appointment', 'scheduled_date'];
let allPatients = [];
let filteredPatients = [];
let currentSort = { column: 'patient_name', direction: 'asc' };
let currentPage = 1;
const rowsPerPage = 10;

function initApp() {
    // Setup tab buttons for larger screens
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
    
    // Setup search listener with debounce
    let searchTimeout;
    document.getElementById('patientSearch').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            filterAndRenderPatients(e.target.value);
        }, 300);
    });

    // Initialize clock
    updateClock();
    setInterval(updateClock, 1000);

    loadAllData();
}

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    const dateString = now.toLocaleDateString([], {weekday: 'short', month: 'short', day: 'numeric'});
    document.getElementById('current-time').textContent = `${dateString} ${timeString}`;
}

function showTab(tab) {
  document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
  document.getElementById(`tab-${tab}`).classList.add('active');
  
  // Sync dropdown for mobile
  const select = document.getElementById('tabs');
  if (select.value !== tab) {
      select.value = tab;
  }
  
  // Update button styles for desktop
  const targetBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(`'${tab}'`));
  if(targetBtn){
      document.querySelectorAll('.tab-btn').forEach(b => {
          b.classList.remove('border-blue-600', 'text-blue-600');
          b.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
      });
      targetBtn.classList.add('border-blue-600', 'text-blue-600');
      targetBtn.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
  }
}

async function loadAllData() {
    await Promise.all([loadStats(), loadPatients(), loadUpcomingAppointments()]);
}

async function loadPatients() {
  try {
    const resp = await fetch('/api/patients');
    allPatients = await resp.json();
    sortPatients(currentSort.column, true); // Initial sort
  } catch(e) { 
    console.error("Failed to load patients", e);
    document.getElementById('patientTbody').innerHTML = '<tr><td data-label="Error" colspan="8" class="p-4 text-center text-red-500">Could not load patients.</td></tr>'; 
  }
}

function filterAndRenderPatients(searchTerm = '') {
    const lowerCaseSearch = searchTerm.toLowerCase();
    filteredPatients = allPatients.filter(p => {
        return (p.patient_name && p.patient_name.toLowerCase().includes(lowerCaseSearch)) ||
               (p.docket_number && p.docket_number.toLowerCase().includes(lowerCaseSearch));
    });
    currentPage = 1;
    renderPatientTable();
}

function sortPatients(column, initial = false) {
    if (!initial && column === currentSort.column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.direction = 'asc';
    }
    
    filteredPatients.sort((a, b) => {
        let valA = a[column] || '';
        let valB = b[column] || '';
        if (currentSort.direction === 'asc') {
            return valA > valB ? 1 : -1;
        } else {
            return valA < valB ? 1 : -1;
        }
    });
    currentPage = 1;
    renderPatientTable();
}

function renderPatientTable() {
    const tbody = document.getElementById('patientTbody');
    tbody.innerHTML = "";
    if (!filteredPatients.length) {
      tbody.innerHTML = `<tr><td data-label="Status" class="p-6 text-center text-gray-500" colspan="8">
        <div class="flex flex-col items-center justify-center py-8">
          <svg class="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h6a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
          </svg>
          <p class="text-lg font-medium">No patients found</p>
          <p class="text-sm">Try adjusting your search criteria</p>
        </div>
      </td></tr>`;
      renderPaginationControls();
      return;
    }

    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedItems = filteredPatients.slice(start, end);

    paginatedItems.forEach(p => {
      const tr = document.createElement('tr');
      tr.className = "table-row";
      tr.innerHTML = `
        <td data-label="Name" class="p-4 whitespace-nowrap">
          <div class="flex items-center">
            <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
              <span class="text-sm font-medium text-blue-600">${escapeHtml(p.patient_name).charAt(0).toUpperCase()}</span>
            </div>
            <div>
              <div class="text-sm font-semibold text-gray-900">${escapeHtml(p.patient_name)}</div>
              <div class="text-xs text-gray-500">ID: ${p.id}</div>
            </div>
          </div>
        </td>
        <td data-label="Docket" class="p-4 whitespace-nowrap">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            ${escapeHtml(p.docket_number) || 'Not assigned'}
          </span>
        </td>
        <td data-label="Modality" class="p-4 whitespace-nowrap">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getModalityColor(p.modality)}">
            ${escapeHtml(p.modality) || 'Not specified'}
          </span>
        </td>
        <td data-label="Procedure" class="p-4 whitespace-nowrap text-sm text-gray-700">${escapeHtml(p.procedure) || '-'}</td>
        <td data-label="Phone" class="p-4 whitespace-nowrap text-sm text-gray-700">${escapeHtml(p.phone_number) || '-'}</td>
        <td data-label="DOB" class="p-4 whitespace-nowrap text-sm text-gray-700">${formatDate(p.dob)}</td>
        <td data-label="Scheduled" class="p-4 whitespace-nowrap text-sm text-gray-700">${formatDate(p.scheduled_date)}</td>
        <td data-label="Actions" class="p-4 text-sm font-medium">
          <div class="flex items-center space-x-2">
            <button class="action-button edit" onclick="openEditModal(${p.id})" title="Edit patient record">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </button>
            <button class="action-button delete" onclick="deletePatient(${p.id})" title="Delete patient record">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });
    renderPaginationControls();
}

function getModalityColor(modality) {
    const colors = {
        'US': 'bg-blue-100 text-blue-800',
        'CT': 'bg-green-100 text-green-800',
        'DX/CR': 'bg-yellow-100 text-yellow-800',
        'MAMMO': 'bg-purple-100 text-purple-800'
    };
    return colors[modality] || 'bg-gray-100 text-gray-800';
}

function formatDate(dateString) {
    if (!dateString) return '-';
    try {
        return new Date(dateString).toLocaleDateString();
    } catch {
        return dateString;
    }
}

function exportPatientData() {
    // Simple CSV export functionality
    const headers = ['Name', 'Docket', 'Modality', 'Procedure', 'Phone', 'DOB', 'Scheduled'];
    const csvContent = [
        headers.join(','),
        ...filteredPatients.map(p => [
            p.patient_name || '',
            p.docket_number || '',
            p.modality || '',
            p.procedure || '',
            p.phone_number || '',
            p.dob || '',
            p.scheduled_date || ''
        ].map(field => `"${field}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `patients_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

function renderPaginationControls() {
    const controls = document.getElementById('patient-pagination-controls');
    const totalPages = Math.ceil(filteredPatients.length / rowsPerPage);
    controls.innerHTML = '';
    if (totalPages <= 1) return;

    const start = (currentPage - 1) * rowsPerPage + 1;
    const end = Math.min(start + rowsPerPage - 1, filteredPatients.length);

    let html = `<span class="text-gray-600">Showing ${start}-${end} of ${filteredPatients.length}</span>`;
    html += `<button onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''} class="ml-2 p-1 rounded-md disabled:opacity-50 enabled:hover:bg-gray-100"><svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clip-rule="evenodd" /></svg></button>`;
    html += `<button onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''} class="p-1 rounded-md disabled:opacity-50 enabled:hover:bg-gray-100"><svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" /></svg></button>`;
    controls.innerHTML = html;
}

function changePage(page) {
    const totalPages = Math.ceil(filteredPatients.length / rowsPerPage);
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    renderPatientTable();
}

async function loadUpcomingAppointments() {
  try {
    const resp = await fetch('/api/upcoming');
    const patients = await resp.json();
    const tbody = document.getElementById('upcomingTbody');
    tbody.innerHTML = "";
    if (!patients.length) {
      tbody.innerHTML = `<tr><td data-label="Status" class="p-4 text-center text-gray-500" colspan="5">No upcoming appointments found.</td></tr>`;
      return;
    }
    patients.forEach(p => {
      const tr = document.createElement('tr');
      tr.className = "hover:bg-gray-50";
      tr.innerHTML = `
        <td data-label="Name" class="p-3 whitespace-nowrap text-sm font-medium text-gray-900">${escapeHtml(p.patient_name)}</td>
        <td data-label="Modality" class="p-3 whitespace-nowrap text-sm text-gray-500">${escapeHtml(p.modality)}</td>
        <td data-label="Time" class="p-3 whitespace-nowrap text-sm text-gray-500">${p.clinic_appointment ? new Date(p.clinic_appointment).toLocaleString([], {year:'numeric', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'}) : ''}</td>
        <td data-label="Phone" class="p-3 whitespace-nowrap text-sm text-gray-500">${escapeHtml(p.phone_number)}</td>
        <td data-label="Actions" class="p-3 text-sm font-medium">
          <button class="text-blue-600 hover:text-blue-900" onclick="openEditModal(${p.id})"><svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" /><path d="M3.5 5.75c0-.69.56-1.25 1.25-1.25H10A.75.75 0 0010 3H4.75A2.75 2.75 0 002 5.75v9.5A2.75 2.75 0 004.75 18h9.5A2.75 2.75 0 0017 15.25V10a.75.75 0 00-1.5 0v5.25c0 .69-.56 1.25-1.25 1.25h-9.5c-.69 0-1.25-.56-1.25-1.25v-9.5z" /></svg></button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch(e) { 
      console.error("Failed to load upcoming appointments", e);
      document.getElementById('upcomingTbody').innerHTML = '<tr><td data-label="Error" class="p-4 text-center text-red-500" colspan="5">Could not load appointments.</td></tr>'; 
  }
}

function navigateFormStep(step) {
    // Update form steps
    document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
    document.getElementById(`patient-form-step-${step}`).classList.add('active');
    
    // Update progress indicator
    document.querySelectorAll('.progress-step').forEach((s, index) => {
        s.classList.remove('active', 'completed');
        if (index + 1 < step) {
            s.classList.add('completed');
        } else if (index + 1 === step) {
            s.classList.add('active');
        }
    });
    
    // Scroll to top of form
    document.getElementById('patientForm').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function handlePatientSubmit(e) {
  e.preventDefault();
  const formData = {};
  patientFormFields.forEach(field => { formData[field] = document.getElementById(field).value; });
  
  const statusEl = document.getElementById('patientStatus');
  statusEl.textContent = "Adding...";
  statusEl.className = 'text-sm font-medium text-gray-500';

  const resp = await fetch('/api/patient', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
  const result = await resp.json();
  statusEl.textContent = result.message;
  
  if (resp.ok) {
    statusEl.className = 'text-sm font-medium text-green-600';
    resetPatientForm();
    loadAllData();
  } else {
    statusEl.className = 'text-sm font-medium text-red-600';
  }
  setTimeout(() => statusEl.textContent = "", 4000);
}

function resetPatientForm() {
    document.getElementById('patientForm').reset();
    navigateFormStep(1); // Go back to the first step
}

async function openEditModal(id) {
    const resp = await fetch(`/api/patient/${id}`);
    if (!resp.ok) { alert("Could not fetch patient details."); return; }
    const patient = await resp.json();
    
    patientFormFields.forEach(field => {
        const el = document.getElementById(`edit_${field}`);
        if (el) el.value = patient[field] || '';
    });
    
    document.getElementById('edit_patient_id').value = patient.id;
    document.getElementById('editModal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    document.getElementById('editPatientForm').reset();
    document.getElementById('editStatus').textContent = '';
}

async function handleUpdateSubmit(e) {
    e.preventDefault();
    const patientId = document.getElementById('edit_patient_id').value;
    const formData = {};
    patientFormFields.forEach(field => { formData[field] = document.getElementById(`edit_${field}`).value; });

    const statusEl = document.getElementById('editStatus');
    statusEl.textContent = "Updating...";
    statusEl.className = 'text-sm font-medium text-gray-500';

    const resp = await fetch(`/api/patient/${patientId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
    const result = await resp.json();
    statusEl.textContent = result.message;

    if (resp.ok) {
        statusEl.className = 'text-sm font-medium text-green-600';
        loadAllData();
        setTimeout(() => {
            closeEditModal();
        }, 1500);
    } else {
        statusEl.className = 'text-sm font-medium text-red-600';
        setTimeout(() => statusEl.textContent = '', 4000);
    }
}

async function deletePatient(id) {
  if (!confirm('Are you sure you want to delete this patient record? This action cannot be undone.')) return;
  await fetch(`/api/patient/${id}`, { method: 'DELETE' });
  loadAllData();
}

function escapeHtml(s){ 
    if (s === null || s === undefined) return ''; 
    return s.toString().replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); 
}

async function loadStats() {
  try {
    const resp = await fetch('/api/stats');
    const stats = await resp.json();
    document.getElementById('stat-total').textContent = stats.total_patients || 0;
    document.getElementById('stat-modalities').textContent = stats.total_modalities || 0;
    document.getElementById('stat-appointments').textContent = stats.pending_appointments || 0;
  } catch(e) {
    console.error("Failed to load stats", e);
  }
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML, app_name=APP_NAME)

@app.route("/api/patients", methods=['GET'])
def get_patients():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Order by name by default for initial load
    cursor.execute("SELECT * FROM patients ORDER BY patient_name ASC")
    patients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(patients)

@app.route("/api/patient/<int:patient_id>", methods=['GET'])
def get_patient(patient_id):
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    if patient is None:
        return jsonify({"message": "Patient not found"}), 404
    return jsonify(dict(patient))

@app.route("/api/patient", methods=['POST'])
def add_patient():
    data = request.json
    if not data or not data.get('patient_name'):
        return jsonify({"message": "Patient name is required."}), 400
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO patients (patient_name, docket_number, modality, procedure, phone_number, dob, coming_from, health_card, clinic_appointment, scheduled_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('patient_name'), data.get('docket_number'), data.get('modality'), data.get('procedure'),
            data.get('phone_number'), data.get('dob'), data.get('coming_from'), data.get('health_card'),
            data.get('clinic_appointment'), data.get('scheduled_date')
        ))
        conn.commit()
        return jsonify({"message": "Patient added successfully!"}), 201
    except sqlite3.Error as e:
        return jsonify({"message": f"Database error: {e}"}), 500
    finally:
        conn.close()

@app.route("/api/patient/<int:patient_id>", methods=['PUT'])
def update_patient(patient_id):
    data = request.json
    if not data or not data.get('patient_name'):
        return jsonify({"message": "Patient name is required."}), 400
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE patients SET
            patient_name = ?, docket_number = ?, modality = ?, procedure = ?, phone_number = ?,
            dob = ?, coming_from = ?, health_card = ?, clinic_appointment = ?, scheduled_date = ?
            WHERE id = ?
        """, (
            data.get('patient_name'), data.get('docket_number'), data.get('modality'), data.get('procedure'),
            data.get('phone_number'), data.get('dob'), data.get('coming_from'), data.get('health_card'),
            data.get('clinic_appointment'), data.get('scheduled_date'), patient_id
        ))
        conn.commit()
        if cursor.rowcount == 0:
             return jsonify({"message": "Patient not found"}), 404
        return jsonify({"message": "Patient updated successfully!"})
    except sqlite3.Error as e:
        return jsonify({"message": f"Database error: {e}"}), 500
    finally:
        conn.close()

@app.route("/api/patient/<int:patient_id>", methods=['DELETE'])
def delete_patient(patient_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        if cursor.rowcount == 0:
             return jsonify({"message": "Patient not found"}), 404
        return jsonify({"message": "Patient deleted successfully."})
    except sqlite3.Error as e:
        return jsonify({"message": f"Database error: {e}"}), 500
    finally:
        conn.close()

@app.route("/api/upcoming", methods=['GET'])
def get_upcoming():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Using 'now' and 'localtime' modifier to ensure correct time comparison
    cursor.execute("""
        SELECT id, patient_name, modality, clinic_appointment, phone_number FROM patients
        WHERE clinic_appointment IS NOT NULL AND clinic_appointment != ''
        AND datetime(clinic_appointment) > datetime('now', 'localtime')
        ORDER BY clinic_appointment ASC
    """)
    patients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(patients)

@app.route("/api/stats", methods=['GET'])
def get_stats():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(id) FROM patients")
        total_patients = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT modality) FROM patients WHERE modality IS NOT NULL AND modality != ''")
        total_modalities = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(id) FROM patients WHERE clinic_appointment IS NOT NULL AND clinic_appointment != '' AND datetime(clinic_appointment) > datetime('now', 'localtime')")
        pending_appointments = cursor.fetchone()[0]
        return jsonify({
            "total_patients": total_patients,
            "total_modalities": total_modalities,
            "pending_appointments": pending_appointments
        })
    except sqlite3.Error as e:
        return jsonify({"message": f"Database error: {e}"}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    # Use a specific port and set debug to False for production
    app.run(debug=True, host='0.0.0.0', port=5001)