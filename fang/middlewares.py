# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals

import random

class UserAgentDownloadMiddlewares(object):
    USER_AGENTS = [
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Acoo '
        'Browser 1.98.744; .NET CLR 3.5.30729)',
        'Mozilla/4.0 (compatible; MSIE 7.0; America Online Browser 1.1; '
        'Windows NT 5.1; (R1 1.5); .NET CLR 2.0.50727; InfoPath.1)',
        'Mozilla/5.0 (compatible; MSIE 9.0; AOL 9.7; AOLBuild 4343.19; '
        'Windows NT 6.1; WOW64; Trident/5.0; FunWebProducts)',
        'Mozilla/5.0 (compatible; U; ABrowse 0.6; Syllable) AppleWebKit/420+ '
        '(KHTML, like Gecko)'
    ]

    def process_request(self,request,spider):
        user_agent = random.choice(self.USER_AGENTS)
        request.headers['User-Agent'] = user_agent