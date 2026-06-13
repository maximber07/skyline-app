import streamlit as st
import pandas as pd
import os
from datetime import date, datetime, timedelta
import time
from fpdf import FPDF
import io

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Skyline Hood Cleaning Services", layout="wide")

# --- 2. ESTILOS INYECTADOS (CSS) PARA DISEÑO ULTRA MODERNO Y MENÚ EXTENDIDO ---
st.markdown("""
<style>
    /* Estilos globales y fuentes modernas */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Poppins', 'Segoe UI', sans-serif;
    }
    
    /* Incrementa el tamaño, grosor y separación de los textos del menú lateral */
    .stSidebar .stRadio div [role="radiogroup"] label {
        font-size: 19px !important; 
        font-weight: 600 !important; 
        padding: 12px 0px !important; 
        color: #333333;
    }
    .stSidebar p {
        font-size: 17px !important;
    }
    
    /* Contenedores con el matiz moderno Premium WOW */
    .hero-container {
        background: linear-gradient(135deg, #06101e 0%, #0b1e36 50%, #122e52 100%); 
        padding: 50px; 
        border-radius: 24px; 
        text-align: center; 
        color: white; 
        margin-bottom: 25px; 
        box-shadow: 0px 15px 35px rgba(0,0,0,0.4); 
        border: 1px solid rgba(0, 210, 255, 0.2);
        border-bottom: 5px solid #00d2ff;
    }
    .card-modern-blue {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.03);
        border-left: 6px solid #00d2ff;
        margin-bottom: 20px;
    }
    .card-modern-dark {
        background: #0d1b2a;
        border: 1px solid #1b263b;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        border-left: 6px solid #e0e1dd;
        margin-bottom: 20px;
        color: #ffffff;
    }
    
    /* Caja de Cotización Rediseñada (Estilo Recibo Premium Digital) */
    .premium-quote-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 30px;
        margin-top: 20px;
        box-shadow: 0px 12px 30px rgba(0, 0, 0, 0.05);
        border-top: 6px solid #11998e;
    }
    .quote-title {
        color: #0b1e36;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 20px;
        border-bottom: 2px dashed #e2e8f0;
        padding-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .quote-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 15px;
        color: #475569;
    }
    .quote-row.total {
        border-bottom: none;
        padding-top: 15px;
        font-size: 22px;
        font-weight: 800;
        color: #11998e;
    }
    .quote-badge {
        background-color: #fef3c7;
        color: #d97706;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN E IMPUESTOS ---
TAX_RATES = {
    "Connecticut (6.35%)": 0.0635,
    "New Jersey (6.625%)": 0.06625,
    "New York (8.875%)": 0.08875,
    "Pennsylvania (6.0%)": 0.060
}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- RUTAS DE ARCHIVOS ---
DB_USUARIOS = os.path.join(BASE_DIR, 'usuarios_skyline.csv')
DB_CLIENTES = os.path.join(BASE_DIR, 'clientes_skyline.csv')
DB_CITAS = os.path.join(BASE_DIR, 'citas_skyline.csv')
DB_INVENTARIO = os.path.join(BASE_DIR, 'inventario_skyline.csv')
DB_ENTREGAS_INVENTARIO = os.path.join(BASE_DIR, 'entregas_inventario.csv')
DB_CONTACTOS = os.path.join(BASE_DIR, 'contactos_skyline.csv')
DB_CHAT = os.path.join(BASE_DIR, 'chat_clientes.csv')

F_FILTROS = os.path.join(BASE_DIR, "foto_filtros.png")
F_FANS = os.path.join(BASE_DIR, "foto_fans.png")
F_MOTORES = os.path.join(BASE_DIR, "foto_motores.png")
F_CORREAS = os.path.join(BASE_DIR, "foto_correas.png")

F_ANTES_DESPUES = os.path.join(BASE_DIR, 'trabajo_antes_despues.png')
F_PRESSURE_WASH = os.path.join(BASE_DIR, 'limpieza_presion.png')
LOGO_SKYLINE = os.path.join(BASE_DIR, 'logo_skyline.png')
LOGO_NFPA = os.path.join(BASE_DIR, 'Gemini_Generated_Image_qxbehqxbehqxbehq.png')

COLS_CITAS = ["Cliente", "Estado", "Campanas", "Filtros", "Abanico_Extractor_Techo", "Ductos", "Reparacion", "Monto_Base", "Total", "Estatus", "Metodo", "Fecha", "Hora", "Notas_Especiales", "Hora_Pago", "Id_Factura", "Frecuencia_Meses"]
COLS_CONTACTOS = ["First_Name", "Last_Name", "Email", "Phone", "Subject", "Message", "Fecha_Registro"]
COLS_CHAT = ["Fecha","Nombre","Mensaje"]

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_time" not in st.session_state:
    st.session_state.login_time = None
if "user" not in st.session_state:
    st.session_state.user = None
if "rol" not in st.session_state:
    st.session_state.rol = None
if "last_work_summary" not in st.session_state:
    st.session_state.last_work_summary = None

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos(archivo, cols):
    if not os.path.exists(archivo) or os.stat(archivo).st_size == 0:
        df_vacio = pd.DataFrame(columns=cols)
        df_vacio.to_csv(archivo, index=False)
        return df_vacio
    try:
        df = pd.read_csv(archivo)
        if 'Metodo' in df.columns: 
            df['Metodo'] = df['Metodo'].astype(str)
        for c in cols:
            if c not in df.columns:
                if c == "Id_Factura": df[c] = ""
                elif c == "Frecuencia_Meses": df[c] = 3
                else: df[c] = "N/A"
        if 'Hora_Pago' in df.columns:
            df['Hora_Pago'] = df['Hora_Pago'].astype(str).replace(['nan', 'NaN', '<NA>'], 'N/A')
        return df[cols]
    except Exception:
        return pd.DataFrame(columns=cols)

def safe_txt(texto):
    return str(texto).encode('latin-1', 'ignore').decode('latin-1')

def verificar_alertas_limpieza():
    df_cit = cargar_datos(DB_CITAS, COLS_CITAS)
    if df_cit.empty: return
    alertas = []
    hoy = date.today()
    for cliente, datos in df_cit.groupby("Cliente"):
        citas_ordenadas = datos.copy()
        citas_ordenadas['Fecha_Parsed'] = pd.to_datetime(citas_ordenadas['Fecha'], format='%m/%d/%Y', errors='coerce')
        citas_ordenadas = citas_ordenadas.dropna(subset=['Fecha_Parsed']).sort_values('Fecha_Parsed', ascending=False)
        if not citas_ordenadas.empty:
            ultima_cita = citas_ordenadas.iloc[0]
            fecha_ultima = ultima_cita['Fecha_Parsed'].date()
            try: meses = int(float(ultima_cita['Frecuencia_Meses']))
            except: meses = 3
            fecha_vencimiento = fecha_ultima + timedelta(days=meses * 30)
            dias_restantes = (fecha_vencimiento - hoy).days
            if dias_restantes <= 15:
                alertas.append({
                    "cliente": cliente, "ultima": fecha_ultima.strftime('%m/%d/%Y'),
                    "vence": fecha_vencimiento.strftime('%m/%d/%Y'), "dias": dias_restantes
                })
    if alertas:
        st.markdown("<h3 style='color: #ff3333; font-weight: bold;'>⚠️ Alertas de Próximos Mantenimientos (15 días o menos)</h3>", unsafe_allow_html=True)
        for a in alertas:
            if a['dias'] > 0: st.warning(f"⏳ El servicio de **{a['cliente']}** se vence el **{a['vence']}** (Faltan {a['dias']} días).")
            elif a['dias'] == 0: st.error(f"🚨 **¡HOY TOCA LIMPIEZA!** El servicio de **{a['cliente']}** vence el día de hoy.")
            else: st.error(f"❌ **¡VENCIDO!** El servicio de **{a['cliente']}** venció hace {abs(a['dias'])} días.")
        st.markdown("---")

# --- FUNCIONES PDF ---
def generar_factura_pdf(d, index):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    monto_base_val = float(d.get('Monto_Base', 0))
    total_val = float(d.get('Total', 0))
    
    if os.path.exists(LOGO_NFPA): pdf.image(LOGO_NFPA, x=15, y=10, w=35)
    elif os.path.exists(LOGO_SKYLINE): pdf.image(LOGO_SKYLINE, x=15, y=12, w=28)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.set_xy(55, 12)
    pdf.cell(100, 4, "Skyline hood cleaning services llc", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.set_x(55)
    pdf.cell(100, 4, "P.O box 27", ln=True)
    pdf.set_x(55)
    pdf.cell(100, 4, "Lodi, NJ 07644-1905 United States", ln=True)
    pdf.set_x(55)
    pdf.cell(100, 4, "skylinehcs@gmail.com | (862) 882-1802", ln=True)
    
    inv_num = str(d.get('Id_Factura', f"#00{1200 + int(index)}"))
    pdf.set_xy(145, 12)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(50, 4, f"Invoice {inv_num}", ln=True, align='R')
    pdf.set_font("Arial", '', 9)
    pdf.set_x(145)
    pdf.cell(50, 4, "Issue date", ln=True, align='R')
    pdf.set_x(145)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(50, 4, safe_txt(d['Fecha']), ln=True, align='R')
    
    pdf.ln(6)
    pdf.set_draw_color(110, 185, 245)
    pdf.set_line_width(2.5)
    pdf.line(15, 38, 195, 38)
    
    pdf.set_y(44)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 10, f"Invoice {inv_num}", ln=True)
    
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, "Thank you for choosing SKYLINE We appreciate your business.", ln=True)
    pdf.ln(4)
    
    pdf.set_draw_color(220, 220, 220)
    pdf.set_line_width(0.3)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    
    df_cli_info = cargar_datos(DB_CLIENTES, ["Nombre_Restaurante", "Telefono_Restaurante", "Direccion_Restaurante"])
    c_data = df_cli_info[df_cli_info["Nombre_Restaurante"] == d["Cliente"]]
    c_phone = c_data.iloc[0]["Telefono_Restaurante"] if not c_data.empty else "N/A"
    c_address = c_data.iloc[0]["Direccion_Restaurante"] if not c_data.empty else "N/A"
    
    y_start_cols = pdf.get_y()
    
    pdf.set_xy(15, y_start_cols)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(60, 4, "Customer", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(15)
    pdf.cell(60, 4, safe_txt(d['Cliente']), ln=True)
    pdf.set_x(15)
    pdf.cell(60, 4, safe_txt(c_phone), ln=True)
    pdf.set_x(15)
    pdf.multi_cell(60, 4, safe_txt(c_address))
    
    pdf.set_xy(80, y_start_cols)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(60, 4, "Invoice Details", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(80)
    pdf.cell(60, 4, f"PDF created {date.today().strftime('%B %d, %Y')}", ln=True)
    pdf.set_x(80)
    pdf.cell(60, 4, f"${total_val:.2f}", ln=True)
    pdf.set_x(80)
    pdf.cell(60, 4, f"Service date {safe_txt(d['Fecha'])}", ln=True)
    
    pdf.set_xy(145, y_start_cols)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(50, 4, "Payment", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(145)
    pdf.cell(50, 4, f"Due {safe_txt(d['Fecha'])}", ln=True)
    pdf.set_x(145)
    pdf.cell(50, 4, f"${total_val:.2f}", ln=True)
    
    pdf.set_y(y_start_cols + 24)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(100, 5, "Items")
    pdf.cell(25, 5, "Quantity", align='C')
    pdf.cell(25, 5, "Price", align='R')
    pdf.cell(30, 5, "Amount", ln=True, align='R')
    
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font("Arial", '', 9.5)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(100, 5, "Custom Amount")
    pdf.cell(25, 5, "1", align='C')
    pdf.cell(25, 5, f"${monto_base_val:.2f}", align='R')
    pdf.cell(30, 5, f"${monto_base_val:.2f}", ln=True, align='R')
    
    pdf.set_font("Arial", '', 8.5)
    pdf.set_text_color(120, 120, 120)
    pdf.set_x(18)
    pdf.cell(100, 4, "COMMERCIAL HOOD CLEANING:", ln=True)
    items_limpieza = ["Clean hood", "Clean blowers", "Clean Fans", "Clean filters", "Clean ducts", "Clean chambers", "Clean walls"]
    for item in items_limpieza:
        pdf.set_x(22)
        pdf.cell(100, 3.8, f"- {item}", ln=True)
        
    pdf.set_x(18)
    pdf.cell(100, 4, f"Technicians: 3", ln=True)
    pdf.ln(3)
    
    pdf.set_font("Arial", 'I', 8.5)
    pdf.cell(0, 4, "Certification labels are affixed to each hood system with date serviced and the next service date", ln=True)
    pdf.ln(2)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", '', 9.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(140, 5, "Subtotal", align='R')
    pdf.cell(40, 5, f"${monto_base_val:.2f}", ln=True, align='R')
    
    monto_tax = total_val - monto_base_val
    if monto_tax > 0:
        pdf.cell(140, 5, f"Tax ({safe_txt(d['Estado'])})", align='R')
        pdf.cell(40, 5, f"${monto_tax:.2f}", ln=True, align='R')
        
    pdf.ln(2)
    pdf.line(120, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(140, 7, "Total Paid", align='R')
    pdf.cell(40, 7, f"${total_val:.2f}", ln=True, align='R')
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 4, "Payments", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(80, 80, 80)
    
    log_pago = d['Hora_Pago'] if d['Hora_Pago'] != "N/A" else d['Fecha']
    pdf.cell(140, 5, f"{safe_txt(log_pago)} ({safe_txt(d['Metodo'])})")
    pdf.cell(40, 5, f"${total_val:.2f}", ln=True, align='R')
    pdf.ln(8)
    
    pdf.set_font("Arial", 'B', 9.5)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 5, "$75 per Referral", ln=True)
    
    pdf.set_y(260)
    pdf.set_draw_color(230, 230, 230)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 8.5)
    pdf.cell(100, 4, "View online")
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(140, 140, 140)
    pdf.cell(80, 4, "Page 1 of 1", ln=True, align='R')
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 3.5, "To view your invoice go to https://squareup.com/u/PeASqSwf", ln=True)
    
    clean_inv_name = str(inv_num).replace("#", "")
    path_factura = os.path.join(BASE_DIR, f"Factura_Comercial_{clean_inv_name}.pdf")
    pdf.output(path_factura)
    return path_factura

def generar_pdf_exacto(d, inputs_usuario):
    pdf = FPDF()
    pdf.add_page()
    
    if os.path.exists(LOGO_NFPA):
        pdf.image(LOGO_NFPA, x=75, y=12, w=60)
        pdf.set_y(48)
    else:
        pdf.set_y(15)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "KEC SERVICE REPORT", ln=True, align='C')
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 5, "SKYLINE HOOD CLEANING SERVICES", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, "EMAIL: SKYLINEHCS@GMAIL.COM | PHONE: 862 882 1802", ln=True, align='C')
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(100, 6, f"Business Name: {safe_txt(d['Cliente'])}", border=1)
    fecha_hoy = date.today().strftime("%m/%d/%Y")
    pdf.cell(90, 6, f"Date: {fecha_hoy}", border=1, ln=True)
    
    pdf.cell(100, 6, f"Address: {safe_txt(inputs_usuario['direccion'])}", border=1)
    pdf.cell(90, 6, f"Time Silas: {safe_txt(inputs_usuario['time_silas'])}", border=1, ln=True)
    pdf.cell(100, 6, f"Contact: {safe_txt(inputs_usuario['contacto'])}", border=1)
    pdf.cell(90, 6, f"Service Term: {safe_txt(inputs_usuario['service_term'])}", border=1, ln=True)
    pdf.cell(100, 6, f"Contact info: {safe_txt(inputs_usuario['contact_info'])}", border=1)
    
    next_service_str = inputs_usuario['next_service'].strftime("%m/%d/%Y") if inputs_usuario['next_service'] else ""
    pdf.cell(90, 6, f"Next service Date: {next_service_str}", border=1, ln=True)
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 5, "OUR CLEANING PROCESS", ln=True, fill=False)
    pdf.set_font("Arial", '', 8)
    procesos = [
        "1) We cover the whole hood with plastic sheeting",
        "2) Using several tools we eliminate all the grease in the hood, duct, suppression nozzle and fan",
        "3) After removing the grease we use chemicals to melt the left over grease",
        "4) After 10 minutes we use a hot steam power washer to remove the grease in the hood and duct",
        "5) We repeat steps 1-4 until all the grease is removed from the hood and duct",
        "6) After grease is completely removed we perform our final inspection and clean up"
    ]
    for p in procesos:
        pdf.cell(0, 4, p, ln=True)
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 5, "PRE-HOOD CLEANING CHECK (FANS & FILTERS)", ln=True)
    pdf.set_font("Arial", '', 8)
    
    last_service_str = inputs_usuario['last_service'].strftime("%m/%d/%Y") if inputs_usuario['last_service'] else ""
    pdf.cell(95, 5, f"Last Date of Service: {last_service_str}", border=1)
    pdf.cell(95, 5, f"Quantity of Fans: {d.get('Abanico_Extractor_Techo', d.get('Fan_Extraccion', ''))}", border=1, ln=True)
    pdf.cell(95, 5, f"Number of Hoods: {d.get('Campanas', d.get('Hoods', ''))}", border=1)
    pdf.cell(95, 5, f"Location: {safe_txt(inputs_usuario['location'])}", border=1, ln=True)
    pdf.cell(95, 5, f"Grease load Level: {safe_txt(inputs_usuario['grease_load'])}", border=1)
    pdf.cell(95, 5, f"Condition: {safe_txt(inputs_usuario['condition'])}", border=1, ln=True)
    pdf.cell(95, 5, f"Hood Lights & Globes: {safe_txt(inputs_usuario['lights'])}", border=1)
    pdf.cell(95, 5, f"Grease collector: {safe_txt(inputs_usuario['collector'])}", border=1, ln=True)
    pdf.cell(95, 5, f"Hinged?: {safe_txt(inputs_usuario['hinged'])}", border=1)
    pdf.cell(95, 5, f"Appliances Disconnected?: {safe_txt(inputs_usuario['appliances'])}", border=1, ln=True)
    pdf.cell(95, 5, f"Gas Pilots: {safe_txt(inputs_usuario['gas_pilots'])}", border=1)
    pdf.cell(95, 5, f"Roof Access?: {safe_txt(inputs_usuario['roof_access'])}", border=1, ln=True)
    pdf.cell(95, 5, f"Duct Grease Level: {safe_txt(inputs_usuario['duct_grease'])}", border=1)
    pdf.cell(95, 5, f"Visible Grease Leaks?: {safe_txt(inputs_usuario['leaks'])}", border=1, ln=True)
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 5, "FILTERS CONFIGURATION (Quantity size)", ln=True)
    pdf.set_font("Arial", '', 8)
    pdf.cell(63, 5, f"25x16: {inputs_usuario['f25x16']}", border=1)
    pdf.cell(63, 5, f"25x20: {inputs_usuario['f25x20']}", border=1)
    pdf.cell(64, 5, f"25x25: {inputs_usuario['f25x25']}", border=1, ln=True)
    pdf.cell(63, 5, f"20x16: {inputs_usuario['f20x16']}", border=1)
    pdf.cell(63, 5, f"20x20: {inputs_usuario['f20x20']}", border=1)
    pdf.cell(64, 5, f"20x25: {inputs_usuario['f20x25']}", border=1, ln=True)
    pdf.cell(63, 5, f"16x16: {inputs_usuario['f16x16']}", border=1)
    pdf.cell(63, 5, f"16x20: {inputs_usuario['f16x20']}", border=1)
    pdf.cell(64, 5, f"16x25: {inputs_usuario['f16x25']}", border=1, ln=True)
    pdf.cell(95, 5, f"Filter Company Used?: {safe_txt(inputs_usuario['filter_company'])}", border=1)
    pdf.cell(95, 5, f"Cleaned on site / Swapped: {safe_txt(inputs_usuario['filter_action'])}", border=1, ln=True)
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(130, 5, "POST-CLEANING CHECK EVALUATION", border=1)
    pdf.cell(60, 5, "CHECK", border=1, ln=True, align='C')
    pdf.set_font("Arial", '', 8)
    post_items = [
        ("Work area free of grease/rags?", safe_txt(inputs_usuario['post_free'])),
        ("Updated sticker placed on Hood?", safe_txt(inputs_usuario['post_sticker'])),
        ("Appliances Reconnected?", safe_txt(inputs_usuario['post_reconnected'])),
        ("Gas Pilots Turned on / Valve status", safe_txt(inputs_usuario['post_gas'])),
        ("Before/After Photos Taken?", safe_txt(inputs_usuario['post_photos'])),
        ("Any inaccessible areas?", safe_txt(inputs_usuario['post_inaccessible']))
    ]
    for item, val in post_items:
        pdf.cell(130, 4, item, border=1)
        pdf.cell(60, 4, val, border=1, ln=True, align='C')
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 5, f"SERVICES PERFORMED: {safe_txt(inputs_usuario['services_done'])}", ln=True)
    pdf.cell(0, 5, "COMMENTS / RECOMMENDATIONS:", ln=True)
    pdf.set_font("Arial", '', 8)
    pdf.multi_cell(0, 5, safe_txt(inputs_usuario['comments']), border=1)
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 5, "THIS REPORT CERTIFIES THAT ALL SYSTEMS ARE UP TO NFPA96 REQUIREMENTS", ln=True, align='C')
    pdf.ln(4)
    
    y_firma = pdf.get_y()
    pdf.cell(95, 5, f"SERVICED BY: {safe_txt(inputs_usuario['serviced_by'])}", ln=False)
    if inputs_usuario['no_one_sign']:
        pdf.cell(95, 5, "[X] NO ONE AVAILABLE TO SIGN", ln=True)
    else:
        pdf.cell(95, 5, "CUSTOMER SIGNATURE: ___________________", ln=True)
        
    if os.path.exists(LOGO_NFPA):
        pdf.image(LOGO_NFPA, x=145, y=y_firma - 4, w=42)
    elif os.path.exists(LOGO_SKYLINE):
        pdf.image(LOGO_SKYLINE, x=150, y=y_firma - 10, w=45)
        
    path = os.path.join(BASE_DIR, "Reporte_KEC_Fiel.pdf")
    pdf.output(path)
    return path

# --- 4. MENÚ GENERAL ---
menu_publico = ["Panel Principal", "Calculadora de Campo", "💬 Chat con Soporte", "🔒 Área Administrativa"]

if st.session_state.logged_in:
    if st.session_state.rol == "Tecnico":
        menu_opciones = ["Panel Principal", "Calculadora de Campo", "💬 Chat con Soporte", "Clientes", "Citas", "Calendario de Google"]
    else:
        menu_opciones = [
            "Panel Principal", "Calculadora de Campo", "💬 Chat con Soporte", "Director del panel", 
            "Clientes", "Citas", "Inventario", "Solicitudes Recibidas", "Generar informe", "Calendario de Google"
        ]
        if st.session_state.rol == "Admin": 
            menu_opciones.append("Gestión Usuarios")
else:
    menu_opciones = menu_publico

menu = st.sidebar.radio("Sección:", menu_opciones)

# --- 5. MONITOREO DE TIEMPO LATERAL ---
if st.session_state.logged_in:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"👤 **Usuario:** {st.session_state.user} (`{st.session_state.rol}`)")
    formato_entrada = st.session_state.login_time.strftime("%I:%M:%S %p")
    st.sidebar.markdown(f"🛫 **Entrada:** {formato_entrada}")
    
    @st.fragment(run_every=1.0)
    def render_live_clock():
        segundos_transcurridos = int(time.time() - st.session_state.login_time.timestamp())
        mins, segs = divmod(segundos_transcurridos, 60)
        hrs, mins = divmod(mins, 60)
        st.markdown(f"⏱️ **Tiempo activo:** `{hrs:02d}h {mins:02d}m {segs:02d}s`")
        
    render_live_clock()
    
    if st.sidebar.button("🔴 Salir / Logout"):
        hora_salida = datetime.now().strftime("%I:%M:%S %p")
        segundos_totales = int(time.time() - st.session_state.login_time.timestamp())
        mins_totales, segs_restantes = divmod(segundos_totales, 60)
        hrs_totales, mins_finales = divmod(mins_totales, 60)
        if segs_restantes > 0 or (hrs_totales == 0 and mins_finales == 0):
            mins_finales += 1
            if mins_finales >= 60:
                mins_finales = 0
                hrs_totales += 1

        st.session_state.last_work_summary = {
            "usuario": st.session_state.user, "entrada": formato_entrada, "salida": hora_salida,
            "horas": hrs_totales, "minutos": mins_finales
        }
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.rol = None
        st.session_state.login_time = None
        st.rerun()

if st.session_state.last_work_summary is not None:
    s = st.session_state.last_work_summary
    st.info(f"💼 **Registro de Jornada de {s['usuario']}:** Entrada {s['entrada']} | Salida {s['salida']} ➡️ **Horas:** {s['horas']}h {s['minutos']}m.")
    st.session_state.last_work_summary = None

# --- 6. CONTENIDO DE LAS SECCIONES ---

if menu == "Panel Principal":
    st.markdown("""
    <div class="hero-container">
        <h1 style="margin: 0; font-size: 52px; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; text-shadow: 0px 4px 12px rgba(0,210,255,0.4); color: #ffffff;">💎 Skyline Hood Cleaning Services</h1>
        <p style="margin: 15px 0 0 0; font-size: 21px; color: #00d2ff; font-weight: 500; letter-spacing: 1px;">Commercial Hood Cleaning & NFPA96 Certified Inspections</p>
        <div style="margin-top: 20px; height: 3px; background: linear-gradient(to right, transparent, #00d2ff, #00ffcc, transparent); width: 50%; margin-left: auto; margin-right: auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        verificar_alertas_limpieza()
    
    st.markdown("""
<style>
    @keyframes marquee { 0% { transform: translateX(0%); } 100% { transform: translateX(-50%); } }
    .marquee-container { overflow: hidden; white-space: nowrap; background: #06101e; padding: 18px 0; border-radius: 14px; box-shadow: inset 0 0 15px rgba(0,0,0,0.6); margin-bottom: 25px; border: 2px solid #00d2ff; display: flex; }
    .marquee-content { display: inline-flex; animation: marquee 25s linear infinite; }
    .marquee-item { display: inline-flex; align-items: center; color: #ffffff; font-family: 'Arial', sans-serif; font-weight: bold; font-size: 16px; margin-right: 50px; letter-spacing: 0.5px; }
    .marquee-item span { color: #00d2ff; margin-right: 10px; font-size: 20px; }
    .marquee-container:hover .marquee-content { animation-play-state: paused; }
</style>
<div class="marquee-container">
    <div class="marquee-content">
        <div class="marquee-item"><span>🌀</span> ABANICOS EXTRACTORES DE TECHO</div>
        <div class="marquee-item"><span>🔥</span> CAMPANAS EXTRACTORAS COMERCIALES</div>
        <div class="marquee-item"><span>🧼</span> FILTROS DE GRASA (GREASE FILTERS)</div>
        <div class="marquee-item"><span>⚙️</span> CORREAS DE DISTRIBUCIÓN (BELTS)</div>
        <div class="marquee-item"><span>⚡</span> MOTORES ELÉCTRICOS DE EXTRACCIÓN</div>
        <div class="marquee-item"><span>🛡️</span> CERTIFICACIÓN OFICIAL NFPA96</div>
        <div class="marquee-item"><span>💧</span> HIDROLAVADO A VAPOR COMPLETO</div>
        <div class="marquee-item"><span>🌀</span> ABANICOS EXTRACTORES DE TECHO</div>
        <div class="marquee-item"><span>🔥</span> CAMPANAS EXTRACTORAS COMERCIALES</div>
        <div class="marquee-item"><span>🧼</span> FILTROS DE GRASA (GREASE FILTERS)</div>
        <div class="marquee-item"><span>⚙️</span> CORREAS DE DISTRIBUCIÓN (BELTS)</div>
        <div class="marquee-item"><span>⚡</span> MOTORES ELÉCTRICOS DE EXTRACCIÓN</div>
        <div class="marquee-item"><span>🛡️</span> CERTIFICACIÓN OFICIAL NFPA96</div>
        <div class="marquee-item"><span>💧</span> HIDROLAVADO A VAPOR COMPLETO</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: center; font-size: 16px; margin-bottom: 25px; font-weight: bold;'>
        <a href='https://www.facebook.com/profile.php?id=61551102158975' target='_blank' style='text-decoration:none; color:#1877f2; margin: 0 15px;'>🔵 Facebook</a> | 
        <a href='https://www.instagram.com/skylinehcs/' target='_blank' style='text-decoration:none; color:#c13584; margin: 0 15px;'>🟣 Instagram</a> | 
        <a href='https://www.tiktok.com/@skylinehcs' target='_blank' style='text-decoration:none; color:#000000; margin: 0 15px; background-color: #f1f1f1; padding: 4px 10px; border-radius: 8px; border: 1px solid #ddd;'>🎵 TikTok Official</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 30px; border-radius: 15px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0px 8px 20px rgba(56,239,125,0.25); position: relative; overflow: hidden;">
        <div style="position: absolute; top: -50px; left: -50px; width: 150px; height: 150px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
        <span style="background-color: #ff3333; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 0 10px rgba(255,51,51,0.6);">⚡ ANUNCIO EN MOVIMIENTO</span>
        <h2 style="margin: 15px 0 8px 0; font-size: 28px; font-weight: 700; color: #ffffff;">🔥 ¿Tu Campana tiene Grasa Acumulada Peligrosa?</h2>
        <p style="margin: 0 0 18px 0; font-size: 16px; color: #f0fff4;">Mira cómo nuestro sistema de hidrolavado a vapor certificado por la NFPA96 remueve el 100% de los residuos al instante.</p>
        <a href="https://www.instagram.com/skylinehcs/" target="_blank" style="text-decoration: none;">
            <button style="background-color: #ffffff; color: #11998e; border: none; padding: 12px 28px; font-size: 15px; font-weight: bold; border-radius: 25px; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: 0.3s;">🔴 LIVE: Ver Limpieza en Acción</button>
        </a>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.video("https://www.tiktok.com/@skylinehcs/video/7422893589459488031?is_from_webapp=1&sender_device=pc&web_id=7644207014075975198")
        st.markdown("<p style='text-align: center; color: gray; font-size: 13px; margin-top: -10px; margin-bottom: 35px;'>🎥 Demostración Oficial: Calidad y Cumplimiento NFPA96</p>", unsafe_allow_html=True)

    st.markdown("<h3 style='color: #00d2ff; font-weight: 700;'>🗺️ Direcciones de Cobertura en Google Maps</h3>", unsafe_allow_html=True)
    col_map1, col_map2, col_map3, col_map4 = st.columns(4)
    with col_map1: st.link_button("🗺️ Abrir Google Maps NY", "https://maps.google.com/?q=New+York", use_container_width=True)
    with col_map2: st.link_button("🗺️ Abrir Google Maps NJ", "https://maps.google.com/?q=New+Jersey", use_container_width=True)
    with col_map3: st.link_button("🗺️ Abrir Google Maps CT", "https://maps.google.com/?q=Connecticut", use_container_width=True)
    with col_map4: st.link_button("🗺️ Abrir Google Maps Filadelfia", "https://www.google.com/maps/place/Trenton,+Nueva+Jersey/@40.2161457,-74.8152052,13z/data=!3m1!4b1!4m6!3m5!1s0x89c143482d3dbbb9:0xcf16567f895cd7bc!8m2!3d40.2201787!4d-74.7642295!16zL20vMGZ2eHo?entry=ttu&g_ep=EgoyMDI2MDYwMy4xIKXMDSoASAFQAw%3D%3D", use_container_width=True)
    
    st.markdown("<hr style='border: 1px solid #e0e0e0; margin: 30px 0;'>", unsafe_allow_html=True)

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("""
        <div class="card-modern-blue">
            <h3 style="margin:0; color: #1e3c72; font-weight: 700;">📩 Contact Us - Skyline Official Portal</h3>
            <p style="margin:5px 0 0 0; font-size:13px; color:gray;">Fiel al formato oficial de nuestra web. Déjanos tus datos y te responderemos inmediatamente.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("contacto_oficial_web"):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                contact_first = st.text_input("First Name *")
                contact_email = st.text_input("Email Address *")
            with f_col2:
                contact_last = st.text_input("Last Name *")
                contact_phone = st.text_input("Phone Number")
                
            contact_subject = st.text_input("Subject *")
            contact_msg = st.text_area("Message *", placeholder="Write your project details...")
            
            if st.form_submit_button("✉️ Send Message"):
                if contact_first and contact_last and contact_email and contact_subject and contact_msg:
                    df_contactos_actual = cargar_datos(DB_CONTACTOS, COLS_CONTACTOS)
                    fecha_reg_str = datetime.now().strftime("%m/%d/%Y %I:%M %p")
                    nuevo_contacto_df = pd.DataFrame([[contact_first, contact_last, contact_email, contact_phone if contact_phone else "N/A", contact_subject, contact_msg, fecha_reg_str]], columns=COLS_CONTACTOS)
                    pd.concat([df_contactos_actual, nuevo_contacto_df], ignore_index=True).to_csv(DB_CONTACTOS, index=False)
                    st.success("🎉 Thank you! Your message has been successfully submitted.")
                else:
                    st.error("Please fill in all required fields marked with an asterisk (*).")

    with col_der:
        st.markdown("""
        <div class="card-modern-dark">
            <h3 style="margin:0; color: #00d2ff; font-weight: 700;">💳 Pasarela Digital Seguro y Consulta</h3>
            <p style="margin:5px 0 0 0; font-size:13px; color:#cbd5e0;">Consulta e ingresa tus métodos de pago usando el código permanente de tu ticket.</p>
        </div>
        """, unsafe_allow_html=True)
        
        factura_input = st.text_input("Ingresa el Número de Factura Emitida (Ej: #001200):").strip()
        if factura_input:
            df_facturas_citas = cargar_datos(DB_CITAS, COLS_CITAS)
            datos_fac_list = df_facturas_citas[df_facturas_citas["Id_Factura"] == factura_input]
            if not datos_fac_list.empty:
                datos_fac = datos_fac_list.iloc[0]
                st.markdown(f"**Cliente:** {datos_fac['Cliente']} | **Fecha del Servicio:** {datos_fac['Fecha']}")
                if datos_fac['Estatus'] == "Pendiente":
                    total_base_float = float(datos_fac['Total'])
                    st.warning(f"Monto de Factura Base: **${total_base_float:.2f} USD**")
                    st.markdown("### 🛠️ Selección de Método de Pago")
                    metodo_seleccionado = st.radio("Elige cómo deseas liquidar:", ["Zelle (Sin cargos adicionales)", "Tarjeta de Débito (Sin cargos)", "Tarjeta de Crédito (Sujeto a +3.5% de procesamiento)"])
                    if metodo_seleccionado == "Zelle (Sin cargos adicionales)":
                        st.success(f"Monto Neto a transferir: **${total_base_float:.2f} USD**")
                        st.link_button("📱 Ir a Transferir por Zelle Directo", "https://www.zellepay.com", use_container_width=True)
                        st.caption("Destinatario Oficial Zelle: **skylinehcs@gmail.com** (Por favor añade el número de factura en la nota del envío).")
                    elif metodo_seleccionado == "Tarjeta de Débito (Sin cargos)":
                        st.info(f"Monto Neto a pagar: **${total_base_float:.2f} USD**")
                        st.button("💳 Proceder a ingresar Tarjeta Débito", disabled=True)
                        st.caption("Llama al (862) 882-1802 para procesar de forma inmediata por teléfono con Square.")
                    elif metodo_seleccionado == "Tarjeta de Crédito (Sujeto a +3.5% de procesamiento)":
                        total_con_recargo = total_base_float * 1.035
                        st.error(f"Monto Final Calculado: **${total_con_recargo:.2f} USD**")
                        st.button("💳 Proceder a ingresar Tarjeta Crédito (+3.5%)", disabled=True)
                        st.caption("Cargo por procesamiento externo Square. Llama al (862) 882-1802 para completar la transacción.")
                else:
                    st.success(f"🎉 La Factura `{datos_fac['Id_Factura']}` por **${float(datos_fac['Total']):.2f} USD** ya se encuentra registrada como **PAGADA** mediante {datos_fac['Metodo']}.")
            else:
                st.error("No se localizó ninguna factura bajo ese número correlativo permanente en el historial.")

    st.markdown("<hr style='border: 1px solid #e0e0e0; margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #1e3c72; font-weight:700;'>📸 Servicios en Acción (Recomendado Skyline)</h3>", unsafe_allow_html=True)
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        if os.path.exists(F_ANTES_DESPUES): st.image(F_ANTES_DESPUES, caption="✨ Transformación Real: Antes vs Después NFPA96", use_container_width=True)
        else: st.info("💡 Sube 'trabajo_antes_despues.png'")
    with col_img2:
        if os.path.exists(F_PRESSURE_WASH): st.image(F_PRESSURE_WASH, caption="💧 Hidrolavado a Alta Presión en Ductos y Extractores", use_container_width=True)
        else: st.info("💡 Sube 'limpieza_presion.png'")

    st.markdown("<hr style='border: 1px solid #e0e0e0; margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 25px; color: #2c5364; font-weight:700;'>📇 Contacto Directo y Canales Corporativos</h3>", unsafe_allow_html=True)
    col_ad1, col_ad2, col_ad3 = st.columns(3)
    
    with col_ad1:
        st.markdown("""
        <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; text-align: left; background-color: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.04); min-height: 240px; font-family: 'Arial', sans-serif;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="color: #2d3748; margin: 0; font-size: 20px; font-weight: bold;">Max Liranzo</h4>
                <span style="background-color: #ebf8ff; color: #2b6cb0; font-size: 11px; padding: 3px 8px; border-radius: 12px; font-weight: bold;">General Manager</span>
            </div>
            <p style="color: #4a5568; font-size: 14px; font-weight: bold; margin: 4px 0 12px 0;">💎 Skyline Hood Cleaning Services</p>
            <hr style="border: 0; border-top: 1px solid #edf2f7; margin: 10px 0;">
            <p style="margin: 6px 0; font-size: 13.5px; color: #4a5568;">📞 <b>Phone:</b> <a href="tel:8622797229" style="color: #3182ce; text-decoration: none;">862-279-7229</a></p>
            <p style="margin: 6px 0; font-size: 13.5px; color: #4a5568;">✉️ <b>Email:</b> skylinehcs@gmail.com</p>
            <p style="margin: 6px 0; font-size: 13.5px; color: #4a5568;">📍 1000 Lafayette Blvd, Bridgeport, CT 06604</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_ad2:
        st.markdown("""
        <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; text-align: left; background-color: #1a202c; box-shadow: 0 4px 12px rgba(0,0,0,0.08); min-height: 240px; color: #ffffff; font-family: 'Arial', sans-serif;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: bold;">David Liranzo</h4>
                <span style="background-color: #2d3748; color: #e2e8f0; font-size: 11px; padding: 3px 8px; border-radius: 12px; font-weight: bold;">Office Admin</span>
            </div>
            <p style="color: #63b3ed; font-size: 14px; font-weight: bold; margin: 4px 0 12px 0;">💎 Skyline Hood Cleaning Services</p>
            <hr style="border: 0; border-top: 1px solid #4a5568; margin: 10px 0;">
            <p style="margin: 6px 0; font-size: 13.5px; color: #e2e8f0;">📞 <b>Office:</b> <a href="tel:8628821802" style="color: #63b3ed; text-decoration: none;">862-882-1802</a></p>
            <p style="margin: 6px 0; font-size: 13.5px; color: #e2e8f0;">✉️ <b>Email:</b> skylinehcs@gmail.com</p>
            <p style="margin: 6px 0; font-size: 13.5px; color: #cbd5e0;">🌐 www.skylinehoodcleanings.com</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_ad3:
        st.markdown("""
        <div style="border: 2px dashed #3182ce; border-radius: 12px; padding: 22px; text-align: center; background-color: #f7fafc; box-shadow: 0 4px 12px rgba(0,0,0,0.02); min-height: 240px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: 'Arial', sans-serif;">
            <h4 style="color: #2b6cb0; margin: 0 0 8px 0; font-size: 17px; font-weight: bold; text-transform: uppercase;">🌐 Canal Web Oficial</h4>
            <p style="color: #718096; font-size: 13px; margin: 0 0 15px 0; line-height: 1.4;">Accede directo al portal central de operaciones de la compañía Skyline.</p>
            <a href="http://www.skylinehoodcleanings.com" target="_blank" style="background-color: #3182ce; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13.5px; display: inline-block; box-shadow: 0 2px 5px rgba(49,130,206,0.3);">Visitar Sitio Web</a>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border: 1px solid #e0e0e0; margin: 30px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 25px; color: #2c5364; font-weight:700;'>📸 Galería de Equipos Certificados</h3>", unsafe_allow_html=True)
    cols_fotos = st.columns(4)
    for col, (r, cap) in zip(cols_fotos, [(F_FILTROS, "Filtros Comerciales"), (F_FANS, "Fan de Extracción"), (F_MOTORES, "Motores Eléctricos"), (F_CORREAS, "Correas de Distribución")]):
        if os.path.exists(r): col.image(r, caption=cap, use_container_width=True)

# --- CALCULADORA DE CAMPO ---
elif menu == "Calculadora de Campo":
    st.header("🧮 Calculadora Skyline para Empleados")
    
    with st.form("calc_form"):
        col1, col2 = st.columns(2)
        with col1:
            q_estado = st.selectbox("Estado:", list(TAX_RATES.keys()))
            q_piso = st.selectbox("Piso:", [str(i) for i in range(1, 15)])
            q_filtros = st.number_input("Cantidad de Filtros:", min_value=2, value=3)
            q_campanas = st.number_input("Hoods Totales:", min_value=1, value=1)
        with col2:
            q_abanicos = st.number_input("Abanicos Totales:", min_value=1, value=1)
            q_ductos = st.number_input("Ductos Totales:", min_value=1, value=1)
            q_desc = st.selectbox("Descuento Cliente:", ["0%", "10%", "15%", "20%", "25%"])
            
        btn_calc = st.form_submit_button("CALCULAR TOTAL", type="primary")

    if btn_calc:
        tasa_tax = TAX_RATES[q_estado]
        porcentaje_desc = float(q_desc.replace('%', '')) / 100

        if q_filtros == 2: precio_objetivo = 408.00
        elif q_filtros == 3: precio_objetivo = 435.50
        elif q_filtros == 4: precio_objetivo = 435.50
        elif q_filtros == 5: precio_objetivo = 440.00
        elif q_filtros == 6: precio_objetivo = 450.00
        elif q_filtros == 7: precio_objetivo = 463.80
        elif q_filtros == 8: precio_objetivo = 480.80
        elif q_filtros == 9: precio_objetivo = 500.00
        elif q_filtros == 10: precio_objetivo = 500.50
        elif q_filtros == 11: precio_objetivo = 515.50
        elif q_filtros == 12: precio_objetivo = 550.50
        elif q_filtros == 13: precio_objetivo = 550.00
        elif q_filtros == 14: precio_objetivo = 580.00
        elif q_filtros == 15: precio_objetivo = 600.00
        elif q_filtros == 16: precio_objetivo = 650.00
        elif q_filtros == 17: precio_objetivo = 660.00
        elif q_filtros == 18: precio_objetivo = 700.00
        elif q_filtros == 19: precio_objetivo = 800.00
        elif q_filtros == 20: precio_objetivo = 850.00
        elif q_filtros == 21: precio_objetivo = 900.00
        elif 22 <= q_filtros <= 26: precio_objetivo = 1200.00
        elif 27 <= q_filtros <= 30: precio_objetivo = 1300.00
        elif 31 <= q_filtros <= 37: precio_objetivo = 1450.00
        else: precio_objetivo = 1450.00 + ((q_filtros - 37) * 40.00)

        base_filtros = precio_objetivo / (1 + tasa_tax)
        extras_campana = (q_campanas - 1) * 35.00 if q_campanas > 1 else 0.0
        extras_abanico = (q_abanicos - 1) * 45.00 if q_abanicos > 1 else 0.0
        
        if q_ductos <= 1: extras_ducto = 0.0
        elif q_ductos == 2: extras_ducto = 20.0
        elif q_ductos == 3: extras_ducto = 40.0
        elif q_ductos == 4: extras_ducto = 55.0
        else: extras_ducto = 65.0 + ((q_ductos - 5) * 15.0)
        
        extras_total = extras_campana + extras_abanico + extras_ducto
        subtotal = base_filtros + extras_total
        
        recargo_piso = subtotal * 0.15 if int(q_piso) >= 3 else 0.0
        base_con_recargo = subtotal + recargo_piso
        
        valor_descuento = base_con_recargo * porcentaje_desc
        base_final = base_con_recargo - valor_descuento
        
        tax_final = base_final * tasa_tax
        total = base_final + tax_final

        st.markdown("---")
        st.markdown("### 🧾 Resumen de Cotización")
        st.write(f"**Precio Base Filtros:** ${base_filtros:.2f}")
        st.write(f"**Cargos Adicionales:** ${extras_total:.2f}")
        if int(q_piso) >= 3: st.write(f"**Recargo Piso ({q_piso}º) [+15%]:** ${recargo_piso:.2f}")
        if valor_descuento > 0: st.markdown(f"**Descuento Cliente:** :red[-${valor_descuento:.2f}]")
        st.write(f"**Tax ({q_estado}):** ${tax_final:.2f}")
        st.markdown(f"<h2 style='color: #0f766e;'>TOTAL NETO: ${total:.2f}</h2>", unsafe_allow_html=True)

# --- CHAT CON SOPORTE ---
elif menu == "💬 Chat con Soporte":
    st.title("💬 Chat con Skyline Hood Cleaning Services")
    df_chat = cargar_datos(DB_CHAT, COLS_CHAT)
    nombre_cliente = st.text_input("Tu nombre")
    mensaje = st.text_area("Escribe tu mensaje")
    if st.button("Enviar Mensaje"):
        if nombre_cliente and mensaje:
            nuevo = pd.DataFrame([[datetime.now().strftime("%m/%d/%Y %I:%M %p"), nombre_cliente, mensaje]], columns=COLS_CHAT)
            pd.concat([df_chat, nuevo], ignore_index=True).to_csv(DB_CHAT, index=False)
            st.success("Mensaje enviado correctamente")
            st.rerun()
    st.markdown("---")
    st.subheader("Mensajes")
    if not df_chat.empty:
        for _, row in reversed(list(df_chat.iterrows())):
            with st.chat_message("user"):
                st.write(f"**{row['Nombre']}**")
                st.write(row['Mensaje'])
                st.caption(row['Fecha'])

# --- ÁREA ADMINISTRATIVA ---
elif menu == "🔒 Área Administrativa" and not st.session_state.logged_in:
    st.title("🔐 Acceso Administrativo - Skyline")
    st.markdown("Ingresa tus credenciales para desbloquear las herramientas internas de gestión.")
    u_in = st.text_input("Usuario")
    p_in = st.text_input("Contraseña", type="password")
    
    if st.button("🔓 Desbloquear Panel"):
        df_u = cargar_datos(DB_USUARIOS, ["Usuario", "Pass", "Rol"])
        if u_in == "admin" and p_in == "skyline2026":
            st.session_state.logged_in = True
            st.session_state.user = "admin"
            st.session_state.rol = "Admin"
            st.session_state.login_time = datetime.now()
            if df_u.empty:
                pd.DataFrame([["admin", "skyline2026", "Admin"]], columns=["Usuario", "Pass", "Rol"]).to_csv(DB_USUARIOS, index=False)
            st.success("¡Sesión iniciada como Admin Maestro!")
            st.rerun()
            
        user = df_u[df_u["Usuario"] == u_in]
        if not user.empty and user.iloc[0]["Pass"] == p_in:
            st.session_state.logged_in = True
            st.session_state.user = u_in
            st.session_state.rol = user.iloc[0]["Rol"]
            st.session_state.login_time = datetime.now()
            st.success(f"¡Bienvenido de vuelta, {u_in}!")
            st.rerun()
        else:
            st.error("Credenciales de acceso incorrectas. Vuelve a intentarlo.")

# --- DIRECTOR DEL PANEL ---
elif menu == "Director del panel" and st.session_state.logged_in:
    st.header("📊 Director del Panel (Métricas y Estatus)")
    tab_resumen, tab_respaldos = st.tabs(["📊 Resumen de Flujos", "📦 Respaldos del Sistema"])
    with tab_resumen:
        verificar_alertas_limpieza()
        df_cit_p = cargar_datos(DB_CITAS, COLS_CITAS)
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1: st.metric("Citas Pendientes de Cobro", len(df_cit_p[df_cit_p["Estatus"] == "Pendiente"]))
        with c_p2: st.metric("Servicios Liquidados", len(df_cit_p[df_cit_p["Estatus"] == "Pagado"]))
        with c_p3:
            total_recaudado = df_cit_p[df_cit_p["Estatus"] == "Pagado"]["Total"].astype(float).sum()
            st.metric("Total Recaudado ($)", f"${total_recaudado:.2f}")
        st.markdown("### Resumen Ejecutivo de Flujos")
        st.dataframe(df_cit_p, use_container_width=True)
    with tab_respaldos:
        st.markdown("### 🗄️ Sistema Seguro de Respaldos de SkylineApp")
        archivos_sistema = {
            "👥 Clientes Registrados": (DB_CLIENTES, ["Nombre_Restaurante", "Telefono_Restaurante", "Direccion_Restaurante", "Nombre_Manager", "Telefono_Manager", "Estado"]),
            "📅 Historial de Citas y Facturas": (DB_CITAS, COLS_CITAS),
            "📦 Inventario de Bodega": (DB_INVENTARIO, ["Material", "Cantidad", "Detalles"]),
            "📩 Solicitudes de Contacto / Leads": (DB_CONTACTOS, COLS_CONTACTOS),
            "🔑 Usuarios del Sistema": (DB_USUARIOS, ["Usuario", "Pass", "Rol"])
        }
        for label, (ruta, cols) in archivos_sistema.items():
            if os.path.exists(ruta):
                df_respaldo = cargar_datos(ruta, cols)
                csv_buffer = io.StringIO()
                df_respaldo.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                nombre_archivo_descarga = os.path.basename(ruta).replace(".csv", f"_backup_{date.today().strftime('%m_%d_%Y')}.csv")
                st.download_button(label=f"📥 Descargar Respaldo: {label}", data=csv_data, file_name=nombre_archivo_descarga, mime="text/csv", key=f"btn_backup_{ruta}")

# --- CLIENTES ---
elif menu == "Clientes" and st.session_state.logged_in:
    st.header("👥 Gestión de Clientes")
    cols = ["Nombre_Restaurante", "Telefono_Restaurante", "Direccion_Restaurante", "Nombre_Manager", "Telefono_Manager", "Estado"]
    df = cargar_datos(DB_CLIENTES, cols)
    with st.form("c_form"):
        st.markdown("### 🏢 Datos del Establecimiento")
        nr = st.text_input("Nombre del Restaurante")
        tr = st.text_input("Teléfono del Restaurante")
        dr = st.text_input("Dirección del Restaurante")
        st.markdown("### 👤 Datos del Manager / Contacto")
        nm = st.text_input("Nombre del Manager")
        tm = st.text_input("Teléfono del Manager")
        e = st.selectbox("Estado", list(TAX_RATES.keys()))
        if st.form_submit_button("💾 Guardar Cliente"):
            if nr and dr:
                nuevo_cliente = pd.DataFrame([[nr, tr, dr, nm, tm, e]], columns=cols)
                pd.concat([df, nuevo_cliente]).to_csv(DB_CLIENTES, index=False)
                st.success(f"¡Cliente '{nr}' guardado con éxito!")
                st.rerun()
            else:
                st.error("Por favor completa al menos el Nombre y la Dirección.")
    st.markdown("### 📋 Clientes Registrados")
    st.dataframe(df)

# --- CITAS ---
elif menu == "Citas" and st.session_state.logged_in:
    st.header("📅 Agenda de Citas")
    df_cli = cargar_datos(DB_CLIENTES, ["Nombre_Restaurante", "Estado"])
    df_cit = cargar_datos(DB_CITAS, COLS_CITAS)
    t1, t2, t3 = st.tabs(["Agendar", "Pendientes", "Pagados"])
    with t1:
        if not df_cli.empty:
            with st.form("a_form"):
                cli_n = st.selectbox("Cliente (Restaurante)", df_cli["Nombre_Restaurante"].tolist())
                cliente_sel = df_cli[df_cli["Nombre_Restaurante"] == cli_n]
                estado_defecto = cliente_sel["Estado"].values[0] if not cliente_sel.empty else list(TAX_RATES.keys())[0]
                idx_defecto = list(TAX_RATES.keys()).index(estado_defecto) if estado_defecto in TAX_RATES else 0
                c1, c2 = st.columns(2)
                with c1:
                    campanas = st.number_input("Campanas", 0)
                    filtros = st.number_input("Filtros", 0)
                    fecha_cita = st.date_input("Fecha", format="MM/DD/YYYY")
                    frecuencia = st.selectbox("🔁 ¿Cada cuántos meses se debe limpiar este restaurante?", options=list(range(1, 13)), index=2, format_func=lambda x: f"Cada {x} mes" if x == 1 else f"Cada {x} meses")
                with c2:
                    abanico = st.number_input("Abanico Extractor de Techo", 0)
                    ductos = st.number_input("Ductos", 0)
                    st.markdown("<p style='margin-bottom:0px; font-weight:bold;'>Hora de la Cita (12h Format):</p>", unsafe_allow_html=True)
                    col_h1, col_h2, col_h3 = st.columns(3)
                    with col_h1: h_hour = st.selectbox("Hora", [f"{i:02d}" for i in range(1, 13)], index=7)
                    with col_h2: h_min = st.selectbox("Minuto", [f"{i:02d}" for i in range(0, 60, 5)], index=0)
                    with col_h3: h_ampm = st.selectbox("AM/PM", ["AM", "PM"], index=0)
                rep = st.text_input("Reparación")
                col_b1, col_b2 = st.columns(2)
                with col_b1: base = st.number_input("Monto Base ($)", 0.0)
                with col_b2: tax_elegido = st.selectbox("Seleccionar Tax Rate aplicable:", list(TAX_RATES.keys()), index=idx_defecto)
                notas = st.text_area("Notas Especiales")
                total = base * (1 + TAX_RATES[tax_elegido])
                if st.form_submit_button("Agendar"):
                    fecha_str = fecha_cita.strftime("%m/%d/%Y")
                    hora_str = f"{h_hour}:{h_min} {h_ampm}"
                    factura_id_generado = f"#00{1200 + len(df_cit)}"
                    nueva_cita = pd.DataFrame([[cli_n, tax_elegido, campanas, filtros, abanico, ductos, rep, base, total, "Pendiente", "N/A", fecha_str, hora_str, notas, "N/A", factura_id_generado, frecuencia]], columns=COLS_CITAS)
                    pd.concat([df_cit, nueva_cita], ignore_index=True).to_csv(DB_CITAS, index=False)
                    st.success(f"Cita agendada correctamente. Factura asignada: {factura_id_generado}")
                    st.rerun()
        else:
            st.warning("Primero debes registrar un cliente.")
    with t2:
        st.markdown("### Citas en Estatus Pendiente")
        pend = df_cit[df_cit["Estatus"] == "Pendiente"]
        for i, row in pend.iterrows():
            id_fac_mostrar = row.get('Id_Factura', f"#00{1200 + i}")
            with st.expander(f"📄 Factura {id_fac_mostrar} - {row['Cliente']} - ${float(row['Total']):.2f} ({row['Fecha']})"):
                if st.session_state.rol == "Tecnico":
                    st.info("Visualización de Técnico: No tienes permisos para alterar el estatus.")
                else:
                    met = st.selectbox("Forma de Pago Recibida:", ["Zelle", "Cheque", "Efectivo"], key=f"m{i}")
                    if st.button("Marcar Pagado ✔️", key=f"b{i}"):
                        df_cit.at[i, "Estatus"] = "Pagado"
                        df_cit.at[i, "Metodo"] = met
                        df_cit.at[i, "Hora_Pago"] = datetime.now().strftime("%m/%d/%Y %I:%M %p")
                        if not row['Id_Factura'] or str(row['Id_Factura']) == "N/A": df_cit.at[i, "Id_Factura"] = f"#00{1200 + i}"
                        df_cit.to_csv(DB_CITAS, index=False)
                        st.success("¡Estatus actualizado a Pagado!")
                        st.rerun()
        st.dataframe(pend)
    with t3: 
        st.markdown("### 🗂️ Descargar Facturas Emitidas (Square Model)")
        pag = df_cit[df_cit["Estatus"] == "Pagado"]
        if not pag.empty:
            for i, row in pag.iterrows():
                id_fac_final = row.get('Id_Factura', f"#00{1200 + i}")
                with st.expander(f"🧾 Factura Comercial Real: {id_fac_final} - {row['Cliente']} - ${float(row['Total']):.2f}"):
                    try:
                        row_dict = row.to_dict()
                        if 'Id_Factura' not in row_dict or row_dict['Id_Factura'] == "N/A": row_dict['Id_Factura'] = id_fac_final
                        ruta_factura_pdf = generar_factura_pdf(row_dict, i)
                        with open(ruta_factura_pdf, "rb") as file_data:
                            st.download_button(label=f"📥 Descargar Factura {id_fac_final}", data=file_data, file_name=f"Invoice_Skyline_{id_fac_final}.pdf", mime="application/pdf", key=f"dl_invoice_btn_{i}")
                    except Exception as err_pdf:
                        st.error(f"Error al compilar PDF: {err_pdf}")
        else:
            st.info("No hay facturas pagadas registradas por el momento.")
        st.dataframe(pag)

# --- INVENTARIO ---
elif menu == "Inventario" and st.session_state.logged_in:
    st.header("📦 Control de Inventario y Almacén Digital")
    cols_inv = ["Material", "Cantidad", "Detalles"]
    cols_entregas = ["Material", "Cantidad", "Entregado_A", "Fecha_Hora"]
    df_inv = cargar_datos(DB_INVENTARIO, cols_inv)
    df_entregas = cargar_datos(DB_ENTREGAS_INVENTARIO, cols_entregas)
    t_stock, t_alta, t_baja, t_historial = st.tabs(["📋 Stock Actual", "➕ Agregar Stock", "➖ Registrar Entrega (Descontar)", "📜 Historial de Salidas"])
    with t_stock:
        st.dataframe(df_inv, use_container_width=True)
    with t_alta:
        with st.form("inv_form"):
            mat = st.text_input("Nombre del Material o Herramienta")
            cant = st.number_input("Cantidad a Ingresar", min_value=0, value=0, step=1)
            det = st.text_input("Detalles adicionales / Notas")
            if st.form_submit_button("Guardar en Stock"):
                if mat and cant > 0:
                    if mat in df_inv["Material"].values:
                        df_inv.loc[df_inv["Material"] == mat, "Cantidad"] += cant
                        df_inv.loc[df_inv["Material"] == mat, "Detalles"] = det
                    else:
                        nuevo_item = pd.DataFrame([[mat, cant, det]], columns=cols_inv)
                        df_inv = pd.concat([df_inv, nuevo_item], ignore_index=True)
                    df_inv.to_csv(DB_INVENTARIO, index=False)
                    st.success(f"Se añadieron {cant} unidades.")
                    st.rerun()
    with t_baja:
        with st.form("baja_form"):
            if not df_inv.empty:
                mat_sel = st.selectbox("Seleccione Material:", df_inv["Material"].tolist())
                cant_baja = st.number_input("Cantidad a Retirar", min_value=1, value=1, step=1)
                tecnico = st.text_input("Entregado a:")
                if st.form_submit_button("Confirmar Salida"):
                    stock_actual = df_inv.loc[df_inv["Material"] == mat_sel, "Cantidad"].values[0]
                    if tecnico and cant_baja <= stock_actual:
                        df_inv.loc[df_inv["Material"] == mat_sel, "Cantidad"] -= cant_baja
                        df_inv.to_csv(DB_INVENTARIO, index=False)
                        f_hora = datetime.now().strftime("%m/%d/%Y %I:%M %p")
                        nueva_entrega = pd.DataFrame([[mat_sel, cant_baja, tecnico, f_hora]], columns=cols_entregas)
                        pd.concat([df_entregas, nueva_entrega], ignore_index=True).to_csv(DB_ENTREGAS_INVENTARIO, index=False)
                        st.success(f"Entrega de {cant_baja} unidades registrada.")
                        st.rerun()
                    else:
                        st.error("Verifica el stock disponible.")
    with t_historial:
        st.dataframe(df_entregas, use_container_width=True)

# --- SOLICITUDES RECIBIDAS ---
elif menu == "Solicitudes Recibidas" and st.session_state.logged_in:
    st.header("📩 Solicitudes Recibidas (Mensajes del Formulario de Contacto)")
    st.dataframe(cargar_datos(DB_CONTACTOS, COLS_CONTACTOS), use_container_width=True)

# --- GENERAR INFORME ---
elif menu == "Generar informe" and st.session_state.logged_in:
    st.header("📄 Generar Reporte Técnico de Inspección KEC")
    df_cit_p = cargar_datos(DB_CITAS, COLS_CITAS)
    df_pagadas = df_cit_p[df_cit_p["Estatus"] == "Pagado"]
    if not df_pagadas.empty:
        cli_rep = st.selectbox("Seleccione el Cliente Liquidado para el Reporte:", df_pagadas["Cliente"].unique().tolist())
        datos_c_cita = df_pagadas[df_pagadas["Cliente"] == cli_rep].iloc[-1]
        if "reporte_listo" not in st.session_state:
            st.session_state.reporte_listo = False
            st.session_state.ruta_reporte = ""
            st.session_state.cliente_reporte = ""
        with st.form("form_reporte"):
            inputs_reporte = {}
            inputs_reporte['direccion'] = st.text_input("Dirección Completa del Establecimiento:")
            inputs_reporte['time_silas'] = st.text_input("Tiempo / Horas Trabajadas (Ej: 4 Hours):", "4 Hours")
            inputs_reporte['contacto'] = st.text_input("Persona de Contacto en sitio:")
            inputs_reporte['service_term'] = st.selectbox("Frecuencia del Término de Servicio:", ["Quarterly", "Semi-Annual", "Annual", "Monthly"])
            inputs_reporte['contact_info'] = st.text_input("Teléfono o Email de Contacto:")
            inputs_reporte['last_service'] = st.date_input("Fecha de Último Servicio Anterior:", value=None)
            inputs_reporte['next_service'] = st.date_input("Fecha Programada Próximo Servicio:")
            inputs_reporte['location'] = st.text_input("Ubicación del Sistema:", "Roof")
            inputs_reporte['grease_load'] = st.selectbox("Nivel de Carga de Grasa:", ["Light", "Medium", "Heavy"])
            inputs_reporte['condition'] = st.selectbox("Condición General:", ["Good", "Fair", "Poor"])
            inputs_reporte['lights'] = st.selectbox("Luces y Globos de Campana Completos?:", ["Yes", "No", "Needs Replacement"])
            inputs_reporte['collector'] = st.selectbox("Colector de Grasa Instalado?:", ["Yes", "No"])
            inputs_reporte['hinged'] = st.selectbox("Extractor con Bisagras (Hinged)?:", ["Yes", "No"])
            inputs_reporte['appliances'] = st.selectbox("Equipos Pilotos Desconectados antes de lavar?:", ["Yes", "No"])
            inputs_reporte['gas_pilots'] = st.selectbox("Estado de Pilotos de Gas al terminar:", ["Turned On", "Left Off / Main Closed"])
            inputs_reporte['roof_access'] = st.selectbox("Acceso Seguro al Techo disponible?:", ["Yes", "No"])
            inputs_reporte['duct_grease'] = st.selectbox("Nivel de Grasa Interno en Ductos:", ["Low", "Medium", "High"])
            inputs_reporte['leaks'] = st.selectbox("Fugas de Grasa Visibles en Estructura?:", ["None Seen", "Yes, minor Leaks"])
            
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                inputs_reporte['f25x16'] = st.number_input("Cant. Filtros 25x16:", 0)
                inputs_reporte['f20x16'] = st.number_input("Cant. Filtros 20x16:", 0)
                inputs_reporte['f16x16'] = st.number_input("Cant. Filtros 16x16:", 0)
            with fc2:
                inputs_reporte['f25x20'] = st.number_input("Cant. Filtros 25x20:", 0)
                inputs_reporte['f20x20'] = st.number_input("Cant. Filtros 20x20:", 0)
                inputs_reporte['f16x20'] = st.number_input("Cant. Filtros 16x20:", 0)
            with fc3:
                inputs_reporte['f25x25'] = st.number_input("Cant. Filtros 25x25:", 0)
                inputs_reporte['f20x25'] = st.number_input("Cant. Filtros 20x25:", 0)
                inputs_reporte['f16x25'] = st.number_input("Cant. Filtros 16x25:", 0)
                
            inputs_reporte['filter_company'] = st.selectbox("Filtros pertenecen a Compañía Externa?:", ["No, Customer owned", "Yes"])
            inputs_reporte['filter_action'] = st.selectbox("Acción tomada con los Filtros:", ["Cleaned on site", "Swapped completely"])
            inputs_reporte['post_free'] = st.selectbox("Área libre de grasa al retirarse?:", ["Yes", "No"])
            inputs_reporte['post_sticker'] = st.selectbox("Sticker actualizado en la Campana?:", ["Yes", "No"])
            inputs_reporte['post_reconnected'] = st.selectbox("Equipos reconectados?:", ["Yes", "No"])
            inputs_reporte['post_gas'] = st.selectbox("Pilotos de Gas funcionando?:", ["Yes", "No, left off safely"])
            inputs_reporte['post_photos'] = st.selectbox("Fotos de Evidencia completado?:", ["Yes", "No"])
            inputs_reporte['post_inaccessible'] = st.text_input("Zonas Inaccesibles informadas:", "None")
            inputs_reporte['services_done'] = st.text_input("Servicios ejecutados (Resumen):", "Commercial Hood Cleaning / NFPA96 Certified")
            inputs_reporte['comments'] = st.text_area("Comentarios Profesionales:", "System is operating up to NFPA96 standards. Next service scheduled accordingly.")
            inputs_reporte['serviced_by'] = st.text_input("Técnicos Certificados a cargo:", "Skyline Team")
            inputs_reporte['no_one_sign'] = st.checkbox("Marque aquí si NO había personal para firmar", value=False)
            
            if st.form_submit_button("🏭 Compilar Datos del Reporte Técnico"):
                try:
                    ruta_reporte_pdf = generar_pdf_exacto(datos_c_cita, inputs_reporte)
                    st.session_state.reporte_listo = True
                    st.session_state.ruta_reporte = ruta_reporte_pdf
                    st.session_state.cliente_reporte = cli_rep
                except Exception as e_rep:
                    st.error(f"Error al generar el Reporte Técnico: {e_rep}")
        if st.session_state.reporte_listo and st.session_state.cliente_reporte == cli_rep:
            st.success("🎉 ¡Los datos del reporte KEC se compilaron con éxito!")
            with open(st.session_state.ruta_reporte, "rb") as rep_data:
                st.download_button(label="📥 DESCARGAR REPORTE PDF OFICIAL KEC", data=rep_data, file_name=f"KEC_Report_{cli_rep.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.info("Aún no tienes citas con Estatus 'Pagado'.")

# --- CALENDARIO DE GOOGLE ---
elif menu == "Calendario de Google" and st.session_state.logged_in:
    st.header("🗓️ Sincronización con Google Calendar")
    st.link_button("🌐 Ir a Google Calendar (Skyline HCS)", "https://calendar.google.com/calendar/u/5?cid=c2t5bGluZWhjcy5jdEBnbWFpbC5jb20", use_container_width=True)

# --- GESTIÓN DE USUARIOS ---
elif menu == "Gestión Usuarios" and st.session_state.rol == "Admin" and st.session_state.logged_in:
    st.header("⚙️ Configuración y Control de Usuarios")
    df_u = cargar_datos(DB_USUARIOS, ["Usuario", "Pass", "Rol"])
    with st.form("u_form"):
        st.markdown("### Crear Nuevo Perfil de Acceso")
        nu = st.text_input("Nombre de Usuario")
        np = st.text_input("Contraseña del Perfil")
        nr = st.selectbox("Rol Asignado", ["Admin", "Tecnico"])
        if st.form_submit_button("🔑 Registrar Cuenta"):
            if nu and np:
                nuevo_u = pd.DataFrame([[nu, np, nr]], columns=["Usuario", "Pass", "Rol"])
                pd.concat([df_u, nuevo_u]).to_csv(DB_USUARIOS, index=False)
                st.success(f"Usuario '{nu}' registrado.")
                st.rerun()
    st.markdown("### Cuentas Activas")
    st.dataframe(df_u)
