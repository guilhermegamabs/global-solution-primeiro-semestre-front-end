# IGNIS — Wildfire Command Dashboard

Global Solution 2026/1 — Front-end e Mobile Development em Sistemas de IA — FIAP

Dashboard interativo para defesa civil e operações de emergência em queimadas no Brasil. Transforma dados satelitais (mockados) em fila de alertas acionáveis com fluxo human-in-the-loop: aprovar, modificar ou descartar recomendações de IA.

## Problema

Queimadas no Cerrado e Amazônia exigem decisão rápida (evacuação, despacho aéreo, vigilância). Portais atuais (INPE BDQueimadas, IBAMA) entregam tabelas densas, sem hierarquia visual nem ação clara. IGNIS substitui esse fluxo por um command-center: o operador vê o que está queimando, o risco de espalhamento, e age antes da janela fechar.

Usuário primário: coordenadores de defesa civil e centros de operações de emergência. Alta urgência, decisão em segundos, registro auditável de toda ação.

## Fonte de Dados

Dados mockados em `providers/mock_alerts.py` e `providers/mock_timeseries.py`. Estrutura projetada para substituição direta em produção por:

- INPE BDQueimadas (focos de queimada Brasil)
- NASA FIRMS (VIIRS / MODIS hotspots)
- GOES-16 ABI Fire Detection (feed contínuo)
- Estações meteorológicas INMET (vento, umidade)

Cada alerta inclui: coordenadas, severidade, confiança da detecção, área afetada, vento, fonte satelital, recomendação de IA com rationale e ação esperada.

## Justificativa do Framework

**Streamlit** escolhido por:

- Ciclo de rerun previsível compatível com `st.session_state` para gerenciar fila de alertas e modo "modify".
- `@st.cache_data` para evitar re-fetch de séries históricas a cada interação.
- Suporte nativo a Plotly (mapa + gráficos interativos) e Matplotlib (histograma horário).
- Layout `wide` + sidebar + tabs cobrem a hierarquia panorama → detalhe sem custo extra.

Gradio seria adequado para protótipos de modelo isolado, mas IGNIS é multi-tela com estado persistente — Streamlit encaixa melhor.

## Arquitetura

```
.
├── app.py                  # entry point, sidebar, roteamento
├── providers/              # acesso a dados externos (mocks substituíveis)
│   ├── mock_alerts.py
│   └── mock_timeseries.py
├── pipelines/              # transformação e filtragem
│   └── alert_pipeline.py
├── state/                  # st.session_state centralizado
│   └── alerts_state.py
├── features/               # telas independentes
│   ├── alerts.py           # fila + audit trail
│   ├── map_view.py         # mapa Plotly + lista
│   └── analytics.py        # série temporal, impacto por estado, padrão horário
├── ui/                     # componentes reutilizáveis + design system
│   ├── components.py       # render_severity_badge, render_confidence_bar
│   └── styles.py           # CSS IGNIS (OKLCH, dark command-center)
└── requirements.txt
```

Fluxo:

```
providers ──► pipelines ──► state ──► features ──► ui
  (mock        (process,     (session   (alerts,    (badges,
   data)        filter)       state)     map,        styles)
                                         analytics)
```

`render_severity_badge` é reutilizado em alerts.py, map_view.py e sidebar (componentização real).

## Requisitos Técnicos Atendidos

- Estado e cache: `init_state` guard único + `@st.cache_data` em providers.
- 3 filtros interativos (Analytics: data, severidade, fonte satelital).
- 4 filtros interativos (Map: estado, severidade, confiança mínima, status).
- 2+ visualizações: Plotly stacked area, Plotly stacked bar, Plotly Scattermapbox, Matplotlib bar.
- Layout: sidebar (nav + summary), tabs (analytics), columns (filtros e ações).
- Design para latência: `st.spinner` no boot de estado, `st.cache_data` em dados pesados.
- Cores semânticas: paleta OKLCH crítica/warning/caution/safe consistente em toda app.
- Human-in-the-loop: Approve / Modify and approve / Dismiss com audit trail (resolvidos ficam colapsados, greyed).

## Instalação

Python 3.10+.

```bash
python -m venv .venv
.\.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
```

## Execução

```bash
streamlit run app.py
```

Abre em `http://localhost:8501`.

## Telas

- **Alert queue**: fila de alertas pendentes ordenada por severidade. Cada card mostra região, fonte satelital, confiança, área, vento, rationale do modelo e ação recomendada. Operador aprova, modifica ou descarta. Resolvidos viram audit trail colapsado.
- **Map view**: Scattermapbox Brasil com marcadores por severidade, hover detalhado, 4 filtros, stats bar e lista compacta abaixo.
- **Analytics**: 3 tabs — série temporal 30 dias (Plotly stacked area), impacto por estado (Plotly stacked bar), padrão horário UTC (Matplotlib bar com destaque overpass VIIRS/MODIS).

## Stack

`streamlit · plotly · matplotlib · pandas`
