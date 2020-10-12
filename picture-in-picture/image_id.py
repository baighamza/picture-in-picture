import os
import skimage
from PIL import Image
from PIL.ExifTags import TAGS
import math

from skimage import io

from config import config
from connect import connect
from create_tables import create_tables
from insert_info import insert_info


import multiprocessing
import multiprocessing.managers



import logging
logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)


class MyListManager(multiprocessing.managers.BaseManager):
    pass







image_list = []
image_dir = os.getcwd() + "/images"

def get_list():
    return image_list



def get_image_info(image_tmp):
    
    images = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]


    for image in images:
        dict_image = {}
        dict_image["Image_Name"] = image
        img = image_dir + "/" + image
        open_image = Image.open(img)
        exifdata = open_image.getexif()
        for tag_id in exifdata:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            # decode bytes 
            if isinstance(data, bytes):
                data = data.decode()
            
            if tag == "ApertureValue":
                stop_value = float(f"{data}")
                f_stop = math.ceil(math.sqrt(pow(2,stop_value)))
                dict_image["Aperture"] = f_stop
            if tag == "ISOSpeedRatings":
                dict_image["ISO"] = f"{data}"
            if tag == "DateTime":
                dict_image["Date_Time"] = f"{data}"
            if tag == "ShutterSpeedValue":
                shutter_val = float(f"{data}")
                prod = math.ceil(pow(2,shutter_val))
                rounded = round(prod/10)*10
                dict_image["Shutter_Speed"] = rounded

                # info = shutter_val.split(", ")
                # num = info[0].replace("(","")
                # den = info[1].replace("(","")
                # div = float(num)/float(den)
                # prod = math.ceil(pow(2,div))
                # dict_image["Shutter_Speed"] = prod

        image_tmp.append(dict_image)
            #print(f"{tag:25}: {data}")

    #print(image_list)




# def classify_image():

#     for index in range(len(image_list)):
#             image = image_dir + "/" + image_list[index]["Image_Name"]
#             camera = io.imread(image)
#             print(camera)

def setup_IPC():
    MyListManager.register("image_list", get_list, exposed=['__getitem__', '__setitem__', '__str__', 'append', 'count', 'extend', 'index', 'insert', 'pop', 'remove', 'reverse', 'sort'])
    manager = MyListManager(address=('/tmp/mypipe'), authkey=b'')
    manager.start()

    image_list_tmp = manager.image_list()
    print("image_list (master):", image_list, "image_list_tmp:", image_list_tmp)

    print("image_list initial:", image_list_tmp.__str__())

    get_image_info(image_list_tmp)

    insert_info(image_list_tmp)
    manager.shutdown()




def main():
    
    setup_IPC()

    config()
    connect()
    create_tables()
  #  classify_image()







if __name__ == "__main__":
    main()