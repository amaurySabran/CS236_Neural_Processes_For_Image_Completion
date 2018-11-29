import torch.nn as nn
import torch.nn.functional as F
import torch
import numpy as np


class ContextEncoder(nn.Module):
    def __init__(self):
        super(ContextEncoder, self).__init__()
        self.layer1 = nn.Linear(3, 200)
        self.layer2 = nn.Linear(200, 200)
        self.layer3 = nn.Linear(200, 128)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)


class MeanAgregator(nn.Module):
    def __init__(self):
        super(MeanAgregator, self).__init__()

    def forward(self, x, mask=None, agg_dim=1):
        # import pdb;
        # pdb.set_trace()
        if mask is None:
            return x.mean(dim=agg_dim)
        else:
            return (x * mask).sum(dim=agg_dim) / (1e-8 + mask.sum(dim=agg_dim))


class AttentionAggregator(nn.Module):
    def __init__(self, input_dim):
        super(AttentionAggregator, self).__init__()
        # TODO add deeper query and key
        self.query = nn.Linear(input_dim, input_dim)
        self.input_dim = input_dim

    def forward(self, x, mask=None, agg_dim=1):
        import pdb;
        pdb.set_trace()

        keys = x
        queries = self.query(x)

        dot_products = (keys * queries).sum(dim=-1) / np.sqrt(self.input_dim)
        if mask is not None:
            dot_products = dot_products - 1000 * mask

        attention_weights = F.softmax(dot_products, dim=-1).unsqueeze(-1).expand(-1, -1, self.input_dim)

        return (attention_weights * x).sum(-2)


class ContextToLatentDistribution(nn.Module):
    # TODO use MLP instead of linear layers
    def __init__(self):
        super(ContextToLatentDistribution, self).__init__()
        self.mu_layer = nn.Linear(128, 128)
        self.logvar_layer = nn.Linear(128, 128)

    def forward(self, x):
        return self.mu_layer(x), self.logvar_layer(x)


class Decoder(nn.Module):
    def __init__(self):
        super(Decoder, self).__init__()
        self.layer1 = nn.Linear(128 + 2, 200)
        self.layer2 = nn.Linear(200, 200)
        self.layer3 = nn.Linear(200, 200)
        self.layer4 = nn.Linear(200, 200)
        self.layer5 = nn.Linear(200, 1)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        x = F.relu(self.layer4(x))
        x = self.layer5(x)
        return F.sigmoid(x)  # for mnist
