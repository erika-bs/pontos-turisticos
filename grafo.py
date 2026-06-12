import osmnx as ox
import networkx as nx

# ─── Pontos turísticos e suas queries de geocodificação ──────────
PONTOS_QUERY = {
    "Praça Central":       "Praça Orlando de Barros Pimentel, Maricá, RJ, Brazil",
    "Terminal Rodoviário": "Terminal Rodoviário de Maricá, RJ, Brazil",
    "Lagoa de Maricá":     "Lagoa de Maricá, RJ, Brazil",
    "Praia de Maricá":     "Praia de Maricá, RJ, Brazil",
    "Barra de Maricá":     "Barra de Maricá, RJ, Brazil",
    "Pedra de Inoã":       "Pedra de Inoã, Maricá, RJ, Brazil",
    "Distrito de Inoã":    "Inoã, Maricá, RJ, Brazil",
    "Praia de Itaipuaçu":  "Praia de Itaipuaçu, Maricá, RJ, Brazil",
    "Lagoa de Guaratiba":  "Lagoa de Guaratiba, Maricá, RJ, Brazil",
    "Cachoeira Espraiado": "Espraiado, Maricá, RJ, Brazil",
}

EMOJIS = {
    "Praça Central":       "🏛",
    "Terminal Rodoviário": "🚌",
    "Lagoa de Maricá":     "🌊",
    "Praia de Maricá":     "🏖",
    "Barra de Maricá":     "⚓",
    "Pedra de Inoã":       "🧗",
    "Distrito de Inoã":    "🏘",
    "Praia de Itaipuaçu":  "🌴",
    "Lagoa de Guaratiba":  "🦢",
    "Cachoeira Espraiado": "💧",
}

def carregar_dados():
    print("📡 Baixando mapa de Maricá do OpenStreetMap...")
    G_osm = ox.graph_from_place(
        "Maricá, Rio de Janeiro, Brazil",
        network_type="drive"
    )
    G_osm = ox.add_edge_speeds(G_osm)
    G_osm = ox.add_edge_travel_times(G_osm)
    print(f"   Grafo carregado: {len(G_osm.nodes)} nós, {len(G_osm.edges)} arestas")

    print("📍 Geocodificando pontos turísticos...")
    coords = {}
    falhas = []
    for nome, query in PONTOS_QUERY.items():
        try:
            lat, lng = ox.geocode(query)
            coords[nome] = (lat, lng)
            print(f"   ✓ {EMOJIS[nome]} {nome}: ({lat:.4f}, {lng:.4f})")
        except Exception as e:
            print(f"   ✗ {nome}: {e}")
            falhas.append(nome)

    if falhas:
        print(f"\n⚠️  Não foi possível geocodificar: {falhas}")
        print("   Verifique sua conexão ou ajuste as queries em PONTOS_QUERY.")

    return G_osm, coords

def calcular_dijkstra(G_osm, coords, origem, destino):
    nos_osm = {}
    for nome, (lat, lng) in coords.items():
        no = ox.nearest_nodes(G_osm, lng, lat)
        nos_osm[nome] = no

    no_origem  = nos_osm[origem]
    no_destino = nos_osm[destino]

    comprimento, caminho_nos = nx.single_source_dijkstra(
        G_osm, no_origem, no_destino, weight="length"
    )
    custo_km = comprimento / 1000

    rota_coords = [
        (G_osm.nodes[n]["y"], G_osm.nodes[n]["x"])
        for n in caminho_nos
    ]

    dist_todos = nx.single_source_dijkstra_path_length(
        G_osm, no_origem, weight="length"
    )
    todas = {}
    for nome, no in nos_osm.items():
        todas[nome] = dist_todos.get(no, float("inf")) / 1000

    nos_na_rota = set(caminho_nos)
    caminho_nomes = [origem] + [
        n for n in list(coords.keys())
        if n != origem and n != destino and nos_osm[n] in nos_na_rota
    ] + [destino]

    return {
        "caminho_nomes": caminho_nomes,
        "custo_km":      round(custo_km, 2),
        "todas":         {k: round(v, 2) for k, v in todas.items()},
        "rota_coords":   rota_coords,
        "origem":        origem,
        "destino":       destino,
    }
