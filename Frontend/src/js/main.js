import { fetchStormAlerts } from './storm.js';
import { initializeMap } from './map.js';
import { TableManager, AlertManager, initializeSearch } from './ui-managers.js';
import { fetchAllPorts, renderPortInfo } from './port-info.js';
import { fetchETAInfo, renderETAInfo } from './eta.js';

document.addEventListener('DOMContentLoaded', async () => {
    // Initialize map
    let mapManager = null;
    try {
        mapManager = initializeMap([]);
    } catch (e) {
        console.error('Error initializing map:', e);
    }

    // Không cần khởi tạo TableManager nữa vì chúng ta sẽ dùng renderETAInfo

    // Initialize alerts
    try {
        const alertsContainer = document.getElementById('alerts');
        const alertManager = new AlertManager(alertsContainer);
        
        // Fetch and render initial alerts
        const loadAlerts = async () => {
            const alerts = await fetchStormAlerts();
            console.log('Received storm alerts:', alerts);
            alertsContainer.innerHTML = ''; // Clear existing alerts
            alerts.forEach(alert => alertManager.renderAlert(alert));
        };
        
        // Load initial alerts
        loadAlerts();
        
        // Update alerts every 5 minutes
        setInterval(loadAlerts, 5 * 60 * 1000);
    } catch (e) {
        console.error('Error initializing alerts:', e);
    }

    // Initialize search
    try {
        const searchInput = document.getElementById('search');
        const tableElement = document.getElementById('table');
        initializeSearch(searchInput, tableElement);
    } catch (e) {
        console.error('Error initializing search:', e);
    }

    // Initialize port information
    const portInfoContainer = document.getElementById('port-info');
    if (!portInfoContainer) {
        console.error('Port info container not found');
    } else {
        try {
            const portsData = await fetchAllPorts();
            // If parent wrapper missing for some reason, fallback to inner element
            const renderTarget = portInfoContainer || portInfoInner;
            renderPortInfo(renderTarget, portsData, (selectedPort) => {
                try {
                    if (mapManager && mapManager.map) {
                        mapManager.map.setView(
                            [selectedPort.latitude, selectedPort.longitude],
                            8
                        );
                    }
                } catch (err) {
                    console.error('Error centering map on selected port:', err);
                }
            });
            // Also add port markers to the map manager so routes can target them
            try {
                if (mapManager && typeof mapManager.addPorts === 'function') {
                    mapManager.addPorts(portsData);
                }
            } catch (e) {
                console.error('Error adding ports to mapManager:', e);
            }

            // After ports are loaded, fetch ETA and create ship markers from ETA data
            try {
                const etaData = await fetchETAInfo();
                console.log("Received ETA data:", etaData);
                
                // Build ships from etaData
                // Add ships to map
                if (mapManager) {
                    console.log(`Adding ${etaData.length} ships to map...`);
                    etaData.forEach((eta) => {
                        // allow 0 coordinates but reject null/undefined
                        if (eta.latitude != null && eta.longitude != null) {
                            mapManager.addShipMarker(eta);
                        } else {
                            // still log for debugging
                            console.debug(`Skipping ship marker (no coords): ${eta.ship_name}`, eta.latitude, eta.longitude);
                        }
                    });
                }
                
                // Render ETA info table
                const etaContainer = document.getElementById('eta-info');
                if (etaContainer) {
                    renderETAInfo(etaContainer, etaData);
                }
            } catch (e) {
                console.error('Error loading ETA to create ships:', e);
            }
        } catch (error) {
            console.error('Error initializing port information:', error);
        }
    }

    // ETA information will be handled by the previous fetchETAInfo call

    // Update data periodically
    setInterval(async () => {
        try {
            // Update ports every 5 minutes
            if (portInfoContainer) {
                const updatedPortsData = await fetchAllPorts();
                renderPortInfo(portInfoContainer, updatedPortsData);
                try {
                    if (mapManager && typeof mapManager.addPorts === 'function') {
                        mapManager.addPorts(updatedPortsData);
                    }
                } catch (e) {
                    console.error('Error updating ports on map:', e);
                }
            }
        } catch (error) {
            console.error('Error updating port information:', error);
        }
    }, 5 * 60 * 1000);  // 5 minutes

    // Start auto-refresh for ETA data
    fetchETAInfo(true);  // true enables auto-refresh every 5 seconds
});