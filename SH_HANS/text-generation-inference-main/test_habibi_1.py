#a.is_available() else "cpu") print(f"Device: {device}") if torch.cuda.is_available():     print(f"GPU: {torch.cuda.get_device_name(0)}") print() # Fake dataset X = torch.randn(1000, 100) y = torch.randn(1000, 10) dataset = TensorDataset(X, y) loader = DataLoader(dataset, batch_size=32, shuffle=True) # Simple model model = nn.Sequential(     nn.Linear(100, 256),     nn.ReLU(),     nn.Linear(256, 10) ).to(device) optimizer = torch.optim.Adam(model.parameters(), lr=0.001) criterion = nn.MSELoss() # Train print("Training...") for epoch in range(3):     total_loss = 0     for batch_x, batch_y in loader:         batch_x, batch_y = batch_x.to(device), batch_y.to(device)         optimizer.zero_grad()         pred = model(batch_x)         loss = criterion(pred, batch_y)         loss.backward()         optimizer.step()         total_loss += loss.item()     print(f"Epoch {epoch+1}: Loss={total_loss/len(loader):.4f}") print("✓ Training complete!")
 #!/usr/bin/env python3

"""simple_train.py - Simple training test"""
 
import torch

import torch.nn as nn

from torch.utils.data import TensorDataset, DataLoader
 
print("=" * 50)

print("GPU Training Test")

print("=" * 50)
 
# GPU info

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"Device: {device}")

if torch.cuda.is_available():

    print(f"GPU: {torch.cuda.get_device_name(0)}")

print()
 
# Fake dataset

X = torch.randn(1000, 100)

y = torch.randn(1000, 10)

dataset = TensorDataset(X, y)

loader = DataLoader(dataset, batch_size=32, shuffle=True)
 
# Simple model

model = nn.Sequential(

    nn.Linear(100, 256),

    nn.ReLU(),

    nn.Linear(256, 10)

).to(device)
 
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

criterion = nn.MSELoss()
 
# Train

print("Training...")

for epoch in range(3):

    total_loss = 0

    for batch_x, batch_y in loader:

        batch_x, batch_y = batch_x.to(device), batch_y.to(device)

        optimizer.zero_grad()

        pred = model(batch_x)

        loss = criterion(pred, batch_y)

        loss.backward()

        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}: Loss={total_loss/len(loader):.4f}")
 
print("✓ Training complete!")
 
