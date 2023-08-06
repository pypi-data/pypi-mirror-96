# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   driver_page.py
"""
from glob import glob
from pathlib import Path
from typing import Union, List, Any, Tuple
from urllib.parse import quote

from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from time import time, sleep

from .common import str_to_loc, get_available_file_name, translate_loc, format_html
from .driver_element import DriverElement, execute_driver_find


class DriverPage(object):
    """DriverPage封装了页面操作的常用功能，使用selenium来获取、解析、操作网页"""

    def __init__(self, driver: WebDriver, timeout: float = 10):
        """初始化函数，接收一个WebDriver对象，用来操作网页"""
        self._driver = driver
        self._timeout = timeout
        self._url = None
        self._url_available = None
        self._wait = None

        self.retry_times = 3
        self.retry_interval = 2

    @property
    def driver(self) -> WebDriver:
        return self._driver

    @property
    def url(self) -> Union[str, None]:
        """返回当前网页url"""
        if not self._driver or not self.driver.current_url.startswith('http'):
            return None
        else:
            return self.driver.current_url

    @property
    def html(self) -> str:
        """返回页面html文本"""
        return format_html(self.driver.find_element_by_xpath("//*").get_attribute("outerHTML"))

    @property
    def url_available(self) -> bool:
        """url有效性"""
        return self._url_available

    @property
    def cookies(self) -> list:
        """返回当前网站cookies"""
        return self.get_cookies(True)

    @property
    def title(self) -> str:
        """返回网页title"""
        return self.driver.title

    @property
    def timeout(self) -> float:
        return self._timeout

    @timeout.setter
    def timeout(self, second: float) -> None:
        self._timeout = second
        self._wait = None

    @property
    def wait(self) -> WebDriverWait:
        if self._wait is None:
            self._wait = WebDriverWait(self.driver, timeout=self.timeout)

        return self._wait

    def get_cookies(self, as_dict: bool = False) -> Union[list, dict]:
        """返回当前网站cookies"""
        if as_dict:
            return {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
        else:
            return self.driver.get_cookies()

    def _try_to_connect(self,
                        to_url: str,
                        times: int = 0,
                        interval: float = 1,
                        show_errmsg: bool = False, ):
        """尝试连接，重试若干次                            \n
        :param to_url: 要访问的url
        :param times: 重试次数
        :param interval: 重试间隔（秒）
        :param show_errmsg: 是否抛出异常
        :return: 是否成功
        """
        err = None
        is_ok = False

        for _ in range(times + 1):
            try:
                self.driver.get(to_url)
                go_ok = True
            except Exception as e:
                err = e
                go_ok = False

            is_ok = self.check_page() if go_ok else False

            if is_ok is not False:
                break

            if _ < times:
                sleep(interval)
                print(f'重试 {to_url}')

        if is_ok is False and show_errmsg:
            raise err if err is not None else ConnectionError('Connect error.')

        return is_ok

    def get(self,
            url: str,
            go_anyway: bool = False,
            show_errmsg: bool = False,
            retry: int = None,
            interval: float = None) -> Union[None, bool]:
        """访问url                                            \n
        :param url: 目标url
        :param go_anyway: 若目标url与当前url一致，是否强制跳转
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :return: 目标url是否可用
        """
        to_url = quote(url, safe='/:&?=%;#@+!')
        retry = int(retry) if retry is not None else int(self.retry_times)
        interval = int(interval) if interval is not None else int(self.retry_interval)

        if not url or (not go_anyway and self.url == to_url):
            return

        self._url = to_url
        self._url_available = self._try_to_connect(to_url, times=retry, interval=interval, show_errmsg=show_errmsg)

        try:
            self._driver.execute_script('Object.defineProperty(navigator,"webdriver",{get:() => Chrome,});')
        except:
            pass

        return self._url_available

    def ele(self,
            loc_or_ele: Union[Tuple[str, str], str, DriverElement, WebElement],
            mode: str = None,
            timeout: float = None) -> Union[DriverElement, List[DriverElement], str, None]:
        """返回页面中符合条件的元素，默认返回第一个                                                         \n
        示例：                                                                                           \n
        - 接收到元素对象时：                                                                              \n
            返回DriverElement对象                                                                        \n
        - 用loc元组查找：                                                                                \n
            ele.ele((By.CLASS_NAME, 'ele_class')) - 返回所有class为ele_class的子元素                      \n
        - 用查询字符串查找：                                                                              \n
            查找方式：属性、tag name和属性、文本、xpath、css selector、id、class                             \n
            @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串           \n
            page.ele('.ele_class')                       - 返回第一个 class 为 ele_class 的元素            \n
            page.ele('.:ele_class')                      - 返回第一个 class 中含有 ele_class 的元素         \n
            page.ele('#ele_id')                          - 返回第一个 id 为 ele_id 的元素                  \n
            page.ele('#:ele_id')                         - 返回第一个 id 中含有 ele_id 的元素               \n
            page.ele('@class:ele_class')                 - 返回第一个class含有ele_class的元素              \n
            page.ele('@name=ele_name')                   - 返回第一个name等于ele_name的元素                \n
            page.ele('@placeholder')                     - 返回第一个带placeholder属性的元素               \n
            page.ele('tag:p')                            - 返回第一个<p>元素                              \n
            page.ele('tag:div@class:ele_class')          - 返回第一个class含有ele_class的div元素           \n
            page.ele('tag:div@class=ele_class')          - 返回第一个class等于ele_class的div元素           \n
            page.ele('tag:div@text():some_text')         - 返回第一个文本含有some_text的div元素             \n
            page.ele('tag:div@text()=some_text')         - 返回第一个文本等于some_text的div元素             \n
            page.ele('text:some_text')                   - 返回第一个文本含有some_text的元素                \n
            page.ele('some_text')                        - 返回第一个文本含有some_text的元素（等价于上一行）  \n
            page.ele('text=some_text')                   - 返回第一个文本等于some_text的元素                \n
            page.ele('xpath://div[@class="ele_class"]')  - 返回第一个符合xpath的元素                        \n
            page.ele('css:div.ele_class')                - 返回第一个符合css selector的元素                 \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param mode: 'single' 或 'all‘，对应查找一个或全部
        :param timeout: 查找元素超时时间
        :return: DriverElement对象
        """
        # 接收到字符串或元组，获取定位loc元组
        if isinstance(loc_or_ele, (str, tuple)):
            if isinstance(loc_or_ele, str):
                loc_or_ele = str_to_loc(loc_or_ele)
            else:
                if len(loc_or_ele) != 2:
                    raise ValueError("Len of loc_or_ele must be 2 when it's a tuple.")
                loc_or_ele = translate_loc(loc_or_ele)

            # if loc_or_ele[0] == 'xpath' and not loc_or_ele[1].startswith(('/', '(')):
            #     loc_or_ele = loc_or_ele[0], f'//{loc_or_ele[1]}'

        # 接收到DriverElement对象直接返回
        elif isinstance(loc_or_ele, DriverElement):
            return loc_or_ele

        # 接收到WebElement对象打包成DriverElement对象返回
        elif isinstance(loc_or_ele, WebElement):
            return DriverElement(loc_or_ele, self)

        # 接收到的类型不正确，抛出异常
        else:
            raise ValueError('Argument loc_or_str can only be tuple, str, DriverElement, DriverElement.')

        return execute_driver_find(self, loc_or_ele, mode, timeout)

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[DriverElement]:
        """返回页面中所有符合条件的元素                                                                     \n
        示例：                                                                                            \n
        - 用loc元组查找：                                                                                 \n
            page.eles((By.CLASS_NAME, 'ele_class')) - 返回所有class为ele_class的元素                       \n
        - 用查询字符串查找：                                                                               \n
            查找方式：属性、tag name和属性、文本、xpath、css selector、id、class                             \n
            @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串           \n
            page.eles('.ele_class')                       - 返回所有 class 为 ele_class 的元素            \n
            page.eles('.:ele_class')                      - 返回所有 class 中含有 ele_class 的元素         \n
            page.eles('#ele_id')                          - 返回所有 id 为 ele_id 的元素                  \n
            page.eles('#:ele_id')                         - 返回所有 id 中含有 ele_id 的元素               \n
            page.eles('@class:ele_class')                 - 返回所有class含有ele_class的元素               \n
            page.eles('@name=ele_name')                   - 返回所有name等于ele_name的元素                 \n
            page.eles('@placeholder')                     - 返回所有带placeholder属性的元素                \n
            page.eles('tag:p')                            - 返回所有<p>元素                               \n
            page.eles('tag:div@class:ele_class')          - 返回所有class含有ele_class的div元素            \n
            page.eles('tag:div@class=ele_class')          - 返回所有class等于ele_class的div元素            \n
            page.eles('tag:div@text():some_text')         - 返回所有文本含有some_text的div元素             \n
            page.eles('tag:div@text()=some_text')         - 返回所有文本等于some_text的div元素             \n
            page.eles('text:some_text')                   - 返回所有文本含有some_text的元素                \n
            page.eles('some_text')                        - 返回所有文本含有some_text的元素（等价于上一行）  \n
            page.eles('text=some_text')                   - 返回所有文本等于some_text的元素                \n
            page.eles('xpath://div[@class="ele_class"]')  - 返回所有符合xpath的元素                        \n
            page.eles('css:div.ele_class')                - 返回所有符合css selector的元素                 \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间
        :return: DriverElement对象组成的列表
        """
        if not isinstance(loc_or_str, (tuple, str)):
            raise TypeError('Type of loc_or_str can only be tuple or str.')

        return self.ele(loc_or_str, mode='all', timeout=timeout)

    # ----------------以下为独有函数-----------------------
    def wait_ele(self,
                 loc_or_ele: Union[str, tuple, DriverElement, WebElement],
                 mode: str,
                 timeout: float = None) -> bool:
        """等待元素从dom删除、显示、隐藏                             \n
        :param loc_or_ele: 可以是元素、查询字符串、loc元组
        :param mode: 等待方式，可选：'del', 'display', 'hidden'
        :param timeout: 等待超时时间
        :return: 等待是否成功
        """
        if mode.lower() not in ('del', 'display', 'hidden'):
            raise ValueError('Argument mode can only be "del", "display", "hidden"')

        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as ec

        timeout = timeout or self.timeout
        is_ele = False

        if isinstance(loc_or_ele, DriverElement):
            loc_or_ele = loc_or_ele.inner_ele
            is_ele = True

        elif isinstance(loc_or_ele, WebElement):
            is_ele = True

        elif isinstance(loc_or_ele, str):
            loc_or_ele = str_to_loc(loc_or_ele)

        elif isinstance(loc_or_ele, tuple):
            pass

        else:
            raise TypeError('The type of loc_or_ele can only be str, tuple, DriverElement, WebElement')

        # 当传入参数是元素对象时
        if is_ele:
            end_time = time() + timeout

            while time() < end_time:
                if mode == 'del':
                    try:
                        loc_or_ele.is_enabled()
                    except:
                        return True

                elif mode == 'display' and loc_or_ele.is_displayed():
                    return True

                elif mode == 'hidden' and not loc_or_ele.is_displayed():
                    return True

            return False

        # 当传入参数是控制字符串或元组时
        else:
            try:
                if mode == 'del':
                    WebDriverWait(self.driver, timeout).until_not(ec.presence_of_element_located(loc_or_ele))

                elif mode == 'display':
                    WebDriverWait(self.driver, timeout).until(ec.visibility_of_element_located(loc_or_ele))

                elif mode == 'hidden':
                    WebDriverWait(self.driver, timeout).until_not(ec.visibility_of_element_located(loc_or_ele))

                return True

            except:
                return False

    def check_page(self) -> Union[bool, None]:
        """检查页面是否符合预期            \n
        由子类自行实现各页面的判定规则
        """
        return None

    def run_script(self, script: str, *args) -> Any:
        """执行js代码                 \n
        :param script: js文本
        :param args: 传入的参数
        :return: js执行结果
        """
        return self.driver.execute_script(script, *args)

    @property
    def tabs_count(self) -> int:
        """返回标签页数量"""
        try:
            return len(self.driver.window_handles)
        except:
            return 0

    @property
    def tab_handles(self) -> list:
        """返回所有标签页handle列表"""
        return self.driver.window_handles

    @property
    def current_tab_num(self) -> int:
        """返回当前标签页序号"""
        return self.driver.window_handles.index(self.driver.current_window_handle)

    @property
    def current_tab_handle(self) -> str:
        """返回当前标签页handle"""
        return self.driver.current_window_handle

    def create_tab(self, url: str = '') -> None:
        """新建并定位到一个标签页,该标签页在最后面  \n
        :param url: 新标签页跳转到的网址
        :return: None
        """
        self.to_tab(-1)
        self.run_script(f'window.open("{url}");')
        self.to_tab(-1)

    def close_current_tab(self) -> None:
        """关闭当前标签页"""
        self.driver.close()

        if self.tabs_count:
            self.to_tab(0)

    def close_other_tabs(self, num_or_handles: Union[int, str, list, tuple] = None) -> None:
        """关闭传入的标签页以外标签页，默认保留当前页。可传入列表或元组                                \n
        :param num_or_handles: 要保留的标签页序号或handle，可传入handle组成的列表或元组
        :return: None
        """
        try:
            tab = int(num_or_handles)
        except (ValueError, TypeError):
            tab = num_or_handles

        tabs = self.driver.window_handles

        if tab is None:
            page_handle = (self.current_tab_handle,)
        elif isinstance(tab, int):
            page_handle = (tabs[tab],)
        elif isinstance(tab, str):
            page_handle = (tab,)
        elif isinstance(tab, (list, tuple)):
            page_handle = tab
        else:
            raise TypeError('Argument num_or_handle can only be int, str, list or tuple.')

        for i in tabs:  # 遍历所有标签页，关闭非保留的
            if i not in page_handle:
                self.driver.switch_to.window(i)
                self.driver.close()

        self.driver.switch_to.window(page_handle[0])  # 把权柄定位回保留的页面

    def to_tab(self, num_or_handle: Union[int, str] = 0) -> None:
        """跳转到标签页                                                         \n
        :param num_or_handle: 标签页序号或handle字符串，序号第一个为0，最后为-1
        :return: None
        """
        try:
            tab = int(num_or_handle)
        except (ValueError, TypeError):
            tab = num_or_handle

        tab = self.driver.window_handles[tab] if isinstance(tab, int) else tab
        self.driver.switch_to.window(tab)

    def to_iframe(self, loc_or_ele: Union[int, str, tuple, WebElement, DriverElement] = 'main') -> None:
        """跳转到iframe                                                                         \n
        可接收iframe序号(0开始)、id或name、查询字符串、loc元组、WebElement对象、DriverElement对象，  \n
        传入'main'跳到最高层，传入'parent'跳到上一层                                               \n
        示例：                                                                                   \n
            to_iframe('tag:iframe')    - 通过传入iframe的查询字符串定位                            \n
            to_iframe('iframe_id')     - 通过iframe的id属性定位                                   \n
            to_iframe('iframe_name')   - 通过iframe的name属性定位                                 \n
            to_iframe(iframe_element)  - 通过传入元素对象定位                                      \n
            to_iframe(0)               - 通过iframe的序号定位                                     \n
            to_iframe('main')          - 跳到最高层                                               \n
            to_iframe('parent')        - 跳到上一层                                               \n
        :param loc_or_ele: iframe的定位信息
        :return: None
        """
        # 根据序号跳转
        if isinstance(loc_or_ele, int):
            self.driver.switch_to.frame(loc_or_ele)

        elif isinstance(loc_or_ele, str):
            # 跳转到最上级
            if loc_or_ele == 'main':
                self.driver.switch_to.default_content()

            # 跳转到上一层
            elif loc_or_ele == 'parent':
                self.driver.switch_to.parent_frame()

            # 传入id或name
            elif ':' not in loc_or_ele and '=' not in loc_or_ele:
                self.driver.switch_to.frame(loc_or_ele)

            # 传入控制字符串
            else:
                ele = self.ele(loc_or_ele)
                self.driver.switch_to.frame(ele.inner_ele)

        elif isinstance(loc_or_ele, WebElement):
            self.driver.switch_to.frame(loc_or_ele)

        elif isinstance(loc_or_ele, DriverElement):
            self.driver.switch_to.frame(loc_or_ele.inner_ele)

        elif isinstance(loc_or_ele, tuple):
            ele = self.ele(loc_or_ele)
            self.driver.switch_to.frame(ele.inner_ele)

    def screenshot(self, path: str, filename: str = None) -> str:
        """截取页面可见范围截图                                  \n
        :param path: 保存路径
        :param filename: 图片文件名，不传入时以页面title命名
        :return: 图片完整路径
        """
        name = filename or self.title
        path = Path(path).absolute()
        path.mkdir(parents=True, exist_ok=True)
        name = get_available_file_name(str(path), f'{name}.png')
        img_path = f'{path}\\{name}'
        self.driver.save_screenshot(img_path)
        return img_path

    def scroll_to_see(self, loc_or_ele: Union[str, tuple, WebElement, DriverElement]) -> None:
        """滚动页面直到元素可见                                                        \n
        :param loc_or_ele: 元素的定位信息，可以是loc元组，或查询字符串（详见ele函数注释）
        :return: None
        """
        ele = self.ele(loc_or_ele)
        ele.run_script("arguments[0].scrollIntoView();")

    def scroll_to(self, mode: str = 'bottom', pixel: int = 300) -> None:
        """按参数指示方式滚动页面                                                                           \n
        :param mode: 可选滚动方向：'top', 'bottom', 'rightmost', 'leftmost', 'up', 'down', 'left', 'right'
        :param pixel: 滚动的像素
        :return: None
        """
        if mode == 'top':
            self.driver.execute_script("window.scrollTo(document.documentElement.scrollLeft,0);")

        elif mode == 'bottom':
            self.driver.execute_script(
                "window.scrollTo(document.documentElement.scrollLeft,document.body.scrollHeight);")

        elif mode == 'rightmost':
            self.driver.execute_script("window.scrollTo(document.body.scrollWidth,document.documentElement.scrollTop);")

        elif mode == 'leftmost':
            self.driver.execute_script("window.scrollTo(0,document.documentElement.scrollTop);")

        elif mode == 'up':
            self.driver.execute_script(f"window.scrollBy(0,-{pixel});")

        elif mode == 'down':
            self.driver.execute_script(f"window.scrollBy(0,{pixel});")

        elif mode == 'left':
            self.driver.execute_script(f"window.scrollBy(-{pixel},0);")

        elif mode == 'right':
            self.driver.execute_script(f"window.scrollBy({pixel},0);")

        else:
            raise ValueError(
                "Argument mode can only be 'top', 'bottom', 'rightmost', 'leftmost', 'up', 'down', 'left', 'right'.")

    def refresh(self) -> None:
        """刷新当前页面"""
        self.driver.refresh()

    def back(self) -> None:
        """浏览器后退"""
        self.driver.back()

    def set_window_size(self, x: int = None, y: int = None) -> None:
        """设置浏览器窗口大小，默认最大化，任一参数为0最小化  \n
        :param x: 浏览器窗口高
        :param y: 浏览器窗口宽
        :return: None
        """
        if x is None and y is None:
            self.driver.maximize_window()

        elif x == 0 or y == 0:
            self.driver.minimize_window()

        else:
            if x < 0 or y < 0:
                raise ValueError('Arguments x and y must greater than 0.')

            new_x = x or self.driver.get_window_size()['width']
            new_y = y or self.driver.get_window_size()['height']
            self.driver.set_window_size(new_x, new_y)

    def chrome_downloading(self, download_path: str) -> list:
        """返回浏览器下载中的文件列表             \n
        :param download_path: 下载文件夹路径
        :return: 文件列表
        """
        return glob(f'{download_path}\\*.crdownload')

    def process_alert(self, mode: str = 'ok', text: str = None) -> Union[str, None]:
        """处理提示框                                                            \n
        :param mode: 'ok' 或 'cancel'，若输入其它值，不会按按钮但依然返回文本值
        :param text: 处理prompt提示框时可输入文本
        :return: 提示框内容文本
        """
        try:
            alert = self.driver.switch_to.alert
        except NoAlertPresentException:
            return None

        if text:
            alert.send_keys(text)

        text = alert.text

        if mode == 'cancel':
            alert.dismiss()

        elif mode == 'ok':
            alert.accept()

        return text
