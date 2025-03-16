#!/usr/bin/env python3
"""
CSM (Conversation Speech Model) Text-to-Speech Generator

This script generates speech from text using the CSM model for Apple Silicon with MLX.

Usage:
    python generate_speech.py --text "Your text here" --output output.wav --temp 0.5 --speaker 0 --max_duration 10000
"""

import argparse
import os
import time
import numpy as np
import torch
import torchaudio
import audiofile
from mlx_lm.sample_utils import make_sampler
from huggingface_hub import hf_hub_download
from csm_mlx import CSM, csm_1b, generate

def generate_speech(text, output_path, temperature=0.5, min_p=0.1, speaker=0, max_duration=10000):
    """Generate speech from text using the CSM model."""
    start_time = time.time()
    
    # Initialize the model
    print("Initializing CSM model...")
    csm = CSM(csm_1b())
    
    # Download and load weights
    print("Loading model weights...")
    weight = hf_hub_download(repo_id="senstella/csm-1b-mlx", filename="ckpt.safetensors")
    csm.load_weights(weight)
    print(f"Model loaded in {time.time() - start_time:.2f} seconds")
    
    # Generate audio from text
    print(f"Generating speech for: '{text}'")
    gen_start = time.time()
    
    audio = generate(
        csm,
        text=text,
        speaker=speaker,
        context=[],
        max_audio_length_ms=max_duration,
        sampler=make_sampler(temp=temperature, min_p=min_p),
    )
    
    gen_time = time.time() - gen_start
    print(f"Speech generated in {gen_time:.2f} seconds")
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or '.', exist_ok=True)
    
    # Save the generated audio
    torchaudio.save(output_path, torch.Tensor(np.asarray(audio)).unsqueeze(0).cpu(), 24_000)
    
    # Calculate audio duration
    audio_duration = len(audio) / 24000  # 24kHz sample rate
    
    print(f"Audio saved to: {output_path}")
    print(f"Audio duration: {audio_duration:.2f} seconds")
    print(f"Real-time factor: {gen_time / audio_duration:.2f}x")

def main():
    parser = argparse.ArgumentParser(description="Generate speech using CSM model")
    parser.add_argument("--text", "-t", type=str, required=True, help="Text to convert to speech")
    parser.add_argument("--output", "-o", type=str, default="output.wav", help="Output audio file path")
    parser.add_argument("--temp", type=float, default=0.5, help="Temperature for sampling (higher = more variation)")
    parser.add_argument("--min_p", type=float, default=0.1, help="Minimum probability for sampling")
    parser.add_argument("--speaker", "-s", type=int, default=0, help="Speaker ID (0, 1, 2, etc.)")
    parser.add_argument("--max_duration", "-d", type=int, default=10000, 
                       help="Maximum audio duration in milliseconds")
    
    args = parser.parse_args()
    
    generate_speech(
        args.text, 
        args.output, 
        temperature=args.temp, 
        min_p=args.min_p,
        speaker=args.speaker,
        max_duration=args.max_duration
    )

if __name__ == "__main__":
    main()