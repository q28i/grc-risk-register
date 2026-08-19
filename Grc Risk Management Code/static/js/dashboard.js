/**
 * GRC Risk Register - Dashboard Controller
 * Manages KPI summary metrics, 3x3 Risk Heatmap, and Severity Distributions with explicit loading states.
 */

const DashboardController = {
  /**
   * Puts all dashboard dynamic elements into an active loading state.
   */
  setLoadingState() {
    // 1. KPI counters
    const kpiIds = ['kpi-val-assets', 'kpi-val-risks', 'kpi-val-open', 'kpi-val-high'];
    kpiIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.innerHTML = '<span class="loading-placeholder">--</span>';
        el.classList.add('loading-fade');
      }
    });

    // 2. 3x3 Risk Heatmap
    const matrixGrid = document.getElementById('dashboard-heatmap-grid');
    if (matrixGrid) {
      matrixGrid.innerHTML = Array(9).fill(0).map(() => `
        <div class="heatmap-cell cell-loading">
          <span class="cell-score-lbl">Score --</span>
          <span class="cell-count"><span class="spinner-sm"></span></span>
        </div>
      `).join('');
    }

    // 3. Severity Distribution Bars
    const statHigh = document.getElementById('stat-count-high');
    const statMed = document.getElementById('stat-count-medium');
    const statLow = document.getElementById('stat-count-low');
    const barHigh = document.getElementById('bar-fill-high');
    const barMed = document.getElementById('bar-fill-medium');
    const barLow = document.getElementById('bar-fill-low');

    if (statHigh) statHigh.textContent = 'Loading...';
    if (statMed) statMed.textContent = 'Loading...';
    if (statLow) statLow.textContent = 'Loading...';
    if (barHigh) barHigh.style.width = '0%';
    if (barMed) barMed.style.width = '0%';
    if (barLow) barLow.style.width = '0%';

    // Status summary chips
    ['chip-count-open', 'chip-count-progress', 'chip-count-treated', 'chip-count-closed'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = '--';
    });

    // 4. Recent Risks Table
    const tbody = document.getElementById('tbody-recent-risks');
    if (tbody) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted"><span class="spinner-sm"></span> Loading dashboard risks...</td></tr>';
    }
  },

  /**
   * Fetches and renders dashboard metrics with visual loading transitions.
   */
  async loadDashboard(showLoading = true) {
    const btnRefresh = document.getElementById('btn-refresh-dashboard');
    if (btnRefresh) {
      const allowed = App.isActionAllowed('dashboard_refresh');
      btnRefresh.disabled = !allowed;
      btnRefresh.title = allowed ? 'Refresh Dashboard Data' : 'Feature currently under development';
    }

    if (showLoading) {
      this.setLoadingState();
    }

    try {
      const metrics = await ApiClient.get('/api/dashboard');
      if (!metrics) return;

      this.renderKPIs(metrics.summary);
      this.renderHeatmap(metrics.heatmap);
      this.renderDistributions(metrics.level_distribution, metrics.status_distribution, metrics.summary.total_risks);
      this.renderRecentRisks(metrics.recent_risks);
    } catch (err) {
      console.error('[Dashboard] Error loading metrics:', err);
      const tbody = document.getElementById('tbody-recent-risks');
      if (tbody) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Unable to load dashboard data.</td></tr>';
      }
      throw err;
    }
  },

  /**
   * Updates top 4 KPI summary cards.
   */
  renderKPIs(summary) {
    if (!summary) return;

    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) {
        el.textContent = val !== undefined ? val : 0;
        el.classList.remove('loading-fade');
      }
    };

    setVal('kpi-val-assets', summary.total_assets);
    setVal('kpi-val-risks', summary.total_risks);
    setVal('kpi-val-open', summary.open_risks);
    setVal('kpi-val-high', summary.high_risks);
  },

  /**
   * Renders the interactive 3x3 Qualitative Risk Heatmap.
   */
  renderHeatmap(grid) {
    const container = document.getElementById('dashboard-heatmap-grid');
    if (!container || !grid) return;

    container.innerHTML = '';

    const canViewMatrix = App.isActionAllowed('dashboard_matrix_view');

    // grid is 3 rows (Likelihood 3 down to 1), each row has 3 columns (Impact 1 to 3)
    grid.forEach(row => {
      row.forEach(cell => {
        const cellEl = document.createElement('div');
        let levelClass = 'cell-low';
        if (cell.level === 'Medium') levelClass = 'cell-medium';
        if (cell.level === 'High') levelClass = 'cell-high';

        cellEl.className = `heatmap-cell ${levelClass}`;
        cellEl.title = `Likelihood: ${cell.likelihood}, Impact: ${cell.impact} -> Score: ${cell.score} (${cell.level} Risk)`;
        
        cellEl.innerHTML = `
          <span class="cell-score-lbl">Score ${cell.score}</span>
          <span class="cell-count">${canViewMatrix ? cell.count : '--'}</span>
        `;

        if (canViewMatrix) {
          // Click cell to jump to Risk Register filtered by level
          cellEl.addEventListener('click', () => {
            App.navigateTo('risks');
            const levelFilter = document.getElementById('risk-level-filter');
            if (levelFilter) {
              levelFilter.value = cell.level;
              RiskController.loadRisks();
            }
          });
        } else {
          cellEl.style.cursor = 'default';
          cellEl.style.opacity = '0.5';
        }

        container.appendChild(cellEl);
      });
    });
  },

  /**
   * Renders severity progress bars and status summary chips.
   */
  renderDistributions(levels, statuses, totalRisks) {
    const canViewDist = App.isActionAllowed('dashboard_distribution_view');
    const total = totalRisks || 0;

    // High Risk
    const highCount = (levels && levels.High) || 0;
    const highPct = (total > 0 && canViewDist) ? Math.round((highCount / total) * 100) : 0;
    const statHigh = document.getElementById('stat-count-high');
    const barHigh = document.getElementById('bar-fill-high');
    if (statHigh) statHigh.textContent = canViewDist ? `${highCount} (${highPct}%)` : '--';
    if (barHigh) barHigh.style.width = `${highPct}%`;

    // Medium Risk
    const medCount = (levels && levels.Medium) || 0;
    const medPct = (total > 0 && canViewDist) ? Math.round((medCount / total) * 100) : 0;
    const statMed = document.getElementById('stat-count-medium');
    const barMed = document.getElementById('bar-fill-medium');
    if (statMed) statMed.textContent = canViewDist ? `${medCount} (${medPct}%)` : '--';
    if (barMed) barMed.style.width = `${medPct}%`;

    // Low Risk
    const lowCount = (levels && levels.Low) || 0;
    const lowPct = (total > 0 && canViewDist) ? Math.round((lowCount / total) * 100) : 0;
    const statLow = document.getElementById('stat-count-low');
    const barLow = document.getElementById('bar-fill-low');
    if (statLow) statLow.textContent = canViewDist ? `${lowCount} (${lowPct}%)` : '--';
    if (barLow) barLow.style.width = `${lowPct}%`;

    // Status Chips
    if (statuses) {
      const setChip = (id, key) => {
        const el = document.getElementById(id);
        if (el) el.textContent = canViewDist ? (statuses[key] || 0) : '--';
      };
      setChip('chip-count-open', 'Open');
      setChip('chip-count-progress', 'In Progress');
      setChip('chip-count-treated', 'Treated');
      setChip('chip-count-closed', 'Closed');
    }
  },

  /**
   * Populates the 5 most recent risks table on the dashboard.
   */
  renderRecentRisks(risks) {
    const tbody = document.getElementById('tbody-recent-risks');
    if (!tbody) return;

    const canViewRecent = App.isActionAllowed('dashboard_recent_view');

    if (!canViewRecent) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted" style="padding: 16px;">Feature currently under development.</td></tr>';
      return;
    }

    if (!risks || risks.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No cybersecurity risks registered yet.</td></tr>';
      return;
    }

    tbody.innerHTML = risks.map(r => {
      const levelClass = r.level === 'High' ? 'badge-high' : (r.level === 'Medium' ? 'badge-medium' : 'badge-low');
      const statusClass = 'status-' + r.status.toLowerCase().replace(/\s+/g, '-');

      return `
        <tr>
          <td class="font-mono font-bold">${r.risk_id}</td>
          <td><strong>${this.escapeHtml(r.title)}</strong></td>
          <td><span class="badge-type">${this.escapeHtml(r.asset_name)}</span></td>
          <td class="font-mono">${r.score}</td>
          <td><span class="${levelClass}">${r.level}</span></td>
          <td><span class="badge-status ${statusClass}">${r.status}</span></td>
          <td>${this.escapeHtml(r.owner)}</td>
        </tr>
      `;
    }).join('');
  },

  escapeHtml(str) {
    if (!str) return '';
    return str.toString().replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    })[m]);
  }
};
