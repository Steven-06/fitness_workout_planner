const defaultBaseUrl = window.location.origin;
const state = {
  baseUrl: defaultBaseUrl,
  user: null,
  lastPlan: null,
};

const elements = {
  backendUrl: document.getElementById('backendUrl'),
  testApiBtn: document.getElementById('testApiBtn'),
  nameInput: document.getElementById('nameInput'),
  goalInput: document.getElementById('goalInput'),
  levelInput: document.getElementById('levelInput'),
  daysCheckboxes: document.getElementById('daysCheckboxes'),
  createUserBtn: document.getElementById('createUserBtn'),
  loadUserId: document.getElementById('loadUserId'),
  loadUserBtn: document.getElementById('loadUserBtn'),
  currentUserInfo: document.getElementById('currentUserInfo'),
  generateRuleBtn: document.getElementById('generateRuleBtn'),
  generateCspBtn: document.getElementById('generateCspBtn'),
  comparePlansBtn: document.getElementById('comparePlansBtn'),
  missedDayInput: document.getElementById('missedDayInput'),
  adaptPlanBtn: document.getElementById('adaptPlanBtn'),
  predictAdherenceBtn: document.getElementById('predictAdherenceBtn'),
  getPlansBtn: document.getElementById('getPlansBtn'),
  getComparisonsBtn: document.getElementById('getComparisonsBtn'),
  getPredictionsBtn: document.getElementById('getPredictionsBtn'),
  listWorkoutsBtn: document.getElementById('listWorkoutsBtn'),
  categoryInput: document.getElementById('categoryInput'),
  levelFilterInput: document.getElementById('levelFilterInput'),
  filterWorkoutsBtn: document.getElementById('filterWorkoutsBtn'),
  statusPanel: document.getElementById('statusPanel'),
  outputArea: document.getElementById('outputArea'),
};

const availableDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

function createDayCheckboxes() {
  availableDays.forEach((day) => {
    const label = document.createElement('label');
    label.innerHTML = `<input type="checkbox" value="${day}" /> ${day}`;
    elements.daysCheckboxes.appendChild(label);
  });
}

function getSelectedDays() {
  return Array.from(elements.daysCheckboxes.querySelectorAll('input:checked')).map(
    (input) => input.value
  );
}

function updateStatus(message, isError = false) {
  elements.statusPanel.textContent = message;
  elements.statusPanel.style.color = isError ? '#ffb4b4' : '#a8c8ff';
}

function updateOutput(title, data) {
  const pretty = JSON.stringify(data, null, 2);
  elements.outputArea.textContent = `${title}\n\n${pretty}`;
}

function renderUserInfo() {
  if (!state.user) {
    elements.currentUserInfo.textContent = 'No user loaded.';
    return;
  }
  const result = {
    id: state.user.id || '(not saved yet)',
    name: state.user.name,
    goal: state.user.goal,
    level: state.user.level,
    available_days: state.user.available_days,
  };
  elements.currentUserInfo.textContent = JSON.stringify(result, null, 2);
}

function getBaseUrl() {
  const value = elements.backendUrl.value.trim();
  return value ? value.replace(/\/+$/, '') : defaultBaseUrl;
}

async function apiRequest(path, method = 'GET', body = null, params = {}) {
  const baseUrl = getBaseUrl();
  const url = new URL(`${baseUrl}/api/v1${path}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value);
    }
  });

  const init = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };
  if (body) {
    init.body = JSON.stringify(body);
  }

  try {
    updateStatus(`Calling ${url.pathname}...`);
    const response = await fetch(url.toString(), init);
    const json = await response.json();
    if (!response.ok) {
      throw new Error(`${response.status} ${json.detail || response.message || response}`);
    }
    return json;
  } catch (error) {
    updateStatus(`Request failed: ${error.message}`, true);
    throw error;
  }
}

async function createUser() {
  const payload = {
    name: elements.nameInput.value.trim() || 'Anonymous',
    goal: elements.goalInput.value,
    level: elements.levelInput.value,
    available_days: getSelectedDays(),
  };

  if (payload.available_days.length === 0) {
    updateStatus('Select at least one available day.', true);
    return;
  }

  const result = await apiRequest('/users', 'POST', payload);
  state.user = { ...payload, id: result.id };
  renderUserInfo();
  updateStatus(`User created: ${result.id}`);
  updateOutput('User created', result);
}

async function loadUser() {
  const userId = elements.loadUserId.value.trim();
  if (!userId) {
    updateStatus('Enter a user ID to load.', true);
    return;
  }
  const user = await apiRequest(`/users/${userId}`);
  state.user = user;
  renderUserInfo();
  updateStatus(`Loaded user ${userId}`);
  updateOutput('Loaded user', user);
}

async function generatePlan(type) {
  if (!state.user) {
    updateStatus('Create or load a user before generating plans.', true);
    return;
  }
  const path = type === 'rule' ? '/plan/rule-based' : '/plan/csp';
  const result = await apiRequest(path, 'POST', state.user);
  state.lastPlan = result;
  updateStatus(`${type === 'rule' ? 'Rule-based' : 'CSP'} plan generated.`);
  updateOutput('Generated plan', result);
}

async function comparePlans() {
  if (!state.user) {
    updateStatus('Create or load a user before comparing plans.', true);
    return;
  }
  const result = await apiRequest('/plan/compare', 'POST', state.user);
  updateStatus('Plan comparison complete.');
  updateOutput('Comparison result', result);
}

async function adaptPlan() {
  if (!state.lastPlan) {
    updateStatus('Generate a plan before adapting it.', true);
    return;
  }
  const missedDay = elements.missedDayInput.value.trim();
  if (!missedDay) {
    updateStatus('Enter a missed day to adapt the plan.', true);
    return;
  }
  const planPayload = { plan: state.lastPlan.plan || state.lastPlan };
  const result = await apiRequest('/plan/adapt', 'POST', planPayload, {
    missed_day: missedDay,
    user_id: state.user?.id || 'temp',
  });
  state.lastPlan = result;
  updateStatus('Plan adapted successfully.');
  updateOutput('Adapted plan', result);
}

async function predictAdherence() {
  if (!state.user) {
    updateStatus('Create or load a user before predicting adherence.', true);
    return;
  }
  const params = {};
  const result = await apiRequest('/predict/adherence', 'POST', state.user, params);
  updateStatus('Adherence prediction returned.');
  updateOutput('Adherence prediction', result);
}

async function fetchUserData(path, title) {
  if (!state.user) {
    updateStatus('Load a user first.', true);
    return;
  }
  const result = await apiRequest(`/users/${state.user.id}/${path}`);
  updateStatus(`${title} loaded.`);
  updateOutput(title, result);
}

async function getWorkouts() {
  const category = elements.categoryInput.value.trim();
  const level = elements.levelFilterInput.value.trim();
  let path = '/workouts';
  if (category && level) {
    path = `/workouts/${encodeURIComponent(category)}/${encodeURIComponent(level)}`;
  } else if (category) {
    path = `/workouts/category/${encodeURIComponent(category)}`;
  } else if (level) {
    path = `/workouts/level/${encodeURIComponent(level)}`;
  }
  const result = await apiRequest(path);
  updateStatus('Workout list updated.');
  updateOutput('Workouts', result);
}

async function testApi() {
  try {
    await apiRequest('/users');
    updateStatus('Backend API connection successful.');
  } catch (error) {
    updateStatus('Backend API connection failed.', true);
  }
}

function attachListeners() {
  elements.testApiBtn.addEventListener('click', testApi);
  elements.createUserBtn.addEventListener('click', createUser);
  elements.loadUserBtn.addEventListener('click', loadUser);
  elements.generateRuleBtn.addEventListener('click', () => generatePlan('rule'));
  elements.generateCspBtn.addEventListener('click', () => generatePlan('csp'));
  elements.comparePlansBtn.addEventListener('click', comparePlans);
  elements.adaptPlanBtn.addEventListener('click', adaptPlan);
  elements.predictAdherenceBtn.addEventListener('click', predictAdherence);
  elements.getPlansBtn.addEventListener('click', () => fetchUserData('plans', 'User plans'));
  elements.getComparisonsBtn.addEventListener('click', () => fetchUserData('comparisons', 'User comparisons'));
  elements.getPredictionsBtn.addEventListener('click', () => fetchUserData('predictions', 'User predictions'));
  elements.listWorkoutsBtn.addEventListener('click', getWorkouts);
  elements.filterWorkoutsBtn.addEventListener('click', getWorkouts);
}

function initialize() {
  createDayCheckboxes();
  renderUserInfo();
  attachListeners();
  if (!elements.backendUrl.value.trim()) {
    elements.backendUrl.value = '';
  }
  updateStatus('Ready. Enter your backend URL or use the current site.');
}

initialize();
