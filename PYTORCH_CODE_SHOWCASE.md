# PyTorch forecast code showcase

The Streamlit dashboard displays a readable excerpt of the actual forecasting implementation. This file preserves the same core logic in plain text for inspection.

## Defence model

```python
class DefenceForecastNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(2, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )

    def forward(self, x):
        return self.network(x)
```

## Training setup

```python
torch.manual_seed(42)

model = DefenceForecastNet()
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(1000):
    optimizer.zero_grad()
    prediction = model(X_train_tensor)
    loss = criterion(prediction, y_train_tensor)
    loss.backward()
    optimizer.step()
```

## One-step inference

```python
with torch.no_grad():
    next_input = torch.tensor([[21083.0, 23622.0]])
    forecast = model(next_input).item()
```

The resulting FY2025-26 experimental defence-export forecast is approximately ₹27,108 crore.

## Important limitation

The model is a small exploratory neural network trained on a very short annual series. The project therefore does not present recursive 2030/2035 values as reliable forecasts.
