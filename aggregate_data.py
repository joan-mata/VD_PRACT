import pandas as pd
import numpy as np
import urllib.request
import ssl
import os
import json
import unicodedata
import re
import hashlib

def remove_accents(input_str):
    if not isinstance(input_str, str):
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_muni_name(name):
    if not isinstance(name, str):
        return ""
    
    # Handle name inversions like "Cogul, el" -> "el Cogul"
    if ',' in name:
        parts = name.split(',')
        if len(parts) == 2:
            name = parts[1].strip() + " " + parts[0].strip()
            
    name = name.upper()
    name = remove_accents(name)
    name = name.replace('.', '')
    name = re.sub(r'\bST\b', 'SANT', name)
    name = re.sub(r'\bSTA\b', 'SANTA', name)
    name = re.sub(r'\bMPAL\b', 'MUNICIPAL', name)
    
    # Remove standard articles at start
    name = re.sub(r'^(L\'|LA\s+|EL\s+|LES\s+|ELS\s+|ES\s+)', '', name)
    name = name.replace("D'ALT", "ALT")
    name = name.replace("D'URGELL", "URGELL")
    name = name.replace("DE LLOBREGAT", "LLOBREGAT")
    name = name.replace("DE LA SELVA", "SELVA")
    name = name.replace("DE TERA", "TERA")
    name = name.replace("DE TER", "TER")
    name = name.replace("DE PARANYS", "PARANYS")
    
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def get_core_muni(muni_name):
    if not isinstance(muni_name, str):
        return ""
    # E.g. "Vallès Occidental Nord-est (Matadepera)" -> "Matadepera"
    match = re.search(r'\(([^)]+)\)', muni_name)
    if match:
        content = match.group(1)
        # If multiple like "Canyelles - Olivella", return the first one
        parts = [p.strip() for p in content.split('-')]
        return parts[0]
        
    # E.g. "Sant Joan les Fonts - Besalú" -> "Sant Joan les Fonts"
    if ' - ' in muni_name:
        parts = [p.strip() for p in muni_name.split(' - ')]
        return parts[0]
        
    return muni_name

def get_deterministic_jitter(name, scale=0.007):
    # Genera un desfase determinista basado en el hash del nombre
    h = hashlib.md5(name.encode('utf-8')).hexdigest()
    lat_offset = (int(h[:8], 16) / 4294967295.0 - 0.5) * 2 * scale
    lng_offset = (int(h[8:16], 16) / 4294967295.0 - 0.5) * 2 * scale
    return lat_offset, lng_offset

def main():
    print("🚀 Iniciando agregación a nivel de TERRITORIOS (Barrios/Agrupaciones Censales y Municipios)...")
    
    # Rutas detectadas dinámicamente
    base_dir = os.path.dirname(os.path.abspath(__file__))
    partidos_path = os.path.join(base_dir, "data/clean_partidos.csv")
    arbitros_path = os.path.join(base_dir, "data/clean_arbitros.csv")
    dim_territorio_path = os.path.join(base_dir, "data/dim_territorio.csv")
    web_dir = base_dir
    
    # 1. Cargar datasets locales
    print("1. Cargando datasets locales...")
    df_part = pd.read_csv(partidos_path, sep=';', low_memory=False)
    df_arb = pd.read_csv(arbitros_path, sep=';')
    df_dim = pd.read_csv(dim_territorio_path, sep=';')
    
    # 2. Descargar coordenadas oficiales
    print("2. Descargando coordenadas de municipios de Cataluña...")
    ssl._create_default_https_context = ssl._create_unverified_context
    coords_url = "https://analisi.transparenciacatalunya.cat/api/views/wpyq-we8x/rows.csv?accessType=DOWNLOAD"
    
    try:
        df_coords_raw = pd.read_csv(coords_url)
        print(f"   Coordenadas descargadas con éxito: {len(df_coords_raw)} municipios.")
    except Exception as e:
        print(f"   ⚠️ Error al descargar coordenadas: {e}")
        raise e
        
    # Crear diccionario de mapeo normalized_name -> (lat, lng)
    coords_map = {}
    for idx, row in df_coords_raw.iterrows():
        muni_original = row['Municipi']
        muni_norm = normalize_muni_name(muni_original)
        lat = row['Latitud']
        lng = row['Longitud']
        if not pd.isna(lat) and not pd.isna(lng):
            coords_map[muni_norm] = (float(lat), float(lng))
            
    # Mapeos especiales manuales para asegurar coincidencia al 100% de ciudades grandes
    special_coords = {
        "BARCELONA": (41.3851, 2.1734),
        "SABADELL": (41.5463, 2.1086),
        "TERRASSA": (41.5642, 2.0125),
        "BADALONA": (41.4469, 2.2450),
        "LLEIDA": (41.6176, 0.6200),
        "GIRONA": (41.9794, 2.8214),
        "TARRAGONA": (41.1189, 1.2445),
        "HOSPITALET DE LLOBREGAT": (41.3597, 2.1003),
        "L'HOSPITALET DE LLOBREGAT": (41.3597, 2.1003),
        "SANT CUGAT DEL VALLES": (41.4723, 2.0855),
        "CORNELLA DE LLOBREGAT": (41.3548, 2.0683),
        "LES": (42.8125, 0.7108),
        "VILANOVA DEL CAMI": (41.5722, 1.6372),
        "NOU DE BERGUEDA, LA": (42.1672, 1.8845),
        "SARRIA DE TER": (41.9961, 2.8286),
        "SANT PERE DE RIBES": (41.2588, 1.7739),
        "SANT FELIU DE LLOBREGAT": (41.3837, 2.0463),
        "MATARO": (41.5381, 2.4447),
        "VILASSAR DE DALT": (41.5173, 2.3582),
        "LINYOLA": (41.7119, 0.9037),
        "ROSES": (42.2616, 3.1799),
        "SANT JOAN DESPI": (41.3686, 2.0569)
    }
    for k, v in special_coords.items():
        coords_map[normalize_muni_name(k)] = v

    # 3. Construir lista única de Territorios (id_territorio)
    print("3. Construyendo dimensión de territorios con coordenadas geográficas...")
    
    # Cruzar partidos con dimensión territorial
    df_part_terr = df_part.merge(df_dim, on='id_territorio', how='inner')
    
    unique_territories = sorted(df_part_terr['id_territorio'].dropna().unique())
    
    # Contar cuántos territorios tiene cada municipio para aplicar desfase si es necesario
    muni_counts = df_part_terr.groupby('municipio')['id_territorio'].nunique().to_dict()
    
    terr_list = []
    terr_to_idx = {}
    
    matched_coords_count = 0
    
    # Coordenadas exactas para Agrupaciones Censales (barrios de grandes ciudades) para evitar la superposición en el centro
    ac_coordinates = {
        # Barcelona
        "Barcelona 79 (la Bonanova, la Torre Vilana i l'Avinguda del Tibidabo)": (41.405, 2.128),
        "Barcelona 179 (el Besòs)": (41.417, 2.218),
        "Barcelona 130 (Can Dragó)": (41.434, 2.180),
        "Barcelona 15 (el Fort Pienc)": (41.398, 2.181),
        "Barcelona 180 (el Maresme i el Maresme Vell)": (41.412, 2.207),
        "Barcelona 35 (l'Escola Industrial)": (41.387, 2.148),
        "Barcelona 51 (la Mare de Déu de Port, Can Clos i el Polvorí)": (41.356, 2.135),
        "Barcelona 48 (Santa Madrona, la Satàlia i Montjuïc)": (41.370, 2.158),
        "Barcelona 124 (Sant Joan d'Horta)": (41.430, 2.160),
        "Barcelona 103 (Joanic)": (41.405, 2.162),
        "Barcelona 62 (Santa Maria de Sants)": (41.377, 2.137),
        "Barcelona 133 (el Turó de la Peira i Can Peguera)": (41.432, 2.168),
        "Barcelona 172 (la Vila Olímpica i el Bogatell)": (41.391, 2.195),
        "Barcelona 120 (Sant Genís dels Agudells)": (41.424, 2.140),
        "Barcelona 135 (la Guineueta)": (41.439, 2.170),
        "Barcelona 118 (el Baix Carmel)": (41.421, 2.155),
        "Barcelona 147 (la Trinitat Vella)": (41.448, 2.191),
        "Barcelona 73 (Pedralbes, la Mercè i el Palau Reial)": (41.396, 2.112),
        "Barcelona 142 (Santa Engràcia)": (41.444, 2.179),
        "Barcelona 13 (Sant Pere)": (41.388, 2.180),
        "Barcelona 10 (Sant Miquel del Port)": (41.378, 2.190),
        "Barcelona 80 (Sant Gervasi de Cassoles)": (41.401, 2.140),
        "Barcelona 146 (Torre Baró, Ciutat Meridiana i Vallbona)": (41.460, 2.179),
        "Barcelona 149 (el Bon Pastor)": (41.437, 2.206),
        # Sabadell
        "Sabadell 12 (la Roureda - Sant Julià)": (41.579, 2.096),
        "Sabadell 14 (Can Rull Nord - Via Alexandra)": (41.554, 2.088),
        "Sabadell 22 (Torre-romeu - Can Roqueta - el Poblenou)": (41.555, 2.131),
        "Sabadell 10 (Ca n'Oriac - Torreguitart - Torrent del Capellà)": (41.569, 2.095),
        "Sabadell 18 (Gràcia)": (41.542, 2.102),
        # Badalona
        "Badalona 25 (Bufalà Oest - sector Can Barriga)": (41.460, 2.241),
        "Badalona 29 (Canyet - Mas Ram - Pomar de Dalt - Pomar)": (41.482, 2.235),
        "Badalona 18 (Sistrells)": (41.444, 2.231),
        "Badalona 22 (Lloreda)": (41.448, 2.222),
        "Badalona 13 (Sant Antoni de Llefià)": (41.437, 2.219),
        "Badalona 7 (Sant Roc Sud-est - la Mora - el Remei)": (41.431, 2.229),
        "Badalona 16 (la Salut Centre)": (41.441, 2.225),
        # L'Hospitalet de Llobregat
        "Hospitalet de Llobregat 15 (Collblanc - Centre - Vallparda), l'": (41.368, 2.102),
        "Hospitalet de Llobregat 3 (Centre - la Farga), l'": (41.360, 2.099),
        "Hospitalet de Llobregat 29 (Bellvitge - Estació), l'": (41.350, 2.113),
        "Hospitalet de Llobregat 26 (Santa Eulàlia - Centre Sud - Ciutat de la Justícia), l'": (41.363, 2.125),
        "Hospitalet de Llobregat 16 (Collblanc - Cementiri - Carretera), l'": (41.370, 2.095),
        "Hospitalet de Llobregat 28 (el Gornal), l'": (41.352, 2.122),
        "Hospitalet de Llobregat 10 (la Florida - Plaça de la Llibertat), l'": (41.369, 2.108),
        "Hospitalet de Llobregat 18 (la Torrassa - Plaça dels Pirineus), l'": (41.368, 2.115),
        # Terrassa
        "Terrassa 9 (Can Jofresa - Can Palet II - Guadalhorce - Xúquer)": (41.551, 2.019),
        "Terrassa 6 (Ca n'Anglada)": (41.564, 2.030),
        "Terrassa 10 (Can Parellada - les Fonts)": (41.529, 2.040),
        "Terrassa 17 (Can Boada)": (41.567, 1.999),
        "Terrassa 15 (la Maurina)": (41.559, 2.000),
        "Terrassa 22 (les Arenes - la Grípia - Can Montllor)": (41.571, 2.039),
        # Cornellà de Llobregat
        "Cornellà de Llobregat 2 (Fontsanta - Fatjó)": (41.361, 2.067),
        "Cornellà de Llobregat 9 (Almeda)": (41.354, 2.083),
        "Cornellà de Llobregat 6 (Sant Ildefons Oest)": (41.363, 2.053),
        # Sant Cugat
        "Sant Cugat del Vallès 9 (Can Sant Joan - Sant Mamet - Vullpalleres - Can Barata - Sector Nord - Can Graells)": (41.488, 2.062),
        "Sant Cugat del Vallès 6 (Mirasol - Mas Gener - Can Cabassa - Can Fontanals - les Casetes de Can Ravella)": (41.464, 2.061),
        # Castelldefels
        "Castelldefels 2 (Vista Alegre - el Castell)": (41.282, 1.979),
        # Ripollet
        "Ripollet 1 (Centre - Maragall)": (41.498, 2.153),
        # Mataró
        "Mataró 10 (la Llàntia)": (41.547, 2.430),
        "Mataró 7 (Rocafonda)": (41.546, 2.454),
        "Mataró 9 (Cirera)": (41.549, 2.441),
        # Santa Coloma de Gramenet
        "Santa Coloma de Gramenet 7 (Singuerlin - Can Zam)": (41.461, 2.211),
        # Esplugues
        "Esplugues de Llobregat 2 (Can Vidalet)": (41.369, 2.091),
        # Sant Boi de Llobregat
        "Sant Boi de Llobregat 11 (Ciutat Cooperativa)": (41.352, 2.021),
        # Manresa
        "Manresa 9 (les Escodines - la Balconada - Cal Gravat - Sant Pau)": (41.721, 1.832),
        "Manresa 5 (el Poble Nou - Mion, Puigberenguer i Miralpeix)": (41.733, 1.815),
        # Rubí
        "Rubí 7 (Districte 5 Nord-est)": (41.499, 2.029),
        # Lleida
        "Lleida 1 (Balàfia)": (41.629, 0.622),
        "Lleida 9 (Pardinyes)": (41.627, 0.635),
        # Granollers
        "Granollers 6 (Congost - Can Gili)": (41.614, 2.274),
    }
    
    for idx, terr in enumerate(unique_territories):
        # Obtener datos de la dimensión
        terr_row = df_dim[df_dim['id_territorio'] == terr].iloc[0]
        muni_raw = terr_row['municipio']
        core_muni = get_core_muni(muni_raw)
        core_muni_norm = normalize_muni_name(core_muni)
        
        # Buscar coordenadas
        lat, lng = None, None
        if terr in ac_coordinates:
            lat, lng = ac_coordinates[terr]
            matched_coords_count += 1
        else:
            if core_muni_norm in coords_map:
                lat, lng = coords_map[core_muni_norm]
                matched_coords_count += 1
            else:
                # Búsqueda parcial difusa
                for key, val in coords_map.items():
                    if key in core_muni_norm or core_muni_norm in key:
                        lat, lng = val
                        matched_coords_count += 1
                        break
                if lat is None:
                    lat, lng = 41.7286, 1.8222 # Por defecto en el centro de Cataluña
            
            # Aplicar un desfase determinista si el municipio tiene múltiples agrupaciones censales (barrios)
            # Esto previene que se solapen totalmente en Barcelona, Badalona, Hospitalet, etc.
            if muni_counts.get(muni_raw, 0) > 1:
                lat_jitter, lng_jitter = get_deterministic_jitter(terr)
                lat += lat_jitter
                lng += lng_jitter
            
        # Recopilar estadios de este territorio específico
        df_sub = df_part_terr[df_part_terr['id_territorio'] == terr]
        stadiums_list = []
        for stad, df_stad in df_sub.groupby('estadio'):
            stad_str = str(stad).upper()
            if any(x in stad_str for x in ['DESCONOCIDO', 'NO ESPECIFICADO', 'DESCONEGUT']) or len(stad_str.strip()) <= 3 or not stad_str.strip():
                continue
            stadiums_list.append({
                'name': str(stad),
                'partidos': int(len(df_stad)),
                'avg_tarjetas': round(float(df_stad['tarjetas_total'].mean()), 2)
            })
        stadiums_list = sorted(stadiums_list, key=lambda x: x['partidos'], reverse=True)[:6]
        
        terr_list.append({
            'id_territorio': str(terr),
            'name': str(terr_row['nombre_territorio']),
            'municipio': str(muni_raw),
            'ciudad': str(terr_row['ciudad']) if 'ciudad' in terr_row else str(muni_raw),
            'barrio': str(terr_row['barrio']) if 'barrio' in terr_row else str(terr_row['nombre_territorio']),
            'lat': float(lat),
            'lng': float(lng),
            'ist': round(float(terr_row['valor_IST']), 1),
            'stadiums': stadiums_list
        })
        terr_to_idx[terr] = idx
        
    print(f"   Territorios geolocalizados con éxito: {matched_coords_count} de {len(unique_territories)} ({matched_coords_count/len(unique_territories)*100:.2f}%)")

    # 4. Construir listas de categorías y comités
    categories = ['CADETE', 'AMATEUR', 'JUVENIL']
    cat_to_idx = {c: idx for idx, c in enumerate(categories)}
    
    unique_comites = sorted(df_part_terr['arbitro_comite'].dropna().unique())
    comite_to_idx = {c: idx for idx, c in enumerate(unique_comites)}
    
    # 5. Generar listado compacto de partidos
    print("5. Generando listado de partidos...")
    partidos_list = []
    
    for idx, row in df_part_terr.iterrows():
        terr = row['id_territorio']
        cat = row['categoria']
        comite = row['arbitro_comite']
        tarjetas = row['tarjetas_total']
        vet = row['ref_years_arbitrando']
        
        t_idx = terr_to_idx.get(terr, -1)
        c_idx = cat_to_idx.get(cat, -1)
        com_idx = comite_to_idx.get(comite, -1)
        
        if t_idx == -1 or c_idx == -1 or com_idx == -1:
            continue
            
        ref_vet = int(vet) if not pd.isna(vet) else None
        
        partidos_list.append([
            t_idx,
            int(tarjetas),
            c_idx,
            com_idx,
            ref_vet
        ])

    # 6. Generar listado de árbitros
    print("6. Generando listado de árbitros activos...")
    df_arb_active = df_arb[df_arb['partidos_dirigidos'] >= 5].copy()
    referees_list = []
    
    for idx, row in df_arb_active.iterrows():
        cat = row['Categoria']
        comite = df_part_terr[df_part_terr['arbitro_principal_clean'] == row['Nom_clean']]['arbitro_comite'].dropna().unique()
        comite_str = comite[0] if len(comite) > 0 else "Desconocido"
        
        ref_vet = int(row['years_arbitrando_2026']) if not pd.isna(row['years_arbitrando_2026']) else None
        ref_idp = round(float(row['IDP']), 3)
        ref_part = int(row['partidos_dirigidos'])
        
        ref_cat_idx = cat_to_idx.get(cat, -1)
        ref_comite_idx = comite_to_idx.get(comite_str, -1)
        
        referees_list.append({
            'id': f"COL_{idx}",
            'cat_idx': ref_cat_idx,
            'comite_idx': ref_comite_idx,
            'vet': ref_vet,
            'idp': ref_idp,
            'partidos': ref_part
        })
        
    # 7. Estadísticas globales
    print("7. Generando estadísticas globales...")
    total_partidos = len(df_part)
    total_partidos_mapeados = len(partidos_list)
    mapeo_pct = (total_partidos_mapeados / total_partidos) * 100
    avg_tarjetas_global = df_part['tarjetas_total'].mean()
    total_arbitros = df_arb['Nom_clean'].nunique()
    
    summary_stats = {
        'total_partidos': int(total_partidos),
        'total_partidos_mapeados': int(total_partidos_mapeados),
        'mapeo_pct': round(float(mapeo_pct), 2),
        'avg_tarjetas_global': round(float(avg_tarjetas_global), 2),
        'total_arbitros': int(total_arbitros)
    }
    
    # 8. Escribir el archivo final web/data.js
    output_js_path = os.path.join(web_dir, "data.js")
    print(f"8. Escribiendo archivo de datos optimizado en: {output_js_path}...")
    
    with open(output_js_path, 'w', encoding='utf-8') as f:
        f.write("// =========================================================\n")
        f.write("// data.js — Datos agregados generados por aggregate_data.py\n")
        f.write("// =========================================================\n\n")
        
        f.write("export const SUMMARY_STATS = ")
        f.write(json.dumps(summary_stats, indent=2, ensure_ascii=False))
        f.write(";\n\n")
        
        f.write("export const CATEGORIES = ")
        f.write(json.dumps(categories, ensure_ascii=False))
        f.write(";\n\n")
        
        f.write("export const COMITES = ")
        f.write(json.dumps(unique_comites, ensure_ascii=False))
        f.write(";\n\n")
        
        f.write("export const TERRITORIES = ")
        f.write(json.dumps(terr_list, indent=2, ensure_ascii=False))
        f.write(";\n\n")
        
        f.write("export const REFEREES = ")
        f.write(json.dumps(referees_list, indent=2, ensure_ascii=False))
        f.write(";\n\n")
        
        f.write("export const PARTIDOS = ")
        f.write(json.dumps(partidos_list, ensure_ascii=False))
        f.write(";\n\n")
        
    print("✅ Datos agregados y exportados a data.js correctamente.")

if __name__ == "__main__":
    main()
