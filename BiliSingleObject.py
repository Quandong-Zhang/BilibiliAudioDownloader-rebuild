from abc import ABC, abstractmethod

class BiliSingleObject(ABC):
    #单个P的对象
    @classmethod
    def getNew(cls)->"BiliSingleObject":
        return cls()
    
    def setPlainJsonInfo(self, json_info: str):
        self._plainJsonInfo = json_info
        return self
    
    def setAuthor(self,author):
        self._author = author
        return self
    
    def setVideoLinkURL(self, url: str):
        #like https://www.bilibili.com/video/BV1BC4y1j7CL   
        self._videoLinkURL = url
        return self
    
    def setCoverURL(self, cover_url: str):
        self._coverURL = cover_url
        return self
    
    def setDownloadURL(self, download_url: str):
        self._downloadURL = download_url
        return self
    
    # def setDownloadURLs(self, download_urls: list[str]):
    #     self.downloadURLs = download_urls
    #     return self
