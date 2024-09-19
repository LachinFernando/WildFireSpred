import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
import time
import requests
import json


IMAGE_ADDRESS = "https://www.growbyginkgo.com/wp-content/uploads/2020/08/14503287131_1e74fa7acf_o-1-scaled.jpg"
# Define the colors based on the values:
COLOR_MAP = {
    0: [0, 0, 0], # white
    1: [0.5, 0.5, 0.5], # Grey
    2: [1, 0, 0] # Red
}
LABEL_MAP = {
    1: "No Spread",
    2: "Risk of Spread"
}

### functions
def get_prediction(data):
    url = 'https://askai.aiclub.world/35045a31-6aba-41e7-a623-a22bc7f1218c'
    r = requests.post(url, data=json.dumps(data))
    response = getattr(r,'_content').decode("utf-8")
    response = json.loads(response)
    sub_response = json.loads(response["body"])
    final_response = int(float(sub_response["predicted_label"])) + 1
    return final_response


def visualize_grid(squares, response_grid):

    # Convert the API response to a 5x5 grid of color codes
    color_grid = np.array(response_grid).reshape(squares, squares)
    # Create a 5x5 RGB grid initialized to black
    rgb_grid = np.zeros((squares, squares, 3))

    # Map the colors to the RGB grid
    for i in range(squares):
        for j in range(squares):
            rgb_grid[i, j] = COLOR_MAP[color_grid[i, j]]

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Display the grid
    ax.imshow(rgb_grid, interpolation='nearest')

    # Optionally add grid lines and labels
    ax.set_xticks(np.arange(5))
    ax.set_yticks(np.arange(5))
    ax.grid(which='both', color='black', linestyle='-', linewidth=2)

    # Optionally remove the tick marks
    ax.set_xticks([])
    ax.set_yticks([])

    return fig

# main web application
st.title("Wildfire Spread Prediction")

# set the image
st.image(IMAGE_ADDRESS, caption = "Wildfire Spreading")

# select the number of squares
num_square = st.slider("Select the number of squares you need", min_value = 5, max_value = 10, value = 5)

if num_square:
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file:
        # read the dataframe as pandas dataframe
        df = pd.read_csv(uploaded_file)
        # validation
        if df.shape[0] != num_square**2:
            st.error("Number of Tiles Mismatching in CSV: You need {} Records.".format(num_square**2), icon = "❌")
            st.stop()
        sample_list = [0 for pixel in range(num_square**2)]
        # generate the graphs
        with st.spinner('Getting Wildfire Statuses......'):
            for index, row in df.iterrows():
                try:
                    choice_ = get_prediction(row.to_dict())
                except Exception as error:
                    message = "Error Getting the Response: {}".format(str(error))
                    st.error("Error Getting the Predictions. Please Try Again!!", icon = "❌")
                    st.stop()
                    break
                sample_list[index] = choice_
                py_fig = visualize_grid(num_square, sample_list)
                with st.sidebar:
                    label_status = LABEL_MAP[choice_]
                    st.markdown("Wildfire Spread Status of Square {}: :red[{}]".format(index +1, label_status))
                    st.pyplot(py_fig)

                if index == (num_square**2 - 1):
                    st.header("Wildfire Grid Status")
                    st.subheader("Final Grid")
                    st.pyplot(py_fig)
                time.sleep(5)



        