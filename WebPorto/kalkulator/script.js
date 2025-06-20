class ProfessionalCalculator {
    constructor() {
        this.currentValue = '0';
        this.previousValue = '';
        this.operation = null;
        this.waitingForNewValue = false;
        this.memory = 0;
        this.history = JSON.parse(localStorage.getItem('calculatorHistory')) || [];
        this.currentMode = 'standard';
        this.currentNumberSystem = 'dec';
        this.isDarkTheme = localStorage.getItem('darkTheme') === 'true';
        
        this.initializeElements();
        this.attachEventListeners();
        this.initializeTheme();
        this.updateDisplay();
        this.updateHistory();
        this.updateMemoryIndicator();
    }
    
    initializeElements() {
        this.display = document.getElementById('mainDisplay');
        this.historyDisplay = document.getElementById('historyDisplay');
        this.memoryIndicator = document.getElementById('memoryIndicator');
        this.historyPanel = document.getElementById('historyPanel');
        this.historyContent = document.getElementById('historyContent');
        this.themeToggle = document.getElementById('themeToggle');
    }
    
    attachEventListeners() {
        // Number buttons
        document.querySelectorAll('[data-number]').forEach(button => {
            button.addEventListener('click', () => {
                this.inputNumber(button.dataset.number);
                this.animateButton(button);
            });
        });
        
        // Operation buttons
        document.querySelectorAll('[data-action]').forEach(button => {
            button.addEventListener('click', () => {
                this.handleAction(button.dataset.action);
                this.animateButton(button);
            });
        });
        
        // Hex buttons for programmer mode
        document.querySelectorAll('[data-hex]').forEach(button => {
            button.addEventListener('click', () => {
                this.inputNumber(button.dataset.hex);
                this.animateButton(button);
            });
        });
        
        // Mode selector
        document.querySelectorAll('.mode-btn').forEach(button => {
            button.addEventListener('click', () => {
                this.switchMode(button.dataset.mode);
            });
        });
        
        // Number system selector
        document.querySelectorAll('.system-btn').forEach(button => {
            button.addEventListener('click', () => {
                this.switchNumberSystem(button.dataset.system);
            });
        });
        
        // Theme toggle
        this.themeToggle.addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // History controls
        document.getElementById('historyBtn').addEventListener('click', () => {
            this.toggleHistoryPanel();
        });
        
        document.getElementById('clearHistoryBtn').addEventListener('click', () => {
            this.clearHistory();
        });
        
        // Keyboard support
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
        
        // History item clicks
        this.historyContent.addEventListener('click', (e) => {
            const historyItem = e.target.closest('.history-item');
            if (historyItem) {
                const result = historyItem.querySelector('.result').textContent;
                this.currentValue = result;
                this.updateDisplay();
            }
        });
    }
    
    initializeTheme() {
        if (this.isDarkTheme) {
            document.body.setAttribute('data-theme', 'dark');
            this.themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }
    
    inputNumber(num) {
        if (this.currentMode === 'programmer') {
            if (!this.isValidForCurrentSystem(num)) return;
        }
        
        if (this.waitingForNewValue) {
            this.currentValue = num;
            this.waitingForNewValue = false;
        } else {
            this.currentValue = this.currentValue === '0' ? num : this.currentValue + num;
        }
        
        this.updateDisplay();
    }
    
    handleAction(action) {
        switch (action) {
            case 'clear-all':
                this.clearAll();
                break;
            case 'clear-entry':
                this.clearEntry();
                break;
            case 'backspace':
                this.backspace();
                break;
            case 'negate':
                this.negate();
                break;
            case 'decimal':
                this.inputDecimal();
                break;
            case 'add':
            case 'subtract':
            case 'multiply':
            case 'divide':
                this.setOperation(action);
                break;
            case 'equals':
                this.calculate();
                break;
            case 'memory-clear':
                this.memoryClear();
                break;
            case 'memory-recall':
                this.memoryRecall();
                break;
            case 'memory-add':
                this.memoryAdd();
                break;
            case 'memory-subtract':
                this.memorySubtract();
                break;
            case 'x2':
                this.square();
                break;
            case '1/x':
                this.reciprocal();
                break;
            case 'sqrt':
                this.squareRoot();
                break;
            case 'sin':
                this.sine();
                break;
            case 'cos':
                this.cosine();
                break;
            case 'tan':
                this.tangent();
                break;
            case 'log':
                this.logarithm();
                break;
            case 'ln':
                this.naturalLog();
                break;
            case 'factorial':
                this.factorial();
                break;
            case 'power':
                this.setOperation('power');
                break;
            case 'pi':
                this.inputConstant(Math.PI);
                break;
            case 'e':
                this.inputConstant(Math.E);
                break;
            case 'and':
            case 'or':
            case 'xor':
            case 'not':
                this.bitwiseOperation(action);
                break;
        }
    }
    
    clearAll() {
        this.currentValue = '0';
        this.previousValue = '';
        this.operation = null;
        this.waitingForNewValue = false;
        this.updateDisplay();
        this.updateHistoryDisplay('');
    }
    
    clearEntry() {
        this.currentValue = '0';
        this.updateDisplay();
    }
    
    backspace() {
        if (this.currentValue.length > 1) {
            this.currentValue = this.currentValue.slice(0, -1);
        } else {
            this.currentValue = '0';
        }
        this.updateDisplay();
    }
    
    negate() {
        this.currentValue = String(-parseFloat(this.currentValue));
        this.updateDisplay();
    }
    
    inputDecimal() {
        if (this.waitingForNewValue) {
            this.currentValue = '0.';
            this.waitingForNewValue = false;
        } else if (this.currentValue.indexOf('.') === -1) {
            this.currentValue += '.';
        }
        this.updateDisplay();
    }
    
    setOperation(op) {
        if (this.operation && !this.waitingForNewValue) {
            this.calculate();
        }
        
        this.previousValue = this.currentValue;
        this.operation = op;
        this.waitingForNewValue = true;
        
        const operatorSymbols = {
            'add': '+',
            'subtract': '-',
            'multiply': '×',
            'divide': '÷',
            'power': '^'
        };
        
        this.updateHistoryDisplay(`${this.previousValue} ${operatorSymbols[op] || op}`);
    }
    
    calculate() {
        if (!this.operation || this.waitingForNewValue) return;
        
        const prev = parseFloat(this.previousValue);
        const current = parseFloat(this.currentValue);
        let result;
        
        try {
            switch (this.operation) {
                case 'add':
                    result = prev + current;
                    break;
                case 'subtract':
                    result = prev - current;
                    break;
                case 'multiply':
                    result = prev * current;
                    break;
                case 'divide':
                    if (current === 0) throw new Error('Division by zero');
                    result = prev / current;
                    break;
                case 'power':
                    result = Math.pow(prev, current);
                    break;
                default:
                    return;
            }
            
            const expression = `${this.previousValue} ${this.getOperatorSymbol(this.operation)} ${this.currentValue}`;
            this.addToHistory(expression, result);
            
            this.currentValue = this.formatResult(result);
            this.operation = null;
            this.previousValue = '';
            this.waitingForNewValue = true;
            
            this.updateDisplay();
            this.updateHistoryDisplay('');
            this.animateSuccess();
            
        } catch (error) {
            this.showError(error.message);
        }
    }
    
    // Memory operations
    memoryClear() {
        this.memory = 0;
        this.updateMemoryIndicator();
    }
    
    memoryRecall() {
        this.currentValue = String(this.memory);
        this.updateDisplay();
    }
    
    memoryAdd() {
        this.memory += parseFloat(this.currentValue);
        this.updateMemoryIndicator();
        this.animateMemory();
    }
    
    memorySubtract() {
        this.memory -= parseFloat(this.currentValue);
        this.updateMemoryIndicator();
        this.animateMemory();
    }
    
    // Scientific operations
    square() {
        const value = parseFloat(this.currentValue);
        const result = value * value;
        this.addToHistory(`${value}²`, result);
        this.currentValue = this.formatResult(result);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    reciprocal() {
        const value = parseFloat(this.currentValue);
        if (value === 0) {
            this.showError('Cannot divide by zero');
            return;
        }
        const result = 1 / value;
        this.addToHistory(`1/${value}`, result);
        this.currentValue = this.formatResult(result);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    squareRoot() {
        const value = parseFloat(this.currentValue);
        if (value < 0) {
            this.showError('Invalid input');
            return;
        }
        const result = Math.sqrt(value);
        this.addToHistory(`√${value}`, result);
        this.currentValue = this.formatResult(result);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    sine() {
        const value = parseFloat(this.currentValue);
        const result = Math.sin(value * Math.PI / 180); // Convert to radians
        this.addToHistory(`sin(${value}°)`, result);
        this.currentValue = this.formatResult(result);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    cosine() {
        const value = parseFloat(this.currentValue);
        const result = Math.cos(value * Math.PI / 180);
        this.addToHistory(`cos(${value}°)`, result);
        this.currentValue = this.formatResult(result);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    tangent() {
        const value = parseFloat(this.currentValue);
        const result = Math.tan(value * Math.PI / 180);
        this.addToHistory(`tan(${value}°)`, result);
        this.currentValue = this.formatResult(result);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    logarithm() {
        const value = parseFloat(this.currentValue);
        if (value <= 0) {
            this.showError('Invalid input');
            return;
        }
        const result = Math.log10(value);
        this.addToHistory(`log(${value})`, result);
        this.currentValue = this.formatResult(result);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    naturalLog() {
        const value = parseFloat(this.currentValue);
        if (value <= 0) {
            this.showError('Invalid input');
            return;
        }
        const result = Math.log(value);
        this.addToHistory(`ln(${value})`, result);
        this.currentValue = this.formatResult(result);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    factorial() {
        const value = parseInt(this.currentValue);
        if (value < 0 || value > 170) {
            this.showError('Invalid input');
            return;
        }
        
        let result = 1;
        for (let i = 2; i <= value; i++) {
            result *= i;
        }
        
        this.addToHistory(`${value}!`, result);
        this.currentValue = this.formatResult(result);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    inputConstant(value) {
        this.currentValue = this.formatResult(value);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    // Bitwise operations for programmer mode
    bitwiseOperation(operation) {
        const value = parseInt(this.currentValue);
        let result;
        
        switch (operation) {
            case 'not':
                result = ~value;
                this.addToHistory(`NOT ${value}`, result);
                break;
            default:
                // For AND, OR, XOR, we need two operands
                this.setOperation(operation);
                return;
        }
        
        this.currentValue = String(result);
        this.updateDisplay();
        this.waitingForNewValue = true;
    }
    
    // Mode switching
    switchMode(mode) {
        this.currentMode = mode;
        
        // Update mode buttons
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
        
        // Show/hide appropriate button grids
        document.querySelectorAll('.button-grid').forEach(grid => {
            grid.classList.remove('active');
        });
        document.getElementById(`${mode}Mode`).classList.add('active');
        
        // Update hex buttons visibility for programmer mode
        if (mode === 'programmer') {
            this.updateHexButtons();
        }
    }
    
    switchNumberSystem(system) {
        if (this.currentMode !== 'programmer') return;
        
        this.currentNumberSystem = system;
        
        // Update system buttons
        document.querySelectorAll('.system-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-system="${system}"]`).classList.add('active');
        
        // Convert current value
        this.convertNumberSystem();
        this.updateHexButtons();
        this.updateDisplay();
    }
    
    convertNumberSystem() {
        const decimalValue = this.getDecimalValue();
        
        switch (this.currentNumberSystem) {
            case 'hex':
                this.currentValue = decimalValue.toString(16).toUpperCase();
                break;
            case 'oct':
                this.currentValue = decimalValue.toString(8);
                break;
            case 'bin':
                this.currentValue = decimalValue.toString(2);
                break;
            default:
                this.currentValue = decimalValue.toString();
        }
    }
    
    getDecimalValue() {
        switch (this.currentNumberSystem) {
            case 'hex':
                return parseInt(this.currentValue, 16) || 0;
            case 'oct':
                return parseInt(this.currentValue, 8) || 0;
            case 'bin':
                return parseInt(this.currentValue, 2) || 0;
            default:
                return parseInt(this.currentValue) || 0;
        }
    }
    
    isValidForCurrentSystem(digit) {
        switch (this.currentNumberSystem) {
            case 'bin':
                return /[01]/.test(digit);
            case 'oct':
                return /[0-7]/.test(digit);
            case 'dec':
                return /[0-9]/.test(digit);
            case 'hex':
                return /[0-9A-F]/.test(digit);
            default:
                return true;
        }
    }
    
    updateHexButtons() {
        document.querySelectorAll('.hex-btn').forEach(btn => {
            const isEnabled = this.currentNumberSystem === 'hex';
            btn.disabled = !isEnabled;
        });
        
        // Update number buttons based on current system
        document.querySelectorAll('.number-btn').forEach(btn => {
            const digit = btn.dataset.number;
            const isEnabled = this.isValidForCurrentSystem(digit);
            btn.disabled = !isEnabled;
        });
    }
    
    // Theme toggle
    toggleTheme() {
        this.isDarkTheme = !this.isDarkTheme;
        
        if (this.isDarkTheme) {
            document.body.setAttribute('data-theme', 'dark');
            this.themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            document.body.removeAttribute('data-theme');
            this.themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
        
        localStorage.setItem('darkTheme', this.isDarkTheme);
    }
    
    // History management
    addToHistory(expression, result) {
        const historyItem = {
            expression,
            result: this.formatResult(result),
            timestamp: new Date().toLocaleString()
        };
        
        this.history.unshift(historyItem);
        
        // Keep only last 50 calculations
        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }
        
        localStorage.setItem('calculatorHistory', JSON.stringify(this.history));
        this.updateHistory();
    }
    
    updateHistory() {
        if (this.history.length === 0) {
            this.historyContent.innerHTML = `
                <div class="empty-history">
                    <i class="fas fa-calculator"></i>
                    <p>Belum ada perhitungan</p>
                </div>
            `;
            return;
        }
        
        this.historyContent.innerHTML = this.history.map(item => `
            <div class="history-item">
                <div class="expression">${item.expression}</div>
                <div class="result">${item.result}</div>
                <div class="timestamp">${item.timestamp}</div>
            </div>
        `).join('');
    }
    
    clearHistory() {
        this.history = [];
        localStorage.removeItem('calculatorHistory');
        this.updateHistory();
    }
    
    toggleHistoryPanel() {
        this.historyPanel.style.display = 
            this.historyPanel.style.display === 'none' ? 'block' : 'none';
    }
    
    // Display updates
    updateDisplay() {
        let displayValue = this.currentValue;
        
        // Format large numbers
        if (this.currentMode !== 'programmer' && !isNaN(displayValue) && displayValue !== '') {
            const num = parseFloat(displayValue);
            if (Math.abs(num) >= 1e12 || (Math.abs(num) < 1e-6 && num !== 0)) {
                displayValue = num.toExponential(6);
            } else if (displayValue.includes('.')) {
                displayValue = parseFloat(displayValue).toFixed(Math.min(10, displayValue.split('.')[1].length));
                displayValue = displayValue.replace(/\.?0+$/, ''); // Remove trailing zeros
            }
        }
        
        this.display.textContent = displayValue;
        
        // Add animation
        this.display.classList.add('calculation-success');
        setTimeout(() => {
            this.display.classList.remove('calculation-success');
        }, 600);
    }
    
    updateHistoryDisplay(text) {
        this.historyDisplay.textContent = text;
    }
    
    updateMemoryIndicator() {
        if (this.memory !== 0) {
            this.memoryIndicator.classList.add('active');
        } else {
            this.memoryIndicator.classList.remove('active');
        }
    }
    
    // Utility functions
    formatResult(result) {
        if (isNaN(result) || !isFinite(result)) {
            return 'Error';
        }
        
        // Handle very large or very small numbers
        if (Math.abs(result) >= 1e15 || (Math.abs(result) < 1e-10 && result !== 0)) {
            return result.toExponential(10);
        }
        
        // Remove unnecessary decimal places
        const str = result.toString();
        if (str.includes('.')) {
            return parseFloat(result.toFixed(10)).toString();
        }
        
        return str;
    }
    
    getOperatorSymbol(operation) {
        const symbols = {
            'add': '+',
            'subtract': '-',
            'multiply': '×',
            'divide': '÷',
            'power': '^'
        };
        return symbols[operation] || operation;
    }
    
    showError(message) {
        this.currentValue = 'Error';
        this.display.classList.add('display-error');
        this.updateDisplay();
        
        setTimeout(() => {
            this.display.classList.remove('display-error');
            this.clearAll();
        }, 2000);
    }
    
    animateButton(button) {
        button.classList.add('pressed');
        setTimeout(() => {
            button.classList.remove('pressed');
        }, 100);
    }
    
    animateSuccess() {
        this.display.classList.add('calculation-success');
        setTimeout(() => {
            this.display.classList.remove('calculation-success');
        }, 600);
    }
    
    animateMemory() {
        this.memoryIndicator.classList.add('active');
        setTimeout(() => {
            if (this.memory === 0) {
                this.memoryIndicator.classList.remove('active');
            }
        }, 1000);
    }
    
    // Keyboard support
    handleKeyboard(event) {
        const key = event.key;
        
        // Prevent default for calculator keys
        if (/[0-9+\-*/=.c]/.test(key.toLowerCase()) || 
            ['Enter', 'Backspace', 'Delete', 'Escape'].includes(key)) {
            event.preventDefault();
        }
        
        // Number keys
        if (/[0-9]/.test(key)) {
            this.inputNumber(key);
        }
        
        // Operation keys
        switch (key) {
            case '+':
                this.handleAction('add');
                break;
            case '-':
                this.handleAction('subtract');
                break;
            case '*':
                this.handleAction('multiply');
                break;
            case '/':
                this.handleAction('divide');
                break;
            case '=':
            case 'Enter':
                this.handleAction('equals');
                break;
            case '.':
                this.handleAction('decimal');
                break;
            case 'Backspace':
                this.handleAction('backspace');
                break;
            case 'Delete':
            case 'Escape':
                this.handleAction('clear-all');
                break;
            case 'c':
            case 'C':
                this.handleAction('clear-entry');
                break;
        }
        
        // Hex keys for programmer mode
        if (this.currentMode === 'programmer' && /[A-F]/.test(key.toUpperCase())) {
            this.inputNumber(key.toUpperCase());
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ProfessionalCalculator();
    
    // Add some extra animations and effects
    addVisualEffects();
});

function addVisualEffects() {
    // Add particle effect on calculation
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('equals-btn')) {
            createParticleEffect(e.target);
        }
    });
    
    // Add hover effect with no background change
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.background = 'transparent';
            btn.style.color = '#667eea';
            btn.style.transform = 'translateY(-2px) scale(1.05)';
        });
        
        btn.addEventListener('mouseleave', () => {
            btn.style.background = 'transparent';
            btn.style.color = '';
            btn.style.transform = '';
        });
    });
}

function createParticleEffect(element) {
    const rect = element.getBoundingClientRect();
    const particles = 12;
    
    for (let i = 0; i < particles; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: fixed;
            width: 4px;
            height: 4px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            left: ${rect.left + rect.width / 2}px;
            top: ${rect.top + rect.height / 2}px;
        `;
        
        document.body.appendChild(particle);
        
        const angle = (i / particles) * Math.PI * 2;
        const velocity = 100 + Math.random() * 50;
        const life = 1000 + Math.random() * 500;
        
        particle.animate([
            {
                transform: 'translate(0, 0) scale(1)',
                opacity: 1
            },
            {
                transform: `translate(${Math.cos(angle) * velocity}px, ${Math.sin(angle) * velocity}px) scale(0)`,
                opacity: 0
            }
        ], {
            duration: life,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }).addEventListener('finish', () => {
            particle.remove();
        });
    }
}
