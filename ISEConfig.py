import tushare as ts
import json


class ISEconfig:
    """get basic configuration from 
    financial interface"""
    _interfaces={'tushare' : ts}
    
    def __init__(self):
        self._interface=None
        self._tstoken=None
    
    def init_tushare(self):
        fh=open('tstoken.json',encoding='utf-8')
        contents=json.load(fh)
        self._tstoken=contents['token']
        ts.set_token(self._tstoken)
        
    def reset_interface(self, keyword):
        if  keyword is 'tushare':
            self._interfaces[keyword].pro_api(self._tstoken)
    
    def get_interface(self, keyword):
        return self._interfaces[keyword]
        
    
    def _add_interface(self, *args):
        pass
        
    
    
    
    
    
    
    
    