// ==========================
//  MAP MANAGER - PROTOTYPE VERSION (P3)
// ==========================

function MapManager() {
    this.map = null;
    this.shipMarkers = {};
    this.portMarkers = {};
    this.portsMap = {};
    this.initializeMap();
}

// --------------------------
//  Khởi tạo bản đồ Leaflet
// --------------------------
MapManager.prototype.initializeMap = function() {
    try {
        this.map = L.map('map', {
            zoomAnimation: true,
            markerZoomAnimation: false,  // Tắt animation mặc định
            fadeAnimation: true,
            zoomSnap: 0.1,              // Làm mượt zoom
            zoomDelta: 0.5,             // Giảm độ nhảy khi zoom
            wheelDebounceTime: 100      // Giảm delay khi dùng chuột
        }).setView([15.5, 112], 5);
        
        // Lưu map instance vào window object để các module khác có thể truy cập
        window.mapInstance = this.map;
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(this.map);
        
        // Xử lý zoom mượt mà hơn
        this.map.on('zoomanim', (e) => {
            const zoom = e.zoom;
            const scale = this.map.getZoomScale(zoom);
            
            document.querySelectorAll('.leaflet-marker-icon').forEach(marker => {
                marker.style.transform = `translate3d(0,0,0) scale(${1/scale})`;
            });
        });

        console.log('✅ Map initialized successfully.');
    } catch (error) {
        console.error('❌ Failed to initialize map:', error);
        this.map = null;
    }
};

// --------------------------
//  Thêm marker của tàu
// --------------------------
MapManager.prototype.addShipMarker = function(ship) {
    if (!this.map) {
        console.error('Map not initialized');
        return;
    }

    if (!ship?.ship_name) {
        console.warn('Invalid ship data:', ship);
        return;
    }

    // Add CSS for smooth marker animations
    if (!document.getElementById('marker-styles')) {
        const style = document.createElement('style');
        style.id = 'marker-styles';
        style.textContent = `
            .leaflet-marker-icon {
                will-change: transform;
                transform-origin: bottom center !important;
            }
            .ship-marker {
                position: absolute;
                left: 50%;
                bottom: 0;
                transform-origin: center;
                transform: translate(-50%, -50%);
                pointer-events: none;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
                transition: all 0.3s ease;
            }
            .leaflet-marker-icon:hover .ship-marker {
                transform: translate(-50%, -50%) scale(1.1);
                filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
            }
            .leaflet-fade-anim .leaflet-popup {
                transition: none !important;
            }
        `;
        document.head.appendChild(style);
    }

    // Nếu marker tàu này đã tồn tại → xóa cũ để cập nhật mới
    if (this.shipMarkers[ship.ship_name]?.ship) {
        this.shipMarkers[ship.ship_name].ship.remove();
        delete this.shipMarkers[ship.ship_name];
    }

    const lat = parseFloat(ship.latitude);
    const lng = parseFloat(ship.longitude);

    // Kiểm tra toạ độ hợp lệ
    if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
        console.warn(`⚠️ Invalid coordinates for ship ${ship.ship_name}:`, lat, lng);
        return;
    }

    // Màu biểu thị độ trễ
    const getShipColor = (delay) => {
        if (delay === 0) return '#22c55e'; // Xanh - đúng giờ
        if (delay > 4) return '#ef4444';   // Đỏ - trễ nhiều
        return '#f97316';                  // Cam - cảnh báo
    };
    const shipColor = getShipColor(ship.delay_hours);

    // --------------------------
    //  Icon tàu
    // --------------------------
    // Tính góc hướng đến cảng đích
    const getRotationAngle = (fromLat, fromLng, toLat, toLng) => {
        const toRadian = angle => (angle * Math.PI) / 180;
        const toDegree = angle => (angle * 180) / Math.PI;

        const dLng = toRadian(toLng - fromLng);
        const fromLatRad = toRadian(fromLat);
        const toLatRad = toRadian(toLat);

        const y = Math.sin(dLng) * Math.cos(toLatRad);
        const x = Math.cos(fromLatRad) * Math.sin(toLatRad) -
                 Math.sin(fromLatRad) * Math.cos(toLatRad) * Math.cos(dLng);

        const angle = toDegree(Math.atan2(y, x));
        return (angle + 360) % 360;
    };

    // Lấy tọa độ cảng đích từ portsMap
    const destPort = this.portsMap[ship.port_to.toLowerCase()];
    let rotationAngle = 0;

    if (destPort) {
        rotationAngle = getRotationAngle(
            parseFloat(ship.latitude),
            parseFloat(ship.longitude),
            parseFloat(destPort.latitude),
            parseFloat(destPort.longitude)
        );
    }

    const shipIcon = L.divIcon({
        html: `
            <div class="ship-marker">
                <svg width="24" height="24" viewBox="0 0 100 100">
                    <defs>
                        <filter id="ship-shadow" x="-20%" y="-20%" width="140%" height="140%">
                            <feGaussianBlur in="SourceAlpha" stdDeviation="1"/>
                            <feOffset dx="1" dy="1" result="offsetblur"/>
                            <feFlood flood-color="#000000" flood-opacity="0.2"/>
                            <feComposite in2="offsetblur" operator="in"/>
                            <feMerge>
                                <feMergeNode/>
                                <feMergeNode in="SourceGraphic"/>
                            </feMerge>
                        </filter>
                    </defs>
                    <g transform="translate(50,50) rotate(${rotationAngle})" filter="url(#ship-shadow)">
                        <!-- Simple arrow shape -->
                        <path d="M0,-40 L20,20 L0,10 L-20,20 Z"
                              fill="${shipColor}"
                              stroke="#ffffff"
                              stroke-width="2"/>
                    </g>
                </svg>
            </div>
        `,
        className: 'leaflet-marker-icon ship-icon',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });

    // --------------------------
    //  Tạo marker tàu trên bản đồ
    // --------------------------
    const marker = L.marker([lat, lng], {
        icon: shipIcon,
        title: ship.ship_name
    }).addTo(this.map);

    // --------------------------
    //  Tạo popup hiển thị thông tin tàu
    // --------------------------
    const popupHtml = `
        <div class="ship-popup">
            <div class="ship-header">
                <h3 class="ship-name">${ship.ship_name}</h3>
                <div class="status-badge ${
                    ship.delay_hours === 0
                        ? 'on-time'
                        : ship.delay_hours > 4
                        ? 'delayed'
                        : 'warning'
                }">
                    ${ship.delay_hours === 0 ? 'Đúng giờ' :
                      ship.delay_hours > 4 ? 'Trễ nhiều' : 'Cảnh báo'}
                </div>
            </div>
            <div class="info-grid">
                <div class="info-item" title="Tuyến đường di chuyển">
                    <span class="info-label">📍 Tuyến:</span>
                    <span class="info-value">${ship.port_from} → ${ship.port_to}</span>
                </div>
                <div class="info-item" title="Vị trí hiện tại">
                    <span class="info-label">🌍 Vị trí:</span>
                    <span class="info-value">${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E</span>
                </div>
                <div class="info-item" title="Thời gian dự kiến đến">
                    <span class="info-label">⏰ ETA:</span>
                    <span class="info-value">${new Date(ship.eta_expected).toLocaleString('vi-VN')}</span>
                </div>
                <div class="info-item" title="Thời gian trễ">
                    <span class="info-label">⌛ Độ trễ:</span>
                    <span class="info-value ${ship.delay_hours > 0 ? 'text-red-600' : 'text-green-600'}">
                        ${ship.delay_hours > 0 ? `+${ship.delay_hours} giờ` : 'Không có'}
                    </span>
                </div>
            </div>
            ${ship.reason ? `
                <div class="warning-box info" title="Lý do trễ">
                    <span class="text-orange-600">ℹ️</span> ${ship.reason}
                </div>` : ''}
            ${ship.distance_to_hazard ? `
                <div class="warning-box danger" title="Cảnh báo vùng nguy hiểm">
                    <span class="text-red-600">⚠️</span> Cách vùng nguy hiểm: ${ship.distance_to_hazard.toFixed(1)} km
                </div>` : ''}
        </div>
    `;

    const popup = L.popup({
        maxWidth: 'auto',
        className: 'ship-popup-custom',
        autoPan: true,
        autoPanPadding: [50, 50],
        closeButton: true,
        closeOnClick: false,
        keepInView: true
    }).setContent(popupHtml);
    
    marker.bindPopup(popup);
    
    // Xử lý các sự kiện để giữ popup trong viewport
    this.map.on('zoomend moveend', () => {
        if (marker.getPopup().isOpen()) {
            const map = this.map;
            const popup = marker.getPopup();
            const pos = map.latLngToContainerPoint(marker.getLatLng());
            const mapSize = map.getSize();
            
            // Kiểm tra nếu popup nằm ngoài viewport
            if (pos.x < 0 || pos.x > mapSize.x || pos.y < 0 || pos.y > mapSize.y) {
                // Tính toán vị trí mới để popup nằm trong viewport
                const padding = 50;
                const newPos = L.point(
                    Math.min(Math.max(pos.x, padding), mapSize.x - padding),
                    Math.min(Math.max(pos.y, padding), mapSize.y - padding)
                );
                const newLatLng = map.containerPointToLatLng(newPos);
                popup.setLatLng(newLatLng);
            }
            
            popup.update();
        }
    });
    
    // Xử lý sự kiện khi popup mở
    marker.on('popupopen', (e) => {
        const popup = e.popup;
        const map = this.map;
        
        // Đảm bảo popup nằm trong viewport khi mở
        const bounds = map.getBounds().pad(-0.1); // Padding 10% từ mép map
        if (!bounds.contains(popup.getLatLng())) {
            const center = marker.getLatLng();
            map.flyTo(center, map.getZoom(), {
                duration: 0.5
            });
        }
    });

    // Lưu marker lại để truy cập sau
    this.shipMarkers[ship.ship_name] = {
        ship: marker,
        status:
            ship.delay_hours > 6
                ? 'danger'
                : ship.delay_hours > 0
                ? 'warning'
                : 'normal'
    };

    // Khi click vào marker tàu → zoom và mở popup
    marker.on('click', () => this.focusShip(ship.ship_name));
};

// --------------------------
//  Hàm tạo nội dung popup tàu (fallback)
// --------------------------
MapManager.prototype.createShipPopup = function(ship) {
    try {
        return `<div class="ship-popup p-3">
                    <div class="text-lg font-bold text-blue-600">${ship.ship_name}</div>
                </div>`;
    } catch (error) {
        console.error('Error creating ship popup:', error);
        return '<div>Error loading ship info</div>';
    }
};

// --------------------------
//  Zoom & mở popup cho tàu
// --------------------------
MapManager.prototype.focusShip = function(shipName) {
    try {
        const marker = this.shipMarkers[shipName];
        if (!marker || !marker.ship) return;

        const shipLatLng = marker.ship.getLatLng();
        if (this.map) {
            this.map.setView(shipLatLng, 8);
            marker.ship.openPopup();
        }
    } catch (error) {
        console.error('Error focusing ship ' + shipName + ':', error);
    }
};

// --------------------------
//  Thêm marker cảng lên bản đồ
// --------------------------
MapManager.prototype.addPorts = function(ports) {
    try {
        if (!Array.isArray(ports) || !this.map) return;

        // Xoá marker cũ nếu có
        Object.values(this.portMarkers).forEach(marker => {
            if (marker && typeof marker.remove === 'function') {
                marker.remove();
            }
        });
        this.portMarkers = {};
        this.portsMap = {};

        // Lặp qua danh sách cảng
        ports.forEach(port => {
            const lat = parseFloat(port.location.latitude);
            const lng = parseFloat(port.location.longitude);

            if (isNaN(lat) || isNaN(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180) {
                console.warn(`⚠️ Invalid port coordinates: ${port.name}`, lat, lng);
                return;
            }

            const key = (port.name || port.port_name || '').toLowerCase();
            if (key) this.portsMap[key] = { latitude: lat, longitude: lng };

            const marker = L.marker([lat, lng], {
                icon: L.divIcon({
                    html: `
                        <div style="width: 28px; height: 28px;">
                            <svg viewBox="0 0 100 100" style="width: 100%; height: 100%;">
                                <defs>
                                    <filter id="port-shadow" x="-20%" y="-20%" width="140%" height="140%">
                                        <feGaussianBlur in="SourceAlpha" stdDeviation="1"/>
                                        <feOffset dx="1" dy="1" result="offsetblur"/>
                                        <feFlood flood-color="#000000" flood-opacity="0.2"/>
                                        <feComposite in2="offsetblur" operator="in"/>
                                        <feMerge>
                                            <feMergeNode/>
                                            <feMergeNode in="SourceGraphic"/>
                                        </feMerge>
                                    </filter>
                                </defs>
                                <g transform="translate(50,50)" filter="url(#port-shadow)">
                                    <!-- Neo với hiệu ứng ánh sáng -->
                                    <path d="
                                        M 0,-35 L 0,20
                                        M -20,-15 L 0,-25 L 20,-15
                                        M -22,10 C -22,10 -12,30 0,10 C 12,30 22,10 22,10
                                    " 
                                    stroke="#3b82f6" 
                                    stroke-width="6"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    fill="none"/>
                                    
                                    <!-- Phần sáng -->
                                    <path d="
                                        M 0,-35 L 0,20
                                        M -20,-15 L 0,-25 L 20,-15
                                        M -22,10 C -22,10 -12,30 0,10 C 12,30 22,10 22,10
                                    " 
                                    stroke="#60a5fa" 
                                    stroke-width="3"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    fill="none"
                                    opacity="0.7"/>
                                </g>
                            </svg>
                        </div>
                    `,
                    className: 'port-marker',
                    iconSize: [28, 28],
                    iconAnchor: [14, 14]
                })
            }).addTo(this.map);

            // Popup hiển thị tên cảng
            const popupContent = `
                <div class="text-center">
                    <h3 class="text-base font-semibold border-b border-gray-200 pb-1 mb-1">
                        ${port.name || port.port_name}
                    </h3>
                    <div class="text-sm text-gray-600">${port.region || ''}, ${port.country || ''}</div>
                </div>
            `;
            marker.bindPopup(popupContent, { closeButton: false, offset: [0, -4] });

            this.portMarkers[key] = marker;
        });
    } catch (e) {
        console.error('Error in addPorts:', e);
    }
};

// --------------------------
//  Export hàm khởi tạo MapManager
// --------------------------
export function initializeMap(shipData) {
    try {
        const mapManager = new MapManager();
        if (mapManager && mapManager.map && Array.isArray(shipData)) {
            shipData.forEach(ship => mapManager.addShipMarker(ship));
        }
        return mapManager;
    } catch (error) {
        console.error('Failed to initialize map:', error);
        return null;
    }
}
