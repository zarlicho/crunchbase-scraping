import time,json,urllib.parse,random,os,requests
from selenium.webdriver.common.by import By
from seleniumbase import SB
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from lxml import html
load_dotenv()

class Cnbase:
	def __init__(self):
		self.sb = None
		self.email = os.getenv('EMAIL')
		self.password = os.getenv('PASS')

	def login(self):
		self.sb.uc_open_with_reconnect("https://www.crunchbase.com/login", 3)
		for retry in range(3):
			try:
				if self.sb.is_text_visible(text="Oops! There was a problem!",selector='//*[@id="mat-mdc-dialog-title-0"]',by=By.XPATH):
					self.sb.refresh()
				self.sb.send_keys('/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/mat-form-field[1]/div[1]/div/div[2]/input', os.getenv('EMAIL'),by=By.XPATH,timeout=10)
				self.sb.send_keys('/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/mat-form-field[2]/div[1]/div/div[2]/input', os.getenv('PASS'),by=By.XPATH,timeout=10)
				self.sb.uc_click(selector='/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/div[2]/button[1]', by=By.XPATH,timeout=10)
				print("login successfuly")
				break
			except Exception as e:
				print(f"{e} in {retry+1}x")
				self.sb.refresh()

		# time.sleep(100)

	def get_element_bs4(self,selector,pgSource,types=""):
		tree = html.fromstring(pgSource)
		if len(tree.xpath(selector)) != 0:
			if types=="text":
				return tree.xpath(selector)[0].text_content()
			else:
				return tree.xpath(selector)[0]
		else:
			return None

	def get_elements(self, selector, by):
		try:
			self.sb.wait_for_element_visible(selector, by=by, timeout=10)
			if self.sb.is_element_visible(selector, by):
				try:
					return self.sb.find_elements(selector, by, limit=50)
				except Exception as e:
					print(f"Error finding elements {selector}: {e}")
					return None
			else:
				print(f"Element {selector} not found!")
				return None
		except Exception as e:
			print(f"Exception in get_elements for {selector}: {e}")
			return None

	def getProfile(self,profUrl):
		self.sb.open(profUrl)
		investName = self.get_element_bs4(selector="/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/ng-component/entity-v2/page-layout/div/div/profile-header/div/header/div/div/div/div[2]/div[1]/h1/text()",pgSource=self.sb.get_page_source())
		investWeb = self.get_element_bs4(selector="//*[@id='mat-tab-nav-panel-0']/div/full-profile/page-centered-layout[1]/div/row-card/div/div[1]/profile-section/section-card/mat-card/div[2]/fields-card/ul/li[5]/label-with-icon/span/field-formatter/link-formatter/a/@href",pgSource=self.sb.get_page_source())
		investLinkedin = self.sb.find_elements(selector="//*[@class='icon']", by="xpath")
		for icon_element in investLinkedin:
			all_links = [(a.get_attribute("href")) for li in icon_element.find_elements(By.TAG_NAME, "li") for a in li.find_elements(By.TAG_NAME, "a") if "linkedin" in a.get_attribute("href")]
			for linkedin in all_links:
				print(investName,investWeb,linkedin)

	def getInvestments(self,investUrl):
		self.sb.open(investUrl+"/recent_investments/investments")
		self.sb.uc_click(selector='//*[@id="mat-tab-nav-panel-0"]/div/div/page-centered-layout[2]/div/profile-section/section-card/mat-card/div[2]/list-card/list-card-more-results/button',by=By.XPATH)
		orgaName = self.sb.find_elements(selector='//*[@id="mat-tab-nav-panel-0"]/div/div/page-centered-layout[2]/div/profile-section/section-card/mat-card/div[2]/list-card/div/table/tbody',by=By.XPATH)
		for tbody in orgaName:
			all_organization = [(tra.get_attribute("href")) for tr in tbody.find_elements(By.TAG_NAME,"tr") for tra in tr.find_elements(By.TAG_NAME,"a") if "organization" in tra.get_attribute("href")]
			# print(all_organization)
			for orgaurl in all_organization:
				self.getProfile(orgaurl)


	def main(self):
		with SB(uc=True) as sb:
			self.sb = sb
			self.login()
			# self.getProfile("https://www.crunchbase.com/organization/luxus-ed55")
			print(self.getInvestments("https://www.crunchbase.com/organization/atx-venture-partners"))

crunchbase = Cnbase()
crunchbase.main()
