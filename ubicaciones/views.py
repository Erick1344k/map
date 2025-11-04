from django.shortcuts import render
import folium
from folium.plugins import LocateControl

def mapa_view(request):
    # Centro UNEMI
    centro_unemi = [-2.1496, -79.6031]

    # Crear mapa con ID fijo
    mapa = folium.Map(
        location=centro_unemi,
        zoom_start=19,
        min_zoom=17,
        max_zoom=21,
        control_scale=True,
        tiles='OpenStreetMap',
        width='100%',
        height='100%',
        html_id='mapa-unemi'  # ID fijo para el mapa
    )

    # Marcadores fijos
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
            popup=folium.Popup(punto["nombre"], max_width=150),
            tooltip=punto["nombre"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mapa)

    # Control de ubicación
    LocateControl(
        auto_start=False,
        position='topright',
        flyTo=True,
        keepCurrentZoomLevel=True,
        setView=True,
        cacheLocation=True,
        strings={
            'title': 'Activar seguimiento',
            'popup': 'Estás aquí'
        },
        locateOptions={
            'enableHighAccuracy': True,
            'watch': True,
            'maximumAge': 0,
            'timeout': 15000
        }
    ).add_to(mapa)

    # JavaScript para inicialización, seguimiento y botón de ubicación
    mapa.get_root().html.add_child(folium.Element('''
    <script>
        document.addEventListener("DOMContentLoaded", function () {
            console.log("Inicializando mapa...");

            // Verificar que Leaflet está cargado
            if (!window.L) {
                console.error("Leaflet no está cargado");
                alert("Error: Leaflet no está disponible. Revisa la consola.");
                return;
            }

            // Buscar el contenedor del mapa
            const mapContainer = document.getElementById('mapa-container');
            if (!mapContainer) {
                console.error("Contenedor #mapa-container no encontrado");
                alert("Error: Contenedor #mapa-container no encontrado.");
                return;
            }

            // Verificar o crear el div del mapa
            let mapDiv = document.getElementById('mapa-unemi');
            if (!mapDiv) {
                console.log("Creando div del mapa...");
                mapDiv = document.createElement('div');
                mapDiv.id = 'mapa-unemi';
                mapDiv.style.width = '100%';
                mapDiv.style.height = '100%';
                mapContainer.appendChild(mapDiv);
            } else {
                console.log("Mapa encontrado, ID: mapa-unemi");
            }

            // Inicializar el mapa
            let map;
            try {
                map = L.map('mapa-unemi', {
                    center: [-2.1496, -79.6031],
                    zoom: 19
                });
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);
                console.log("Mapa inicializado correctamente");
            } catch (e) {
                console.error("Error al inicializar el mapa: ", e);
                alert("Error al inicializar el mapa: " + e.message);
                return;
            }

            // Agregar LocateControl manualmente
            try {
                L.control.locate({
                    position: 'topright',
                    flyTo: true,
                    keepCurrentZoomLevel: true,
                    setView: true,
                    cacheLocation: true,
                    strings: {
                        title: 'Activar seguimiento',
                        popup: 'Estás aquí'
                    },
                    locateOptions: {
                        enableHighAccuracy: true,
                        watch: true,
                        maximumAge: 0,
                        timeout: 15000
                    }
                }).addTo(map);
                console.log("LocateControl añadido correctamente");
            } catch (e) {
                console.error("Error al añadir LocateControl: ", e);
                alert("Error al añadir el control de ubicación: " + e.message);
                return;
            }

            // Configurar botón de ubicación
            let isFollowing = false;
            let userMarker = null;
            const locateBtn = document.querySelector('.leaflet-control-locate a');
            if (!locateBtn) {
                console.error("Botón de ubicación no encontrado");
                alert("Error: Botón de ubicación no encontrado.");
                return;
            }

            console.log("Botón de ubicación encontrado");
            locateBtn.title = "Activar seguimiento de ubicación";

            locateBtn.addEventListener('click', function () {
                if (!isFollowing) {
                    console.log("Activando seguimiento...");
                    map.locate({
                        watch: true,
                        setView: true,
                        maxZoom: 19,
                        enableHighAccuracy: true
                    });

                    locateBtn.classList.add('active');
                    locateBtn.title = "Detener seguimiento";
                    isFollowing = true;

                    map.on('locationfound', function (e) {
                        console.log("Ubicación encontrada: ", e.latlng);
                        if (userMarker) {
                            userMarker.setLatLng(e.latlng);
                        } else {
                            userMarker = L.circleMarker(e.latlng, {
                                radius: 8,
                                fillColor: "#4285F4",
                                color: "#4285F4",
                                weight: 2,
                                opacity: 1,
                                fillOpacity: 0.6
                            }).addTo(map).bindPopup("Estás aquí");
                        }
                        map.setView(e.latlng, 19);
                    });

                    map.on('locationerror', function (e) {
                        console.error("Error de geolocalización: ", e.message);
                        alert("No se pudo obtener la ubicación: " + e.message);
                    });

                } else {
                    console.log("Desactivando seguimiento...");
                    map.stopLocate();
                    if (userMarker) {
                        map.removeLayer(userMarker);
                        userMarker = null;
                    }
                    locateBtn.classList.remove('active');
                    locateBtn.title = "Activar seguimiento de ubicación";
                    isFollowing = false;
                }
            });
        });
    </script>
    '''))

    # Estilos personalizados
    mapa.get_root().html.add_child(folium.Element('''
    <style>
        .leaflet-control-locate a {
            font-size: 20px !important;
            width: 34px !important;
            height: 34px !important;
            line-height: 34px !important;
            background-color: white !important;
            border: 2px solid rgba(0,0,0,0.2) !important;
            border-radius: 4px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
            transition: all 0.2s ease;
        }
        .leaflet-control-locate a:hover {
            background-color: #f4f4f4 !important;
        }
        .leaflet-control-locate.active a {
            background-color: #4285F4 !important;
            color: white !important;
        }
        .leaflet-popup-content {
            font-family: 'Roboto', sans-serif;
            font-size: 14px;
            text-align: center;
        }
        #mapa-container, #mapa-container > div {
            width: 100% !important;
            height: 100% !important;
        }
    </style>
    '''))

    # Renderizar sin iframe
    mapa_html = mapa.get_root().render()

    return render(request, 'ubicaciones/mapa.html', {'mapa_html': mapa_html})