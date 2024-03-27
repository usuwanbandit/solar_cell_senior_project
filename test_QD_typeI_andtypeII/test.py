import matplotlib.pyplot as plt
import numpy as np

def get_color(number_of_color):
    cmap = plt.get_cmap('RdYlBu')
    colors = [cmap(i/number_of_color) for i in range(number_of_color)]
    return colors

# Example usage:
colors = get_color(5)
print(colors)  # Output: list of colors transitioning from red to blue
