
import requests
import re
from bs4 import BeautifulSoup


class BotInvestigator:
    def simulate_interaction(self, bot_url):
        """
        Performs real OSINT investigation of a Telegram bot/channel using HTTP.
        Extracts real info: description, links, phone numbers, and embedded URLs.
        """
        steps = []

        # Extract username from URL
        username = bot_url.rstrip("/").split("/")[-1]
        api_url = f"https://t.me/{username}"

        steps.append(f"[*] Target identified: {username}")
        steps.append(f"[*] Fetching public profile: {api_url}")

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(api_url, headers=headers, timeout=10)

            if resp.status_code != 200:
                steps.append(f"[!] HTTP {resp.status_code}: Could not reach target.")
                return steps

            soup = BeautifulSoup(resp.text, "html.parser")

            # Bot/channel name
            title_tag = soup.find("div", class_="tgme_page_title")
            if title_tag:
                steps.append(f"[+] Name: {title_tag.get_text(strip=True)}")

            # Description
            desc_tag = soup.find("div", class_="tgme_page_description")
            if desc_tag:
                desc_text = desc_tag.get_text(strip=True)
                steps.append(f"[+] Description: {desc_text[:300]}")

                # Extract embedded URLs
                links = re.findall(r"https?://\S+", desc_text)
                for link in links:
                    steps.append(f"[!!] Embedded URL found: {link}")

            # Subscriber/member count
            extra_tag = soup.find("div", class_="tgme_page_extra")
            if extra_tag:
                steps.append(f"[+] Stats: {extra_tag.get_text(strip=True)}")

            # Look for phone numbers
            full_text = soup.get_text()
            phones = re.findall(r"\+?\d[\d\s\-]{9,}\d", full_text)
            for ph in set(phones[:3]):
                steps.append(f"[!!] Phone number found: {ph.strip()}")

            # Look for other telegram links/bots mentioned
            tg_links = re.findall(r"t\.me/[A-Za-z0-9_]+", full_text)
            for tl in set(tg_links[:5]):
                if tl not in bot_url:
                    steps.append(f"[+] Related TG entity: https://{tl}")

            steps.append("[*] Investigation complete.")

        except Exception as e:
            steps.append(f"[!] Error during investigation: {str(e)}")

        return steps

    def get_hidden_urls(self, bot_url):
        """Extract all URLs found during investigation."""
        steps = self.simulate_interaction(bot_url)
        urls = []
        for step in steps:
            found = re.findall(r"https?://\S+", step)
            urls.extend(found)
        return list(set(urls))
