#!/usr/bin/env python3
"""
CSM Speech Generator - A web UI for the CSM text-to-speech model
"""

import os
import time
import numpy as np
import torch
import torchaudio
from datetime import datetime
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

# Create directories
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
    """Return the built-in voice presets"""
    presets_by_category = get_presets_by_category()
    
    # Convert to JSON-serializable format
    result = {}
    for category, presets in presets_by_category.items():
        result[category] = [preset.to_dict() for preset in presets]
    
    return jsonify(result)

# New endpoints for voice preset database
from voice_db import VoicePreset, db as voice_db

@app.route('/api/presets', methods=['GET'])
def get_all_presets():
    """Get all saved voice presets"""
    presets = voice_db.get_all_presets()
    return jsonify([preset.to_dict() for preset in presets])

@app.route('/api/presets/<int:preset_id>', methods=['GET'])
def get_preset(preset_id):
    """Get a specific preset by ID"""
    preset = voice_db.get_preset_by_id(preset_id)
    if not preset:
        return jsonify({"error": "Preset not found"}), 404
    return jsonify(preset.to_dict())

@app.route('/api/presets', methods=['POST'])
def create_preset():
    """Create a new voice preset"""
    data = request.json
    
    # Basic validation
    required_fields = ['name', 'speaker_id', 'temperature', 'min_p']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    preset = VoicePreset(
        name=data['name'],
        speaker_id=int(data['speaker_id']),
        temperature=float(data['temperature']),
        min_p=float(data['min_p']),
        seed=data.get('seed'),
        speed=float(data.get('speed', 1.0)),
        description=data.get('description')
    )
    
    preset_id = voice_db.create_preset(preset)
    
    # Check if sample audio was included
    if 'audio_path' in data and 'text' in data:
        voice_db.add_voice_sample(preset_id, data['audio_path'], data['text'])
    
    # Return the created preset with its ID
    preset.id = preset_id
    return jsonify(preset.to_dict()), 201

@app.route('/api/presets/<int:preset_id>', methods=['PUT'])
def update_preset(preset_id):
    """Update an existing preset"""
    data = request.json
    
    # Check if preset exists
    existing = voice_db.get_preset_by_id(preset_id)
    if not existing:
        return jsonify({"error": "Preset not found"}), 404
    
    # Update the preset
    preset = VoicePreset(
        id=preset_id,
        name=data.get('name', existing.name),
        speaker_id=int(data.get('speaker_id', existing.speaker_id)),
        temperature=float(data.get('temperature', existing.temperature)),
        min_p=float(data.get('min_p', existing.min_p)),
        seed=data.get('seed', existing.seed),
        speed=float(data.get('speed', existing.speed)),
        description=data.get('description', existing.description)
    )
    
    success = voice_db.update_preset(preset)
    
    # Check if sample audio was included
    if success and 'audio_path' in data and 'text' in data:
        voice_db.add_voice_sample(preset_id, data['audio_path'], data['text'])
    
    return jsonify(preset.to_dict())

@app.route('/api/presets/<int:preset_id>', methods=['DELETE'])
def delete_preset(preset_id):
    """Delete a voice preset"""
    success = voice_db.delete_preset(preset_id)
    if not success:
        return jsonify({"error": "Preset not found"}), 404
    return jsonify({"message": "Preset deleted successfully"})

@app.route('/api/presets/<int:preset_id>/samples', methods=['GET'])
def get_preset_samples(preset_id):
    """Get all audio samples for a preset"""
    # Check if preset exists
    preset = voice_db.get_preset_by_id(preset_id)
    if not preset:
        return jsonify({"error": "Preset not found"}), 404
        
    samples = voice_db.get_voice_samples(preset_id)
    return jsonify(samples)

@app.route('/api/presets/similar', methods=['GET'])
def find_similar_presets():
    """Find presets with similar settings"""
    speaker_id = request.args.get('speaker_id')
    temperature = request.args.get('temperature')
    min_p = request.args.get('min_p')
    seed = request.args.get('seed')
    
    if not all([speaker_id, temperature, min_p]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    presets = voice_db.find_similar_preset(
        speaker_id=int(speaker_id),
        temperature=float(temperature),
        min_p=float(min_p),
        seed=seed
    )
    
    return jsonify([preset.to_dict() for preset in presets])

@app.route('/generate', methods=['POST'])
def generate_speech():
    """Generate speech from text"""
    try:
        # Get parameters from request
        text = request.form.get('text', 'Hello from CSM!')
        speaker_id = request.form.get('speaker', '0')
        
        # Convert speaker ID to integer but limit to 0-9 range
        try:
            speaker = int(speaker_id) % 10  # Enforce range 0-9
        except ValueError:
            speaker = 0
        
        temperature = float(request.form.get('temperature', 0.7))
        min_p = float(request.form.get('min_p', 0.05))
        max_duration = int(request.form.get('max_duration', 30000))  # Default to 30 seconds
        
        # Get random seed if provided to ensure consistent results
        seed = request.form.get('seed')
        seed_value = None
        
        if seed:
            try:
                seed_value = int(seed)
                # Set random seed for consistent generation
                mx.random.seed(seed_value)
                print(f"Using seed: {seed_value}")
            except ValueError:
                print(f"Invalid seed provided: {seed}, using random seed")
        else:
            # If no seed provided, let's generate a random one for reproducibility
            seed_value = int(time.time()) % 1000000
            mx.random.seed(seed_value)
            print(f"No seed provided, using random seed: {seed_value}")
        
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
        
        # Auto-save this voice preset if requested
        preset_id = None
        if request.form.get('auto_save') == 'true':
            # Check if similar preset exists
            similar_presets = voice_db.find_similar_preset(
                speaker_id=speaker,
                temperature=temperature,
                min_p=min_p,
                seed=str(seed_value) if seed_value else None
            )
            
            if similar_presets:
                # Use the first similar preset
                preset_id = similar_presets[0].id
                
                # Add this generation as a sample
                voice_db.add_voice_sample(
                    preset_id=preset_id,
                    audio_path=web_path,
                    text=text
                )
            else:
                # Create a new preset
                preset_name = f"Voice {speaker} (T:{temperature:.2f}, P:{min_p:.2f})"
                if seed_value:
                    preset_name += f", S:{seed_value}"
                
                preset = VoicePreset(
                    name=preset_name,
                    speaker_id=speaker,
                    temperature=temperature,
                    min_p=min_p,
                    seed=str(seed_value) if seed_value else None,
                    speed=1.0,
                    description=f"Auto-saved voice from generation on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                
                preset_id = voice_db.create_preset(preset)
                
                # Add this generation as the first sample
                voice_db.add_voice_sample(
                    preset_id=preset_id,
                    audio_path=web_path,
                    text=text
                )
        
        response = {
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
                'seed': seed_value
            }
        }
        
        # Add preset info if created or found
        if preset_id:
            response['preset_id'] = preset_id
        
        return jsonify(response)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error generating speech: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return jsonify({
            'success': False,
            'message': f"Error generating speech: {str(e)}",
            'error_details': error_traceback
        }), 500  # Return 500 status to clearly indicate server error

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