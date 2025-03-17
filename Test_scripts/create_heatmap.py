# Run Command: python Test_scripts/create_heatmap.py
import numpy as np
import matplotlib.pyplot as plt

def create_heatmap(ad_size):
    return np.zeros((ad_size[0], ad_size[1]))

def test_create_heatmap():
    ad_size = (1080, 1920)
    heatmap = create_heatmap(ad_size)
    
    # Expected values
    expected_shape = (1080, 1920)
    expected_value = 0
    
    assert heatmap.shape == expected_shape, f"Expected heatmap shape to be {expected_shape}, but got {heatmap.shape}"
    assert np.all(heatmap == expected_value), f"Expected all values in heatmap to be {expected_value}, but got different values"
    
    print("test_create_heatmap passed.")
    plt.imshow(heatmap, cmap="hot", interpolation="nearest")
    plt.show()

if __name__ == "__main__":
    test_create_heatmap()