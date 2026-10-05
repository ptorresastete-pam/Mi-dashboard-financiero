import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Financiero Personal Avanzado",
    page_icon="💳",
    layout="wide",
)

ARCHIVO_DATOS = "datos_gastos.csv"
ARCHIVO_PRESUPUESTOS = "presupuestos.csv"
ARCHIVO_TARJETAS = "tarjetas.csv"


def cargar_datos():
  try:
    return pd.read_csv(ARCHIVO_DATOS)
  except FileNotFoundError:
    df = pd.DataFrame(
        columns=[
            "Fecha",
            "Tipo",
            "Categoria",
            "Descripcion",
            "Monto",
            "Medio_Pago",
            "Detalle_Tarjeta",
            "Es_Suscripcion",
        ]
    )
    df.to_csv(ARCHIVO_DATOS, index=False)
    return df


def cargar_presupuestos():
  try:
    return pd.read_csv(ARCHIVO_PRESUPUESTOS)
  except FileNotFoundError:
    df = pd.DataFrame({
        "Categoria": [
            "Alimentación",
            "Servicios",
            "Transporte",
            "Entretenimiento",
            "Compras",
            "Otros",
        ],
        "Presupuesto": [1200.0, 500.0, 400.0, 300.0, 600.0, 200.0],
    })
    df.to_csv(ARCHIVO_PRESUPUESTOS, index=False)
    return df


def cargar_tarjetas():
  try:
    return pd.read_csv(ARCHIVO_TARJETAS)
  except FileNotFoundError:
    df = pd.DataFrame(
        {
            "Nombre_Tarjeta": [
                "Tarjeta Principal (Débito/Crédito)",
                "Visa BCP (Ejemplo)",
            ]
        }
    )
    df.to_csv(ARCHIVO_TARJETAS, index=False)
    return df


df = cargar_datos()
df_presupuestos = cargar_presupuestos()
df_tarjetas = cargar_tarjetas()

st.title("💳 Dashboard Financiero con Alertas y Control Multi-Tarjeta")
st.markdown(
    "Gestiona tus gastos, suscripciones automáticas, medios de pago y alertas"
    " inteligentes."
)

pestana1, pestana2, pestana3, pestana4, pestana5 = st.tabs([
    "📈 Dashboard & Alertas",
    "📥 Importar Excel / CSV",
    "➕ Registro Manual",
    "🎯 Control de Presupuestos",
    "⚙️ Configurar Tarjetas",
])

if not df.empty:
  df["Fecha"] = pd.to_datetime(df["Fecha"])
  df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
  if "Detalle_Tarjeta" not in df.columns:
    df["Detalle_Tarjeta"] = "General"
  if "Es_Suscripcion" not in df.columns:
    df["Es_Suscripcion"] = "No"

# ==================== PESTAÑA 1 ====================
with pestana1:
  if df.empty:
    st.info(
        "Aún no hay datos registrados. Comienza importando o agregando"
        " movimientos."
    )
  else:
    meses_disponibles = sorted(df["Mes"].unique(), reverse=True)
    mes_seleccionado = st.selectbox(
        "Selecciona el Mes a Visualizar", meses_disponibles
    )
    df_mes = df[df["Mes"] == mes_seleccionado]

    total_ingresos = df_mes[df_mes["Tipo"] == "Ingreso"]["Monto"].sum()
    total_egresos = df_mes[
        df_mes["Tipo"].isin(["Gasto", "Consumo Tarjeta de Crédito"])
    ]["Monto"].sum()
    total_retiros = df_mes[df_mes["Tipo"] == "Retiro Efectivo"]["Monto"].sum()
    total_suscripciones = df_mes[df_mes["Es_Suscripcion"] == "Sí"][
        "Monto"
    ].sum()
    balance = total_ingresos - total_egresos

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Ingresos", f"S/ {total_ingresos:,.2f}")
    c2.metric("Total Egresos / Tarjetas", f"S/ {total_egresos:,.2f}")
    c3.metric("Total Retiros Efectivo", f"S/ {total_retiros:,.2f}")
    c4.metric(
        "Balance del Mes",
        f"S/ {balance:,.2f}",
        delta_color="normal" if balance >= 0 else "inverse",
    )

    st.markdown("---")
    st.subheader("🚨 Panel de Alertas Automáticas")
    alertas_activas = 0

    if total_ingresos > 0 and (total_retiros / total_ingresos) > 0.30:
      alertas_activas += 1
      st.warning(
          f"⚠️ **Alerta de Retiros:** Tus retiros en efectivo (S/"
          f" {total_retiros:,.2f}) superan el 30% de tus ingresos del mes."
      )

    gastos_tc = df_mes[df_mes["Medio_Pago"] == "Tarjeta Crédito"][
        "Monto"
    ].sum()
    if total_ingresos > 0 and (gastos_tc / total_ingresos) > 0.50:
      alertas_activas += 1
      st.error(
          f"🚨 **Alerta de Endeudamiento:** Tus consumos con Tarjeta de Crédito"
          f" (S/ {gastos_tc:,.2f}) representan más del 50% de tus ingresos."
      )

    if total_suscripciones > 300:
      alertas_activas += 1
      st.info(
          f"ℹ️ **Aviso de Suscripciones:** Este mes tienes S/"
          f" {total_suscripciones:,.2f} debitados automáticamente."
      )

    if alertas_activas == 0:
      st.success(
          "✅ ¡Todo en orden! No hay alertas de riesgo financiero activas."
      )

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
      st.subheader("Egresos por Medio de Pago / Aplicación")
      df_gastos_mes = df_mes[
          df_mes["Tipo"].isin(["Gasto", "Consumo Tarjeta de Crédito"])
      ]
      if not df_gastos_mes.empty:
        fig_pago = px.pie(
            df_gastos_mes,
            names="Medio_Pago",
            values="Monto",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu,
        )
        st.plotly_chart(fig_pago, use_container_width=True)

    with col_g2:
      st.subheader("Desglose por Tarjeta Específica")
      df_tarjetas_uso = df_gastos_mes[
          df_gastos_mes["Detalle_Tarjeta"] != "General"
      ]
      if not df_tarjetas_uso.empty:
        fig_tar = px.bar(
            df_tarjetas_uso,
            x="Detalle_Tarjeta",
            y="Monto",
            color="Categoria",
            barmode="stack",
            color_discrete_sequence=px.colors.sequential.Tealgrn,
        )
        st.plotly_chart(fig_tar, use_container_width=True)
      else:
        st.write("No hay consumos asociados a tarjetas específicas.")

    st.subheader(f"📋 Historial de Movimientos - {mes_seleccionado}")
    st.dataframe(
        df_mes.sort_values(by="Fecha", ascending=False),
        use_container_width=True,
    )

# ==================== PESTAÑA 2 ====================
with pestana2:
  st.subheader("📥 Carga Automática de Movimientos")
  plantilla_ejemplo = pd.DataFrame({
      "Fecha": ["2026-10-01", "2026-10-02"],
      "Tipo": ["Gasto", "Consumo Tarjeta de Crédito"],
      "Categoria": ["Alimentación", "Entretenimiento"],
      "Descripcion": ["Supermercado", "Netflix"],
      "Monto": [150.50, 45.00],
      "Medio_Pago": ["Tarjeta Crédito", "Tarjeta Débito"],
      "Detalle_Tarjeta": ["Tarjeta Principal", "General"],
      "Es_Suscripcion": ["No", "Sí"],
  })
  st.download_button(
      "⬇️ Descargar Plantilla Modelo Avanzada",
      plantilla_ejemplo.to_csv(index=False).encode("utf-8"),
      "plantilla_avanzada.csv",
      "text/csv",
  )

  archivo_subido = st.file_uploader(
      "Elige tu archivo Excel o CSV", type=["csv", "xlsx"]
  )
  if archivo_subido is not None:
    try:
      df_imp = (
          pd.read_csv(archivo_subido)
          if archivo_subido.name.endswith(".csv")
          else pd.read_excel(archivo_subido)
      )
      st.dataframe(df_imp.head(), use_container_width=True)
      if st.button("Confirmar e Importar al Sistema"):
        columnas_req = [
            "Fecha",
            "Tipo",
            "Categoria",
            "Descripcion",
            "Monto",
            "Medio_Pago",
            "Detalle_Tarjeta",
            "Es_Suscripcion",
        ]
        if all(col in df_imp.columns for col in columnas_req):
          df = pd.concat([df, df_imp[columnas_req]], ignore_index=True)
          df.to_csv(ARCHIVO_DATOS, index=False)
          st.success("¡Importación exitosa!")
        else:
          st.error("El archivo no contiene las columnas requeridas.")
    except Exception as e:
      st.error(f"Error procesando el archivo: {e}")

# ==================== PESTAÑA 3 ====================
with pestana3:
  st.subheader("➕ Registrar Movimiento Detallado")
  with st.form("form_manual_avanzado", clear_on_submit=True):
    col_m1, col_m2 = st.columns(2)
    with col_m1:
      fecha_m = st.date_input("Fecha", datetime.date.today())
      tipo_m = st.selectbox(
          "Tipo",
          [
              "Gasto",
              "Consumo Tarjeta de Crédito",
              "Retiro Efectivo",
              "Ingreso",
          ],
      )
      categoria_m = st.selectbox(
          "Categoría",
          list(df_presupuestos["Categoria"].unique()) + ["Otros"],
      )
      descripcion_m = st.text_input("Descripción / Establecimiento")
    with col_m2:
      monto_m = st.number_input("Monto (S/)", min_value=0.0, format="%.2f")
      medio_pago_m = st.selectbox(
          "Medio de Pago",
          [
              "Tarjeta Débito",
              "Tarjeta Crédito",
              "Yape",
              "Plin",
              "Efectivo",
              "Transferencia",
          ],
      )
      tarjetas_disponibles = list(df_tarjetas["Nombre_Tarjeta"].unique()) + [
          "Ninguna / General"
      ]
      detalle_tarjeta_m = st.selectbox(
          "¿A qué tarjeta pertenece?", tarjetas_disponibles
      )
      es_suscripcion_m = st.radio(
          "¿Es una suscripción o débito automático?", ["No", "Sí"]
      )

    if st.form_submit_button("Guardar Transacción"):
      nuevo_reg = pd.DataFrame({
          "Fecha": [str(fecha_m)],
          "Tipo": [tipo_m],
          "Categoria": [categoria_m],
          "Descripcion": [descripcion_m],
          "Monto": [monto_m],
          "Medio_Pago": [medio_pago_m],
          "Detalle_Tarjeta": [detalle_tarjeta_m],
          "Es_Suscripcion": [es_suscripcion_m],
      })
      df = pd.concat([df, nuevo_reg], ignore_index=True)
      df.to_csv(ARCHIVO_DATOS, index=False)
      st.success("¡Transacción guardada correctamente!")

# ==================== PESTAÑA 4 ====================
with pestana4:
  st.subheader("🎯 Seguimiento de Presupuestos Mensuales")
  edited_presupuestos = st.data_editor(
      df_presupuestos, num_rows="dynamic", use_container_width=True
  )
  if st.button("Guardar Presupuestos"):
    edited_presupuestos.to_csv(ARCHIVO_PRESUPUESTOS, index=False)
    df_presupuestos = edited_presupuestos
    st.success("¡Presupuestos actualizados!")

  st.markdown("---")
  st.markdown("### Ejecución del Mes Actual")
  if not df.empty:
    mes_actual = str(datetime.date.today().strftime("%Y-%m"))
    df_mes_actual = df[
        (df["Mes"] == mes_actual)
        & (df["Tipo"].isin(["Gasto", "Consumo Tarjeta de Crédito"]))
    ]
    gastos_por_cat = (
        df_mes_actual.groupby("Categoria")["Monto"].sum().reset_index()
    )
    comparativa = pd.merge(
        df_presupuestos, gastos_por_cat, on="Categoria", how="left"
    ).fillna(0)
    comparativa.rename(
        columns={"Monto": "Gastado", "Presupuesto": "Limite"}, inplace=True
    )

    for index, row in comparativa.iterrows():
      cat, limite, gastado = (
          row["Categoria"],
          row["Limite"],
          row["Gastado"],
      )
      porcentaje = (gastado / limite) if limite > 0 else 0
      st.markdown(
          f"**{cat}** — Gastado: S/ {gastado:,.2f} / Límite: S/ {limite:,.2f}"
      )
      st.progress(min(porcentaje, 1.0))
      if gastado > limite and limite > 0:
        st.error(
            f"⚠️ ¡Te pasaste del presupuesto en **{cat}** por S/"
            f" {(gastado - limite):,.2f}!"
        )
      elif porcentaje >= 0.8:
        st.warning(
            f"⚠️ Estás al límite ({porcentaje*100:.0f}%) en **{cat}**."
        )

# ==================== PESTAÑA 5 ====================
with pestana5:
  st.subheader("⚙️ Gestión de Tarjetas y Cuentas")
  edited_tarjetas = st.data_editor(
      df_tarjetas, num_rows="dynamic", use_container_width=True
  )
  if st.button("Actualizar Lista de Tarjetas"):
    edited_tarjetas.to_csv(ARCHIVO_TARJETAS, index=False)
    df_tarjetas = edited_tarjetas
    st.success("¡Tarjetas actualizadas correctamente!")
