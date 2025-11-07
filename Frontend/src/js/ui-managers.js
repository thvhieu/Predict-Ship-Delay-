export class TableManager {
    constructor(tableElement, mapManager) {
        this.tableElement = tableElement;
        this.mapManager = mapManager;
    }

    renderShipRow(ship) {
        const row = this.tableElement.insertRow();
        row.onclick = () => this.mapManager.showShipRoute(ship);
        row.className = 'hover:bg-gray-50 cursor-pointer';
        
        row.insertCell(0).textContent = ship.name;
        row.insertCell(1).textContent = ship.route;
        row.insertCell(2).textContent = ship.eta;
        
        const delayCell = row.insertCell(3);
        delayCell.textContent = ship.delay > 0 ? '+' + ship.delay + 'h' : 'On time';
        delayCell.className = ship.delay > 3 ? 'text-red-600' : ship.delay > 0 ? 'text-yellow-600' : 'text-green-600';
        
        const statusCell = row.insertCell(4);
        statusCell.innerHTML = `<span class="px-2 py-1 rounded text-xs ${
            ship.st === 'danger' ? 'bg-red-100 text-red-800' : 
            ship.st === 'warning' ? 'bg-yellow-100 text-yellow-800' : 
            'bg-green-100 text-green-800'
        }">${
            ship.st === 'danger' ? 'Trễ nhiều' : 
            ship.st === 'warning' ? 'Cảnh báo' : 
            'Bình thường'
        }</span>`;
    }
}

export class AlertManager {
    constructor(alertsContainer) {
        this.container = alertsContainer;
    }

    renderAlert(alert) {
        const div = document.createElement('div');
        div.className = 'alert-item';
        div.innerHTML = `
            <div class="flex items-start gap-4">
                <div class="alert-icon ${
                    alert.status === 'Siêu bão' ? 'bg-red-100' :
                    alert.status === 'Bão mạnh' ? 'bg-orange-100' :
                    alert.status === 'Bão' ? 'bg-yellow-100' :
                    'bg-blue-100'
                }">
                    ${
                        alert.status === 'Siêu bão' ? '🌪️' :
                        alert.status === 'Bão mạnh' ? '🌀' :
                        alert.status === 'Bão' ? '🌊' :
                        '🌧️'
                    }
                </div>
                <div class="flex-1">
                    <div class="flex items-center justify-between mb-2">
                        <p class="alert-message">${alert.m}</p>
                        <span class="alert-status ${
                            alert.status === 'Siêu bão' ? 'bg-red-100 text-red-800' :
                            alert.status === 'Bão mạnh' ? 'bg-orange-100 text-orange-800' :
                            alert.status === 'Bão' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-blue-100 text-blue-800'
                        }">
                            ${alert.status}
                        </span>
                    </div>
                    <p class="alert-time">${alert.t}</p>
                </div>
            </div>`;
        this.container.appendChild(div);
    }
}

export function initializeSearch(searchInput, tableElement) {
    searchInput.oninput = (e) => {
        const searchValue = e.target.value.toLowerCase();
        Array.from(tableElement.rows).forEach(row => {
            row.style.display = row.textContent.toLowerCase().includes(searchValue) ? '' : 'none';
        });
    };
}