# Run Command: python Test_scripts/get_screen_resolution.py
from screeninfo import get_monitors

def get_screen_resolution():
    monitor = get_monitors()[0]
    return monitor.width, monitor.height

def test_get_screen_resolution():
    width, height = get_screen_resolution()
    
    # Expected values (replace with actual expected values for your setup)
    expected_width = 1920
    expected_height = 1080
    
    assert width == expected_width, f"Expected width to be {expected_width}, but got {width}"
    assert height == expected_height, f"Expected height to be {expected_height}, but got {height}"
    
    print("test_get_screen_resolution passed.")

if __name__ == "__main__":
    test_get_screen_resolution()