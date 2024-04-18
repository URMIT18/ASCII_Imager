from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image

app = Flask(__name__)

def get_str_ascii(intent):
    index = intent // 32
    ascii_chars = ['', '.', ',', '-', '~', '+', '=', '@']
    return ascii_chars[index]

def get_image_ascii(image_path, scale):
    img = Image.open(image_path)
    width, height = img.size
    ascii_art = ''
    for y in range(0, height, scale * 2):
        for x in range(0, width, scale):
            pix = img.getpixel((x, y))
            if len(pix) < 4:  # Check if alpha channel exists
                intent = sum(pix) // 3
            else:
                intent = sum(pix[:3]) // 3
                if pix[3] == 0:
                    intent = 0
            ascii_art += get_str_ascii(intent)
        if y % (scale * 2) == 0:
            ascii_art += '\n'
    return ascii_art

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ascii', methods=['POST'])
def ascii_art():
    try:
        if 'image_file' not in request.files:
            error_message = "Error: No file part in the request."
            return jsonify({"error": error_message}), 400
        
        image_file = request.files['image_file']
        if image_file.filename == '':
            error_message = "Error: No selected file."
            return jsonify({"error": error_message}), 400

        if not image_file.mimetype.startswith('image'):
            error_message = "Error: Uploaded file is not an image."
            return jsonify({"error": error_message}), 400
        
        image_path = 'uploaded_image.png'
        image_file.save(image_path)

        scale = int(request.form.get('scale', 4))

        ascii_art = get_image_ascii(image_path, scale)
        
        with open('ascii_image.txt', 'w') as file:
            file.write(ascii_art)

        return send_file('ascii_image.txt', as_attachment=True)

    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"error": error_message}), 400

