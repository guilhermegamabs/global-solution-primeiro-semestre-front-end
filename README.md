# IGNIS — Wildfire Command Dashboard

## Integrantes

| Nome | RM |
|---|---|
| Guilherme Gama | RM565293 |
| Igor Thiago Nakajima Vieira | RM563632 |

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

Diagrama completo (Mermaid) em [`ARCHITECTURE.md`](./ARCHITECTURE.md) — camadas, fluxo de alerta, responsabilidades.


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

## Instalação

Python 3.10+.

```bash
python -m venv .venv
.\.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
```

## Modelo de IA (risco de evacuação)

`pipelines/risk_model.py` — `RandomForestClassifier` (scikit-learn) que prevê probabilidade de "ação urgente recomendada" a partir de `fire_area_ha`, `wind_speed`, `confidence`, `hours_since_detection`, `severity_ordinal`. Treinado em dataset sintético reproduzível (seed=42, 5000 amostras), AUC-ROC ~0.78.

```bash
python -m pipelines.train_risk_model     # treina e salva pipelines/risk_model.joblib
```

Score (`ml_risk_score`) é anexado a cada alerta em `init_state` (cacheado via `@st.cache_resource`) e exibido como badge "ML risk N%" no card.

## Testes automatizados

```bash
pytest tests/ -v
```

30 testes cobrem `pipelines/alert_pipeline.py` (ordenação, filtros), `pipelines/enrichment.py` (cruzamento 2ª fonte, agregação), `pipelines/risk_model.py` (predição, alto vs baixo risco) e `providers/` (shape, ranges, alinhamento de arrays). Rodam fora do Streamlit — provam que arquitetura não depende do framework de UI. Config em `pytest.ini`.

## Execução

```bash
streamlit run app.py
```

Abre em `http://localhost:8501`.

## Telas (storytelling panorama → detalhe)

- **Briefing** *(entrada)*: KPIs nacionais (eventos, pendentes, críticos, área queimada, ML risk médio), tabela por UF cruzando carga de incêndio com previsão climática 24h (vento + umidade + chuva) e badge spread_risk_24h. Call-to-action direciona para fila.
- **Alert queue**: fila ordenada por severidade. Card mostra região, satélite, confiança, área, vento, rationale, badge ML risk e ação recomendada. Approve / Modify / Dismiss. Resolvidos viram audit trail colapsado.
- **Map view**: Scattermapbox Brasil, 4 filtros, hover detalhado, stats bar.
- **Analytics**: 3 tabs — série temporal 30 dias (Plotly area), impacto por estado (Plotly bar), padrão horário UTC (Matplotlib bar com overpass VIIRS/MODIS destacado).

## Múltiplas fontes integradas

Pipeline cruza 2 fontes:
1. `providers/mock_alerts.py` — focos satelitais (GOES-16, VIIRS, MODIS).
2. `providers/mock_weather.py` — previsão INMET-like por UF (vento, umidade, chuva).

`pipelines/enrichment.py` calcula `spread_risk_24h` por alerta combinando ambos — exibido no Briefing e disponível em cards/mapa.
