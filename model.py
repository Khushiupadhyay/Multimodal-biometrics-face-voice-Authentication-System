import torch
import torch.nn as nn

class ECAPA_TDNN(nn.Module):
    def __init__(self, input_size):
        super(ECAPA_TDNN, self).__init__()
        self.layer1 = nn.Conv1d(input_size, 512, kernel_size=5, stride=1, padding=2)
        self.layer2 = nn.Conv1d(512, 512, kernel_size=3, stride=1, padding=1)
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(512, 256)
        
        # Add ReLU activations for better feature extraction
        self.relu = nn.ReLU()

    def forward(self, x):
        # Handle different input dimensions
        if x.dim() == 3:  # batch x channels x time
            pass
        elif x.dim() == 2:  # channels x time
            x = x.unsqueeze(0)
        
        # Apply first convolutional layer
        x = self.layer1(x)
        x = self.relu(x)
        
        # Apply second convolutional layer
        x = self.layer2(x)
        x = self.relu(x)
        
        # Global pooling
        x = self.global_pool(x).squeeze(-1)
        
        # Final linear layer
        return self.fc(x)