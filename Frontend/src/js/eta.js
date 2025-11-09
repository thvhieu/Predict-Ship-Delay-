// Hàm để format thời gian
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

// Hàm để lấy style cho status
function getStatusStyle(status, delay) {
    if (status === "Trễ") {
        return {
            text: 'Trễ',
            class: 'bg-red-100 text-red-800'
        };
    }
    if (delay === 0) {
        return {
            text: 'Bình thường',
            class: 'bg-green-100 text-green-800'
        };
    }
    return {
        text: 'Cảnh báo',
        class: 'bg-yellow-100 text-yellow-800'
    };
}

// Hàm để lấy thông tin ETA từ API
export async function fetchETAInfo(autoRefresh = false) {
    try {
        // Thêm timestamp và no-cache headers
        const timestamp = new Date().getTime();
        const response = await fetch(`http://localhost:8000/api/eta?_t=${timestamp}`, {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            cache: 'no-store'
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log("ETA Data from API:", data);

        // Normalize response shape in case backend returns an object wrapper
        if (data && !Array.isArray(data)) {
            if (Array.isArray(data.results)) {
                if (autoRefresh) setTimeout(() => fetchETAInfo(true), 5000);
                return data.results;
            }
            if (Array.isArray(data.data)) {
                if (autoRefresh) setTimeout(() => fetchETAInfo(true), 5000);
                return data.data;
            }
            // If it's an object but not an array, try to find the first array value
            const firstArray = Object.values(data).find(v => Array.isArray(v));
            if (firstArray) {
                if (autoRefresh) setTimeout(() => fetchETAInfo(true), 5000);
                return firstArray;
            }
        }
        
        // Nếu autoRefresh = true, tự động gọi lại API sau mỗi 5 giây
        if (autoRefresh) {
            setTimeout(() => fetchETAInfo(true), 5000); // Giảm thời gian refresh xuống 5 giây
        }
        
    return data;
    } catch (error) {
        console.error('Error fetching ETA data:', error);
        return [];
    }
}

// Hàm để render thông tin ETA
export function renderETAInfo(container, etaData) {
    // Clear any existing content
    container.innerHTML = '';

    if (!etaData || !Array.isArray(etaData)) {
        container.innerHTML = '<div class="text-center py-4">Đang tải thông tin ETA...</div>';
        return;
    }
    
    if (etaData.length === 0) {
        container.innerHTML = '<div class="text-center py-4">Không có thông tin ETA</div>';
        return;
    }

    // Container
    container.className = 'bg-white rounded-lg shadow-lg overflow-hidden flex flex-col';
    
    // Header (fixed)
    const header = document.createElement('div');
    header.className = 'bg-[#4052b6] text-white p-4 flex items-center space-x-2 sticky top-0 z-10';
    header.innerHTML = `
        <span class="text-2xl">⏰</span>
        <h2 class="text-xl font-bold">ETA Table</h2>
    `;
    container.appendChild(header);

    // Table container with scroll
    const tableContainer = document.createElement('div');
    tableContainer.className = 'overflow-auto max-h-[300px] custom-scrollbar';
    
    // Table
    const table = document.createElement('table');
    table.className = 'w-full';

    // Table header
    const thead = document.createElement('thead');
    thead.className = 'bg-white sticky top-0 shadow-sm z-10';
    thead.innerHTML = `
        <tr class="text-left border-b">
            <th class="p-3 w-[15%] font-semibold">Tàu</th>
            <th class="p-3 w-[25%] font-semibold">Tuyến</th>
            <th class="p-3 w-[20%] font-semibold">Vị trí</th>
            <th class="p-3 w-[15%] font-semibold">ETA</th>
            <th class="p-3 w-[10%] font-semibold">Delay</th>
            <th class="p-3 w-[15%] font-semibold">Status</th>
        </tr>
    `;
    table.appendChild(thead);

    // Table body
    const tbody = document.createElement('tbody');
    tbody.className = 'bg-white';
    tbody.innerHTML = etaData.map((eta, index) => {
        const status = getStatusStyle(eta.status, eta.delay_hours);
        const delayText = eta.delay_hours > 0 
            ? `<span class="text-orange-500">+${eta.delay_hours}h</span>`
            : `<span class="text-green-600">On time</span>`;

        return `
            <tr class="${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} border-b hover:bg-blue-50 transition-colors">
                <td class="p-3 w-[15%]">
                    <div class="font-medium truncate">${eta.ship_name}</div>
                </td>
                <td class="p-3 w-[25%]">
                    <div class="flex items-center space-x-2">
                        <span class="truncate">${eta.port_from}</span>
                        <span>→</span>
                        <span class="truncate">${eta.port_to}</span>
                    </div>
                </td>
                <td class="p-3 w-[20%]">
                    ${(eta.latitude || eta.latitude_ship) && (eta.longitude || eta.longitude_ship) ? 
                      `<div class="text-gray-600 flex flex-col">
                         <span title="Vĩ độ">${(eta.latitude || eta.latitude_ship).toFixed(4)}°N</span>
                         <span title="Kinh độ">${(eta.longitude || eta.longitude_ship).toFixed(4)}°E</span>
                       </div>` : 
                      '<span class="text-gray-400">N/A</span>'}
                </td>
                <td class="p-3 w-[15%]">
                    <div class="whitespace-nowrap">${formatDateTime(eta.eta_expected)}</div>
                </td>
                <td class="p-3 w-[10%]">
                    <div class="whitespace-nowrap">${delayText}</div>
                </td>
                <td class="p-3 w-[15%]">
                    <span class="px-2 py-0.5 rounded-full text-sm ${status.class} whitespace-nowrap">
                        ${status.text}
                    </span>
                </td>
            </tr>
        `;
    }).join('');
    
    table.appendChild(tbody);
    tableContainer.appendChild(table);
    container.appendChild(tableContainer);
    
    // Add custom scrollbar styles if not already added
    if (!document.getElementById('custom-scrollbar-style')) {
        const style = document.createElement('style');
        style.id = 'custom-scrollbar-style';
        style.textContent = `
            .custom-scrollbar::-webkit-scrollbar {
                width: 6px;
                height: 6px;
            }
            .custom-scrollbar::-webkit-scrollbar-track {
                background: #f1f1f1;
            }
            .custom-scrollbar::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 3px;
            }
            .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
        `;
        document.head.appendChild(style);
    }
}

// Hàm để lấy thông tin ETA của một tàu cụ thể
export async function fetchShipETA(shipName) {
    try {
        const response = await fetch(`http://localhost:8000/api/eta/${encodeURIComponent(shipName)}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching ship ETA:', error);
        return null;
    }
}