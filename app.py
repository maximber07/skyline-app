import streamlit as st

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Calculadora Skyline", page_icon="🧮", layout="centered")

# --- DISEÑO VISUAL PARA CELULAR (Sin errores de Padding) ---
st.markdown("""
<style>
    .resumen-caja {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0f766e;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .total-neto {
        color: #0f766e; 
        font-size: 22px; 
        font-weight: bold; 
        border-top: 2px solid #cbd5e1;
        padding-top: 10px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧮 Skyline Hood Cleaning")
st.markdown("**Cálculos rápidos para empleados (Versión Móvil)**")

TAX_RATES = {
    "Connecticut (6.35%)": 0.0635,
    "New Jersey (6.625%)": 0.06625,
    "New York (8.875%)": 0.08875,
    "Pennsylvania (6.0%)": 0.060
}

# --- FORMULARIO DE DATOS ---
st.subheader("⚙️ Configuración de la Orden")
q_estado = st.selectbox("Estado:", list(TAX_RATES.keys()))
q_tipo_rest = st.selectbox("Tipo de Restaurante:", ["Hispano (Normal)", "Americano (+10%)", "Chino (+15%)"])

col1, col2 = st.columns(2)
with col1:
    q_piso = st.selectbox("Piso del Local:", [int(i) for i in range(1, 15)])
with col2:
    q_desc = st.selectbox("Descuento Cliente:", ["0%", "10%", "15%", "20%", "25%"])

st.subheader("🔧 Componentes del Sistema")
c1, c2 = st.columns(2)
with c1:
    q_filtros = st.number_input("Cantidad de Filtros:", min_value=2, value=3)
    q_campanas = st.number_input("Hoods Totales:", min_value=1, value=1)
with c2:
    q_abanicos = st.number_input("Abanicos Totales:", min_value=1, value=1)
    q_ductos = st.number_input("Ductos Totales:", min_value=1, value=1)

# --- BOTÓN DE CÁLCULO ---
if st.button("CALCULAR TOTAL", type="primary", use_container_width=True):
    tasa_tax = TAX_RATES[q_estado]
    porcentaje_desc = float(q_desc.replace('%', '')) / 100
    
    # 1. MATRIZ DE PRECIOS BASE
    precios_fijos = {
        2: 408.00, 3: 435.50, 4: 435.50, 5: 440.00, 6: 450.00,
        7: 463.80, 8: 480.80, 9: 500.00, 10: 500.50, 11: 515.50,
        12: 550.50, 13: 550.00, 14: 580.00, 15: 600.00, 16: 650.00,
        17: 660.00, 18: 700.00, 19: 800.00, 20: 850.00, 21: 900.00
    }
    
    if q_filtros in precios_fijos:
        precio_objetivo = precios_fijos[q_filtros]
    elif 22 <= q_filtros <= 26:
        precio_objetivo = 1200.00
    elif 27 <= q_filtros <= 30:
        precio_objetivo = 1300.00
    elif 31 <= q_filtros <= 37:
        precio_objetivo = 1450.00
    else:
        precio_objetivo = 1450.00 + ((q_filtros - 37) * 40.00)

    base_filtros_limpio = precio_objetivo / (1 + tasa_tax)

    # 2. EXTRAS (Campanas, Abanicos y Ductos escalonados)
    extras_campana = (q_campanas - 1) * 35.00 if q_campanas > 1 else 0.0
    extras_abanico = (q_abanicos - 1) * 45.00 if q_abanicos > 1 else 0.0
    
    if q_ductos <= 1: extras_ducto = 0.0
    elif q_ductos == 2: extras_ducto = 20.0
    elif q_ductos == 3: extras_ducto = 40.0
    elif q_ductos == 4: extras_ducto = 50.0
    else: extras_ducto = 60.0 + ((q_ductos - 5) * 10.0)

    total_adicionales_base = extras_campana + extras_abanico + extras_ducto
    subtotal_base_limpio = base_filtros_limpio + total_adicionales_base

    # 3. RECARGO TIPO DE RESTAURANTE
    porcentaje_tipo = 0.0
    nombre_tipo_display = "Hispano"
    if "Americano" in q_tipo_rest:
        porcentaje_tipo = 0.10
        nombre_tipo_display = "Americano (+10%)"
    elif "Chino" in q_tipo_rest:
        porcentaje_tipo = 0.15
        nombre_tipo_display = "Chino (+15%)"
        
    recargo_tipo = subtotal_base_limpio * porcentaje_tipo
    
    # 4. RECARGO PISO ESCALONADO
    recargo_piso = 0.0
    if q_piso >= 3:
        recargo_piso = 25.0 + ((q_piso - 3) * 10.0)
        
    base_con_recargos = subtotal_base_limpio + recargo_tipo + recargo_piso
    
    # 5. DESCUENTO Y TAX
    valor_descuento = base_con_recargos * porcentaje_desc
    base_final = base_con_recargos - valor_descuento
    
    tax_final = base_final * tasa_tax
    total_final_cobrar = base_final + tax_final

    # --- PANTALLA DE RESULTADOS ---
    st.markdown('<div class="resumen-caja">', unsafe_allow_html=True)
    st.markdown("### 🧾 Resumen de Cotización")
    st.write(f"**Precio Base Filtros:** ${base_filtros_limpio:.2f}")
    st.write(f"**Cargos Adicionales:** ${total_adicionales_base:.2f}")
    
    if porcentaje_tipo > 0:
        st.write(f"**Recargo Rest. {nombre_tipo_display}:** ${recargo_tipo:.2f}")
    
    if q_piso >= 3:
        st.write(f"**Recargo Piso ({q_piso}º):** ${recargo_piso:.2f}")
        
    if valor_descuento > 0:
        st.markdown(f"**Descuento Cliente:** :red[-${valor_descuento:.2f}]")
        
    estado_nombre = q_estado.split(' ')[0]
    st.write(f"**Tax ({estado_nombre}):** ${tax_final:.2f}")
    st.markdown(f'<div class="total-neto">TOTAL NETO A COBRAR: ${total_final_cobrar:.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
