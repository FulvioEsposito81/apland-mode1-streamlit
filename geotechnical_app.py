import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from api_client_geo import GeotechnicalAPIClient
from config_app import API_BASE_URL, APP_TITLE, APP_VERSION
import os

# Page configuration
st.set_page_config(
    page_title="MODEI - Server Backup",
    layout="wide",
)

# Initialize API client
@st.cache_resource
def get_api_client():
    return GeotechnicalAPIClient(base_url=API_BASE_URL)

api_client = get_api_client()

# Initialize session state
if 'sfd_value' not in st.session_state:
    st.session_state.sfd_value = None
if 'sfd_calculated' not in st.session_state:
    st.session_state.sfd_calculated = False
if 'enable_saturated' not in st.session_state:
    st.session_state.enable_saturated = False
if 'enable_unsaturated' not in st.session_state:
    st.session_state.enable_unsaturated = False
if 'last_params' not in st.session_state:
    st.session_state.last_params = {}

# Function to calculate SFd
def calculate_sfd(h, alpha, gamma, phi, c):
    """Calculate Safety Factor (SFd) via API"""
    # Check if all required parameters are non-zero
    if h > 0 and gamma > 0 and phi > 0 and c >= 0:
        # Check if parameters have changed
        current_params = {
            'h': h,
            'alpha': alpha,
            'gamma': gamma,
            'phi': phi,
            'c': c
        }
        
        if current_params != st.session_state.last_params:
            st.session_state.last_params = current_params
            
            # Call API
            with st.spinner('Calcolo SFd in corso...'):
                result = api_client.calculate_sfd(
                    c=c,
                    gamma=gamma,
                    h=h,
                    alpha=alpha,
                    phi=phi
                )
            
            if result.get('success', False):
                sfd = result.get('sfd')
                st.session_state.sfd_value = sfd
                st.session_state.sfd_calculated = True
                
                # Enable appropriate fieldset based on SFd value
                if sfd <= 1:
                    # SFd <= 1: Enable unsaturated section (second fieldset)
                    st.session_state.enable_saturated = False
                    st.session_state.enable_unsaturated = True
                else:  # sfd > 1
                    # SFd > 1: Enable saturated section (first fieldset)
                    st.session_state.enable_saturated = True
                    st.session_state.enable_unsaturated = False
                
                return True, sfd, None
            else:
                error = result.get('error', 'Unknown error')
                st.session_state.sfd_calculated = False
                return False, None, error
    
    return False, None, None

# Custom CSS to match the interface style
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #e0e0e0;
        color: black;
        border: 1px solid #ccc;
        padding: 5px 15px;
        border-radius: 3px;
    }
    .section-header {
        font-weight: bold;
        font-size: 14px;
        margin-top: 20px;
        margin-bottom: 10px;
        color: #333;
    }
    .section-header.disabled {
        color: #999;
    }
    div[data-testid="column"] {
        background-color: white;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stNumberInput label {
        font-size: 13px;
        color: #555;
    }
    .disabled-section {
        opacity: 0.5;
        pointer-events: none;
        background-color: #f9f9f9;
    }
    .sfd-display {
        font-size: 18px;
        font-weight: bold;
        color: #2196F3;
    }
    .sfd-error {
        color: #f44336;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title(APP_TITLE)


# Create two columns for the layout
col1, col2 = st.columns([1, 2])

with col1:
   
    st.markdown('<div class="section-header">Dati geometrici</div>', unsafe_allow_html=True)
    
    # Geometric data inputs
    col_label1, col_input1, col_unit1 = st.columns([3, 1, 0.5])
    with col_label1:
        st.text("Profondità superficie di scorrimento dal P.C.")
    with col_input1:
        h_value = st.number_input("H", value=0.0, step=1e-10, label_visibility="collapsed", key="h")
    with col_unit1:
        st.text("m")
    
    col_label2, col_input2, col_unit2 = st.columns([3, 1, 0.5])
    with col_label2:
        st.text("Angolo di inclinazione del P.C.")
    with col_input2:
        alpha_value = st.number_input("α", value=0.0, step=1e-10, label_visibility="collapsed", key="alpha")
    with col_unit2:
        st.text("°")
    
    st.markdown('<div class="section-header">Caratterizzazione meccanica del terreno</div>', unsafe_allow_html=True)
    
    col_label3, col_input3, col_unit3 = st.columns([3, 1, 0.5])
    with col_label3:
        st.text("Peso unità di volume terreno")
    with col_input3:
        gamma_value = st.number_input("γ", value=0.0, step=1e-10, label_visibility="collapsed", key="gamma")
    with col_unit3:
        st.text("kN/m³")
    
    col_label4, col_input4, col_unit4 = st.columns([3, 1, 0.5])
    with col_label4:
        st.text("Angolo di resistenza al taglio")
    with col_input4:
        phi_value = st.number_input("φ", value=0.0, step=1e-10, label_visibility="collapsed", key="phi")
    with col_unit4:
        st.text("°")
    
    col_label5, col_input5, col_unit5 = st.columns([3, 1, 0.5])
    with col_label5:
        st.text("Coesione efficace")
    with col_input5:
        c_value = st.number_input("c'", value=0.0, step=1e-10, label_visibility="collapsed", key="c")
    with col_unit5:
        st.text("kPa")
    
    # Calculate SFd when parameters are entered
    success, sfd_result, error = calculate_sfd(h_value, alpha_value, gamma_value, phi_value, c_value)
    
    st.markdown("---")
    
    # Safety Factor section
    col_sf1, col_sf2 = st.columns([3, 1])
    with col_sf1:
        st.markdown('<div class="section-header">Fattore di Sicurezza in assenza di pressioni neutre (SFd)</div>', unsafe_allow_html=True)
    with col_sf2:
        if st.session_state.sfd_calculated and st.session_state.sfd_value is not None:
            st.markdown(f'<div class="sfd-display">{st.session_state.sfd_value:.2f}</div>', unsafe_allow_html=True)
        else:
            st.text("NaN")
    
    # Show error if SFd calculation failed
    if error:
        st.error(f"Errore nel calcolo SFd: {error}")
    
    # Display info based on SFd value
    if st.session_state.sfd_calculated and st.session_state.sfd_value is not None:
        if st.session_state.sfd_value >= 1:
            st.info("SFd>=1: una frana potrebbe verificarsi per perturazione della stazione (usare parametri saturi)")
        else:
            st.info("SFd<1: una frana potrebbe verificarsi per innalzamento della falda (usare parametri non saturi)")
    else:
        st.info("SFd>=1 una frana potrebbe verificarsi per perturazione della stazione")
        st.info("SFd<1 una frana potrebbe verificarsi per innalzamento della falda")
    
    # Saturated soil section - enabled when SFd > 1
    saturated_enabled = st.session_state.enable_saturated
    
    header_class = "section-header" if saturated_enabled else "section-header disabled"
    st.markdown(f'<div class="{header_class}">Caratterizzazione idraulica del terreno saturo</div>', unsafe_allow_html=True)
    
    if not saturated_enabled:
        st.info("ℹ️ Questa sezione sarà abilitata quando SFd >= 1")
    
    col_label6, col_input6, col_unit6 = st.columns([3, 1, 0.5])
    with col_label6:
        st.text("Conducibilità idraulica")
    with col_input6:
        k_sat_value = st.number_input("k", format="%.2e", value=0.0, step=1e-10, label_visibility="collapsed", key="k_sat", disabled=not saturated_enabled)
    with col_unit6:
        st.text("m/s")
    
    col_label7, col_input7, col_unit7 = st.columns([3, 1, 0.5])
    with col_label7:
        st.text("Potenziale di infiltrazione")
        st.caption("(Ipputare un valore nullo per usare p=k(cosα))")
    with col_input7:
        p_value = st.number_input("p", value=0.0, step=1e-10, label_visibility="collapsed", key="p", disabled=not saturated_enabled)
    with col_unit7:
        st.text("mm/day")
    
    col_label8, col_input8, col_unit8 = st.columns([3, 1, 0.5])
    with col_label8:
        st.text("Pressione neutra iniziale")
    with col_input8:
        uw0_value = st.number_input("u_w0", value=0.0, step=1e-10, label_visibility="collapsed", key="uw0", disabled=not saturated_enabled)
    with col_unit8:
        st.text("kPa")
    
    col_label9, col_input9, col_unit9 = st.columns([3, 1, 0.5])
    with col_label9:
        st.text("Grado di saturazione")
    with col_input9:
        sr_value = st.number_input("Sr", value=0.0, step=1e-10, label_visibility="collapsed", key="sr", disabled=not saturated_enabled)
    with col_unit9:
        st.text("-")
    
    col_label10, col_input10, col_unit10 = st.columns([3, 1, 0.5])
    with col_label10:
        st.text("Porosità")
    with col_input10:
        n_value = st.number_input("n", value=0.0, step=1e-10, label_visibility="collapsed", key="n", disabled=not saturated_enabled)
    with col_unit10:
        st.text("-")
    
    # Unsaturated soil section - enabled when SFd < 1
    unsaturated_enabled = st.session_state.enable_unsaturated
    
    header_class = "section-header" if unsaturated_enabled else "section-header disabled"
    st.markdown(f'<div class="{header_class}">Caratterizzazione idraulica del terreno parzialmente saturo</div>', unsafe_allow_html=True)
    
    if not unsaturated_enabled:
        st.info("ℹ️ Questa sezione sarà abilitata quando SFd < 1")
    
    col_label11, col_input11, col_unit11 = st.columns([3, 1, 0.5])
    with col_label11:
        st.text("Conducibilità idraulica")
    with col_input11:
        k_unsat_value = st.number_input("k", format="%.2e", value=0.0, step=1e-10, label_visibility="collapsed", key="k_unsat", disabled=not unsaturated_enabled)
    with col_unit11:
        st.text("m/s")
    
    col_label12, col_input12, col_unit12 = st.columns([3, 1, 0.5])
    with col_label12:
        st.text("Potenziale di infiltrazione")
        st.caption("(Ipputare un valore nullo per usare p=k(cosα))")
    with col_input12:
        p_unsat_value = st.number_input("p", value=0.0, step=1e-10, label_visibility="collapsed", key="p_unsat", disabled=not unsaturated_enabled)
    with col_unit12:
        st.text("mm/day")
    
    col_label13, col_input13, col_unit13 = st.columns([3, 1, 0.5])
    with col_label13:
        st.text("Suzione iniz. mis. sulla sup. di scorrimento")
    with col_input13:
        uw0_unsat_value = st.number_input("u_w0", value=0.0, step=1e-10, label_visibility="collapsed", key="uw0_unsat", disabled=not unsaturated_enabled)
    with col_unit13:
        st.text("kPa")
    
    col_label14, col_input14, col_unit14 = st.columns([3, 1, 0.5])
    with col_label14:
        st.text("Coefficiente di ritenzione idrica")
    with col_input14:
        mw_value = st.number_input("m_w", format="%.2e", value=0.0, step=1e-10, label_visibility="collapsed", key="mw", disabled=not unsaturated_enabled)
    with col_unit14:
        st.text("kPa⁻¹")
    
    col_label15, col_input15, col_unit15 = st.columns([3, 1, 0.5])
    with col_label15:
        st.text("Parametro χ")
    with col_input15:
        chi_value = st.number_input("χ(S-1)", value=0.0, step=1e-10, label_visibility="collapsed", key="chi", disabled=not unsaturated_enabled)
    with col_unit15:
        st.text("-")
    
    st.markdown('<div class="section-header">Evento pioggia</div>', unsafe_allow_html=True)
    
    # Date input
    date_value = st.date_input("Data o ID", value=datetime(2026, 1, 28))
    
    col_duration, col_duration_unit = st.columns([2, 1])
    with col_duration:
        duration_value = st.number_input("Durata dell'evento", value=0, format="%d", label_visibility="visible")
    with col_duration_unit:
        st.text("ore")
    
    col_intensity, col_intensity_unit = st.columns([2, 1])
    with col_intensity:
        intensity_value = st.number_input("Intensità evento", value=0.0, step=1e-10, label_visibility="visible")
    with col_intensity_unit:
        st.text("mm/day")
    
    st.markdown("---")
    
    # Calculate button
    if st.button("Calcola"):
        # Validate that SFd has been calculated
        if not st.session_state.sfd_calculated or st.session_state.sfd_value is None:
            st.error("Calcolare prima SFd inserendo i parametri geometrici e meccanici")
        else:
            # Determine which parameters to use based on SFd
            sfd_val = st.session_state.sfd_value
            
            # Check if appropriate section has been filled
            if sfd_val <= 1 and not unsaturated_enabled:
                st.error("Compilare i parametri del terreno parzialmente saturo (SFd < 1)")
            elif sfd_val > 1 and not saturated_enabled:
                st.error("Compilare i parametri del terreno saturo (SFd >= 1)")
            else:
                # Prepare parameters for API call
                with st.spinner("Calcolo in corso..."):
                    try:
                        # Determine prisl based on enabled section
                        prisl = "unsaturated" if sfd_val < 1 else "saturated"
                        
                        # Call compute API
                        if sfd_val < 1:
                            # Use unsaturated parameters
                            result = api_client.calculate_compute(
                                c=c_value,
                                gamma=gamma_value,
                                h=h_value,
                                alpha=alpha_value,
                                phi=phi_value,
                                prisl=prisl,
                                sfd=sfd_val,
                                k=k_unsat_value,
                                p=p_unsat_value,
                                u_w0=uw0_unsat_value,
                                event_id=str(date_value),
                                duration=duration_value,
                                intensity=intensity_value,
                                m_w=mw_value,
                                x0_1=chi_value
                            )
                        else:
                            # Use saturated parameters
                            result = api_client.calculate_compute(
                                c=c_value,
                                gamma=gamma_value,
                                h=h_value,
                                alpha=alpha_value,
                                phi=phi_value,
                                prisl=prisl,
                                sfd=sfd_val,
                                k=k_sat_value,
                                p=p_value,
                                u_w0=uw0_value,
                                event_id=str(date_value),
                                duration=duration_value,
                                intensity=intensity_value,
                                sr=sr_value,
                                n=n_value
                            )
                        
                        if not result.get('success', True):
                            st.error(f"❌ Errore nel calcolo: {result.get('error', 'Unknown error')}")
                        else:
                            st.session_state['calculation_done'] = True
                            st.session_state['results'] = result
                            st.success("✅ Calcolo completato con successo!")
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Errore durante il calcolo: {str(e)}")

with col2:
    st.markdown('<div class="section-header">Info calcolo</div>', unsafe_allow_html=True)

    # Display calculation info
    if 'calculation_done' in st.session_state and st.session_state['calculation_done']:
        results = st.session_state.get('results', {})
        sfd_value = st.session_state.get('sfd_value', None)

        st.success("✓ Calcolo completato con successo")

        # Check if SFD < 1 for tab layout
        if sfd_value is not None and sfd_value < 1:
            # Tabs layout for SFD < 1
            tab1, tab2 = st.tabs(["Risultati numerici", "Grafici"])

            with tab1:
                st.subheader("Risultati del calcolo")

                # Display main results
                col_res1, col_res2 = st.columns(2)

                with col_res1:
                    if 'p' in results:
                        p_value = results['p']
                        st.metric("Potenziale di infiltrazione", f"{p_value:.4f}" if isinstance(p_value, (int, float)) else str(p_value))

                    if 'I' in results:
                        i_value = results['I']
                        st.metric("Infiltrazione", f"{i_value:.4f}" if isinstance(i_value, (int, float)) else str(i_value))

                with col_res2:
                    # Display stability status
                    if 'plot' in results and results['plot']:
                        plot_data = results['plot']
                        if 'critical_curve' in plot_data and 'series' in plot_data['critical_curve']:
                            if 'R1' in plot_data['critical_curve']['series']:
                                r1_data = plot_data['critical_curve']['series']['R1']
                                is_stable = r1_data.get('stable', False)

                                if is_stable:
                                    st.success("**PENDIO STABILE**")
                                else:
                                    st.error("**PENDIO INSTABILE**")

            with tab2:
                st.subheader("Grafici dei risultati")

                if 'plot' in results and results['plot']:
                    plot_data = results['plot']

                    # Check for critical_curve data structure
                    if 'critical_curve' in plot_data:
                        cc_data = plot_data['critical_curve']

                        # Create figure with both critical curve and R1 point
                        fig = go.Figure()

                        # Add critical_curve series
                        if 'series' in cc_data and 'critical_curve' in cc_data['series']:
                            cc_series = cc_data['series']['critical_curve']
                            if 'x' in cc_series and 'y' in cc_series:
                                fig.add_trace(go.Scatter(
                                    x=cc_series['x'],
                                    y=cc_series['y'],
                                    mode='lines',
                                    name='Curva Critica',
                                    line=dict(color='blue', width=2)
                                ))

                        # Add R1 point
                        if 'series' in cc_data and 'R1' in cc_data['series']:
                            r1_series = cc_data['series']['R1']
                            if 'x' in r1_series and 'y' in r1_series:
                                is_stable = r1_series.get('stable', False)
                                fig.add_trace(go.Scatter(
                                    x=r1_series['x'],
                                    y=r1_series['y'],
                                    mode='markers',
                                    name='R1',
                                    marker=dict(
                                        color='green' if is_stable else 'red',
                                        size=12,
                                        symbol='circle'
                                    )
                                ))

                        # Update layout with axis limits
                        x_label = cc_data.get('xAxes', 'x')
                        y_label = cc_data.get('yAxes', 'y')
                        x_max = cc_data.get('xMax', 0)
                        y_max = cc_data.get('yMax', 0)

                        # Calculate axis limits from data if xMax/yMax are not set
                        if x_max == 0:
                            all_x = []
                            if 'critical_curve' in cc_data['series'] and 'x' in cc_data['series']['critical_curve']:
                                all_x.extend(cc_data['series']['critical_curve']['x'])
                            if 'R1' in cc_data['series'] and 'x' in cc_data['series']['R1']:
                                all_x.extend(cc_data['series']['R1']['x'])
                            if all_x:
                                x_max = max(all_x) * 1.1  # Add 10% padding

                        if y_max == 0:
                            all_y = []
                            if 'critical_curve' in cc_data['series'] and 'y' in cc_data['series']['critical_curve']:
                                all_y.extend(cc_data['series']['critical_curve']['y'])
                            if 'R1' in cc_data['series'] and 'y' in cc_data['series']['R1']:
                                all_y.extend(cc_data['series']['R1']['y'])
                            if all_y:
                                y_max = max(all_y) * 1.1  # Add 10% padding

                        layout_config = {
                            'xaxis_title': x_label,
                            'yaxis_title': y_label,
                            'height': 500,
                            'hovermode': 'closest',
                            'showlegend': True
                        }

                        if x_max > 0:
                            layout_config['xaxis'] = dict(range=[0, x_max], title=x_label)
                        if y_max > 0:
                            layout_config['yaxis'] = dict(range=[0, y_max], title=y_label)

                        fig.update_layout(**layout_config)

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Dati del grafico non disponibili")
                else:
                    st.info("Nessun dato grafico disponibile")

        else:
            # Standard tabs layout for SFD >= 1 or when SFD not available
            tab1, tab2 = st.tabs(["Risultati numerici", "Grafici"])

            with tab1:
                st.subheader("Risultati del calcolo")

                # Display main results
                col_res1, col_res2 = st.columns(2)

                with col_res1:
                    if 'p' in results:
                        p_value = results['p']
                        st.metric("Potenziale di infiltrazione", f"{p_value:.4f}" if isinstance(p_value, (int, float)) else str(p_value))

                    if 'I' in results:
                        i_value = results['I']
                        st.metric("Infiltrazione", f"{i_value:.4f}" if isinstance(i_value, (int, float)) else str(i_value))

                with col_res2:
                    # Display stability status
                    if 'plot' in results and results['plot']:
                        plot_data = results['plot']
                        if 'critical_curve' in plot_data and 'series' in plot_data['critical_curve']:
                            if 'R1' in plot_data['critical_curve']['series']:
                                r1_data = plot_data['critical_curve']['series']['R1']
                                is_stable = r1_data.get('stable', False)

                                if is_stable:
                                    st.success("**PENDIO STABILE**")
                                else:
                                    st.error("**PENDIO INSTABILE**")

            with tab2:
                st.subheader("Grafici dei risultati")

                if 'plot' in results and results['plot']:
                    plot_data = results['plot']

                    # Check for critical_curve data structure
                    if 'critical_curve' in plot_data:
                        cc_data = plot_data['critical_curve']

                        # Create figure with both critical curve and R1 point
                        fig = go.Figure()

                        # Add critical_curve series
                        if 'series' in cc_data and 'critical_curve' in cc_data['series']:
                            cc_series = cc_data['series']['critical_curve']
                            if 'x' in cc_series and 'y' in cc_series:
                                fig.add_trace(go.Scatter(
                                    x=cc_series['x'],
                                    y=cc_series['y'],
                                    mode='lines',
                                    name='Curva Critica',
                                    line=dict(color='blue', width=2)
                                ))

                        # Add R1 point
                        if 'series' in cc_data and 'R1' in cc_data['series']:
                            r1_series = cc_data['series']['R1']
                            if 'x' in r1_series and 'y' in r1_series:
                                is_stable = r1_series.get('stable', False)
                                fig.add_trace(go.Scatter(
                                    x=r1_series['x'],
                                    y=r1_series['y'],
                                    mode='markers',
                                    name='R1',
                                    marker=dict(
                                        color='green' if is_stable else 'red',
                                        size=12,
                                        symbol='circle'
                                    )
                                ))

                        # Update layout with axis limits
                        x_label = cc_data.get('xAxes', 'x')
                        y_label = cc_data.get('yAxes', 'y')
                        x_max = cc_data.get('xMax', 0)
                        y_max = cc_data.get('yMax', 0)
                        os.write(1, f"x_max = {x_max}".encode())
                        os.write(1, f"y_max = {y_max}".encode())

                        # Calculate axis limits from data if xMax/yMax are not set
                        if x_max == 0:
                            all_x = []
                            if 'critical_curve' in cc_data['series'] and 'x' in cc_data['series']['critical_curve']:
                                all_x.extend(cc_data['series']['critical_curve']['x'])
                            if 'R1' in cc_data['series'] and 'x' in cc_data['series']['R1']:
                                all_x.extend(cc_data['series']['R1']['x'])
                            if all_x:
                                x_max = max(all_x) * 1.1  # Add 10% padding

                        if y_max == 0:
                            all_y = []
                            if 'critical_curve' in cc_data['series'] and 'y' in cc_data['series']['critical_curve']:
                                all_y.extend(cc_data['series']['critical_curve']['y'])
                            if 'R1' in cc_data['series'] and 'y' in cc_data['series']['R1']:
                                all_y.extend(cc_data['series']['R1']['y'])
                            if all_y:
                                y_max = max(all_y) * 1.1  # Add 10% padding

                        layout_config = {
                            'xaxis_title': x_label,
                            'yaxis_title': y_label,
                            'height': 500,
                            'hovermode': 'closest',
                            'showlegend': True
                        }

                        if x_max > 0:
                            layout_config['xaxis'] = dict(range=[0, x_max], title=x_label)
                        if y_max > 0:
                            layout_config['yaxis'] = dict(range=[0, y_max], title=y_label)

                        fig.update_layout(**layout_config)

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Dati del grafico non disponibili")
                else:
                    st.info("Nessun dato grafico disponibile")
    else:
        st.info("Inserire i parametri e premere 'Calcola' per visualizzare i risultati")

# Footer
st.markdown("---")
col_footer1, col_footer2 = st.columns([4, 1])
with col_footer2:
    st.caption(f"Versione: {APP_VERSION}")
