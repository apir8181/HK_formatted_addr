# -*- coding: utf-8 -*-
import urllib2
import xml.etree.ElementTree as ET
from helper import *

ak = "4ab941552488bab30a0eef54a2ac4cd6"
class GeoCoding:
    def __init__(self, addr):
        url = "http://api.map.baidu.com/geocoder/v2/?" +\
            "output=xml&ak=%s&address=%s" % (ak, addr)
        xml = urllib2.urlopen(url.encode('utf-8')).read()
        self.root = ET.fromstring(xml)
    
    def GetStats(self):
        return int(self.root.find("status").text)

    def GetConfidence(self):
        result = self.root.find("result")
        return int(result.find("confidence").text)

    def GetLatlng(self):
        result = self.root.find("result")
        location = result.find("location")
        lat = float(location.find("lat").text)
        lng = float(location.find("lng").text)
        return (lat, lng)

    def GetPrecise(self):
        result = self.root.find("result")
        return int(result.find("precise").text)

class InvGeoCoding:
    def __init__(self, lat, lng):
        url = "http://api.map.baidu.com/geocoder/v2/?" +\
            "output=xml&ak=%s&location=%f,%f" % (ak, lat, lng)
        xml = urllib2.urlopen(url.encode('utf-8')).read()
        self.root = ET.fromstring(xml)
    
    def GetStats(self):
        return int(self.root.find("status").text)

    def GetFormattedAddr(self):
        result = self.root.find("result")
        return result.find("formatted_address").text

    def GetProvince(self):
        result = self.root.find("result")
        component = result.find("addressComponent")
        return component.find("province").text

    def GetCity(self):
        result = self.root.find("result")
        component = result.find("addressComponent")
        return component.find("city").text

    def GetSmallDistrict(self):
        result = self.root.find("result")
        component = result.find("addressComponent")
        return component.find("district").text

    def GetBigDistrict(self):
        smallDis = self.GetSmallDistrict().encode('utf-8')
        bigDis = hk_wiki.Maps.get(smallDis)
        return u'无记录' if bigDis == None else bigDis

if __name__ == "__main__":
    while True:
        addr = remove_spaces_utf8(raw_input().decode('utf-8'))
        addr = traditional_to_simple(addr)
        geoCoding = GeoCoding(addr)
        lat, lng = geoCoding.GetLatlng()
        invGeoCoding = InvGeoCoding(lat, lng)
