import xml.dom.minidom
from xml.dom.minidom import Node
import urllib.request
import threading


YBMInstance = None

def get_instance():
    global YBMInstance
    if  YBMInstance:
        return YBMInstance
    else:
        YBMInstance = YellowBoxManager()
        return YBMInstance
class YellowBoxManager(object):
    def __init__(self):
        print("YellowBoxManager created")
        self.boxes_loaded = []
    def create_box(self, down_xml):
        new_box = self.YellowBox(down_xml)
        self.boxes_loaded.append(new_box)
        return new_box
    class YellowBox(object):
        class ParallelExecute(threading.Thread):
            def __init__(self, function=None):
                threading.Thread.__init__(self)
                self.f = function
            def run(self):
                self.f()
        def __init__(self, download_data_xml):
            self.downDataFile = download_data_xml
            self.downloadData = {}
            self.downloadQueue = []
            self.doneList = []
            self.downloadStatuses = []
        def load_download_data(self):
            try:
                self.down_data = xml.dom.minidom.parse(self.downDataFile)
                self.down_config = {"fail": "", "order": ""}
                self.down_config["order"] = self.down_data.getElementsByTagName("download-config")[0].getAttribute("order")
                self.down_config["fail"] = self.down_data.getElementsByTagName("download-config")[0].getAttribute("fail")
                self.down_queue = []
                downTags = self.down_data.getElementsByTagName("download")
                for itr in downTags:
                    if self.down_config["order"] == "as_listed":
                        tempDict = {"url": itr.getAttribute("url"), "filename": itr.getAttribute("filename")}
                    else:
                        tempDict = {"url": itr.getAttribute("url"), "filename": itr.getAttribute("filename"),\
                                     "list_info": itr.getAttribute("list_info")}
                    self.down_queue.append(tempDict)
                self.downxml_load = True
                return True
            except IOError:
                print("Error ocurred when reading download xml file")
                return False

        def start_download(self, index, callback=None):
            if index >= len(self.down_queue):
                if callback:
                    callback() 
                return
            print("Downloading " + self.down_queue[index]["filename"] + " from " + self.down_queue[index]["url"])
            try:
                urllib.request.urlretrieve(self.down_queue[index]["url"], self.down_queue[index]["filename"])
            except Exception as ex:
                print(ex)              
                print("Error ocurred while downloading " + self.down_queue[index]["filename"])
                if self.down_config["fail"] == "proceed":
                    self.start_download(index + 1, callback=callback)
                    return
                elif self.down_config["fail"] == "abort":
                    print("Aborting unpack")
                    return
            print("Ended download")
            self.start_download(index + 1, callback=callback)
            
        def start_download_queue(self):
            def onDownloadsEnd():
                print("Ended downloading files")
            self.ParallelExecute(function=(lambda: self.start_download(0, callback=onDownloadsEnd))).start()
        def rearrange_queue(self):
            print("Rearranging download queue")
            new_queue = []
            if self.down_config["order"] == "as_listed":
                return
            elif self.down_config["order"] == "num_listed":
                for it1 in range(1, len(self.down_queue) + 1):
                    for it2 in self.down_queue:
                        if it2["list_info"] == str(it1):
                            new_queue.append(it2)
                self.down_queue = new_queue
                            
        def unpack(self):
            if self.load_download_data():
                self.rearrange_queue()
                if(len(self.down_queue)):
                    self.start_download_queue()
        
        