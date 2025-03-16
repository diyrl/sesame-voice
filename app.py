#!/usr/bin/env python3
"""
CSM Speech Generator - A web UI for the CSM text-to-speech model
"""

import os
import time
import numpy as np
import torch
import torchaudio
from flask import Flask, render_template, request, jsonify, send_file
import mlx.core as mx
from mlx_lm.sample_utils import make_sampler
from huggingface_hub import hf_hub_download
from csm_mlx import CSM, csm_1b, generate, Segment
from csm_mlx.voice_presets import get_presets_by_category, get_preset_by_name, BASIC_VOICES

app = Flask(__name__)

# Global variables for model and configuration
model = None
output_dir = "static/audio"  # For browser playback
downloads_dir = "outputs"    # For downloads
os.makedirs(output_dir, exist_ok=True)
os.makedirs(downloads_dir, exist_ok=True)

def get_model():
    """Load the model once and reuse it for multiple requests"""
    global model
    if model is None:
        print("Initializing CSM model...")
        start_time = time.time()
        model = CSM(csm_1b())
        weight = hf_hub_download(repo_id="senstella/csm-1b-mlx", filename="ckpt.safetensors")
        model.load_weights(weight)
        print(f"Model loaded in {time.time() - start_time:.2f} seconds")
    return model

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/voice_presets', methods=['GET'])
def get_voices():
    """Return the available voice presets"""
    presets_by_category = get_presets_by_category()
    
    # Convert to JSON-serializable format
    result = {}
    for category, presets in presets_by_category.items():
        result[category] = [preset.to_dict() for preset in presets]
    
    return jsonify(result)

@app.route('/generate', methods=['POST'])
def generate_speech():
    """Generate speech from text"""
    # Get parameters from request
    text = request.form.get('text', 'Hello from CSM!')
    
    # We support two ways to specify the voice, but in this simplified UI,
    # we'll only use the direct parameters
    speaker_id = request.form.get('speaker', '0')
    # Convert speaker ID to integer but limit to 0-9 range
    try:
        speaker = int(speaker_id) % 10  # Enforce range 0-9
    except ValueError:
        speaker = 0
    
    temperature = float(request.form.get('temperature', 0.7))
    min_p = float(request.form.get('min_p', 0.05))
    max_duration = int(request.form.get('max_duration', 30000))  # Default to 30 seconds
    
    # Generate unique filenames
    timestamp = int(time.time())
    web_filename = f"speech_{timestamp}_speaker_{speaker}.wav"
    download_filename = f"speech_{timestamp}_speaker_{speaker}.wav"
    
    web_path = os.path.join(output_dir, web_filename)
    download_path = os.path.join(downloads_dir, download_filename)
    
    # Get the model
    csm = get_model()
    
    # Ensure text ends with punctuation for better speech quality
    if text and not text[-1] in ['.', '!', '?', ',', ';', ':', '-']:
        text += '.'
    
    # Generate audio - always use max allowed length to ensure full text is generated
    start_time = time.time()
    try:
        audio = generate(
            csm,
            text=text,
            speaker=speaker,
            context=[],
            max_audio_length_ms=max_duration,
            sampler=make_sampler(temp=temperature, min_p=min_p),
        )
        generation_time = time.time() - start_time
        
        # Convert to numpy and save
        audio_array = np.asarray(audio)
        
        # Save for web playback
        torchaudio.save(web_path, torch.Tensor(audio_array).unsqueeze(0).cpu(), 24_000)
        
        # Save for download (same file for now, but could be different format if needed)
        torchaudio.save(download_path, torch.Tensor(audio_array).unsqueeze(0).cpu(), 24_000)
        
        # Calculate audio duration
        audio_duration = len(audio) / 24000  # 24kHz sample rate
        
        return jsonify({
            'success': True,
            'message': 'Speech generated successfully',
            'audio_path': f"/static/audio/{web_filename}",
            'download_path': f"/download/{download_filename}",
            'filename': download_filename,
            'duration': f"{audio_duration:.2f}",
            'generation_time': f"{generation_time:.2f}",
            'real_time_factor': f"{generation_time / audio_duration:.2f}" if audio_duration > 0 else "0.0",
            'voice_parameters': {
                'speaker': speaker,
                'temperature': temperature,
                'min_p': min_p,
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error generating speech: {str(e)}",
        })

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    """Serve the generated audio file for web playback"""
    try:
        return send_file(os.path.join(output_dir, filename))
    except Exception as e:
        return f"Error serving audio file: {str(e)}", 404

@app.route('/download/<filename>')
def download_audio(filename):
    """Serve the generated audio file for download"""
    try:
        return send_file(os.path.join(downloads_dir, filename), 
                        as_attachment=True, 
                        download_name=filename)
    except Exception as e:
        return f"Error downloading audio file: {str(e)}", 404

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'ok',
        'message': 'CSM Speech Generator is running',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    # Force preloading the model
    get_model()
    print("Model loaded, starting server...")
    # Use 0.0.0.0 to make it accessible from any network interface
    app.run(debug=True, host='0.0.0.0', port=8080)