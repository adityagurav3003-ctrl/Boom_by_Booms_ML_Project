import torch
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# -----------------------------
# Defence model
# -----------------------------
class DefenceForecastNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.network = torch.nn.Sequential(
            torch.nn.Linear(2, 8),
            torch.nn.ReLU(),
            torch.nn.Linear(8, 1),
        )

    def forward(self, x):
        return self.network(x)

# -----------------------------
# Space model: NSIL total revenue
# -----------------------------

def main():
    # Defence: forecast FY2025-26 from the two latest historical observations.
    defence = DefenceForecastNet()
    defence.load_state_dict(
        torch.load(ROOT / "models" / "defence_exports_model.pth",
                   map_location="cpu", weights_only=True)
    )
    defence.eval()

    with torch.no_grad():
        defence_input = torch.tensor([[21083.0, 23622.0]], dtype=torch.float32)
        defence_forecast = defence(defence_input).item()

    # Space: NSIL total revenue, annual FY2019-20 to FY2024-25.
    # The model is a simple PyTorch linear trend model fitted to all six observations.
    space = torch.nn.Linear(1, 1)
    space.load_state_dict(
        torch.load(ROOT / "models" / "space_nsil_revenue_model.pth",
                   map_location="cpu", weights_only=True)
    )
    space.eval()

    x_mean = 2.5
    x_std = (35.0 / 12.0) ** 0.5
    y_mean = 182195.6083333333
    y_std = 107603.27170338602

    with torch.no_grad():
        next_time = torch.tensor([[(6.0 - x_mean) / x_std]], dtype=torch.float32)
        space_forecast_lakh = space(next_time).item() * y_std + y_mean

    print("=" * 62)
    print("BOOM BY BOOMS — COMBINED ML INFERENCE")
    print("=" * 62)
    print()
    print("DEFENCE")
    print("Target: Total Indian defence exports")
    print("Inputs: FY2023-24 ₹21,083 crore; FY2024-25 ₹23,622 crore")
    print(f"Experimental FY2025-26 forecast: ₹{defence_forecast:,.2f} crore")
    print()
    print("SPACE")
    print("Target: NSIL total revenue (company-level indicator)")
    print("Model: PyTorch linear trend")
    print(f"Experimental FY2025-26 forecast: ₹{space_forecast_lakh:,.2f} lakh")
    print(f"Equivalent: ₹{space_forecast_lakh/100:,.2f} crore")
    print()
    print("IMPORTANT")
    print("Both forecasts are exploratory model outputs, not official projections.")
    print("The NSIL forecast is NOT a forecast of total Indian space-sector revenue.")
    print("=" * 62)


if __name__ == "__main__":
    main()
