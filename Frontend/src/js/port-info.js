// API functions for ports
export async function fetchAllPorts() {
    try {
        console.log('Fetching ports...'); // Debug log
        const response = await fetch('http://localhost:8000/api/ports');
        
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Raw API response:', data); // Debug log
        
        // Normalize status values
        if (data.ports) {
            data.ports = data.ports.map(port => ({
                ...port,
                status: (port.status || 'ổn định').toLowerCase()
            }));
        }
        console.log('Processed ports data:', data); // Debug log
        
        // Handle different response formats
        const ports = data.ports || data;
        if (!ports) {
            console.error('No ports data in response:', data);
            return [];
        }
        
        console.log('Processed ports:', ports); // Debug log
        return ports;
    } catch (error) {
        console.error('Error fetching ports:', error);
        return [];
    }
}

// UI Component for rendering port information
export function renderPortInfo(container, portData, onPortClick) {
    console.log('Rendering port info:', { portData }); // Debug log
    
    // Show loading state
    if (!portData) {
        container.innerHTML = `
            <div class="text-center py-4">
                <div class="inline-block w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
                <p class="mt-2">Đang tải thông tin cảng...</p>
            </div>
        `;
        return;
    }

    // Input validation
    if (!Array.isArray(portData) || portData.length === 0) {
        container.innerHTML = '<div class="text-center py-4">Không có thông tin cảng</div>';
        return;
    }

    // Reset container
    container.innerHTML = '';
    // Don't override the container's existing styles
    container.classList.add('overflow-hidden');

    // Add header
    const header = document.createElement('div');
    header.className = 'text-white p-4';
    header.innerHTML = `
        <h2 class="text-xl font-semibold flex items-center">
            <span class="mr-2">🚢</span>
            Thông tin cảng
        </h2>
    `;
    container.appendChild(header);

    // Create scrollable list
    const listContainer = document.createElement('div');
    listContainer.className = 'max-h-[400px] overflow-y-auto custom-scrollbar';

    // Create list
    const list = document.createElement('div');
    list.className = 'divide-y divide-gray-200';

    // Generate list items
    try {
        list.innerHTML = portData.map((port, index) => {
            try {
                console.log('Processing port:', port); // Debug log
                
                // Safely extract port data with fallbacks
                const location = port.location || {};
                const latitude = location.latitude || port.latitude || 'N/A';
                const longitude = location.longitude || port.longitude || 'N/A';
                const name = port.name || port.port_name || 'Unknown Port';
                const country = port.country || 'N/A';
                const status = (port.status || 'ổn định').toLowerCase();
                console.log(`Port ${name} - Raw status:`, port.status);
                console.log(`Port ${name} - Processed status:`, status);
                
                console.log(`Port ${name} status from database:`, port.status);
                console.log(`Final status after fallback:`, status);
                
                return `
                    <div class="p-4 bg-white m-2 rounded-lg cursor-pointer hover:transform hover:-translate-y-1 transition-all"
                         onclick="window.selectPort(${port.id || index})">
                        <h3 class="font-semibold text-lg mb-2 text-gray-800">${name}</h3>
                        <div class="text-sm space-y-2">
                            <div class="flex items-center">
                                <span class="font-medium text-gray-600 w-20">Vị trí:</span> 
                                <span class="text-gray-800">${latitude}°N, ${longitude}°E</span>
                            </div>
                            <div class="flex items-center">
                                <span class="font-medium text-gray-600 w-20">Quốc gia:</span> 
                                <span class="text-gray-800">${country}</span>
                            </div>
                            <div class="flex items-center">
                                <span class="font-medium text-gray-600 w-20">Trạng thái:</span>
                                <span class="px-2 py-0.5 rounded-full text-xs font-medium ${
                                    (!status || status.toLowerCase() === 'ổn định') 
                                    ? 'bg-green-100 text-green-800 border border-green-200' 
                                    : status.toLowerCase() === 'bận'
                                    ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                                    : 'bg-red-100 text-red-800 border border-red-200'
                                }">
                                    ${(!status || status.toLowerCase() === 'ổn định') ? 'Ổn định' : status.toLowerCase() === 'bận' ? 'Bận' : 'Quá tải'}
                                </span>
                            </div>
                        </div>
                    </div>
                `;
            } catch (error) {
                console.error('Error processing port:', error);
                return '';
            }
        }).join('');
    } catch (error) {
        console.error('Error generating list:', error);
        list.innerHTML = '<div class="text-center py-4">Lỗi hiển thị danh sách cảng</div>';
    }

    // Assemble components
    listContainer.appendChild(list);
    container.appendChild(listContainer);

    // Add custom scrollbar styles if not already added
    if (!document.getElementById('custom-scrollbar-style')) {
        const style = document.createElement('style');
        style.id = 'custom-scrollbar-style';
        style.textContent = `
            .custom-scrollbar::-webkit-scrollbar {
                width: 4px;
            }
            .custom-scrollbar::-webkit-scrollbar-track {
                background: transparent;
            }
            .custom-scrollbar::-webkit-scrollbar-thumb {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
            }
        `;
        document.head.appendChild(style);
    }

    // Add port selection handler
    window.selectPort = (portId) => {
        try {
            const selectedPort = portData.find(p => (p.id || p.port_id) === portId);
            if (selectedPort && onPortClick) {
                const location = selectedPort.location || {};
                onPortClick({
                    ...selectedPort,
                    latitude: location.latitude || selectedPort.latitude,
                    longitude: location.longitude || selectedPort.longitude
                });
            }
        } catch (error) {
            console.error('Error in port selection:', error);
        }
    };
}