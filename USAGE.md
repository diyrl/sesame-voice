# CSM-MLX Usage Guide

This guide explains how to use the Conversation Speech Model (CSM) implementation for Apple Silicon using MLX.

## Prerequisites

- A Mac with Apple Silicon (M1/M2/M3)
- Python 3.12+ installed

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/senstella/csm-mlx.git
   cd csm-mlx
   ```

2. Install using uv (recommended):
   ```bash
   uv add git+https://github.com/senstella/csm-mlx
   ```

   Or install using pip:
   ```bash
   pip install git+https://github.com/senstella/csm-mlx
   ```

3. Install additional dependencies:
   ```bash
   pip install torch torchaudio numpy audiofile
   ```

## Usage

### Simple Text-to-Speech Generation

Use the `generate_speech.py` script to generate speech from text:

```bash
python generate_speech.py --text "Hello from CSM!" --output hello.wav
```

Options:
- `--text` or `-t`: Text to convert to speech
- `--output` or `-o`: Output file path (default: output.wav)
- `--temp`: Temperature for sampling (higher = more variation, default: 0.5)
- `--min_p`: Minimum probability for sampling (default: 0.1)
- `--speaker` or `-s`: Speaker ID (0, 1, 2, etc., default: 0)
- `--max_duration` or `-d`: Maximum audio duration in milliseconds (default: 10000)

### Conversation Demo

Run the conversation demo to see how context works:

```bash
python conversation_demo.py
```

This will generate a demo conversation with multiple turns between two speakers and save both individual turns and a complete conversation audio file in the `outputs/conversation/` directory.

### Using the API in Your Own Code

Here's a basic example of how to use the CSM API in your own Python code:

```python
from mlx_lm.sample_utils import make_sampler
from huggingface_hub import hf_hub_download
from csm_mlx import CSM, csm_1b, generate
import numpy as np
import torch
import torchaudio

# Initialize the model
csm = CSM(csm_1b())
weight = hf_hub_download(repo_id="senstella/csm-1b-mlx", filename="ckpt.safetensors")
csm.load_weights(weight)

# Generate audio from text
audio = generate(
    csm,
    text="Hello from CSM!",
    speaker=0,
    context=[],
    max_audio_length_ms=10_000,
    sampler=make_sampler(temp=0.5, min_p=0.1),
)

# Save the generated audio
torchaudio.save("hello.wav", torch.Tensor(np.asarray(audio)).unsqueeze(0).cpu(), 24_000)
```

### Adding Conversation Context

For a conversation with context:

```python
from csm_mlx import CSM, csm_1b, generate, Segment
import mlx.core as mx

# Initialize the model
csm = CSM(csm_1b())
weight = hf_hub_download(repo_id="senstella/csm-1b-mlx", filename="ckpt.safetensors")
csm.load_weights(weight)

# Previous conversation turns
context = [
    Segment(
        speaker=0,
        text="How are you doing today?",
        audio=mx.array(...)  # Previous audio for this segment
    ),
    Segment(
        speaker=1,
        text="I'm doing great, thank you!",
        audio=mx.array(...)  # Previous audio for this segment
    )
]

# Generate a response
audio = generate(
    csm,
    text="That's wonderful to hear!",
    speaker=0,
    context=context,
    max_audio_length_ms=5_000
)
```

## Performance Tips

1. The first generation might be slower due to model loading and compilation.
2. Shorter texts generate faster than longer ones.
3. Different speaker IDs can produce different voice characteristics.
4. The model runs entirely on your Mac's Neural Engine and doesn't require internet after the initial model download.

## Limitations

- Maximum audio length is limited to protect against excessive resource usage.
- The model may struggle with certain pronunciations or very technical terms.
- Higher temperature values can lead to more varied but sometimes less accurate speech.

## Troubleshooting

If you encounter issues:

1. Make sure you're using Python 3.12+
2. Check that all dependencies are installed correctly
3. Verify that you're running on Apple Silicon hardware
4. Restart your Python environment if model loading fails