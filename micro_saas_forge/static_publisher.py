import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "curated_insights_global.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "shipmicro_site", "public")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index_global.html")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TITAN SaaS Radar - Top High-ROI Tools for Founders</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Inter', 'sans-serif'],
                    }},
                    colors: {{
                        titan: {{
                            50: '#f0fdf4',
                            100: '#dcfce7',
                            500: '#22c55e',
                            600: '#16a34a',
                            900: '#14532d',
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{ background-color: #f8fafc; font-family: 'Inter', sans-serif; }}
        .glass-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(226, 232, 240, 0.8);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
            transition: all 0.3s ease;
        }}
        .glass-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            border-color: #cbd5e1;
        }}
        .score-badge {{
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        }}
    </style>
</head>
<body class="text-slate-800 antialiased selection:bg-titan-200 selection:text-titan-900 pb-20">
    
    <!-- Header -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center gap-2">
                <div class="bg-slate-900 text-white font-bold p-1.5 rounded text-xs tracking-wider">TITAN</div>
                <span class="font-bold text-lg tracking-tight text-slate-900">SaaS Radar <span class="text-titan-600">Global</span></span>
            </div>
            <div class="text-sm font-medium text-slate-500">
                Updated: {update_time}
            </div>
        </div>
    </header>

    <!-- Hero -->
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <div class="text-center max-w-3xl mx-auto">
            <h1 class="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 mb-4">
                The Ultimate <span class="text-transparent bg-clip-text bg-gradient-to-r from-titan-500 to-emerald-700">Problem-Solving SaaS</span> Leaderboard
            </h1>
            <p class="text-lg text-slate-600 mb-8 leading-relaxed">
                Based on 10,000+ real founder complaints analyzed by AI across Reddit, we've matched the biggest pain points with the perfect high-ROI SaaS solutions.
            </p>
        </div>
    </div>

    <!-- Cards Container -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {cards_html}
    </div>

    <!-- Footer -->
    <footer class="mt-24 border-t border-slate-200 bg-white py-12">
        <div class="max-w-5xl mx-auto px-4 text-center">
            <p class="text-slate-500 text-sm">Powered by TITAN Engine (Global Edition MVP)</p>
            <p class="text-slate-400 text-xs mt-2">100% Data-Driven SaaS Matching</p>
        </div>
    </footer>

</body>
</html>
"""

CARD_TEMPLATE = """
        <div class="glass-card rounded-2xl overflow-hidden relative">
            <div class="absolute top-0 right-0 p-4">
                <div class="score-badge text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-sm flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clip-rule="evenodd" />
                    </svg>
                    Match Score {score}
                </div>
            </div>
            
            <div class="p-6 md:p-8">
                <!-- Label & Pain Point -->
                <div class="mb-5 pr-24">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-red-100 text-red-800 mb-3 border border-red-200">
                        Top Pain Point
                    </span>
                    <h2 class="text-xl md:text-2xl font-bold text-slate-900 leading-tight">
                        {pain_point}
                    </h2>
                </div>
                
                <!-- Evidence Box -->
                <div class="bg-slate-50 border border-slate-100 rounded-lg p-4 mb-6 relative">
                    <div class="absolute -left-2 -top-2 text-slate-300">
                        <svg class="h-8 w-8" fill="currentColor" viewBox="0 0 32 32" aria-hidden="true"><path d="M9.352 4C4.456 7.456 1 13.12 1 19.36c0 5.088 3.072 8.064 6.624 8.064 3.36 0 5.856-2.688 5.856-5.856 0-3.168-2.208-5.472-5.088-5.472-.576 0-1.344.096-1.536.192.48-3.264 3.552-7.104 6.624-9.024L9.352 4zm16.512 0c-4.8 3.456-8.256 9.12-8.256 15.36 0 5.088 3.072 8.064 6.624 8.064 3.264 0 5.856-2.688 5.856-5.856 0-3.168-2.304-5.472-5.184-5.472-.576 0-1.248.096-1.44.192.48-3.264 3.456-7.104 6.528-9.024L25.864 4z" /></svg>
                    </div>
                    <p class="text-slate-600 text-sm italic pl-6">
                        Real Complaint: "{evidence}"
                    </p>
                </div>
                
                <!-- Solution & CTA -->
                <div class="bg-titan-50 rounded-xl p-5 md:p-6 border border-titan-100 flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div class="flex-1">
                        <div class="text-titan-900 font-semibold text-lg mb-1 flex items-center gap-2">
                            <svg class="w-5 h-5 text-titan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            TITAN Recommend: {solution_name}
                        </div>
                        <p class="text-titan-800 text-sm font-medium mt-2">
                            {pitch_copy}
                        </p>
                    </div>
                    <div class="flex-shrink-0 flex flex-col items-center gap-2">
                        <a href="{affiliate_url}" target="_blank" rel="noopener noreferrer" class="inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-slate-900 hover:bg-slate-800 shadow-sm hover:shadow transition-all w-full md:w-auto">
                            Get This Tool
                            <svg class="ml-2 -mr-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                        </a>
                        <span class="text-[10px] text-slate-400 font-mono hidden">Partner Rate: {commission_rate}</span>
                    </div>
                </div>
            </div>
        </div>
"""

def main():
    print("="*60)
    print("TITAN Engine - Static Publisher (Global Edition MVP)")
    print("="*60)
    
    if not os.path.exists(INPUT_FILE):
        logging.error(f"Input file not found: {INPUT_FILE}. Please run titan_analyzer.py first.")
        return
        
    logging.info(f"Loading insights from {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        insights = json.load(f)
        
    if not insights:
        logging.error("No insights found to publish.")
        return
        
    # Sort insights by match score descending
    insights.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    
    logging.info(f"Generating HTML for {len(insights)} insight cards...")
    cards_html = ""
    for insight in insights:
        cards_html += CARD_TEMPLATE.format(
            score=insight.get("match_score", 0),
            pain_point=insight.get("pain_point", "N/A").replace('"', '&quot;'),
            evidence=insight.get("evidence", "N/A").replace('"', '&quot;'),
            solution_name=insight.get("solution_name", "N/A").replace('"', '&quot;'),
            pitch_copy=insight.get("pitch_copy", "N/A").replace('"', '&quot;'),
            affiliate_url=insight.get("affiliate_url", "#").replace('"', '&quot;'),
            commission_rate=insight.get("commission_rate", "N/A").replace('"', '&quot;')
        )
        
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Fill main template
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    final_html = HTML_TEMPLATE.format(
        update_time=now_str,
        cards_html=cards_html
    )
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    logging.info(f"Successfully published static site to {OUTPUT_FILE}")
    print(f"\n✅ Created high-conversion GLOBAL HTML page at: {OUTPUT_FILE}")
    print("👉 Ready to be tested on Reddit and Twitter!")

if __name__ == "__main__":
    main()
