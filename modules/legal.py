
class LegalEvidence:
    def __init__(self):
        self.uk_rk = {
            "190": "Мошенничество (Fraud)",
            "217": "Создание и руководство финансовой (инвестиционной) пирамидой (Financial Pyramid)",
            "307": "Организация незаконного игорного бизнеса (Illegal Gambling)"
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
            if any(w in ind_lower for w in ["casino", "betting", "aviator", "казино", "slot", "gambling", "игор"]):
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

        # Empty indicators AND no clear domain keywords → needs manual check
        if not indicators:
            return ["Требует ручной проверки (Manual Review Required)"]

        return ["Проверка продолжается"]

    def generate_report(self, data):
        """
        Generates a draft report based on SUNQAR AI logic.
        """
        from datetime import date

        threat_level = data.get('threat_level', 'High')
        today = date.today().strftime('%Y-%m-%d')
        
        # ЛОГИКА ФОРМИРОВАНИЯ ЗАКЛЮЧЕНИЯ
        if threat_level == "Low" or "Законодательство соблюдено" in str(data.get('legal_articles')):
            title = "ОТЧЕТ О СООТВЕТСТВИИ (SAFETY REPORT)"
            status_text = "СООТВЕТСТВУЕТ (CLEAN)"
            conclusion = "Заключение: В ходе анализа SUNQAR AI нарушений законодательства Республики Казахстан не выявлено. Ресурс признан легитимным (Safe). Блокировка не требуется."
        else:
            title = "РАПОРТ ОБ ОБНАРУЖЕНИИ ПРИЗНАКОВ ПРЕСТУПЛЕНИЯ"
            status_text = f"КРИТИЧЕСКИЙ (DANGER: {threat_level})"
            conclusion = "Заключение: Обнаружены признаки нарушения законодательства РК (Экономические преступления). Рекомендуется незамедлительная блокировка ресурса и передача цифровых следов в АФМ РК."

        report = f"""
# {title}
**Дата проверки:** {today}
**Интеллектуальная система:** SUNQAR AI OSINT Agent

## 1. ОБЪЕКТ АНАЛИЗА
**Адрес / Контент:** {data.get('url', 'Медиа-загрузка')}
**Технический отпечаток (IP):** {data.get('ip', 'N/A')}

## 2. АНАЛИТИЧЕСКИЙ СТАТУС
**Уровень угрозы:** {status_text}
**Квалификация нарушений:** {", ".join(data.get('legal_articles', []))}

## 3. ОБОСНОВАНИЕ ВЕРДИКТА (AI INDICATORS)
{chr(10).join(['- ' + str(i) for i in data.get('indicators', []) if i]) if data.get('indicators') else '- Признаков преступлений не выявлено.'}

## 4. ИНФРАСТРУКТУРНЫЕ ДАННЫЕ
- **Registrar (Регистратор):** {data.get('registrar', 'N/A')}
- **Сервер (IP):** {data.get('ip', 'N/A')}
- **Цифровые маркеры:** {", ".join(data.get('markers', [])) if data.get('markers') else 'Отсутствуют'}

## ЗАКЛЮЧЕНИЕ
{conclusion}
        """
        return report
