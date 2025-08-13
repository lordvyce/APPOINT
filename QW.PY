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
    --primary-color: #3B82F6; /* Calming Blue */
    --primary-hover: #2563EB;
    --secondary-color: #10B981; /* Medical Green */
    --background-color: #F3F4F6; /* Soft Gray */
    --card-background: #FFFFFF;
    --text-primary: #1F2937;
    --text-secondary: #4B5563;
    --border-color: #E5E7EB;
  }
  body {
    font-family: 'Inter', sans-serif;
    background-color: var(--background-color);
    color: var(--text-primary);
  }
  .card {
    background-color: var(--card-background);
    border-radius: 0.75rem;
    border: 1px solid var(--border-color);
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
  }
  .table-responsive-wrapper {
    overflow-x: auto;
  }
  .button-primary {
    background-color: var(--primary-color);
    color: white;
    font-weight: 500;
    padding: 0.6rem 1.25rem;
    border-radius: 0.5rem;
    transition: background-color 0.2s;
  }
  .button-primary:hover { background-color: var(--primary-hover); }
  .button-secondary {
    background-color: var(--card-background);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
    font-weight: 500;
    padding: 0.6rem 1.25rem;
    border-radius: 0.5rem;
    transition: background-color 0.2s;
  }
  .button-secondary:hover { background-color: #F9FAFB; }
  .form-input {
    width: 100%;
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 0.75rem 1rem;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .form-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4);
  }
  .table-header {
    background-color: #F9FAFB;
    color: var(--text-secondary);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.75rem;
    cursor: pointer;
  }
  .table-header .sort-icon {
    opacity: 0.4;
    transition: opacity 0.2s;
  }
  .table-header:hover .sort-icon { opacity: 1; }

  /* Responsive Table styling for mobile */
  @media (max-width: 768px) {
    .responsive-table thead { display: none; }
    .responsive-table tr {
        display: block;
        margin-bottom: 1rem;
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    .responsive-table td {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border-color);
    }
    .responsive-table td:last-child { border-bottom: none; }
    .responsive-table td::before {
        content: attr(data-label);
        font-weight: 600;
        margin-right: 1rem;
        color: var(--text-primary);
    }
  }
  /* Modal Styles */
  .modal-overlay {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.4);
    display: none; align-items: center; justify-content: center; z-index: 1000;
    backdrop-filter: blur(4px);
  }
  /* Form Wizard */
  .form-step { display: none; }
  .form-step.active { display: block; }
</style>
</head>
<body onload="initApp()">
  <div class="min-h-screen">
    <nav class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3">
            <svg class="h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" /></svg>
            <span class="text-xl font-bold text-gray-800">{{ app_name }}</span>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-4 sm:px-0">
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
          <div class="card p-5">
            <dt class="text-sm font-medium text-gray-500 truncate flex items-center">
              <svg class="h-5 w-5 mr-2 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.101a1.531 1.531 0 01.634-2.033l.283-.177a1.13 1.13 0 00-.704-2.226c-1.131-.24-2.202-.602-3.182-1.098A4.125 4.125 0 005.364 2.5a4.125 4.125 0 007.533 2.493m-3.753-.421c-.813-.328-1.71-.53-2.625-.532A9.337 9.337 0 003.121 4.542a4.125 4.125 0 00-7.533 2.493h3.753z" /></svg>
              Total Patients
            </dt>
            <dd id="stat-total" class="mt-1 text-3xl font-semibold text-gray-900">0</dd>
          </div>
          <div class="card p-5">
            <dt class="text-sm font-medium text-gray-500 truncate flex items-center">
                <svg class="h-5 w-5 mr-2 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 4.5l7.5 7.5-7.5 7.5m-6-15l7.5 7.5-7.5 7.5" /></svg>
                Total Modalities
            </dt>
            <dd id="stat-modalities" class="mt-1 text-3xl font-semibold text-gray-900">0</dd>
          </div>
          <div class="card p-5">
            <dt class="text-sm font-medium text-gray-500 truncate flex items-center">
                <svg class="h-5 w-5 mr-2 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" /></svg>
                Upcoming Appointments
            </dt>
            <dd id="stat-appointments" class="mt-1 text-3xl font-semibold text-gray-900">0</dd>
          </div>
        </div>
      </div>
      
      <div class="mt-6">
          <div class="sm:hidden">
              <label for="tabs" class="sr-only">Select a tab</label>
              <select id="tabs" name="tabs" class="block w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500" onchange="showTab(this.value)">
                  <option value="manage" selected>Add Patient</option>
                  <option value="patients">Patient List</option>
                  <option value="upcoming">Upcoming Appointments</option>
              </select>
          </div>
          <div class="hidden sm:block">
              <div class="border-b border-gray-200">
                  <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                      <button class="tab-btn active" onclick="showTab('manage')">Add Patient</button>
                      <button class="tab-btn" onclick="showTab('patients')">Patient List</button>
                      <button class="tab-btn" onclick="showTab('upcoming')">Upcoming Appointments</button>
                  </nav>
              </div>
          </div>
      </div>
      
      <div class="mt-6">
        <div id="tab-manage" class="tab-content active">
          <div class="card p-6 lg:p-8">
            <form id="patientForm" onsubmit="handlePatientSubmit(event)">
              <div id="patient-form-step-1" class="form-step active">
                <h3 class="text-lg font-medium leading-6 text-gray-900">1. Patient Information</h3>
                <p class="mt-1 text-sm text-gray-600">Enter the patient's personal and contact details.</p>
                <div class="mt-6 grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-8">
                    <div><label class="block text-sm font-medium text-gray-700">Patient Name <span class="text-red-500">*</span></label><div class="mt-1"><input type="text" id="patient_name" class="form-input" required></div></div>
                    <div><label class="block text-sm font-medium text-gray-700">Date of Birth</label><div class="mt-1"><input type="date" id="dob" class="form-input"></div></div>
                    <div><label class="block text-sm font-medium text-gray-700">Phone Number</label><div class="mt-1"><input type="tel" id="phone_number" class="form-input"></div></div>
                    <div><label class="block text-sm font-medium text-gray-700">Docket Number</label><div class="mt-1"><input type="text" id="docket_number" class="form-input"></div></div>
                </div>
                <div class="mt-8 flex justify-end">
                    <button type="button" class="button-primary" onclick="navigateFormStep(2)">Next &rarr;</button>
                </div>
              </div>

              <div id="patient-form-step-2" class="form-step">
                <h3 class="text-lg font-medium leading-6 text-gray-900">2. Examination Details</h3>
                <p class="mt-1 text-sm text-gray-600">Provide information about the medical examination.</p>
                <div class="mt-6 grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-8">
                    <div><label class="block text-sm font-medium text-gray-700">Modality</label><div class="mt-1"><select id="modality" class="form-input"><option value="">Select...</option><option>US</option><option>CT</option><option>DX/CR</option><option>MAMMO</option></select></div></div>
                    <div><label class="block text-sm font-medium text-gray-700">Procedure</label><div class="mt-1"><input type="text" id="procedure" class="form-input"></div></div>
                    <div><label class="block text-sm font-medium text-gray-700">Source / Coming From</label><div class="mt-1"><input type="text" id="coming_from" class="form-input"></div></div>
                    <div><label class="block text-sm font-medium text-gray-700">Health Card</label><div class="mt-1"><select id="health_card" class="form-input"><option value="">Select...</option><option>Sagicor</option><option>Canopy</option><option>Guardian Life</option><option>Other</option></select></div></div>
                </div>
                <div class="mt-8 flex justify-between">
                    <button type="button" class="button-secondary" onclick="navigateFormStep(1)">&larr; Back</button>
                    <button type="button" class="button-primary" onclick="navigateFormStep(3)">Next &rarr;</button>
                </div>
              </div>

              <div id="patient-form-step-3" class="form-step">
                <h3 class="text-lg font-medium leading-6 text-gray-900">3. Scheduling</h3>
                <p class="mt-1 text-sm text-gray-600">Set dates for the procedure and clinic follow-up.</p>
                <div class="mt-6 grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-8">
                    <div><label class="block text-sm font-medium text-gray-700">Scheduled Procedure Date</label><div class="mt-1"><input type="date" id="scheduled_date" class="form-input"></div></div>
                    <div><label class="block text-sm font-medium text-gray-700">Clinic Appointment</label><div class="mt-1"><input type="datetime-local" id="clinic_appointment" class="form-input"></div></div>
                </div>
                <div class="mt-8 flex justify-between items-center">
                    <button type="button" class="button-secondary" onclick="navigateFormStep(2)">&larr; Back</button>
                    <div class="flex items-center space-x-4">
                        <div id="patientStatus" class="text-sm font-medium"></div>
                        <button type="submit" class="button-primary">Add Patient</button>
                    </div>
                </div>
              </div>
            </form>
          </div>
        </div>

        <div id="tab-patients" class="tab-content">
          <div class="card">
            <div class="p-4 border-b border-gray-200 flex items-center justify-between">
                <div class="relative">
                    <div class="pointer-events-none absolute inset-y-0 left-0 pl-3 flex items-center">
                        <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd" /></svg>
                    </div>
                    <input type="search" id="patientSearch" class="form-input pl-10" placeholder="Search by name, docket...">
                </div>
                <div id="patient-pagination-controls" class="flex items-center space-x-2 text-sm"></div>
            </div>
            <div class="table-responsive-wrapper">
                <table class="min-w-full responsive-table">
                    <thead class="table-header">
                        <tr>
                            <th class="p-3 text-left" onclick="sortPatients('patient_name')">Name <span class="sort-icon">&uarr;&darr;</span></th>
                            <th class="p-3 text-left" onclick="sortPatients('docket_number')">Docket <span class="sort-icon">&uarr;&darr;</span></th>
                            <th class="p-3 text-left">Modality</th>
                            <th class="p-3 text-left">Procedure</th>
                            <th class="p-3 text-left">Phone</th>
                            <th class="p-3 text-left" onclick="sortPatients('dob')">DOB <span class="sort-icon">&uarr;&darr;</span></th>
                            <th class="p-3 text-left" onclick="sortPatients('scheduled_date')">Scheduled <span class="sort-icon">&uarr;&darr;</span></th>
                            <th class="p-3 text-left">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="patientTbody" class="divide-y divide-gray-200 bg-white"></tbody>
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
    <div class="card w-full max-w-3xl m-4">
      <div class="p-6">
        <h2 id="modal-title" class="text-xl font-bold text-gray-900">Edit Patient Record</h2>
        <form id="editPatientForm" onsubmit="handleUpdateSubmit(event)" class="mt-4">
          <input type="hidden" id="edit_patient_id">
          <div class="grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-6">
            <div><label class="block text-sm font-medium">Name</label><input type="text" id="edit_patient_name" class="form-input mt-1" required></div>
            <div><label class="block text-sm font-medium">Docket Number</label><input type="text" id="edit_docket_number" class="form-input mt-1"></div>
            <div><label class="block text-sm font-medium">Modality</label><select id="edit_modality" class="form-input mt-1"><option value="">Select...</option><option>US</option><option>CT</option><option>DX/CR</option><option>MAMMO</option></select></div>
            <div><label class="block text-sm font-medium">Procedure</label><input type="text" id="edit_procedure" class="form-input mt-1"></div>
            <div><label class="block text-sm font-medium">Phone</label><input type="tel" id="edit_phone_number" class="form-input mt-1"></div>
            <div><label class="block text-sm font-medium">DOB</label><input type="date" id="edit_dob" class="form-input mt-1"></div>
            <div><label class="block text-sm font-medium">Source</label><input type="text" id="edit_coming_from" class="form-input mt-1"></div>
            <div><label class="block text-sm font-medium">Health Card</label><select id="edit_health_card" class="form-input mt-1"><option value="">Select</option><option>Sagicor</option><option>Canopy</option><option>Guardian Life</option><option>Other</option></select></div>
            <div><label class="block text-sm font-medium">Scheduled Date</label><input type="date" id="edit_scheduled_date" class="form-input mt-1"></div>
            <div><label class="block text-sm font-medium">Clinic Appointment</label><input type="datetime-local" id="edit_clinic_appointment" class="form-input mt-1"></div>
          </div>
          <div class="mt-6 flex justify-end items-center space-x-4">
            <div id="editStatus" class="text-sm font-medium"></div>
            <button type="button" class="button-secondary" onclick="closeEditModal()">Cancel</button>
            <button type="submit" class="button-primary">Update Patient</button>
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
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active', 'text-blue-600', 'border-blue-600'));
            btn.classList.add('active', 'text-blue-600', 'border-blue-600');
        });
    });
    // Setup search listener
    document.getElementById('patientSearch').addEventListener('input', (e) => {
        filterAndRenderPatients(e.target.value);
    });

    loadAllData();
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
      tbody.innerHTML = `<tr><td data-label="Status" class="p-4 text-center text-gray-500" colspan="8">No patients found.</td></tr>`;
      renderPaginationControls();
      return;
    }

    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedItems = filteredPatients.slice(start, end);

    paginatedItems.forEach(p => {
      const tr = document.createElement('tr');
      tr.className = "hover:bg-gray-50";
      tr.innerHTML = `
        <td data-label="Name" class="p-3 whitespace-nowrap text-sm font-medium text-gray-900">${escapeHtml(p.patient_name)}</td>
        <td data-label="Docket" class="p-3 whitespace-nowrap text-sm text-gray-500">${escapeHtml(p.docket_number)}</td>
        <td data-label="Modality" class="p-3 whitespace-nowrap text-sm text-gray-500">${escapeHtml(p.modality)}</td>
        <td data-label="Procedure" class="p-3 whitespace-nowrap text-sm text-gray-500">${escapeHtml(p.procedure)}</td>
        <td data-label="Phone" class="p-3 whitespace-nowrap text-sm text-gray-500">${escapeHtml(p.phone_number)}</td>
        <td data-label="DOB" class="p-3 whitespace-nowrap text-sm text-gray-500">${escapeHtml(p.dob)}</td>
        <td data-label="Scheduled" class="p-3 whitespace-nowrap text-sm text-gray-500">${escapeHtml(p.scheduled_date)}</td>
        <td data-label="Actions" class="p-3 text-sm font-medium">
          <div class="flex items-center space-x-2">
            <button class="text-blue-600 hover:text-blue-900" onclick="openEditModal(${p.id})"><svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" /><path d="M3.5 5.75c0-.69.56-1.25 1.25-1.25H10A.75.75 0 0010 3H4.75A2.75 2.75 0 002 5.75v9.5A2.75 2.75 0 004.75 18h9.5A2.75 2.75 0 0017 15.25V10a.75.75 0 00-1.5 0v5.25c0 .69-.56 1.25-1.25 1.25h-9.5c-.69 0-1.25-.56-1.25-1.25v-9.5z" /></svg></button>
            <button class="text-red-600 hover:text-red-900" onclick="deletePatient(${p.id})"><svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.58.22-2.326.432C2.044 4.963 1 6.227 1 7.618v5.772c0 1.392 1.044 2.656 2.674 2.973.746.212 1.531.355 2.326.432v.443A2.75 2.75 0 008.75 20h2.5A2.75 2.75 0 0014 17.25v-.443c.795-.077 1.58-.22 2.326-.432C17.956 16.037 19 14.773 19 13.382V7.618c0-1.392-1.044-2.656-2.674-2.973A23.89 23.89 0 0014 4.193v-.443A2.75 2.75 0 0011.25 1h-2.5zM10 8.5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 8.5z" clip-rule="evenodd" /></svg></button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });
    renderPaginationControls();
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
    document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
    document.getElementById(`patient-form-step-${step}`).classList.add('active');
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