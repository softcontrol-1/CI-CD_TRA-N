"""
Flask Web Uygulaması - CI/CD Demo
Duck Hunt tarzı mini oyun + CI/CD pipeline gösterimi.
Render (PaaS) üzerinde Docker ile deploy edilecek.
"""

from flask import Flask, render_template_string
import datetime
import os

app = Flask(__name__)

# ─── Duck Hunt Oyunu HTML Şablonu ────────────────────────────────
GAME_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Duck Hunt - CI/CD Demo</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            height: 100vh;
            cursor: crosshair;
            user-select: none;
        }

        /* ─── Oyun Sahası ─── */
        #game-scene {
            position: relative;
            width: 100%;
            height: 100vh;
            background: linear-gradient(180deg, #87CEEB 0%, #b6e3f4 40%, #4a8f3f 40%, #3d7a34 42%, #2d5a1e 100%);
            overflow: hidden;
        }

        /* Güneş */
        .sun {
            position: absolute;
            top: 40px;
            right: 80px;
            width: 70px;
            height: 70px;
            background: radial-gradient(circle, #ffe066, #ffb300);
            border-radius: 50%;
            box-shadow: 0 0 40px #ffe06688, 0 0 80px #ffb30044;
        }

        /* Bulutlar */
        .cloud {
            position: absolute;
            font-size: 48px;
            opacity: 0.7;
            animation: drift 30s linear infinite;
        }
        .cloud:nth-child(2) { top: 30px; left: -100px; animation-duration: 35s; font-size: 36px; }
        .cloud:nth-child(3) { top: 80px; left: -200px; animation-duration: 45s; font-size: 54px; opacity: 0.5; }
        .cloud:nth-child(4) { top: 140px; left: -300px; animation-duration: 50s; font-size: 30px; }

        @keyframes drift {
            from { transform: translateX(-150px); }
            to   { transform: translateX(110vw); }
        }

        /* Ağaçlar */
        .trees {
            position: absolute;
            bottom: 56%;
            left: 0;
            width: 100%;
            font-size: 52px;
            letter-spacing: 20px;
            text-align: center;
            opacity: 0.6;
            pointer-events: none;
        }

        /* ─── Üst Bilgi Çubuğu ─── */
        #hud {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 24px;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(8px);
            z-index: 100;
        }

        .hud-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #fff;
            font-family: 'Press Start 2P', monospace;
            font-size: 13px;
        }

        .hud-label {
            color: #aaa;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .hud-value {
            color: #00ff88;
            font-size: 18px;
        }

        .hud-value.time { color: #ff6b6b; }
        .hud-value.ammo { color: #ffd93d; }

        /* ─── Ördek ─── */
        .duck {
            position: absolute;
            font-size: 48px;
            cursor: crosshair;
            z-index: 50;
            transition: transform 0.1s;
            filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.3));
            animation: flap 0.3s ease-in-out infinite alternate;
        }

        .duck:hover {
            transform: scale(1.1);
        }

        @keyframes flap {
            from { transform: translateY(0px) rotate(-3deg); }
            to   { transform: translateY(-6px) rotate(3deg); }
        }

        .duck.hit {
            animation: fall 0.6s ease-in forwards;
            pointer-events: none;
        }

        @keyframes fall {
            0%   { opacity: 1; transform: rotate(0deg); }
            100% { opacity: 0; transform: translateY(400px) rotate(720deg); }
        }

        /* ─── Patlama Efekti ─── */
        .bang {
            position: absolute;
            font-family: 'Press Start 2P', monospace;
            font-size: 20px;
            color: #ff0;
            pointer-events: none;
            z-index: 200;
            animation: bangPop 0.5s ease-out forwards;
            text-shadow: 2px 2px 0 #f00, -1px -1px 0 #f80;
        }

        @keyframes bangPop {
            0%   { opacity: 1; transform: scale(0.5) translateY(0); }
            50%  { opacity: 1; transform: scale(1.3) translateY(-10px); }
            100% { opacity: 0; transform: scale(0.8) translateY(-40px); }
        }

        /* Skor popup */
        .score-pop {
            position: absolute;
            font-family: 'Press Start 2P', monospace;
            font-size: 16px;
            color: #00ff88;
            pointer-events: none;
            z-index: 200;
            animation: scoreFly 0.8s ease-out forwards;
        }

        @keyframes scoreFly {
            0%   { opacity: 1; transform: translateY(0); }
            100% { opacity: 0; transform: translateY(-60px); }
        }

        /* ─── Mermi İzi ─── */
        .muzzle-flash {
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: radial-gradient(circle, #fff, #ff0, transparent);
            pointer-events: none;
            z-index: 150;
            animation: flash 0.2s ease-out forwards;
        }

        @keyframes flash {
            0%   { opacity: 1; transform: scale(1); }
            100% { opacity: 0; transform: scale(3); }
        }

        /* ─── Başlangıç / Bitiş Ekranı ─── */
        #overlay {
            position: absolute;
            inset: 0;
            background: rgba(0,0,0,0.85);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 500;
            backdrop-filter: blur(4px);
        }

        #overlay.hidden { display: none; }

        #overlay h1 {
            font-family: 'Press Start 2P', monospace;
            font-size: 36px;
            color: #00ff88;
            margin-bottom: 8px;
            text-shadow: 3px 3px 0 #006633;
        }

        #overlay .duck-title {
            font-size: 72px;
            margin-bottom: 16px;
        }

        #overlay p {
            color: #ccc;
            font-size: 14px;
            margin-bottom: 24px;
            text-align: center;
            line-height: 1.8;
        }

        #overlay .final-score {
            font-family: 'Press Start 2P', monospace;
            font-size: 24px;
            color: #ffd93d;
            margin-bottom: 16px;
        }

        #overlay .stats {
            color: #aaa;
            font-size: 13px;
            margin-bottom: 24px;
            text-align: center;
            line-height: 2;
        }

        .btn-start {
            font-family: 'Press Start 2P', monospace;
            font-size: 14px;
            padding: 16px 32px;
            border: none;
            border-radius: 8px;
            background: linear-gradient(135deg, #00ff88, #00cc66);
            color: #003311;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 15px rgba(0,255,136,0.3);
        }

        .btn-start:hover {
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 6px 25px rgba(0,255,136,0.5);
        }

        /* CI/CD Rozeti */
        .cicd-badge {
            position: absolute;
            bottom: 16px;
            right: 16px;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(8px);
            padding: 8px 14px;
            border-radius: 20px;
            font-size: 11px;
            color: rgba(255,255,255,0.5);
            z-index: 90;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .cicd-badge span { color: #00d2ff; }

        /* Çimen çizgisi */
        .grass-line {
            position: absolute;
            bottom: 58%;
            left: 0;
            width: 100%;
            height: 4px;
            background: #2d5a1e;
            z-index: 40;
            box-shadow: 0 -2px 8px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div id="game-scene">
        <!-- Gökyüzü Elemanları -->
        <div class="sun"></div>
        <div class="cloud" style="top:20px;">☁️</div>
        <div class="cloud">☁️</div>
        <div class="cloud">☁️</div>
        <div class="cloud">☁️</div>

        <!-- Ağaçlar -->
        <div class="trees">🌲🌳🌲🌳🌲🌲🌳🌲🌳🌲🌲🌳</div>
        <div class="grass-line"></div>

        <!-- HUD -->
        <div id="hud">
            <div class="hud-item">
                <div>
                    <div class="hud-label">Skor</div>
                    <div class="hud-value" id="score">0</div>
                </div>
            </div>
            <div class="hud-item">
                <div>
                    <div class="hud-label">Süre</div>
                    <div class="hud-value time" id="timer">30</div>
                </div>
            </div>
            <div class="hud-item">
                <div>
                    <div class="hud-label">Vuruş</div>
                    <div class="hud-value ammo" id="hits">0 / 0</div>
                </div>
            </div>
        </div>

        <!-- Başlangıç Ekranı -->
        <div id="overlay">
            <div class="duck-title">🦆</div>
            <h1>DUCK HUNT</h1>
            <p>Ördekleri tıklayarak vur!<br>30 saniyede en yüksek skoru yap.</p>
            <button class="btn-start" id="btn-start" onclick="startGame()">BAŞLA</button>
        </div>

        <!-- CI/CD Rozeti -->
        <div class="cicd-badge">
            🚀 <span>CI/CD</span> ile deploy edildi • Flask + Docker + Render
        </div>
    </div>

    <script>
        // ─── Oyun Değişkenleri ──────────────────────────
        let score = 0;
        let timeLeft = 30;
        let totalShots = 0;
        let totalHits = 0;
        let gameRunning = false;
        let gameTimer = null;
        let duckTimer = null;

        const scene = document.getElementById('game-scene');
        const scoreEl = document.getElementById('score');
        const timerEl = document.getElementById('timer');
        const hitsEl = document.getElementById('hits');
        const overlay = document.getElementById('overlay');

        const duckEmojis = ['🦆', '🐥', '🐤'];
        const shootSounds = [];

        // ─── Ateş Efekti ────────────────────────────────
        scene.addEventListener('click', function(e) {
            if (!gameRunning) return;
            totalShots++;
            updateHits();

            // Muzzle flash
            const flash = document.createElement('div');
            flash.className = 'muzzle-flash';
            flash.style.left = (e.clientX - 10) + 'px';
            flash.style.top = (e.clientY - 10) + 'px';
            scene.appendChild(flash);
            setTimeout(() => flash.remove(), 200);
        });

        // ─── Ördek Oluşturma ────────────────────────────
        function spawnDuck() {
            if (!gameRunning) return;

            const duck = document.createElement('div');
            duck.className = 'duck';
            duck.textContent = duckEmojis[Math.floor(Math.random() * duckEmojis.length)];

            // Rastgele konum (gökyüzü bölgesi — üst %55)
            const maxX = window.innerWidth - 60;
            const maxY = window.innerHeight * 0.45;
            const x = 60 + Math.random() * (maxX - 120);
            const y = 60 + Math.random() * (maxY - 60);

            duck.style.left = x + 'px';
            duck.style.top = y + 'px';

            // Rastgele boyut (küçük = daha zor, daha çok puan)
            const sizes = [
                { size: 48, points: 10, label: '+10' },
                { size: 36, points: 25, label: '+25' },
                { size: 26, points: 50, label: '+50' }
            ];
            const chosen = sizes[Math.floor(Math.random() * sizes.length)];
            duck.style.fontSize = chosen.size + 'px';
            duck.dataset.points = chosen.points;
            duck.dataset.label = chosen.label;

            // Hareket yönü
            const speedX = (Math.random() - 0.5) * 4;
            const speedY = (Math.random() - 0.5) * 2;
            let posX = x, posY = y;

            // Tıklama → vurma
            duck.addEventListener('click', function(e) {
                e.stopPropagation();
                if (duck.classList.contains('hit')) return;

                totalShots++;
                totalHits++;
                score += chosen.points;
                scoreEl.textContent = score;
                updateHits();

                // BANG efekti
                const bang = document.createElement('div');
                bang.className = 'bang';
                bang.textContent = 'BANG!';
                bang.style.left = (e.clientX - 30) + 'px';
                bang.style.top = (e.clientY - 30) + 'px';
                scene.appendChild(bang);
                setTimeout(() => bang.remove(), 500);

                // Skor popup
                const pop = document.createElement('div');
                pop.className = 'score-pop';
                pop.textContent = chosen.label;
                pop.style.left = (e.clientX - 15) + 'px';
                pop.style.top = (e.clientY - 20) + 'px';
                scene.appendChild(pop);
                setTimeout(() => pop.remove(), 800);

                // Flash
                const flash = document.createElement('div');
                flash.className = 'muzzle-flash';
                flash.style.left = (e.clientX - 10) + 'px';
                flash.style.top = (e.clientY - 10) + 'px';
                scene.appendChild(flash);
                setTimeout(() => flash.remove(), 200);

                duck.classList.add('hit');
                setTimeout(() => duck.remove(), 600);
            });

            scene.appendChild(duck);

            // Hareket animasyonu
            const moveInterval = setInterval(() => {
                if (!gameRunning || duck.classList.contains('hit')) {
                    clearInterval(moveInterval);
                    return;
                }
                posX += speedX;
                posY += speedY;

                // Sınırlardan sekme
                if (posX < 0 || posX > maxX) posX = Math.max(0, Math.min(posX, maxX));
                if (posY < 50 || posY > maxY) posY = Math.max(50, Math.min(posY, maxY));

                duck.style.left = posX + 'px';
                duck.style.top = posY + 'px';
            }, 30);

            // Kaçış süresi (2-4 saniye sonra uçup gider)
            const escapeTime = 2000 + Math.random() * 2000;
            setTimeout(() => {
                if (!duck.classList.contains('hit') && duck.parentNode) {
                    duck.style.transition = 'all 0.5s ease-in';
                    duck.style.top = '-60px';
                    duck.style.opacity = '0';
                    setTimeout(() => duck.remove(), 500);
                    clearInterval(moveInterval);
                }
            }, escapeTime);
        }

        // ─── HUD Güncelle ───────────────────────────────
        function updateHits() {
            hitsEl.textContent = totalHits + ' / ' + totalShots;
        }

        // ─── Oyunu Başlat ───────────────────────────────
        function startGame() {
            score = 0;
            timeLeft = 30;
            totalShots = 0;
            totalHits = 0;
            gameRunning = true;

            scoreEl.textContent = '0';
            timerEl.textContent = '30';
            hitsEl.textContent = '0 / 0';
            overlay.classList.add('hidden');

            // Zamanlayıcı
            gameTimer = setInterval(() => {
                timeLeft--;
                timerEl.textContent = timeLeft;
                if (timeLeft <= 10) timerEl.style.color = '#ff4444';
                if (timeLeft <= 0) endGame();
            }, 1000);

            // Ördek spawn (her 800-1500ms)
            function scheduleNextDuck() {
                if (!gameRunning) return;
                const delay = 600 + Math.random() * 900;
                duckTimer = setTimeout(() => {
                    spawnDuck();
                    scheduleNextDuck();
                }, delay);
            }
            scheduleNextDuck();
            spawnDuck();
        }

        // ─── Oyunu Bitir ────────────────────────────────
        function endGame() {
            gameRunning = false;
            clearInterval(gameTimer);
            clearTimeout(duckTimer);

            // Kalan ördekleri temizle
            document.querySelectorAll('.duck').forEach(d => d.remove());

            const accuracy = totalShots > 0 ? Math.round((totalHits / totalShots) * 100) : 0;

            let rank = '🥉 Çaylak Avcı';
            if (score >= 500) rank = '🥇 Efsane Nişancı';
            else if (score >= 300) rank = '🥈 Usta Avcı';
            else if (score >= 150) rank = '🏅 İyi Avcı';

            overlay.classList.remove('hidden');
            overlay.innerHTML = `
                <div class="duck-title">🎯</div>
                <h1>SÜRE DOLDU!</h1>
                <div class="final-score">${score} PUAN</div>
                <div class="stats">
                    ${rank}<br>
                    İsabet: ${totalHits} / ${totalShots} (%${accuracy})<br>
                </div>
                <button class="btn-start" onclick="resetAndStart()">TEKRAR OYNA</button>
            `;
            timerEl.style.color = '#ff6b6b';
        }

        function resetAndStart() {
            timerEl.style.color = '#ff6b6b';
            startGame();
        }
    </script>
</body>
</html>
"""


@app.route("/")
def home():
    """Ana sayfa - Duck Hunt oyunu."""
    return render_template_string(GAME_TEMPLATE)


@app.route("/health")
def health():
    """Sağlık kontrolü endpoint'i."""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
