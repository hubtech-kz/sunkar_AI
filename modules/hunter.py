
import requests
import socket
import time as time_module
import itertools

try:
    from googlesearch import search as google_search
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class SunkarHunter:
    def __init__(self):
        # Google Dorks (used if Google works, as a supplement)
        self.dorks = [
            'site:.xyz "kaspi" "бонус"',
            'inurl:aviator "казахстан"',
            '"казино" "казахстан" site:.digital',
            'site:.online "halyk" "выплата"',
            '"invest" "kz" "пассивный доход" site:.com',
        ]

        # ─── PROFESSIONAL DOMAIN PATTERN ENGINE ───────────────────────────────
        # Known scam brand prefixes and suffixes used in KZ criminal ecosystem
        self._brand_prefixes = [
            "1xbet", "mostbet", "melbet", "pin-up", "pinup", "pokerdom",
            "admiral", "vulkan", "casino", "aviator", "slot", "lucky", "bet",
            "win", "boom", "kz-casino", "kaspi-win", "bonus-kz", "invest-kz",
        ]
        self._brand_suffixes = [
            "-kz", "kz", "-kazahstan", "-online", "-mirror", "-login",
            "2025", "2026", "-official", "-games", "-play", "-club",
        ]
        self._tlds = [
            ".top", ".xyz", ".digital", ".online", ".site",
            ".live", ".bet", ".win", ".casino",
        ]

    # ─── HELPERS ────────────────────────────────────────────────────────────

    def domain_resolves(self, url):
        try:
            domain = url.replace("https://", "").replace("http://", "").split("/")[0]
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

    def check_live(self, url):
        try:
            r = requests.get(url, timeout=4, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
            return r.status_code < 400
        except Exception:
            return False

    # ─── DOMAIN PATTERN GENERATOR ─────────────────────────────────────────

    def generate_candidate_domains(self, max_candidates=50, progress_callback=None):
        """
        Generates likely scam domain candidates based on known patterns
        in the Kazakhstan criminal domain ecosystem.
        Validates each via DNS + HTTP.
        """
        candidates = []
        checked = 0

        if progress_callback:
            progress_callback("🧬 **Generating domain pattern candidates** from known KZ scam ecosystem...")

        # Generate combinations
        combos = []
        for prefix in self._brand_prefixes:
            for tld in self._tlds:
                combos.append(f"https://{prefix}{tld}")
            for suffix in self._brand_suffixes:
                for tld in self._tlds:
                    combos.append(f"https://{prefix}{suffix}{tld}")

        # Shuffle and limit
        import random
        random.shuffle(combos)
        combos = combos[:max_candidates * 3]  # check 3x more than target

        for url in combos:
            if len(candidates) >= max_candidates:
                break
            checked += 1

            if self.domain_resolves(url):
                if self.check_live(url):
                    candidates.append(url)
                    if progress_callback:
                        progress_callback(f"✅ Live target discovered: `{url}`")

        if progress_callback:
            progress_callback(f"🔬 Checked {checked} domain patterns, found {len(candidates)} live targets.")

        return candidates

    # ─── GOOGLE DORKING (supplement if available) ─────────────────────────

    def discover_via_google(self, max_per_dork=3, progress_callback=None):
        if not GOOGLE_AVAILABLE:
            return []
        candidates = set()
        for i, dork in enumerate(self.dorks):
            if progress_callback:
                progress_callback(f"🔍 Dork {i+1}/{len(self.dorks)}: `{dork[:60]}`")
            try:
                for url in google_search(dork, num_results=max_per_dork, lang="kk"):
                    if url not in candidates and self.domain_resolves(url):
                        candidates.add(url)
            except Exception:
                time_module.sleep(2)
                continue
            time_module.sleep(1)
        return list(candidates)

    # ─── AUTO-PIPELINE ──────────────────────────────────────────────────────

    def auto_investigate(self, mapper, vision, legal, db, progress_callback=None):
        """
        Full autonomous investigation pipeline:
        1. Domain Pattern Generation + Google Dorking (if available) → live candidates
        2. Selenium scraping (bypass Cloudflare)
        3. GPT-4o analysis → threat_level, scam_type, indicators
        4. Rule-based Risk Score (0–100)
        5. Save to DB automatically
        """
        all_results = []

        if progress_callback:
            progress_callback("🛰️ **PHASE 1:** Domain intelligence gathering...")

        # METHOD A: Pattern-based candidate generation (always works)
        candidates = set(self.generate_candidate_domains(max_candidates=15, progress_callback=progress_callback))

        # METHOD B: Google Dorking (if available, as supplement)
        google_hits = self.discover_via_google(progress_callback=progress_callback)
        candidates.update(google_hits)

        candidates = list(candidates)

        if not candidates:
            if progress_callback:
                progress_callback("⚠️ No live domains found. Check your network connection.")
            return []

        if progress_callback:
            progress_callback(f"\n🎯 **PHASE 2:** Found **{len(candidates)}** live targets. Starting deep OSINT scan...")

        for url in candidates:
            try:
                if progress_callback:
                    progress_callback(f"\n🔬 **SCANNING:** `{url}`")

                # Infrastructure scan
                mapper_data = mapper.analyze_url(url)
                domain = mapper_data.get('domain', url)

                # Selenium/HTTP web scrape
                if progress_callback:
                    progress_callback(f"  🌐 Loading page via Headless Browser...")
                web_data = mapper.get_website_content(url)
                context = {**mapper_data, **web_data}

                # GPT-4o analysis
                if progress_callback:
                    progress_callback(f"  🤖 Running GPT-4o threat analysis...")
                vision_result = vision.analyze_text(context)
                threat_level = vision_result.get('threat_level', 'Medium')
                indicators = vision_result.get('indicators', [])

                # Skip obviously safe results
                if threat_level == "Low" and not indicators:
                    if progress_callback:
                        progress_callback(f"  🟢 Clean — skipping.")
                    continue

                # Risk scoring
                risk_result = legal.compute_risk_score(indicators, domain=domain, threat_level=threat_level)
                legal_articles = legal.qualify_offense(indicators, domain=domain)
                if risk_result['articles']:
                    legal_articles = list(set(legal_articles + risk_result['articles']))

                result = {
                    'url': url,
                    'domain': domain,
                    'ip': mapper_data.get('ip', 'N/A'),
                    'registrar': mapper_data.get('registrar', 'N/A'),
                    'markers': mapper_data.get('markers', []),
                    'threat_level': threat_level,
                    'scam_type': vision_result.get('scam_type', 'Unknown'),
                    'indicators': indicators,
                    'explanation': vision_result.get('explanation', ''),
                    'legal_articles': legal_articles,
                    'risk_score': risk_result['score'],
                    'confidence': risk_result['confidence'],
                    'matched_rules': risk_result['matched_rules'],
                }

                db.log_incident(result)

                level_emoji = "🔴" if threat_level == "High" else "🟡"
                if progress_callback:
                    progress_callback(
                        f"  {level_emoji} **{threat_level}** | Risk: **{risk_result['score']}/100** | "
                        f"`{', '.join(legal_articles[:2]) or 'Checking...'}`"
                    )

                all_results.append(result)

            except Exception as e:
                if progress_callback:
                    progress_callback(f"  ⚠️ Error scanning `{url}`: {str(e)[:100]}")
                continue

        if progress_callback:
            high_count = sum(1 for r in all_results if r.get('threat_level') == 'High')
            progress_callback(
                f"\n\n✅ **Hunt Complete.** "
                f"Analyzed: **{len(all_results)}** | 🔴 High Threats: **{high_count}** | Saved to DB."
            )

        return all_results

    # Legacy compatibility
    def proactive_search(self):
        return self.generate_candidate_domains()
