import cv2
from skimage.metrics import structural_similarity
import streamlit as st
from PIL import Image
import os
import time

BASE_DIR = 'data'
UPLOADED_IMAGE = None

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def save_image(uploaded_file):
    image = Image.open(uploaded_file)
    image.save(BASE_DIR + uploaded_file.name)
    global UPLOADED_IMAGE
    UPLOADED_IMAGE = uploaded_file.name
    return  BASE_DIR + uploaded_file.name


def search_folders(search_dir):
    images_list = []
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith(('.png', 'jpg', 'jpeg')) and file != UPLOADED_IMAGE:
                images_list.append(root + '\\' + file)
    return images_list


def similar_images(base_img, img, size=(1080, 720)):
    base_img = cv2.imread(base_img)
    base_img = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
    base_img = cv2.resize(base_img, size)

    img = cv2.imread(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, size)
    
    score, diff = structural_similarity(base_img, img, full=True)
    return score


st.title('Similar Image')
st.markdown('---')

uploaded_image = st.file_uploader(
    'You can upload .png, .jpg, .jpeg',
    type=['png, jpg, jpeg'],
    help="Upload an image for search",
    accept_multiple_files=False)

if uploaded_image:
    saved_path = save_image(uploaded_image)

    user_input = st.chat_input("Type folder name to be searched...")

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        
        with st.spinner("Analyzing..."):
            relevant_images = search_folders(user_input)
            images_dict = {}
            for i in range(len(relevant_images)):
                images_dict[relevant_images[i]] = similar_images(saved_path, relevant_images[i])
            images_dict = dict(sorted(images_dict.items(), key=lambda item: item[1], reverse=True))

        with st.chat_message("assistant"):  
            if images_dict:
                for k, v in images_dict.items():
                    st.write(f'Image Path: {k} | Score: {v*100:.2f}%')
                    st.image(Image.open(k), width=200)
            else:
                st.error('Folder not found!')