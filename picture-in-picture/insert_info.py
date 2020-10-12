#!/usr/bin/python
import time

import multiprocessing
import multiprocessing.managers

import logging

import psycopg2
from config import config


logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)


class MyListManager(multiprocessing.managers.BaseManager):
    pass

MyListManager.register("image_list")

def insert_info(list):
   ## print ("arr = %s" % (test_var))

    #print(test_var.get('Image_Name'))
    """ insert a new vendor into the vendors table """
    sql = """INSERT INTO images(image_name, shutter_speed, aperture, iso, date_time)
             VALUES(%s, %s, %s, %s, %s);"""


    conn = None
    vendor_id = None

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    cur = conn.cursor()
    for image in list:
        image_name = image["Image_Name"]
        shutter_speed = image["Shutter_Speed"]
        aperture = image["Aperture"]
        iso = image["ISO"]
        date_time = image["Date_Time"]

        

        try:
             cur.execute(sql, (image_name,shutter_speed,aperture,iso,date_time))
             conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    
    cur.close()






def main():
  manager = MyListManager(address=('/tmp/mypipe'), authkey=b'')
  manager.connect()
  image_list = manager.image_list()

  insert_info(image_list)

  




if __name__ == '__main__':
    main()