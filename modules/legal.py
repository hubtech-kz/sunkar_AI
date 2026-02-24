
class LegalEvidence:
    def __init__(self):
        self.uk_rk = {
            "190": "Мошенничество (Fraud)",
            "217": "Создание и руководство финансовой (инвестиционной) пирамидой (Financial Pyramid)",
            "307": "Организация незаконного игорного бизнеса (Illegal Gambling)"
        }

        # Rule-based indicator → article + score mapping
        # Each rule has: keywords, article, weight (contribution to 0–100 score), explanation
        self.rules = [
            # GAMBLING (Art. 307)
            {"keywords": ["casino", "казино", "casin"], "article": "Ст. 307 УК РК", "weight": 40, "label": "Gambling platform (casino)"},
            {"keywords": ["slot", "слот", "aviator"], "article": "Ст. 307 УК РК", "weight": 35, "label": "Gambling (slot/aviator)"},
            {"keywords": ["betting", "ставки", "букмекер", "bookmaker"], "article": "Ст. 307 УК РК", "weight": 35, "label": "Illegal bookmaker"},
            {"keywords": ["poker", "покер"], "article": "Ст. 307 УК РК", "weight": 30, "label": "Gambling (poker)"},
            {"keywords": ["bonus", "бонус", "фриспин", "freespin"], "article": "Ст. 307 УК РК", "weight": 15, "label": "Gambling bonus incentive"},
            # PYRAMID (Art. 217)
            {"keywords": ["pyramid", "пирамид", "инвест", "invest"], "article": "Ст. 217 УК РК", "weight": 40, "label": "Investment pyramid"},
            {"keywords": ["roi", "пассивный доход", "passive income"], "article": "Ст. 217 УК РК", "weight": 30, "label": "High ROI passive income"},
            {"keywords": ["referral", "реферал", "привлеки друга"], "article": "Ст. 217 УК РК", "weight": 20, "label": "Referral recruitment chain"},
            # PHISHING (Art. 190)
            {"keywords": ["halyk", "халык"], "article": "Ст. 190 УК РК", "weight": 50, "label": "Halyk Bank phishing clone"},
            {"keywords": ["kaspi", "каспи"], "article": "Ст. 190 УК РК", "weight": 50, "label": "Kaspi Bank phishing clone"},
            {"keywords": ["egov", "электронное правительство", "e-gov"], "article": "Ст. 190 УК РК", "weight": 50, "label": "Government portal phishing"},
            {"keywords": ["fake", "phishing", "клон", "фейк", "scam", "fraud"], "article": "Ст. 190 УК РК", "weight": 35, "label": "Fraud / fake clone"},
            # DOMAIN SUSPICION (no-article, adds to score)
            {"keywords": ["mirror", "зеркало"], "article": None, "weight": 20, "label": "Mirror site (illegal activity indicator)"},
            {"keywords": [".xyz", ".top", ".digital", ".site"], "article": None, "weight": 10, "label": "Suspicious TLD"},
        ]

    def compute_risk_score(self, indicators, domain="", threat_level="Medium"):
        """
        Deterministic Rule-Based Risk Score (0–100).
        Returns: score (int), matched_rules (list of dicts), articles (list of str)
        """
        score = 0
        matched_rules = []
        articles = set()
        combined_text = " ".join(indicators).lower() + " " + domain.lower()

        for rule in self.rules:
            if any(kw in combined_text for kw in rule["keywords"]):
                score += rule["weight"]
                matched_rules.append({
                    "label": rule["label"],
                    "article": rule["article"],
                    "weight": rule["weight"],
                })
                if rule["article"]:
                    articles.add(rule["article"])

        # Clamp to 100
        score = min(score, 100)

        # If LLM says High but rules didn't catch it — give minimum 60
        if threat_level == "High" and score < 60:
            score = 60
        # If LLM says Low and rules are low — cap at 25
        if threat_level == "Low" and score > 25:
            score = 25

        # Confidence: based on how many rules fired
        confidence = round(min(85 + len(matched_rules) * 2, 99), 1)
        if not matched_rules:
            confidence = 55.0  # Uncertain — no rules matched

        return {
            "score": score,
            "confidence": confidence,
            "matched_rules": matched_rules,
            "articles": list(articles),
        }

    def qualify_offense(self, indicators, domain=""):
        """
        Qualify the findings based on UK RK.
        """
        # Only mark Compliant if AI EXPLICITLY says clean
        explicitly_safe = indicators and any(
            x in ["No threats detected", "Legit", "Verified", "Safe", "Official institution"]
            for x in indicators
        )
        if explicitly_safe:
            return ["Законодательство соблюдено (Compliance)"]

        qualification = []

        # 1. Keyword scan of AI-returned indicators
        for ind in indicators:
            ind_lower = str(ind).lower()
            if any(w in ind_lower for w in ["pyramid", "investment", "доход", "табыс", "roi", "passive"]):
                qualification.append("Ст. 217 УК РК")
            if any(w in ind_lower for w in ["casino", "betting", "aviator", "казино", "slot", "gambling", "игор", "poker"]):
                qualification.append("Ст. 307 УК РК")
            if any(w in ind_lower for w in ["fake", "fraud", "scam", "clone", "клон", "фейк", "phishing"]):
                qualification.append("Ст. 190 УК РК")

        # 2. Backup: analyze domain name directly
        if not qualification and domain:
            d = domain.lower()
            if any(w in d for w in ["casino", "casin", "slot", "aviator", "betting", "poker"]):
                qualification.append("Ст. 307 УК РК")
            if any(w in d for w in ["invest", "profit", "earn"]):
                qualification.append("Ст. 217 УК РК")
            if any(w in d for w in ["halyk", "kaspi", "egov"]):
                qualification.append("Ст. 190 УК РК (Фишинг)")

        if qualification:
            return list(set(qualification))

        # Empty → needs manual
        if not indicators:
            return ["Требует ручной проверки (Manual Review Required)"]

        return ["Проверка продолжается"]

    def generate_report(self, data):
        """
        Generates a professional legal report with risk score and explainability.
        """
        from datetime import date

        threat_level = data.get('threat_level', 'High')
        today = date.today().strftime('%Y-%m-%d')
        risk_score = data.get('risk_score', 0)
        confidence = data.get('confidence', 0)
        matched_rules = data.get('matched_rules', [])

        # Risk level label
        if risk_score >= 75:
            risk_label = "КРИТИЧЕСКИЙ (CRITICAL)"
        elif risk_score >= 50:
            risk_label = "ВЫСОКИЙ (HIGH)"
        elif risk_score >= 25:
            risk_label = "СРЕДНИЙ (MEDIUM)"
        else:
            risk_label = "НИЗКИЙ (LOW)"

        # Report type
        if threat_level == "Low" or "Законодательство соблюдено" in str(data.get('legal_articles')):
            title = "ОТЧЕТ О СООТВЕТСТВИИ (SAFETY REPORT)"
            status_text = "СООТВЕТСТВУЕТ (CLEAN)"
            conclusion = "Заключение: В ходе анализа SUNQAR AI нарушений законодательства Республики Казахстан не выявлено. Ресурс признан легитимным (Safe). Блокировка не требуется."
        else:
            title = "РАПОРТ ОБ ОБНАРУЖЕНИИ ПРИЗНАКОВ ПРЕСТУПЛЕНИЯ"
            status_text = f"КРИТИЧЕСКИЙ (DANGER: {threat_level})"
            conclusion = "Заключение: Обнаружены признаки нарушения законодательства РК (Экономические преступления). Рекомендуется незамедлительная блокировка ресурса и передача цифровых следов в АФМ РК."

        # Explainability block
        explainability_lines = []
        for rule in matched_rules:
            article_text = f"→ {rule['article']}" if rule['article'] else "→ Дополнительный риск-фактор"
            explainability_lines.append(f"  • [{rule['weight']:+d} балл] {rule['label']} {article_text}")
        explainability_block = "\n".join(explainability_lines) if explainability_lines else "  Детальный анализ не выявил совпадений с базой правил."

        report = f"""
# {title}
**Дата проверки:** {today}
**Интеллектуальная система:** SUNQAR AI OSINT Agent v2.0

## 1. ОБЪЕКТ АНАЛИЗА
**Адрес / Контент:** {data.get('url', 'Медиа-загрузка')}
**Технический отпечаток (IP):** {data.get('ip', 'N/A')}

## 2. АНАЛИТИЧЕСКИЙ СТАТУС
**Уровень угрозы:** {status_text}
**Риск-скор (0–100):** {risk_score} / 100 [{risk_label}]
**Уверенность системы:** {confidence}%
**Квалификация нарушений:** {", ".join(data.get('legal_articles', []))}

## 3. ОБОСНОВАНИЕ ВЕРДИКТА (EXPLAINABILITY LAYER)
### 3a. Индикаторы угрозы (AI):
{chr(10).join(['- ' + str(i) for i in data.get('indicators', []) if i]) if data.get('indicators') else '- Признаков преступлений не выявлено.'}

### 3b. Rule-Based детализация (Какие признаки → Какая статья):
{explainability_block}

## 4. ИНФРАСТРУКТУРНЫЕ ДАННЫЕ
- **Registrar (Регистратор):** {data.get('registrar', 'N/A')}
- **Сервер (IP):** {data.get('ip', 'N/A')}
- **Цифровые маркеры:** {", ".join(data.get('markers', [])) if data.get('markers') else 'Отсутствуют'}

## ЗАКЛЮЧЕНИЕ
{conclusion}
        """
        return report
