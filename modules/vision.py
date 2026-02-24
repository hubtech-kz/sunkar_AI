import google.generativeai as genai
from openai import OpenAI
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

class VisionRecon:
    def __init__(self, gemini_key=None, openai_key=None):
        self.gemini_key = gemini_key or os.getenv("GOOGLE_API_KEY")
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
            
        if self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)
        else:
            self.openai_client = None

    def analyze_image(self, image_path):
        """
        Analyzes an image for scam indicators using hybrid AI.
        """
        if not self.gemini_model and not self.openai_client:
            return {
                "threat_level": "None",
                "scam_type": "No AI Provider",
                "indicators": ["API keys missing"],
                "explanation": "Please provide API keys in the .env file to enable real analysis."
            }

        try:
            img = Image.open(image_path)
            
            # 1. Scan with Gemini
            prompt = """
            IMPORTANT CONTEXT: Currently, in Kazakhstan (Turkestan), an AI Hackathon by DER is taking place with a prize fund of 10,000,000 KZT. This is a 100% LEGITIMATE government-supported event. Do not mark AI-Hackathon, Hubtech.kz, AstanaHub, or AYU.EDU.KZ as a scam.
            
            Analyze this image for economic crime indicators in Kazakhstan.
            Detect: Deepfakes, fake banking, scam keywords.
            If looks like the AI Hackathon flyer, identify it as 'Safe / Low Threat'.
            """
            gemini_res = self.gemini_model.generate_content([prompt, img]) if self.gemini_model else "Vision scan skipped."
            gemini_text = gemini_res.text if hasattr(gemini_res, 'text') else str(gemini_res)

            # 2. Refined Reasoning with GPT-4o
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                  model="gpt-4o",
                  messages=[
                    {"role": "system", "content": "You are SUNQAR AI. Provide a technical crime report in JSON based on visual context provided by Gemini vision scan."},
                    {"role": "user", "content": f"Vision Input: {gemini_text}. Return threat_level (High/Medium/Low), scam_type, indicators (list), and explanation."}
                  ],
                  response_format={ "type": "json_object" }
                )
                import json
                return json.loads(response.choices[0].message.content)
            
            # Fallback to Gemini text if GPT-4o is missing
            return {
                "threat_level": "Low",
                "scam_type": "Vision Detection",
                "indicators": [gemini_text[:100]],
                "explanation": gemini_text
            }

        except Exception as e:
            return {"error": str(e)}

    def analyze_text(self, context_data):
        """
        Analyzes technical and text data for scams using GPT-4o.
        """
        if not self.openai_client:
            return {
                "threat_level": "None",
                "scam_type": "No GPT-4o Client",
                "indicators": ["API key missing"],
                "explanation": "Please provide OPENAI_API_KEY to enable text-based OSINT analysis."
            }

        domain = context_data.get('domain', '')
        title = context_data.get('title', 'Unknown')
        text_content = context_data.get('text_content', '')
        
        # If scraping failed or returned no content, still analyze the domain name itself
        content_note = "Page content was blocked/unavailable. Analyze based on domain name and URL structure only." if not text_content or text_content.strip() == "" else f"Page text snippet:\n{text_content[:2000]}"
        
        prompt = f"""
        You are SUNQAR AI, an elite OSINT investigator for Kazakhstan's DER/AFM agency.
        Analyze this URL and data for signs of illegal activity under Kazakhstan law.
        
        WHITELIST (DO NOT flag as threat):
        - Domains ending in .gov.kz, .edu.kz
        - Known legitimate: hubtech.kz, astanahub.com, ayu.edu.kz, derkhackathon.kz
        
        ANALYZE:
        - Domain: {domain}
        - Page Title: {title}
        - {content_note}
        
        CRITICAL RULES for Kazakhstan (UK RK):
        1. GAMBLING: If you see "Казино", "Casino", "Poker", "Slot", "Aviator", "1xBet", "Pokerdom", "Букмекер" or betting links -> High Threat (Art. 307). Mirror sites (random domain prefixes) are clear signs of illegal activity.
        2. PYRAMID: High ROI, referrals, "Invest and earn" -> High Threat (Art. 217).
        3. PHISHING: Fake bank clones (Kaspi, Halyk) -> High Threat (Art. 190).
        
        IMPORTANT: Even if page text is short, identifying keywords like 'Pokerdom' or 'Бонус за регистрацию' is enough for a 'High' threat verdict.
        
        Return JSON only: {{"threat_level": "High"|"Medium"|"Low", "scam_type": "...", "indicators": ["..."], "explanation": "..."}}
        """
        try:
            response = self.openai_client.chat.completions.create(
              model="gpt-4o",
              messages=[
                {"role": "system", "content": "You are SUNQAR AI, an elite security investigator for Kazakhstan DER."},
                {"role": "user", "content": prompt}
              ],
              response_format={ "type": "json_object" }
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}

    def _mock_analysis(self):
        # Kept only for internal reference, not called during normal operation anymore
        return {
            "threat_level": "Low",
            "scam_type": "Safety Check",
            "indicators": ["No threats detected"],
            "explanation": "Real AI analysis is enabled."
        }
