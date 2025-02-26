# -*- coding: utf-8 -*-

from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify
import google.generativeai as genai
import os
from firebase_config import db
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'suggestify-secret-key'  # Session için gerekli

# API anahtarını environment variable'dan al veya varsayılan değeri kullan
api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyBMeBWG1Jg6bKzp2wvK8Bersfm02DJay8w')

# Gemini API yapılandırması
genai.configure(api_key=api_key)

# Örnek generation_config ayarları
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# Model nesnesini tanımlıyoruz
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=generation_config,
)

@app.route('/add_to_list', methods=['POST'])
def add_to_list():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Oturum açmanız gerekiyor!'})
    
    try:
        data = request.json
        item_type = data.get('type')  # 'movie' veya 'series'
        item_name = data.get('name')
        username = session['username']
        
        # Kullanıcı dokümanını al
        user_ref = db.collection('users').document(username)
        user = user_ref.get()
        
        if user.exists:
            # Mevcut listeleri al veya boş liste oluştur
            user_data = user.to_dict()
            movies_list = user_data.get('movies', [])
            series_list = user_data.get('series', [])
            
            # Yeni öğeyi uygun listeye ekle
            if item_type == 'movie' and item_name not in movies_list:
                movies_list.append(item_name)
                user_ref.update({'movies': movies_list})
            elif item_type == 'series' and item_name not in series_list:
                series_list.append(item_name)
                user_ref.update({'series': series_list})
            
            return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Liste güncelleme hatası: {str(e)}")
        return jsonify({'success': False, 'error': 'Bir hata oluştu!'})

@app.route('/remove_from_list', methods=['POST'])
def remove_from_list():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Oturum açmanız gerekiyor!'})
    
    try:
        data = request.json
        item_type = data.get('type')  # 'movie' veya 'series'
        item_name = data.get('name')
        username = session['username']
        
        # Kullanıcı dokümanını al
        user_ref = db.collection('users').document(username)
        user = user_ref.get()
        
        if user.exists:
            # Mevcut listeleri al
            user_data = user.to_dict()
            if item_type == 'movie':
                movies_list = user_data.get('movies', [])
                if item_name in movies_list:
                    movies_list.remove(item_name)
                    user_ref.update({'movies': movies_list})
            elif item_type == 'series':
                series_list = user_data.get('series', [])
                if item_name in series_list:
                    series_list.remove(item_name)
                    user_ref.update({'series': series_list})
            
            return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Liste güncelleme hatası: {str(e)}")
        return jsonify({'success': False, 'error': 'Bir hata oluştu!'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = ""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            # Kullanıcıyı Firestore'da ara veya oluştur
            user_ref = db.collection('users').document(username)
            user = user_ref.get()
            
            if not user.exists:
                # Yeni kullanıcı oluştur
                user_ref.set({
                    'username': username,
                    'created_at': datetime.now(),
                    'movies': [],  # Film listesi
                    'series': []   # Dizi listesi
                })
            
            # Session'a kullanıcı bilgisini kaydet
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error_message = "Kullanıcı adı boş olamaz!"

    return f'''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Suggestify - Giriş</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    }}
                    
                    body {{
                        background: linear-gradient(135deg, #6C63FF, #FF6B6B);
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 20px;
                    }}
                    
                    .login-container {{
                        background: rgba(255, 255, 255, 0.15);
                        backdrop-filter: blur(10px);
                        padding: 2rem;
                        border-radius: 20px;
                        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                        width: 100%;
                        max-width: 400px;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }}
                    
                    h1 {{
                        color: #fff;
                        text-align: center;
                        margin-bottom: 2rem;
                        font-size: 2rem;
                    }}
                    
                    .form-group {{
                        margin-bottom: 1.5rem;
                    }}
                    
                    input[type="text"] {{
                        width: 100%;
                        padding: 12px;
                        border: 2px solid rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        background: rgba(255, 255, 255, 0.1);
                        color: #fff;
                        font-size: 1rem;
                    }}
                    
                    input[type="text"]:focus {{
                        outline: none;
                        border-color: #fff;
                    }}
                    
                    button {{
                        width: 100%;
                        padding: 12px;
                        background: linear-gradient(45deg, #FF6B6B, #FFB88C);
                        border: none;
                        border-radius: 10px;
                        color: white;
                        font-size: 1.1rem;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }}
                    
                    button:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
                    }}
                    
                    .error-message {{
                        background: rgba(255, 99, 71, 0.2);
                        color: #fff;
                        padding: 1rem;
                        border-radius: 10px;
                        margin-bottom: 1rem;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="login-container">
                    <h1>🎬 Suggestify Giriş</h1>
                    {f'<div class="error-message">{error_message}</div>' if error_message else ''}
                    <form method="post">
                        <div class="form-group">
                            <input type="text" name="username" placeholder="Kullanıcı Adı" required>
                        </div>
                        <button type="submit">Giriş Yap</button>
                    </form>
                </div>
            </body>
        </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET','POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    error_message = ""
    response_html = ""
    
    # Kullanıcının mevcut listelerini al
    user_ref = db.collection('users').document(session['username'])
    user = user_ref.get()
    user_data = user.to_dict()
    series_list = user_data.get('series', [])
    movies_list = user_data.get('movies', [])
    
    # JavaScript kodunu ayrı bir değişkende tanımla
    RESPONSE_SCRIPT = '''
        const responseText = `%s`;
        const suggestionsDiv = document.getElementById('suggestions');
        const lines = responseText.split('\\n').filter(line => line.trim());
        
        let currentCategory = '';
        let html = '';
        
        lines.forEach(line => {
            if (line.includes('DİZİLER:') || line.includes('FİLMLER:')) {
                if (html) html += '</ul>';
                currentCategory = line.includes('DİZİLER:') ? 'series' : 'movie';
                html += `<h3>${line}</h3><ul class="suggestions-list">`;
            } else if (line.trim()) {
                const itemName = line.replace(/^[-•*]\\s*/, '').trim();
                html += `
                    <li>
                        <span>${itemName}</span>
                        <button class="action-button add-button" 
                                onclick="addToList('${currentCategory}', '${itemName}')">
                            Ekle
                        </button>
                    </li>`;
            }
        });
        
        if (html) html += '</ul>';
        suggestionsDiv.innerHTML = html;
    '''
    
    # HTML Template tanımı
    HTML_TEMPLATE = '''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Suggestify - Akıllı Dizi Önerici</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    }
                    
                    body {
                        background: linear-gradient(135deg, #6C63FF, #FF6B6B);
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 20px;
                    }
                    
                    .container {
                        background: rgba(255, 255, 255, 0.15);
                        backdrop-filter: blur(10px);
                        padding: 2rem;
                        border-radius: 20px;
                        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                        width: 100%;
                        max-width: 600px;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        position: relative;
                    }
                    
                    .profile-section {
                        position: absolute;
                        top: 20px;
                        right: 20px;
                        z-index: 1000;
                    }
                    
                    .profile-button {
                        padding: 8px 16px;
                        background: rgba(255, 255, 255, 0.1);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        border-radius: 20px;
                        color: #fff;
                        text-decoration: none;
                        font-size: 0.9rem;
                        transition: all 0.3s ease;
                    }
                    
                    .profile-button:hover {
                        background: rgba(255, 255, 255, 0.2);
                        transform: translateY(-2px);
                    }
                    
                    h1 {
                        color: #fff;
                        text-align: center;
                        margin-bottom: 2rem;
                        font-size: 2.5rem;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                        background: linear-gradient(to right, #fff, #FFD700);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    }
                    
                    .form-group {
                        margin-bottom: 1.5rem;
                    }
                    
                    label {
                        color: #fff;
                        display: block;
                        margin-bottom: 0.5rem;
                        font-size: 1.1rem;
                    }
                    
                    input[type="text"] {
                        width: 100%;
                        padding: 12px;
                        border: 2px solid rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        background: rgba(255, 255, 255, 0.1);
                        color: #fff;
                        font-size: 1rem;
                        transition: all 0.3s ease;
                    }
                    
                    input[type="text"]:focus {
                        outline: none;
                        background: rgba(255, 255, 255, 0.2);
                        box-shadow: 0 0 15px rgba(255,255,255,0.2);
                        border-color: rgba(255, 255, 255, 0.4);
                    }
                    
                    button {
                        width: 100%;
                        padding: 12px;
                        background: linear-gradient(45deg, #FF6B6B, #FFB88C);
                        border: none;
                        border-radius: 10px;
                        color: white;
                        font-size: 1.1rem;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        font-weight: bold;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }
                    
                    button:hover {
                        background: linear-gradient(45deg, #FFB88C, #FF6B6B);
                        transform: translateY(-2px);
                        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
                    }
                    
                    .response-section {
                        margin-top: 2rem;
                        padding: 1.5rem;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 10px;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }
                    
                    .response-content {
                        background: rgba(255, 255, 255, 0.1);
                        padding: 1.5rem;
                        border-radius: 10px;
                        color: #fff;
                        white-space: pre-wrap;
                        line-height: 1.6;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    }
                    
                    .error-message {
                        background: rgba(255, 99, 71, 0.2);
                        color: #fff;
                        padding: 1rem;
                        border-radius: 10px;
                        margin-bottom: 1rem;
                        text-align: center;
                        border: 1px solid rgba(255, 99, 71, 0.3);
                    }
                    
                    .suggestion-item {
                        display: flex;
                        align-items: center;
                        margin: 5px 0;
                        padding: 8px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 5px;
                    }

                    .suggestion-item span {
                        flex: 1;
                    }

                    .action-button {
                        padding: 4px 12px;
                        border: none;
                        border-radius: 4px;
                        color: white;
                        font-size: 0.8rem;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        width: 45px;
                        text-align: center;
                        margin-left: auto;
                    }

                    .add-button {
                        background: linear-gradient(45deg, #4CAF50, #45a049);
                        width: 45px;
                    }
                    
                    .add-button:hover {
                        transform: translateY(-1px);
                        box-shadow: 0 2px 5px rgba(76, 175, 80, 0.4);
                    }

                    .remove-button {
                        background: linear-gradient(45deg, #ff4444, #cc0000);
                        width: 45px;
                    }

                    .remove-button:hover {
                        transform: translateY(-1px);
                        box-shadow: 0 2px 5px rgba(255, 68, 68, 0.4);
                    }

                    .list-items li {
                        padding: 6px 8px;
                        margin: 5px 0;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 5px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        font-size: 0.9rem;
                    }

                    .list-items li span {
                        margin-right: 10px;
                        flex: 1;
                    }

                    .lists-section {
                        display: flex;
                        gap: 20px;
                        margin-top: 20px;
                    }

                    .list-container {
                        flex: 1;
                        background: rgba(255, 255, 255, 0.1);
                        padding: 15px;
                        border-radius: 10px;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }

                    .list-title {
                        color: #fff;
                        margin-bottom: 15px;
                        font-size: 1.2rem;
                        text-align: center;
                    }

                    .form-select {
                        width: 100%;
                        padding: 12px;
                        border: 2px solid rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        background: rgba(255, 255, 255, 0.1);
                        color: #fff;
                        font-size: 1rem;
                        margin-bottom: 1rem;
                        cursor: pointer;
                    }
                    
                    .form-select:focus {
                        outline: none;
                        background: rgba(255, 255, 255, 0.2);
                        box-shadow: 0 0 15px rgba(255,255,255,0.2);
                        border-color: rgba(255, 255, 255, 0.4);
                    }

                    .suggestions-list {
                        list-style: none;
                        padding: 0;
                    }

                    .suggestions-list li {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 8px;
                        margin: 5px 0;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 5px;
                    }

                    .suggestions-list li span {
                        flex: 1;
                        margin-right: 10px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="profile-section">
                        <a href="/logout" class="profile-button">Profilim ({{ session['username'] }})</a>
                    </div>
                    <h1>🎬 Suggestify</h1>
                    {% if error_message %}
                        <div class="error-message">{{ error_message }}</div>
                    {% endif %}
                    <form method="post">
                        <div class="form-group">
                            <label for="suggestion_type">Öneri Tipi:</label>
                            <select id="suggestion_type" name="suggestion_type" class="form-select">
                                <option value="custom">Özel Giriş</option>
                                <option value="movies">Film Listeme Göre</option>
                                <option value="series">Dizi Listeme Göre</option>
                            </select>
                        </div>
                        <div class="form-group" id="custom_input">
                            <label for="dizi_input">Sevdiğiniz Dizileri Girin:</label>
                            <input type="text" id="dizi_input" name="dizi_input" 
                                   placeholder="Örnek: Dark, The Walking Dead">
                        </div>
                        <button type="submit">Öneriler Al</button>
                    </form>
                    
                    {{ response_html | safe }}

                    <div class="lists-section">
                        <div class="list-container">
                            <h3 class="list-title">📺 Dizi Listem</h3>
                            <ul class="list-items">
                                {% for item in series_list %}
                                <li>
                                    <span>{{ item }}</span>
                                    <button class="action-button remove-button" onclick="removeFromList('series', '{{ item }}')">Sil</button>
                                </li>
                                {% endfor %}
                            </ul>
                        </div>
                        <div class="list-container">
                            <h3 class="list-title">🎬 Film Listem</h3>
                            <ul class="list-items">
                                {% for item in movies_list %}
                                <li>
                                    <span>{{ item }}</span>
                                    <button class="action-button remove-button" onclick="removeFromList('movie', '{{ item }}')">Sil</button>
                                </li>
                                {% endfor %}
                            </ul>
                        </div>
                    </div>
                </div>
                <script>
                    function addToList(type, name) {
                        fetch('/add_to_list', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                type: type,
                                name: name
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                location.reload();
                            } else {
                                alert(data.error || 'Bir hata oluştu!');
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('Bir hata oluştu!');
                        });
                    }

                    function removeFromList(type, name) {
                        if (confirm('Bu öğeyi listeden çıkarmak istediğinize emin misiniz?')) {
                            fetch('/remove_from_list', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    type: type,
                                    name: name
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    location.reload();
                                } else {
                                    alert(data.error || 'Bir hata oluştu!');
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                alert('Bir hata oluştu!');
                            });
                        }
                    }

                    document.getElementById('suggestion_type').addEventListener('change', function() {
                        const customInput = document.getElementById('custom_input');
                        if (this.value === 'custom') {
                            customInput.style.display = 'block';
                            document.getElementById('dizi_input').required = true;
                        } else {
                            customInput.style.display = 'none';
                            document.getElementById('dizi_input').required = false;
                        }
                    });
                </script>
            </body>
        </html>
    '''

    if request.method == 'POST':
        try:
            suggestion_type = request.form.get('suggestion_type', 'custom')
            prompt = ""
            
            if suggestion_type == 'custom':
                user_input = request.form.get('dizi_input', '').strip()
                if not user_input:
                    error_message = "Lütfen en az bir dizi/film adı girin!"
                    return render_template_string(HTML_TEMPLATE, error_message=error_message, response_html="", series_list=series_list, movies_list=movies_list)
                prompt = f"Ben {user_input} gibi içerikleri seviyorum. Bana benzer türde 10 dizi ve 10 film önerir misin? Lütfen önerilerini 'DİZİLER:' ve 'FİLMLER:' başlıkları altında liste halinde yaz. bana sadece dizi ve film adını yaz,açıklama yazma"
            
            elif suggestion_type == 'movies':
                if not movies_list:
                    error_message = "Film listeniz boş! Lütfen önce listeye film ekleyin."
                    return render_template_string(HTML_TEMPLATE, error_message=error_message, response_html="", series_list=series_list, movies_list=movies_list)
                movies_str = ", ".join(movies_list)
                prompt = f"Film listemde {movies_str} var. Bu filmlere benzer türde 10 film önerir misin? Lütfen önerilerini 'FİLMLER:' başlığı altında liste halinde yaz. bana sadece film adını yaz,açıklama yazma"
            
            else:  # series
                if not series_list:
                    error_message = "Dizi listeniz boş! Lütfen önce listeye dizi ekleyin."
                    return render_template_string(HTML_TEMPLATE, error_message=error_message, response_html="", series_list=series_list, movies_list=movies_list)
                series_str = ", ".join(series_list)
                prompt = f"Dizi listemde {series_str} var. Bu dizilere benzer türde 10 dizi önerir misin? Lütfen önerilerini 'DİZİLER:' başlığı altında liste halinde yaz. bana sadece dizi adını yaz,açıklama yazma"

            response = model.generate_content(prompt)
            response_text = response.text
            
            if response_text:
                script_content = RESPONSE_SCRIPT % response_text.replace('`', '\\`').replace("'", "\\'")
                response_html = f'''
                    <div class="response-section">
                        <h2>🎯 Öneriler</h2>
                        <div class="response-content">
                            <div id="suggestions"></div>
                        </div>
                    </div>
                    <script>{script_content}</script>
                '''

        except Exception as e:
            app.logger.error(f"Hata: {str(e)}")
            error_message = "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."
            response_html = ""

    return render_template_string(HTML_TEMPLATE, error_message=error_message, response_html=response_html, series_list=series_list, movies_list=movies_list)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
