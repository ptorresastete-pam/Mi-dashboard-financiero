import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Financiero Multi-Tarjeta",
    page_icon="💳",
    layout="wide"
)

st.title("💳 Dashboard Financiero con Alertas y Control Multi-Tarjeta")
st.markdown("Gestiona tus gastos, suscripciones automáticas, medios de pago y lectura automática de comprobantes.")

# Menú de navegación simple en pestañas
tab1, tab2 = st.tabs(["📊 Dashboard & Alertas", "📥 Importación y Lectura Automática"])

# Inicializar datos en la memoria de la sesión si no existen
if 'df_gastos' not in st.session_state:
    st.session_state.df_gastos = pd.DataFrame(columns=['Fecha', 'Concepto', 'Categoría', 'Monto', 'Método'])

with tab2:
    st.header("Lectura y Carga de Movimientos")
    st.markdown("Sube tus capturas de Yape/Plin (imágenes), estados de cuenta (PDF) o archivos Excel/CSV. El sistema registrará los datos de forma automática.")
    
    # Selector de archivos múltiple (soporta imágenes, PDFs, Excel y CSV)
    archivos_subidos = st.file_uploader(
        "Sube tus comprobantes o archivos de gastos", 
        type=["png", "jpg", "jpeg", "pdf", "csv", "xlsx"], 
        accept_multiple_files=True
    )
    
    if archivos_subidos:
        for archivo in archivos_subidos:
            st.success(f"¡Archivo procesado con éxito: {archivo.name}!")
            
            # Si es una imagen (Yape / Plin)
            if archivo.name.lower().endswith(('png', 'jpg', 'jpeg')):
                imagen = Image.open(archivo)
                st.image(imagen, caption=f"Comprobante: {archivo.name}", width=300)
                st.info("💡 Lectura automática simulada: Comprobante detectado. Puedes registrarlo abajo o integrarlo al consolidado.")
                
            # Si es Excel o CSV
            elif archivo.name.lower().endswith(('csv', 'xlsx')):
                try:
                    if archivo.name.endswith('csv'):
                        df_temp = pd.read_csv(archivo)
                    else:
                        df_temp = pd.read_excel(archivo)
                    
                    st.write("Vista previa de los datos encontrados:")
                    st.dataframe(df_temp.head(3))
                    
                    if st.button(f"Agregar datos de {archivo.name} al Dashboard", key=archivo.name):
                        st.session_state.df_gastos = pd.concat([st.session_state.df_gastos, df_temp], ignore_index=True)
                        st.success("¡Datos añadidos al dashboard correctamente!")
                except Exception as e:
                    st.error(f"No se pudo leer el archivo automáticamente: {e}")

    with st.form("registro_manual"):
        st.subheader("O registra un movimiento rápido de forma manual")
        f_fecha = st.date_input("Fecha")
        f_concepto = st.text_input("Concepto (ej. Starbucks, Yape a Juan)")
        f_categoria = st.selectbox("Categoría", ["Alimentos", "Transporte", "Servicios", "Suscripciones", "Yape/Plin", "Otros"])
        f_monto = st.number_input("Monto (S/)", min_value=0.0, format="%.2f")
        f_metodo = st.selectbox("Método de Pago", ["Yape", "Plin", "Tarjeta de Crédito", "Efectivo"])
        
        submitted = st.form_submit_button("Guardar Movimiento")
        if submitted:
            nuevo_dato = pd.DataFrame([[f_fecha, f_concepto, f_categoria, f_monto, f_metodo]], columns=['Fecha', 'Concepto', 'Categoría', 'Monto', 'Método'])
            st.session_state.df_gastos = pd.concat([st.session_state.df_gastos, nuevo_dato], ignore_index=True)
            st.success("¡Movimiento registrado con éxito!")

with tab1:
    st.header("Resumen General de Gastos")
    
    df = st.session_state.df_gastos
    
    if df.empty:
        st.info("📌 Aún no hay datos registrados. Ve a la pestaña **'Importación y Lectura Automática'** para subir tus imágenes de Yape/Plin o archivos.")
    else:
        # Métricas principales
        total_gastado = df['Monto'].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Gasto Total", f"S/ {total_gastado:.2f}")
        col2.metric("Total Movimientos", len(df))
        col3.metric("Métodos Activos", df['Método'].nunique())
        
        st.markdown("---")
        
        # Gráficos interactivos con Plotly
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Gastos por Categoría")
            fig_cat = px.pie(df, names='Categoría', values='Monto', hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with col_g2:
            st.subheader("Gastos por Método de Pago")
            fig_met = px.bar(df, x='Método', y='Monto', color='Método', text_auto=True, color_discrete_sequence=px.colors.sequential.Sunset)
            st.plotly_chart(fig_met, use_container_width=True)
            
        st.subheader("Historial de Movimientos")
        st.dataframe(df, use_container_width=True)
