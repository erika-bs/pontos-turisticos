import folium
import tempfile
import os
import webbrowser

from grafo import EMOJIS

COR_ORIGEM  = "#F59E0B"
COR_DESTINO = "#EF4444"
COR_ROTA    = "#0D9488"
COR_OUTROS  = "#1B3455"

def _icone(emoji, cor, tam):
    html = f"""<div style="
        background:{cor};border:2.5px solid #fff;border-radius:50%;
        width:{tam*2}px;height:{tam*2}px;
        display:flex;align-items:center;justify-content:center;
        font-size:{tam}px;box-shadow:0 2px 8px rgba(0,0,0,.3)">{emoji}</div>"""
    return folium.DivIcon(html=html,
                          icon_size=(tam*2, tam*2),
                          icon_anchor=(tam, tam))

def gerar_mapa(resultado, coords):
    origem        = resultado["origem"]
    destino       = resultado["destino"]
    caminho_nomes = resultado["caminho_nomes"]
    custo_km      = resultado["custo_km"]
    todas         = resultado["todas"]
    rota_coords   = resultado["rota_coords"]

    lat_c = sum(c[0] for c in rota_coords) / len(rota_coords)
    lng_c = sum(c[1] for c in rota_coords) / len(rota_coords)

    m = folium.Map(location=[lat_c, lng_c], zoom_start=13,
                   tiles="CartoDB positron")

    folium.PolyLine(
        locations=rota_coords,
        color=COR_ROTA,
        weight=5,
        opacity=0.9,
        tooltip=f"Rota: {custo_km:.2f} km"
    ).add_to(m)

    nomes = list(coords.keys())
    for i, a in enumerate(nomes):
        for b in nomes[i+1:]:
            folium.PolyLine(
                locations=[coords[a], coords[b]],
                color="#CBD5E1", weight=1,
                opacity=0.3,
                dash_array="4 6"
            ).add_to(m)

    for nome, (lat, lng) in coords.items():
        if nome == origem:
            cor, tam = COR_ORIGEM, 18
        elif nome == destino:
            cor, tam = COR_DESTINO, 18
        elif nome in caminho_nomes:
            cor, tam = COR_ROTA, 15
        else:
            cor, tam = COR_OUTROS, 12

        na_rota = nome in caminho_nomes
        destaque = '<br><b style="color:#0D9488">✓ No caminho mínimo</b>' if na_rota else ""
        popup_html = f"""
        <div style="font-family:sans-serif;min-width:180px;padding:4px">
            <b style="font-size:14px">{EMOJIS[nome]} {nome}</b><br>
            <span style="color:#64748b;font-size:12px">
                {todas[nome]:.2f} km de {origem}
            </span>{destaque}
        </div>"""

        folium.Marker(
            location=[lat, lng],
            icon=_icone(EMOJIS[nome], cor, tam),
            popup=folium.Popup(popup_html, max_width=230),
            tooltip=nome
        ).add_to(m)

    passos = " → ".join(EMOJIS[n] for n in caminho_nomes)
    legenda = f"""
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
        background:white;padding:14px 18px;border-radius:12px;
        border:1px solid #e2e8f0;font-family:sans-serif;font-size:12px;
        box-shadow:0 2px 16px rgba(0,0,0,.12);max-width:250px">
        <b style="font-size:14px">🗺️ Dijkstra — Maricá RJ</b>
        <br><small style="color:#64748b">Distâncias reais via OpenStreetMap</small><br><br>
        <span style="color:{COR_ORIGEM}">●</span> Origem: {EMOJIS[origem]} {origem}<br>
        <span style="color:{COR_DESTINO}">●</span> Destino: {EMOJIS[destino]} {destino}<br>
        <span style="color:{COR_ROTA}">●</span> No caminho mínimo<br><br>
        <b style="color:{COR_ROTA}">Total: {custo_km:.2f} km</b><br>
        <span style="color:#64748b;font-size:11px">{passos}</span>
    </div>"""
    m.get_root().html.add_child(folium.Element(legenda))

    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    m.save(tmp.name)
    return tmp.name

def abrir_mapa(resultado, coords):
    path = gerar_mapa(resultado, coords)
    webbrowser.open("file://" + os.path.abspath(path))
