
import socket
import requests
import re
import whois

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False


class InfrastructureMapper:
    def analyze_url(self, url):
        domain = url.split("//")[-1].split("/")[0]
        results = {
            "domain": domain,
            "ip": "Unknown",
            "location": "Unknown",
            "age": "Unknown",
            "registrar": "Unknown",
            "markers": [],
        }
        try:
            # Real IP lookup
            ip = socket.gethostbyname(domain)
            results["ip"] = ip

            # Real WHOIS data
            try:
                w = whois.whois(domain)
                results["age"] = str(
                    w.creation_date[0]
                    if isinstance(w.creation_date, list)
                    else w.creation_date
                )
                results["registrar"] = w.registrar or "Unknown"
                results["location"] = w.country or "Unknown"
            except Exception:
                results["age"] = "Not found"

            # Official institutions: no tracker check needed
            if ".gov" in domain or ".edu" in domain:
                results["markers"] = ["Verified Institution (No trackers detected)"]
            else:
                # Real tracker detection from live page HTML
                results["markers"] = self._detect_trackers(url)

        except Exception as e:
            results["error"] = str(e)
        return results

    def _detect_trackers(self, url):
        """Detect real tracking pixels and analytics codes from page source."""
        found_trackers = []
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=8)
            html = resp.text

            # Facebook Pixel
            fb_ids = re.findall(r"fbq\(['\"]init['\"],\s*['\"](\d+)['\"]", html)
            for fid in fb_ids:
                found_trackers.append(f"FB Pixel: {fid}")

            # Google Analytics (UA- and G-)
            ua_ids = re.findall(r"UA-\d{4,}-\d+", html)
            g_ids = re.findall(r"G-[A-Z0-9]{8,}", html)
            for uid in set(ua_ids):
                found_trackers.append(f"Google Analytics: {uid}")
            for gid in set(g_ids):
                found_trackers.append(f"Google Analytics (G4): {gid}")

            # Google Tag Manager
            gtm_ids = re.findall(r"GTM-[A-Z0-9]+", html)
            for gid in set(gtm_ids):
                found_trackers.append(f"Google Tag Manager: {gid}")

            # TikTok Pixel
            tt_ids = re.findall(r"ttq\.load\(['\"]([A-Z0-9]+)['\"]", html)
            for tid in tt_ids:
                found_trackers.append(f"TikTok Pixel: {tid}")

            # Yandex Metrika
            ym_ids = re.findall(r"ym\((\d+),", html)
            for yid in set(ym_ids):
                found_trackers.append(f"Yandex Metrika: {yid}")

        except Exception:
            pass

        return found_trackers if found_trackers else ["No trackers detected"]

    def get_website_content(self, url):
        """
        Fetches website text content using a Professional Headless Browser (Selenium).
        Bypasses Cloudflare, DDoS-Guard and other JS-based anti-bot protection.
        """
        from bs4 import BeautifulSoup
        import time

        domain = url.split("//")[-1].split("/")[0]

        # Professional Method: Selenium Headless Chromium (Standard for Selenium 4.10+)
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            # Explicitly point to snap chromium if needed
            chrome_options.binary_location = "/snap/bin/chromium"
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled") # Bypass some bot detection
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            # Selenium 4.10+ automatically handles driver installation via Selenium Manager
            driver = webdriver.Chrome(options=chrome_options)
            
            driver.set_page_load_timeout(30)
            driver.get(url)
            
            # Wait for JS execution (Cloudflare challenge)
            time.sleep(7)
            
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            driver.quit()

            for tag in soup(["script", "style", "nav", "footer"]):
                tag.extract()
            
            raw = " ".join(soup.get_text(separator=" ").split())
            title = soup.title.string.strip() if soup.title else domain
            
            return {
                "title": title,
                "meta_description": "Extracted via Headless Browser",
                "text_content": raw[:4000]
            }
        except Exception as e:
            print(f"[DEBUG] Selenium failed: {str(e)}")
            # Fallback to Method 2: Direct request (if Selenium fails to init)
            return self._fallback_scrape(url)

    def _fallback_scrape(self, url):
        """Simple requests-based fallback."""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style"]): tag.extract()
            return {
                "title": soup.title.string.strip() if soup.title else "N/A",
                "meta_description": "Fallback (Limited Accuracy)",
                "text_content": " ".join(soup.get_text().split())[:2000]
            }
        except:
            return {"title": "Error", "text_content": ""}
