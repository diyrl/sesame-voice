from mlx_lm.sample_utils import make_sampler
from huggingface_hub import hf_hub_download
from csm_mlx import CSM, csm_1b, generate
import numpy as np
import torch
import torchaudio
import audiofile
import os

# Create output directory if it doesn't exist
os.makedirs("outputs", exist_ok=True)

# Initialize the model
print("Initializing CSM model...")
csm = CSM(csm_1b())  # csm_1b() is a configuration for the CSM model.
print("Downloading weights...")
weight = hf_hub_download(repo_id="senstella/csm-1b-mlx", filename="ckpt.safetensors")
print(f"Downloaded weights to {weight}")
print("Loading weights...")
csm.load_weights(weight)
print("Model loaded successfully!")

# Generate audio from text
text = "Hello! This is a test of the Conversation Speech Model running on Apple Silicon with MLX."
print(f"Generating audio for text: '{text}'")

audio = generate(
    csm,
    text=text,
    speaker=0,
    context=[],
    max_audio_length_ms=10_000,
    sampler=make_sampler(temp=0.5, min_p=0.1),
)

print("Audio generated successfully!")

# Save the generated audio using torchaudio
output_path = "outputs/audio_torchaudio.wav"
torchaudio.save(output_path, torch.Tensor(np.asarray(audio)).unsqueeze(0).cpu(), 24_000)
print(f"Audio saved to {output_path}")

# Save the audio using audiofile as well (as a backup)
output_path2 = "outputs/audio_audiofile.wav"
audiofile.write(output_path2, np.asarray(audio), 24_000)
print(f"Audio also saved to {output_path2}")

print("Done!")