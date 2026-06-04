"""
================================================================================
SIMULADOR ECONÓMICO MecaSync S.A.S. - Aplicación Web Interactiva (Streamlit)
================================================================================
Proyecto Final - Economía - Ingeniería en Mecatrónica
Universidad Militar Nueva Granada - 2026-I

Integrantes: Juan Osuna, Santiago Rey, Juan Parrado, Germán Salazar

EJECUCIÓN:
    1. Instalar dependencias: pip install "streamlit>=1.28.0" "numpy>=1.24.0" "pandas>=2.0.0" "plotly>=5.17.0"
    2. Correr la app:          streamlit run app.py
    

================================================================================
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================

st.set_page_config(
    page_title="Simulador MecaSync S.A.S.",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Header principal */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        color: white;
    }
    .main-header p {
        margin: 0.3rem 0 0 0;
        opacity: 0.9;
    }

    /* Tarjetas de métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
    }

    /* Veredicto card */
    .veredicto-verde {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
    }
    .veredicto-amarillo {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
    }
    .veredicto-rojo {
        background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
    }
    .veredicto-card h2 {
        color: white;
        margin: 0;
        font-size: 1.5rem;
    }
    .veredicto-card p {
        color: white;
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }

    /* Concepto card */
    .concepto-card {
        background: #f8f9fa;
        border-left: 4px solid #2a5298;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        border-radius: 6px;
    }
    .concepto-card h4 {
        margin: 0 0 0.5rem 0;
        color: #1e3c72;
    }

    /* Reducir padding de tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 16px;
        background-color: #f0f2f6;
        border-radius: 8px;
        color: #1F2937 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2a5298 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Paleta de colores
COL_ACTUAL  = "#3498db"
COL_PARCIAL = "#2ecc71"
COL_TOTAL   = "#e74c3c"

# Valores base para comparación de deltas
VALORES_BASE = {
    "precio_venta": 2_500_000,
    "demanda": 520,
    "trm": 4_150,
    "inflacion": 0.045,
    "tasa_interes": 0.12,
    "salario_integral": 2_800_000,
    "operarios_actual": 12,
    "operarios_parcial": 8,
    "operarios_total": 3,
    "capex_mejoras": 65_000_000,
    "capex_parcial": 320_000_000,
    "capex_total": 1_000_000_000,
    "capacidad_actual": 550,
    "capacidad_parcial": 720,
    "capacidad_total": 950,
    "cf_actual": 180_000_000,
    "cf_parcial": 235_000_000,
    "cf_total": 345_000_000,
    "cv_materiales": 1_750_000,
    "horizonte": 5,
}


# ==============================================================================
# SISTEMA DEL TOUR GUIADO
# ==============================================================================

# Inicialización del estado del tour
if "tour_activo" not in st.session_state:
    st.session_state.tour_activo = False
if "tour_paso" not in st.session_state:
    st.session_state.tour_paso = 1

# Contenido de cada paso del tour
TOTAL_PASOS = 9
PASOS_TOUR = {
    1: {
        "tab_nombre": "🎓 Cómo usar",
        "titulo": "Bienvenidos — explorando el panel de control",
        "narracion": """
        Antes de calcular nada, observen el **panel lateral izquierdo (sidebar)**.
        Ahí está concentrada toda la información de entrada del modelo: precio, demanda,
        TRM, inflación, tasa de interés, salarios, CAPEX, capacidad instalada, etc.

        Cada slider es un **supuesto declarado** del caso MecaSync S.A.S. Al modificarlo,
        todo el simulador se recalcula automáticamente y muestra cómo cambian los indicadores.

        Esto permite hacer **análisis de sensibilidad** sobre cualquier variable del modelo.
        """,
        "observar": """
        - Las **7 secciones** del sidebar agrupan variables por categoría temática
        - El botón **🔄 Restaurar valores por defecto** vuelve al escenario base
        - Cada slider tiene un **tooltip explicativo** (paren el cursor sobre el ícono de ayuda)
        """,
        "siguiente_tab": "📊 Dashboard",
    },
    2: {
        "tab_nombre": "📊 Dashboard",
        "titulo": "El veredicto y los indicadores financieros",
        "narracion": """
        Aquí está el **resumen ejecutivo del análisis**. Lo primero es el veredicto
        del simulador: una recomendación generada automáticamente integrando todos los
        indicadores económicos.

        Debajo, los **indicadores financieros por alternativa**: Ganancia, ROI, Payback,
        Utilidad mensual. Estos son los criterios clásicos de evaluación de proyectos
        de inversión.
        """,
        "observar": """
        - **Ganancia positiva** (verde) significa que la alternativa genera valor económico
        - **Ganancia negativa** (rojo) significa que destruye valor
        - El **ROI** debe superar la tasa de interés (12%) para que el proyecto sea mejor que un CDT
        - El **Payback** indica en cuántos años se recupera la inversión
        """,
        "siguiente_tab": "💰 Costos",
    },
    3: {
        "tab_nombre": "💰 Costos",
        "titulo": "Descomposición de costos — el corazón de la microeconomía",
        "narracion": """
        Aquí se descomponen los costos por alternativa. Vemos:
        - **Costos fijos (CF):** mano de obra fija, arriendo, mantenimiento base
        - **Costos variables (CV):** materiales, energía, reproceso
        - **Costo total (CT) = CF + CV**
        - **Costo medio (CMe) = CT / Q** — costo por unidad
        - **Costo marginal (CMg)** — costo de producir una unidad adicional

        La gráfica izquierda muestra dónde está el **punto de equilibrio** (intersección CT-IT)
        y la gráfica derecha cómo el costo medio baja con la escala (economías de escala).
        """,
        "observar": """
        - El sistema actual tiene **CF bajo** pero **CVu alto** (mucho reproceso)
        - La auto. total tiene **CF alto** pero **CVu bajo** (línea más eficiente)
        - La auto. parcial es el **equilibrio óptimo** entre ambos extremos
        """,
        "siguiente_tab": "📈 Mercado",
    },
    4: {
        "tab_nombre": "📈 Mercado",
        "titulo": "Oferta, demanda y elasticidad",
        "narracion": """
        Aquí analizamos el mercado donde opera MecaSync. La **curva de demanda** es
        Q = 1300 - 0.000312·P (lineal, decreciente).

        La **elasticidad precio (ε)** mide qué tanto cambia la cantidad demandada
        cuando cambia el precio. Con ε = -1.500 tenemos **demanda elástica**: subir
        precios reduce significativamente las ventas.

        Las **curvas horizontales** son las ofertas de cada alternativa (su CMg).
        Las **líneas verticales punteadas** son las capacidades instaladas.
        """,
        "observar": """
        - Cuando |ε| > 1 → demanda **elástica** (cuidado al subir precios)
        - Cuando |ε| < 1 → demanda **inelástica** (puede subir precios sin perder mucho volumen)
        - El **punto negro** indica precio y cantidad actuales del modelo
        """,
        "siguiente_tab": "⚙️ Productividad",
    },
    5: {
        "tab_nombre": "⚙️ Productividad",
        "titulo": "El trade-off central del proyecto",
        "narracion": """
        Este tab muestra el **insight más importante del análisis**. Tenemos tres indicadores:

        - **Productividad** (uds/hora-hombre): la auto. total gana claramente
        - **Eficiencia técnica** (Q/capacidad): el sistema actual la maximiza
        - **Eficiencia económica** (utilidad/CT): aquí está la sorpresa

        La automatización total es la **mejor en productividad** pero la **peor en
        eficiencia económica**. Esto demuestra que la mejor opción técnica no
        siempre es la mejor opción económica.
        """,
        "observar": """
        - Auto. total: productividad **0.903** uds/h-h (la más alta)
        - Auto. total: eficiencia económica **negativa** (-2.1%)
        - Auto. parcial: el **balance óptimo** entre las tres dimensiones
        """,
        "siguiente_tab": "🌎 Macro",
    },
    6: {
        "tab_nombre": "🌎 Macro",
        "titulo": "El contexto macroeconómico importa",
        "narracion": """
        El proyecto no vive en el vacío. Variables macroeconómicas como **inflación,
        tasa de interés, TRM, política fiscal y monetaria, ciclos económicos y
        comercio internacional** afectan directamente la viabilidad.

        Aquí vemos especialmente el **impacto de la TRM en el CAPEX**: las alternativas
        con mayor componente importado (sensores, PLC, robots) son más sensibles
        a la devaluación del peso.
        """,
        "observar": """
        - **Auto. total** es la más expuesta al riesgo cambiario
        - La **TRM actual** vs la TRM de cotización inicial genera ajustes al CAPEX
        - Las 7 variables macro explicadas tienen aplicación real al caso
        """,
        "siguiente_tab": "🎲 Escenarios",
    },
    7: {
        "tab_nombre": "🎲 Escenarios",
        "titulo": "Análisis de riesgo económico",
        "narracion": """
        Ninguna decisión responsable se toma sin considerar **qué pasa si la
        coyuntura cambia**. Aquí simulamos tres escenarios:

        - **Pesimista:** demanda -25%, TRM 4.600, inflación 7.5%, tasa 16%
        - **Probable:** los valores base del modelo
        - **Optimista:** demanda +20%, TRM 3.850, inflación 3%, tasa 9%

        Esto es **análisis de sensibilidad multivariable**. Una alternativa puede ser
        excelente en el escenario base pero **no resistir un escenario adverso**.
        """,
        "observar": """
        - En el **escenario pesimista**, todas las alternativas tienen Ganancia negativa
        - Por eso el veredicto es "IMPLEMENTAR POR FASES" en lugar de "IMPLEMENTAR"
        - La auto. parcial sigue siendo la **más resiliente** en escenarios adversos
        """,
        "siguiente_tab": "⚖️ Matriz de decisión",
    },
    8: {
        "tab_nombre": "⚖️ Matriz de decisión",
        "titulo": "Decisión multicriterio ponderada",
        "narracion": """
        La Ganancia sola no basta para decidir. Aquí integramos **7 criterios ponderados**:
        rentabilidad, productividad, eficiencia económica, riesgo, payback,
        flexibilidad operativa y bajo CAPEX.

        Cada alternativa se califica de 1 a 5 en cada criterio, y se pondera por
        importancia. El **puntaje total** integra todas las dimensiones del análisis
        en una sola métrica.
        """,
        "observar": """
        - **Auto. parcial** obtiene el mayor puntaje ponderado (4.30 / 5.00)
        - **Sistema actual** queda segundo (3.35) — bajo riesgo pero baja rentabilidad
        - **Auto. total** es la peor (3.00) — alta productividad pero alto riesgo
        - El **umbral verde (3.5)** indica un puntaje aceptable
        """,
        "siguiente_tab": "📚 Conceptos económicos",
    },
    9: {
        "tab_nombre": "📚 Conceptos económicos",
        "titulo": "Conceptos económicos aplicados — cierre del tour",
        "narracion": """
        Para cerrar el tour, este tab es un **glosario rápido** de los 17+ conceptos
        económicos aplicados en el simulador. Es un repaso útil del aparato conceptual
        que sustenta todo el análisis.

        **¡Han recorrido las 9 etapas del análisis económico!**

        Ahora pueden:
        - Volver al **panel lateral** y experimentar con los sliders
        - Probar los **15 casos de estudio** del tab "Cómo usar"
        - Modificar variables y ver cómo cambia el veredicto en tiempo real
        """,
        "observar": """
        - Los **17 conceptos** aplicados superan el mínimo curricular de 10
        - El **insight clave** del proyecto se resume al final de este tab
        - Cada concepto tiene una definición + aplicación concreta al modelo
        """,
        "siguiente_tab": None,  # Es el último paso
    },
}


def mostrar_paso_tour(paso_del_tab):
    """
    Muestra el banner del tour si el paso actual coincide con el paso de este tab.
    Si el tour está activo pero estamos en un tab equivocado, muestra un mini-aviso.
    """
    if not st.session_state.tour_activo:
        return

    paso_actual = st.session_state.tour_paso

    if paso_actual != paso_del_tab:
        # El tour está activo pero estamos en el tab equivocado
        if paso_actual in PASOS_TOUR:
            tab_correcto = PASOS_TOUR[paso_actual]["tab_nombre"]
            st.info(f"🎓 **Tour activo — Paso {paso_actual} de {TOTAL_PASOS}** · "
                   f"Para continuar el tour, vayan al tab **{tab_correcto}**")
        return

    # Es el paso correcto - mostrar contenido completo del paso
    info = PASOS_TOUR[paso_actual]

    st.success(f"""
    ### 🎓 Tour guiado — Paso {paso_actual} de {TOTAL_PASOS}
    #### {info['titulo']}

    {info['narracion']}
    """)

    if info.get("observar"):
        with st.expander("👀 **Qué observar específicamente**", expanded=False):
            st.markdown(info["observar"])

    # Hint del siguiente paso
    if info.get("siguiente_tab"):
        st.markdown(f"⏭️ **Próximo paso:** al avanzar, vayan al tab **{info['siguiente_tab']}**")

    # Botones de navegación
    col_prev, col_next, col_exit = st.columns([1, 1, 1])
    with col_prev:
        if st.button("← Anterior", disabled=(paso_actual == 1),
                    key=f"tour_prev_{paso_actual}", use_container_width=True):
            st.session_state.tour_paso = max(1, paso_actual - 1)
            st.rerun()
    with col_next:
        if paso_actual < TOTAL_PASOS:
            if st.button("Siguiente →", key=f"tour_next_{paso_actual}",
                        type="primary", use_container_width=True):
                st.session_state.tour_paso = paso_actual + 1
                st.rerun()
        else:
            if st.button("✓ Finalizar tour", key=f"tour_end_{paso_actual}",
                        type="primary", use_container_width=True):
                st.session_state.tour_activo = False
                st.session_state.tour_paso = 1
                st.rerun()
    with col_exit:
        if st.button("🚪 Salir del tour", key=f"tour_exit_{paso_actual}",
                    use_container_width=True):
            st.session_state.tour_activo = False
            st.session_state.tour_paso = 1
            st.rerun()

    st.markdown("---")


# ==============================================================================
# FUNCIONES DE CÁLCULO ECONÓMICO
# ==============================================================================

def calcular_alternativa(params, tipo):
    """Calcula todos los indicadores económicos de una alternativa."""

    if tipo == "actual":
        capex = params["capex_mejoras"]
        operarios = params["operarios_actual"]
        cf_otros = params["cf_actual"]
        cv_energia = 45_000
        cv_reproceso = 280_000
        capacidad = params["capacidad_actual"]
        importados_usd = 5_000
    elif tipo == "parcial":
        capex = params["capex_parcial"]
        operarios = params["operarios_parcial"]
        cf_otros = params["cf_parcial"]
        cv_energia = 62_000
        cv_reproceso = 110_000
        capacidad = params["capacidad_parcial"]
        importados_usd = 48_000
    elif tipo == "total":
        capex = params["capex_total"]
        operarios = params["operarios_total"]
        cf_otros = params["cf_total"]
        cv_energia = 85_000
        cv_reproceso = 38_000
        capacidad = params["capacidad_total"]
        importados_usd = 145_000

    # Producción real (limitada por capacidad)
    Q = min(params["demanda"], capacidad)

    # Costos — el TRM también encarece materiales importados
    cf_mano_obra = operarios * params["salario_integral"]
    CF = cf_otros + cf_mano_obra
    # 30% de los materiales son componentes importados → suben con la TRM
    factor_trm_mat = 1 + 0.30 * (params["trm"] - 4_000) / 4_000
    cv_materiales_real = params["cv_materiales"] * factor_trm_mat
    CVu = cv_materiales_real + cv_energia + cv_reproceso
    CV = CVu * Q
    CT = CF + CV
    CMe = CT / Q if Q > 0 else 0
    CMg = CVu

    # Ingresos y utilidad
    P = params["precio_venta"]
    IT = P * Q
    utilidad_mensual = IT - CT
    utilidad_anual = utilidad_mensual * 12

    # CAPEX ajustado por TRM (equipos importados)
    capex_ajustado = capex + importados_usd * (params["trm"] - 4_000)

    # Punto de equilibrio
    Q_equilibrio = CF / (P - CVu) if (P - CVu) > 0 else float('inf')

    # Productividad y eficiencia
    horas_hombre_total = operarios * 192
    productividad = Q / horas_hombre_total if horas_hombre_total > 0 else 0
    eficiencia_tecnica = Q / capacidad if capacidad > 0 else 0
    eficiencia_economica = utilidad_mensual / CT if CT > 0 else 0

    # Rentabilidad con ajuste macroeconómico
    horizonte = params["horizonte"]
    inflacion = params["inflacion"]
    tasa = params["tasa_interes"]

    # 1. INFLACIÓN sube los costos fijos a lo largo del horizonte
    factor_inflacion = 1 + inflacion * (horizonte - 1) / 3
    CF_promedio = CF * factor_inflacion
    CT_promedio = CF_promedio + CV  # CV usa precios actuales de materiales
    utilidad_promedio = IT - CT_promedio

    # 2. GANANCIA BRUTA del proyecto
    ganancia_bruta = (utilidad_promedio * 12 * horizonte) - capex_ajustado

    # 3. COSTO DE OPORTUNIDAD (interés compuesto del CDT)
    ganancia_cdt = capex_ajustado * ((1 + tasa) ** horizonte - 1)

    # 4. PRIMA DE RIESGO MACROECONÓMICO
    #    Penaliza cuando inflación, tasa o TRM están por encima de la línea base
    #    A peor entorno macro, mayor prima → menor ganancia
    desviacion_inf = max(0, inflacion - 0.045)
    desviacion_tasa = max(0, tasa - 0.12)
    desviacion_trm = max(0, (params["trm"] - 4150) / 4150)
    prima_riesgo = (desviacion_inf * 2 + desviacion_tasa * 1.5 + desviacion_trm) * capex_ajustado * horizonte / 2

    # 5. GANANCIA NETA = bruta - CDT - riesgo macro
    ganancia_proyecto = ganancia_bruta - ganancia_cdt - prima_riesgo

    margen = utilidad_promedio / IT if IT > 0 else 0
    payback = capex_ajustado / (utilidad_promedio * 12) if utilidad_promedio > 0 else float('inf')
    ROI = (utilidad_promedio * 12) / capex_ajustado if capex_ajustado > 0 else 0
    ventaja_vs_cdt = ganancia_proyecto

    return {
        "tipo": tipo, "Q": Q, "P": P, "CF": CF, "CV": CV, "CT": CT,
        "CVu": CVu, "CMe": CMe, "CMg": CMg, "IT": IT,
        "utilidad_mensual": utilidad_mensual, "utilidad_anual": utilidad_anual,
        "capex": capex, "capex_ajustado": capex_ajustado,
        "Q_equilibrio": Q_equilibrio, "productividad": productividad,
        "eficiencia_tecnica": eficiencia_tecnica,
        "eficiencia_economica": eficiencia_economica,
        "capacidad": capacidad, "operarios": operarios,
        "ganancia_proyecto": ganancia_proyecto, "margen": margen,
        "payback": payback, "ROI": ROI,
        "ventaja_vs_cdt": ventaja_vs_cdt,
    }



def calcular_escenarios(params_base):
    """Calcula resultados para 3 escenarios RELATIVOS a los valores actuales."""
    escenarios_def = {
        "PESIMISTA": {"demanda_mult": 0.85, "precio_mult": 0.97, "trm_delta": 300, "cf_mult": 1.03, "salario_mult": 1.05},
        "PROBABLE":  {"demanda_mult": 1.0,  "precio_mult": 1.0,  "trm_delta": 0,   "cf_mult": 1.0,  "salario_mult": 1.0},
        "OPTIMISTA": {"demanda_mult": 1.20, "precio_mult": 1.05, "trm_delta": -300, "cf_mult": 0.95, "salario_mult": 0.95},
    }
    resultados = {}
    for esc, m in escenarios_def.items():
        p = params_base.copy()
        p["demanda"] = int(params_base["demanda"] * m["demanda_mult"])
        p["precio_venta"] = params_base["precio_venta"] * m["precio_mult"]
        p["trm"] = params_base["trm"] + m["trm_delta"]
        p["salario_integral"] = params_base["salario_integral"] * m["salario_mult"]
        p["cf_actual"]  = params_base["cf_actual"]  * m["cf_mult"]
        p["cf_parcial"] = params_base["cf_parcial"] * m["cf_mult"]
        p["cf_total"]   = params_base["cf_total"]   * m["cf_mult"]
        resultados[esc] = {
            "actual":  calcular_alternativa(p, "actual"),
            "parcial": calcular_alternativa(p, "parcial"),
            "total":   calcular_alternativa(p, "total"),
        }
    return resultados


def calcular_matriz_multicriterio(res_actual, res_parcial, res_total):
    """Calcula la matriz con puntajes DINÁMICOS basados en resultados."""
    pesos = {
        "Rentabilidad":           0.25,
        "Productividad":          0.15,
        "Eficiencia económica":   0.15,
        "Bajo riesgo":            0.15,
        "Recuperación rápida":    0.10,
        "Flexibilidad operativa": 0.10,
        "Bajo CAPEX":             0.10,
    }
    def rank3(vals, higher_better=True):
        idx = sorted(range(3), key=lambda i: vals[i], reverse=higher_better)
        s = [0,0,0]; s[idx[0]]=5; s[idx[1]]=4; s[idx[2]]=2
        return s
    R = [res_actual, res_parcial, res_total]
    sc = [
        rank3([r["ganancia_proyecto"] for r in R], True),
        rank3([r["productividad"] for r in R], True),
        rank3([r["eficiencia_economica"] for r in R], True),
        rank3([r["capex_ajustado"] for r in R], False),
        rank3([r["payback"] if r["payback"]!=float("inf") else 9999 for r in R], False),
        rank3([r["operarios"] for r in R], True),
        rank3([r["capex_ajustado"] for r in R], False),
    ]
    alt_names = ["Sistema actual","Automatización parcial","Automatización total"]
    crit_names = list(pesos.keys())
    puntajes = {}
    for i, alt in enumerate(alt_names):
        puntajes[alt] = {crit_names[j]: sc[j][i] for j in range(7)}
    totales = {}; detalle = {}
    for alt, scores in puntajes.items():
        total = 0; detalle[alt] = {}
        for crit, p in scores.items():
            pond = p * pesos[crit]; detalle[alt][crit] = (p, pesos[crit], pond); total += pond
        totales[alt] = total
    return pesos, puntajes, totales, detalle


def generar_veredicto(res_actual, res_parcial, res_total, escenarios, totales_matriz, tasa):
    """Genera recomendación basada en ganancia, margen, ROI y escenarios."""
    ganadora_nombre = max(totales_matriz, key=totales_matriz.get)
    mapa = {"Sistema actual": (res_actual, "actual"),
            "Automatización parcial": (res_parcial, "parcial"),
            "Automatización total": (res_total, "total")}
    res_g, key_g = mapa[ganadora_nombre]
    gan = res_g["ganancia_proyecto"]
    margen = res_g["margen"]
    roi = res_g["ROI"]
    pb = res_g["payback"]
    gan_pesim = escenarios["PESIMISTA"][key_g]["ganancia_proyecto"]
    todas_neg = all(r["ganancia_proyecto"] <= 0 for r in [res_actual, res_parcial, res_total])

    if todas_neg:
        return {"veredicto": "DESCARTAR automatización",
                "alternativa": "Mantener sistema actual + mejoras",
                "color": "rojo",
                "justif": "Ninguna alternativa genera ganancia positiva en las condiciones actuales. La inversión no se recupera."}
    if gan > 0 and gan_pesim > 0 and margen > 0.02 and roi > tasa:
        return {"veredicto": "IMPLEMENTAR",
                "alternativa": f"{ganadora_nombre}",
                "color": "verde",
                "justif": f"{ganadora_nombre} genera ganancia de ${gan/1e6:,.0f}M, ROI del {roi:.0%} (supera tasa del {tasa:.0%}), margen del {margen:.1%}, y resiste el escenario pesimista (${gan_pesim/1e6:,.0f}M). Recuperación en {pb:.1f} años."}
    if gan > 0 and roi > tasa:
        return {"veredicto": "IMPLEMENTAR POR FASES",
                "alternativa": f"{ganadora_nombre} — por fases",
                "color": "amarillo",
                "justif": f"{ganadora_nombre} es rentable (ganancia ${gan/1e6:,.0f}M, ROI {roi:.0%}), pero en pesimista la ganancia sería ${gan_pesim/1e6:,.0f}M. Implementar gradualmente."}
    if gan > 0:
        return {"veredicto": "ESPERAR",
                "alternativa": "Postergar 12-18 meses",
                "color": "amarillo",
                "justif": f"Ganancia positiva pero marginal (${gan/1e6:,.0f}M). ROI ({roi:.0%}) cercano a la tasa alternativa ({tasa:.0%}). Esperar mejores condiciones."}
    return {"veredicto": "REDISEÑAR el alcance",
            "alternativa": "Replantear el proyecto",
            "color": "amarillo",
            "justif": "Indicadores no concluyentes; reformular alcance."}


# ==============================================================================
# SIDEBAR: PANEL DE CONTROL DE PARÁMETROS
# ==============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/factory.png", width=80)
    st.title("⚙️ Panel de control")
    st.caption("Modifique las variables y observe cómo cambia la decisión en tiempo real")

    # Indicador del tour si está activo
    if st.session_state.tour_activo:
        st.info(f"🎓 **Tour en curso**\n\nPaso {st.session_state.tour_paso} de {TOTAL_PASOS}")
        if st.button("🚪 Salir del tour", key="sidebar_exit_tour", use_container_width=True):
            st.session_state.tour_activo = False
            st.session_state.tour_paso = 1
            st.rerun()
        st.markdown("---")

    # === MERCADO Y PRODUCTO ===
    with st.expander("🏭 Mercado y producto", expanded=True):
        precio_M = st.slider(
            "Precio de venta (millones COP)",
            min_value=1.5, max_value=4.0, value=2.5, step=0.05,
            help="Precio al que MecaSync vende cada módulo electromecánico"
        )
        demanda = st.slider(
            "Demanda esperada (uds/mes)",
            min_value=200, max_value=1000, value=520, step=10,
            help="Cantidad de módulos que el mercado demandará por mes"
        )

    # === MACROECONOMÍA ===
    with st.expander("🌎 Macroeconomía", expanded=True):
        trm = st.slider(
            "TRM (COP/USD)",
            min_value=3500, max_value=5500, value=4150, step=50,
            help="Tasa de cambio. Afecta CAPEX importado"
        )
        inflacion_pct = st.slider(
            "Inflación anual (%)",
            min_value=1.0, max_value=15.0, value=4.5, step=0.5,
            help="Inflación esperada en Colombia"
        )
        tasa_pct = st.slider(
            "Tasa de interés / costo de capital (%)",
            min_value=5.0, max_value=25.0, value=12.0, step=0.5,
            help="Tasa para descontar flujos futuros en la Ganancia"
        )

    # === MANO DE OBRA ===
    with st.expander("👥 Mano de obra"):
        salario_M = st.slider(
            "Salario integral mensual (M COP)",
            min_value=1.5, max_value=5.0, value=2.8, step=0.1
        )
        st.caption("Número de operarios por alternativa:")
        col1, col2, col3 = st.columns(3)
        with col1:
            op_actual = st.number_input("Actual", value=12, min_value=1, max_value=30)
        with col2:
            op_parcial = st.number_input("Parcial", value=8, min_value=1, max_value=30)
        with col3:
            op_total = st.number_input("Total", value=3, min_value=1, max_value=30)

    # === CAPEX ===
    with st.expander("💰 Inversión (CAPEX) en millones COP"):
        capex_mejoras_M = st.number_input(
            "Mejoras al sistema actual", value=65, min_value=10, max_value=500, step=5
        )
        capex_parcial_M = st.number_input(
            "Automatización parcial", value=320, min_value=100, max_value=2000, step=10
        )
        capex_total_M = st.number_input(
            "Automatización total", value=1000, min_value=300, max_value=5000, step=50
        )

    # === CAPACIDAD ===
    with st.expander("⚙️ Capacidad instalada (uds/mes)"):
        col1, col2, col3 = st.columns(3)
        with col1:
            cap_actual = st.number_input("Actual ", value=550, min_value=100, max_value=2000, step=50)
        with col2:
            cap_parcial = st.number_input("Parcial ", value=720, min_value=100, max_value=2000, step=50)
        with col3:
            cap_total = st.number_input("Total ", value=950, min_value=100, max_value=2000, step=50)

    # === COSTOS FIJOS ===
    with st.expander("📋 Costos fijos mensuales (M COP, sin mano de obra)"):
        cf_actual_M = st.number_input("CF actual ", value=180, min_value=50, max_value=500, step=10)
        cf_parcial_M = st.number_input("CF parcial ", value=235, min_value=50, max_value=500, step=10)
        cf_total_M = st.number_input("CF total ", value=345, min_value=50, max_value=500, step=10)

    # === OTROS ===
    with st.expander("🎯 Otros parámetros"):
        horizonte = st.slider("Horizonte de análisis (años)", 1, 10, 5)
        cv_materiales_M = st.slider(
            "Costo materiales unitario (M COP/u)",
            min_value=1.0, max_value=3.0, value=1.75, step=0.05
        )

    st.markdown("---")
    if st.button("🔄 Restaurar valores por defecto", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown("**Universidad Militar Nueva Granada**")
    st.caption("Ingeniería en Mecatrónica — 2026-I")
    st.markdown("**Integrantes:**")
    st.markdown("""
    - Juan Osuna
    - Santiago Rey
    - Juan Parrado
    - Germán Salazar
    """)


# Construir el diccionario de parámetros
params = {
    "precio_venta": precio_M * 1_000_000,
    "demanda": demanda,
    "trm": trm,
    "inflacion": inflacion_pct / 100,
    "tasa_interes": tasa_pct / 100,
    "salario_integral": salario_M * 1_000_000,
    "operarios_actual": op_actual,
    "operarios_parcial": op_parcial,
    "operarios_total": op_total,
    "capex_mejoras": capex_mejoras_M * 1_000_000,
    "capex_parcial": capex_parcial_M * 1_000_000,
    "capex_total": capex_total_M * 1_000_000,
    "capacidad_actual": cap_actual,
    "capacidad_parcial": cap_parcial,
    "capacidad_total": cap_total,
    "cf_actual": cf_actual_M * 1_000_000,
    "cf_parcial": cf_parcial_M * 1_000_000,
    "cf_total": cf_total_M * 1_000_000,
    "cv_materiales": cv_materiales_M * 1_000_000,
    "horizonte": horizonte,
}

# Calcular todo
res_actual = calcular_alternativa(params, "actual")
res_parcial = calcular_alternativa(params, "parcial")
res_total = calcular_alternativa(params, "total")
escenarios = calcular_escenarios(params)
pesos, puntajes, totales_matriz, detalle_matriz = calcular_matriz_multicriterio(
    res_actual, res_parcial, res_total
)
veredicto = generar_veredicto(res_actual, res_parcial, res_total, escenarios,
                               totales_matriz, params["tasa_interes"])

# Calcular también los resultados con los VALORES BASE (para mostrar deltas)
res_actual_base = calcular_alternativa(VALORES_BASE, "actual")
res_parcial_base = calcular_alternativa(VALORES_BASE, "parcial")
res_total_base = calcular_alternativa(VALORES_BASE, "total")

# Detectar cuántas variables están modificadas vs los valores base
variables_modificadas = []
labels_legibles = {
    "precio_venta": "Precio de venta",
    "demanda": "Demanda esperada",
    "trm": "TRM",
    "inflacion": "Inflación",
    "tasa_interes": "Tasa de interés",
    "salario_integral": "Salario integral",
    "operarios_actual": "Operarios (actual)",
    "operarios_parcial": "Operarios (parcial)",
    "operarios_total": "Operarios (total)",
    "capex_mejoras": "CAPEX mejoras",
    "capex_parcial": "CAPEX parcial",
    "capex_total": "CAPEX total",
    "capacidad_actual": "Capacidad (actual)",
    "capacidad_parcial": "Capacidad (parcial)",
    "capacidad_total": "Capacidad (total)",
    "cf_actual": "CF (actual)",
    "cf_parcial": "CF (parcial)",
    "cf_total": "CF (total)",
    "cv_materiales": "CV materiales",
    "horizonte": "Horizonte",
}
for key, val_base in VALORES_BASE.items():
    if abs(params[key] - val_base) > 0.0001:
        variables_modificadas.append(labels_legibles.get(key, key))


# ==============================================================================
# HEADER PRINCIPAL
# ==============================================================================

st.markdown("""
<div class="main-header">
    <h1>🏭 Simulador Económico — MecaSync S.A.S.</h1>
    <p>Análisis de viabilidad: automatización de línea de ensamble de módulos electromecánicos</p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# TABS PRINCIPALES
# ==============================================================================

tab_guia, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎓 Cómo usar",
    "📊 Dashboard",
    "💰 Costos",
    "📈 Mercado",
    "⚙️ Productividad",
    "🌎 Macro",
    "🎲 Escenarios",
    "⚖️ Matriz de decisión",
    "📚 Conceptos económicos",
])


# ==============================================================================
# TAB GUÍA: CÓMO USAR LA APLICACIÓN
# ==============================================================================

with tab_guia:
    st.header("🎓 Cómo usar este simulador")

    # Mostrar el banner del tour si está activo y este es el paso 1
    mostrar_paso_tour(1)

    st.markdown("""
    Bienvenido al simulador económico de MecaSync S.A.S. Esta aplicación les permite
    **explorar la decisión de automatización** modificando variables y viendo en tiempo real
    cómo cambian los indicadores económicos y la recomendación final.
    """)

    # === BOTÓN DE INICIAR TOUR ===
    st.markdown("---")
    col_tour_a, col_tour_b = st.columns([2, 1])
    with col_tour_a:
        st.subheader("🎓 Tour guiado por la aplicación")
        st.markdown("""
        ¿Es la primera vez que usan el simulador? Tomen el **tour guiado** que los
        llevará paso a paso por las 9 etapas del análisis económico, con explicaciones
        narradas en cada sección.
        """)
    with col_tour_b:
        st.write("")
        st.write("")
        if not st.session_state.tour_activo:
            if st.button("▶ Iniciar tour guiado", type="primary",
                        use_container_width=True, key="btn_iniciar_tour"):
                st.session_state.tour_activo = True
                st.session_state.tour_paso = 1
                st.rerun()
        else:
            st.success(f"✅ Tour en curso — Paso {st.session_state.tour_paso} de {TOTAL_PASOS}")
            if st.button("🚪 Salir del tour", use_container_width=True, key="btn_salir_tour_main"):
                st.session_state.tour_activo = False
                st.session_state.tour_paso = 1
                st.rerun()

    st.markdown("---")

    # --- PASOS RÁPIDOS ---
    st.subheader("⚡ Empezar en 3 pasos")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ##### 1️⃣ Explora
        Revisa el tab **📊 Dashboard** para ver el veredicto y los indicadores actuales con los **valores base** del modelo.
        """)
    with col2:
        st.markdown("""
        ##### 2️⃣ Modifica
        En el **panel izquierdo (sidebar)**, mueve los sliders para simular distintas condiciones del mercado o de la inversión.
        """)
    with col3:
        st.markdown("""
        ##### 3️⃣ Compara
        Observa cómo cambian los indicadores y, eventualmente, el veredicto cuando las condiciones se vuelven más adversas.
        """)

    st.markdown("---")

    # --- DEMOS RECOMENDADOS ---
    st.subheader("🎬 Casos de estudio interactivos")
    st.caption("Situaciones específicas que ilustran el comportamiento del modelo ante distintas condiciones económicas. Sigan las instrucciones para reproducirlas.")

    st.markdown("##### 🌍 Casos macroeconómicos y de mercado")

    # Demo 1
    with st.expander("**Demo 1: Crisis cambiaria — TRM se dispara** 💱", expanded=False):
        st.markdown("""
        **Situación:** El dólar sube fuerte por una crisis financiera global.

        **Qué hacer:**
        1. En el sidebar, abrir la sección **🌎 Macroeconomía**
        2. Subir el slider **TRM** de `4.150` a `5.500` COP/USD

        **Qué observar:**
        - El **CAPEX ajustado** de la auto. total sube (tab 🌎 Macro)
        - El **Ganancia de la auto. total** se vuelve aún más negativo
        - El veredicto sigue siendo "IMPLEMENTAR POR FASES" pero ahora con margen menor

        **Interpretación económica:**
        La automatización total es la alternativa más expuesta al riesgo cambiario por su alto componente importado. En un escenario de devaluación, su CAPEX real puede superar lo presupuestado en más de $200 millones.
        """)

    # Demo 2
    with st.expander("**Demo 2: Crisis de demanda — el mercado se cae** 📉", expanded=False):
        st.markdown("""
        **Situación:** Recesión económica, la demanda industrial cae.

        **Qué hacer:**
        1. En el sidebar, abrir **🏭 Mercado y producto**
        2. Bajar el slider **Demanda esperada** de `520` a `300` uds/mes

        **Qué observar:**
        - **Todas las Ganancias se vuelven negativos** (ver tab 📊 Dashboard)
        - El **veredicto cambia a "DESCARTAR"** (color rojo)
        - El simulador recomienda no automatizar y mantener el sistema actual

        **Interpretación económica:**
        En un escenario de recesión, ninguna alternativa de automatización es viable. Esto demuestra la importancia del análisis de escenarios y el riesgo económico.
        """)

    # Demo 3
    with st.expander("**Demo 3: Política monetaria contractiva — sube la tasa** 🏦", expanded=False):
        st.markdown("""
        **Situación:** El Banco de la República sube la tasa de interés para frenar la inflación.

        **Qué hacer:**
        1. En el sidebar, **🌎 Macroeconomía**
        2. Subir **Tasa de interés** de `12%` a `20%`

        **Qué observar:**
        - El **Ganancia de la auto. parcial** cae significativamente
        - El **Ganancia del sistema actual** también baja (los flujos futuros valen menos hoy)
        - Posible cambio de veredicto a "ESPERAR"

        **Interpretación económica:**
        Una tasa de interés más alta penaliza más fuertemente las alternativas con CAPEX elevado. La política monetaria del Banco de la República impacta directamente la viabilidad de proyectos de inversión.
        """)

    # Demo 4
    with st.expander("**Demo 4: Boom económico — todas las condiciones mejoran** 📈", expanded=False):
        st.markdown("""
        **Situación:** Crecimiento económico, demanda en alza, dólar estable, tasas bajas.

        **Qué hacer:**
        1. **🏭 Mercado y producto:** subir demanda a `900` uds/mes
        2. **🌎 Macroeconomía:** bajar tasa de interés a `8%`
        3. **🌎 Macroeconomía:** bajar TRM a `3.800`

        **Qué observar:**
        - El **veredicto puede cambiar a "IMPLEMENTAR"** (verde)
        - Los **Ganancia de auto. parcial y total** suben fuerte
        - La auto. total empieza a competir con la parcial

        **Interpretación económica:**
        En un escenario expansivo, las alternativas con mayor capacidad instalada se vuelven rentables. La decisión depende fundamentalmente del ciclo económico esperado.
        """)

    # Demo 5
    with st.expander("**Demo 5: Demanda alta + crisis cambiaria simultáneas** ⚡", expanded=False):
        st.markdown("""
        **Situación:** Mercado en crecimiento pero con presión cambiaria (típico de Colombia).

        **Qué hacer:**
        1. Subir **demanda** a `750`
        2. Subir **TRM** a `5.000`
        3. Subir **inflación** a `8%`

        **Qué observar:**
        - Comportamiento mixto: ingresos crecen pero costos también
        - La auto. parcial muestra resiliencia por bajo CAPEX importado
        - Diferencia entre alternativas se acentúa

        **Interpretación económica:**
        En contextos de inflación con demanda al alza, las alternativas con menor exposición al dólar son más robustas. La auto. parcial gana por su balance riesgo-rentabilidad.
        """)

    st.markdown("##### 💼 Casos operativos y de gestión interna")

    # Demo 6 - PROVEEDORES
    with st.expander("**Demo 6: Negociación exitosa con proveedores** 🤝", expanded=False):
        st.markdown("""
        **Situación:** El área de compras logra renegociar contratos de materiales con un proveedor estratégico, bajando el costo unitario un 15%.

        **Qué hacer:**
        1. En el sidebar, abrir **🎯 Otros parámetros**
        2. Bajar el slider **Costo materiales unitario** de `1.75` a `1.50` M COP/u

        **Qué observar:**
        - **Margen unitario aumenta** en todas las alternativas
        - **Ganancia de la auto. parcial** crece significativamente
        - **Punto de equilibrio baja** (necesitas menos unidades para no perder)

        **Interpretación económica:**
        La negociación con proveedores impacta directamente el costo variable unitario (CVu) y por tanto el costo marginal (CMg). Una mejora en el costo de materiales tiene efecto multiplicador porque se replica en cada unidad vendida durante todo el horizonte del proyecto.
        """)

    # Demo 7 - SALARIOS
    with st.expander("**Demo 7: Aumento salarial por presión sindical** 👥", expanded=False):
        st.markdown("""
        **Situación:** Acuerdo con el sindicato eleva el salario integral mensual en un 25%.

        **Qué hacer:**
        1. En el sidebar, abrir **👥 Mano de obra**
        2. Subir **Salario integral mensual** de `2.8` a `3.5` M COP

        **Qué observar:**
        - **Sistema actual** (12 operarios) es el MÁS afectado
        - **Auto. total** (3 operarios) es el MENOS afectado
        - Brecha de utilidad entre alternativas se amplía a favor de la automatización
        - Posible mejora del veredicto a favor de auto. parcial o total

        **Interpretación económica:**
        El costo laboral es un costo fijo. Cuando sube, las alternativas con menor intensidad de mano de obra ganan ventaja relativa. Este es el argumento clásico para justificar la inversión en automatización: protegerse de la inflación salarial estructural.
        """)

    # Demo 8 - SOBRECOSTOS DE INVERSIÓN
    with st.expander("**Demo 8: Sobrecostos en la inversión inicial** 💸", expanded=False):
        st.markdown("""
        **Situación:** Los proveedores de tecnología cotizan más caro de lo esperado. El CAPEX de la automatización total se incrementa 30%.

        **Qué hacer:**
        1. En el sidebar, abrir **💰 Inversión (CAPEX)**
        2. Subir **Automatización total** de `1000` a `1300` M COP

        **Qué observar:**
        - **Ganancia de auto. total** cae aún más en territorio negativo
        - **Payback de auto. total** empeora
        - El **gap entre auto. parcial y total** se amplía a favor de la parcial

        **Interpretación económica:**
        Los sobrecostos en proyectos de automatización son comunes en la realidad (típicamente +15% a +40% sobre el presupuesto inicial). El simulador permite estresar este parámetro para validar la robustez de la decisión.
        """)

    # Demo 9 - GUERRA DE PRECIOS
    with st.expander("**Demo 9: Guerra de precios — la competencia presiona** 💥", expanded=False):
        st.markdown("""
        **Situación:** Entra un nuevo competidor agresivo al mercado y MecaSync debe bajar el precio un 12% para defender participación.

        **Qué hacer:**
        1. En el sidebar, **🏭 Mercado y producto**
        2. Bajar **Precio de venta** de `2.5` a `2.20` M COP

        **Qué observar:**
        - **Margen unitario se reduce** en todas las alternativas
        - **Punto de equilibrio sube** drásticamente
        - **Ganancia** de todas las opciones se deteriora
        - El sistema actual con CMe alto puede entrar en pérdidas

        **Interpretación económica:**
        En mercados con demanda elástica (como el nuestro, ε = -1.5), bajar precios atrae más demanda. Pero el efecto sobre la utilidad depende de cuánto se contraiga el margen. Aquí se aprecia el delicado balance entre precio, volumen y margen que la microeconomía estudia.
        """)

    # Demo 10 - PRODUCTO PREMIUM
    with st.expander("**Demo 10: Estrategia premium — diferenciación del producto** ⭐", expanded=False):
        st.markdown("""
        **Situación:** MecaSync invierte en certificaciones de calidad y reposiciona su producto como premium. Logra un precio 20% mayor (aunque la demanda baja un poco por elasticidad).

        **Qué hacer:**
        1. **🏭 Mercado y producto:** subir **Precio** de `2.5` a `3.0` M COP
        2. **🏭 Mercado y producto:** bajar **Demanda** de `520` a `420` uds/mes

        **Qué observar:**
        - **Ingresos totales pueden subir o bajar** según la elasticidad
        - **Margen unitario crece** significativamente
        - La estrategia depende de si la pérdida de volumen compensa la ganancia de margen

        **Interpretación económica:**
        Este es el clásico análisis de elasticidad en acción: con demanda elástica (|ε|>1), subir precios reduce los ingresos totales. Pero si el margen aumenta lo suficiente, la utilidad puede crecer. Es una decisión estratégica de posicionamiento.
        """)

    # Demo 11 - REESTRUCTURACIÓN DE PLANTILLA
    with st.expander("**Demo 11: Reestructuración de plantilla operativa** 🔄", expanded=False):
        st.markdown("""
        **Situación:** Aún con el sistema actual, MecaSync optimiza turnos y reduce 2 operarios. En automatización parcial, mantiene la misma estructura.

        **Qué hacer:**
        1. En el sidebar, **👥 Mano de obra**
        2. Bajar **Operarios actual** de `12` a `10`

        **Qué observar:**
        - **Ganancia del sistema actual** mejora
        - El gap con auto. parcial se reduce ligeramente
        - Demuestra que **siempre hay oportunidades de mejora sin grandes inversiones**

        **Interpretación económica:**
        Antes de invertir en automatización, hay que evaluar si la línea actual está operando eficientemente. La reingeniería de procesos puede generar mejoras sustanciales con CAPEX casi cero. Este es el concepto de "low-hanging fruit" en gestión de operaciones.
        """)

    # Demo 12 - REDUCCIÓN DE COSTOS FIJOS
    with st.expander("**Demo 12: Programa de eficiencia operativa** 📉", expanded=False):
        st.markdown("""
        **Situación:** MecaSync implementa un programa Lean que reduce gastos generales (arriendo renegociado, energía, mantenimiento preventivo) en un 15%.

        **Qué hacer:**
        1. En el sidebar, abrir **📋 Costos fijos mensuales**
        2. Bajar **CF actual** de `180` a `155` M COP
        3. Bajar **CF parcial** de `235` a `200` M COP
        4. Bajar **CF total** de `345` a `295` M COP

        **Qué observar:**
        - **Todas las Ganancias mejoran** simultáneamente
        - **Auto. total** se beneficia más en términos absolutos (tiene los CF más altos)
        - El **punto de equilibrio baja** para todas las alternativas

        **Interpretación económica:**
        Los costos fijos son particularmente importantes porque se pagan independientemente de las ventas. Una reducción estructural en CF tiene efecto perpetuo y palanca operativa: cada peso ahorrado se multiplica por el horizonte de análisis al calcular la Ganancia.
        """)

    # Demo 13 - SOBRECOSTOS DE MANTENIMIENTO
    with st.expander("**Demo 13: Sobrecostos de mantenimiento en automatización** 🔧", expanded=False):
        st.markdown("""
        **Situación:** La automatización total resulta más costosa de mantener de lo previsto: contratos de servicio técnico especializado, repuestos importados, paradas no planeadas.

        **Qué hacer:**
        1. En el sidebar, **📋 Costos fijos mensuales**
        2. Subir **CF total** de `345` a `420` M COP

        **Qué observar:**
        - **Ganancia de auto. total** cae aún más
        - Refuerza que la decisión de descartar auto. total es correcta
        - La auto. parcial se consolida como ganadora

        **Interpretación económica:**
        Los costos ocultos de la tecnología (TCO - Total Cost of Ownership) suelen subestimarse en proyectos de automatización. Es importante hacer análisis de sensibilidad con incrementos de CF para validar la robustez de la decisión ante imprevistos operativos.
        """)

    st.markdown("##### 🎯 Casos estratégicos y de planeación")

    # Demo 14 - HORIZONTE DE LARGO PLAZO
    with st.expander("**Demo 14: Visión de largo plazo — extender el horizonte** 🔭", expanded=False):
        st.markdown("""
        **Situación:** MecaSync decide evaluar el proyecto con horizonte de 10 años en lugar de 5, asumiendo que la línea seguirá operando.

        **Qué hacer:**
        1. En el sidebar, **🎯 Otros parámetros**
        2. Subir **Horizonte de análisis** de `5` a `10` años

        **Qué observar:**
        - **Ganancia de TODAS las alternativas sube** (más años de flujos positivos)
        - **Auto. total puede acercarse a Ganancia positiva**
        - La inversión inicial se diluye entre más años de retorno

        **Interpretación económica:**
        El horizonte de análisis es una decisión estratégica clave. Tecnologías con CAPEX alto necesitan horizontes largos para amortizarse. El sesgo de "cortoplacismo" puede hacer rechazar proyectos que sí generan valor en el largo plazo. Sin embargo, también hay mayor incertidumbre en pronósticos lejanos.
        """)

    # Demo 15 - ESTRATEGIA MIXTA
    with st.expander("**Demo 15: Estrategia integral — múltiples palancas a la vez** 🎯", expanded=False):
        st.markdown("""
        **Situación:** El directorio decide ejecutar una estrategia completa: renegociar proveedores, optimizar costos fijos y reposicionar el producto, todo en paralelo.

        **Qué hacer:**
        1. **🎯 Otros parámetros:** bajar **CV materiales** a `1.55` M COP
        2. **📋 Costos fijos:** bajar **CF parcial** a `200` M COP
        3. **🏭 Mercado:** subir **Precio** a `2.75` M COP
        4. **🏭 Mercado:** bajar **Demanda** a `480` (por elasticidad del precio mayor)

        **Qué observar:**
        - Múltiples efectos combinados sobre la Ganancia
        - La auto. parcial mejora sustancialmente su Ganancia
        - Demuestra la utilidad de simular **escenarios estratégicos integrales**

        **Interpretación económica:**
        En la práctica, las decisiones empresariales rara vez modifican una sola variable. Este caso muestra el poder del simulador como herramienta de planeación: permite evaluar el efecto combinado de múltiples iniciativas estratégicas antes de comprometer recursos.
        """)

    st.markdown("---")

    # --- INTERPRETAR EL VEREDICTO ---
    st.subheader("🎯 Cómo entender el veredicto")
    st.markdown("""
    El simulador emite 1 de **5 posibles veredictos** según las condiciones:
    """)

    veredictos_info = [
        ("✅ IMPLEMENTAR", "verde", "Ganancia positiva, buen margen, ROI superior a la tasa y resiste el pesimista."),
        ("⚠️ IMPLEMENTAR POR FASES", "amarillo", "Ganancia positiva con ROI atractivo, pero no resiste el pesimista. Avanzar por etapas."),
        ("🟡 ESPERAR", "amarillo", "Ganancia positiva pero marginal. ROI cercano a la tasa alternativa. Postergar."),
        ("🔴 DESCARTAR", "rojo", "Ninguna alternativa genera ganancia positiva. Mantener sistema actual."),
        ("🟠 REDISEÑAR", "amarillo", "Indicadores no concluyentes; revisar el alcance del proyecto."),
    ]

    for vname, vcolor, vdesc in veredictos_info:
        st.markdown(f"""
        <div class="concepto-card">
            <h4>{vname}</h4>
            <p style="margin:0;">{vdesc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- EXPLICACIÓN DEL POR QUÉ A VECES NO CAMBIA ---
    st.subheader("❓ ¿Por qué a veces cambio una variable y el veredicto no cambia?")
    st.info("""
    **Es comportamiento correcto del simulador**, no un error.

    El veredicto solo cambia cuando los indicadores **cruzan ciertos umbrales**:
    - Ganancia pasa de positiva a negativa (o viceversa)
    - ROI supera o no la tasa de interés
    - El escenario pesimista deja de ser viable

    **Pero los NÚMEROS sí están cambiando todo el tiempo.** Por ejemplo, si subes inflación
    del 4.5% al 6%, verás en el Dashboard que la Ganancia cambia (los resultados del proyecto se ven afectados
    en pesos nominales, pero también se descuentan más fuerte). El veredicto puede mantenerse
    en "IMPLEMENTAR POR FASES" porque las condiciones siguen dentro del mismo rango lógico.

    **Para forzar un cambio de veredicto, prueba los demos 2, 3 o 4** arriba.
    """)

    st.markdown("---")

    # --- TABS EXPLICADOS ---
    st.subheader("📑 Qué hay en cada tab")

    tabs_info = [
        ("📊 Dashboard", "Veredicto principal + métricas clave (Ganancia, ROI, Payback, ROI) por alternativa, con comparación a valores base."),
        ("💰 Costos", "Análisis detallado de costos fijos, variables, costo medio y costo marginal. Incluye gráficas de CT vs IT y curvas de CMe."),
        ("📈 Mercado", "Curvas de oferta y demanda, cálculo de elasticidad-precio, interpretación económica."),
        ("⚙️ Productividad", "El trade-off central del proyecto: eficiencia técnica vs eficiencia económica."),
        ("🌎 Macro", "Sensibilidad del CAPEX a la TRM, explicación de cada variable macroeconómica."),
        ("🎲 Escenarios", "Análisis de riesgo con escenarios pesimista, probable y optimista."),
        ("⚖️ Matriz de decisión", "Matriz multicriterio ponderada con 7 criterios para integrar la decisión."),
        ("📚 Conceptos económicos", "Glosario rápido de los 17+ conceptos económicos aplicados en el modelo."),
    ]

    cols = st.columns(2)
    for i, (tab_name, tab_desc) in enumerate(tabs_info):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="concepto-card">
                <h4>{tab_name}</h4>
                <p style="margin:0; font-size: 0.9rem;">{tab_desc}</p>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# TAB 1: DASHBOARD
# ==============================================================================

with tab1:
    st.header("📊 Resumen ejecutivo")

    # Banner del tour si corresponde
    mostrar_paso_tour(2)

    # === INDICADOR DE CONFIGURACIÓN ===
    if variables_modificadas:
        n_mod = len(variables_modificadas)
        with st.container():
            st.warning(f"""
            🔧 **Configuración modificada** — {n_mod} variable{'s' if n_mod > 1 else ''} fuera de valor base:
            **{', '.join(variables_modificadas[:5])}**{' ...' if n_mod > 5 else ''}

            Los números abajo muestran el **cambio respecto al escenario base** entre paréntesis.
            """)
    else:
        st.info("✅ **Escenario base** — Todas las variables están en sus valores originales. Modifique los sliders del sidebar para explorar.")

    # === VEREDICTO ===
    color_class = f"veredicto-{veredicto['color']}"
    st.markdown(f"""
    <div class="{color_class} veredicto-card">
        <h2>🎯 {veredicto['veredicto']}</h2>
        <p style="font-size: 1.1rem; margin-top: 0.5rem;">{veredicto['alternativa']}</p>
        <p style="font-size: 0.95rem; margin-top: 0.8rem;">{veredicto['justif']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # === MÉTRICAS PRINCIPALES POR ALTERNATIVA ===
    st.subheader("Indicadores financieros por alternativa")
    if variables_modificadas:
        st.caption("📌 El **delta (Δ)** muestra el cambio vs el escenario base original")

    def fmt_delta_van(actual_van, base_van):
        """Formatea el delta dla Ganancia respecto al base."""
        if not variables_modificadas:
            return None
        diff = (actual_van - base_van) / 1e6
        if abs(diff) < 1:
            return None
        signo = "+" if diff > 0 else ""
        return f"{signo}${diff:,.0f}M vs base"

    def fmt_delta_pct(actual, base, fmt="{:.1%}"):
        """Formatea delta de porcentajes/ratios."""
        if not variables_modificadas:
            return None
        diff = actual - base
        if abs(diff) < 0.001:
            return None
        signo = "+" if diff > 0 else ""
        return f"{signo}{fmt.format(diff)} vs base"

    def fmt_delta_money(actual, base):
        """Formatea delta de cantidades de dinero (mensuales)."""
        if not variables_modificadas:
            return None
        diff = (actual - base) / 1e6
        if abs(diff) < 0.1:
            return None
        signo = "+" if diff > 0 else ""
        return f"{signo}${diff:,.1f}M vs base"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### 🔵 Sistema actual + mejoras")
        delta_van = fmt_delta_van(res_actual['ganancia_proyecto'], res_actual_base['ganancia_proyecto'])
        st.metric("Ganancia", f"${res_actual['ganancia_proyecto']/1e6:,.0f}M",
                 delta=delta_van if delta_van else ('✓ Positiva' if res_actual['ganancia_proyecto'] > 0 else '✗ Negativa'),
                 delta_color="normal" if delta_van else ("normal" if res_actual['ganancia_proyecto'] > 0 else "inverse"))
        st.metric("ROI anual", f"{res_actual['ROI']:.0%}",
                 delta=fmt_delta_pct(res_actual['ROI'], res_actual_base['ROI']))
        payback_str = "∞" if res_actual['payback'] == float('inf') else f"{res_actual['payback']:.2f} años"
        st.metric("Payback", payback_str)
        st.metric("Utilidad mensual", f"${res_actual['utilidad_mensual']/1e6:,.1f}M",
                 delta=fmt_delta_money(res_actual['utilidad_mensual'], res_actual_base['utilidad_mensual']))

    with col2:
        st.markdown("##### 🟢 Automatización parcial")
        delta_van = fmt_delta_van(res_parcial['ganancia_proyecto'], res_parcial_base['ganancia_proyecto'])
        st.metric("Ganancia", f"${res_parcial['ganancia_proyecto']/1e6:,.0f}M",
                 delta=delta_van if delta_van else ('✓ Positiva' if res_parcial['ganancia_proyecto'] > 0 else '✗ Negativa'),
                 delta_color="normal" if delta_van else ("normal" if res_parcial['ganancia_proyecto'] > 0 else "inverse"))
        st.metric("ROI anual", f"{res_parcial['ROI']:.0%}",
                 delta=fmt_delta_pct(res_parcial['ROI'], res_parcial_base['ROI']))
        payback_str = "∞" if res_parcial['payback'] == float('inf') else f"{res_parcial['payback']:.2f} años"
        st.metric("Payback", payback_str)
        st.metric("Utilidad mensual", f"${res_parcial['utilidad_mensual']/1e6:,.1f}M",
                 delta=fmt_delta_money(res_parcial['utilidad_mensual'], res_parcial_base['utilidad_mensual']))

    with col3:
        st.markdown("##### 🔴 Automatización total")
        delta_van = fmt_delta_van(res_total['ganancia_proyecto'], res_total_base['ganancia_proyecto'])
        st.metric("Ganancia", f"${res_total['ganancia_proyecto']/1e6:,.0f}M",
                 delta=delta_van if delta_van else ('✓ Positiva' if res_total['ganancia_proyecto'] > 0 else '✗ Negativa'),
                 delta_color="normal" if delta_van else ("normal" if res_total['ganancia_proyecto'] > 0 else "inverse"))
        st.metric("ROI anual", f"{res_total['ROI']:.0%}",
                 delta=fmt_delta_pct(res_total['ROI'], res_total_base['ROI']))
        payback_str = "∞" if res_total['payback'] == float('inf') else f"{res_total['payback']:.2f} años"
        st.metric("Payback", payback_str)
        st.metric("Utilidad mensual", f"${res_total['utilidad_mensual']/1e6:,.1f}M",
                 delta=fmt_delta_money(res_total['utilidad_mensual'], res_total_base['utilidad_mensual']))

    st.markdown("---")

    # === GRÁFICA COMPARATIVA VAN ===
    st.subheader("Comparación de la Ganancia del proyecto")

    fig = go.Figure()
    nombres = ["Sistema actual", "Auto. parcial", "Auto. total"]
    vans = [res_actual["ganancia_proyecto"]/1e6, res_parcial["ganancia_proyecto"]/1e6, res_total["ganancia_proyecto"]/1e6]
    colores = [COL_ACTUAL, COL_PARCIAL, COL_TOTAL]

    fig.add_trace(go.Bar(
        x=nombres, y=vans, marker_color=colores,
        text=[f"${v:,.0f}M" for v in vans], textposition="outside",
        textfont=dict(size=14, color="black"),
    ))
    fig.add_hline(y=0, line_color="black", line_width=1)
    fig.update_layout(
        yaxis_title="Ganancia (millones COP)",
        height=400, showlegend=False,
        plot_bgcolor="white",
    )
    fig.update_yaxes(gridcolor="lightgray")
    st.plotly_chart(fig, use_container_width=True)


# ==============================================================================
# TAB 2: COSTOS
# ==============================================================================

with tab2:
    st.header("💰 Análisis de costos")

    # Banner del tour si corresponde
    mostrar_paso_tour(3)

    st.markdown("""
    Conceptos aplicados: **costos fijos (CF)**, **costos variables (CV)**, **costo total (CT)**,
    **costo medio (CMe)**, **costo marginal (CMg)**, **punto de equilibrio**.
    """)

    # Tabla comparativa
    st.subheader("Tabla comparativa de costos")
    df_costos = pd.DataFrame({
        "Concepto": [
            "Producción mensual (uds)",
            "Costo fijo mensual",
            "Costo variable total",
            "Costo variable unitario (CVu)",
            "Costo total mensual",
            "Costo medio (CMe)",
            "Costo marginal (CMg)",
            "Punto de equilibrio (uds)",
            "Ingreso total",
            "Utilidad mensual",
        ],
        "Sistema actual": [
            f"{res_actual['Q']:,.0f}",
            f"${res_actual['CF']/1e6:,.0f}M",
            f"${res_actual['CV']/1e6:,.0f}M",
            f"${res_actual['CVu']/1e6:.2f}M",
            f"${res_actual['CT']/1e6:,.0f}M",
            f"${res_actual['CMe']/1e6:.3f}M",
            f"${res_actual['CMg']/1e6:.3f}M",
            f"{res_actual['Q_equilibrio']:,.0f}",
            f"${res_actual['IT']/1e6:,.0f}M",
            f"${res_actual['utilidad_mensual']/1e6:,.1f}M",
        ],
        "Auto. parcial": [
            f"{res_parcial['Q']:,.0f}",
            f"${res_parcial['CF']/1e6:,.0f}M",
            f"${res_parcial['CV']/1e6:,.0f}M",
            f"${res_parcial['CVu']/1e6:.2f}M",
            f"${res_parcial['CT']/1e6:,.0f}M",
            f"${res_parcial['CMe']/1e6:.3f}M",
            f"${res_parcial['CMg']/1e6:.3f}M",
            f"{res_parcial['Q_equilibrio']:,.0f}",
            f"${res_parcial['IT']/1e6:,.0f}M",
            f"${res_parcial['utilidad_mensual']/1e6:,.1f}M",
        ],
        "Auto. total": [
            f"{res_total['Q']:,.0f}",
            f"${res_total['CF']/1e6:,.0f}M",
            f"${res_total['CV']/1e6:,.0f}M",
            f"${res_total['CVu']/1e6:.2f}M",
            f"${res_total['CT']/1e6:,.0f}M",
            f"${res_total['CMe']/1e6:.3f}M",
            f"${res_total['CMg']/1e6:.3f}M",
            f"{res_total['Q_equilibrio']:,.0f}",
            f"${res_total['IT']/1e6:,.0f}M",
            f"${res_total['utilidad_mensual']/1e6:,.1f}M",
        ],
    })
    st.dataframe(df_costos, use_container_width=True, hide_index=True)

    # Gráficas
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Costo Total vs Ingreso Total")
        Q_range = np.arange(50, 1001, 10)
        fig1 = go.Figure()

        for nombre, res, color in [
            ("Sistema actual", res_actual, COL_ACTUAL),
            ("Auto. parcial", res_parcial, COL_PARCIAL),
            ("Auto. total", res_total, COL_TOTAL),
        ]:
            CT_curve = (res["CF"] + res["CVu"] * Q_range) / 1e6
            fig1.add_trace(go.Scatter(
                x=Q_range, y=CT_curve, mode="lines",
                name=f"CT — {nombre}", line=dict(color=color, width=2.5)
            ))

        IT_curve = params["precio_venta"] * Q_range / 1e6
        fig1.add_trace(go.Scatter(
            x=Q_range, y=IT_curve, mode="lines",
            name="Ingreso Total", line=dict(color="black", width=2, dash="dash")
        ))

        fig1.update_layout(
            xaxis_title="Cantidad producida (uds/mes)",
            yaxis_title="Millones COP",
            height=400, plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig1.update_xaxes(gridcolor="lightgray")
        fig1.update_yaxes(gridcolor="lightgray")
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.subheader("Costo Medio (CMe) por alternativa")
        Q_range2 = np.arange(100, 1001, 10)
        fig2 = go.Figure()

        for nombre, res, color in [
            ("Sistema actual", res_actual, COL_ACTUAL),
            ("Auto. parcial", res_parcial, COL_PARCIAL),
            ("Auto. total", res_total, COL_TOTAL),
        ]:
            CMe_curve = (res["CF"] + res["CVu"] * Q_range2) / Q_range2 / 1e3
            fig2.add_trace(go.Scatter(
                x=Q_range2, y=CMe_curve, mode="lines",
                name=nombre, line=dict(color=color, width=2.5)
            ))

        fig2.update_layout(
            xaxis_title="Cantidad producida (uds/mes)",
            yaxis_title="Costo medio (miles COP/und)",
            height=400, plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig2.update_xaxes(gridcolor="lightgray")
        fig2.update_yaxes(gridcolor="lightgray")
        st.plotly_chart(fig2, use_container_width=True)

    st.info("""
    **💡 Interpretación:** El sistema actual tiene CF bajo pero CVu alto por reproceso elevado.
    La automatización total reduce CVu drásticamente pero eleva CF por mantenimiento y costo de capital.
    La automatización parcial ofrece un balance entre ambos extremos.
    """)


# ==============================================================================
# TAB 3: MERCADO
# ==============================================================================

with tab3:
    st.header("📈 Mercado: oferta, demanda y elasticidad")

    # Banner del tour si corresponde
    mostrar_paso_tour(4)

    # Cálculo de elasticidad
    a_dem = 1300
    b_dem = 0.000312
    P_actual = params["precio_venta"]
    Q_demandada = a_dem - b_dem * P_actual
    elasticidad = -b_dem * P_actual / Q_demandada if Q_demandada > 0 else 0

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Cantidad demandada", f"{Q_demandada:.0f} uds/mes")
    with col_b:
        st.metric("Elasticidad precio (ε)", f"{elasticidad:.3f}")
    with col_c:
        if abs(elasticidad) > 1:
            tipo_demanda = "🔴 ELÁSTICA"
        elif abs(elasticidad) < 1:
            tipo_demanda = "🔵 INELÁSTICA"
        else:
            tipo_demanda = "⚪ UNITARIA"
        st.metric("Tipo de demanda", tipo_demanda)

    st.markdown(f"""
    **Función de demanda asumida:**
    $$Q_d = {a_dem} - {b_dem:.6f} \\times P$$

    **Interpretación de la elasticidad ε = {elasticidad:.3f}:**
    """)

    if abs(elasticidad) > 1:
        st.warning("""
        ⚠️ **DEMANDA ELÁSTICA** (|ε| > 1): Pequeños cambios en el precio generan
        grandes cambios en la cantidad demandada. **Cuidado al subir precios.**
        """)
    elif abs(elasticidad) < 1:
        st.info("""
        ℹ️ **DEMANDA INELÁSTICA** (|ε| < 1): La cantidad demandada responde poco al precio.
        Puede haber margen para subir precios sin perder mucho volumen.
        """)

    # Gráfica oferta-demanda
    st.subheader("Curvas de oferta y demanda")

    Q_d_range = np.arange(0, 1200, 10)
    P_d = (a_dem - Q_d_range) / b_dem / 1e6

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=Q_d_range, y=P_d, mode="lines", name="Demanda",
        line=dict(color="blue", width=3),
    ))

    for nombre, res, color in [
        ("Auto. total", res_total, COL_TOTAL),
        ("Auto. parcial", res_parcial, COL_PARCIAL),
        ("Sistema actual", res_actual, COL_ACTUAL),
    ]:
        fig.add_trace(go.Scatter(
            x=[0, 1200], y=[res["CMg"]/1e6, res["CMg"]/1e6], mode="lines",
            name=f"Oferta — {nombre} (CMg=${res['CMg']/1e6:.2f}M)",
            line=dict(color=color, width=1.5, dash="dash"),
        ))

    fig.add_trace(go.Scatter(
        x=[Q_demandada], y=[P_actual/1e6], mode="markers",
        name=f"Precio actual: ${P_actual/1e6:.2f}M",
        marker=dict(color="black", size=12, symbol="circle"),
    ))

    fig.update_layout(
        xaxis_title="Cantidad (uds/mes)",
        yaxis_title="Precio (millones COP/und)",
        yaxis=dict(range=[0, 4.5]),
        xaxis=dict(range=[0, 1200]),
        height=500, plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="lightgray")
    fig.update_yaxes(gridcolor="lightgray")
    st.plotly_chart(fig, use_container_width=True)

    # Capacidades por alternativa
    st.subheader("Oferta por alternativa")
    df_oferta = pd.DataFrame({
        "Alternativa": ["Sistema actual", "Auto. parcial", "Auto. total"],
        "Capacidad (uds/mes)": [
            f"{res_actual['capacidad']:,.0f}",
            f"{res_parcial['capacidad']:,.0f}",
            f"{res_total['capacidad']:,.0f}",
        ],
        "CMe (COP/und)": [
            f"${res_actual['CMe']:,.0f}",
            f"${res_parcial['CMe']:,.0f}",
            f"${res_total['CMe']:,.0f}",
        ],
        "CMg (COP/und)": [
            f"${res_actual['CMg']:,.0f}",
            f"${res_parcial['CMg']:,.0f}",
            f"${res_total['CMg']:,.0f}",
        ],
    })
    st.dataframe(df_oferta, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 4: PRODUCTIVIDAD
# ==============================================================================

with tab4:
    st.header("⚙️ Productividad y eficiencia")

    # Banner del tour si corresponde
    mostrar_paso_tour(5)

    st.markdown("""
    **Definiciones:**
    - **Productividad** = unidades producidas / horas-hombre
    - **Eficiencia técnica** = producción real / capacidad instalada
    - **Eficiencia económica** = utilidad / costo total
    """)

    # Métricas comparativas
    col1, col2, col3 = st.columns(3)
    nombres = ["Sistema actual", "Auto. parcial", "Auto. total"]
    resultados = [res_actual, res_parcial, res_total]
    iconos = ["🔵", "🟢", "🔴"]

    for col, nombre, res, icono in zip([col1, col2, col3], nombres, resultados, iconos):
        with col:
            st.markdown(f"##### {icono} {nombre}")
            st.metric("Productividad", f"{res['productividad']:.3f} uds/h-h")
            st.metric("Eficiencia técnica", f"{res['eficiencia_tecnica']:.1%}")
            st.metric("Eficiencia económica", f"{res['eficiencia_economica']:.2%}")
            st.caption(f"Operarios: {res['operarios']} | Capacidad: {res['capacidad']:,.0f} uds")

    st.markdown("---")

    # Gráficas comparativas (3 sub-gráficas)
    fig = make_subplots(rows=1, cols=3, subplot_titles=(
        "Productividad (uds/h-h)",
        "Eficiencia técnica",
        "Eficiencia económica"
    ))

    nombres_corto = ["Actual", "Parcial", "Total"]
    colores = [COL_ACTUAL, COL_PARCIAL, COL_TOTAL]

    productividad = [r["productividad"] for r in resultados]
    fig.add_trace(go.Bar(x=nombres_corto, y=productividad,
                         marker_color=colores,
                         text=[f"{v:.3f}" for v in productividad],
                         textposition="outside", showlegend=False),
                  row=1, col=1)

    ef_tec = [r["eficiencia_tecnica"] for r in resultados]
    fig.add_trace(go.Bar(x=nombres_corto, y=ef_tec,
                         marker_color=colores,
                         text=[f"{v:.1%}" for v in ef_tec],
                         textposition="outside", showlegend=False),
                  row=1, col=2)

    ef_eco = [r["eficiencia_economica"] for r in resultados]
    fig.add_trace(go.Bar(x=nombres_corto, y=ef_eco,
                         marker_color=colores,
                         text=[f"{v:.2%}" for v in ef_eco],
                         textposition="outside", showlegend=False),
                  row=1, col=3)

    fig.update_layout(height=400, plot_bgcolor="white")
    fig.update_xaxes(gridcolor="lightgray")
    fig.update_yaxes(gridcolor="lightgray")
    st.plotly_chart(fig, use_container_width=True)

    st.warning("""
    **⭐ TRADE-OFF CLAVE DEL PROYECTO:**

    La automatización total **maximiza la productividad técnica** (más uds por hora-hombre),
    pero **NO necesariamente es la más eficiente económicamente**.

    Aquí se demuestra el concepto central de Economía: la mejor opción **técnica** puede ser
    la peor opción **económica**. La decisión correcta integra ambas dimensiones.
    """)


# ==============================================================================
# TAB 5: MACRO
# ==============================================================================

with tab5:
    st.header("🌎 Variables macroeconómicas y sensibilidad")

    # Banner del tour si corresponde
    mostrar_paso_tour(6)

    # Variables actuales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Inflación anual", f"{params['inflacion']*100:.2f}%")
    with col2:
        st.metric("Tasa de interés", f"{params['tasa_interes']*100:.2f}%")
    with col3:
        st.metric("TRM", f"${params['trm']:,.0f} COP/USD")

    st.markdown("---")

    # Sensibilidad CAPEX a TRM
    st.subheader("Sensibilidad del CAPEX al tipo de cambio (TRM)")

    df_trm = pd.DataFrame({
        "Alternativa": ["Sistema actual", "Auto. parcial", "Auto. total"],
        "CAPEX base (COP)": [
            f"${res_actual['capex']/1e6:,.0f}M",
            f"${res_parcial['capex']/1e6:,.0f}M",
            f"${res_total['capex']/1e6:,.0f}M",
        ],
        "CAPEX ajustado por TRM": [
            f"${res_actual['capex_ajustado']/1e6:,.0f}M",
            f"${res_parcial['capex_ajustado']/1e6:,.0f}M",
            f"${res_total['capex_ajustado']/1e6:,.0f}M",
        ],
        "Δ por TRM": [
            f"${(res_actual['capex_ajustado']-res_actual['capex'])/1e6:+,.0f}M",
            f"${(res_parcial['capex_ajustado']-res_parcial['capex'])/1e6:+,.0f}M",
            f"${(res_total['capex_ajustado']-res_total['capex'])/1e6:+,.0f}M",
        ],
    })
    st.dataframe(df_trm, use_container_width=True, hide_index=True)

    st.warning("""
    ⚠️ La automatización total es la **más expuesta al riesgo cambiario** debido a su alto
    componente de equipos importados (sensores, PLC, robots).
    """)

    st.markdown("---")

    # Explicaciones macro
    st.subheader("Cómo afecta cada variable macroeconómica al proyecto")

    macro_items = [
        ("💵 INFLACIÓN", "Eleva el costo de mano de obra y materiales año a año. Los flujos de caja futuros se ajustan por inflación."),
        ("🏦 TASA DE INTERÉS", "Es el costo de capital usado para descontar flujos futuros (cálculo dla Ganancia). Una tasa más alta penaliza alternativas con CAPEX elevado."),
        ("💱 TIPO DE CAMBIO (TRM)", "Sensores, PLC y robots son importados. Si la TRM sube, el CAPEX real aumenta para alternativas con mayor componente importado."),
        ("🏛️ POLÍTICA MONETARIA", "Determina la tasa de interés. El Banco de la República puede subir tasas si la inflación se desvía de la meta (3%)."),
        ("📊 POLÍTICA FISCAL", "Beneficios tributarios por inversión en innovación (Ley 1715 o equivalentes) podrían reducir el CAPEX efectivo."),
        ("📉 CICLOS ECONÓMICOS", "En recesión, la demanda industrial cae. Esto afecta la producción esperada y por ende la Ganancia."),
        ("🌐 COMERCIO INTERNACIONAL", "Aranceles e impuestos a importación de bienes de capital impactan el CAPEX de las alternativas más tecnificadas."),
    ]

    for titulo, desc in macro_items:
        with st.container():
            st.markdown(f"""
            <div class="concepto-card">
                <h4>{titulo}</h4>
                <p style="margin:0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# TAB 6: ESCENARIOS
# ==============================================================================

with tab6:
    st.header("🎲 Análisis de escenarios — riesgo económico")

    # Banner del tour si corresponde
    mostrar_paso_tour(7)

    st.markdown("""
    Para evaluar el **riesgo económico**, simulamos tres escenarios:
    - **🔴 Pesimista:** demanda -15%, precio -3%, TRM +$300, CF +3%, salarios +5%
    - **⚪ Probable:** valores base del modelo (los que están en el panel izquierdo)
    - **🟢 Optimista:** demanda +20%, precio +5%, TRM -$300, CF -5%, salarios -5%
    """)

    # Tabla VAN por escenario
    st.subheader("Ganancia por escenario y alternativa")

    df_esc = pd.DataFrame({
        "Escenario": ["🔴 PESIMISTA", "⚪ PROBABLE", "🟢 OPTIMISTA"],
        "Sistema actual": [
            f"${escenarios['PESIMISTA']['actual']['ganancia_proyecto']/1e6:,.0f}M",
            f"${escenarios['PROBABLE']['actual']['ganancia_proyecto']/1e6:,.0f}M",
            f"${escenarios['OPTIMISTA']['actual']['ganancia_proyecto']/1e6:,.0f}M",
        ],
        "Auto. parcial": [
            f"${escenarios['PESIMISTA']['parcial']['ganancia_proyecto']/1e6:,.0f}M",
            f"${escenarios['PROBABLE']['parcial']['ganancia_proyecto']/1e6:,.0f}M",
            f"${escenarios['OPTIMISTA']['parcial']['ganancia_proyecto']/1e6:,.0f}M",
        ],
        "Auto. total": [
            f"${escenarios['PESIMISTA']['total']['ganancia_proyecto']/1e6:,.0f}M",
            f"${escenarios['PROBABLE']['total']['ganancia_proyecto']/1e6:,.0f}M",
            f"${escenarios['OPTIMISTA']['total']['ganancia_proyecto']/1e6:,.0f}M",
        ],
    })
    st.dataframe(df_esc, use_container_width=True, hide_index=True)

    # Gráfica
    st.subheader("Visualización de la Ganancia por escenario")

    escs = ["PESIMISTA", "PROBABLE", "OPTIMISTA"]
    fig = go.Figure()

    for alt_key, alt_nombre, color in [
        ("actual", "Sistema actual", COL_ACTUAL),
        ("parcial", "Auto. parcial", COL_PARCIAL),
        ("total", "Auto. total", COL_TOTAL),
    ]:
        vals = [escenarios[e][alt_key]["ganancia_proyecto"]/1e6 for e in escs]
        fig.add_trace(go.Bar(
            x=escs, y=vals, name=alt_nombre, marker_color=color,
            text=[f"${v:,.0f}M" for v in vals], textposition="outside",
        ))

    fig.add_hline(y=0, line_color="black", line_width=1)
    fig.update_layout(
        yaxis_title="Ganancia (millones COP)",
        barmode="group", height=500, plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="lightgray")
    fig.update_yaxes(gridcolor="lightgray")
    st.plotly_chart(fig, use_container_width=True)

    # Utilidad mensual por escenario
    st.subheader("Utilidad mensual por escenario")

    df_util = pd.DataFrame({
        "Escenario": ["🔴 PESIMISTA", "⚪ PROBABLE", "🟢 OPTIMISTA"],
        "Sistema actual": [
            f"${escenarios['PESIMISTA']['actual']['utilidad_mensual']/1e6:,.1f}M",
            f"${escenarios['PROBABLE']['actual']['utilidad_mensual']/1e6:,.1f}M",
            f"${escenarios['OPTIMISTA']['actual']['utilidad_mensual']/1e6:,.1f}M",
        ],
        "Auto. parcial": [
            f"${escenarios['PESIMISTA']['parcial']['utilidad_mensual']/1e6:,.1f}M",
            f"${escenarios['PROBABLE']['parcial']['utilidad_mensual']/1e6:,.1f}M",
            f"${escenarios['OPTIMISTA']['parcial']['utilidad_mensual']/1e6:,.1f}M",
        ],
        "Auto. total": [
            f"${escenarios['PESIMISTA']['total']['utilidad_mensual']/1e6:,.1f}M",
            f"${escenarios['PROBABLE']['total']['utilidad_mensual']/1e6:,.1f}M",
            f"${escenarios['OPTIMISTA']['total']['utilidad_mensual']/1e6:,.1f}M",
        ],
    })
    st.dataframe(df_util, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 7: MATRIZ DE DECISIÓN
# ==============================================================================

with tab7:
    st.header("⚖️ Matriz de decisión multicriterio")

    # Banner del tour si corresponde
    mostrar_paso_tour(8)

    st.markdown("""
    Integramos **7 criterios ponderados** para llegar a una decisión robusta.
    Cada criterio se califica de 1 a 5 por alternativa, y se pondera según su importancia.
    """)

    # Matriz visual
    st.subheader("Matriz de calificación ponderada")

    df_matriz = pd.DataFrame({
        "Criterio": list(pesos.keys()),
        "Peso": [f"{p:.0%}" for p in pesos.values()],
        "Sistema actual": [f"{detalle_matriz['Sistema actual'][c][0]} ({detalle_matriz['Sistema actual'][c][2]:.2f})" for c in pesos],
        "Auto. parcial": [f"{detalle_matriz['Automatización parcial'][c][0]} ({detalle_matriz['Automatización parcial'][c][2]:.2f})" for c in pesos],
        "Auto. total": [f"{detalle_matriz['Automatización total'][c][0]} ({detalle_matriz['Automatización total'][c][2]:.2f})" for c in pesos],
    })
    st.dataframe(df_matriz, use_container_width=True, hide_index=True)

    # Puntajes totales
    st.subheader("Puntajes ponderados totales")

    col1, col2, col3 = st.columns(3)
    nombres_matriz = list(totales_matriz.keys())
    valores = list(totales_matriz.values())

    for col, nombre, valor in zip([col1, col2, col3], nombres_matriz, valores):
        with col:
            color = "🟢" if valor >= 4.0 else ("🟡" if valor >= 3.5 else "🔴")
            st.metric(f"{color} {nombre}", f"{valor:.2f} / 5.00")

    # Gráfica de barras
    fig = go.Figure()
    nombres_corto = ["Actual", "Parcial", "Total"]
    fig.add_trace(go.Bar(
        x=nombres_corto, y=valores,
        marker_color=[COL_ACTUAL, COL_PARCIAL, COL_TOTAL],
        text=[f"{v:.2f}" for v in valores], textposition="outside",
        textfont=dict(size=16),
    ))
    fig.add_hline(y=3.5, line_dash="dash", line_color="green",
                  annotation_text="Umbral aceptable (3.5)", annotation_position="right")
    fig.update_layout(
        yaxis_title="Puntaje ponderado",
        yaxis=dict(range=[0, 5]),
        height=400, plot_bgcolor="white", showlegend=False,
    )
    fig.update_xaxes(gridcolor="lightgray")
    fig.update_yaxes(gridcolor="lightgray")
    st.plotly_chart(fig, use_container_width=True)

    ganadora = max(totales_matriz, key=totales_matriz.get)
    st.success(f"⭐ **Alternativa con mayor puntaje:** {ganadora} ({totales_matriz[ganadora]:.2f}/5.00)")


# ==============================================================================
# TAB 8: GUÍA DE CONCEPTOS
# ==============================================================================

with tab8:
    st.header("📚 Guía de conceptos económicos")

    # Banner del tour si corresponde (último paso)
    mostrar_paso_tour(9)

    st.caption("Conceptos económicos aplicados en el simulador con su definición y cómo se usan en el modelo.")

    conceptos = [
        ("1. Trade-offs", "Sacrificio que se hace al elegir una opción sobre otra. Ej: elegir auto. total significa sacrificar flexibilidad por productividad."),
        ("2. Oferta", "Cantidad que MecaSync puede producir. Está limitada por la capacidad instalada de cada alternativa (550/720/950 uds/mes)."),
        ("3. Demanda", "Cantidad que el mercado quiere comprar a cada precio. Modelada como Q = 1300 - 0.000312·P."),
        ("4. Equilibrio de mercado", "Punto donde oferta = demanda. Determina el precio y la cantidad transada."),
        ("5. Elasticidad", "Mide qué tanto cambia la cantidad demandada cuando cambia el precio. ε = -1.500 → demanda elástica."),
        ("6. Costos fijos (CF)", "No dependen del nivel de producción. Incluyen arriendo, depreciación, mantenimiento base, mano de obra fija."),
        ("7. Costos variables (CV)", "Crecen con la producción. Incluyen materiales, energía y reproceso."),
        ("8. Costo total (CT)", "CT = CF + CV. Costo total de operación."),
        ("9. Costo medio (CMe)", "CMe = CT/Q. Costo por unidad producida. A mayor producción, menor CMe (economías de escala)."),
        ("10. Costo marginal (CMg)", "ΔCT/ΔQ. Costo de producir una unidad adicional. En nuestro modelo lineal, CMg = CVu."),
        ("11. Productividad", "Unidades producidas por hora-hombre. La auto. total maximiza este indicador (0.903 uds/h-h)."),
        ("12. Eficiencia técnica", "Q real / capacidad instalada. Mide qué tan bien se usa la capacidad. Sistema actual: 94.5%."),
        ("13. Eficiencia económica", "Utilidad / costo total. Mide rentabilidad por peso invertido. **Aquí está el trade-off clave del proyecto**."),
        ("14. Inflación", "Aumento sostenido de precios. En el simulador, los flujos futuros se ajustan por 4.5% anual."),
        ("15. Tasa de interés", "Costo de oportunidad del capital. Es la rentabilidad alternativa: lo que ganarías en un CDT (12% E.A.). Se compara contra el ROI del proyecto."),
        ("16. Tipo de cambio (TRM)", "Precio del dólar en pesos. Afecta el CAPEX de equipos importados (sensores, PLC, robots)."),
        ("17. Punto de equilibrio", "Q donde IT = CT (no hay ni pérdida ni ganancia). Q_eq = CF/(P-CVu)."),
        ("18. Rentabilidad (Ganancia, ROI, Payback)", "Conjunto de indicadores que miden el valor económico generado por la inversión."),
        ("19. Riesgo económico", "Probabilidad de obtener resultados diferentes a los esperados. Se analiza con los 3 escenarios."),
    ]

    cols = st.columns(2)
    for i, (titulo, desc) in enumerate(conceptos):
        col = cols[i % 2]
        with col:
            st.markdown(f"""
            <div class="concepto-card">
                <h4>{titulo}</h4>
                <p style="margin:0; font-size: 0.9rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("""
    **Insight clave del proyecto: trade-off entre eficiencia técnica y económica**

    La automatización total maximiza la productividad técnica (0.903 uds/h-h) pero presenta
    eficiencia económica negativa (-2.1%) porque su CAPEX no se recupera con la demanda esperada.
    Esto demuestra que la mejor opción técnica no siempre es la mejor opción económica.
    """)


# ==============================================================================
# FOOTER
# ==============================================================================

st.markdown("---")
st.caption("""
🏭 **Simulador MecaSync S.A.S.** — Proyecto Final de Economía 2026-I
| Universidad Militar Nueva Granada — Ingeniería en Mecatrónica
| Integrantes: Juan Osuna, Santiago Rey, Juan Parrado, Germán Salazar
""")
