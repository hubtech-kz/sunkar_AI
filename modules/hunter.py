
import requests
import socket
import time as time_module
import re

try:
    from googlesearch import search as google_search
except ImportError:
    google_search = None


class SunkarHunter:
    def __init__(self):
        # Real OSINT Footprints (Dorks) targeting known scam patterns in KZ
        self.dorks = [
            'site:.xyz "kaspi" "бонус"',
            'inurl:aviator "казахстан" "ойнау"',
            '"казино" "казахстан" site:.digital',
            'site:.online "halyk" "выплата"',
            '"invest" "kz" "пассивный доход" site:.com',
            '"aviator" "получить" "kz" site:.top',
            '"casino" "казахстан" "бонус" site:.xyz',
            '"poker" OR "pokies" "kz" "зеркало"',
        ]

    # ─── HELPERS ────────────────────────────────────────────────────────────

    def domain_resolves(self, url):
        """DNS check — domain must actually exist."""
        try:
            domain = url.replace("https://", "").replace("http://", "").split("/")[0]
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

    def check_live(self, url):
        """HTTP check — server must respond."""
        try:
            r = requests.get(
                url, timeout=5, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True
            )
            return r.status_code < 400
        except Exception:
            return False

    # ─── DISCOVERY ─────────────────────────────────────────────────────────

    def discover_candidates(self, max_per_dork=3, progress_callback=None):
        """
        Real-time discovery via Google Dorking.
        Returns a list of live URLs that passed DNS + HTTP check.
        """
        candidates = set()

        if not google_search:
            return list(candidates)

        for i, dork in enumerate(self.dorks):
            if progress_callback:
                progress_callback(f"🔍 Dork {i+1}/{len(self.dorks)}: `{dork[:60]}...`")
            try:
                for url in google_search(dork, num_results=max_per_dork, lang="kk"):
                    if url not in candidates and self.domain_resolves(url) and self.check_live(url):
                        candidates.add(url)
                        if progress_callback:
                            progress_callback(f"✅ Found live target: `{url}`")
            except Exception:
                # Google may rate-limit — skip and continue
                time_module.sleep(2)
                continue
            time_module.sleep(1.5)  # Be polite to Google

        return list(candidates)

    # ─── AUTO-PIPELINE ──────────────────────────────────────────────────────

    def auto_investigate(self, mapper, vision, legal, db, progress_callback=None):
        """
        Full autonomous investigation pipeline:
        1. Google Dorking → live URL candidates
        2. Selenium scraping (bypass Cloudflare)
        3. GPT-4o analysis → threat_level, scam_type, indicators
        4. Rule-based Risk Score (0–100)
        5. Save to DB
        Returns: list of result dicts
        """
        all_results = []

        # STEP 1: Discovery
        if progress_callback:
            progress_callback("🛰️ **STEP 1:** Starting Google Dorking discovery...")

        candidates = self.discover_candidates(progress_callback=progress_callback)

        if not candidates:
            if progress_callback:
                progress_callback("⚠️ No live targets found via Dorking. Possible Google rate-limit.")
            return []

        if progress_callback:
            progress_callback(f"🎯 Found **{len(candidates)}** live targets. Beginning deep scan...")

        # STEP 2-5: Deep scan per URL
        for url in candidates:
            try:
                if progress_callback:
                    progress_callback(f"\n🔬 **SCANNING:** `{url}`")

                # Infrastructure scan
                mapper_data = mapper.analyze_url(url)
                domain = mapper_data.get('domain', url)

                # Selenium web scrape
                if progress_callback:
                    progress_callback(f"  🌐 Headless browser loading...")
                web_data = mapper.get_website_content(url)
                context = {**mapper_data, **web_data}

                # GPT-4o analysis
                if progress_callback:
                    progress_callback(f"  🤖 GPT-4o analyzing content...")
                vision_result = vision.analyze_text(context)

                # Risk scoring
                threat_level = vision_result.get('threat_level', 'Medium')
                indicators = vision_result.get('indicators', [])
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

                # Save to DB immediately
                db.log_incident(result)

                level_emoji = "🔴" if threat_level == "High" else "🟡" if threat_level == "Medium" else "🟢"
                if progress_callback:
                    progress_callback(
                        f"  {level_emoji} **Verdict:** {threat_level} | **Risk:** {risk_result['score']}/100 | {', '.join(legal_articles[:2])}"
                    )

                all_results.append(result)

            except Exception as e:
                if progress_callback:
                    progress_callback(f"  ⚠️ Failed to analyze `{url}`: {str(e)[:80]}")
                continue

        if progress_callback:
            progress_callback(f"\n✅ **Hunt complete.** Analyzed {len(all_results)} threats. Results saved to database.")

        return all_results

    # Legacy method kept for compatibility
    def proactive_search(self):
        return self.discover_candidates()
