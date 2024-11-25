import json,requests,os,urllib.parse
from dotenv import load_dotenv
from thefuzz import fuzz
import pandas as pd

load_dotenv()
class Airtable:
    def __init__(self):
        self.apikey = os.getenv('AIRTABLE_apikey')
        self.headers = {'Authorization': f'Bearer {self.apikey}','Content-Type': 'application/json'}
        self.GetInvestors()

    def Credd(self,view,crmid,prostable):
        return [view,crmid,prostable]

    def GetCompany(self,cred):
        # Fetch company data from Airtable
        print("Get all company data...")
        AllRecordIds = []
        offset = ''
        while True:
            CompanyTableURL = f'https://api.airtable.com/v0/{cred[1]}/{cred[2]}'
            params = {'offset': offset,"view":''}
            if cred[0]:
                params['view'] = cred[0]
            OutputTable = requests.get(CompanyTableURL, headers=self.headers, params=params).json()
            for record in OutputTable["records"]:
                fields = record.get("fields", {})
                if "Company Name" not in fields:
                    continue
                SingleRecord = {
                    "Company": fields["Company Name"],
                    "HQ": fields.get('HQ', ''),
                    "Website": fields.get("Website", ''),
                    "Link to Company": fields.get("Link to Company",'')
                }
                print(" " * 5, SingleRecord["Company"])
                AllRecordIds.append(SingleRecord)
            
            if "offset" not in OutputTable:
                break
            offset = OutputTable["offset"]
        if AllRecordIds:
            print("Done!")
            return AllRecordIds

    def GetInvestors(self):
        print("Get all Investors data...")
        AllRecordIds = []
        offset = ''
        while True:
            CompanyTableURL = f'https://api.airtable.com/v0/appjvhsxUUz6o0dzo/tblOws03Uc7SOVAKI'
            params = {'offset': offset,"view":''}
            params['view'] = "Grid view"
            OutputTable = requests.get(CompanyTableURL, headers=self.headers, params=params).json()
            for record in OutputTable["records"]:
                fields = record.get("fields", {})
                if "Name" not in fields:
                    continue
                SingleRecord = {"InvName": fields["Name"],"RecordId":record['id']}
                print("Investor Name: ", SingleRecord["InvName"])
                AllRecordIds.append(SingleRecord)
            if "offset" not in OutputTable:
                break
            offset = OutputTable["offset"]
        if AllRecordIds:
            with open('../documents/InvestorData.json','w+') as Data:
                Data.write(json.dumps(AllRecordIds))

    def FindInvestor(self,invName):
        with open('../documents/InvestorData.json','r+') as inv:
            investors = json.load(inv)
        investor = next((i for i in investors if i['InvName'] == invName), None)
        return investor['RecordId'] if investor else print(f'Investor "{invName}" not found!')

    def FuzMatch(self,CompanyRecords):
        print("Checking Company...")
        df = pd.read_excel('..\documents\data-shortly.xlsx').drop_duplicates()
        for row_index in range(df.shape[0]):
            for record in CompanyRecords:
                percetange = fuzz.ratio(df.iloc[row_index,1],record['Company'])
                if percetange>70:
                    break
            if percetange <50:
                print(f'Check {df.iloc[row_index,1]} and {record["Company"]}: {percetange}%')
                ProsData = json.dumps({
                    "fields":{
                        "Company Name":df.iloc[row_index,1],
                        "Website (Delete)":df.iloc[row_index,2],
                        "LinkedIn URL (Delete)":df.iloc[row_index,3],
                    }
                })
                CompData = json.dumps({
                    "fields":{
                        "Company Name":df.iloc[row_index,1],
                        "Website":df.iloc[row_index,2],
                        "LinkedInURL":df.iloc[row_index,3],
                    }
                })
                try:
                    foundInvest = self.FindInvestor(invName=df.iloc[row_index,0])
                    if foundInvest: 
                        print(foundInvest)
                        CompRec = self.CreateField(cred=ar.Credd(view="Company",crmid="appjvhsxUUz6o0dzo",prostable="tblEssTJ1FlLrTj8Q"),data=CompData)
                        ProsRec = self.CreateField(cred=ar.Credd(view=df.iloc[row_index,0],crmid="appjvhsxUUz6o0dzo",prostable="tblf4Ed9PaDo76QHH"),data=ProsData)
                        self.UpRec(cred=ar.Credd(view=df.iloc[row_index,0],crmid="appjvhsxUUz6o0dzo",prostable="tblf4Ed9PaDo76QHH"),data={"fields":{"Company Name":df.iloc[row_index,1],"Link to Company":[CompRec],"Linked Investors":[foundInvest],"Investors":[foundInvest]}},recId=ProsRec)
                        self.UpRec(cred=ar.Credd(view="Company",crmid="appjvhsxUUz6o0dzo",prostable="tblEssTJ1FlLrTj8Q"),data={"fields":{"Company Name":df.iloc[row_index,1],"Is Prospect (Link to Prospects)":[ProsRec],"Linked Investors (Link to Investors)":[foundInvest]}},recId=CompRec)
                except ValueError:
                    print("something error when creating data")

    def DeleteFields(self,recId,tabId):
        response = requests.delete(f"https://api.airtable.com/v0/appjvhsxUUz6o0dzo/{tabId}/{recId}",headers=self.headers)
        if response.status_code !=200:
            raise ValueError
        else:
            return f'success to deleting {recId} data'

    def UpRec(self,cred,data, recId):
        companyName = data['fields']['Company Name']
        response = requests.request(
            "PATCH",
            f"https://api.airtable.com/v0/{cred[1]}/{cred[2]}/{recId}",headers=self.headers,data=json.dumps(data)
        )
        print("CRM PATHCING STATUS: ", response.status_code)
        if response.status_code != 200:
            print(f"something error when updating data to airtable. {response.status_code}")
            try:
                print(self.DeleteFields(recId=recId,tabId=cred[2]))
            except ValueError:
                print(f"failed to delete {list(data['fields'].values())[1][0]} field!")
            # raise ValueError
        else:
            print(f"UPDATING {companyName} TO CRM DONE!")

    def CreateField(self,cred,data):
        response = requests.request("POST", f'https://api.airtable.com/v0/{cred[1]}/{cred[2]}', headers=self.headers, data=data)
        if response.status_code !=200:
            raise ValueError
        else:
            print(f"Success to create {json.loads(data)['fields']['Company Name']} fields")
            return json.loads(response.text)['id']

if __name__ == "__main__":
    ar = Airtable()
    credential = ar.Credd(view="Nashville Entrepreneur Center",crmid="appjvhsxUUz6o0dzo",prostable="tblf4Ed9PaDo76QHH")
    ar.FuzMatch(CompanyRecords=ar.GetCompany(cred=credential))
    # ar.GetInvestors()
    # ar.DeleteFields(recId="rec02wx281njjRjhm",tabId="tblf4Ed9PaDo76QHH")
    # ar.UpRec(cred=ar.Credd(view="",crmid="appjvhsxUUz6o0dzo",prostable="tblf4Ed9PaDo76QHH"),data={"fields":{"Company Name":"KEY Concierge"}},recId="CompRec")
