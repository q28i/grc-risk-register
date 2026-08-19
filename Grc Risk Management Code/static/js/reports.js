/**
 * GRC Risk Register - Reports & Export Controller
 * Generates executive printable reports and downloadable CSV exports with visual loading states.
 */

const ReportController = {
  currentRisks: [],

  /**
   * Puts report dynamic elements into loading state.
   */
  setLoadingState() {
    ['rep-val-assets', 'rep-val-risks', 'rep-val-high', 'rep-val-open'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = '<span class="loading-placeholder">--</span>';
    });

    const tbody = document.getElementById('tbody-report-data');
    if (tbody) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted"><span class="spinner-sm"></span> Generating report dataset...</td></tr>';
    }
  },

  /**
   * Loads report data and populates summary counters and report table.
   */
  async loadReports() {
    this.setLoadingState();
    this.updateActionButtons();

    try {
      const [risks, dashboard] = await Promise.all([
        ApiClient.get('/api/risks?active_only=true'),
        ApiClient.get('/api/dashboard')
      ]);

      this.currentRisks = risks || [];

      // Update Report Header Metadata
      const now = new Date();
      const dateEl = document.getElementById('report-meta-date');
      const authorEl = document.getElementById('report-meta-user');
      if (dateEl) dateEl.textContent = now.toLocaleDateString() + ' ' + now.toLocaleTimeString();
      if (authorEl) authorEl.textContent = App.currentUser ? `${App.currentUser.full_name} (${App.currentUser.role})` : 'System Analyst';

      // Update Report Summary KPI counts
      if (dashboard && dashboard.summary) {
        const aEl = document.getElementById('rep-val-assets');
        const rEl = document.getElementById('rep-val-risks');
        const hEl = document.getElementById('rep-val-high');
        const oEl = document.getElementById('rep-val-open');
        if (aEl) aEl.textContent = dashboard.summary.total_assets || 0;
        if (rEl) rEl.textContent = dashboard.summary.total_risks || 0;
        if (hEl) hEl.textContent = dashboard.summary.high_risks || 0;
        if (oEl) oEl.textContent = dashboard.summary.open_risks || 0;
      }

      this.renderReportTable(this.currentRisks);
      this.updateActionButtons();
    } catch (err) {
      console.error('[Reports] Error loading report data:', err);
      const tbody = document.getElementById('tbody-report-data');
      if (tbody) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Unable to load report data.</td></tr>';
      }
    }
  },

  /**
   * Updates disabled states for export/print based on feature controls.
   */
  updateActionButtons() {
    const btnExport = document.getElementById('btn-export-csv');
    const btnPrint = document.getElementById('btn-print-report');

    if (btnExport) {
      const allowed = App.isActionAllowed('report_export_csv');
      btnExport.disabled = !allowed;
      btnExport.title = allowed ? 'Export Risk Register to CSV' : 'Feature currently under development';
    }

    if (btnPrint) {
      const allowed = App.isActionAllowed('report_print');
      btnPrint.disabled = !allowed;
      btnPrint.title = allowed ? 'Print Risk Report' : 'Feature currently under development';
    }
  },

  /**
   * Renders the printable report table rows.
   */
  renderReportTable(risks) {
    const tbody = document.getElementById('tbody-report-data');
    if (!tbody) return;

    if (!App.isActionAllowed('report_view')) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted" style="padding: 24px;">Feature currently under development.</td></tr>';
      return;
    }

    if (!risks || risks.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No active risk records available.</td></tr>';
      return;
    }

    tbody.innerHTML = risks.map(r => {
      const levelClass = r.level === 'High' ? 'badge-high' : (r.level === 'Medium' ? 'badge-medium' : 'badge-low');
      const statusClass = 'status-' + r.status.toLowerCase().replace(/\s+/g, '-');

      return `
        <tr>
          <td class="font-mono font-bold">${r.risk_id}</td>
          <td><strong>${App.escapeHtml(r.title)}</strong><br><small class="text-muted">${App.escapeHtml(r.consequence)}</small></td>
          <td>${App.escapeHtml(r.asset_name)}</td>
          <td class="text-center font-mono font-bold">${r.score}</td>
          <td><span class="${levelClass}">${r.level}</span></td>
          <td><span class="badge-status ${statusClass}">${r.status}</span></td>
          <td>${App.escapeHtml(r.owner)}</td>
        </tr>
      `;
    }).join('');
  },

  /**
   * Exports current risk records to a clean CSV file.
   */
  exportCSV() {
    if (!App.isActionAllowed('report_export_csv')) {
      App.showToast('This feature is currently under development.', 'info');
      return;
    }

    if (!this.currentRisks || this.currentRisks.length === 0) {
      App.showToast('No risk data available to export.', 'error');
      return;
    }

    const headers = [
      'Risk ID',
      'Title',
      'Consequence',
      'Linked Asset ID',
      'Linked Asset Name',
      'Likelihood (1-3)',
      'Impact (1-3)',
      'Calculated Score',
      'Risk Level',
      'Status',
      'Owner',
      'Remediation Notes',
      'Created Date'
    ];

    const rows = this.currentRisks.map(r => [
      r.risk_id,
      `"${(r.title || '').replace(/"/g, '""')}"`,
      `"${(r.consequence || '').replace(/"/g, '""')}"`,
      r.asset_id_code || '',
      `"${(r.asset_name || '').replace(/"/g, '""')}"`,
      r.likelihood,
      r.impact,
      r.score,
      r.level,
      r.status,
      `"${(r.owner || '').replace(/"/g, '""')}"`,
      `"${(r.notes || '').replace(/"/g, '""')}"`,
      r.created_at || ''
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\r\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `GRC_Risk_Register_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    App.showToast('Risk Register CSV exported successfully.', 'success');
  },

  /**
   * Invokes browser native print dialog for the report.
   */
  printReport() {
    if (!App.isActionAllowed('report_print')) {
      App.showToast('This feature is currently under development.', 'info');
      return;
    }
    window.print();
  }
};
