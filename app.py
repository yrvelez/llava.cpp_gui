from flask import Flask, request, render_template
import subprocess
import os
import re  # Import the regular expression library

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['imageFile']
    image_path = ""
    output_text = ""
    
    if uploaded_file.filename != '':
        # Ensure 'static/uploads' directory exists
        upload_dir = os.path.join('static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Save the uploaded file
        image_path = os.path.join(upload_dir, uploaded_file.filename)
        uploaded_file.save(image_path)

        # Execute the C command
        cmd = f"./llava -m examples/llava/ggml-model-q5_k.gguf --mmproj examples/llava/mmproj-model-f16.gguf --image {image_path}"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Get all the text output
        full_output_text = result.stdout

        # Extract relevant text using regular expressions
        try:
            match = re.search(r'clip_model_load: total allocated memory: (.+?) MB(.+?)main: image encoded in (.+?) ms by CLIP', full_output_text, re.DOTALL)
            if match:
                output_text = match.group(2).strip()  # The relevant text is in the second capturing group
        except re.error:
            output_text = "Error in extracting relevant text."

    return render_template('index.html', image_path=image_path, output_text=output_text)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
