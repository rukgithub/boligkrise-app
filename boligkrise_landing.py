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
    html_content = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

    <style>
      /* Her er de farver, du brugte før */
      :root {
        --rv-green: #009540;
        --rv-magenta: #E5007E;
        --rv-black: #000000;
        --rv-gray: #F0F0F0;
        --rv-white: #FFFFFF;
      }

      body, html {
        margin: 0;
        padding: 0;
        font-family: 'Segoe UI', Arial, sans-serif;
        height: 100%;
        overflow: hidden; /* Kortet fylder hele skærmen; overlays scroller */
      }

      #map {
        width: 100%;
        height: 100%;
        position: relative;
      }

      /* Overordnet boksdesign - mere luft, rundede hjørner, skygge */
      .overlay-box {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(255, 255, 255, 0.97);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        border: 2px solid var(--rv-green);
        max-width: 700px;        /* Lad boksen have en fornuftig maxbredde */
        width: 90%;              /* Fyld 90% af skærmen på mobil */
        max-height: 80vh;        /* Undgå at boksen bliver for høj */
        overflow-y: auto;        /* Gør det muligt at scrolle */
      }

      .overlay-box h1, .overlay-box h2 {
        color: var(--rv-green);
        border-bottom: 3px solid var(--rv-green);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
      }

      .overlay-box p {
        line-height: 1.6;
        margin-bottom: 1rem;
        color: #333;
      }

      .overlay-box .blockquote {
        border-left: 4px solid var(--rv-green);
        padding-left: 1rem;
        margin: 1.5rem 0;
        font-style: italic;
        color: #555;
      }

      .overlay-box footer {
        font-size: 0.9rem;
        color: #555;
      }

      .crisis-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
      }

      .stat-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid var(--rv-green);
      }

      .action-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 1.5rem;
        justify-content: center;
      }

      .action-button {
        background: var(--rv-green);
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
      }

      .action-button:hover {
        background: var(--rv-magenta);
        transform: translateY(-2px);
      }

      .action-button.secondary-button {
        background: white;
        color: var(--rv-green);
        border: 2px solid var(--rv-green);
      }

      .action-button.secondary-button:hover {
        background: var(--rv-green);
        color: white;
      }

      /* Løsningselementerne */
      .solution-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        transition: transform 0.2s;
      }

      .solution-item:hover {
        transform: translateX(5px);
        background: #f0f2f5;
      }

      .solution-icon {
        font-size: 2rem;
        color: var(--rv-green);
        min-width: 40px;
        text-align: center;
      }

      .solution-content h3 {
        color: var(--rv-green);
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
      }

      .solution-content p {
        margin-bottom: 0.5rem;
        color: #333;
      }

      .tooltip-content {
        display: none;
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 2px solid var(--rv-green);
        max-width: 300px;
        position: absolute;
        z-index: 1002;
      }

      .solution-item:hover .tooltip-content {
        display: block;
      }

      /* Knapper til at åbne/lukke overlays */
      .nav-buttons {
        position: absolute;
        bottom: 1rem;
        right: 1rem;
        z-index: 1001;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
      }

      .nav-button {
        background: var(--rv-green);
        color: white;
        border: none;
        padding: 0.8rem 1.2rem;
        border-radius: 25px;
        cursor: pointer;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
      }

      .nav-button:hover {
        background: var(--rv-magenta);
        transform: translateY(-2px);
      }

      /* RESPONSIVE FORBEDRINGER VIA MEDIA QUERIES */
      @media (max-width: 768px) {
        .overlay-box {
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 90%;
          max-width: 600px;
          max-height: 80vh;
        }

        .action-button {
          width: 100%;
          justify-content: center;
        }

        .nav-buttons {
          flex-direction: column;
          bottom: 1rem;
          right: 1rem;
        }

        .solution-content h3 {
          font-size: 1.1rem;
        }

        .solution-icon {
          font-size: 1.8rem;
        }
      }
    </style>

    <!-- HTML: De to bokse, vi viser/skjuler -->
    <div class="overlay-box" id="welcomeBox">
      <h1><i class="fas fa-home"></i> Boligkrisen rammer unge i hovedstaden</h1>
      
      <p>
        Prisstigninger og mangel på studieboliger tvinger et rekordhøjt antal unge til at blive boende hjemme
        hos mor og far. I 2010 boede mindre end hver fjerde ung fra 20-24 år hos deres forældre. I dag er det
        over hver tredje. Og hovedstadskommuner som Frederiksberg, København og Glostrup er de absolutte
        højdespringere.
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
        "Vi står i en reel boligkrise for unge i hovedstadsområdet. Det er alvorligt, fordi manglen på
        studieboliger i sidste ende gør det sværere at gennemføre en uddannelse. Især for studerende, som
        ikke bliver støttet økonomisk af deres forældre. Boligpriserne er med til at skabe ulighed i
        uddannelsessystemet, og det er en politisk opgave at rette op på den skævhed."
        <footer>- Ruben Kidde, Formand for Undervisningsudvalget på Frederiksberg</footer>
      </div>

      <p>
        Da jeg flyttede hjemmefra, kunne jeg betale min studiebolig med halvdelen af min SU. Det er
        fuldstændig umuligt for de fleste studerende nu. Boligprisudviklingen har skabt en ekstrem
        skævvridning mellem generationerne, hvor mange i mine forældres generation har tjent større
        summer på deres bolig, end de nogensinde har kunnet på arbejdsmarkedet.
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

    <div class="overlay-box" id="solutionsBox" style="display: none;">
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
            trække en større del af renteudgifterne fra i skat. Det betyder, at de månedlige udgifter
            falder, hvilket gør det mere overkommeligt for unge at eje en bolig.
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
            Det hjælper især førstegangskøbere, som ofte har begrænsede midler til rådighed.
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
          <p>Kun én ungdomsbolig per tolvte studerende i Kbh. og Frederiksberg</p>
          <div class="tooltip-content">
            Vi skal oprette en ungdomsboligfond og øremærke midler til kommuner, så der kan
            opføres billige kollegie- og studieboliger. I dag er der kun én almen
            ungdomsbolig for hver tolvte studerende i København og Frederiksberg.
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
            Ved at lempe eller helt fjerne krav om store gennemsnitsstørrelser ved nybyggeri
            kan vi opføre flere små lejligheder rettet mod unge og studerende, som efterspørger
            billigere boliger. Dette øger udbuddet af betalelige boliger markant.
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

    <!-- Knapper til at springe til intro/løsninger uden at gå ud af kortet -->
    <div class="nav-buttons">
      <button class="nav-button" onclick="showWelcome()">
        <i class="fas fa-home"></i> Intro
      </button>
      <button class="nav-button" onclick="showSolutions()">
        <i class="fas fa-lightbulb"></i> Løsninger
      </button>
    </div>

    <script>
      /* Gør folium-map tilgængelig som 'map' i scriptet */
      let map = document.querySelector('.folium-map');

      function hideWelcome() {
        document.getElementById('welcomeBox').style.display = 'none';
        document.getElementById('solutionsBox').style.display = 'none';
        // eventuelt sæt zoom/center her om ønsket
      }

      function showWelcome() {
        document.getElementById('welcomeBox').style.display = 'block';
        document.getElementById('solutionsBox').style.display = 'none';
      }

      function showSolutions() {
        document.getElementById('solutionsBox').style.display = 'block';
        document.getElementById('welcomeBox').style.display = 'none';
      }
    </script>
    """
    
    m.get_root().html.add_child(folium.Element(html_content))
    
    # Gem kortet
    output_path = "index.html"
    m.save(output_path)
    print(f"Interaktivt kort med landing page gemt som '{output_path}'")

if __name__ == "__main__":
    main() 