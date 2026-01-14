const { createApp } = Vue;

createApp({
    data() {
        return {
            userName: "Admin User",
            userRole: "Security Administrator",
            showDropdown: false,
            cctvs: [
                { 
                    name: "Main Gate CCTV", 
                    lat: 20.0450, 
                    lng: 99.8925, 
                    status: "up",
                    location: "Main Entrance",
                    lastUpdate: "2 min ago"
                },
                { 
                    name: "Library CCTV", 
                    lat: 20.0442, 
                    lng: 99.8945, 
                    status: "up",
                    location: "Central Library",
                    lastUpdate: "1 min ago"
                },
                { 
                    name: "Dormitory CCTV", 
                    lat: 20.0435, 
                    lng: 99.8952, 
                    status: "down",
                    location: "Student Housing",
                    lastUpdate: "15 min ago"
                },
                { 
                    name: "Parking Lot CCTV", 
                    lat: 20.0455, 
                    lng: 99.8935, 
                    status: "up",
                    location: "Parking Area A",
                    lastUpdate: "Just now"
                },
                { 
                    name: "Sports Complex CCTV", 
                    lat: 20.0438, 
                    lng: 99.8920, 
                    status: "up",
                    location: "Athletic Center",
                    lastUpdate: "3 min ago"
                }
            ],
            map: null
        };
    },
    computed: {
        onlineCount() {
            return this.cctvs.filter(c => c.status === "up").length;
        },
        offlineCount() {
            return this.cctvs.filter(c => c.status === "down").length;
        },
        totalCount() {
            return this.cctvs.length;
        },
        userInitials() {
            return this.userName
                .split(' ')
                .map(n => n[0])
                .join('')
                .toUpperCase()
                .slice(0, 2);
        }
    },
    methods: {
        toggleProfileMenu() {
            this.showDropdown = !this.showDropdown;
        },
        closeDropdown() {
            this.showDropdown = false;
        },
        goToProfile() {
            alert('Navigate to Profile page');
            this.closeDropdown();
        },
        goToSettings() {
            alert('Navigate to Settings page');
            this.closeDropdown();
        },
        viewActivity() {
            alert('View Activity Log');
            this.closeDropdown();
        },
        logout() {
            if (confirm('Are you sure you want to logout?')) {
                alert('Logging out...');
                this.closeDropdown();
                // Add your logout logic here
            }
        },
        handleLogoError(event) {
            // Fallback if logo image doesn't exist
            event.target.style.display = 'none';
        },
        initMap() {
            // Initialize map with better styling
            this.map = L.map('map', {
                zoomControl: true,
                attributionControl: true
            }).setView([20.0443, 99.8937], 16);

            // Use a more professional map tile
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(this.map);

            // Add CCTV markers
            this.cctvs.forEach(cctv => {
                this.addMarker(cctv);
            });
        },
        addMarker(cctv) {
            const color = cctv.status === "up" ? "#10b981" : "#ef4444";
            const statusText = cctv.status === "up" ? "Online" : "Offline";

            // Create custom marker
            const marker = L.circleMarker([cctv.lat, cctv.lng], {
                radius: 10,
                color: color,
                fillColor: color,
                fillOpacity: 0.8,
                weight: 3
            }).addTo(this.map);

            // Create custom popup content
            const popupContent = `
                <div class="popup-header">${cctv.name}</div>
                <div class="popup-body">
                    <div class="popup-status">
                        <span class="status-badge ${cctv.status}">
                            <span class="legend-dot ${cctv.status}"></span>
                            ${statusText}
                        </span>
                    </div>
                    <div class="popup-info">
                        <div class="popup-info-item">
                            <span class="popup-info-label">Location:</span>
                            <span>${cctv.location}</span>
                        </div>
                        <div class="popup-info-item">
                            <span class="popup-info-label">Last Update:</span>
                            <span>${cctv.lastUpdate}</span>
                        </div>
                        <div class="popup-info-item">
                            <span class="popup-info-label">Coordinates:</span>
                            <span>${cctv.lat.toFixed(4)}, ${cctv.lng.toFixed(4)}</span>
                        </div>
                    </div>
                </div>
            `;

            marker.bindPopup(popupContent, {
                maxWidth: 300,
                className: 'custom-popup'
            });

            // Add pulsing animation for offline cameras
            if (cctv.status === "down") {
                setInterval(() => {
                    marker.setStyle({ fillOpacity: marker.options.fillOpacity === 0.8 ? 0.3 : 0.8 });
                }, 1000);
            }
        }
    },
    mounted() {
        this.initMap();
    }
}).mount('#app');
