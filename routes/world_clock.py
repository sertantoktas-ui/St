"""World Clock routes for multi-timezone time display"""

from flask import Blueprint, render_template_string, jsonify, request
from datetime import datetime
import pytz

world_clock_bp = Blueprint('world_clock', __name__)

# Default timezones
DEFAULT_TIMEZONES = [
    {'country': 'Türkiye', 'city': 'Istanbul', 'timezone': 'Europe/Istanbul', 'highlight': True},
    {'country': 'Çin', 'city': 'Pekin', 'timezone': 'Asia/Shanghai', 'highlight': False},
    {'country': 'Çin', 'city': 'Hong Kong', 'timezone': 'Asia/Hong_Kong', 'highlight': False},
    {'country': 'ABD', 'city': 'New York', 'timezone': 'America/New_York', 'highlight': False},
    {'country': 'ABD', 'city': 'Los Angeles', 'timezone': 'America/Los_Angeles', 'highlight': False},
    {'country': 'Japonya', 'city': 'Tokyo', 'timezone': 'Asia/Tokyo', 'highlight': False},
    {'country': 'Singapur', 'city': 'Singapur', 'timezone': 'Asia/Singapore', 'highlight': False},
    {'country': 'İngiltere', 'city': 'Londra', 'timezone': 'Europe/London', 'highlight': False},
]

@world_clock_bp.route('/clock', methods=['GET'])
def world_clock_page():
    """Render world clock page"""
    html = render_template_string(WORLD_CLOCK_HTML)
    return html

@world_clock_bp.route('/api/times', methods=['GET'])
def get_times():
    """Get current times for all configured timezones"""
    timezones = request.args.getlist('tz')

    if not timezones:
        timezones = [tz['timezone'] for tz in DEFAULT_TIMEZONES]

    times = {}
    for tz_name in timezones:
        try:
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            times[tz_name] = {
                'time': now.strftime('%H:%M:%S'),
                'date': now.strftime('%d.%m.%Y'),
                'hour': now.hour,
                'minute': now.minute,
                'second': now.second
            }
        except Exception as e:
            times[tz_name] = {'error': str(e)}

    return jsonify(times)

@world_clock_bp.route('/api/timezones', methods=['GET'])
def get_available_timezones():
    """Get all available timezones"""
    all_timezones = pytz.all_timezones
    return jsonify({'timezones': all_timezones})

@world_clock_bp.route('/api/timezone-info/<timezone>', methods=['GET'])
def get_timezone_info(timezone):
    """Get information about a specific timezone"""
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        utc_offset = now.strftime('%z')

        return jsonify({
            'timezone': timezone,
            'time': now.strftime('%H:%M:%S'),
            'date': now.strftime('%d.%m.%Y'),
            'utc_offset': utc_offset,
            'dst': bool(now.dst())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@world_clock_bp.route('/api/convert-time', methods=['POST'])
def convert_time():
    """Convert time from one timezone to another"""
    data = request.json
    from_tz = data.get('from_timezone')
    to_tz = data.get('to_timezone')
    time_str = data.get('time', None)  # Format: HH:MM:SS

    try:
        if time_str:
            parts = time_str.split(':')
            hour, minute, second = int(parts[0]), int(parts[1]), int(parts[2])

            from_timezone = pytz.timezone(from_tz)
            to_timezone = pytz.timezone(to_tz)

            now = datetime.now()
            dt = from_timezone.localize(now.replace(hour=hour, minute=minute, second=second))
            converted = dt.astimezone(to_timezone)
        else:
            from_timezone = pytz.timezone(from_tz)
            to_timezone = pytz.timezone(to_tz)

            dt = datetime.now(from_timezone)
            converted = dt.astimezone(to_timezone)

        return jsonify({
            'from_timezone': from_tz,
            'to_timezone': to_tz,
            'from_time': dt.strftime('%H:%M:%S'),
            'to_time': converted.strftime('%H:%M:%S'),
            'difference_hours': (converted.hour - dt.hour) % 24
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# HTML Template
WORLD_CLOCK_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dünya Saatleri - World Clock</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            width: 100%;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .clocks-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .clock-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .clock-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
        }

        .clock-card.highlight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .country-name {
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }

        .clock-card.highlight .country-name {
            color: white;
        }

        .city-name {
            font-size: 0.95em;
            opacity: 0.7;
            margin-bottom: 15px;
            color: #666;
        }

        .clock-card.highlight .city-name {
            opacity: 0.9;
        }

        .digital-time {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 10px;
            font-family: 'Courier New', monospace;
            color: #667eea;
            letter-spacing: 2px;
        }

        .clock-card.highlight .digital-time {
            color: #fff;
        }

        .timezone-info {
            font-size: 0.85em;
            opacity: 0.6;
            color: #999;
        }

        .clock-card.highlight .timezone-info {
            opacity: 0.8;
            color: rgba(255, 255, 255, 0.8);
        }

        .clock-date {
            font-size: 0.9em;
            opacity: 0.7;
            color: #666;
            margin-top: 8px;
        }

        .clock-card.highlight .clock-date {
            opacity: 0.9;
            color: rgba(255, 255, 255, 0.9);
        }

        .add-timezone {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            margin-bottom: 30px;
        }

        .add-timezone h3 {
            color: #333;
            margin-bottom: 15px;
        }

        .timezone-input {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .timezone-input input,
        .timezone-input select {
            padding: 10px 15px;
            border: 2px solid #667eea;
            border-radius: 10px;
            font-size: 1em;
        }

        .timezone-input input {
            flex: 1;
            min-width: 150px;
        }

        .timezone-input button {
            padding: 10px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s ease;
        }

        .timezone-input button:hover {
            transform: scale(1.05);
        }

        .quick-zones {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
        }

        .quick-zone-btn {
            padding: 10px 15px;
            background: #f0f0f0;
            border: 2px solid #ddd;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            color: #333;
            transition: all 0.2s ease;
        }

        .quick-zone-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .quick-zone-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }

            .clocks-grid {
                grid-template-columns: 1fr;
            }

            .digital-time {
                font-size: 1.8em;
            }
        }

        .remove-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 0, 0, 0.7);
            color: white;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            font-size: 1.2em;
            transition: all 0.2s ease;
            opacity: 0;
        }

        .clock-card {
            position: relative;
        }

        .clock-card:hover .remove-btn {
            opacity: 1;
        }

        .remove-btn:hover {
            background: rgba(255, 0, 0, 1);
            transform: scale(1.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 Dünya Saatleri</h1>
            <p>World Clock - Saatları İzle / Watch the Times</p>
        </div>

        <div class="add-timezone">
            <h3>⏰ Saat Dilimi Ekle / Add Timezone</h3>
            <div class="timezone-input">
                <input type="text" id="countryInput" placeholder="Ülke/Country adı">
                <input type="text" id="cityInput" placeholder="Şehir/City adı (isteğe bağlı)">
                <select id="timezoneSelect">
                    <option value="">Saat Dilimi Seç / Select Timezone</option>
                </select>
                <button onclick="addTimezone()">Ekle / Add</button>
            </div>
            <p style="font-size: 0.9em; color: #666; margin-bottom: 15px;">Hızlı Seçimler / Quick Options:</p>
            <div class="quick-zones" id="quickZones"></div>
        </div>

        <div class="clocks-grid" id="clocksContainer"></div>
    </div>

    <script>
        let timezones = [
            { country: 'Türkiye', city: 'Istanbul', timezone: 'Europe/Istanbul', highlight: true },
            { country: 'Çin', city: 'Pekin', timezone: 'Asia/Shanghai', highlight: false },
            { country: 'Çin', city: 'Hong Kong', timezone: 'Asia/Hong_Kong', highlight: false },
            { country: 'ABD', city: 'New York', timezone: 'America/New_York', highlight: false },
            { country: 'Japonya', city: 'Tokyo', timezone: 'Asia/Tokyo', highlight: false },
        ];

        const commonZones = [
            { name: '🇹🇷 Türkiye', tz: 'Europe/Istanbul' },
            { name: '🇨🇳 Çin (Beijing)', tz: 'Asia/Shanghai' },
            { name: '🇨🇳 Hong Kong', tz: 'Asia/Hong_Kong' },
            { name: '🇯🇵 Japonya', tz: 'Asia/Tokyo' },
            { name: '🇬🇧 İngiltere', tz: 'Europe/London' },
            { name: '🇺🇸 New York', tz: 'America/New_York' },
            { name: '🇺🇸 Los Angeles', tz: 'America/Los_Angeles' },
            { name: '🇦🇺 Sydney', tz: 'Australia/Sydney' },
        ];

        function initializeTimezoneSelect() {
            const select = document.getElementById('timezoneSelect');
            fetch('/api/timezones')
                .then(r => r.json())
                .then(data => {
                    data.timezones.forEach(tz => {
                        const option = document.createElement('option');
                        option.value = tz;
                        option.textContent = tz.replace(/_/g, ' ');
                        select.appendChild(option);
                    });
                })
                .catch(() => {
                    console.log('Using fallback timezones');
                });
        }

        function createClockCard(tzData, index) {
            const card = document.createElement('div');
            card.className = 'clock-card' + (tzData.highlight ? ' highlight' : '');
            card.innerHTML = `
                <button class="remove-btn" onclick="removeTimezone(${index})">×</button>
                <div class="country-name">${tzData.country}</div>
                <div class="city-name">${tzData.city}</div>
                <div class="digital-time" id="time-${index}">--:--:--</div>
                <div class="clock-date" id="date-${index}">--.--.----</div>
                <div class="timezone-info">${tzData.timezone}</div>
            `;
            return card;
        }

        function updateClocks() {
            const tzList = timezones.map(t => t.timezone).join('&tz=');
            fetch(`/api/times?tz=${tzList}`)
                .then(r => r.json())
                .then(data => {
                    timezones.forEach((tz, index) => {
                        const timeData = data[tz.timezone];
                        if (timeData && !timeData.error) {
                            const timeEl = document.getElementById(`time-${index}`);
                            const dateEl = document.getElementById(`date-${index}`);
                            if (timeEl) timeEl.textContent = timeData.time;
                            if (dateEl) dateEl.textContent = timeData.date;
                        }
                    });
                });
        }

        function renderClocks() {
            const container = document.getElementById('clocksContainer');
            container.innerHTML = '';
            timezones.forEach((tzData, index) => {
                container.appendChild(createClockCard(tzData, index));
            });
            updateClocks();
        }

        function addTimezone() {
            const countryInput = document.getElementById('countryInput').value.trim();
            const cityInput = document.getElementById('cityInput').value.trim();
            const timezoneSelect = document.getElementById('timezoneSelect').value;

            if (!countryInput || !timezoneSelect) {
                alert('Lütfen ülke ve saat dilimi seçiniz');
                return;
            }

            if (!timezones.find(t => t.timezone === timezoneSelect)) {
                const newTz = {
                    country: countryInput,
                    city: cityInput || timezoneSelect.split('/')[1].replace(/_/g, ' '),
                    timezone: timezoneSelect,
                    highlight: false
                };

                timezones.push(newTz);
                document.getElementById('countryInput').value = '';
                document.getElementById('cityInput').value = '';
                document.getElementById('timezoneSelect').value = '';
                renderClocks();
            }
        }

        function removeTimezone(index) {
            timezones.splice(index, 1);
            renderClocks();
        }

        function populateQuickZones() {
            const quickZones = document.getElementById('quickZones');
            commonZones.forEach(zone => {
                const btn = document.createElement('button');
                btn.className = 'quick-zone-btn';
                btn.textContent = zone.name;

                if (timezones.find(t => t.timezone === zone.tz)) {
                    btn.classList.add('active');
                }

                btn.onclick = () => {
                    const exists = timezones.find(t => t.timezone === zone.tz);
                    if (exists) {
                        timezones = timezones.filter(t => t.timezone !== zone.tz);
                    } else {
                        const parts = zone.tz.split('/');
                        timezones.push({
                            country: zone.name.split(' ').slice(1).join(' '),
                            city: parts[1].replace(/_/g, ' '),
                            timezone: zone.tz,
                            highlight: false
                        });
                    }
                    renderClocks();
                    populateQuickZones();
                };
                quickZones.appendChild(btn);
            });
        }

        // Initialize
        initializeTimezoneSelect();
        renderClocks();
        populateQuickZones();

        // Update every second
        setInterval(updateClocks, 1000);
    </script>
</body>
</html>
"""
