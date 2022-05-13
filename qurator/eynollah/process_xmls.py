import json
from os import listdir
from os.path import isfile, join
import argparse
import os
import sys
from collections import defaultdict
import xml.etree.ElementTree as ET

FINAL_OUTPUT_DIR = os.path.dirname(os.getcwd()) + "/output/data/international_data/original_uploaded_files/ar"


def get_region_coords(regions, root, namespaces):

    region_coords = list()
    region_coords_list = list()
    region_names_list = list()

    # loop over regions in order
    for region in regions:
        region_ele = root.find(f".//pc:TextRegion[@id='{region}']", namespaces)
        region_type = region_ele.attrib["type"]

        if region_type == "paragraph" or region_type == "header":
            # text_line_eles = region_ele.findall(".//pc:TextLine", namespaces)
            coords_ele = region_ele.find("pc:Coords", namespaces)

            coords_points = coords_ele.attrib["points"]

            # text_line_coords = list()
            x_list = list()
            y_list = list()

            coords_points_x_y = coords_points.split(" ")

            # loop over each text line in paragraph
            for x_y_coord in coords_points_x_y:

                x_y = x_y_coord.split(",")
                x = x_y[0]
                y = x_y[1]

                x_list.append(int(x))
                y_list.append(int(y))

            min_x = min(x_list)
            max_x = max(x_list)
            min_y = min(y_list)
            max_y = max(y_list)

            region_coord = [[min_x, min_y], [max_x, min_y], [max_x, max_y], [min_x, max_y]]
            region_coord_tuple = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
            region_names_list.append(region)
            region_coords_list.append(region_coord)
            region_coords.append(region_coord)

    # region_dict = {k[0]: k[1] for k in zip(region_names_list, region_coords)}
    return region_names_list, region_coords_list, region_coords


def parse_xml(xmlfile):

    # create element tree object
    tree = ET.parse(xmlfile)

    namespaces = {"pc": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"}


    root = tree.getroot()

    regions = []

    ordering_list = root.find(".//pc:OrderedGroup", namespaces)
    page_detail = root.find(".//pc:Page", namespaces)

    img_width = page_detail.attrib["imageWidth"]
    img_height = page_detail.attrib["imageHeight"]
    if ordering_list:
        for ele in ordering_list:
            regions.append(ele.attrib["regionRef"])

        region_names_list, region_coords_list, region_coords =  get_region_coords(regions, root, namespaces)
        return img_width, img_height, region_names_list, region_coords_list, region_coords
    else:
        return img_width, img_height, list(), list(), list()


def generate_output(path):
    path_to_xml = path
    if not os.path.exists(path_to_xml):
        print('The xml path specified does not exist')
        sys.exit()
    with open(path_to_xml, "r") as f:
        img_width, img_height, region_names_list,region_coords_list, region_coords = parse_xml(f)
    region_list = list()
    for i, (region_name, region_coord) in enumerate(zip(region_names_list, region_coords_list)):
                region_dict = {"region": region_name, "index": i, "region_coords": region_coord}
                region_list.append(region_dict)
    regions = {
                "width": img_width,
                "height": img_height,
                "regions": region_list
            }
    return regions


def process_xmls(xml_dir, finalout_dir, img_file_year, img_dir_name):
    onlyfiles = [f for f in listdir(xml_dir) if isfile(join(xml_dir, f))]
    onlyfiles.sort()
    output_path_year = os.path.join(finalout_dir, img_file_year)
    if not os.path.exists(output_path_year):
        os.mkdir(output_path_year)
    output_path_year_and_img_dir_name = os.path.join(output_path_year, img_dir_name) + ".txt"
    with open(output_path_year_and_img_dir_name, "w+") as f:
        for index in range(0, len(onlyfiles)):
            xml_file =  "page" + str(index) + ".xml"
            xml_file_path = xml_dir + "/" + xml_file
            if not os.path.exists(xml_file_path):
                print('The image path specified does not exist')
                sys.exit()

            f.write(json.dumps(generate_output(xml_file_path)))
            f.write("\n")
