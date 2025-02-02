import json
import pandas as pd
import geopandas as gpd
import folium
from folium.features import MacroElement
from branca.element import Template
from io import StringIO

def main():
    # --------------------------------------------
    # 1. Dataindlæsning – CSV-data med udviklings-tal
    # --------------------------------------------
    data = """Kommune	Hjemmeboende_2010	Hjemmeboende_2023	Hjemmeboende_2024	Population_2010	Population_2023	Population_2024	Region	Andel_2010	Andel_2023	Andel_2024	pct_change_2010_2024
Aabenraa	856	1147	1166	2597	2645	2629	Region Syddanmark	0,32961109	0,433648393	0,443514644	34,5569546
Aalborg	2138	3151	3448	17463	23346	22375	Region Nordjylland	0,122430281	0,134969588	0,154100559	25,8680101
Aarhus	3761	5934	6442	35360	46580	46426	Region Midtjylland	0,106363122	0,127393731	0,138758454	30,45729712
Albertslund	575	908	938	1920	1995	2025	Region Hovedstaden	0,299479167	0,455137845	0,463209877	54,67181965
Allerød	403	646	688	707	882	905	Region Hovedstaden	0,570014144	0,732426304	0,760220994	33,36879481
Assens	619	885	923	1464	1603	1647	Region Syddanmark	0,422814208	0,552089832	0,560412872	32,54352899
Ballerup	725	1287	1384	2568	2679	2964	Region Hovedstaden	0,282320872	0,480403135	0,466936572	65,39215413
Billund	443	552	612	1217	1224	1315	Region Syddanmark	0,36400986	0,450980392	0,46539924	27,85347055
Bornholm	520	572	627	1440	1277	1261	Region Hovedstaden	0,361111111	0,447924824	0,497224425	37,69291771
Brøndby	679	1009	1058	1788	2245	2684	Region Hovedstaden	0,379753915	0,449443207	0,394187779	3,800846779
Brønderslev	494	668	706	1406	1408	1397	Region Nordjylland	0,351351351	0,474431818	0,505368647	43,83569187
Dragør	190	289	333	335	378	422	Region Hovedstaden	0,567164179	0,764550265	0,789099526	39,13070591
Egedal	609	1121	1225	1182	1721	1825	Region Hovedstaden	0,515228426	0,651365485	0,671232877	30,27869627
Esbjerg	1499	2004	2146	7044	6799	6517	Region Syddanmark	0,212805224	0,294749228	0,329292619	54,73897334
Faaborg-Midtfyn	792	974	1028	1807	1873	1900	Region Syddanmark	0,438295517	0,520021356	0,541052632	23,44471026
Fanø	35	60	57	61	75	74	Region Syddanmark	0,573770492	0,8	0,77027027	34,24710425
Favrskov	639	1133	1269	1503	1773	1882	Region Midtjylland	0,425149701	0,639029893	0,674282678	58,59888342
Faxe	564	753	850	1332	1500	1573	Region Sjælland	0,423423423	0,502	0,540368722	27,61899609
Fredensborg	645	987	1069	1383	1522	1631	Region Hovedstaden	0,46637744	0,64848883	0,655426119	40,53555388
Fredericia	601	963	1023	2507	2628	2703	Region Syddanmark	0,239728759	0,366438356	0,378468368	57,87357733
Frederiksberg	821	1638	1784	7933	9230	8925	Region Hovedstaden	0,103491743	0,177464789	0,199887955	93,14386705
Frederikshavn	877	918	949	2664	2238	2259	Region Nordjylland	0,329204204	0,410187668	0,420097388	27,60997061
Frederikssund	761	1152	1167	1668	1883	1886	Region Hovedstaden	0,456235012	0,611789697	0,618769883	35,6252517
Furesø	640	985	1082	1305	1451	1553	Region Hovedstaden	0,490421456	0,678842178	0,696716033	42,0647537
Gentofte	919	1645	1748	2895	3312	3364	Region Hovedstaden	0,317443869	0,496678744	0,519619501	63,68862396
Gladsaxe	965	1603	1700	3779	4206	4224	Region Hovedstaden	0,25535856	0,381122206	0,402462121	57,60666902
Glostrup	285	528	586	1296	1348	1415	Region Hovedstaden	0,219907407	0,391691395	0,414134276	88,3221127
Greve	834	1294	1386	1727	2117	2280	Region Sjælland	0,482918356	0,611242324	0,607894737	25,87940174
Gribskov	675	893	1015	1278	1475	1593	Region Hovedstaden	0,528169014	0,605423729	0,637162586	20,63611634
Guldborgsund	801	1031	1075	2836	2691	2692	Region Sjælland	0,282440056	0,383128948	0,399331352	41,38623155
Haderslev	843	1057	1113	2787	2608	2655	Region Syddanmark	0,30247578	0,405291411	0,41920904	38,59259706
Halsnæs	517	677	747	1168	1222	1232	Region Hovedstaden	0,442636986	0,55400982	0,606331169	36,98158708
Hedensted	725	1081	1178	1621	1965	2055	Region Midtjylland	0,447254781	0,550127226	0,57323601	28,16766507
Helsingør	841	1428	1607	2496	2659	2793	Region Hovedstaden	0,336939103	0,537044002	0,575366989	70,76290182
Herlev	490	702	772	1473	1634	1711	Region Hovedstaden	0,332654447	0,429620563	0,45119813	35,63568268
Herning	1265	1967	2027	5285	5263	5099	Region Midtjylland	0,23935667	0,373741212	0,397528927	66,08224352
Hillerød	691	1358	1479	2084	3058	3015	Region Hovedstaden	0,331573896	0,444081099	0,490547264	47,94507923
Hjørring	1014	1216	1238	3190	2940	2822	Region Nordjylland	0,317868339	0,413605442	0,43869596	38,0118455
Holbæk	1097	1667	1741	3196	3448	3515	Region Sjælland	0,343241552	0,483468677	0,495305832	44,30241017
Holstebro	866	1163	1252	3359	3412	3453	Region Midtjylland	0,257814826	0,340855803	0,362583261	40,63708701
Horsens	1123	1699	1848	5173	6176	5932	Region Midtjylland	0,21708873	0,27509715	0,311530681	43,503848
Hvidovre	806	1266	1314	3048	3046	3129	Region Hovedstaden	0,264435696	0,415627052	0,419942474	58,80702973
Høje-Taastrup	897	1300	1404	2587	3175	3585	Region Hovedstaden	0,346733668	0,409448819	0,391631799	12,94888121
Hørsholm	351	516	547	803	778	821	Region Hovedstaden	0,437110834	0,663239075	0,666260658	52,42373452
Ikast-Brande	591	856	929	1773	1941	1974	Region Midtjylland	0,333333333	0,441009789	0,470618034	41,18541033
Ishøj	481	666	640	1270	1562	1556	Region Hovedstaden	0,378740157	0,42637644	0,411311054	8,599800117
Jammerbugt	628	710	777	1478	1429	1468	Region Nordjylland	0,424898512	0,496850945	0,529291553	24,56893559
Kalundborg	641	991	1051	1955	2141	2197	Region Sjælland	0,327877238	0,462867819	0,478379609	45,9020491
Kerteminde	349	485	522	812	867	885	Region Syddanmark	0,429802956	0,559400231	0,589830508	37,2327716
Kolding	1253	1855	2058	5196	5441	5373	Region Syddanmark	0,241147036	0,340929976	0,383026242	58,83514406
København	4696	9902	10495	55199	66544	65632	Region Hovedstaden	0,085074005	0,148803799	0,159906753	87,9619431
Køge	909	1521	1614	2510	3080	3133	Region Sjælland	0,362151394	0,493831169	0,515161187	42,25022885
Langeland	183	207	207	448	381	373	Region Syddanmark	0,408482143	0,543307087	0,554959786	35,8590076
Lejre	421	700	772	747	1015	1129	Region Sjælland	0,563587684	0,689655172	0,683790965	21,32823069
Lemvig	427	478	506	971	868	878	Region Midtjylland	0,439752832	0,550691244	0,576309795	31,05311731
Lolland	589	597	629	1870	1530	1520	Region Sjælland	0,314973262	0,390196078	0,413815789	31,38124386
Lyngby-Taarbæk	695	1206	1333	3429	4424	4449	Region Hovedstaden	0,202682998	0,272603978	0,299617892	47,82586338
Læsø	18	17	22	34	41	45	Region Nordjylland	0,529411765	0,414634146	0,488888889	-7,654320988
Mariagerfjord	733	795	876	1925	1718	1730	Region Nordjylland	0,380779221	0,462747381	0,506358382	32,97952038
Middelfart	501	852	935	1293	1485	1523	Region Syddanmark	0,387470998	0,573737374	0,613919895	58,44279923
Morsø	379	417	456	989	876	896	Region Nordjylland	0,383215369	0,476027397	0,508928571	32,80484357
Norddjurs	631	661	703	1742	1704	1667	Region Midtjylland	0,362227325	0,387910798	0,421715657	16,42292778
Nordfyns	428	596	623	971	1105	1145	Region Syddanmark	0,440782698	0,539366516	0,544104803	23,44059911
Nyborg	436	666	688	1213	1370	1317	Region Syddanmark	0,359439406	0,486131387	0,522399393	45,3372622
Næstved	1038	1664	1766	4157	4490	4524	Region Sjælland	0,249699302	0,370601336	0,390362511	56,33304031
Odder	327	541	590	829	906	981	Region Midtjylland	0,394451146	0,597130243	0,601427115	52,47188945
Odense	2284	3525	3797	16433	21412	20858	Region Syddanmark	0,13898862	0,164627312	0,182040464	30,97508522
Odsherred	450	662	678	1137	1261	1226	Region Sjælland	0,395778364	0,524980174	0,553017945	39,72920065
Randers	1156	1846	1947	5238	5522	5310	Region Midtjylland	0,220694922	0,334299167	0,366666667	66,14186851
Rebild	455	598	664	1037	1007	1040	Region Nordjylland	0,43876567	0,593843098	0,638461538	45,51310228
Ringkøbing-Skjern	986	1275	1423	2658	2589	2697	Region Midtjylland	0,370955606	0,492468134	0,527623285	42,23353873
Ringsted	511	807	853	1548	1863	1922	Region Sjælland	0,330103359	0,433172303	0,443808533	34,44532461
Roskilde	1148	2110	2340	4691	5461	5474	Region Sjælland	0,244723939	0,386376122	0,427475338	74,67655143
Rudersdal	749	1226	1360	2124	2453	2532	Region Hovedstaden	0,352636535	0,499796168	0,537124803	52,31683319
Rødovre	533	949	979	1955	2288	2468	Region Hovedstaden	0,272634271	0,414772727	0,396677472	45,49802196
Samsø	39	47	52	89	85	95	Region Midtjylland	0,438202247	0,552941176	0,547368421	24,9122807
Silkeborg	1266	2078	2302	4275	4605	4765	Region Midtjylland	0,296140351	0,451248643	0,483105981	63,13412869
Skanderborg	845	1472	1596	1854	2284	2341	Region Midtjylland	0,455771305	0,644483363	0,681759932	49,58377672
Skive	746	916	965	2482	2184	2140	Region Midtjylland	0,300564061	0,419413919	0,450934579	50,02944051
Slagelse	1038	1580	1780	4188	4647	4590	Region Sjælland	0,247851003	0,340004304	0,387799564	56,4647953
Solrød	330	565	620	635	938	995	Region Sjælland	0,519685039	0,602345416	0,623115578	19,90254302
Sorø	381	624	657	1148	1170	1173	Region Sjælland	0,331881533	0,533333333	0,560102302	68,76573293
Stevns	376	499	519	774	871	852	Region Sjælland	0,485788114	0,572904707	0,60915493	25,39519029
Struer	302	421	441	901	889	886	Region Midtjylland	0,33518313	0,473565804	0,497742664	48,49872184
Svendborg	812	1192	1204	3072	2918	2879	Region Syddanmark	0,264322917	0,408498972	0,418200764	58,2158556
Syddjurs	538	854	910	1308	1585	1592	Region Midtjylland	0,411314985	0,538801262	0,57160804	38,97087669
Sønderborg	916	1450	1491	3578	3591	3625	Region Syddanmark	0,256008944	0,403787246	0,411310345	60,66249059
Thisted	744	862	934	2070	1984	1994	Region Nordjylland	0,35942029	0,434475806	0,468405216	30,32241887
Tårnby	637	1057	1089	1785	1900	1983	Region Hovedstaden	0,356862745	0,556315789	0,549167927	53,88771591
Tønder	713	708	717	1882	1611	1593	Region Syddanmark	0,378852285	0,439478585	0,450094162	18,80465818
Vallensbæk	217	369	405	548	842	988	Region Hovedstaden	0,395985401	0,43824228	0,409919028	3,518722364
Varde	902	1052	1074	2246	2234	2195	Region Syddanmark	0,40160285	0,470904208	0,48929385	21,83525347
Vejen	732	870	937	1891	1927	1976	Region Syddanmark	0,387096774	0,451478983	0,474190283	22,49915655
Vejle	1440	2613	2811	5123	6521	6537	Region Syddanmark	0,281085302	0,400705413	0,430013768	52,9833703
Vesthimmerlands	677	706	729	1842	1555	1508	Region Nordjylland	0,367535288	0,454019293	0,483421751	31,5307038
Viborg	1268	1898	2012	4463	4692	4755	Region Midtjylland	0,284113825	0,404518329	0,423133544	48,93099411
Vordingborg	515	829	922	1837	1915	1951	Region Sjælland	0,280348394	0,432898172	0,472578165	68,56817266
Ærø	76	73	69	176	167	180	Region Syddanmark	0,431818182	0,437125749	0,383333333	-11,22807018
"""
    # --------------------------------------------
    # 2. Indlæs CSV-data og filtrer til Region Hovedstaden
    # --------------------------------------------
    df = pd.read_csv(StringIO(data), sep="\t", decimal=",")
    # Filtrér til kun de kommuner, hvor kolonnen "Region" er "Region Hovedstaden"
    df_hovedstaden = df[df["Region"] == "Region Hovedstaden"]
    
    # --------------------------------------------
    # 3. Hent GeoJSON-data og merge med CSV-data
    # --------------------------------------------
    geojson_url = "https://raw.githubusercontent.com/magnuslarsen/geoJSON-Danish-municipalities/master/municipalities/municipalities.geojson"
    gdf = gpd.read_file(geojson_url)
    # Merge på feltet "label_dk" (i GeoJSON) med "Kommune" (i CSV)
    merged = gdf.merge(df_hovedstaden, left_on="label_dk", right_on="Kommune", how="left")
    
    # --------------------------------------------
    # 4. Opret et statisk, flot kort
    # --------------------------------------------
    # Vi vælger en baggrund, der giver et rent look
    m = folium.Map(location=[55.75, 12.5], zoom_start=9, tiles="CartoDB Positron")
    
    # Zoom kortet til grænserne for de samlede Region Hovedstaden-kommuner
    bounds = merged.total_bounds  # [minx, miny, maxx, maxy]
    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
    
    # Tilføj et choropleth-lag, der farvekoder kommunerne efter pct_change_2010_2024
    choropleth = folium.Choropleth(
        geo_data=merged.to_json(),
        data=merged,
        columns=["label_dk", "pct_change_2010_2024"],
        key_on="feature.properties.label_dk",
        fill_color="YlOrRd",
        fill_opacity=0.8,
        line_opacity=0.5,
        legend_name="Procentvis stigning (2010-2024)",
        nan_fill_color="white"
    ).add_to(m)
    
    # Tilføj et GeoJSON-lag med tooltips, så man kan se kommuneoplysninger ved hover
    folium.GeoJson(
        merged.to_json(),
        name="Kommuner",
        style_function=lambda feature: {
            "fillColor": "transparent",
            "color": "black",
            "weight": 1,
            "dashArray": "3"
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["label_dk", "pct_change_2010_2024"],
            aliases=["Kommune: ", "Stigning (2010-2024): "],
            localize=True
        )
    ).add_to(m)
    
    # --------------------------------------------
    # 5. Tilføj en flot titel over kortet
    # --------------------------------------------
    title_html = '''
         <h3 align="center" style="font-size:20px; font-family: Arial, sans-serif;">
         <b>Procentvis udvikling i andelen af hjemmeboende unge (20-24 år) i Region Hovedstaden</b>
         </h3>
         '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # --------------------------------------------
    # 6. Gem kortet som en statisk HTML-fil
    # --------------------------------------------
    output_path = r"C:\Users\ruk\OneDrive - Green Power Denmark\APP Stork\Kampagne\bolig\DST tal\Data til SoMe\hovedstaden_static.html"
    m.save(output_path)
    print(f"Statisk kort for Region Hovedstaden gemt som '{output_path}'")

if __name__ == "__main__":
    main()
