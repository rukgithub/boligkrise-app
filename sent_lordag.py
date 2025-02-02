import json
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import Search, Fullscreen
from branca.element import MacroElement, Template, Figure
from io import StringIO

# Opdaterer farver til Radikale Venstres designguide
RV_GREEN = '#009540'
RV_MAGENTA = '#E5007E'
RV_BLACK = '#000000'
RV_GRAY = '#F0F0F0'
RV_WHITE = '#FFFFFF'

def main():
    # --------------------------------------------
    # 1. Indlæs data og forbered det
    # --------------------------------------------
    # Indlæs GeoJSON-fil med kommunegrænser
    geojson_url = "https://raw.githubusercontent.com/magnuslarsen/geoJSON-Danish-municipalities/master/municipalities/municipalities.geojson"
    kommuner = gpd.read_file(geojson_url)
    
    # Indlæs CSV-data med udviklings-tal
    df = pd.read_csv("NY Kopi af DST_Kommune_20_24.csv", 
                     encoding='utf-8', 
                     sep=';',
                     decimal=',')
    
    # Filtrer Bornholm fra og behold kun Region Hovedstaden
    df_hovedstaden = df[
        (df['Region'] == 'Region Hovedstaden') & 
        (df['Kommune'] != 'Bornholm')
    ].copy()
    
    # Beregn procenttal
    df_hovedstaden["Andel_2010_pct"] = df_hovedstaden["Andel_2010"] * 100
    df_hovedstaden["Andel_2024_pct"] = df_hovedstaden["Andel_2024"] * 100
    df_hovedstaden["pct_change_2010_2024"] = ((df_hovedstaden["Andel_2024"] / df_hovedstaden["Andel_2010"]) - 1) * 100
    
    # Afrund alle procenttal til én decimal
    for col in ['Andel_2010_pct', 'Andel_2024_pct', 'pct_change_2010_2024']:
        df_hovedstaden[col] = df_hovedstaden[col].round(1)
    
    # Forbered GeoJSON data
    merged = kommuner.merge(df_hovedstaden, left_on='label_dk', right_on='Kommune')
    
    # --------------------------------------------
    # 2. Opret et interaktivt kort med moderne design
    # --------------------------------------------
    m = folium.Map(
        location=[55.7, 12.5],
        zoom_start=9,
        tiles='cartodbpositron',
        control_scale=True
    )
    
    # Tilføj fuldskærmsknap
    Fullscreen().add_to(m)
    
    # Fast zoom til Region Hovedstaden (uden Bornholm)
    m.fit_bounds([[55.5, 12.0], [56.0, 12.7]])
    
    # Opret choropleth lag med RV farver
    choropleth = folium.Choropleth(
        geo_data=merged.to_json(),
        name='choropleth',
        data=merged,
        columns=['label_dk', 'pct_change_2010_2024'],
        key_on='feature.properties.label_dk',
        fill_color='RdYlGn_r',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Stigning i andel hjemmeboende unge (20-24 år)',
        smooth_factor=0.5,
        nan_fill_color="white",
        highlight=True
    ).add_to(m)
    
    # Tilføj GeoJSON lag for bedre interaktivitet
    geojson_layer = folium.GeoJson(
        merged.to_json(),
        name="Kommuner",
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': RV_GREEN,
            'weight': 1,
            'dashArray': '3'
        },
        highlight_function=lambda x: {
            'fillColor': RV_MAGENTA,
            'color': RV_MAGENTA,
            'weight': 2,
            'dashArray': '',
            'fillOpacity': 0.1
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[
                'label_dk',
                'Andel_2010_pct',
                'Andel_2024_pct',
                'pct_change_2010_2024',
                'Hjemmeboende_2024'
            ],
            aliases=[
                'Kommune',
                'Andel hjemmeboende 2010 (%)',
                'Andel hjemmeboende 2024 (%)',
                'Stigning 2010-2024 (%)',
                'Antal unge (20-24 år) i 2024'
            ],
            localize=True,
            sticky=True,
            labels=True,
            style="""
                background-color: white;
                border: 2px solid #009540;
                border-radius: 5px;
                box-shadow: 3px 3px 6px rgba(0,0,0,0.2);
                font-size: 14px;
                font-family: Arial, sans-serif;
                padding: 12px;
            """
        )
    ).add_to(m)
    
    # Tilføj diskret søgefunktion
    Search(
        layer=geojson_layer,
        geom_type="Polygon",
        placeholder="Søg efter kommune...",
        collapsed=True,
        search_label="label_dk",
        search_zoom=12
    ).add_to(m)
    
    # Tilføj velkomstboks med RV styling
    welcome_html = """
    <div id="welcome" style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0,0,0,0.2);
        z-index: 1000;
        max-width: 500px;
        font-family: Arial, sans-serif;
    ">
        <h2 style="color: #009540; margin-bottom: 15px;">Boligkrise: Eksplosiv stigning i hjemmeboende unge</h2>
        <p style="margin-bottom: 15px;">Prisstigninger og mangel på studieboliger tvinger et rekordhøjt antal unge til 
        at blive boende hjemme. I 2010 boede mindre end hver fjerde ung (20-24 år) 
        hos forældrene - i dag er det over hver tredje.</p>
        <div style="background: #F0F0F0; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <p style="font-weight: bold; margin-bottom: 10px;">Største stigninger:</p>
            <ul style="margin: 0; padding-left: 20px;">
                <li>Frederiksberg: +93,1% (fra 10,3% til 20,0%)</li>
                <li>København: +87,9% (fra 8,5% til 16,0%)</li>
                <li>Glostrup: +88,3% (fra 22,0% til 41,4%)</li>
            </ul>
        </div>
        <p style="color: #E5007E; font-weight: bold; margin: 15px 0;">
        Ruben Kidde sætter fokus på boligkrisen og foreslår en ambitiøs ungeboligpakke 
        som løsning på problemet.</p>
        <button onclick="closeWelcome()" style="
            background: #009540;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            width: 200px;
            margin: 10px auto;
            display: block;
        ">Udforsk kortet</button>
    </div>
    
    <script>
    function closeWelcome() {
        document.getElementById('welcome').style.display = 'none';
        map.flyTo([55.7, 12.5], 11, {
            duration: 1.5,
            easeLinearity: 0.5
        });
    }
    </script>
    """
    
    m.get_root().html.add_child(folium.Element(welcome_html))
    
    # Gem kortet
    output_path = "hovedstaden_boligkrise.html"
    m.save(output_path)
    print(f"Interaktivt kort over boligkrisen gemt som '{output_path}'")

if __name__ == "__main__":
    main()
