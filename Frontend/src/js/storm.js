// =============================
// FETCH & HIỂN THỊ BÃO TRÊN BẢN ĐỒ
// =============================

// Lưu marker để xóa khi reload
let stormLayers = [];

/**
 * Xóa toàn bộ layer bão khỏi bản đồ
 */
function clearStormsFromMap(map) {
    stormLayers.forEach(layer => map.removeLayer(layer));
    stormLayers = [];
}

/**
 * Hàm vẽ các điểm bão lên bản đồ
 * @param {Array} alerts - danh sách alert đã qua xử lý
 * @param {Object} map - instance Leaflet map
 */
function drawStormsOnMap(alerts, map) {
    if (!map) {
        console.warn('⚠️ Map instance không tồn tại – không thể vẽ bão.');
        return;
    }

    clearStormsFromMap(map);

    alerts.forEach(alert => {
        // Tạo icon bão (màu & emoji tùy theo status)
        const stormIcon = L.divIcon({
            className: 'storm-icon',
            html: `<div class="storm-marker ${
                alert.status === 'Siêu bão' ? 'super-typhoon' :
                alert.status === 'Bão mạnh' ? 'strong-typhoon' :
                alert.status === 'Bão' ? 'typhoon' : 'tropical-depression'
            }">${
                alert.status === 'Siêu bão' ? '🌪️' :
                alert.status === 'Bão mạnh' ? '🌀' :
                alert.status === 'Bão' ? '🌊' : '🌧️'
            }</div>`,
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });

        // Marker tâm bão
        const marker = L.marker([alert.lat, alert.lng], { icon: stormIcon })
            .bindPopup(`
                <div class="storm-popup">
                    <h3 class="font-bold">${alert.m}</h3>
                    <p class="text-sm mt-1">Vị trí: ${alert.t}</p>
                    <p class="text-sm mt-1">Tốc độ gió: ${alert.windSpeed} km/h</p>
                    <p class="text-sm mt-1">Bán kính ảnh hưởng: ${alert.radius} km</p>
                    <p class="text-sm mt-1">Bán kính cảnh báo: ${alert.warningRadius} km</p>
                    <p class="text-sm mt-1 ${
                        alert.status === 'Siêu bão' ? 'text-red-600' :
                        alert.status === 'Bão mạnh' ? 'text-orange-600' :
                        alert.status === 'Bão' ? 'text-yellow-600' : 'text-blue-600'
                    }">${alert.status}</p>
                </div>
            `);

        // Vòng tròn ảnh hưởng
        const stormCircle = L.circle([alert.lat, alert.lng], {
            color: alert.status === 'Siêu bão' ? '#ff0000' :
                alert.status === 'Bão mạnh' ? '#ffa500' :
                alert.status === 'Bão' ? '#ffff00' : '#0000ff',
            fillColor: alert.status === 'Siêu bão' ? '#ff000033' :
                alert.status === 'Bão mạnh' ? '#ffa50033' :
                alert.status === 'Bão' ? '#ffff0033' : '#0000ff33',
            fillOpacity: 0.3,
            radius: alert.radius * 1000
        });

        // Vòng tròn cảnh báo
        const warningCircle = L.circle([alert.lat, alert.lng], {
            color: stormCircle.options.color,
            fillColor: 'transparent',
            weight: 1,
            dashArray: '5, 10',
            radius: alert.warningRadius * 1000
        });

        marker.addTo(map);
        stormCircle.addTo(map);
        warningCircle.addTo(map);

        stormLayers.push(marker, stormCircle, warningCircle);
    });
}

/**
 * Gọi API & xử lý dữ liệu bão
 */
export async function fetchStormAlerts(map) {
    try {
        const response = await fetch('http://localhost:8000/api/storm-alerts');

        if (!response.ok) throw new Error('API storm-alerts trả về lỗi');

        const data = await response.json();
        console.log('🌩️ Raw API Response:', data);

        // Convert DB fields → UI-friendly fields
        const alerts = data.map(alert => ({
            m: alert.message,
            s: alert.severity,
            status: alert.status,
            lat: alert.latitude,
            lng: alert.longitude,
            radius: alert.radius_km,
            warningRadius: alert.warning_radius_km,
            windSpeed: alert.wind_kmh,
            t: `${alert.latitude.toFixed(4)}°N, ${alert.longitude.toFixed(4)}°E`
        }));

        drawStormsOnMap(alerts, map);

        console.log('✅ Processed Alerts:', alerts);
        return alerts;
    } catch (error) {
        console.error('❌ Error fetching storm alerts:', error);
        return [];
    }
}

/**
 * Format thời gian kiểu "x ago"
 */
function formatTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);

    if (diffSec < 60) return 'vừa xong';

    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;

    const diffHours = Math.floor(diffMin / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    return `${Math.floor(diffHours / 24)}d ago`;
}
