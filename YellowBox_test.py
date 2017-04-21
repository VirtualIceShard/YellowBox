import yellowbox
import urllib.request
import threading
ybm = yellowbox.get_instance()
box1 = ybm.create_box("download_data.xml")
box1.unpack()


