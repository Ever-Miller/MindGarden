from models import *
import torch 
from torch.utils.data import Dataset
import torch.nn as nn
import torch.optim as optim
from pathlib import Path

class FlashcardModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(in_features=8, out_features=32),
            nn.Sigmoid(),
            nn.Linear(in_features=32, out_features=32),
            nn.Sigmoid(),
            nn.Linear(in_features=32, out_features=1)
        )

    def forward(self, x):
        return self.layers(x)

def mape_fn(y_true, y_pred):
    percentage_error = torch.abs((y_true - y_pred) / y_true) * 100
    mape = percentage_error.mean().item()
    return mape

def rmse_fn(y_true, y_pred):
    mse = torch.mean((y_true - y_pred) ** 2)
    rmse = torch.sqrt(mse).item()
    return rmse

def train_loop(model_01, X_train, y_train, X_test, y_test):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    loss_fn = nn.MSELoss()
    torch.manual_seed(57)

    epochs = 1000

    X_train, y_train = X_train.to(device), y_train.to(device)
    X_test, y_test = X_test.to(device), y_test.to(device)

    optimizer = torch.optim.Adam(params=model_01.parameters(),
                                lr=0.01)


    # Build training and evaluation loop
    for epoch in range(epochs):
        ### Training
        model_01.train()

        y_pred = model_01(X_train).squeeze()

        # 2. Calculate loss/accuracy
        loss = loss_fn(y_pred, y_train)

        train_mape = mape_fn(y_train, y_pred)
        train_rmse = rmse_fn(y_train, y_pred)

        # 3. Optimizer zero grad
        optimizer.zero_grad()

        # 4. Loss backwards
        loss.backward()

        # 5. Optimizer step
        optimizer.step()

        ### Testing
        model_01.eval()
        with torch.inference_mode():
            # 1. Forward pass
            test_pred = model_01(X_test).squeeze()
            # 2. Caculate loss/accuracy
            test_loss = loss_fn(test_pred, y_test)

            test_mape = mape_fn(y_test, test_pred)
            test_rmse = rmse_fn(y_test, test_pred)

        # Print out what's happening every 10 epochs
        if epoch % 100 == 0:
            print(f"Epoch: {epoch:03d} | Loss: {loss:.5f} | Train MAPE: {train_mape:.2f}% | Train RMSE: {train_rmse:.5f} | Test MAPE: {test_mape:.2f}% | Test RMSE: {test_rmse:.5f}")

def load_model_01():

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # To load in a saved state_dict we have to instantiate a new instance of our model class
    base_model = FlashcardModel()
    MODEL_PATH = Path("Flashcard_models")

    # 2. Create model save path
    MODEL_NAME = "SmartCards_model_01.pth"
    MODEL_SAVE_PATH = MODEL_PATH / MODEL_NAME

    base_model.load_state_dict(torch.load(f=MODEL_SAVE_PATH, 
                                        weights_only=True))
    
    return base_model

def fine_tune_model(model, user_data, optimizer, epochs=5):
    model.train()
    for epoch in range(epochs):
        for batch in user_data:  # Assuming `user_data` is a DataLoader with user-specific data
            features, labels = batch['features'], batch['label']
            features, labels = features.to(device), labels.to(device)

            # Forward pass
            predictions = model(features).squeeze()
            loss = loss_fn(predictions, labels)

            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Optional: Print fine-tuning progress
        if epoch % 1 == 0:
            print(f"Fine-tuning epoch {epoch + 1}/{epochs} | Loss: {loss.item():.4f}")



def capture_review_data(card, difficulty_score, response_time, success):
    # Update card attributes based on user review
    card._review_count += 1
    card._average_quality = ((card._average_quality * (card._review_count - 1)) + (5 - difficulty_score)) / card._review_count
    card._last_response_time = response_time
    card._success_rate = ((card._success_rate * (card._review_count - 1)) + success) / card._review_count
    card._time_since_last_review = torch.tensor([0.0])  # Reset; update as needed in real scenarios

    # Convert relevant features and label to tensors
    features = torch.tensor([
        card._time_since_last_review.item(),
        card._interval,
        card._review_count,
        card._average_quality,
        card._ease,
        card._last_response_time,
        card._success_rate,
        card._char_count
    ], dtype=torch.float32)

    label = torch.tensor(card._interval, dtype=torch.float32)

    return {'features': features, 'label': label}


