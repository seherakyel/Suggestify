from flask import Flask, request
import google.generativeai as genai

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
            )
            response_text = response.text  # Cevabı alıyoruz

    # Basit bir HTML formu döndürüyoruz
    return f'''
        <html>
            <head>
                <title>Dizi Önerici</title>
            </head>
            <body>
                <form method="post">
                    <label for="dizi_input">Dizi Listesi Girin:</label><br>
                    <input type="text" id="dizi_input" name="dizi_input" placeholder="Örnek: Dark, The Walking Dead" style="width:300px"><br><br>
                    <input type="submit" value="Öner">
                </form>
                <hr>
                <h3>Cevap:</h3>
                <div style="white-space: pre-wrap;">{response_text}</div>
            </body>
        </html>
    '''

if __name__ == '__main__':
    # Flask sunucusunu başlat
    app.run(debug=True)
