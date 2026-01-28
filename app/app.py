import streamlit as st
import pandas as pd
import docker
import os
import time

st.set_page_config(page_title="Le Gardien", page_icon="🛡️", layout="wide")
DATA_FILE = "/app/data/stats.csv"

# Connexion Docker (Pour les actions ET les logs)
try:
    client = docker.from_env()
except:
    st.error("🚨 Erreur critique : Impossible de contacter Docker (Socket non monté ?)")
    st.stop()

st.title("🛡️ Le Gardien du Serveur")

tab_mon, tab_act = st.tabs(["📈 Monitoring & Logs", "⚡ Actions Rapides"])

# --- ONGLET 1 : MONITORING ---
with tab_mon:
    # Vérification présence fichier CSV
    if not os.path.exists(DATA_FILE):
        st.info("⏳ Le logger s'initialise... (Attente des données)")
        time.sleep(2)
        st.rerun()
    else:
        try:
            # Lecture du CSV
            df = pd.read_csv(DATA_FILE)
            
            if len(df) > 0:
                # Sélecteur de conteneur
                containers_list = df['container_name'].unique()
                selected = st.selectbox("🔍 Inspecter un conteneur :", containers_list)
                
                # Filtrage des données (40 derniers points)
                data = df[df['container_name'] == selected].tail(40)
                
                if not data.empty:
                    last = data.iloc[-1]
                    status = last['status']
                    
                    st.divider()

                    # --- PARTIE 1 : STATUT (Vert/Rouge) ---
                    col_stat, col_cpu, col_ram = st.columns(3)
                    
                    with col_stat:
                        # Si Running -> Vert (Success), Sinon -> Rouge (Error)
                        if status.lower() == "running":
                            st.success(f"🟢 Statut : {status.upper()}")
                        else:
                            st.error(f"🔴 Statut : {status.upper()}")
                            
                    col_cpu.metric("CPU Moyen", f"{last['cpu_percent']}%")
                    col_ram.metric("RAM Utilisée", f"{last['ram_usage_mb']} Mo")
                    
                    # --- PARTIE 2 : GRAPHIQUES ---
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        st.caption("Historique CPU (%)")
                        st.area_chart(data, x="timestamp", y="cpu_percent", color="#FF4B4B")
                    with col_g2:
                        st.caption("Historique RAM (Mo)")
                        st.line_chart(data, x="timestamp", y="ram_usage_mb", color="#0068C9")

                    # --- PARTIE 3 : LOGS (Nouvelle fonctionnalité) ---
                    st.subheader("📜 Journaux (Logs)")
                    with st.expander(f"Voir les logs de {selected}", expanded=False):
                        try:
                            # On demande à Docker les logs en direct
                            container_obj = client.containers.get(selected)
                            # On récupère les 50 dernières lignes et on décode les bytes en texte
                            logs = container_obj.logs(tail=50).decode("utf-8", errors="ignore")
                            
                            if logs:
                                st.code(logs, language="bash")
                            else:
                                st.info("Aucun log disponible ou conteneur muet.")
                        except docker.errors.NotFound:
                            st.warning("Ce conteneur n'existe plus dans Docker (mais est présent dans l'historique CSV).")
                        except Exception as e:
                            st.error(f"Erreur lecture logs : {e}")

                if st.button("🔄 Rafraîchir les données"):
                    st.rerun()
        except Exception as e:
            st.error(f"Erreur lecture fichier CSV : {e}")

# --- ONGLET 2 : ACTIONS ---
with tab_act:
    st.write("### 🎛️ Gestionnaire de Conteneurs")
    
    # On récupère la liste fraîche depuis Docker
    real_containers = client.containers.list(all=True)
    
    # En-têtes
    h1, h2, h3 = st.columns([3, 1.5, 1])
    h1.markdown("**Nom du Conteneur**")
    h2.markdown("**État**")
    h3.markdown("**Action**")
    st.divider()

    for c in real_containers:
        col1, col2, col3 = st.columns([3, 1.5, 1])
        
        # Nom
        col1.markdown(f"**{c.name}**")
        
        # État coloré
        with col2:
            if c.status == "running":
                st.markdown("🟢 `Running`")
            elif c.status == "exited":
                st.markdown("🔴 `Exited`")
            else:
                st.markdown(f"⚪ `{c.status}`")
        
        # Boutons
        with col3:
            if c.status == "running":
                if st.button("Stop", key=f"stop_{c.id}", type="primary"):
                    c.stop()
                    st.toast(f"{c.name} arrêté !")
                    time.sleep(1)
                    st.rerun()
            else:
                if st.button("Start", key=f"start_{c.id}"):
                    c.start()
                    st.toast(f"{c.name} démarré !")
                    time.sleep(1)
                    st.rerun()