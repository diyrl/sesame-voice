# CSM Web Interface

A simple and sleek web interface for the Conversation Speech Model (CSM) running on Apple Silicon with MLX.

## Features

- Clean, modern UI
- Multiple speaker voices
- Adjustable temperature and minimum probability settings
- Audio playback directly in the browser
- History of generated speech
- Download generated audio files
- Real-time performance statistics

## Getting Started

To run the web interface:

1. Make sure you have completed the installation steps in the main README.md

2. Run the web application using the provided script:
   ```bash
   ./run_webapp.sh
   ```

3. Open your web browser and go to one of:
   ```
   http://localhost:8080
   http://127.0.0.1:8080
   ```
   
   If you want to access it from another device on your network, use your computer's IP address:
   ```
   http://YOUR_IP_ADDRESS:8080
   ```

## Using the Interface

1. **Enter Text**: Type or paste the text you want to convert to speech in the text area.

2. **Voice Settings**:
   - Select a speaker voice from the dropdown (0-4)
   - Adjust the temperature slider (higher values = more variation)
   - Adjust the minimum probability slider (controls token filtering)
   - Set the maximum duration in milliseconds

3. **Generate Speech**: Click the "Generate Speech" button and wait for the generation to complete.

4. **Listen and Download**: 
   - Play the generated audio directly in the browser
   - Download the audio file by clicking the "Download Audio" button
   - View generation statistics (duration, generation time, real-time factor)

5. **History**: 
   - Previously generated speech is stored in the history section
   - Click "Play" on any history item to listen to it again

## Troubleshooting

### If you can't access the web interface:

1. **Check the server is running**: The terminal should show "Running on http://0.0.0.0:8080"

2. **Try different URLs**:
   - http://localhost:8080
   - http://127.0.0.1:8080
   - http://YOUR_COMPUTER_IP:8080

3. **Check firewall settings**: Make sure port 8080 is not blocked

4. **Restart the server**: Press Ctrl+C to stop the server, then run `./run_webapp.sh` again

### If audio generation fails:

1. Check that the model was installed correctly
2. For performance issues, try generating shorter text segments
3. The first generation might be slower as the model is loaded and compiled

## Customization

You can customize the interface by editing:
- `templates/index.html` - HTML structure 
- `static/css/style.css` - Visual styling
- `app.py` - Backend functionality