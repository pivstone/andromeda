from django.test import TestCase, Client

__author__ = 'pivstone'


class UrlsRouterTest(TestCase):
    """
    测试 URL Router的匹配情况
    """

    def setUp(self):
        self.client = Client()
        self.urls_list = [
            "/v2/",
            "/v2/_catalog",
        ]

    def test_v2_api_root(self):
        for url in self.urls_list:
            self.assertEqual(200, self.client.get(url).status_code)

    def test_p(self):
        class Solution(object):
            def longestPalindrome(self, s):
                """
                :type s: str
                :rtype: str
                """
                if not s:
                    return s
                if len(s)==1:
                    return s
                def center(t,left,right):
                    while(left>=0 and right<len(t) and t[left]==t[right]):
                        left-=1
                        right+=1
                    return right-left-1

                half=(len(s)+1)//2-1

                def half_range(area):
                    start = 0
                    end = 0
                    for i in area:
                        le=center(s,i,i)
                        le2=center(s,i,i+1)
                        lex=max(le,le2)
                        if lex>end-start:
                            end=i+lex//2
                            start=i-(lex-1)//2
                    return start,end
                s1,e1=half_range(range(half,-1,-1))
                s2,e2=half_range(range(half,len(s)))
                if e1-s1 > e2-s2:
                    start=s1
                    end=e1
                else:
                    start = s2
                    end = e2
                return s[start:end+1]


        s = Solution()
        print(s.longestPalindrome("bbb"))
