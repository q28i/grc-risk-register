/**
 * GRC Risk Register - Core Application Router & Controllers
 * Pure Vanilla JavaScript SPA Controller with zero external library dependencies.
 */

// ============================================================================
// 1. API CLIENT WRAPPER
// ============================================================================
const ApiClient = {
  getToken() {
    return localStorage.getItem('grc_session_token');
  },

  setToken(token) {
    if (token) {
      localStorage.setItem('grc_session_token', token);
    } else {
      localStorage.removeItem('grc_session_token');
    }
  },

  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...(options.headers || {})
    };

    try {
      const response = await fetch(endpoint, {
        ...options,
        headers
      });

      const data = await response.json().catch(() => ({}));

      if (response.status === 401) {
        App.handleUnauthorized();
        throw new Error(data.message || data.error || 'Authentication required.');
      }

      if (!response.ok) {
        throw new Error(data.message || data.error || `Request failed with status ${response.status}`);
      }

      return data;
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err.message);
      throw err;
    }
  },

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  post(endpoint, body) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body)
    });
  },

  put(endpoint, body) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body)
    });
  }
};

// ============================================================================
// 2. MAIN APPLICATION CONTROLLER
// ============================================================================
const App = {
  currentUser: null,
  currentTab: 'dashboard',
  featureControls: {},
  rawControls: [],

  async init() {
    this.bindGlobalEvents();
    await this.fetchFeatureControls();
    await this.checkAuthentication();
  },

  async fetchFeatureControls() {
    try {
      const res = await ApiClient.get('/api/feature-controls');
      if (res) {
        this.featureControls = res.controls_dict || {};
        this.rawControls = res.controls || [];
      }
    } catch (err) {
      console.warn('[App] Could not fetch feature controls:', err);
    }
  },

  isActionAllowed(featureKey) {
    if (!this.currentUser) return false;
    // Administrators always have 100% unrestricted access
    if (this.currentUser.role === 'admin') return true;

    // Risk Analyst has standard operator privileges
    if (this.currentUser.role === 'analyst') {
      const adminOnlyKeys = ['admin_fc_view', 'admin_fc_modify', 'admin_users_view', 'audit_view'];
      return !adminOnlyKeys.includes(featureKey);
    }

    // Demo User is strictly governed by persisted SQLite feature controls
    if (this.currentUser.role === 'demo') {
      return Boolean(this.featureControls[featureKey]);
    }

    return false;
  },

  bindGlobalEvents() {
    // Navigation tab switching
    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        this.navigateTo(tab);
      });
    });

    // Dashboard refresh button
    const btnRefresh = document.getElementById('btn-refresh-dashboard');
    if (btnRefresh) {
      btnRefresh.addEventListener('click', () => this.refreshDashboardWithFeedback());
    }

    const btnGotoRisks = document.getElementById('btn-goto-risks');
    if (btnGotoRisks) {
      btnGotoRisks.addEventListener('click', () => this.navigateTo('risks'));
    }

    // Reports export & print
    const btnExport = document.getElementById('btn-export-csv');
    if (btnExport) {
      btnExport.addEventListener('click', () => ReportController.exportCSV());
    }

    const btnPrint = document.getElementById('btn-print-report');
    if (btnPrint) {
      btnPrint.addEventListener('click', () => ReportController.printReport());
    }

    // Logout
    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
      btnLogout.addEventListener('click', () => this.logout());
    }

    // Login Form
    const formLogin = document.getElementById('form-login');
    if (formLogin) {
      formLogin.addEventListener('submit', (e) => this.handleLogin(e));
    }

    // Initialize Sub-Controllers
    AssetController.init();
    RiskController.init();
    ProfileController.init();
  },

  async refreshDashboardWithFeedback() {
    if (!this.isActionAllowed('dashboard_refresh')) {
      this.showToast('This feature is currently under development.', 'info');
      return;
    }

    const btn = document.getElementById('btn-refresh-dashboard');
    if (!btn) return;

    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-sm"></span> Refreshing...`;

    try {
      await DashboardController.loadDashboard(true);
      this.showToast('Dashboard metrics refreshed.', 'info');
    } catch (err) {
      this.showToast('Failed to refresh dashboard.', 'error');
    } finally {
      setTimeout(() => {
        btn.innerHTML = originalHTML;
        btn.disabled = !this.isActionAllowed('dashboard_refresh');
      }, 400);
    }
  },

  async checkAuthentication() {
    const token = ApiClient.getToken();
    if (!token) {
      this.showLoginView();
      return;
    }

    try {
      const res = await ApiClient.get('/api/auth/me');
      if (res && res.authenticated) {
        this.currentUser = res.user;
        this.updateUserUI(res.user);
        this.showAppView();
        this.navigateTo(this.currentTab);
      } else {
        this.showLoginView();
      }
    } catch {
      this.showLoginView();
    }
  },

  async handleLogin(e) {
    e.preventDefault();
    const errorEl = document.getElementById('login-error-msg');
    errorEl.style.display = 'none';

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    const submitBtn = document.getElementById('btn-submit-login');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner-sm"></span> Signing in...`;

    try {
      const res = await ApiClient.post('/api/auth/login', { username, password });
      if (res && res.token) {
        ApiClient.setToken(res.token);
        this.currentUser = res.user;
        await this.fetchFeatureControls();
        this.updateUserUI(res.user);
        this.showAppView();
        this.showToast(`Welcome, ${res.user.full_name}!`, 'success');
        this.navigateTo('dashboard');
      }
    } catch (err) {
      errorEl.textContent = err.message || 'Login failed. Invalid username or password.';
      errorEl.style.display = 'block';
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Sign In';
    }
  },

  async logout() {
    try {
      await ApiClient.post('/api/auth/logout', {});
    } catch (err) {
      console.warn('Logout notification error:', err);
    }
    ApiClient.setToken(null);
    this.currentUser = null;
    this.showLoginView();
    this.showToast('You have been logged out.', 'info');
  },

  handleUnauthorized() {
    ApiClient.setToken(null);
    this.currentUser = null;
    this.showLoginView();
  },

  showLoginView() {
    const unauth = document.getElementById('unauthenticated-view');
    const auth = document.getElementById('authenticated-view');
    if (unauth) unauth.style.display = 'flex';
    if (auth) auth.style.display = 'none';
    const pwdInput = document.getElementById('login-password');
    if (pwdInput) pwdInput.value = '';
  },

  showAppView() {
    const unauth = document.getElementById('unauthenticated-view');
    const auth = document.getElementById('authenticated-view');
    if (unauth) unauth.style.display = 'none';
    if (auth) auth.style.display = 'block';
  },

  updateUserUI(user) {
    if (!user) return;
    const nameEl = document.getElementById('current-user-name');
    const roleEl = document.getElementById('current-user-role');
    const noticeEl = document.getElementById('dev-notice-banner');

    if (nameEl) nameEl.textContent = user.full_name || user.username;
    if (roleEl) {
      if (user.role === 'admin') {
        roleEl.textContent = 'Administrator';
        roleEl.className = 'user-role-badge role-admin';
      } else if (user.role === 'demo') {
        roleEl.textContent = 'Demo User';
        roleEl.className = 'user-role-badge role-demo';
      } else {
        roleEl.textContent = 'Risk Analyst';
        roleEl.className = 'user-role-badge';
      }
    }

    if (noticeEl) {
      // Unobtrusive development notice: displayed when features are governed, hidden for full admin
      noticeEl.style.display = (user.role === 'admin') ? 'none' : 'flex';
    }
  },

  navigateTo(tabId) {
    this.currentTab = tabId;

    // Update nav button states
    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabId);
    });

    // Update tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
      pane.classList.remove('active');
    });

    const activePane = document.getElementById(`pane-${tabId}`);
    if (activePane) {
      activePane.classList.add('active');
    }

    // Trigger tab-specific data load
    if (tabId === 'dashboard') {
      DashboardController.loadDashboard(false);
    } else if (tabId === 'assets') {
      AssetController.loadAssets();
    } else if (tabId === 'risks') {
      RiskController.loadRisks();
    } else if (tabId === 'reports') {
      ReportController.loadReports();
    } else if (tabId === 'profile') {
      ProfileController.loadProfile();
    }
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${this.escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  },

  escapeHtml(str) {
    if (!str) return '';
    return str.toString().replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    })[m]);
  }
};

// ============================================================================
// 3. ASSET CONTROLLER
// ============================================================================
const AssetController = {
  assets: [],

  init() {
    // Open Add Modal
    const btnOpen = document.getElementById('btn-open-add-asset-modal');
    if (btnOpen) {
      btnOpen.addEventListener('click', () => this.openAddModal());
    }

    // Modal Close buttons
    const btnClose = document.getElementById('btn-close-asset-modal');
    const btnCancel = document.getElementById('btn-cancel-asset');
    if (btnClose) btnClose.addEventListener('click', () => this.closeModal());
    if (btnCancel) btnCancel.addEventListener('click', () => this.closeModal());

    // Form Submit
    const formAsset = document.getElementById('form-asset');
    if (formAsset) {
      formAsset.addEventListener('submit', (e) => this.saveAsset(e));
    }

    // Filters
    const inputSearch = document.getElementById('asset-search-input');
    if (inputSearch) {
      inputSearch.addEventListener('input', () => this.loadAssets());
    }

    const selectType = document.getElementById('asset-type-filter');
    if (selectType) {
      selectType.addEventListener('change', () => this.loadAssets());
    }

    const chkArchived = document.getElementById('asset-show-archived');
    if (chkArchived) {
      chkArchived.addEventListener('change', () => this.loadAssets());
    }
  },

  async loadAssets() {
    const btnOpen = document.getElementById('btn-open-add-asset-modal');
    if (btnOpen) {
      const allowed = App.isActionAllowed('asset_add');
      btnOpen.disabled = !allowed;
      btnOpen.title = allowed ? 'Register New Asset' : 'Feature currently under development';
    }

    const inputSearch = document.getElementById('asset-search-input');
    if (inputSearch) {
      const allowed = App.isActionAllowed('asset_search');
      inputSearch.disabled = !allowed;
      inputSearch.placeholder = allowed ? 'Search assets by name, ID, or owner...' : 'Search is currently unavailable';
    }

    const selectType = document.getElementById('asset-type-filter');
    if (selectType) {
      const allowed = App.isActionAllowed('asset_filter');
      selectType.disabled = !allowed;
    }

    const chkArchived = document.getElementById('asset-show-archived');
    if (chkArchived) {
      const allowed = App.isActionAllowed('asset_show_archived');
      chkArchived.disabled = !allowed;
    }

    const tbody = document.getElementById('tbody-assets');
    if (tbody) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted"><span class="spinner-sm"></span> Loading organizational assets...</td></tr>';
    }

    const search = (inputSearch && !inputSearch.disabled) ? inputSearch.value.trim() : '';
    const type = (selectType && !selectType.disabled) ? selectType.value : '';
    const showArchived = (chkArchived && !chkArchived.disabled) ? chkArchived.checked : false;

    let url = `/api/assets?active_only=${!showArchived}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (type) url += `&type=${encodeURIComponent(type)}`;

    try {
      const data = await ApiClient.get(url);
      this.assets = data || [];
      this.renderTable(this.assets);
    } catch (err) {
      console.error('[Assets] Error loading assets:', err);
      if (tbody) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-danger">Error loading assets.</td></tr>';
      }
    }
  },

  renderTable(assets) {
    const tbody = document.getElementById('tbody-assets');
    if (!tbody) return;

    if (!App.isActionAllowed('asset_view')) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted" style="padding: 24px;">Feature currently under development.</td></tr>';
      return;
    }

    if (!assets || assets.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No organizational assets found matching criteria.</td></tr>';
      return;
    }

    const isAdmin = App.currentUser && App.currentUser.role === 'admin';
    const canEdit = App.isActionAllowed('asset_edit');
    const canArchive = App.isActionAllowed('asset_archive');

    tbody.innerHTML = assets.map(a => {
      const isArchived = a.active === 0;
      const rowClass = isArchived ? 'row-archived' : '';
      const impClass = a.importance === 'High' ? 'badge-high' : (a.importance === 'Medium' ? 'badge-medium' : 'badge-low');

      return `
        <tr class="${rowClass}">
          <td class="font-mono font-bold">${a.asset_id}</td>
          <td>
            <strong>${App.escapeHtml(a.name)}</strong>
            ${a.description ? `<br><small class="text-muted">${App.escapeHtml(a.description)}</small>` : ''}
          </td>
          <td><span class="badge-type">${a.type}</span></td>
          <td><span class="${impClass}">${a.importance}</span></td>
          <td>${App.escapeHtml(a.owner)}</td>
          <td class="font-mono">${a.risk_count || 0}</td>
          <td>
            ${isArchived ? '<span class="badge-status status-closed">Archived</span>' : '<span class="badge-status status-treated">Active</span>'}
          </td>
          <td class="text-right">
            <div class="table-actions">
              ${!isArchived ? `
                <button class="btn-action" ${canEdit ? `onclick="AssetController.openEditModal(${a.id})"` : 'disabled title="Feature currently under development"'}>Edit</button>
                <button class="btn-action btn-action-danger" ${canArchive ? `onclick="AssetController.archiveAsset(${a.id}, '${App.escapeHtml(a.name)}')"` : 'disabled title="Feature currently under development"'}>Archive</button>
              ` : `
                ${isAdmin ? `<button class="btn-action" onclick="AssetController.unarchiveAsset(${a.id})">Restore</button>` : '<span class="text-muted text-sm">Archived</span>'}
              `}
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },

  openAddModal() {
    if (!App.isActionAllowed('asset_add')) {
      App.showToast('This feature is currently under development.', 'info');
      return;
    }
    document.getElementById('asset-modal-title').textContent = 'Register New Organizational Asset';
    document.getElementById('asset-form-id').value = '';
    document.getElementById('form-asset').reset();
    document.getElementById('asset-error-msg').style.display = 'none';
    document.getElementById('modal-asset').classList.add('active');
  },

  openEditModal(id) {
    if (!App.isActionAllowed('asset_edit')) {
      App.showToast('This feature is currently under development.', 'info');
      return;
    }
    const asset = this.assets.find(a => a.id === id);
    if (!asset) return;

    document.getElementById('asset-modal-title').textContent = `Edit Asset: ${asset.asset_id}`;
    document.getElementById('asset-form-id').value = asset.id;
    document.getElementById('asset-form-name').value = asset.name;
    document.getElementById('asset-form-type').value = asset.type;
    document.getElementById('asset-form-importance').value = asset.importance;
    document.getElementById('asset-form-owner').value = asset.owner;
    document.getElementById('asset-form-description').value = asset.description || '';
    document.getElementById('asset-error-msg').style.display = 'none';
    document.getElementById('modal-asset').classList.add('active');
  },

  closeModal() {
    document.getElementById('modal-asset').classList.remove('active');
  },

  async saveAsset(e) {
    e.preventDefault();
    const errorEl = document.getElementById('asset-error-msg');
    errorEl.style.display = 'none';

    const id = document.getElementById('asset-form-id').value;
    const isUpdate = Boolean(id);

    if (isUpdate && !App.isActionAllowed('asset_edit')) {
      errorEl.textContent = 'This feature is currently under development.';
      errorEl.style.display = 'block';
      return;
    }
    if (!isUpdate && !App.isActionAllowed('asset_add')) {
      errorEl.textContent = 'This feature is currently under development.';
      errorEl.style.display = 'block';
      return;
    }

    const payload = {
      name: document.getElementById('asset-form-name').value.trim(),
      type: document.getElementById('asset-form-type').value,
      importance: document.getElementById('asset-form-importance').value,
      owner: document.getElementById('asset-form-owner').value.trim(),
      description: document.getElementById('asset-form-description').value.trim()
    };

    try {
      if (id) {
        await ApiClient.put(`/api/assets/${id}`, payload);
        App.showToast('Asset updated successfully.', 'success');
      } else {
        await ApiClient.post('/api/assets', payload);
        App.showToast('Asset registered successfully.', 'success');
      }
      this.closeModal();
      this.loadAssets();
    } catch (err) {
      errorEl.textContent = err.message || 'Error saving asset.';
      errorEl.style.display = 'block';
    }
  },

  async archiveAsset(id, name) {
    if (!App.isActionAllowed('asset_archive')) {
      App.showToast('This feature is currently under development.', 'info');
      return;
    }
    if (!confirm(`Are you sure you want to safely archive asset "${name}"?`)) return;
    try {
      await ApiClient.post(`/api/assets/${id}/archive`, {});
      App.showToast(`Asset "${name}" archived.`, 'info');
      this.loadAssets();
    } catch (err) {
      App.showToast(err.message || 'Error archiving asset.', 'error');
    }
  },

  async unarchiveAsset(id) {
    try {
      await ApiClient.post(`/api/assets/${id}/unarchive`, {});
      App.showToast('Asset restored to active inventory.', 'success');
      this.loadAssets();
    } catch (err) {
      App.showToast(err.message || 'Error restoring asset.', 'error');
    }
  }
};

// ============================================================================
// 4. RISK CONTROLLER (WITH DYNAMIC CALCULATION PREVIEW)
// ============================================================================
const RiskController = {
  risks: [],

  init() {
    // Open Add Modal
    const btnOpen = document.getElementById('btn-open-add-risk-modal');
    if (btnOpen) {
      btnOpen.addEventListener('click', () => this.openAddModal());
    }

    // Modal Close
    const btnClose = document.getElementById('btn-close-risk-modal');
    const btnCancel = document.getElementById('btn-cancel-risk');
    if (btnClose) btnClose.addEventListener('click', () => this.closeModal());
    if (btnCancel) btnCancel.addEventListener('click', () => this.closeModal());

    // Form Submit
    const formRisk = document.getElementById('form-risk');
    if (formRisk) {
      formRisk.addEventListener('submit', (e) => this.saveRisk(e));
    }

    // Dynamic Risk Score Calculation Listeners
    const selectLikelihood = document.getElementById('risk-form-likelihood');
    const selectImpact = document.getElementById('risk-form-impact');
    if (selectLikelihood && selectImpact) {
      selectLikelihood.addEventListener('change', () => this.updateCalculationPreview());
      selectImpact.addEventListener('change', () => this.updateCalculationPreview());
    }

    // Filters
    const inputSearch = document.getElementById('risk-search-input');
    if (inputSearch) {
      inputSearch.addEventListener('input', () => this.loadRisks());
    }

    const selectLevel = document.getElementById('risk-level-filter');
    if (selectLevel) {
      selectLevel.addEventListener('change', () => this.loadRisks());
    }

    const selectStatus = document.getElementById('risk-status-filter');
    if (selectStatus) {
      selectStatus.addEventListener('change', () => this.loadRisks());
    }

    const chkArchived = document.getElementById('risk-show-archived');
    if (chkArchived) {
      chkArchived.addEventListener('change', () => this.loadRisks());
    }
  },

  async loadRisks() {
    const btnOpen = document.getElementById('btn-open-add-risk-modal');
    if (btnOpen) {
      const allowed = App.isActionAllowed('risk_add');
      btnOpen.disabled = !allowed;
      btnOpen.title = allowed ? 'Assess New Risk' : 'Feature currently under development';
    }

    const inputSearch = document.getElementById('risk-search-input');
    if (inputSearch) {
      const allowed = App.isActionAllowed('risk_search');
      inputSearch.disabled = !allowed;
      inputSearch.placeholder = allowed ? 'Search risks by title, ID, or owner...' : 'Search is currently unavailable';
    }

    const selectLevel = document.getElementById('risk-level-filter');
    const selectStatus = document.getElementById('risk-status-filter');
    if (selectLevel) selectLevel.disabled = !App.isActionAllowed('risk_filter');
    if (selectStatus) selectStatus.disabled = !App.isActionAllowed('risk_filter');

    const chkArchived = document.getElementById('risk-show-archived');
    if (chkArchived) chkArchived.disabled = !App.isActionAllowed('risk_show_archived');

    const tbody = document.getElementById('tbody-risks');
    if (tbody) {
      tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted"><span class="spinner-sm"></span> Loading risk register...</td></tr>';
    }

    const search = (inputSearch && !inputSearch.disabled) ? inputSearch.value.trim() : '';
    const level = (selectLevel && !selectLevel.disabled) ? selectLevel.value : '';
    const status = (selectStatus && !selectStatus.disabled) ? selectStatus.value : '';
    const showArchived = (chkArchived && !chkArchived.disabled) ? chkArchived.checked : false;

    let url = `/api/risks?active_only=${!showArchived}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (level) url += `&level=${encodeURIComponent(level)}`;
    if (status) url += `&status=${encodeURIComponent(status)}`;

    try {
      const data = await ApiClient.get(url);
      this.risks = data || [];
      this.renderTable(this.risks);
    } catch (err) {
      console.error('[Risks] Error loading risks:', err);
      if (tbody) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center text-danger">Error loading risk register.</td></tr>';
      }
    }
  },

  renderTable(risks) {
    const tbody = document.getElementById('tbody-risks');
    if (!tbody) return;

    if (!App.isActionAllowed('risk_view')) {
      tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted" style="padding: 24px;">Feature currently under development.</td></tr>';
      return;
    }

    if (!risks || risks.length === 0) {
      tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted">No cybersecurity risks found matching criteria.</td></tr>';
      return;
    }

    const isAdmin = App.currentUser && App.currentUser.role === 'admin';
    const canEdit = App.isActionAllowed('risk_edit');
    const canArchive = App.isActionAllowed('risk_archive');
    const canViewDetails = App.isActionAllowed('risk_view_details');

    tbody.innerHTML = risks.map(r => {
      const isArchived = r.active === 0;
      const rowClass = isArchived ? 'row-archived' : '';
      const levelClass = r.level === 'High' ? 'badge-high' : (r.level === 'Medium' ? 'badge-medium' : 'badge-low');
      const statusClass = 'status-' + r.status.toLowerCase().replace(/\s+/g, '-');

      return `
        <tr class="${rowClass}">
          <td class="font-mono font-bold">${r.risk_id}</td>
          <td>
            <strong>${App.escapeHtml(r.title)}</strong>
            ${canViewDetails && r.consequence ? `<br><small class="text-muted">${App.escapeHtml(r.consequence)}</small>` : ''}
          </td>
          <td><span class="badge-type">${App.escapeHtml(r.asset_name)}</span></td>
          <td class="text-center font-mono">${r.likelihood}</td>
          <td class="text-center font-mono">${r.impact}</td>
          <td class="text-center font-mono font-bold">${r.score}</td>
          <td><span class="${levelClass}">${r.level}</span></td>
          <td><span class="badge-status ${statusClass}">${r.status}</span></td>
          <td>${App.escapeHtml(r.owner)}</td>
          <td class="text-right">
            <div class="table-actions">
              ${!isArchived ? `
                <button class="btn-action" ${canEdit ? `onclick="RiskController.openEditModal(${r.id})"` : 'disabled title="Feature currently under development"'}>Edit</button>
                <button class="btn-action btn-action-danger" ${canArchive ? `onclick="RiskController.archiveRisk(${r.id}, '${App.escapeHtml(r.title)}')"` : 'disabled title="Feature currently under development"'}>Archive</button>
              ` : `
                ${isAdmin ? `<button class="btn-action" onclick="RiskController.unarchiveRisk(${r.id})">Restore</button>` : '<span class="text-muted text-sm">Archived</span>'}
              `}
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },

  updateCalculationPreview() {
    const l = parseInt(document.getElementById('risk-form-likelihood').value, 10) || 1;
    const i = parseInt(document.getElementById('risk-form-impact').value, 10) || 1;
    const score = l * i;

    let level = 'Low';
    let badgeClass = 'badge-low';
    if (score >= 6) {
      level = 'High';
      badgeClass = 'badge-high';
    } else if (score >= 3) {
      level = 'Medium';
      badgeClass = 'badge-medium';
    }

    const scoreEl = document.getElementById('preview-risk-score');
    const levelEl = document.getElementById('preview-risk-level');

    if (scoreEl) scoreEl.textContent = score;
    if (levelEl) {
      levelEl.textContent = level;
      levelEl.className = `result-badge ${badgeClass}`;
    }
  },

  async populateAssetDropdown(selectedAssetId = null) {
    const select = document.getElementById('risk-form-asset');
    if (!select) return;

    try {
      const assets = await ApiClient.get('/api/assets?active_only=true');
      select.innerHTML = '<option value="">-- Select Organizational Asset --</option>';
      (assets || []).forEach(a => {
        const opt = document.createElement('option');
        opt.value = a.id;
        opt.textContent = `[${a.asset_id}] ${a.name} (${a.type})`;
        if (selectedAssetId && a.id === selectedAssetId) {
          opt.selected = true;
        }
        select.appendChild(opt);
      });
    } catch (err) {
      console.error('[Risks] Error loading asset options:', err);
    }
  },

  async openAddModal() {
    if (!App.isActionAllowed('risk_add')) {
      App.showToast('This feature is currently under development.', 'info');
      return;
    }
    document.getElementById('risk-modal-title').textContent = 'Assess New Cybersecurity Risk';
    document.getElementById('risk-form-id').value = '';
    document.getElementById('form-risk').reset();
    document.getElementById('risk-error-msg').style.display = 'none';
    await this.populateAssetDropdown();
    this.updateCalculationPreview();
    document.getElementById('modal-risk').classList.add('active');
  },

  async openEditModal(id) {
    if (!App.isActionAllowed('risk_edit') && !App.isActionAllowed('risk_status_change')) {
      App.showToast('This feature is currently under development.', 'info');
      return;
    }
    const risk = this.risks.find(r => r.id === id);
    if (!risk) return;

    document.getElementById('risk-modal-title').textContent = `Edit Risk Assessment: ${risk.risk_id}`;
    document.getElementById('risk-form-id').value = risk.id;
    document.getElementById('risk-form-title').value = risk.title;
    document.getElementById('risk-form-owner').value = risk.owner;
    document.getElementById('risk-form-likelihood').value = risk.likelihood;
    document.getElementById('risk-form-impact').value = risk.impact;
    document.getElementById('risk-form-consequence').value = risk.consequence;
    document.getElementById('risk-form-status').value = risk.status;
    document.getElementById('risk-form-notes').value = risk.notes || '';
    document.getElementById('risk-form-description').value = risk.description || '';
    document.getElementById('risk-error-msg').style.display = 'none';

    // If only status change is allowed, disable other fields in form
    const canFullEdit = App.isActionAllowed('risk_edit');
    document.getElementById('risk-form-title').disabled = !canFullEdit;
    document.getElementById('risk-form-owner').disabled = !canFullEdit;
    document.getElementById('risk-form-likelihood').disabled = !canFullEdit;
    document.getElementById('risk-form-impact').disabled = !canFullEdit;
    document.getElementById('risk-form-consequence').disabled = !canFullEdit;
    document.getElementById('risk-form-description').disabled = !canFullEdit;

    await this.populateAssetDropdown(risk.asset_id);
    this.updateCalculationPreview();
    document.getElementById('modal-risk').classList.add('active');
  },

  closeModal() {
    document.getElementById('modal-risk').classList.remove('active');
  },

  async saveRisk(e) {
    e.preventDefault();
    const errorEl = document.getElementById('risk-error-msg');
    errorEl.style.display = 'none';

    const id = document.getElementById('risk-form-id').value;
    const isUpdate = Boolean(id);

    if (isUpdate && !App.isActionAllowed('risk_edit') && !App.isActionAllowed('risk_status_change')) {
      errorEl.textContent = 'This feature is currently under development.';
      errorEl.style.display = 'block';
      return;
    }
    if (!isUpdate && !App.isActionAllowed('risk_add')) {
      errorEl.textContent = 'This feature is currently under development.';
      errorEl.style.display = 'block';
      return;
    }

    const payload = {
      title: document.getElementById('risk-form-title').value.trim(),
      asset_id: parseInt(document.getElementById('risk-form-asset').value, 10),
      owner: document.getElementById('risk-form-owner').value.trim(),
      likelihood: parseInt(document.getElementById('risk-form-likelihood').value, 10),
      impact: parseInt(document.getElementById('risk-form-impact').value, 10),
      consequence: document.getElementById('risk-form-consequence').value.trim(),
      status: document.getElementById('risk-form-status').value,
      notes: document.getElementById('risk-form-notes').value.trim(),
      description: document.getElementById('risk-form-description').value.trim()
    };

    if (!payload.asset_id) {
      errorEl.textContent = 'Please select an affected organizational asset.';
      errorEl.style.display = 'block';
      return;
    }

    try {
      if (id) {
        await ApiClient.put(`/api/risks/${id}`, payload);
        App.showToast('Risk assessment updated.', 'success');
      } else {
        await ApiClient.post('/api/risks', payload);
        App.showToast('Cybersecurity risk registered.', 'success');
      }
      this.closeModal();
      this.loadRisks();
    } catch (err) {
      errorEl.textContent = err.message || 'Error saving risk.';
      errorEl.style.display = 'block';
    }
  },

  async archiveRisk(id, title) {
    if (!App.isActionAllowed('risk_archive')) {
      App.showToast('This feature is currently under development.', 'info');
      return;
    }
    if (!confirm(`Are you sure you want to safely archive risk "${title}"?`)) return;
    try {
      await ApiClient.post(`/api/risks/${id}/archive`, {});
      App.showToast(`Risk "${title}" archived.`, 'info');
      this.loadRisks();
    } catch (err) {
      App.showToast(err.message || 'Error archiving risk.', 'error');
    }
  },

  async unarchiveRisk(id) {
    try {
      await ApiClient.post(`/api/risks/${id}/unarchive`, {});
      App.showToast('Risk restored to active register.', 'success');
      this.loadRisks();
    } catch (err) {
      App.showToast(err.message || 'Error restoring risk.', 'error');
    }
  }
};

// ============================================================================
// 5. PROFILE & AUDIT CONTROLLER (WITH DEMO FEATURE CONTROLS FOR ADMIN)
// ============================================================================
const ProfileController = {
  init() {
    const formFC = document.getElementById('form-feature-controls');
    if (formFC) {
      formFC.addEventListener('submit', (e) => this.saveFeatureControls(e));
    }
  },

  async loadProfile() {
    const user = App.currentUser;
    if (user) {
      const nameEl = document.getElementById('profile-display-name');
      const userEl = document.getElementById('profile-username');
      const roleEl = document.getElementById('profile-role');
      const emailEl = document.getElementById('profile-email');
      const roleTag = document.getElementById('profile-role-tag');

      if (nameEl) nameEl.textContent = user.full_name || user.username;
      if (userEl) userEl.textContent = user.username;
      if (emailEl) emailEl.textContent = user.email || 'N/A';
      
      const roleName = user.role === 'admin' ? 'Administrator' : (user.role === 'demo' ? 'Demo User' : 'Risk Analyst');
      if (roleEl) roleEl.textContent = roleName;
      if (roleTag) roleTag.textContent = roleName;
    }

    const isAdmin = user && user.role === 'admin';
    const auditCard = document.getElementById('audit-log-card');
    const fcCard = document.getElementById('card-feature-controls');

    if (isAdmin) {
      if (auditCard) {
        auditCard.style.display = 'block';
        this.loadAuditLogs();
      }
      if (fcCard) {
        fcCard.style.display = 'block';
        this.renderFeatureControlsForm();
      }
    } else {
      if (auditCard) {
        const canViewAudit = App.isActionAllowed('audit_view');
        auditCard.style.display = canViewAudit ? 'block' : 'none';
        if (canViewAudit) this.loadAuditLogs();
      }
      if (fcCard) {
        const canViewFC = App.isActionAllowed('admin_fc_view');
        fcCard.style.display = canViewFC ? 'block' : 'none';
        if (canViewFC) this.renderFeatureControlsForm();
      }
    }
  },

  renderFeatureControlsForm() {
    const containers = {
      'Dashboard': document.getElementById('fc-group-dashboard'),
      'Assets': document.getElementById('fc-group-assets'),
      'Risks': document.getElementById('fc-group-risks'),
      'Reports': document.getElementById('fc-group-reports'),
      'Profile / Audit': document.getElementById('fc-group-profile'),
      'Administration': document.getElementById('fc-group-admin')
    };

    Object.values(containers).forEach(c => {
      if (c) c.innerHTML = '';
    });

    const canModify = App.currentUser && (App.currentUser.role === 'admin' || App.isActionAllowed('admin_fc_modify'));
    const saveBtn = document.getElementById('btn-save-feature-controls');
    if (saveBtn) saveBtn.disabled = !canModify;

    App.rawControls.forEach(ctrl => {
      const container = containers[ctrl.category] || containers['Administration'];
      if (!container) return;

      const item = document.createElement('label');
      item.className = 'fc-checkbox-item';
      item.innerHTML = `
        <input type="checkbox" name="${ctrl.feature_key}" ${ctrl.is_enabled_for_demo ? 'checked' : ''} ${canModify ? '' : 'disabled'}>
        <div class="fc-item-info">
          <span class="fc-item-label">${App.escapeHtml(ctrl.feature_name || ctrl.label)}</span>
          <span class="fc-item-desc">${App.escapeHtml(ctrl.description)}</span>
        </div>
      `;

      container.appendChild(item);
    });
  },

  async saveFeatureControls(e) {
    e.preventDefault();
    const form = document.getElementById('form-feature-controls');
    if (!form) return;

    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    const controls = {};
    checkboxes.forEach(cb => {
      controls[cb.name] = cb.checked;
    });

    const submitBtn = document.getElementById('btn-save-feature-controls');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-sm"></span> Saving...`;
    }

    try {
      const res = await ApiClient.put('/api/feature-controls', { controls });
      if (res && res.success) {
        App.featureControls = res.controls_dict || {};
        App.rawControls = res.controls || [];
        App.showToast('Feature availability settings updated successfully.', 'success');
      }
    } catch (err) {
      App.showToast(err.message || 'Error updating feature controls.', 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Save Changes';
      }
    }
  },

  async loadAuditLogs() {
    const tbody = document.getElementById('tbody-audit-logs');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted"><span class="spinner-sm"></span> Loading audit logs...</td></tr>';

    try {
      const logs = await ApiClient.get('/api/audit-logs');
      if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No audit logs recorded yet.</td></tr>';
        return;
      }

      tbody.innerHTML = logs.map(l => {
        const dateStr = new Date(l.timestamp).toLocaleString();
        return `
          <tr>
            <td class="font-mono text-sm">${dateStr}</td>
            <td><strong>${App.escapeHtml(l.username)}</strong></td>
            <td><span class="badge-tag">${App.escapeHtml(l.action)}</span></td>
            <td><span class="badge-type">${App.escapeHtml(l.entity_type)}</span> ${App.escapeHtml(l.entity_id || '')}</td>
            <td><small>${App.escapeHtml(l.details || '')}</small></td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error('[Profile] Error loading audit logs:', err);
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error loading audit logs.</td></tr>';
    }
  }
};

// Boot App on DOM Ready
document.addEventListener('DOMContentLoaded', () => App.init());
