// Hàm để lấy thông tin cảng từ API
export async function fetchPortsData() {
    try {
        console.log('Fetching ports data...');
        const response = await fetch('http://192.168.1.176:8000/api/ports');
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Raw API response:', data);
        return data.ports; // API trả về object với key "ports"
    } catch (error) {
        console.error('Error fetching ports data:', error);
        return null;
    }
}

// Hàm để render thông tin cảng
export function renderPortInfo(container, portData) {
    if (!portData) {
        container.innerHTML = '<div class="text-center py-4">Không thể tải thông tin cảng</div>';
        return;
    }
    
    // Debug logs
    console.log('Port Data received in renderPortInfo:', portData);
    console.log('Raw port status:', portData.status);
    console.log('Port status type:', typeof portData.status);
    
    // Đảm bảo status là chữ thường để so sánh chính xác
    const status = (portData.status || '').toLowerCase();

    container.innerHTML = `
        <h2 class="text-xl font-bold mb-4">🚢 Thông tin Cảng</h2>
        <div class="space-y-4">
            <div class="border-b border-blue-400 pb-2">
                <div class="font-medium">Số tàu đang neo đậu:</div>
                <div class="text-2xl font-bold">${portData.dockedShips || 0}</div>
            </div>
            <div class="border-b border-blue-400 pb-2">
                <div class="font-medium">Công suất sử dụng:</div>
                <div class="text-lg">
                    ${portData.capacity || 0}% 
                    <span class="text-sm">(${portData.availableSlots || 0} chỗ trống)</span>
                </div>
            </div>
            <div class="border-b border-blue-400 pb-2">
                <div class="font-medium">Thời gian chờ trung bình:</div>
                <div class="text-lg">${portData.avgWaitingTime || 'N/A'}</div>
            </div>
            <div>
                <div class="font-medium">Trạng thái hoạt động:</div>
                <div class="flex items-center mt-1">
                    <span class="w-3 h-3 rounded-full ${
                        status === 'ổn định' || !status ? 'bg-green-500' : 
                        status === 'bận' ? 'bg-yellow-500' : 
                        'bg-red-500'
                    } mr-2"></span>
                    <span class="${
                        status === 'ổn định' || !status ? 'text-green-600' : 
                        status === 'bận' ? 'text-yellow-600' : 
                        'text-red-600'
                    } font-medium">${
                        status === 'ổn định' || !status ? 'Ổn định' :
                        status === 'bận' ? 'Bận' :
                        'Quá tải'
                    }</span>
                </div>
            </div>
        </div>
    `;
}