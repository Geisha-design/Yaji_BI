from DrissionPage import ChromiumOptions

from DrissionPage import Chromium
from DrissionPage.common import Settings



Settings.set_singleton_tab_obj(False)
browser = Chromium()
tab1 = browser.new_tab("https://www.1688.com/zw/page.html?hpageId=old-sem-pc-list&keywords=博仕宠物食品（淮安）有限公司")
# tab2 = browser.get_tab()
print(tab1.title, id(tab1))

