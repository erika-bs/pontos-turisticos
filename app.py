import tkinter as tk
from tkinter import ttk, messagebox
import threading
import networkx as nx

from grafo import EMOJIS, PONTOS_QUERY, carregar_dados, calcular_dijkstra
from mapa import abrir_mapa

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dijkstra — Maricá RJ")
        self.resizable(False, False)
        self.configure(bg="#f8fafc")

        self.G_osm  = None
        self.coords = None

        self._build_loading()
        self._iniciar_download()

    def _build_loading(self):
        self.frame_loading = tk.Frame(self, bg="#f8fafc")
        self.frame_loading.pack(padx=40, pady=40)

        tk.Label(self.frame_loading,
                 text="🗺️  Dijkstra - Pontos turísticos de Maricá",
                 font=("Helvetica", 16, "bold"),
                 bg="#f8fafc", fg="#0f172a").pack(pady=(0, 6))

        tk.Label(self.frame_loading,
                 text="Baixando mapa real do OpenStreetMap...",
                 font=("Helvetica", 10),
                 bg="#f8fafc", fg="#64748b").pack(pady=(0, 16))

        self.progress = ttk.Progressbar(self.frame_loading,
                                        mode="indeterminate", length=280)
        self.progress.pack(pady=(0, 10))
        self.progress.start(12)

        self.lbl_status = tk.Label(self.frame_loading, text="Conectando ao OSM...",
                                   font=("Helvetica", 9), bg="#f8fafc", fg="#94a3b8")
        self.lbl_status.pack()

    def _iniciar_download(self):
        def worker():
            try:
                self.lbl_status.config(text="Baixando grafo de ruas de Maricá...")
                G_osm, coords = carregar_dados()
                self.G_osm  = G_osm
                self.coords = coords
                self.after(0, self._download_concluido)
            except Exception as e:
                self.after(0, lambda: self._download_erro(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _download_concluido(self):
        self.progress.stop()
        self.frame_loading.destroy()
        self._build_ui()

    def _download_erro(self, msg):
        self.progress.stop()
        self.lbl_status.config(text=f"Erro: {msg}", fg="#EF4444")
        messagebox.showerror("Erro ao baixar mapa",
                             f"Não foi possível baixar o mapa do OSM.\n\n{msg}")

    def _build_ui(self):
        nomes = list(PONTOS_QUERY.keys())

        tk.Label(self, text="🗺️ Dijkstra - Maricá",
                 font=("Helvetica", 16, "bold"),
                 bg="#f8fafc", fg="#0f172a").pack(pady=(20, 2))
        tk.Label(self,
                 text="Distâncias reais via OpenStreetMap",
                 font=("Helvetica", 10),
                 bg="#f8fafc", fg="#64748b").pack(pady=(0, 16))

        card = tk.Frame(self, bg="white",
                        highlightbackground="#e2e8f0", highlightthickness=1)
        card.pack(padx=24, pady=4, fill="x")

        tk.Label(card, text="Origem", font=("Helvetica", 11, "bold"),
                 bg="white", fg="#0f172a").grid(
                     row=0, column=0, sticky="w", padx=16, pady=(16, 4))
        self.combo_origem = ttk.Combobox(card, values=nomes,
                                         state="readonly", width=32,
                                         font=("Helvetica", 11))
        self.combo_origem.grid(row=1, column=0, padx=16, pady=(0, 12))
        self.combo_origem.set(nomes[0])

        tk.Label(card, text="Destino", font=("Helvetica", 11, "bold"),
                 bg="white", fg="#0f172a").grid(
                     row=2, column=0, sticky="w", padx=16, pady=(4, 4))
        self.combo_destino = ttk.Combobox(card, values=nomes,
                                          state="readonly", width=32,
                                          font=("Helvetica", 11))
        self.combo_destino.grid(row=3, column=0, padx=16, pady=(0, 16))
        self.combo_destino.set(nomes[7])

        tk.Button(self,
                  text="Calcular e Abrir Mapa  →",
                  font=("Helvetica", 12, "bold"),
                  bg="#0D9488", fg="white", bd=0,
                  activebackground="#0f766e", activeforeground="white",
                  cursor="hand2", pady=10,
                  command=self.calcular).pack(padx=24, pady=12, fill="x")

        self.frame_resultado = tk.Frame(self, bg="#f0fdf9",
                                        highlightbackground="#0D9488",
                                        highlightthickness=1)
        self.lbl_caminho = tk.Label(self.frame_resultado, text="",
                                    font=("Helvetica", 11),
                                    bg="#f0fdf9", fg="#0f172a",
                                    wraplength=360, justify="left")
        self.lbl_caminho.pack(padx=14, pady=(12, 4), anchor="w")
        self.lbl_custo = tk.Label(self.frame_resultado, text="",
                                  font=("Helvetica", 13, "bold"),
                                  bg="#f0fdf9", fg="#0D9488")
        self.lbl_custo.pack(padx=14, pady=(0, 12), anchor="w")

        # Tabela de distâncias
        tk.Label(self, text="Distâncias reais a partir da origem",
                 font=("Helvetica", 10, "bold"),
                 bg="#f8fafc", fg="#64748b").pack(
                     padx=24, pady=(12, 4), anchor="w")

        frame_tab = tk.Frame(self, bg="#f8fafc")
        frame_tab.pack(padx=24, pady=(0, 20), fill="x")

        colunas = ("Ponto", "Distância real (km)")
        self.tabela = ttk.Treeview(frame_tab, columns=colunas,
                                   show="headings", height=10)
        for col in colunas:
            self.tabela.heading(col, text=col)
            self.tabela.column(col,
                               width=210 if col == "Ponto" else 150,
                               anchor="w")

        sb = ttk.Scrollbar(frame_tab, orient="vertical",
                           command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=sb.set)
        self.tabela.pack(side="left", fill="x", expand=True)
        sb.pack(side="right", fill="y")

        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 10), rowheight=26)
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

    def calcular(self):
        origem  = self.combo_origem.get()
        destino = self.combo_destino.get()

        if not origem or not destino:
            messagebox.showwarning("Atenção", "Selecione origem e destino.")
            return
        if origem == destino:
            messagebox.showwarning("Atenção",
                                   "Origem e destino devem ser diferentes.")
            return

        try:
            resultado = calcular_dijkstra(self.G_osm, self.coords,
                                          origem, destino)
        except nx.NetworkXNoPath:
            messagebox.showerror("Sem caminho",
                                 "Não foi possível encontrar caminho entre os pontos.")
            return
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return

        self._atualizar_resultado(resultado)
        abrir_mapa(resultado, self.coords)

    def _atualizar_resultado(self, resultado):
        caminho = resultado["caminho_nomes"]
        custo   = resultado["custo_km"]
        todas   = resultado["todas"]

        passos = " → ".join(f"{EMOJIS[n]} {n}" for n in caminho)
        self.lbl_caminho.config(text=f"Caminho: {passos}")
        self.lbl_custo.config(text=f"Distância total: {custo:.2f} km")
        self.frame_resultado.pack(padx=24, pady=4, fill="x")

        for row in self.tabela.get_children():
            self.tabela.delete(row)

        for ponto, dist in sorted(todas.items(), key=lambda x: x[1]):
            tag = "rota" if ponto in caminho else "normal"
            self.tabela.insert("", "end",
                               values=(f"{EMOJIS[ponto]}  {ponto}",
                                       f"{dist:.2f} km"),
                               tags=(tag,))

        self.tabela.tag_configure("rota",
                                  background="#f0fdf9",
                                  foreground="#0D9488")
        self.tabela.tag_configure("normal",
                                  background="white",
                                  foreground="#0f172a")
