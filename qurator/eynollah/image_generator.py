#!/home/ubuntu/layout_detection/venv/bin/python
import csv
import tempfile
import sys
from PIL import Image, ImageDraw, ImageFont
import os
import argparse
from pdf2image import convert_from_path

BATCH_PROCESSOR_PATH = "/home/ubuntu/layout_detection/eynollah_batch_processing"

IMAGE_OUTPUT_DIR = BATCH_PROCESSOR_PATH + "/images"
IMAGE_COMPLETED_DIR = BATCH_PROCESSOR_PATH + "/completed_images"

def generate_images(pdf_file_path, folder, year):
    filename_ext = os.path.basename(pdf_file_path)
    filename = filename_ext.split(".")[0]
    print("PDF " + pdf_file_path)

    output_dir = IMAGE_OUTPUT_DIR + "/" + "000___" + folder + "___" + year + "___" + filename
    completed_dir = IMAGE_COMPLETED_DIR + "/" + "000___" + folder + "___" + year + "___" + filename
    if not os.path.isdir(output_dir) and not os.path.isdir(completed_dir):
        os.mkdir(output_dir)
    else:
        print("dir already exists, skipping")
        return
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(pdf_file_path, output_folder=path)

        for index, image in enumerate(images):
            image_save_path = output_dir + "/page" + str(index) + ".jpg"
            print("image saved " + image_save_path)
            image.save(image_save_path)
        with open(os.path.join(output_dir, "final.txt"), "w+") as f:
            f.write("\n")

def generate_images_of_pdf(tracking_code, uploaded_file, date, doc_type):
    try:
        _folder = doc_type.lower().replace(" ", "_")
        _year = date[0:4]
        file_path =  "/mnt/storm/spirit_intl_files/original_uploaded_files/" + _folder + "/" +_year + "/" + tracking_code + "__" + uploaded_file
        generate_images(file_path, _folder, _year)
        return True
    except Exception as e:
        print(e)
        return False

