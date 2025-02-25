from flask import Flask, request
import google.generativeai as genai
import os

# Google Gemini API anahtarınızı buraya girin:
genai.configure(api_key="AIzaSyBMeBWG1Jg6bKzp2wvK8Bersfm02DJay8w")

# Örnek generation_config ayarları
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Model nesnesini tanımlıyoruz
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=generation_config,
)

# Flask uygulaması
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    response_text = ""
    
    # Eğer form POST ile submit edildiyse
    if request.method == 'POST':
        # Formdan gelen kullanıcı girişi
        user_input = request.form.get('dizi_input', '')

        if user_input:
            # Gemini API'ye istek atıyoruz
            response = model.generate_content(
                f"Sana bir dizi listesi veriyorum: {user_input}\n"
                "Bana bu dizi listesine göre yeni dizi önerileri sunar mısın?"
                "Önerileri sadece dizilerin adını yaz, açıklamasını yazma"
            )
            response_text = response.text  # Cevabı alıyoruz

    # Modern tasarımlı HTML sayfası
    return f'''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Suggestify - Akıllı Dizi Önerici</title>
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
                    
                    .container {{
                        background: rgba(255, 255, 255, 0.15);
                        backdrop-filter: blur(10px);
                        padding: 2rem;
                        border-radius: 20px;
                        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                        width: 100%;
                        max-width: 600px;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }}
                    
                    h1 {{
                        color: #fff;
                        text-align: center;
                        margin-bottom: 2rem;
                        font-size: 2.5rem;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                        background: linear-gradient(to right, #fff, #FFD700);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                    }}
                    
                    .form-group {{
                        margin-bottom: 1.5rem;
                    }}
                    
                    label {{
                        color: #fff;
                        display: block;
                        margin-bottom: 0.5rem;
                        font-size: 1.1rem;
                    }}
                    
                    input[type="text"] {{
                        width: 100%;
                        padding: 12px;
                        border: 2px solid rgba(255, 255, 255, 0.2);
                        border-radius: 10px;
                        background: rgba(255, 255, 255, 0.1);
                        color: #fff;
                        font-size: 1rem;
                        transition: all 0.3s ease;
                    }}
                    
                    input[type="text"]:focus {{
                        outline: none;
                        background: rgba(255, 255, 255, 0.2);
                        box-shadow: 0 0 15px rgba(255,255,255,0.2);
                        border-color: rgba(255, 255, 255, 0.4);
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
                        font-weight: bold;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }}
                    
                    button:hover {{
                        background: linear-gradient(45deg, #FFB88C, #FF6B6B);
                        transform: translateY(-2px);
                        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
                    }}
                    
                    .response-section {{
                        margin-top: 2rem;
                        padding-top: 2rem;
                        border-top: 1px solid rgba(255,255,255,0.2);
                    }}
                    
                    .response-content {{
                        background: rgba(255, 255, 255, 0.1);
                        padding: 1.5rem;
                        border-radius: 10px;
                        color: #fff;
                        white-space: pre-wrap;
                        line-height: 1.6;
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    }}
                    
                    .response-title {{
                        color: #fff;
                        margin-bottom: 1rem;
                        font-size: 1.5rem;
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎬 Suggestify</h1>
                    <form method="post">
                        <div class="form-group">
                            <label for="dizi_input">Sevdiğiniz Dizileri Girin:</label>
                            <input type="text" id="dizi_input" name="dizi_input" 
                                   placeholder="Örnek: Dark, The Walking Dead" 
                                   required>
                        </div>
                        <button type="submit">Dizi Öner</button>
                    </form>
                    
                    {f'''
                    <div class="response-section">
                        <h2 class="response-title">🎯 Önerilen Diziler</h2>
                        <div class="response-content">{response_text}</div>
                    </div>
                    ''' if response_text else ''}
                </div>
            </body>
        </html>
    '''

if __name__ == '__main__':
    # Render için port ayarı
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
