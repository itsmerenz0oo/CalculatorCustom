(function () {
  const resultEl = document.getElementById('result');
  const prevEl = document.getElementById('prevExpr');
  const keypad = document.getElementById('keypad');
  const lightBtn = document.getElementById('lightBtn');
  const darkBtn = document.getElementById('darkBtn');
  const closeBtn = document.getElementById('closeBtn');

  let current = "0";
  let stored = null;
  let pendingOp = null;
  let justEvaluated = false;

  const fmt = n => new Intl.NumberFormat().format(n);
  const opSym = op => op === '*' ? '×' : op === '/' ? '÷' : op;

  function render() { resultEl.textContent = current; }

  function inputDigit(d) {
    if (justEvaluated) { current = "0"; justEvaluated = false; }
    current = current === "0" ? d : current + d;
    render();
  }

  function inputDot() {
    if (justEvaluated) { current = "0"; justEvaluated = false; }
    if (!current.includes(".")) current += ".";
    render();
  }

  function setOperator(op) {
    if (pendingOp && stored !== null && !justEvaluated) compute();
    stored = parseFloat(current);
    pendingOp = op;
    justEvaluated = true;
    prevEl.textContent = `${fmt(stored)} ${opSym(op)}`;
  }

  function compute() {
    if (pendingOp === null || stored === null) return;
    const b = parseFloat(current);
    let r;
    switch (pendingOp) {
      case '+': r = stored + b; break;
      case '-': r = stored - b; break;
      case '*': r = stored * b; break;
      case '/': r = b === 0 ? NaN : stored / b; break;
      default: r = b;
    }
    prevEl.textContent = `${fmt(stored)} ${opSym(pendingOp)} ${fmt(b)}`;
    current = Number.isFinite(r) ? String(Math.round(r * 1e10) / 1e10) : "Error";
    stored = null; pendingOp = null; justEvaluated = true;
    resultEl.textContent = current;
  }

  keypad.addEventListener('click', (e) => {
    const btn = e.target.closest('button.key');
    if (!btn) return;
    const op = btn.dataset.op;
    const action = btn.dataset.action;

    if (op) { setOperator(op); return; }
    if (action === 'clear') { current = "0"; stored = null; pendingOp = null; justEvaluated = false; prevEl.textContent = '\u00A0'; render(); return; }
    if (action === 'sign') { current = String(parseFloat(current) * -1); render(); return; }
    if (action === 'percent') { current = String(parseFloat(current) / 100); render(); return; }
    if (action === 'equals') { compute(); return; }

    const label = btn.textContent.trim();
    if (label === '.') inputDot();
    else inputDigit(label);
  });

  document.addEventListener('keydown', (e) => {
    if (/[0-9]/.test(e.key)) inputDigit(e.key);
    else if (e.key === '.') inputDot();
    else if (['+', '-', '*', '/'].includes(e.key)) setOperator(e.key);
    else if (e.key === 'Enter' || e.key === '=') compute();
    else if (e.key === 'Backspace') { current = current.length > 1 ? current.slice(0, -1) : "0"; render(); }
    else if (e.key.toLowerCase() === 'c') { current = "0"; stored = null; pendingOp = null; prevEl.textContent = '\u00A0'; render(); }
  });

  closeBtn.addEventListener('click', () => {
    current = "0"; stored = null; pendingOp = null; justEvaluated = false; prevEl.textContent = '\u00A0'; render();
  });

  function setTheme(dark) {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    lightBtn.classList.toggle('active', !dark);
    darkBtn.classList.toggle('active', dark);
  }
  lightBtn.addEventListener('click', () => setTheme(false));
  darkBtn.addEventListener('click', () => setTheme(true));

  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  setTheme(prefersDark);
  render();
})();
