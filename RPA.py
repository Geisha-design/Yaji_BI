from DrissionPage import ChromiumOptions

from DrissionPage import Chromium
from DrissionPage.common import Settings



Settings.set_singleton_tab_obj(False)
browser = Chromium()
tab1 = browser.new_tab("https://www.1688.com/zw/hamlet.html?scene=6&cosite=baidujj_pz&location=re&trackid=885662561117990122602&")
# tab2 = browser.get_tab()
print(tab1.title, id(tab1))

