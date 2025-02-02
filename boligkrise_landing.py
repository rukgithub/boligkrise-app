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
    
    # Tilføj Font Awesome CSS
    html_content = f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .welcome-box {{
            max-width: 800px;
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1000;
            font-family: 'Segoe UI', Arial, sans-serif;
            border: 2px solid {RV_GREEN};
        }}

        .welcome-box h1 {{
            color: {RV_GREEN};
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            border-bottom: 3px solid {RV_GREEN};
            padding-bottom: 0.5rem;
        }}

        .welcome-box p {{
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
            color: #333;
        }}

        .stat-highlight {{
            background: {RV_GREEN};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            display: inline-block;
            margin: 0.5rem 0;
            font-weight: bold;
        }}

        .solutions-box {{
            max-width: 900px;
            background: rgba(255, 255, 255, 0.97);
            padding: 2.5rem;
            border-radius: 15px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1000;
            display: none;
            font-family: 'Segoe UI', Arial, sans-serif;
            border: 2px solid {RV_GREEN};
        }}

        .solutions-box h2 {{
            color: {RV_GREEN};
            font-size: 2.2rem;
            margin-bottom: 2rem;
            text-align: center;
            border-bottom: 3px solid {RV_GREEN};
            padding-bottom: 0.5rem;
        }}

        .solution-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 1.5rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
            transition: transform 0.2s;
        }}

        .solution-item:hover {{
            transform: translateX(10px);
            background: #f0f2f5;
        }}

        .solution-icon {{
            font-size: 2rem;
            color: {RV_GREEN};
            margin-right: 1rem;
            min-width: 50px;
            text-align: center;
        }}

        .solution-content {{
            flex: 1;
        }}

        .solution-content h3 {{
            color: {RV_GREEN};
            margin-bottom: 0.5rem;
            font-size: 1.3rem;
        }}

        .nav-buttons {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1001;
            display: flex;
            gap: 1rem;
        }}

        .nav-button {{
            background: {RV_GREEN};
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}

        .nav-button:hover {{
            background: {RV_MAGENTA};
            transform: translateY(-2px);
        }}

        .blockquote {{
            border-left: 4px solid {RV_GREEN};
            padding-left: 1rem;
            margin: 1.5rem 0;
            font-style: italic;
            color: #555;
        }}

        .crisis-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }}

        .stat-card {{
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid {RV_GREEN};
        }}

        @media (max-width: 768px) {{
            .welcome-box, .solutions-box {{
                width: 90%;
                margin: 1rem;
                padding: 1.5rem;
            }}

            .nav-buttons {{
                bottom: 1rem;
                right: 1rem;
            }}
        }}

        .tooltip-content {{
            display: none;
            position: absolute;
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border: 2px solid {RV_GREEN};
            max-width: 300px;
            z-index: 1002;
        }}

        .solution-item:hover .tooltip-content {{
            display: block;
            left: 100%;
            top: 0;
            margin-left: 1rem;
        }}

        .action-buttons {{
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
            justify-content: center;
        }}

        .action-button {{
            background: {RV_GREEN};
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s;
            text-decoration: none;
        }}

        .action-button:hover {{
            background: {RV_MAGENTA};
            transform: translateY(-2px);
        }}

        .secondary-button {{
            background: white;
            color: {RV_GREEN};
            border: 2px solid {RV_GREEN};
        }}

        .secondary-button:hover {{
            background: {RV_GREEN};
            color: white;
        }}
    </style>

    <div class="welcome-box" id="welcomeBox">
        <h1><i class="fas fa-home"></i> Boligkrisen rammer unge i hovedstaden</h1>
        
        <p>
            Prisstigninger og mangel på studieboliger tvinger et rekordhøjt antal unge til at blive boende hjemme hos mor
            og far. I 2010 boede mindre end hver fjerde ung fra 20-24 år hos deres forældre. I dag er det
            over hver tredje. Og hovedstadskommuner som Frederiksberg, København og Glostrup er de absolutte højdespringere.
        </p>
        
        <div class="crisis-stats">
            <div class="stat-card">
                <i class="fas fa-chart-line"></i>
                <h3>Frederiksberg</h3>
                <p>+93% (fra 10,3% til 20,0%)</p>
            </div>
            <div class="stat-card">
                <i class="fas fa-city"></i>
                <h3>København</h3>
                <p>+88% (fra 8,5% til 16,0%)</p>
            </div>
            <div class="stat-card">
                <i class="fas fa-building"></i>
                <h3>Glostrup</h3>
                <p>+88% (fra 22,0% til 41,4%)</p>
            </div>
        </div>

        <div class="blockquote">
            <i class="fas fa-quote-left"></i>
            "Vi står i en reel boligkrise for unge i hovedstadsområdet. Det er alvorligt, fordi manglen på studieboliger i
            sidste ende gør det sværere at gennemføre en uddannelse. Især for studerende, som ikke bliver støttet
            økonomisk af deres forældre. Boligpriserne er med til at skabe ulighed i uddannelsessystemet, og det er en
            politisk opgave at rette op på den skævhed."
            <footer style="margin-top: 0.5rem; font-size: 0.9rem;">
                - Ruben Kidde, Formand for Undervisningsudvalget på Frederiksberg
            </footer>
        </div>

        <p>
            Da jeg flyttede hjemmefra, kunne jeg betale min studiebolig med halvdelen af min SU. Det er fuldstændig
            umuligt for de fleste studerende nu. Boligprisudviklingen har skabt en ekstrem skævvridning mellem
            generationerne, hvor mange i mine forældres generation har tjent større summer på deres bolig, end de
            nogensinde har kunnet på arbejdsmarkedet.
        </p>

        <div class="action-buttons">
            <button class="action-button" onclick="hideWelcome()">
                <i class="fas fa-map-marked-alt"></i> Udforsk kortet
            </button>
            <button class="action-button secondary-button" onclick="showSolutions()">
                <i class="fas fa-lightbulb"></i> Se løsningerne
            </button>
        </div>
    </div>

    <div class="solutions-box" id="solutionsBox">
        <h2><i class="fas fa-lightbulb"></i> Rubens ungeboligpakke</h2>
        
        <div class="solution-item">
            <div class="solution-icon">
                <i class="fas fa-percentage"></i>
            </div>
            <div class="solution-content">
                <h3>Øget rentefradrag for førstegangskøbere</h3>
                <p>Gør det billigere for unge at komme ind på boligmarkedet</p>
                <div class="tooltip-content">
                    Dette forslag vil reducere de årlige skattebetalinger for førstegangskøbere, da de vil kunne
                    trække en større del af deres renteudgifter fra i skat. Det betyder, at de månedlige
                    udgifter til boligen falder, hvilket gør det mere overkommeligt for unge at eje en bolig.
                </div>
            </div>
        </div>

        <div class="solution-item">
            <div class="solution-icon">
                <i class="fas fa-file-invoice-dollar"></i>
            </div>
            <div class="solution-content">
                <h3>Fjernelse af tinglysningsafgift</h3>
                <p>Reducer startomkostningerne ved boligkøb</p>
                <div class="tooltip-content">
                    Ved at fjerne tinglysningsafgiften vil man reducere de initiale omkostninger ved boligkøb.
                    Tinglysningsafgiften er en engangsudgift, der betales ved overdragelse af ejendommen,
                    og ved at fjerne den vil det især hjælpe førstegangskøbere, som ofte har begrænsede
                    midler til rådighed.
                </div>
            </div>
        </div>

        <div class="solution-item">
            <div class="solution-icon">
                <i class="fas fa-piggy-bank"></i>
            </div>
            <div class="solution-content">
                <h3>Brug pensionsopsparing til boligkøb</h3>
                <p>Gør det muligt at bruge pensionsmidler til udbetalingen</p>
                <div class="tooltip-content">
                    Ved at give unge mulighed for at bruge en del af deres pensionsmidler til
                    udbetalingen på en ejerbolig, kan vi lette vejen ind på boligmarkedet og give
                    flere mulighed for at etablere sig med egen bolig tidligere i livet.
                </div>
            </div>
        </div>

        <div class="solution-item">
            <div class="solution-icon">
                <i class="fas fa-building-user"></i>
            </div>
            <div class="solution-content">
                <h3>Flere almene ungdomsboliger</h3>
                <p>Kun én ungdomsbolig per tolvte studerende i København og Frederiksberg</p>
                <div class="tooltip-content">
                    Vi skal oprette en ungdomsboligfond og øremærke midler til kommuner, så der kan opføres billige
                    kollegie- og studieboliger uden forsinkende bureaukrati. I dag er der kun én almen ungdomsbolig 
                    for hver tolvte studerende i København og Frederiksberg - det er helt utilstrækkeligt.
                </div>
            </div>
        </div>

        <div class="solution-item">
            <div class="solution-icon">
                <i class="fas fa-home"></i>
            </div>
            <div class="solution-content">
                <h3>Lempe krav om store gennemsnitsstørrelser</h3>
                <p>Gør det muligt at bygge flere små, billige boliger</p>
                <div class="tooltip-content">
                    Ved at lempe eller helt fjerne krav om store gennemsnitsstørrelser ved nybyggeri i
                    kommuner kan vi opføre flere små lejligheder, særligt rettet mod unge og studerende,
                    som efterspørger billigere boliger. Dette vil øge udbuddet af betalelige boliger markant.
                </div>
            </div>
        </div>

        <div class="action-buttons">
            <button class="action-button" onclick="hideWelcome()">
                <i class="fas fa-map-marked-alt"></i> Udforsk kortet
            </button>
            <button class="action-button secondary-button" onclick="showWelcome()">
                <i class="fas fa-arrow-left"></i> Tilbage til intro
            </button>
        </div>
    </div>

    <div class="nav-buttons">
        <button class="nav-button" onclick="showWelcome()">
            <i class="fas fa-home"></i> Intro
        </button>
        <button class="nav-button" onclick="showSolutions()">
            <i class="fas fa-lightbulb"></i> Løsninger
        </button>
    </div>

    <script>
        function hideWelcome() {{
            document.getElementById('welcomeBox').style.display = 'none';
            document.getElementById('solutionsBox').style.display = 'none';
            map.setView([55.676098, 12.568337], 11);
        }}

        function showWelcome() {{
            document.getElementById('welcomeBox').style.display = 'block';
            document.getElementById('solutionsBox').style.display = 'none';
        }}

        function showSolutions() {{
            document.getElementById('solutionsBox').style.display = 'block';
            document.getElementById('welcomeBox').style.display = 'none';
        }}
    </script>
    """
    
    m.get_root().html.add_child(folium.Element(html_content))
    
    # Gem kortet
    output_path = "index.html"
    m.save(output_path)
    print(f"Interaktivt kort med landing page gemt som '{output_path}'")

if __name__ == "__main__":
    main() 