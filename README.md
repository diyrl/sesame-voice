# CSM Speech Generator

A web interface for generating customizable human-like speech using the Conversation Speech Model (CSM) on Apple Silicon.

## Quick Start

```bash
# Clone repo
git clone https://github.com/yourusername/csm-mlx.git
cd csm-mlx

# Install dependencies
pip install git+https://github.com/senstella/csm-mlx
pip install torch torchaudio numpy flask

# Start server
python app.py
```

Visit http://localhost:8080 in your browser

## Voice Creation Guide

### Understanding Parameters

| Parameter      | Effect                                       | Range       | For Deeper, Calmer Voice |
|----------------|----------------------------------------------|-------------|--------------------------|
| Speaker ID     | Base voice identity                          | 0-9         | 4 (Female)               |
| Seed           | Makes voice consistent between generations   | Any integer | Try 123456, 555555       |
| Expressiveness | Controls voice variation                     | 0.1-1.5     | 0.3-0.5 (lower = calmer) |
| Speech Clarity | Controls token filtering                     | 0.01-0.2    | 0.08-0.12 (higher)       |
| Speech Speed   | Controls playback rate                       | 0.7-1.3     | 0.8-0.9 (slower)         |

### Creating Unique Voices

1. **Select Speaker ID**: Start with ID 4 for female voice
2. **Choose a Seed**: Seed ensures voice consistency
3. **Adjust Expressiveness**: Lower for calmer voice
4. **Set Clarity**: Higher for clearer articulation
5. **Generate**: Test with the same text sample
6. **Save**: Voice settings are automatically saved

### Voice Combinations

For a deeper, calmer female voice, try:
- Speaker ID 4 + Seed 555555 + Expressiveness 0.4 + Clarity 0.1
- Speaker ID 4 + Seed 123456 + Expressiveness 0.3 + Clarity 0.12

For different voice characteristics:
- Warm Voice: Speaker ID 3 + Expressiveness 0.7 + Clarity 0.03
- Clear Voice: Speaker ID 2 + Expressiveness 0.5 + Clarity 0.15
- Expressive Voice: Speaker ID 6 + Expressiveness 0.9 + Clarity 0.05

## Features

- **10 Voice Options**: Full range of speaker IDs with unique characteristics
- **Consistent Voices**: Random seed selection ensures reproducible results
- **Voice Presets**: Automatically save and recall successful voice settings
- **Local Processing**: All generation happens on your Mac

## Requirements

- Mac with Apple Silicon (M1/M2/M3)
- Python 3.10+
- Web browser

## Acknowledgements

- [csm-mlx](https://github.com/senstella/csm-mlx) - CSM implementation for Apple Silicon
- [MLX](https://github.com/ml-explore/mlx) - ML framework for Apple Silicon