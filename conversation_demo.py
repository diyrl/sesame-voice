#!/usr/bin/env python3
"""
CSM (Conversation Speech Model) Conversation Demo

This script demonstrates how to use CSM for generating a conversation with context.
"""

import os
import time
import numpy as np
import torch
import torchaudio
import mlx.core as mx
from mlx_lm.sample_utils import make_sampler
from huggingface_hub import hf_hub_download
from csm_mlx import CSM, csm_1b, generate, Segment

def main():
    # Create output directory
    output_dir = "outputs/conversation"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the model
    print("Initializing CSM model...")
    start_time = time.time()
    csm = CSM(csm_1b())
    weight = hf_hub_download(repo_id="senstella/csm-1b-mlx", filename="ckpt.safetensors")
    csm.load_weights(weight)
    print(f"Model loaded in {time.time() - start_time:.2f} seconds")
    
    # Set up a conversation
    conversation = [
        {"speaker": 0, "text": "Hello! How are you doing today?"},
        {"speaker": 1, "text": "I'm doing great, thanks for asking! How about you?"},
        {"speaker": 0, "text": "I'm wonderful, thanks! What are your plans for today?"},
        {"speaker": 1, "text": "I'm going to work on some coding projects and then relax."}
    ]
    
    # Generate and save each turn of the conversation
    context = []
    
    for i, turn in enumerate(conversation):
        speaker = turn["speaker"]
        text = turn["text"]
        
        print(f"\nGenerating turn {i+1} (Speaker {speaker}): '{text}'")
        gen_start = time.time()
        
        # Generate audio
        audio = generate(
            csm,
            text=text,
            speaker=speaker,
            context=context,
            max_audio_length_ms=10_000,
            sampler=make_sampler(temp=0.5, min_p=0.1),
        )
        
        gen_time = time.time() - gen_start
        audio_array = np.asarray(audio)
        
        # Save audio
        output_path = f"{output_dir}/turn_{i+1}_speaker_{speaker}.wav"
        torchaudio.save(output_path, torch.Tensor(audio_array).unsqueeze(0).cpu(), 24_000)
        
        # Calculate audio duration
        audio_duration = len(audio) / 24000  # 24kHz sample rate
        print(f"  Generated in {gen_time:.2f} seconds")
        print(f"  Audio duration: {audio_duration:.2f} seconds")
        print(f"  Real-time factor: {gen_time / audio_duration:.2f}x")
        print(f"  Saved to: {output_path}")
        
        # Add this turn to context for the next turn
        context.append(Segment(
            speaker=speaker,
            text=text,
            audio=mx.array(audio_array)
        ))
    
    # Concatenate all audio files into a single conversation
    concatenate_conversation(output_dir, conversation)
    
    print("\nConversation demo completed!")

def concatenate_conversation(output_dir, conversation):
    """Concatenate all audio files into a single conversation with a short pause between turns."""
    print("\nConcatenating all turns into a single conversation file...")
    
    all_audio = []
    sample_rate = 24000
    pause_samples = int(0.5 * sample_rate)  # 0.5 second pause
    pause = torch.zeros(1, pause_samples)
    
    for i, turn in enumerate(conversation):
        audio_path = f"{output_dir}/turn_{i+1}_speaker_{turn['speaker']}.wav"
        waveform, _ = torchaudio.load(audio_path)
        
        # Add a speaker label before each turn (for demo visualization)
        all_audio.append(waveform)
        
        # Add pause after each turn (except the last one)
        if i < len(conversation) - 1:
            all_audio.append(pause)
    
    # Concatenate all audio
    full_conversation = torch.cat(all_audio, dim=1)
    
    # Save the full conversation
    output_path = f"{output_dir}/full_conversation.wav"
    torchaudio.save(output_path, full_conversation, sample_rate)
    
    print(f"Full conversation saved to: {output_path}")
    print(f"Total duration: {full_conversation.shape[1] / sample_rate:.2f} seconds")

if __name__ == "__main__":
    main()