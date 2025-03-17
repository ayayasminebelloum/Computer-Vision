# Run Command: python Test_scripts/display_heatmap.py
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os

def create_heatmap(ad_size):
    return np.zeros((ad_size[0], ad_size[1]))

def display_heatmap(heatmap, ad_path):
    img = cv2.imread(ad_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    smoothed_heatmap = cv2.GaussianBlur(heatmap, (31, 31), 0)
    plt.figure(figsize=(10, 6))
    plt.imshow(img)
    heatmap_display = plt.imshow(smoothed_heatmap, cmap="jet", alpha=0.5)
    plt.colorbar(heatmap_display, label="Gaze Fixation Intensity")
    plt.title("Gaze Heatmap")
    plt.show()

def test_display_heatmap():
    ad_size = (1080, 1920)
    heatmap = create_heatmap(ad_size)
    ad_path = os.path.join('AdImages', 'PHOTO-2025-03-02-09-10-01.jpg')
    display_heatmap(heatmap, ad_path)
    
    # Check if heatmap is generated
    assert heatmap is not None, "Heatmap should not be None"
    assert heatmap.shape == (1080, 1920), f"Expected heatmap shape to be (1080, 1920), but got {heatmap.shape}"
    
    print("test_display_heatmap passed.")

if __name__ == "__main__":
    test_display_heatmap()