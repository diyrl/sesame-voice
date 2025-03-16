# CSM Speech Generator

A elegant web interface for generating human-like speech using the Conversation Speech Model (CSM) on Apple Silicon.

## Overview

This application provides a clean, user-friendly interface for the CSM speech synthesis model. It allows you to generate natural-sounding speech directly in your browser, with controls for different voice types, expressiveness, and other parameters.

## Acknowledgements

This project builds upon:

- [csm-mlx](https://github.com/senstella/csm-mlx) - CSM implementation for Apple Silicon using MLX
- [Sesame](https://sesame.com) - Original PyTorch implementation and weights
- [torchtune](https://github.com/pytorch/torchtune) project - Providing LLaMA attention implementation
- [MLX](https://github.com/ml-explore/mlx) project - The framework that made this implementation possible

## Features

- **Clean, minimal interface** with a black and white design
- **Multiple voice options** with clearly labeled human-like voices
- **Adjustable parameters** for fine-tuning speech generation:
  - Expressiveness (temperature)
  - Voice clarity
  - Maximum duration
- **Audio playback** directly in the browser
- **Download generated audio** files
- **History of generated speech** for easy reference
- **Fully local processing** - your data never leaves your computer

## Requirements

- Mac with Apple Silicon (M1/M2/M3)
- Python 3.12+
- Web browser

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/diyrl/sesame-voice.git
   cd sesame-voice
   ```

2. Install the package and dependencies:
   ```bash
   # Using uv (recommended)
   uv add git+https://github.com/senstella/csm-mlx
   
   # Or using pip
   pip install git+https://github.com/senstella/csm-mlx
   ```

3. Install additional requirements:
   ```bash
   pip install torch torchaudio numpy audiofile flask
   ```

## Usage

1. Start the web server:
   ```bash
   ./run_webapp.sh
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

3. Enter your text, select a voice, adjust parameters, and click "Generate Speech"

4. Listen to the generated speech directly in the browser or download the audio file

## Voice Options

The application provides several voice options:

- **Natural Male & Female** - The most human-like voices
- **Standard Neutral** - A balanced, neutral voice
- **Warm Voice** - A warmer, friendlier tone
- **Bright Voice** - A more energetic, upbeat voice
- **Additional experimental voices** - For more variety

## Adjustable Parameters

- **Expressiveness** - Controls the variation in speech (temperature)
- **Voice Clarity** - Adjusts the token filtering (minimum probability)
- **Max Duration** - Sets the maximum length of generated audio

## Management Scripts

The application includes several helpful scripts:

- `run_webapp.sh` - Starts the web server
- `test_server.sh` - Tests if the server is running correctly
- `reset_audio.sh` - Clears all generated audio files

## How It Works

The application uses the CSM model, which is a neural speech synthesis model:

1. Text is tokenized and processed by the CSM model
2. The model generates audio tokens representing the speech
3. These tokens are converted to audio waveforms
4. The audio is played in your browser or saved as a WAV file

All processing happens locally on your Mac, using the Apple Neural Engine through MLX.

## License

Apache 2.0 (following the original license of CSM)