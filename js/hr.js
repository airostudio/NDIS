/**
 * Velma HR & Compliance Module
 * Handles employee management, screening, training, documents, and incidents
 */

// Sample data structure for demonstration
const sampleEmployees = [
    {
        id: 1,
        name: 'Sarah Johnson',
        position: 'Support Worker - Level 2.2',
        status: 'active',
        startDate: '2024-01-15',
        email: 'sarah.johnson@example.com',
        phone: '0412 345 678',
        wwcc: { number: 'WWC123456', expiry: '2026-06-30', status: 'valid' },
        policeCheck: { date: '2025-01-10', expiry: '2026-01-10', status: 'valid' },
        ndisScreening: { number: 'NDIS789012', expiry: '2027-03-15', status: 'valid' },
        firstAid: { expiry: '2026-04-20', status: 'valid' },
        cpr: { expiry: '2026-04-20', status: 'valid' },
        manualHandling: { expiry: '2025-08-30', status: 'expiring' },
        compliance: 95
    },
    {
        id: 2,
        name: 'Michael Chen',
        position: 'Team Leader - Level 3',
        status: 'active',
        startDate: '2023-03-22',
        email: 'michael.chen@example.com',
        phone: '0423 456 789',
        wwcc: { number: 'WWC234567', expiry: '2025-12-15', status: 'valid' },
        policeCheck: { date: '2024-11-05', expiry: '2025-11-05', status: 'expiring' },
        ndisScreening: { number: 'NDIS890123', expiry: '2026-09-20', status: 'valid' },
        firstAid: { expiry: '2026-07-10', status: 'valid' },
        cpr: { expiry: '2026-07-10', status: 'valid' },
        manualHandling: { expiry: '2026-02-28', status: 'valid' },
        compliance: 90
    },
    {
        id: 3,
        name: 'Emma Williams',
        position: 'Support Worker - Level 2.1',
        status: 'onboarding',
        startDate: '2026-02-01',
        email: 'emma.williams@example.com',
        phone: '0434 567 890',
        wwcc: { number: 'WWC345678', expiry: '2028-01-10', status: 'valid' },
        policeCheck: { date: '2026-01-20', expiry: '2027-01-20', status: 'valid' },
        ndisScreening: { number: 'NDIS901234', expiry: '2028-05-05', status: 'pending' },
        firstAid: { expiry: null, status: 'required' },
        cpr: { expiry: null, status: 'required' },
        manualHandling: { expiry: null, status: 'required' },
        compliance: 45
    }
];

const sampleIncidents = [
    {
        id: 'INC-2026-001',
        date: '2026-02-03',
        type: 'Near Miss',
        severity: 'low',
        reporter: 'Sarah Johnson',
        description: 'Client nearly tripped on loose carpet edge in hallway',
        status: 'under_review',
        actions: 'Maintenance notified, carpet repair scheduled'
    },
    {
        id: 'INC-2026-002',
        date: '2026-01-28',
        type: 'Client Injury',
        severity: 'medium',
        reporter: 'Michael Chen',
        description: 'Client sustained minor bruise during transfer',
        status: 'resolved',
        actions: 'First aid provided, incident form completed, family notified'
    }
];

// Data management
class HRDataManager {
    constructor() {
        this.employees = this.loadData('hr_employees') || sampleEmployees;
        this.incidents = this.loadData('hr_incidents') || sampleIncidents;
        this.documents = this.loadData('hr_documents') || [];
    }

    loadData(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error(`Error loading ${key}:`, error);
            return null;
        }
    }

    saveData(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.error(`Error saving ${key}:`, error);
        }
    }

    getEmployees() {
        return this.employees;
    }

    addEmployee(employee) {
        employee.id = Date.now();
        this.employees.push(employee);
        this.saveData('hr_employees', this.employees);
        return employee;
    }

    updateEmployee(id, updates) {
        const index = this.employees.findIndex(e => e.id === id);
        if (index !== -1) {
            this.employees[index] = { ...this.employees[index], ...updates };
            this.saveData('hr_employees', this.employees);
            return this.employees[index];
        }
        return null;
    }

    deleteEmployee(id) {
        this.employees = this.employees.filter(e => e.id !== id);
        this.saveData('hr_employees', this.employees);
    }

    getIncidents() {
        return this.incidents;
    }

    addIncident(incident) {
        incident.id = `INC-${new Date().getFullYear()}-${String(this.incidents.length + 1).padStart(3, '0')}`;
        incident.date = new Date().toISOString().split('T')[0];
        this.incidents.unshift(incident);
        this.saveData('hr_incidents', this.incidents);
        return incident;
    }

    updateIncident(id, updates) {
        const index = this.incidents.findIndex(i => i.id === id);
        if (index !== -1) {
            this.incidents[index] = { ...this.incidents[index], ...updates };
            this.saveData('hr_incidents', this.incidents);
            return this.incidents[index];
        }
        return null;
    }

    getDocuments() {
        return this.documents;
    }

    addDocument(document) {
        document.id = Date.now();
        document.uploadDate = new Date().toISOString().split('T')[0];
        this.documents.push(document);
        this.saveData('hr_documents', this.documents);
        return document;
    }

    // Calculate statistics
    getStats() {
        const employees = this.getEmployees();
        const now = new Date();
        const thirtyDaysFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);

        let expiringCount = 0;
        employees.forEach(emp => {
            if (emp.status === 'active') {
                const checks = [
                    emp.wwcc?.expiry,
                    emp.policeCheck?.expiry,
                    emp.ndisScreening?.expiry,
                    emp.firstAid?.expiry,
                    emp.cpr?.expiry,
                    emp.manualHandling?.expiry
                ];

                checks.forEach(expiry => {
                    if (expiry) {
                        const expiryDate = new Date(expiry);
                        if (expiryDate >= now && expiryDate <= thirtyDaysFromNow) {
                            expiringCount++;
                        }
                    }
                });
            }
        });

        const compliantEmployees = employees.filter(e =>
            e.status === 'active' && e.compliance >= 90
        ).length;

        const openIncidents = this.incidents.filter(i =>
            i.status !== 'resolved' && i.status !== 'closed'
        ).length;

        return {
            totalEmployees: employees.length,
            compliantEmployees,
            expiringCredentials: expiringCount,
            openIncidents
        };
    }

    // Get expiry alerts
    getExpiryAlerts() {
        const employees = this.getEmployees();
        const now = new Date();
        const thirtyDaysFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
        const alerts = [];

        employees.forEach(emp => {
            if (emp.status === 'active') {
                const checks = [
                    { name: 'WWCC', expiry: emp.wwcc?.expiry, type: 'wwcc' },
                    { name: 'Police Check', expiry: emp.policeCheck?.expiry, type: 'police' },
                    { name: 'NDIS Screening', expiry: emp.ndisScreening?.expiry, type: 'ndis' },
                    { name: 'First Aid', expiry: emp.firstAid?.expiry, type: 'firstaid' },
                    { name: 'CPR', expiry: emp.cpr?.expiry, type: 'cpr' },
                    { name: 'Manual Handling', expiry: emp.manualHandling?.expiry, type: 'manual' }
                ];

                checks.forEach(check => {
                    if (check.expiry) {
                        const expiryDate = new Date(check.expiry);
                        const daysUntilExpiry = Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24));

                        if (daysUntilExpiry <= 30 && daysUntilExpiry >= 0) {
                            alerts.push({
                                employee: emp.name,
                                credential: check.name,
                                expiry: check.expiry,
                                daysRemaining: daysUntilExpiry,
                                type: check.type
                            });
                        } else if (daysUntilExpiry < 0) {
                            alerts.push({
                                employee: emp.name,
                                credential: check.name,
                                expiry: check.expiry,
                                daysRemaining: daysUntilExpiry,
                                type: check.type,
                                expired: true
                            });
                        }
                    }
                });
            }
        });

        return alerts.sort((a, b) => a.daysRemaining - b.daysRemaining);
    }
}

// Initialize HR Module
class HRModule {
    constructor() {
        this.dataManager = new HRDataManager();
        this.currentTab = 'employees';
        this.init();
    }

    init() {
        // Update stats
        this.updateStats();

        // Show expiry alerts
        this.showExpiryAlerts();

        // Setup tab switching
        this.setupTabs();

        // Render initial tables
        this.renderEmployeesTable();
        this.renderScreeningTable();
        this.renderTrainingTable();
        this.renderDocumentsTable();
        this.renderIncidentsTable();

        // Setup button handlers
        this.setupButtonHandlers();

        // Setup search and filters
        this.setupSearchAndFilters();
    }

    updateStats() {
        const stats = this.dataManager.getStats();

        document.getElementById('totalEmployees').textContent = stats.totalEmployees;
        document.getElementById('compliantEmployees').textContent = stats.compliantEmployees;
        document.getElementById('expiringCredentials').textContent = stats.expiringCredentials;
        document.getElementById('openIncidents').textContent = stats.openIncidents;

        // Update alerts badge
        const alertsBadge = document.getElementById('alertsBadge');
        if (alertsBadge) {
            const totalAlerts = stats.expiringCredentials + stats.openIncidents;
            alertsBadge.textContent = totalAlerts;
            alertsBadge.style.display = totalAlerts > 0 ? 'inline-block' : 'none';
        }
    }

    showExpiryAlerts() {
        const alerts = this.dataManager.getExpiryAlerts();
        const alertsSection = document.getElementById('alertsSection');

        if (alerts.length === 0) {
            alertsSection.innerHTML = '';
            return;
        }

        const expiredAlerts = alerts.filter(a => a.expired);
        const expiringAlerts = alerts.filter(a => !a.expired);

        let html = '';

        if (expiredAlerts.length > 0) {
            html += '<div class="alert alert-error" style="margin-bottom: var(--spacing-md);">';
            html += '<strong>⚠️ Expired Credentials</strong><ul style="margin: var(--spacing-sm) 0 0 var(--spacing-xl); padding: 0;">';
            expiredAlerts.slice(0, 3).forEach(alert => {
                html += `<li>${alert.employee}: ${alert.credential} expired ${Math.abs(alert.daysRemaining)} days ago</li>`;
            });
            if (expiredAlerts.length > 3) {
                html += `<li>... and ${expiredAlerts.length - 3} more</li>`;
            }
            html += '</ul></div>';
        }

        if (expiringAlerts.length > 0) {
            html += '<div class="alert alert-warning">';
            html += '<strong>⏰ Credentials Expiring Soon (Next 30 Days)</strong><ul style="margin: var(--spacing-sm) 0 0 var(--spacing-xl); padding: 0;">';
            expiringAlerts.slice(0, 5).forEach(alert => {
                html += `<li>${alert.employee}: ${alert.credential} expires in ${alert.daysRemaining} days (${alert.expiry})</li>`;
            });
            if (expiringAlerts.length > 5) {
                html += `<li>... and ${expiringAlerts.length - 5} more</li>`;
            }
            html += '</ul></div>';
        }

        alertsSection.innerHTML = html;
    }

    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons and content
                tabButtons.forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });

                // Add active class to clicked button and corresponding content
                button.classList.add('active');
                const tabName = button.dataset.tab;
                document.getElementById(`${tabName}Tab`).classList.add('active');

                this.currentTab = tabName;
            });
        });
    }

    renderEmployeesTable() {
        const tbody = document.getElementById('employeeTableBody');
        const employees = this.dataManager.getEmployees();

        if (employees.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: var(--spacing-3xl); color: var(--color-gray-500);">No employees yet. Click "Add Employee" to get started.</td></tr>';
            return;
        }

        tbody.innerHTML = employees.map(emp => `
            <tr>
                <td>
                    <div style="font-weight: var(--font-weight-semibold);">${emp.name}</div>
                    <div style="font-size: var(--font-size-sm); color: var(--color-gray-600);">${emp.email}</div>
                </td>
                <td>${emp.position}</td>
                <td><span class="badge badge-${this.getStatusClass(emp.status)}">${this.formatStatus(emp.status)}</span></td>
                <td>
                    <div style="display: flex; align-items: center; gap: var(--spacing-sm);">
                        <div style="flex: 1; height: 8px; background: var(--color-gray-200); border-radius: var(--radius-full); overflow: hidden;">
                            <div style="height: 100%; width: ${emp.compliance}%; background: ${this.getComplianceColor(emp.compliance)};"></div>
                        </div>
                        <span style="font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold);">${emp.compliance}%</span>
                    </div>
                </td>
                <td>${this.formatDate(emp.startDate)}</td>
                <td>
                    <button class="btn btn-sm btn-ghost" onclick="hrModule.viewEmployee(${emp.id})">View</button>
                </td>
            </tr>
        `).join('');
    }

    renderScreeningTable() {
        const tbody = document.getElementById('screeningTableBody');
        const employees = this.dataManager.getEmployees();

        if (employees.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: var(--spacing-3xl); color: var(--color-gray-500);">No screening records yet.</td></tr>';
            return;
        }

        tbody.innerHTML = employees.map(emp => `
            <tr>
                <td>${emp.name}</td>
                <td>${this.renderCredentialStatus(emp.wwcc)}</td>
                <td>${this.renderCredentialStatus(emp.policeCheck)}</td>
                <td>${this.renderCredentialStatus(emp.ndisScreening)}</td>
                <td><span class="badge badge-${emp.compliance >= 90 ? 'success' : emp.compliance >= 70 ? 'warning' : 'error'}">${emp.compliance >= 90 ? 'Compliant' : 'Action Required'}</span></td>
                <td>
                    <button class="btn btn-sm btn-ghost" onclick="hrModule.updateScreening(${emp.id})">Update</button>
                </td>
            </tr>
        `).join('');
    }

    renderTrainingTable() {
        const tbody = document.getElementById('trainingTableBody');
        const employees = this.dataManager.getEmployees();

        if (employees.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: var(--spacing-3xl); color: var(--color-gray-500);">No training records yet.</td></tr>';
            return;
        }

        tbody.innerHTML = employees.map(emp => `
            <tr>
                <td>${emp.name}</td>
                <td>${this.renderCredentialStatus(emp.firstAid)}</td>
                <td>${this.renderCredentialStatus(emp.cpr)}</td>
                <td>${this.renderCredentialStatus(emp.manualHandling)}</td>
                <td><span class="badge badge-info">View All</span></td>
                <td>
                    <button class="btn btn-sm btn-ghost" onclick="hrModule.updateTraining(${emp.id})">Update</button>
                </td>
            </tr>
        `).join('');
    }

    renderDocumentsTable() {
        const tbody = document.getElementById('documentsTableBody');
        const documents = this.dataManager.getDocuments();

        if (documents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: var(--spacing-3xl); color: var(--color-gray-500);">No documents uploaded yet.</td></tr>';
            return;
        }

        tbody.innerHTML = documents.map(doc => `
            <tr>
                <td>${doc.name}</td>
                <td>${doc.employeeName}</td>
                <td><span class="badge badge-info">${doc.type}</span></td>
                <td>${this.formatDate(doc.uploadDate)}</td>
                <td>${doc.expiryDate ? this.formatDate(doc.expiryDate) : 'N/A'}</td>
                <td>${this.renderDocumentStatus(doc)}</td>
                <td>
                    <button class="btn btn-sm btn-ghost" onclick="hrModule.viewDocument(${doc.id})">View</button>
                </td>
            </tr>
        `).join('');
    }

    renderIncidentsTable() {
        const tbody = document.getElementById('incidentsTableBody');
        const incidents = this.dataManager.getIncidents();

        if (incidents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: var(--spacing-3xl); color: var(--color-gray-500);">No incidents reported.</td></tr>';
            return;
        }

        tbody.innerHTML = incidents.map(incident => `
            <tr>
                <td><strong>${incident.id}</strong></td>
                <td>${this.formatDate(incident.date)}</td>
                <td><span class="badge badge-info">${incident.type}</span></td>
                <td><span class="badge badge-${this.getSeverityClass(incident.severity)}">${this.formatSeverity(incident.severity)}</span></td>
                <td>${incident.reporter}</td>
                <td><span class="badge badge-${this.getIncidentStatusClass(incident.status)}">${this.formatIncidentStatus(incident.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-ghost" onclick="hrModule.viewIncident('${incident.id}')">View</button>
                </td>
            </tr>
        `).join('');
    }

    renderCredentialStatus(credential) {
        if (!credential || !credential.expiry) {
            return '<span class="badge badge-gray">Not Provided</span>';
        }

        const statusClass = this.getCredentialStatusClass(credential.status);
        const expiryText = credential.expiry ? `Expires: ${this.formatDate(credential.expiry)}` : '';

        return `
            <div>
                <span class="badge badge-${statusClass}">${this.formatCredentialStatus(credential.status)}</span>
                ${expiryText ? `<div style="font-size: var(--font-size-xs); color: var(--color-gray-600); margin-top: var(--spacing-xs);">${expiryText}</div>` : ''}
            </div>
        `;
    }

    renderDocumentStatus(doc) {
        if (!doc.expiryDate) {
            return '<span class="badge badge-gray">No Expiry</span>';
        }

        const now = new Date();
        const expiry = new Date(doc.expiryDate);
        const daysUntil = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));

        if (daysUntil < 0) {
            return '<span class="badge badge-error">Expired</span>';
        } else if (daysUntil <= 30) {
            return '<span class="badge badge-warning">Expiring Soon</span>';
        } else {
            return '<span class="badge badge-success">Current</span>';
        }
    }

    setupButtonHandlers() {
        // Add Employee button
        document.getElementById('addEmployeeBtn')?.addEventListener('click', () => {
            VelmaToast.info('Employee onboarding form coming soon. For now, sample data is pre-loaded.');
        });

        // Report Incident button
        document.getElementById('reportIncidentBtn')?.addEventListener('click', () => {
            this.showReportIncidentModal();
        });
    }

    setupSearchAndFilters() {
        const searchInput = document.getElementById('employeeSearch');
        const filterSelect = document.getElementById('filterStatus');

        if (searchInput) {
            searchInput.addEventListener('input', () => this.renderEmployeesTable());
        }

        if (filterSelect) {
            filterSelect.addEventListener('change', () => this.renderEmployeesTable());
        }
    }

    showReportIncidentModal() {
        const employees = this.dataManager.getEmployees();
        const employeeOptions = employees.map(e =>
            `<option value="${e.name}">${e.name}</option>`
        ).join('');

        const modalContent = `
            <form id="incidentForm">
                <div class="form-group">
                    <label class="form-label">Incident Type *</label>
                    <select class="form-select" name="type" required>
                        <option value="">Select type...</option>
                        <option value="Near Miss">Near Miss</option>
                        <option value="Client Injury">Client Injury</option>
                        <option value="Staff Injury">Staff Injury</option>
                        <option value="Property Damage">Property Damage</option>
                        <option value="Medication Error">Medication Error</option>
                        <option value="Behavioral Incident">Behavioral Incident</option>
                        <option value="Other">Other</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="form-label">Severity *</label>
                    <select class="form-select" name="severity" required>
                        <option value="">Select severity...</option>
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                </div>

                <div class="form-group">
                    <label class="form-label">Reporter *</label>
                    <select class="form-select" name="reporter" required>
                        <option value="">Select reporter...</option>
                        ${employeeOptions}
                    </select>
                </div>

                <div class="form-group">
                    <label class="form-label">Description *</label>
                    <textarea class="form-control" name="description" rows="4" required placeholder="Describe what happened..."></textarea>
                </div>

                <div class="form-group">
                    <label class="form-label">Immediate Actions Taken</label>
                    <textarea class="form-control" name="actions" rows="3" placeholder="Describe any immediate actions taken..."></textarea>
                </div>
            </form>
        `;

        VelmaModal.show(
            'Report Incident',
            modalContent,
            [
                {
                    id: 'cancel',
                    label: 'Cancel',
                    className: 'btn btn-ghost'
                },
                {
                    id: 'submit',
                    label: 'Report Incident',
                    className: 'btn btn-primary',
                    handler: () => {
                        const form = document.getElementById('incidentForm');
                        if (form.checkValidity()) {
                            const formData = new FormData(form);
                            const incident = {
                                type: formData.get('type'),
                                severity: formData.get('severity'),
                                reporter: formData.get('reporter'),
                                description: formData.get('description'),
                                actions: formData.get('actions') || 'None recorded',
                                status: 'under_review'
                            };

                            this.dataManager.addIncident(incident);
                            this.updateStats();
                            this.renderIncidentsTable();
                            this.showExpiryAlerts();

                            VelmaToast.success(`Incident ${incident.id} reported successfully`);
                        } else {
                            form.reportValidity();
                            return false; // Don't close modal
                        }
                    }
                }
            ]
        );
    }

    // View employee details
    viewEmployee(id) {
        const employee = this.dataManager.getEmployees().find(e => e.id === id);
        if (!employee) return;

        VelmaToast.info(`Viewing details for ${employee.name}. Full employee profile coming soon.`);
    }

    // Update screening
    updateScreening(id) {
        VelmaToast.info('Screening update form coming soon.');
    }

    // Update training
    updateTraining(id) {
        VelmaToast.info('Training update form coming soon.');
    }

    // View document
    viewDocument(id) {
        VelmaToast.info('Document viewer coming soon.');
    }

    // View incident details
    viewIncident(id) {
        const incident = this.dataManager.getIncidents().find(i => i.id === id);
        if (!incident) return;

        const content = `
            <div style="display: grid; gap: var(--spacing-md);">
                <div><strong>Incident ID:</strong> ${incident.id}</div>
                <div><strong>Date:</strong> ${this.formatDate(incident.date)}</div>
                <div><strong>Type:</strong> ${incident.type}</div>
                <div><strong>Severity:</strong> <span class="badge badge-${this.getSeverityClass(incident.severity)}">${this.formatSeverity(incident.severity)}</span></div>
                <div><strong>Reporter:</strong> ${incident.reporter}</div>
                <div><strong>Status:</strong> <span class="badge badge-${this.getIncidentStatusClass(incident.status)}">${this.formatIncidentStatus(incident.status)}</span></div>
                <div><strong>Description:</strong><br>${incident.description}</div>
                <div><strong>Actions Taken:</strong><br>${incident.actions}</div>
            </div>
        `;

        VelmaModal.show(
            'Incident Details',
            content,
            [
                {
                    id: 'close',
                    label: 'Close',
                    className: 'btn btn-primary'
                }
            ]
        );
    }

    // Utility functions
    getStatusClass(status) {
        const classes = {
            'active': 'success',
            'onboarding': 'info',
            'inactive': 'gray'
        };
        return classes[status] || 'gray';
    }

    formatStatus(status) {
        return status.charAt(0).toUpperCase() + status.slice(1);
    }

    getComplianceColor(compliance) {
        if (compliance >= 90) return 'var(--color-success)';
        if (compliance >= 70) return 'var(--color-warning)';
        return 'var(--color-error)';
    }

    getCredentialStatusClass(status) {
        const classes = {
            'valid': 'success',
            'expiring': 'warning',
            'expired': 'error',
            'pending': 'info',
            'required': 'gray'
        };
        return classes[status] || 'gray';
    }

    formatCredentialStatus(status) {
        return status.charAt(0).toUpperCase() + status.slice(1);
    }

    getSeverityClass(severity) {
        const classes = {
            'low': 'info',
            'medium': 'warning',
            'high': 'error',
            'critical': 'error'
        };
        return classes[severity] || 'gray';
    }

    formatSeverity(severity) {
        return severity.charAt(0).toUpperCase() + severity.slice(1);
    }

    getIncidentStatusClass(status) {
        const classes = {
            'under_review': 'warning',
            'investigating': 'info',
            'resolved': 'success',
            'closed': 'gray'
        };
        return classes[status] || 'gray';
    }

    formatIncidentStatus(status) {
        return status.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-AU', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    }
}

// Initialize HR module when DOM is loaded
let hrModule;
document.addEventListener('DOMContentLoaded', () => {
    hrModule = new HRModule();
});
