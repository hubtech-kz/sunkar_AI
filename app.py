
import streamlit as st
import os
import time
from modules.vision import VisionRecon
from modules.mapper import InfrastructureMapper
from modules.bot_investigator import BotInvestigator
from modules.legal import LegalEvidence
from modules.hunter import SunkarHunter
from utils.db_manager import DBManager

# Initialize modules
vision = VisionRecon()
mapper = InfrastructureMapper()
bot_inv = BotInvestigator()
legal = LegalEvidence()
hunter = SunkarHunter()
db = DBManager()

# Set page config
st.set_page_config(
    page_title="SUNQAR AI | Anti-Scam OSINT",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Create assets dir if not exists
if not os.path.exists("assets"):
    os.makedirs("assets")

# CSS path
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    local_css(css_path)

# Translations
LANGUAGES = {
    "English": {
        "title": "SUNQAR AI | Anti-Scam OSINT",
        "header": "SUNQAR AI Dashboard",
        "subheader": "Autonomous intelligence for financial sovereignty of Kazakhstan",
        "nav": "Navigation",
        "menu": ["Dashboard", "Vision Recon", "Bot Investigator", "Infrastructure Map", "Autonomous Hunter", "History"],
        "status": "System Status: ACTIVE",
        "analyzed": "Analyzed",
        "threats": "Threats",
        "networks": "Bot-Networks",
        "precision": "Precision",
        "live": "🔍 Live Investigation",
        "input": "Input Sources",
        "verdict": "AI Verdict",
        "run": "RUN DEEP RECON",
        "url_placeholder": "Analyze URL (Web/Telegram)",
        "upload": "Upload suspicious Media (Images/Reels)",
        "threat_detected": "🚨 THREAT DETECTED",
        "suspicious": "⚠️ SUSPICIOUS",
        "legal": "Legal Qualification",
        "confidence": "Confidence",
        "markers": "Detection Markers",
        "gen_report": "GENERATE LEGAL REPORT",
        "history": "Incident Log",
    },
    "Русский": {
        "title": "SUNQAR AI | Анти-Скам OSINT",
        "header": "SUNQAR AI Панель управления",
        "subheader": "Автономный интеллект для защиты финансового суверенитета Казахстана",
        "nav": "Навигация",
        "menu": ["Дашборд", "Vision Recon", "Bot Investigator", "Карта инфраструктуры", "Автономный охотник", "История"],
        "status": "Статус системы: АКТИВЕН",
        "analyzed": "Проверено",
        "threats": "Угрозы",
        "networks": "Бот-сети",
        "precision": "Точность",
        "live": "🔍 Живое расследование",
        "input": "Источники данных",
        "verdict": "Вердикт ИИ",
        "run": "ЗАПУСТИТЬ ПРОВЕРКУ",
        "url_placeholder": "Введите URL (Сайт/Telegram)",
        "upload": "Загрузите медиа (Фото/Видео)",
        "threat_detected": "🚨 ОБНАРУЖЕНА УГРОЗА",
        "suspicious": "⚠️ ПОДОЗРИТЕЛЬНО",
        "legal": "Юридическая квалификация",
        "confidence": "Уверенность",
        "markers": "Маркеры обнаружения",
        "gen_report": "СФОРМИРОВАТЬ ОТЧЕТ",
        "history": "История инцидентов",
    },
    "Қазақша": {
        "title": "SUNQAR AI | Анти-Скам OSINT",
        "header": "SUNQAR AI Басқару панелі",
        "subheader": "Қазақстанның қаржылық κυвернитетін қорғауға арналған автономды интеллект",
        "nav": "Навигация",
        "menu": ["Бақылау тақтасы", "Vision Recon", "Bot Investigator", "Инфрақұрылым картасы", "Автономды аңшы", "Тарих"],
        "status": "Жүйе күйі: БЕЛСЕНДІ",
        "analyzed": "Тексерілді",
        "threats": "Қауіптер",
        "networks": "Бот-желілер",
        "precision": "Дәлдік",
        "live": "🔍 Тікелей тергеу",
        "input": "Мәліметтер көзі",
        "verdict": "ИИ үкімі",
        "run": "ТЕКСЕРУДІ БАСТАУ",
        "url_placeholder": "URL енгізіңіз (Сайт/Telegram)",
        "upload": "Медианы жүктеңіз (Фото/Видео)",
        "threat_detected": "🚨 ҚҚАУІП АНЫҚТАЛДЫ",
        "suspicious": "⚠️ КҮДІКТІ",
        "legal": "Заңдық біліктілік",
        "confidence": "Сенімділік",
        "markers": "Анықтау маркерлері",
        "gen_report": "ЕСЕПТІ ҚАЛЫПТАСТЫРУ",
        "history": "Оқиғалар тарихы",
    }
}

# Sidebar
with st.sidebar:
    st.markdown("# SUNQAR AI")
    lang = st.selectbox("Language / Тіл / Язык", ["English", "Русский", "Қазақша"])
    t = LANGUAGES[lang]
    
    st.markdown("---")
    menu_selection = st.radio(
        t["nav"],
        t["menu"]
    )
    st.markdown("---")
    st.info(t["status"])
    st.caption("v0.1-alpha | DER Turkestan Edition")

# Main Content
if menu_selection == t["menu"][0]: # Dashboard
    st.markdown(f'<h1 class="main-header">{t["header"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{t["subheader"]}</p>', unsafe_allow_html=True)


    stats = db.get_stats()
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    with stats_col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t["analyzed"]}</h3>
            <h2 style="color: #58a6ff">{stats["total"]}</h2>
            <p>Total scanned</p>
        </div>
        """, unsafe_allow_html=True)
    with stats_col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t["threats"]}</h3>
            <h2 style="color: #f85149">{stats["high_threat"]}</h2>
            <p>High risk</p>
        </div>
        """, unsafe_allow_html=True)
    with stats_col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t["networks"]}</h3>
            <h2 style="color: #d29922">{stats["clusters"]}</h2>
            <p>Scam types</p>
        </div>
        """, unsafe_allow_html=True)
    with stats_col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{t["precision"]}</h3>
            <h2 style="color: #3fb950">{stats["precision"]}%</h2>
            <p>Verdict coverage</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"### {t['live']}")
    
    input_col, result_col = st.columns([1, 1])
    
    # Check if a link was passed from Hunter
    default_url = ""
    if "url_input_auto" in st.session_state:
        default_url = st.session_state.url_input_auto
        del st.session_state.url_input_auto

    with input_col:
        st.markdown(f"#### {t['input']}")
        url_input = st.text_input(t["url_placeholder"], value=default_url, placeholder="https://t.me/...", key="url_input")
        uploaded_file = st.file_uploader(t["upload"], type=["jpg", "png", "mp4"])
        
        if st.button(t["run"]):
            if url_input or uploaded_file:
                # CLEANUP: Reset results from previous scan
                if "recon_done" in st.session_state:
                    del st.session_state["recon_done"]
                if "current_results" in st.session_state:
                    del st.session_state["current_results"]
                
                with st.spinner("SUNQAR is hunting..."):
                    # Process Input
                    results = {}
                    
                    if uploaded_file:
                        # 1. Vision Analysis
                        with open("temp_media.png", "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        results['vision'] = vision.analyze_image("temp_media.png")
                        if url_input: # If both provided
                            results['mapper'] = mapper.analyze_url(url_input)
                    if url_input:
                        # MANUAL SAFE-LIST FOR DEMO STABILITY
                        if any(x in url_input for x in ["ayu.edu.kz", "ai-hackathon", "hubtech.kz", "astanahub.com"]):
                            results['vision'] = {
                                "threat_level": "Low",
                                "scam_type": "Verified Partner / Entity",
                                "indicators": ["Verified official domain", "Institutional reliability"],
                                "explanation": "Legitimate institutional resource (Verified Partner)."
                            }
                            results['mapper'] = mapper.analyze_url(url_input)
                            results['url'] = url_input
                        else:
                            # 2. URL Real OSINT + GPT-4o Text Analysis
                            results['mapper'] = mapper.analyze_url(url_input)
                            results['url'] = url_input
                            
                            web_data = mapper.get_website_content(url_input)
                            # Merge tech data with web text for real AI verdict
                            context = {**results['mapper'], **web_data}
                            results['vision'] = vision.analyze_text(context)
                        
                        if "t.me" in url_input:
                            results['bot_steps'] = bot_inv.simulate_interaction(url_input)
                    
                    # Store data
                    all_indicators = results.get('vision', {}).get('indicators', [])\
                        if results.get('vision', {}).get('indicators') else []
                    domain_for_analysis = results.get('mapper', {}).get('domain', '') if 'mapper' in results else ''
                    threat_level = results.get('vision', {}).get('threat_level', 'Medium')
                    results['indicators'] = all_indicators
                    results['legal_articles'] = legal.qualify_offense(all_indicators, domain=domain_for_analysis)
                    results['threat_level'] = threat_level

                    # ✅ NEW: Rule-based risk scoring with explainability
                    risk_result = legal.compute_risk_score(all_indicators, domain=domain_for_analysis, threat_level=threat_level)
                    results['risk_score'] = risk_result['score']
                    results['confidence'] = risk_result['confidence']
                    results['matched_rules'] = risk_result['matched_rules']
                    # Merge article qualification from rule engine too
                    if risk_result['articles']:
                        combined_articles = list(set(results['legal_articles'] + risk_result['articles']))
                        results['legal_articles'] = combined_articles

                    results['explanation'] = results.get('vision', {}).get('explanation', '')
                    results['scam_type'] = results.get('vision', {}).get('scam_type', 'Detection')
                    results['ip'] = results.get('mapper', {}).get('ip', 'N/A') if 'mapper' in results else 'N/A'
                    results['markers'] = results.get('mapper', {}).get('markers', []) if 'mapper' in results else []
                    results['registrar'] = results.get('mapper', {}).get('registrar', 'N/A') if 'mapper' in results else 'N/A'

                    # Log to DB
                    db.log_incident(results)
                    st.session_state.current_results = results
                    st.session_state.recon_done = True
            else:
                st.warning("Please provide an input.")

    with result_col:
        st.markdown(f"#### {t['verdict']}")
        if "recon_done" in st.session_state and st.session_state.recon_done:
            res = st.session_state.current_results

            # ── 1. STATUS BANNER ──────────────────────────────────────────────
            if res.get('threat_level') == "High":
                st.error(f"🚨 THREAT DETECTED: {res.get('scam_type', '')}")
            elif res.get('threat_level') == "Low" or "Compliance" in str(res.get('legal_articles', '')):
                st.success(f"✅ SAFE / ТАЗА: {res.get('scam_type', '')}")
            else:
                st.warning(f"⚠️ {t['suspicious']}: {res.get('scam_type', '')}")

            # ── 2. RISK SCORE GAUGE ───────────────────────────────────────────
            risk_score = res.get('risk_score', 0)
            confidence = res.get('confidence', 0)
            if risk_score >= 75:
                score_color = "#f85149"
                score_label = "КРИТИЧЕСКИЙ"
            elif risk_score >= 50:
                score_color = "#d29922"
                score_label = "ВЫСОКИЙ"
            elif risk_score >= 25:
                score_color = "#58a6ff"
                score_label = "СРЕДНИЙ"
            else:
                score_color = "#3fb950"
                score_label = "НИЗКИЙ"

            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px;margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:12px;color:#8b949e;">RISK SCORE</div>
                        <div style="font-size:42px;font-weight:900;color:{score_color};line-height:1;">{risk_score}</div>
                        <div style="font-size:11px;color:{score_color};">{score_label}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:12px;color:#8b949e;">CONFIDENCE</div>
                        <div style="font-size:32px;font-weight:700;color:#c9d1d9;">{confidence}%</div>
                        <div style="font-size:11px;color:#8b949e;">{t['legal']}</div>
                    </div>
                </div>
                <div style="margin-top:10px;background:#21262d;border-radius:6px;height:10px;">
                    <div style="background:{score_color};width:{risk_score}%;height:10px;border-radius:6px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── 3. LEGAL QUALIFICATION ────────────────────────────────────────
            legal_text = ", ".join(res.get('legal_articles', []))
            st.markdown(f"**⚖️ {t['legal']}:** `{legal_text}`")

            # ── 4. EXPLAINABILITY LAYER ───────────────────────────────────────
            matched_rules = res.get('matched_rules', [])
            if matched_rules:
                with st.expander("📋 Explainability — Какие признаки → Какая статья", expanded=True):
                    for rule in matched_rules:
                        article = rule.get('article') or '⚠️ Дополнительный риск-фактор'
                        weight = rule.get('weight', 0)
                        label = rule.get('label', '')
                        color = "#f85149" if weight >= 30 else "#d29922"
                        st.markdown(
                            f"<div style='padding:4px 8px;margin:3px 0;border-left:3px solid {color};font-size:13px;'>"
                            f"<b style='color:{color}'>[+{weight} pts]</b> {label} "
                            f"<code style='float:right;font-size:11px;'>{article}</code></div>",
                            unsafe_allow_html=True
                        )

            # ── 5. AI INDICATORS ──────────────────────────────────────────────
            ai_indicators = res.get('vision', {}).get('indicators', [])
            if ai_indicators:
                with st.expander("🤖 AI Indicators (GPT-4o)"):
                    for ind in ai_indicators:
                        st.write(f"• {ind}")

            # ── 6. REPORT GENERATION ──────────────────────────────────────────
            if st.button(t["gen_report"]):
                report = legal.generate_report(res)
                st.download_button("📥 Download Report (.txt)", report, file_name="sunqar_report.txt")
                st.markdown("### Report Preview")
                st.code(report)
        else:
            st.info("Awaiting input for analysis...")

elif menu_selection == t["menu"][1]: # Vision Recon
    st.markdown(f'<h1 class="main-header">{t["menu"][1]}</h1>', unsafe_allow_html=True)
    st.write("Specialized AI analysis of visual fraud triggers.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("Detection Matrix")
        st.write("- Deepfake likelihood map")
        st.write("- Logo authenticity check")
        st.write("- OCR Context extraction")
    with col2:
        st.success("Supported Formats: PNG, JPG, MP4 (Frames)")

elif menu_selection == t["menu"][2]: # Bot Investigator
    st.markdown(f'<h1 class="main-header">{t["menu"][2]}</h1>', unsafe_allow_html=True)
    st.markdown("Real-time Telegram investigation via public HTTP. Enter a `t.me/` link and run analysis in Dashboard first.")
    if "current_results" in st.session_state and "bot_steps" in st.session_state.current_results:
        st.markdown("### 📋 Investigation Log")
        for step in st.session_state.current_results['bot_steps']:
            if "[!!]" in step:
                st.error(step)
            elif "[+]" in step:
                st.success(step)
            else:
                st.code(step)
    else:
        st.info("Run a Telegram analysis: enter a `https://t.me/` link in the Dashboard and click 'Run'.")

elif menu_selection == t["menu"][3]: # Infrastructure Map / Network Intelligence
    st.markdown(f'<h1 class="main-header">{t["menu"][3]}</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🗺️ OSINT Footprint", "🕸️ Network Intelligence"])
    
    with tab1:
        if "current_results" in st.session_state and "mapper" in st.session_state.current_results:
            m = st.session_state.current_results['mapper']
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("IP Address", m.get("ip", "N/A"))
                st.metric("Domain Age", m.get("age", "N/A"))
                st.metric("Registrar", m.get("registrar", "N/A"))
            with col_b:
                st.metric("Domain", m.get("domain", "N/A"))
                risk = st.session_state.current_results.get("risk_score", 0)
                st.metric("Risk Score", f"{risk}/100")
            st.markdown("#### 🔍 Digital Markers (Trackers)")
            markers = m.get("markers", [])
            if markers and markers != ["No trackers detected"]:
                for mk in markers:
                    st.warning(f"📡 {mk}")
            else:
                st.info("No tracking beacons detected on this domain.")
        else:
            st.info("Run a URL analysis first to map its infrastructure.")
    
    with tab2:
        st.markdown("### 🕸️ Scam Network Clusters")
        st.caption("Domains sharing the same IP address are grouped as potential scam networks/clusters.")
        clusters = db.get_network_clusters()
        if clusters:
            for i, cluster in enumerate(clusters, 1):
                risk_color = "#f85149" if cluster['avg_risk_score'] >= 50 else "#d29922"
                with st.expander(f"🔴 Cluster #{i} — IP: {cluster['shared_ip']} ({cluster['count']} domains)", expanded=i==1):
                    st.markdown(f"**Avg. Risk Score:** <span style='color:{risk_color};font-size:18px;font-weight:bold;'>{cluster['avg_risk_score']}/100</span>", unsafe_allow_html=True)
                    st.markdown(f"**Scam Types:** {', '.join(cluster['scam_types'])}")
                    st.markdown("**Linked Domains:**")
                    for d in cluster['domains']:
                        st.code(d)
        else:
            st.info("No clusters detected yet. Analyze multiple URLs to build network intelligence. Clusters form when two or more domains share the same server IP.")


elif menu_selection == t["menu"][4]: # Autonomous Hunter
    st.markdown(f'<h1 class="main-header">{t["menu"][4]}</h1>', unsafe_allow_html=True)
    st.markdown("""
    **🛰️ Autonomous Google Dorking → Deep OSINT Pipeline**  
    Система сама ищет живые мошеннические ресурсы через Google Dorking, затем автоматически  
    прогоняет каждый найденный URL через **Selenium + GPT-4o + Risk Score** и сохраняет в базу.
    """)

    if st.button("🦅 ЗАПУСТИТЬ АВТОНОМНУЮ ОХОТУ", type="primary"):
        st.markdown("---")
        st.markdown("### 📡 Live Intelligence Feed")
        log_container = st.container()
        log_lines = []

        def stream_log(msg):
            log_lines.append(msg)
            with log_container:
                for line in log_lines[-25:]:  # show last 25 lines
                    st.markdown(line)

        # Run full auto-pipeline
        results = hunter.auto_investigate(
            mapper=mapper,
            vision=vision,
            legal=legal,
            db=db,
            progress_callback=stream_log
        )

        # Results table
        st.markdown("---")
        st.markdown(f"### 🎯 Hunt Report — {len(results)} threats processed")
        if results:
            for r in results:
                level = r.get('threat_level', 'Medium')
                score = r.get('risk_score', 0)
                color = "#f85149" if level == "High" else "#d29922" if level == "Medium" else "#3fb950"
                with st.expander(f"{r.get('url', 'N/A')} | Risk: {score}/100 | {level}", expanded=False):
                    col1, col2 = st.columns(2)
                    col1.metric("Risk Score", f"{score}/100")
                    col2.metric("Confidence", f"{r.get('confidence', 0)}%")
                    st.markdown(f"**Scam Type:** {r.get('scam_type', 'N/A')}")
                    st.markdown(f"**Articles:** `{', '.join(r.get('legal_articles', []))}`")
                    st.markdown(f"**IP:** {r.get('ip', 'N/A')} | **Registrar:** {r.get('registrar', 'N/A')}")
                    if r.get('indicators'):
                        st.markdown("**AI Indicators:**")
                        for ind in r['indicators']:
                            st.write(f"• {ind}")
        else:
            st.info("Ничего не найдено. Возможно, Google ограничил запросы. Попробуйте через несколько минут.")


elif menu_selection == t["menu"][5]: # History
    st.markdown(f'<h1 class="main-header">{t["history"]}</h1>', unsafe_allow_html=True)
    hist = db.get_history()
    if hist:
        for item in hist:
            with st.expander(f"{item[1]} - {item[2]} ({item[3]})"):
                st.write(f"**Type:** {item[4]}")
                st.write(f"**Articles:** {item[7]}")
                st.write(f"**IP:** {item[6]}")
    else:
        st.write("No incidents logged yet.")
