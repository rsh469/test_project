"""
Tea Flavor Aggregator — Streamlit Dashboard
==========================================
Run:  streamlit run app.py
"""

import io
import time
import textwrap
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image

from taxonomy import FLAVOR_WHEEL, CATEGORY_COLORS
from scrapers import collect_all
from aggregator import aggregate, build_sunburst_data, build_radar_data

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Tea Flavor Aggregator",
    page_icon="🍵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #3d2b1f;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #7a5c44;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f0eb, #ede0d4);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        border-left: 4px solid #8b5e3c;
    }
    .source-badge {
        display: inline-block;
        background: #8b5e3c;
        color: white;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.8rem;
        margin: 2px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f5ebe0;
        border-radius: 8px 8px 0 0;
        color: #3d2b1f;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🍵 Tea Flavor Aggregator")
    st.markdown("---")

    tea_input = st.text_input(
        "Введите сорт чая",
        placeholder="Дянь Хун Мао Фэн / Dian Hong Mao Feng",
        help="Можно на русском или английском языке",
    )

    st.markdown("### Параметры поиска")
    use_reddit = st.checkbox("Reddit r/tea", value=True)
    use_steepster = st.checkbox("Steepster", value=True)
    use_ratetea = st.checkbox("RateTea", value=True)
    use_teavivre = st.checkbox("TeaVivre", value=True)
    use_yunnansourcing = st.checkbox("Yunnan Sourcing", value=True)
    use_websearch = st.checkbox("Web Search (DuckDuckGo)", value=True)

    st.markdown("---")
    search_btn = st.button("🔍 Искать и анализировать", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("### Демо-режим")
    demo_btn = st.button("🎯 Загрузить демо-данные", use_container_width=True)

    st.markdown("---")
    st.markdown(
        "<small>Источники: Reddit, Steepster, RateTea, TeaVivre, Yunnan Sourcing, Web</small>",
        unsafe_allow_html=True,
    )

# ── Demo data ─────────────────────────────────────────────────────────────────

DEMO_TEXTS = {
    "Dian Hong Mao Feng": [
        ("Steepster",
         "Beautiful Dian Hong Mao Feng with rich malty sweetness and notes of honey, "
         "cocoa, and dark chocolate. The aroma is floral with hints of rose and orchid. "
         "Smooth texture with a creamy vanilla finish. Some earthy undertones and a hint "
         "of wood. Very low astringency, sweet aftertaste reminiscent of peach and apricot."),
        ("Reddit r/tea",
         "This Yunnan black tea is exceptional. Strong malty backbone, honey sweetness, "
         "and a wonderful roasted aroma. I get caramel, chocolate, and dried fruit notes. "
         "The finish is long with rose and osmanthus florals emerging. Almost no bitterness."),
        ("RateTea",
         "Golden tips produce a rich amber liquor. Flavor profile: honey, caramel, "
         "roasted grain, a whisper of smoke, and beautiful sweet floral notes. "
         "Mouthfeel is buttery. Slight mineral finish. Rose, jasmine undertones."),
        ("TeaVivre",
         "Dian Hong Mao Feng is a premium Yunnan black tea featuring beautiful golden "
         "downy tips. The infusion has a sweet, malty, honey-like character with "
         "chocolate and cocoa nuances. Floral notes of rose and orchid complement "
         "the fruity peach and apricot accents. Earthy, woody base with cedar undertones."),
        ("Yunnan Sourcing",
         "Excellent spring harvest Dian Hong. Aroma: sweet, floral, roasted malt. "
         "Taste: honey, caramel, chocolate, slight earthiness, leather, tobacco. "
         "Finish: lingering sweetness with rose petals and dried fruit (raisin, cherry). "
         "Smooth, creamy, medium body. Mineral aftertaste."),
        ("Web Article",
         "Dian Hong teas are known for their malty flavor, honey sweetness, and floral "
         "bouquet. The best grades display golden tips that contribute to a sweet, "
         "almost sugary quality. Common tasting notes include cocoa, chocolate, rose, "
         "honey, caramel, malt, and stone fruits like peach and apricot. "
         "Some tasters detect woody, earthy or smoky notes, especially in lower grades. "
         "The aftertaste is smooth, sweet, and long-lasting with floral persistence."),
        ("Reddit r/tea",
         "Had a lovely session with Dian Hong Mao Feng today. The honey and malt are "
         "front and center. I also picked up caramel, a hint of vanilla, sweet tobacco, "
         "and something like rose water. The body is thick and satisfying. Great tea!"),
        ("Steepster",
         "Warm and comforting. This tea smells like fresh roses and tastes like liquid "
         "honey with a malt backbone. Notes of almond, chocolate, and dried cherry. "
         "Smooth buttery mouthfeel. Slight mineral and wood in the finish."),
    ]
}


def load_demo_data():
    from scrapers import ReviewEntry
    entries = []
    for tea, texts in DEMO_TEXTS.items():
        for source, text in texts:
            entries.append(ReviewEntry(source=source, tea_name=tea, text=text))
    return entries, "Dian Hong Mao Feng (демо)"


# ── Plotting helpers ───────────────────────────────────────────────────────────

def plot_flavor_wheel_sunburst(data: dict) -> go.Figure:
    sb = build_sunburst_data(data["sunburst_df"])
    fig = go.Figure(go.Sunburst(
        labels=sb["labels"],
        parents=sb["parents"],
        values=sb["values"],
        marker=dict(colors=sb["colors"]),
        branchvalues="total",
        hovertemplate="<b>%{label}</b><br>Упоминаний: %{value}<extra></extra>",
        maxdepth=3,
    ))
    fig.update_layout(
        title=dict(text="Вкусо-ароматическое колесо (Sunburst)", font=dict(size=18)),
        margin=dict(t=60, l=10, r=10, b=10),
        height=600,
    )
    return fig


def plot_radar(data: dict) -> go.Figure:
    rd = build_radar_data(data["radar_data"])
    cats = rd["categories"]
    vals = rd["values"]
    if not cats:
        return go.Figure()
    colors_list = [CATEGORY_COLORS.get(c, "#999") for c in data["radar_data"]["category"]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals,
        theta=cats,
        fill="toself",
        fillcolor="rgba(139,94,60,0.25)",
        line=dict(color="#8b5e3c", width=2),
        name="Профиль",
        hovertemplate="%{theta}: %{r:.1%}<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(vals) * 1.2 if vals else 1],
                            tickformat=".0%"),
            angularaxis=dict(direction="clockwise"),
        ),
        showlegend=False,
        title=dict(text="Радарная диаграмма категорий", font=dict(size=18)),
        height=500,
        margin=dict(t=80, l=60, r=60, b=60),
    )
    return fig


def plot_category_bar(data: dict) -> go.Figure:
    df = data["cat_totals"].sort_values("count", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["count"],
        y=df["category"],
        orientation="h",
        marker_color=df["color"],
        text=df["count"],
        textposition="outside",
        hovertemplate="%{y}: %{x} упоминаний<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Категории вкусо-ароматических дескрипторов", font=dict(size=16)),
        xaxis_title="Количество упоминаний",
        height=420,
        margin=dict(t=50, l=180, r=60, b=40),
        plot_bgcolor="#faf7f4",
    )
    return fig


def plot_top_keywords(data: dict, n: int = 30) -> go.Figure:
    df = data["kw_freq"].head(n).sort_values("count", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["count"],
        y=df["keyword"],
        orientation="h",
        marker_color=df["color"],
        text=df["count"],
        textposition="outside",
        hovertemplate="%{y} (%{customdata}): %{x}<extra></extra>",
        customdata=df["category"],
    ))
    fig.update_layout(
        title=dict(text=f"Топ-{n} дескрипторов", font=dict(size=16)),
        xaxis_title="Количество упоминаний",
        height=700,
        margin=dict(t=50, l=160, r=60, b=40),
        plot_bgcolor="#faf7f4",
    )
    return fig


def plot_subcategory_bar(data: dict) -> go.Figure:
    df = data["sub_totals"].head(25).sort_values("count", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["count"],
        y=df["subcategory"],
        orientation="h",
        marker_color=df["color"],
        text=df["count"],
        textposition="outside",
        hovertemplate="%{y} [%{customdata}]: %{x}<extra></extra>",
        customdata=df["category"],
    ))
    fig.update_layout(
        title=dict(text="Топ подкатегорий вкуса/аромата", font=dict(size=16)),
        xaxis_title="Количество упоминаний",
        height=550,
        margin=dict(t=50, l=180, r=60, b=40),
        plot_bgcolor="#faf7f4",
    )
    return fig


def plot_source_heatmap(data: dict) -> go.Figure:
    df = data["source_cat"]
    pivot = df.pivot_table(index="source", columns="category", values="count", fill_value=0)
    # Normalize rows
    pivot_norm = pivot.div(pivot.sum(axis=1), axis=0).fillna(0)

    fig = go.Figure(go.Heatmap(
        z=pivot_norm.values,
        x=pivot_norm.columns.tolist(),
        y=pivot_norm.index.tolist(),
        colorscale="YlOrBr",
        hovertemplate="Источник: %{y}<br>Категория: %{x}<br>Доля: %{z:.1%}<extra></extra>",
        text=pivot_norm.round(2).values,
        texttemplate="%{z:.0%}",
    ))
    fig.update_layout(
        title=dict(text="Тепловая карта: дескрипторы по источникам", font=dict(size=16)),
        xaxis_tickangle=-35,
        height=380,
        margin=dict(t=60, l=150, r=40, b=100),
    )
    return fig


def plot_source_breakdown(data: dict) -> go.Figure:
    df = data["source_cat"]
    sources = df["source"].unique().tolist()
    categories = df["category"].unique().tolist()

    fig = go.Figure()
    for cat in categories:
        sub = df[df["category"] == cat]
        fig.add_trace(go.Bar(
            name=cat,
            x=sub["source"],
            y=sub["count"],
            marker_color=CATEGORY_COLORS.get(cat, "#999"),
            hovertemplate=f"<b>{cat}</b><br>%{{x}}: %{{y}}<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack",
        title=dict(text="Дескрипторы по источникам (stacked)", font=dict(size=16)),
        xaxis_title="Источник",
        yaxis_title="Упоминания",
        height=420,
        plot_bgcolor="#faf7f4",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=80, b=80),
    )
    return fig


def plot_wordcloud(wc_data: dict) -> Image.Image:
    if not wc_data:
        return None
    wc = WordCloud(
        width=900,
        height=420,
        background_color="white",
        colormap="copper",
        max_words=80,
        prefer_horizontal=0.8,
        collocations=False,
        font_path=None,
    ).generate_from_frequencies(wc_data)
    return wc.to_image()


def plot_treemap(data: dict) -> go.Figure:
    sub = data["sub_totals"].copy()
    sub["parent_label"] = sub["category"]
    fig = px.treemap(
        sub,
        path=["category", "subcategory"],
        values="count",
        color="category",
        color_discrete_map=CATEGORY_COLORS,
        title="Трикарта вкусо-ароматических дескрипторов",
    )
    fig.update_traces(
        hovertemplate="%{label}<br>Упоминаний: %{value}<extra></extra>",
        textinfo="label+value",
    )
    fig.update_layout(height=500, margin=dict(t=60, l=10, r=10, b=10))
    return fig


def plot_pie(data: dict) -> go.Figure:
    df = data["cat_totals"]
    fig = go.Figure(go.Pie(
        labels=df["category"],
        values=df["count"],
        marker=dict(colors=df["color"]),
        hole=0.4,
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
        textinfo="label+percent",
    ))
    fig.update_layout(
        title=dict(text="Распределение категорий", font=dict(size=16)),
        height=450,
        legend=dict(orientation="h"),
        margin=dict(t=60, b=40),
    )
    return fig


def plot_cumulative_bar(data: dict, top_n: int = 20) -> go.Figure:
    df = data["kw_freq"].head(top_n).copy()
    df = df.sort_values("count", ascending=False)
    df["cumulative"] = df["count"].cumsum()
    df["cumulative_pct"] = 100 * df["cumulative"] / df["count"].sum()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["keyword"],
        y=df["count"],
        name="Упоминания",
        marker_color=df["color"],
        hovertemplate="%{x}: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["keyword"],
        y=df["cumulative_pct"],
        name="Накопл. %",
        yaxis="y2",
        line=dict(color="#3d2b1f", width=2, dash="dash"),
        marker=dict(size=5),
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=f"Парето: топ-{top_n} дескрипторов", font=dict(size=16)),
        yaxis=dict(title="Упоминания"),
        yaxis2=dict(title="Накопленный %", overlaying="y", side="right",
                    range=[0, 110], ticksuffix="%"),
        xaxis_tickangle=-35,
        height=450,
        plot_bgcolor="#faf7f4",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(t=80, b=100),
    )
    return fig


# ── Main layout ───────────────────────────────────────────────────────────────

st.markdown('<p class="main-title">🍵 Tea Flavor Aggregator</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Агрегатор вкусо-ароматических дескрипторов чая из множества источников</p>',
    unsafe_allow_html=True,
)

# ── Session state ──────────────────────────────────────────────────────────────

if "results" not in st.session_state:
    st.session_state.results = None
if "tea_label" not in st.session_state:
    st.session_state.tea_label = ""

# ── Handle search / demo ───────────────────────────────────────────────────────

if demo_btn:
    with st.spinner("Загружаем демо-данные..."):
        reviews, label = load_demo_data()
        st.session_state.results = aggregate(reviews)
        st.session_state.tea_label = label
        st.session_state.reviews = reviews
    st.success(f"Демо: {label} — загружено {len(reviews)} отзывов")

if search_btn and tea_input.strip():
    tea_query = tea_input.strip()
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    total_steps = sum([use_reddit, use_steepster, use_ratetea,
                       use_teavivre, use_yunnansourcing, use_websearch])
    step = 0

    from scrapers import (scrape_reddit, scrape_steepster, scrape_ratetea,
                          scrape_teavivre, scrape_yunnansourcing, scrape_web_search,
                          ReviewEntry)

    all_reviews = []
    scraper_map = [
        (use_reddit, "Reddit r/tea", scrape_reddit),
        (use_steepster, "Steepster", scrape_steepster),
        (use_ratetea, "RateTea", scrape_ratetea),
        (use_teavivre, "TeaVivre", scrape_teavivre),
        (use_yunnansourcing, "Yunnan Sourcing", scrape_yunnansourcing),
        (use_websearch, "Web Search", scrape_web_search),
    ]

    for enabled, name, fn in scraper_map:
        if enabled:
            status_placeholder.info(f"🔍 Сканирую **{name}**...")
            try:
                entries = fn(tea_query)
                all_reviews.extend(entries)
            except Exception as e:
                st.warning(f"Ошибка при сборе с {name}: {e}")
            step += 1
            progress_bar.progress(step / total_steps)

    progress_bar.empty()
    status_placeholder.empty()

    if all_reviews:
        st.session_state.results = aggregate(all_reviews)
        st.session_state.tea_label = tea_query
        st.session_state.reviews = all_reviews
        st.success(f"Собрано {len(all_reviews)} отзывов/описаний для «{tea_query}»")
    else:
        st.warning("Ничего не найдено. Попробуйте другое название или включите демо-режим.")

elif search_btn and not tea_input.strip():
    st.warning("Введите название чая для поиска.")

# ── Dashboard ──────────────────────────────────────────────────────────────────

data = st.session_state.results

if data is None:
    st.info("👆 Введите название сорта чая в боковой панели и нажмите **«Искать»**, "
            "или загрузите **демо-данные** для Dian Hong Mao Feng.")

    # Show taxonomy reference
    with st.expander("📖 Справка: вкусо-ароматическое колесо (таксономия)"):
        cols = st.columns(3)
        for i, (cat, cat_data) in enumerate(FLAVOR_WHEEL.items()):
            with cols[i % 3]:
                st.markdown(f"**{cat}**")
                for sub in cat_data["subcategories"]:
                    st.markdown(f"  - {sub}")

else:
    tea_label = st.session_state.tea_label

    # ── KPI bar ─────────────────────────────────────────────────────────────
    st.markdown(f"### Анализ: **{tea_label}**")
    k1, k2, k3, k4 = st.columns(4)
    reviews_total = data.get("reviews_total", 0)
    total_mentions = data.get("total_mentions", 0)
    n_keywords = len(data.get("kw_freq", [])) if not data.get("empty") else 0
    n_sources = data["source_cat"]["source"].nunique() if not data.get("empty") else 0

    with k1:
        st.metric("📄 Источников/отзывов", reviews_total)
    with k2:
        st.metric("🔢 Всего упоминаний", total_mentions)
    with k3:
        st.metric("🏷️ Уникальных дескрипторов", n_keywords)
    with k4:
        st.metric("🌐 Источников данных", n_sources)

    if data.get("empty"):
        st.warning("Дескрипторы не найдены в собранных текстах. "
                   "Попробуйте другой запрос или загрузите демо-данные.")
    else:
        # ── Tabs ────────────────────────────────────────────────────────────
        tab_wheel, tab_radar, tab_bars, tab_pareto, tab_treemap, \
        tab_heatmap, tab_sources, tab_wc, tab_data = st.tabs([
            "🌸 Flavor Wheel",
            "🕸️ Radar",
            "📊 Bar Charts",
            "📈 Парето",
            "🗂️ Treemap",
            "🌡️ Heatmap",
            "📡 По источникам",
            "☁️ Облако слов",
            "🗃️ Данные",
        ])

        with tab_wheel:
            st.plotly_chart(plot_flavor_wheel_sunburst(data), use_container_width=True)
            st.caption("Sunburst-диаграмма показывает иерархию: Категория → Подкатегория → Ключевое слово. "
                       "Размер сегмента пропорционален числу упоминаний.")

        with tab_radar:
            col_r1, col_r2 = st.columns([3, 2])
            with col_r1:
                st.plotly_chart(plot_radar(data), use_container_width=True)
            with col_r2:
                st.plotly_chart(plot_pie(data), use_container_width=True)

        with tab_bars:
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.plotly_chart(plot_category_bar(data), use_container_width=True)
            with col_b2:
                st.plotly_chart(plot_subcategory_bar(data), use_container_width=True)
            st.markdown("---")
            n_top = st.slider("Число топ-дескрипторов", 10, 60, 30, key="top_kw_slider")
            st.plotly_chart(plot_top_keywords(data, n=n_top), use_container_width=True)

        with tab_pareto:
            n_pareto = st.slider("Число дескрипторов в Парето", 10, 40, 20, key="pareto_slider")
            st.plotly_chart(plot_cumulative_bar(data, top_n=n_pareto), use_container_width=True)
            st.caption("Диаграмма Парето показывает, какие дескрипторы составляют 80% всех упоминаний.")

        with tab_treemap:
            st.plotly_chart(plot_treemap(data), use_container_width=True)

        with tab_heatmap:
            if n_sources > 1:
                st.plotly_chart(plot_source_heatmap(data), use_container_width=True)
                st.caption("Цвет показывает долю упоминаний данной категории в конкретном источнике.")
            else:
                st.info("Для тепловой карты нужно минимум 2 источника данных.")

        with tab_sources:
            if n_sources > 0:
                st.plotly_chart(plot_source_breakdown(data), use_container_width=True)
                st.markdown("#### Топ дескрипторов по каждому источнику")
                source_kw = data["source_kw"]
                for src in source_kw["source"].unique():
                    with st.expander(f"📡 {src}"):
                        sub = source_kw[source_kw["source"] == src].head(15)
                        st.dataframe(sub[["keyword", "category", "count"]].reset_index(drop=True),
                                     use_container_width=True)

        with tab_wc:
            wc_img = plot_wordcloud(data["wc_data"])
            if wc_img:
                st.image(wc_img, use_column_width=True,
                         caption="Облако слов: размер пропорционален числу упоминаний")
            else:
                st.warning("Нет данных для облака слов.")

        with tab_data:
            st.markdown("#### Все дескрипторы (частоты)")
            st.dataframe(data["kw_freq"].reset_index(drop=True), use_container_width=True)
            st.markdown("#### Сырые записи")
            if "reviews" in st.session_state:
                raw_rows = [
                    {"source": r.source, "tea_name": r.tea_name,
                     "url": r.url, "text_preview": r.text[:200] + "..."}
                    for r in st.session_state.reviews
                ]
                st.dataframe(pd.DataFrame(raw_rows), use_container_width=True)

            # Download button
            csv = data["kw_freq"].to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Скачать CSV дескрипторов",
                data=csv,
                file_name=f"{tea_label.replace(' ', '_')}_descriptors.csv",
                mime="text/csv",
            )

# ── Footer ─────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<small>Tea Flavor Aggregator · данные: Reddit, Steepster, RateTea, TeaVivre, "
    "Yunnan Sourcing, Web · таксономия: World Tea Flavor Wheel</small>",
    unsafe_allow_html=True,
)
