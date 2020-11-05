from hub.api.dataset import Dataset
import numpy as np


def test_logs():
    logs = Dataset(dtype={"train_acc": float, "train_loss": float, 
                          "val_acc": float, "val_loss": float},
                   shape=(1,), url='./models/logs', mode='w')
    metrics_1 = {'val_loss': 1.21, 
                 'val_acc': 0.5,
                 'train_loss': 2.4,
                 'train_acc': 0.75}
    for key, value in metrics_1.items():
        logs[key][0] = value
    assert np.isclose(logs['val_loss'][0].numpy(), 1.21)
    assert np.isclose(logs['train_loss'][0].numpy(), 2.4)
