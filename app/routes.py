# صفحات الموقع
from app import app
from flask import render_template_string
from app.matches import matches_db
from app.utils import get_today_matches, get_live_matches

# قالب HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏆 كأس العالم 2026</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0e1a, #1a1f35);
            color: #fff;
            font-family: Arial, sans-serif;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            padding: 40px;
            background: linear-gradient(145deg, #1a1f35, #2a3f5f);
            border-radius: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 215, 0, 0.2);
        }
        .header h1 { font-size: 3em; color: #ffd700; }
        .header p { color: #aaa; font-size: 1.2em; }
        .section-title {
            font-size: 2em;
            color: #ffd700;
            margin: 30px 0 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 215, 0, 0.2);
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        .card {
            background: linear-gradient(145deg, #1a1f35, #252a45);
            padding: 25px;
            border-radius: 18px;
            border: 1px solid #2a3f5f;
            text-align: center;
            transition: 0.3s;
        }
        .card:hover { border-color: #ffd700; transform: translateY(-5px); }
        .card .live-badge {
            background: #e74c3c;
            color: #fff;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            display: inline-block;
            animation: blink 1s infinite;
        }
        @keyframes blink { 50% { opacity: 0.3; } }
        .card .teams { font-size: 1.5em; font-weight: bold; margin: 15px 0; }
        .card .teams .home { color: #2ecc71; }
        .card .teams .away { color: #e74c3c; }
        .card .teams .vs { color: #ffd700; margin: 0 10px; }
        .card .score { font-size: 2em; color: #ffd700; margin: 10px 0; }
        .card .info { color: #aaa; line-height: 1.8; }
        .card .info span { color: #fff; }
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #ffd700, #f5a623);
            color: #1a1f35;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            margin: 5px;
        }
        .footer {
            text-align: center;
            padding: 30px;
            color: #555;
            border-top: 1px solid #2a3f5f;
            margin-top: 40px;
        }
        .footer a { color: #ffd700; text-decoration: none; }
        @media (max-width: 600px) { .header h1 { font-size: 2em; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 كأس العالم 2026</h1>
            <p>تابع المباريات المباشرة والقادمة</p>
            <div style="margin-top: 15px;">
                <a href="https://t.me/Ali_worldcup_bot" class="btn">🤖 البوت على تليجرام</a>
            </div>
        </div>

        <h2 class="section-title">🔴 مباريات مباشرة</h2>
        <div class="cards">
            {% for match in live_matches %}
            <div class="card">
                <span class="live-badge">🔴 مباشر</span>
                <div class="teams">
                    <span class="home">{{ match.home_flag }} {{ match.home }}</span>
                    <span class="vs">⚔️</span>
                    <span class="away">{{ match.away_flag }} {{ match.away }}</span>
                </div>
                <div class="score">{{ match.home_score }} - {{ match.away_score }}</div>
                <div class="info">
                    📍 <span>{{ match.stadium }}</span><br>
                    📅 <span>{{ match.date }}</span> | 🕒 <span>{{ match.time }}</span>
                </div>
            </div>
            {% else %}
            <div class="card" style="grid-column:1/-1;padding:40px;">
                <p>🔴 لا توجد مباريات مباشرة حالياً</p>
            </div>
            {% endfor %}
        </div>

        <h2 class="section-title">📅 مباريات اليوم</h2>
        <div class="cards">
            {% for match in today_matches %}
            <div class="card">
                <div class="teams">
                    <span class="home">{{ match.home_flag }} {{ match.home }}</span>
                    <span class="vs">⚔️</span>
                    <span class="away">{{ match.away_flag }} {{ match.away }}</span>
                </div>
                <div class="info">
                    📍 <span>{{ match.stadium }}</span><br>
                    📅 <span>{{ match.date }}</span> | 🕒 <span>{{ match.time }}</span>
                </div>
            </div>
            {% else %}
            <div class="card" style="grid-column:1/-1;padding:40px;">
                <p>📭 لا توجد مباريات اليوم</p>
            </div>
            {% endfor %}
        </div>

        <div class="footer">
            <p>🏆 كأس العالم 2026 - جميع الحقوق محفوظة</p>
            <p style="font-size:0.85em;color:#444;">🤖 <a href="https://t.me/Ali_worldcup_bot">@Ali_worldcup_bot</a></p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    today_matches = get_today_matches(matches_db)
    live_matches = get_live_matches(matches_db)
    return render_template_string(HTML_TEMPLATE, today_matches=today_matches, live_matches=live_matches)
