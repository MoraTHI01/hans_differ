#!/usr/bin/env python3
"""
gpu_test_simple.py - Simple LLM training test for single GPU
"""
 
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import time
from datetime import datetime
 
class SimpleTextDataset(Dataset):
    """Simple dataset for testing"""
    def __init__(self, num_samples=1000, seq_length=128):
        self.num_samples = num_samples
        self.seq_length = seq_length
        self.vocab_size = 50000
    def __len__(self):
        return self.num_samples
    def __getitem__(self, idx):
        # Generate random sequences
        input_ids = torch.randint(0, self.vocab_size, (self.seq_length,))
        labels = torch.randint(0, self.vocab_size, (self.seq_length,))
        return {'input_ids': input_ids, 'labels': labels}
 
class SimpleLLM(nn.Module):
    """Simple transformer-like model for testing"""
    def __init__(self, vocab_size=50000, hidden_size=768, num_layers=12):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=hidden_size,
                nhead=12,
                dim_feedforward=hidden_size * 4,
                batch_first=True
            ),
            num_layers=num_layers
        )
        self.output = nn.Linear(hidden_size, vocab_size)
    def forward(self, input_ids):
        x = self.embedding(input_ids)
        x = self.transformer(x)
        return self.output(x)
 
def train_single_gpu():
    """Train on single GPU"""
    print("=" * 60)
    print("GPU Test - Single GPU Training")
    print("=" * 60)
    # Check GPU
    if not torch.cuda.is_available():
        print("❌ ERROR: No GPU available!")
        return
    device = torch.device("cuda:0")
    print(f"✓ Using GPU: {torch.cuda.get_device_name(0)}")
    print(f"✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print()
    # Create dataset and dataloader
    print("Creating dataset...")
    dataset = SimpleTextDataset(num_samples=1000, seq_length=128)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True, num_workers=4)
    # Create model
    print("Creating model...")
    model = SimpleLLM(vocab_size=50000, hidden_size=768, num_layers=12)
    model = model.to(device)
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"✓ Model parameters: {total_params:,}")
    print()
    # Optimizer and loss
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    criterion = nn.CrossEntropyLoss()
    # Training loop
    num_epochs = 3
    print(f"Starting training for {num_epochs} epochs...")
    print("-" * 60)
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        start_time = time.time()
        for batch_idx, batch in enumerate(dataloader):
            input_ids = batch['input_ids'].to(device)
            labels = batch['labels'].to(device)
            # Forward pass
            optimizer.zero_grad()
            outputs = model(input_ids)
            # Calculate loss
            loss = criterion(outputs.view(-1, outputs.size(-1)), labels.view(-1))
            # Backward pass
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            # Print progress
            if batch_idx % 10 == 0:
                gpu_mem = torch.cuda.memory_allocated(0) / 1e9
                print(f"Epoch {epoch+1}/{num_epochs} | "
                      f"Batch {batch_idx}/{len(dataloader)} | "
                      f"Loss: {loss.item():.4f} | "
                      f"GPU Mem: {gpu_mem:.2f} GB")
        epoch_time = time.time() - start_time
        avg_loss = total_loss / len(dataloader)
        print(f"\n✓ Epoch {epoch+1} completed in {epoch_time:.2f}s")
        print(f"  Average Loss: {avg_loss:.4f}")
        print(f"  GPU Memory: {torch.cuda.max_memory_allocated(0) / 1e9:.2f} GB")
        print("-" * 60)
        torch.cuda.reset_peak_memory_stats()
    print("\n✓ Training completed successfully!")
    print("=" * 60)
 
if __name__ == "__main__":
    train_single_gpu()
