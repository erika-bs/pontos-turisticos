# Dijkstra — Maricá RJ (Dados Reais)

Aplicação desktop que calcula o **menor caminho real pelas ruas** entre pontos
turísticos de Maricá usando o algoritmo de Dijkstra.

Os dados vêm do **OpenStreetMap** via OSMnx, são as ruas reais de Maricá,
não distâncias estimadas.

## Como rodar

```bash
pip install osmnx folium networkx
python main.py
```

> Na primeira execução o programa baixa o mapa (~30s com boa internet).
> O OSMnx faz cache automático, então as próximas execuções são mais rápidas.

## Estrutura do projeto

```
dijkstra_marica_real/
│
├── main.py    ← execute este arquivo
├── app.py     ← interface gráfica (Tkinter) com tela de loading
├── grafo.py   ← download OSMnx + Dijkstra com distâncias reais
└── mapa.py    ← mapa Folium com rota exata pelas ruas
```

## O que cada arquivo faz

| Arquivo   | Responsabilidade |
|-----------|-----------------|
| `main.py` | Ponto de entrada |
| `app.py`  | Interface gráfica. Mostra loading durante o download. Chama `grafo.py` e `mapa.py` |
| `grafo.py`| Baixa o grafo real de Maricá via OSMnx, geocodifica os pontos e executa Dijkstra |
| `mapa.py` | Gera o mapa Folium com a rota exata pelas ruas (não linha reta) |


## Dependências

- `osmnx` — download do grafo de ruas + geocodificação
- `networkx` — algoritmo de Dijkstra
- `folium` — mapa interativo no navegador
- `tkinter` — interface gráfica 
