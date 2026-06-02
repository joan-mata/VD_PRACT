import pandas as pd
import numpy as np
import re
import os
import unicodedata

def clean_ref_name(name):
    if not isinstance(name, str):
        return "DESCONOCIDO"
    name = name.strip().upper()
    name = re.sub(r'\s+', ' ', name)
    return name

def parse_date(date_str):
    if not isinstance(date_str, str):
        return pd.NaT
    date_str = date_str.strip()
    for fmt in ('%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d'):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue
    return pd.NaT

def remove_accents(input_str):
    if not isinstance(input_str, str):
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_text(text):
    text = str(text).upper()
    text = remove_accents(text)
    text = text.replace('.', '')
    text = re.sub(r'\bST\b', 'SANT', text)
    text = re.sub(r'\bSTA\b', 'SANTA', text)
    text = re.sub(r'\bMPAL\b', 'MUNICIPAL', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_name_for_matching(name):
    name_clean = re.sub(r'^(L\'|LA\s+|EL\s+|LES\s+|ELS\s+|ES\s+)', '', name, flags=re.IGNORECASE)
    name_clean = re.sub(r',\s*(l\'|la|el|les|els|es)$', '', name_clean, flags=re.IGNORECASE)
    return name_clean.strip()

def get_muni_keywords(muni):
    muni_clean = clean_name_for_matching(muni)
    muni_norm = normalize_text(muni_clean)
    words = muni_norm.split()
    if len(words) == 0:
        return []
    
    stop_words = {'LES', 'PAU', 'CARME', 'EL', 'LA', 'ELS', 'ES', 'L', 'SANT', 'SANTA'}
    
    if words[0] in ['SANT', 'SANTA', 'EL', 'LA', 'LES', 'ELS', 'ES', 'L\'']:
        if len(words) > 1:
            core = words[0] + " " + words[1]
            return [muni_norm, core, words[1]]
            
    if len(words) == 1 and words[0] in stop_words:
        return [muni_norm]
        
    return [muni_norm, words[0]]

def get_ciudad_y_barrio(id_territorio):
    if not isinstance(id_territorio, str) or id_territorio in ['Desconocido', 'NONE', '']:
        return 'Desconocido', 'Desconocido'
    
    clean_id = id_territorio.strip()
    match = re.match(r'^([^0-9]+)\s+[0-9]+\s*\(([^)]+)\)', clean_id)
    if match:
        ciudad = match.group(1).strip()
        barrio = match.group(2).strip()
        
        if ciudad.endswith(','):
            ciudad = ciudad[:-1].strip()
        if ',' in ciudad:
            parts = [p.strip() for p in ciudad.split(',')]
            if len(parts) == 2 and parts[1].lower() in ['el', 'la', 'les', 'els', 'es', 'l\'', 'l']:
                article = parts[1].capitalize()
                if article == "L'":
                    ciudad = f"L'{parts[0]}"
                else:
                    ciudad = f"{article} {parts[0]}"
        return ciudad, barrio
        
    ciudad = clean_id
    if ',' in ciudad:
        parts = [p.strip() for p in ciudad.split(',')]
        if len(parts) == 2 and parts[1].lower() in ['el', 'la', 'les', 'els', 'es', 'l\'', 'l']:
            article = parts[1].capitalize()
            if article == "L'":
                ciudad = f"L'{parts[0]}"
            else:
                ciudad = f"{article} {parts[0]}"
    return ciudad, ciudad

def main():
    print("🚀 Iniciando preparación de datos optimizada para la PRACT2...")
    
    # Rutas detectadas dinámicamente
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    # Si estamos dentro de la subcarpeta de git VD_PRACT, los archivos raw están en el padre
    raw_dir = parent_dir if os.path.exists(os.path.join(parent_dir, "data/fcf_analytics_2526.csv")) else base_dir
    
    partidos_path = os.path.join(raw_dir, "data/fcf_analytics_2526.csv")
    arbitros_path = os.path.join(raw_dir, "data/Arbitros.csv")
    ist_ac_path = os.path.join(raw_dir, "data/ist14034ac.csv")
    ist_mun_path = os.path.join(raw_dir, "data/ist14034mun.csv")
    
    # 1. Cargar datasets IST
    print("1. Cargando y limpiando datasets IST (Agrupaciones Censales y Municipios)...")
    df_ac_raw = pd.read_csv(ist_ac_path, sep=';')
    df_mun_raw = pd.read_csv(ist_mun_path, sep=';')
    
    # Convertir valores de IST a float
    for df in [df_ac_raw, df_mun_raw]:
        df['valor'] = df['valor'].astype(str).str.replace(',', '.').astype(float, errors='ignore')
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        
    # Filtrar por año más reciente (2023)
    ac_year = df_ac_raw['any'].max()
    mun_year = df_mun_raw['any'].max()
    print(f"   Año más reciente - AC: {ac_year}, Municipio: {mun_year}")
    
    df_ac = df_ac_raw[df_ac_raw['any'] == ac_year].copy()
    df_mun = df_mun_raw[df_mun_raw['any'] == mun_year].copy()
    
    # Extraer el municipio de la agrupación censal
    def extract_municipality(ac_name):
        match = re.match(r'^([^0-9]+)\s+[0-9]+', ac_name)
        if match:
            return match.group(1).strip()
        return ac_name.split(',')[0].strip()
        
    df_ac['municipio_ist'] = df_ac['agrupació censal'].apply(extract_municipality)
    
    # Listados únicos de municipios
    munis_ac = df_ac['municipio_ist'].unique()
    munis_all = df_mun['municipi'].unique()
    
    # Precomputar palabras clave para búsqueda de municipios
    muni_keywords_ac = {m: get_muni_keywords(m) for m in munis_ac}
    muni_keywords_all = {m: get_muni_keywords(m) for m in munis_all}
    
    # 2. Cargar Árbitros
    print("2. Cargando y procesando dataset de Árbitros...")
    df_arb = pd.read_csv(arbitros_path, sep=';')
    df_arb['Nom_clean'] = df_arb['Nom'].apply(clean_ref_name)
    
    # Eliminar columna NIF por privacidad
    if 'NIF' in df_arb.columns:
        df_arb = df_arb.drop(columns=['NIF'])
        
    # Calcular edad en 2026
    df_arb['fecha_nac'] = df_arb['F. Naixem.'].apply(parse_date)
    df_arb['edad_2026'] = df_arb['fecha_nac'].apply(lambda x: 2026 - x.year if not pd.isnull(x) else np.nan)
    
    # Calcular años arbitrando en 2026
    df_arb['fecha_alta'] = df_arb["Data d'alta"].apply(parse_date)
    df_arb['years_arbitrando_2026'] = df_arb['fecha_alta'].apply(lambda x: 2026 - x.year if not pd.isnull(x) else np.nan)
    
    # Años en la categoría actual
    df_arb['fecha_alta_cat'] = df_arb['Alta Categoria'].apply(parse_date)
    df_arb['years_categoria_2026'] = df_arb['fecha_alta_cat'].apply(lambda x: 2026 - x.year if not pd.isnull(x) else np.nan)
    
    # 3. Cargar Partidos
    print("3. Cargando y procesando dataset de Partidos...")
    df_part = pd.read_csv(partidos_path, sep=';', low_memory=False)
    df_part['arbitro_principal_clean'] = df_part['arbitro_principal'].apply(clean_ref_name)
    
    # Estandarizar métricas de tarjetas
    for col in ['amarillas_local', 'amarillas_visitante', 'rojas_local', 'rojas_visitante']:
        df_part[col] = pd.to_numeric(df_part[col], errors='coerce').fillna(0).astype(int)
        
    df_part['tarjetas_total'] = df_part['amarillas_local'] + df_part['amarillas_visitante'] + df_part['rojas_local'] + df_part['rojas_visitante']
    
    # 4. Calcular el IDP (Índice de Desviación de Punitividad) de los Árbitros
    print("4. Calculando métricas de punitividad del árbitro (IDP)...")
    cat_avg = df_part.groupby('categoria')['tarjetas_total'].mean().to_dict()
    df_part['desviacion_tarjetas'] = df_part.apply(lambda r: r['tarjetas_total'] - cat_avg.get(r['categoria'], 0), axis=1)
    
    ref_counts = df_part['arbitro_principal_clean'].value_counts()
    ref_desv = df_part.groupby('arbitro_principal_clean')['desviacion_tarjetas'].mean()
    
    df_arb_idp = pd.DataFrame({
        'partidos_dirigidos': ref_counts,
        'IDP': ref_desv
    })
    
    df_arb = df_arb.merge(df_arb_idp, left_on='Nom_clean', right_index=True, how='left')
    df_arb['IDP'] = df_arb['IDP'].fillna(0)
    df_arb['partidos_dirigidos'] = df_arb['partidos_dirigidos'].fillna(0).astype(int)
    
    # Guardar Árbitros Enriquecidos
    arb_clean_path = os.path.join(base_dir, "data/clean_arbitros.csv")
    df_arb.to_csv(arb_clean_path, sep=';', index=False)
    
    # 5. Algoritmo de Mapeo de Estadios a Agrupaciones Censales y Municipios
    print("5. Ejecutando algoritmo de mapeo geográfico de estadios...")
    unique_stadiums = df_part[['estadio', 'equipo_local']].drop_duplicates().copy()
    
    # Patrones específicos refinados para estadios/equipos conflictivos o muy comunes
    patterns = {
        r'HORTA DE SANT JOAN|HORTA DE ST\. JOAN|HORTA SAN JUAN': ('MUN', 'Horta de Sant Joan'),
        r'SANT ROC OLOT': ('MUN', 'Olot'),
        r'JUVENTUS-LLORET|JUVENTUS.*LLORET': ('MUN', 'Lloret de Mar'),
        r'LA MINA|MINA': ('AC', 'Sant Adrià de Besòs 4 (la Mina - la Catalana)'),
        r'SANT ROC|ST\. ROC': ('AC', 'Badalona 7 (Sant Roc Sud-est - la Mora - el Remei)'),
        r'LLEFIA|LLEFIÀ': ('AC', 'Badalona 13 (Sant Antoni de Llefià)'),
        r'RAVAL': ('AC', 'Barcelona 3 (la Riereta)'),
        r'SANT GERVASI|ST\. GERVASI': ('AC', 'Barcelona 80 (Sant Gervasi de Cassoles)'),
        r'FORT PIENC|FORT-PIENC': ('AC', 'Barcelona 15 (el Fort Pienc)'),
        r'CAN DRAGO|CAN DRAGÓ': ('AC', 'Barcelona 130 (Can Dragó)'),
        r'BESOS|BESÒS': ('AC', 'Barcelona 179 (el Besòs)'),
        r'SALUT': ('AC', 'Badalona 16 (la Salut Centre)'),
        r'ROCAFONDA': ('AC', 'Mataró 7 (Rocafonda)'),
        r'CONGOST': ('AC', 'Granollers 6 (Congost - Can Gili)'),
        r'BON PASTOR': ('AC', 'Barcelona 149 (el Bon Pastor)'),
        r'TRINITAT NOVA': ('AC', 'Barcelona 145 (la Trinitat Nova)'),
        r'TRINITAT VELLA': ('AC', 'Barcelona 147 (la Trinitat Vella)'),
        r'CIUTAT MERIDIANA': ('AC', 'Barcelona 146 (Torre Baró, Ciutat Meridiana i Vallbona)'),
        r'GORNAL|SPORTVENFI': ('AC', 'Hospitalet de Llobregat 28 (el Gornal), l\''),
        r'BELLVITGE': ('AC', 'Hospitalet de Llobregat 29 (Bellvitge - Estació), l\''),
        r'FLORIDA': ('AC', 'Hospitalet de Llobregat 10 (la Florida - Plaça de la Llibertat), l\''),
        r'COLLBLANC': ('AC', 'Hospitalet de Llobregat 15 (Collblanc - Centre - Vallparda), l\''),
        r'SISTRELLS': ('AC', 'Badalona 18 (Sistrells)'),
        r'MONTAÑESA': ('AC', 'Barcelona 133 (el Turó de la Peira i Can Peguera)'),
        r'HORTA': ('AC', "Barcelona 124 (Sant Joan d'Horta)"),
        r'SABADELL NORD|CA N\'ORIAC': ('AC', 'Sabadell 10 (Ca n\'Oriac - Torreguitart - Torrent del Capellà)'),
        r'TORRE-ROMEU|TORRE ROMEU': ('AC', 'Sabadell 22 (Torre-romeu - Can Roqueta - el Poblenou)'),
        r'MERINALS': ('AC', 'Sabadell 17 (Can Feu - els Merinals - la Serra d\'en Camaró)'),
        r'ZEM DE RIPOLLET|RIPOLLET': ('AC', 'Ripollet 1 (Centre - Maragall)'),
        r'BUFALA|BUFALÀ': ('AC', 'Badalona 25 (Bufalà Oest - sector Can Barriga)'),
        r'SANT IGNASI|BONANOVA|LA SALLE BONANOVA': ('AC', 'Barcelona 79 (la Bonanova, la Torre Vilana i l\'Avinguda del Tibidabo)'),
        r'ESCOLA INDUSTRIAL|DON BOSCO': ('AC', 'Barcelona 35 (l\'Escola Industrial)'),
        r'JUNIOR': ('AC', 'Sant Cugat del Vallès 9 (Can Sant Joan - Sant Mamet - Vullpalleres - Can Barata - Sector Nord - Can Graells)'),
        r'BASCULA|BÀSCULA': ('AC', 'Barcelona 51 (la Mare de Déu de Port, Can Clos i el Polvorí)'),
        r'SATALIA|SATÀLIA|PSEC|POBLE SEC|APA POBLE': ('AC', 'Barcelona 48 (Santa Madrona, la Satàlia i Montjuïc)'),
        r'MIRA-SOL|MIRASOL': ('AC', 'Sant Cugat del Vallès 6 (Mirasol - Mas Gener - Can Cabassa - Can Fontanals - les Casetes de Can Ravella)'),
        r'ALMEDA': ('AC', 'Cornellà de Llobregat 9 (Almeda)'),
        r'SANT ILDEFONS': ('AC', 'Cornellà de Llobregat 6 (Sant Ildefons Oest)'),
        r'SANT GENIS|SANT GENÍS': ('AC', 'Barcelona 120 (Sant Genís dels Agudells)'),
        r'CAN BUXERES': ('AC', 'Hospitalet de Llobregat 16 (Collblanc - Cementiri - Carretera), l\''),
        r'TURO DE LA PEIRA|TURÓ DE LA PEIRA': ('AC', 'Barcelona 133 (el Turó de la Peira i Can Peguera)'),
        r'CAN RULL': ('AC', 'Sabadell 14 (Can Rull Nord - Via Alexandra)'),
        r'GUINEUETA': ('AC', 'Barcelona 135 (la Guineueta)'),
        r'POMAR': ('AC', 'Badalona 29 (Canyet - Mas Ram - Pomar de Dalt - Pomar)'),
        r'CIUTAT COOPERATIVA': ('AC', 'Sant Boi de Llobregat 11 (Ciutat Cooperativa)'),
        r'VIARO|VIARÓ': ('AC', 'Sant Cugat del Vallès 9 (Can Sant Joan - Sant Mamet - Vullpalleres - Can Barata - Sector Nord - Can Graells)'),
        r'XALOC|BALANDRAU': ('AC', 'Hospitalet de Llobregat 26 (Santa Eulàlia - Centre Sud - Ciutat de la Justícia), l\''),
        r'LA CANYA': ('MUN', 'la Canya'),
        r'CAN FATJO|CAN FATJÓ': ('AC', 'Cornellà de Llobregat 2 (Fontsanta - Fatjó)'),
        r'CAMP-REDO|CAMP-REDÓ|CAMPREDO': ('MUN', 'Tortosa'),
        r'FONTAJAU|SANT PONÇ|GERMANS SABAT|GIRONES-SABAT|CAN GIBERT|GEIEG': ('MUN', 'Girona'),
        r'RECASENS|AEM': ('MUN', 'Lleida'),
        
        # Mapeos adicionales
        r'CAN VIDALET': ('AC', 'Esplugues de Llobregat 2 (Can Vidalet)'),
        r'VISTA ALEGRE': ('AC', 'Castelldefels 2 (Vista Alegre - el Castell)'),
        r'CIRERA': ('AC', 'Mataró 9 (Cirera)'),
        r'CAN BOADA': ('AC', 'Terrassa 17 (Can Boada)'),
        r'CA N\'ANGLADA|SAN CRISTOBAL|SAN CRISTÒFOL': ('AC', 'Terrassa 6 (Ca n\'Anglada)'),
        r'CAN JOFRESA|JABAC': ('AC', 'Terrassa 9 (Can Jofresa - Can Palet II - Guadalhorce - Xúquer)'),
        r'CAN CANYADÓ|CANYADO|CANYADÓ': ('AC', 'Badalona 30 (Casagemes - Canyadó - Manresà - les Guixeres)'),
        r'ROVERE|ROUREDA|ATLETICO ROUREDA': ('AC', 'Sabadell 12 (la Roureda - Sant Julià)'),
        r'SINGUERLIN|SINGUERLÍN': ('AC', 'Santa Coloma de Gramenet 7 (Singuerlin - Can Zam)'),
        r'FATIMA|FÀTIMA': ('MUN', 'Igualada'),
        r'BARCELONETA': ('AC', 'Barcelona 10 (Sant Miquel del Port)'),
        r'JUVENTUS': ('AC', 'Mataró 10 (la Llàntia)'),
        r'LLANTIA|LA LLÀNTIA': ('AC', 'Mataró 10 (la Llàntia)'),
        r'BARCINO': ('AC', 'Barcelona 13 (Sant Pere)'),
        r'VILA OLIMPICA|VILA OLÍMPICA': ('AC', 'Barcelona 172 (la Vila Olímpica i el Bogatell)'),
        r'COLLBLANC-TORRASSA|TORRASSA': ('AC', 'Hospitalet de Llobregat 18 (la Torrassa - Plaça dels Pirineus), l\''),
        r'HOSPITALENSE': ('AC', 'Hospitalet de Llobregat 3 (Centre - la Farga), l\''),
        r'CE EUROPA|C\.E\. EUROPA|NOU SARDENYA|L\'ÀLIGA|L\'ALIGA': ('AC', 'Barcelona 103 (Joanic)'),
        r'LES FONTS': ('AC', 'Terrassa 10 (Can Parellada - les Fonts)'),
        r'LES ROQUETES': ('MUN', 'Sant Pere de Ribes'),
        r'LES GARRIGUES': ('MUN', 'Borges Blanques, les'),
        r'LES MALLORQUINES': ('MUN', 'Sils'),
        
        # Mapeos de optimización de tasa (95%+)
        r'PARDINYES': ('AC', 'Lleida 9 (Pardinyes)'),
        r'REDDIS|SANTES CREUS': ('MUN', 'Reus'),
        r'FONTSANTA-FATJO|FONTSANTA-FATJÓ': ('AC', 'Cornellà de Llobregat 2 (Fontsanta - Fatjó)'),
        r'SANTVICENTI': ('MUN', 'Sant Vicenç de Montalt'),
        r'ESPLAIS|CENTRE HISTORIC|CENTRE HISTÒRIC': ('MUN', "Castelló d'Empúries"),
        r'MONELLS': ('MUN', "Cruïlles, Monells i Sant Sadurní de l'Heura"),
        r'ESPLUGUENC': ('MUN', 'Esplugues de Llobregat'),
        r'ROMANICA|ROMÀNICA': ('MUN', 'Barberà del Vallès'),
        r'1ER. DE MAIG|1ER DE MAIG': ('MUN', 'Granollers'),
        r'LLOREDA': ('AC', 'Badalona 22 (Lloreda)'),
        r'MAURINA': ('AC', 'Terrassa 15 (la Maurina)'),
        r'CARMEL|CARMELO': ('AC', 'Barcelona 118 (el Baix Carmel)'),
        r'25 DE SETEMBRE|25 DE SEPTIEMBRE': ('AC', 'Rubí 7 (Districte 5 Nord-est)'),
        r'CAN TRIES|CAN TRIAS': ('MUN', 'Viladecavalls'),
        r'SINERA': ('MUN', 'Arenys de Mar'),
        r'MARESME|PUJADAS': ('AC', 'Barcelona 180 (el Maresme i el Maresme Vell)'),
        r'LES ARENES|JUAN XXIII': ('AC', 'Terrassa 22 (les Arenes - la Grípia - Can Montllor)'),
        r'ENERGIA': ('AC', 'Barcelona 62 (Santa Maria de Sants)'),
        r'PASTORETA': ('MUN', 'Reus'),
        r'ORGEL\.LIA|EMILI VICENTE': ('MUN', "Seu d'Urgell, la"),
        r'BALAFIA|BALÀFIA': ('AC', 'Lleida 1 (Balàfia)'),
        r'LA FARGA': ('MUN', 'Sant Cugat del Vallès'),
        r'GRAMA': ('MUN', 'Santa Coloma de Gramenet'),
        r'MION|PUIGBERENGUER|PIRINAICA': ('AC', 'Manresa 5 (el Poble Nou - Mion, Puigberenguer i Miralpeix)'),
        r'ESPIRALL': ('MUN', 'Vilafranca del Penedès'),
        r'SAN MAURO': ('MUN', 'Santa Margarida de Montbui'),
        r'BALCONADA|PARE IGNASI PUIG': ('AC', 'Manresa 9 (les Escodines - la Balconada - Cal Gravat - Sant Pau)'),
        r'BOSC DE TOSCA': ('MUN', 'les Preses'),
        r'COSTA DAURADA': ('MUN', 'Salou'),
        r'ATENEU IGUALADI': ('MUN', 'Igualada'),
        r'BRAFA': ('AC', 'Barcelona 142 (Santa Engràcia)'),
        r'CAL AGUIDO|CA LA GUIDO|CA LA GUIDÓ': ('MUN', 'Blanes'),
        r'OAR GRÀCIA|OAR GRACIA': ('AC', 'Sabadell 18 (Gràcia)'),
        r'CAN BORRELL': ('MUN', 'Blanes'),
        r'DIAGONAL CLUB': ('AC', 'Barcelona 73 (Pedralbes, la Mercè i el Palau Reial)'),
        r'BONAVISTA': ('MUN', 'Tarragona'),
    }
    
    def match_stadium_row(row):
        estadio = normalize_text(row['estadio'])
        equipo = normalize_text(row['equipo_local'])
        
        # Detectar si el estadio es genérico o desconocido (eliminamos el '' de la lista para evitar falsos positivos)
        is_unknown = any(x in estadio for x in ['DESCONOCIDO', 'NO ESPECIFICADO', 'DESCONEGUT']) or len(estadio.strip()) <= 3 or not estadio.strip()
        
        # 1. Patrones manuales prioritarios (se aplican siempre, sobre estadio o equipo)
        for pat, (tipo, val) in patterns.items():
            if re.search(pat, estadio) or re.search(pat, equipo):
                return tipo, val
                
        # 2. Buscar en municipios grandes (AC) (solo si el estadio es conocido para evitar sesgo)
        if not is_unknown:
            for muni, kws in muni_keywords_ac.items():
                for kw in kws:
                    if len(kw) >= 3:
                        if kw in ['LES', 'PAU', 'CARME']:
                            continue
                        pattern = r'\b' + re.escape(kw) + r'\b' if len(kw) <= 4 else re.escape(kw)
                        if re.search(pattern, estadio) or re.search(pattern, equipo):
                            # Si no se ha detectado el barrio específico mediante patrones en el paso 1,
                            # NO debemos asignar arbitrariamente el primer barrio de la lista (ac_list[0]),
                            # ya que esto colocaría erróneamente todos los partidos de la ciudad en ese barrio.
                            # Dejamos que pase al paso 3 para asignarlo a nivel de Municipio (MUN).
                            pass
                            
        # 3. Fallback a municipios pequeños (MUN) (se permite para estadios conocidos o desconocidos)
        for muni, kws in muni_keywords_all.items():
            for kw in kws:
                if len(kw) >= 3:
                    if kw in ['LES', 'PAU', 'CARME']:
                        if estadio == kw or equipo == kw or estadio == f"CAMP DE FUTBOL MPAL {kw}" or estadio == f"CAMP DE FUTBOL MPAL DE {kw}":
                            return 'MUN', muni
                        continue
                    pattern = r'\b' + re.escape(kw) + r'\b' if len(kw) <= 4 else re.escape(kw)
                    if re.search(pattern, estadio) or re.search(pattern, equipo):
                        return 'MUN', muni
                        
        return 'NONE', 'Desconocido'

    # Ejecutar emparejamiento optimizado sobre el listado único
    print("   Aplicando algoritmos de emparejamiento por texto...")
    mapped_list = unique_stadiums.apply(match_stadium_row, axis=1)
    unique_stadiums['mapped_type'] = [r[0] for r in mapped_list]
    unique_stadiums['mapped_val'] = [r[1] for r in mapped_list]
    
    mapped_count = (unique_stadiums['mapped_val'] != "Desconocido").sum()
    total_count = len(unique_stadiums)
    print(f"   Mapeados con éxito: {mapped_count} de {total_count} ({mapped_count/total_count*100:.2f}%)")
    
    # 6. Generar dimensiones y tablas puente con ciudad y barrio
    print("6. Generando dimensión territorial unificada y tablas puente con ciudad y barrio...")
    
    # Generar dim_territorio: Contiene las claves de territorio de AC e IST Municipal
    dim_records = []
    
    # Agregar agrupaciones censales
    for idx, row in df_ac.iterrows():
        ciudad, barrio = get_ciudad_y_barrio(row['agrupació censal'])
        dim_records.append({
            'id_territorio': row['agrupació censal'],
            'tipo_territorio': 'Agrupación Censal',
            'nombre_territorio': row['agrupació censal'],
            'municipio': row['municipio_ist'],
            'ciudad': ciudad,
            'barrio': barrio,
            'valor_IST': row['valor']
        })
        
    # Agregar municipios (solo los que no estén ya representados como municipio en AC o todos como fallback)
    for idx, row in df_mun.iterrows():
        ciudad, barrio = get_ciudad_y_barrio(row['municipi'])
        dim_records.append({
            'id_territorio': row['municipi'],
            'tipo_territorio': 'Municipio',
            'nombre_territorio': row['municipi'],
            'municipio': row['municipi'],
            'ciudad': ciudad,
            'barrio': barrio,
            'valor_IST': row['valor']
        })
        
    df_dim_territorio = pd.DataFrame(dim_records).drop_duplicates(subset=['id_territorio'])
    
    # Guardar Dimensión Territorio
    dim_terr_path = os.path.join(base_dir, "data/dim_territorio.csv")
    df_dim_territorio.to_csv(dim_terr_path, sep=';', index=False)
    print(f"   Dimensión territorial unificada guardada en: {dim_terr_path}")
    
    # Tabla Puente: estadio -> id_territorio
    df_mapping = unique_stadiums[['estadio', 'equipo_local', 'mapped_val']].copy()
    df_mapping.columns = ['estadio', 'equipo_local', 'id_territorio']
    
    # Agregar ciudad y barrio
    res_cb = df_mapping['id_territorio'].apply(lambda val: pd.Series(get_ciudad_y_barrio(val)))
    df_mapping['ciudad'] = res_cb[0]
    df_mapping['barrio'] = res_cb[1]
    
    mapping_csv_path = os.path.join(base_dir, "data/stadium_to_ist_mapping.csv")
    df_mapping.to_csv(mapping_csv_path, sep=';', index=False)
    print(f"   Tabla puente de estadios a IST guardada en: {mapping_csv_path}")
    
    # 7. Cruzar partidos y guardar partidos enriquecidos
    print("7. Cruzando partidos con dimensiones y guardando clean_partidos.csv...")
    df_part = df_part.merge(df_mapping, on=['estadio', 'equipo_local'], how='left')
    
    # Unir métricas de árbitros
    df_arb_short = df_arb[['Nom_clean', 'edad_2026', 'years_arbitrando_2026', 'years_categoria_2026', 'Categoria', 'IDP']].copy()
    df_arb_short.columns = ['arbitro_principal_clean', 'ref_edad', 'ref_years_arbitrando', 'ref_years_categoria', 'ref_rango_oficial', 'ref_IDP']
    
    df_part = df_part.merge(df_arb_short, on='arbitro_principal_clean', how='left')
    
    # Guardar partidos
    part_clean_path = os.path.join(base_dir, "data/clean_partidos.csv")
    df_part.to_csv(part_clean_path, sep=';', index=False)
    print(f"   Dataset de partidos enriquecidos guardado en: {part_clean_path}")
    
    # Estadísticas de partidos
    mapped_partidos = (df_part['id_territorio'] != 'Desconocido').sum()
    total_partidos = len(df_part)
    print(f"   Estadística final de partidos mapeados: {mapped_partidos} de {total_partidos} ({mapped_partidos/total_partidos*100:.2f}%)")
    print("✅ Proceso de preparación de datos finalizado con éxito.")

if __name__ == "__main__":
    main()
