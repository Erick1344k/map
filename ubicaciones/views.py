from django.shortcuts import render
import folium

def mapa_view(request):
    # Centro del campus
    centro_unemi = [-2.1496, -79.6031]

    # Mapa con OpenStreetMap, zoom máximo 21
    mapa = folium.Map(
        location=centro_unemi,
        zoom_start=19,
        max_zoom=21,
        control_scale=True,
        tiles='OpenStreetMap'
    )

    # === PUNTOS FIJOS DEL CAMPUS ===
    puntos = [
        {"nombre": "CRAI", "coordenadas": [-2.14970, -79.60325]},
        {"nombre": "Bloque M", "coordenadas": [-2.15035, -79.60345]},
        {"nombre": "SIM", "coordenadas": [-2.14910, -79.60330]},
        {"nombre": "Bloque V", "coordenadas": [-2.14830, -79.60372]},
        {"nombre": "Bloque W", "coordenadas": [-2.14810, -79.60320]},
        {"nombre": "Piscina UNEMI", "coordenadas": [-2.14855, -79.60263]},
        {"nombre": "Cancha UNEMI", "coordenadas": [-2.14910, -79.60200]},
    ]

    for punto in puntos:
        folium.Marker(
            location=punto["coordenadas"],
            popup=punto["nombre"],
            tooltip=punto["nombre"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mapa)

    # === JavaScript: GPS en tiempo real + botón visible + puntero con rotación ===
    mapa.get_root().html.add_child(folium.Element("""
    <script>
        let userMarker = null;
        let userCircle = null;
        let watchId = null;

        // SVG: Flecha azul tipo Google Maps
        const arrowSvg = `
            <svg width="34" height="34" viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg">
                <circle cx="17" cy="17" r="16" fill="#4285F4" stroke="white" stroke-width="3"/>
                <path d="M17 6 L11 16 L17 13 L23 16 Z" fill="white" transform="translate(0, -1)"/>
                <circle cx="17" cy="17" r="6" fill="white"/>
                <circle cx="17" cy="17" r="4" fill="#1A73E8"/>
            </svg>
        `;

        const arrowIcon = L.divIcon({
            html: arrowSvg,
            className: "user-location-arrow",
            iconSize: [34, 34],
            iconAnchor: [17, 17]
        });

        document.addEventListener('DOMContentLoaded', function() {
            const map = window.map;

            // === BOTÓN GPS GRANDE Y VISIBLE ===
            const gpsBtn = L.control({position: 'topleft'});
            gpsBtn.onAdd = function(map) {
                const div = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
                div.style.cssText = `
                    background: white;
                    width: 40px;
                    height: 40px;
                    text-align: center;
                    line-height: 40px;
                    font-weight: bold;
                    font-size: 18px;
                    cursor: pointer;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                    border-radius: 6px;
                    margin: 10px;
                    user-select: none;
                `;
                div.innerHTML = 'GPS';
                div.title = 'Activar mi ubicación';

                div.onclick = function(e) {
                    L.DomEvent.stopPropagation(e);
                    startTracking();
                };

                return div;
            };
            gpsBtn.addTo(map);

            function startTracking() {
                if (watchId) {
                    // Si ya está activo, detener
                    navigator.geolocation.clearWatch(watchId);
                    watchId = null;
                    if (userMarker) map.removeLayer(userMarker);
                    if (userCircle) map.removeLayer(userCircle);
                    return;
                }

                // Iniciar seguimiento
                watchId = navigator.geolocation.watchPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        const accuracy = position.coords.accuracy;
                        const heading = position.coords.heading !== null ? position.coords.heading : 0;
                        const latlng = [lat, lng];

                        // Eliminar marcador anterior
                        if (userMarker) map.removeLayer(userMarker);
                        if (userCircle) map.removeLayer(userCircle);

                        // Marcador con rotación
                        userMarker = L.marker(latlng, {
                            icon: arrowIcon,
                            rotationAngle: heading,
                            rotationOrigin: 'center'
                        }).addTo(map)
                        .bindPopup(`Estás aquí<br>±${Math.round(accuracy)} m`)
                        .openPopup();

                        // Círculo de precisión
                        userCircle = L.circle(latlng, {
                            radius: accuracy,
                            color: '#4285F4',
                            fillColor: '#4285F4',
                            fillOpacity: 0.15,
                            weight: 2
                        }).addTo(map);

                        // Centrar solo si estás fuera del campus
                        const campusBounds = L.latLngBounds([
                            [-2.1515, -79.6045],
                            [-2.1475, -79.6015]
                        ]);
                        if (!campusBounds.contains(latlng)) {
                            map.setView(latlng, 21);
                        }
                    },
                    function(error) {
                        let msg = 'Error GPS: ';
                        if (error.code === 1) msg += 'Permiso denegado.';
                        else if (error.code === 2) msg += 'Posición no disponible.';
                        else if (error.code === 3) msg += 'Tiempo agotado.';
                        else msg += error.message;
                        alert(msg);
                    },
                    {
                        enableHighAccuracy: true,
                        maximumAge: 0,
                        timeout: 15000
                    }
                );
            }

            // Detener al salir de la página
            window.addEventListener('beforeunload', () => {
                if (watchId) navigator.geolocation.clearWatch(watchId);
            });
        });
    </script>

    <style>
        .user-location-arrow svg {
            filter: drop-shadow(0 1px 4px rgba(0,0,0,0.5));
            transition: transform 0.2s ease-out;
        }
        .leaflet-control-custom {
            margin: 10px !important;
        }
        .leaflet-popup-content {
            font-family: 'Roboto', sans-serif;
            text-align: center;
            margin: 8px;
            font-size: 14px;
        }
        .leaflet-popup-content-wrapper {
            border-radius: 12px;
        }
    </style>
    """))

    # Renderizar el mapa
    mapa = mapa._repr_html_()
    return render(request, 'ubicaciones/mapa.html', {'mapa': mapa})