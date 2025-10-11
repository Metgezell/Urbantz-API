// Urbantz Interface JavaScript
class UrbantzInterface {
    constructor() {
        this.apiKey = '';
        this.baseUrl = 'https://api.urbantz.com';
        this.history = JSON.parse(localStorage.getItem('urbantz-history') || '[]');
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSavedConfig();
        this.updateStatus();
        this.renderHistory();
        this.setDefaultDate();
    }

    setupEventListeners() {
        // API Key toggle
        document.getElementById('toggleApiKey').addEventListener('click', () => {
            const input = document.getElementById('apiKey');
            input.type = input.type === 'password' ? 'text' : 'password';
        });

        // Test connection
        document.getElementById('testConnection').addEventListener('click', () => {
            this.testConnection();
        });

        // Form submission
        document.getElementById('taskForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createTask();
        });

        // Clear form
        document.getElementById('clearForm').addEventListener('click', () => {
            this.clearForm();
        });

        // Add item
        document.getElementById('addItem').addEventListener('click', () => {
            this.addItemRow();
        });

        // Remove items (delegated event listener)
        document.getElementById('itemsContainer').addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-item')) {
                e.target.closest('.item-row').remove();
            }
        });

        // Auto-save API key
        document.getElementById('apiKey').addEventListener('input', (e) => {
            this.apiKey = e.target.value;
            this.saveConfig();
            this.updateStatus();
        });
    }

    loadSavedConfig() {
        const savedApiKey = localStorage.getItem('urbantz-api-key');
        if (savedApiKey) {
            document.getElementById('apiKey').value = savedApiKey;
            this.apiKey = savedApiKey;
        }
    }

    saveConfig() {
        localStorage.setItem('urbantz-api-key', this.apiKey);
    }

    updateStatus() {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (this.apiKey) {
            statusDot.classList.add('connected');
            statusText.textContent = 'Verbonden';
        } else {
            statusDot.classList.remove('connected');
            statusText.textContent = 'Niet verbonden';
        }
    }

    setDefaultDate() {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        document.getElementById('serviceDate').value = tomorrow.toISOString().split('T')[0];
    }

    async testConnection() {
        if (!this.apiKey) {
            this.showMessage('Voer eerst een API key in', 'error');
            return;
        }

        this.showLoading(true);
        
        try {
            const response = await fetch(`${this.baseUrl}/v2/announce`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': this.apiKey
                },
                body: JSON.stringify({
                    customerRef: 'TEST-CONNECTION',
                    deliveryAddress: { line1: 'Test Address' },
                    serviceDate: '2025-01-01'
                })
            });

            if (response.status === 401) {
                this.showMessage('Ongeldige API key', 'error');
            } else if (response.status === 400) {
                this.showMessage('API verbinding succesvol!', 'success');
            } else {
                this.showMessage('API verbinding succesvol!', 'success');
            }
        } catch (error) {
            this.showMessage('Verbindingsfout: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async createTask() {
        if (!this.apiKey) {
            this.showMessage('Voer eerst een API key in', 'error');
            return;
        }

        const taskData = this.collectFormData();
        if (!taskData) return;

        this.showLoading(true);

        try {
            const response = await fetch(`${this.baseUrl}/v2/announce`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': this.apiKey
                },
                body: JSON.stringify(taskData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showMessage('Taak succesvol aangemaakt!', 'success');
                this.addToHistory(taskData, result, 'success');
                this.clearForm();
            } else {
                this.showMessage(`Fout: ${result.message || 'Onbekende fout'}`, 'error');
                this.addToHistory(taskData, result, 'error');
            }
        } catch (error) {
            this.showMessage('Verbindingsfout: ' + error.message, 'error');
            this.addToHistory(taskData, { error: error.message }, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    collectFormData() {
        const customerRef = document.getElementById('customerRef').value.trim();
        const serviceDate = document.getElementById('serviceDate').value;
        const timeStart = document.getElementById('timeStart').value;
        const timeEnd = document.getElementById('timeEnd').value;

        // Required fields validation
        if (!customerRef) {
            this.showMessage('Klant referentie is verplicht', 'error');
            return null;
        }

        if (!serviceDate) {
            this.showMessage('Service datum is verplicht', 'error');
            return null;
        }

        const deliveryLine1 = document.getElementById('deliveryLine1').value.trim();
        if (!deliveryLine1) {
            this.showMessage('Leveradres regel 1 is verplicht', 'error');
            return null;
        }

        // Build task data
        const taskData = {
            customerRef,
            serviceDate,
            deliveryAddress: {
                line1: deliveryLine1,
                postalCode: document.getElementById('deliveryPostal').value.trim() || undefined,
                city: document.getElementById('deliveryCity').value.trim() || undefined,
                contactName: document.getElementById('deliveryContact').value.trim() || undefined,
                contactPhone: document.getElementById('deliveryPhone').value.trim() || undefined,
                contactEmail: document.getElementById('deliveryEmail').value.trim() || undefined
            }
        };

        // Add time window if provided
        if (timeStart) taskData.timeWindowStart = timeStart;
        if (timeEnd) taskData.timeWindowEnd = timeEnd;

        // Add pickup address if provided
        const pickupLine1 = document.getElementById('pickupLine1').value.trim();
        if (pickupLine1) {
            taskData.pickupAddress = {
                line1: pickupLine1,
                postalCode: document.getElementById('pickupPostal').value.trim() || undefined,
                city: document.getElementById('pickupCity').value.trim() || undefined,
                contactName: document.getElementById('pickupContact').value.trim() || undefined
            };
        }

        // Add items
        const items = this.collectItems();
        if (items.length > 0) {
            taskData.items = items;
        }

        // Add notes
        const notes = document.getElementById('notes').value.trim();
        if (notes) {
            taskData.notes = notes;
        }

        return taskData;
    }

    collectItems() {
        const items = [];
        const itemRows = document.querySelectorAll('.item-row');
        
        itemRows.forEach(row => {
            const sku = row.querySelector('.item-sku').value.trim();
            const description = row.querySelector('.item-description').value.trim();
            const quantity = parseInt(row.querySelector('.item-quantity').value) || 1;
            const weight = parseFloat(row.querySelector('.item-weight').value) || undefined;
            const tempClass = row.querySelector('.item-temp').value;

            if (description) {
                const item = {
                    description,
                    quantity
                };

                if (sku) item.sku = sku;
                if (weight) item.weightKg = weight;
                if (tempClass !== 'ambient') item.tempClass = tempClass;

                items.push(item);
            }
        });

        return items;
    }

    addItemRow() {
        const container = document.getElementById('itemsContainer');
        const itemRow = document.createElement('div');
        itemRow.className = 'item-row';
        itemRow.innerHTML = `
            <input type="text" placeholder="SKU (optioneel)" class="item-sku">
            <input type="text" placeholder="Beschrijving" class="item-description">
            <input type="number" placeholder="Aantal" class="item-quantity" min="1" value="1">
            <input type="number" placeholder="Gewicht (kg)" class="item-weight" step="0.1">
            <select class="item-temp">
                <option value="ambient">Kamertemperatuur</option>
                <option value="chilled">Gekoeld</option>
                <option value="frozen">Bevroren</option>
            </select>
            <button type="button" class="remove-item">❌</button>
        `;
        container.appendChild(itemRow);
    }

    clearForm() {
        document.getElementById('taskForm').reset();
        this.setDefaultDate();
        
        // Clear items except the first one
        const container = document.getElementById('itemsContainer');
        const firstRow = container.querySelector('.item-row');
        container.innerHTML = '';
        if (firstRow) {
            container.appendChild(firstRow);
        }
    }

    addToHistory(taskData, result, status) {
        const historyItem = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            taskData,
            result,
            status
        };

        this.history.unshift(historyItem);
        
        // Keep only last 50 items
        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }

        localStorage.setItem('urbantz-history', JSON.stringify(this.history));
        this.renderHistory();
        this.renderResults(historyItem);
    }

    renderHistory() {
        const container = document.getElementById('historyContainer');
        
        if (this.history.length === 0) {
            container.innerHTML = '<div class="no-history"><p>Geen taken in de geschiedenis.</p></div>';
            return;
        }

        const historyHTML = this.history.map(item => `
            <div class="history-item">
                <div class="history-info">
                    <div><strong>${item.taskData.customerRef}</strong></div>
                    <div>${item.taskData.deliveryAddress.line1}</div>
                    <div class="history-time">${new Date(item.timestamp).toLocaleString('nl-NL')}</div>
                </div>
                <div class="result-status ${item.status}">
                    ${item.status === 'success' ? '✅ Succes' : '❌ Fout'}
                </div>
            </div>
        `).join('');

        container.innerHTML = historyHTML;
    }

    renderResults(item) {
        const container = document.getElementById('resultsContainer');
        const resultHTML = `
            <div class="result-item ${item.status}">
                <div class="result-header">
                    <h3>${item.taskData.customerRef}</h3>
                    <div class="result-status ${item.status}">
                        ${item.status === 'success' ? '✅ Succes' : '❌ Fout'}
                    </div>
                </div>
                <div class="result-details">
                    <p><strong>Adres:</strong> ${item.taskData.deliveryAddress.line1}</p>
                    <p><strong>Datum:</strong> ${item.taskData.serviceDate}</p>
                    ${item.status === 'success' ? 
                        `<p><strong>Task ID:</strong> ${item.result.taskId || 'N/A'}</p>` :
                        `<p><strong>Fout:</strong> ${item.result.message || item.result.error || 'Onbekende fout'}</p>`
                    }
                </div>
            </div>
        `;

        // Remove no-results message if it exists
        const noResults = container.querySelector('.no-results');
        if (noResults) {
            noResults.remove();
        }

        container.insertAdjacentHTML('afterbegin', resultHTML);
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }

    showMessage(message, type = 'info') {
        const container = document.getElementById('messageContainer');
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}`;
        messageEl.textContent = message;
        
        container.appendChild(messageEl);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 5000);
    }
}

// Initialize the interface when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new UrbantzInterface();
});
