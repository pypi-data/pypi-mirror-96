# -*- coding: utf-8 -*-
'''
Created on 2020-11-9

@author: zhys513(254851907@qq.com)
'''
from opspipe.reg.spliter import RegularExtrator 
from unittest import TestCase 
import unittest

text = '急寻特朗普，男孩，于2018年11月27号11时在陕西省安康市汉滨区走失。丢失发型短发，...如有线索，请迅速与警方联系：系18100065143，132-6156-2938，baizhantang@sina.com.cn 和yangyangfuture at gmail dot com'
    
class TestMain(TestCase):
    
    def test_seg_generator(self): 
        ex = RegularExtrator(text) 
        print(ex.clear_txt())
        print(ex.split_txt(r'[：]'))
        print(ex.split_list())
        print(ex.seg_generator(10,5))
        self.assertTrue(len(ex.data_list)>0)

if __name__ == "__main__": 
    unittest.main()