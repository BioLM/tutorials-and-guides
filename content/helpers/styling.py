import seaborn as sns
import os
from matplotlib import rcParams
from matplotlib.font_manager import fontManager, FontProperties

def apply_plot_styling(font_filename="Geist-Regular.ttf"):
    """
    Applies custom font and Seaborn theme styling for consistent plot visuals.
    
    Parameters:
        font_filename (str): Name of the .ttf font file located in the same directory as this script.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, font_filename)

    fontManager.addfont(font_path)
    prop = FontProperties(fname=font_path)
    font_name = prop.get_name()

    sns.set_theme(
        font=font_name,
        style="white",
        context="notebook",
        palette="pastel"
    )

    rcParams['font.family'] = font_name