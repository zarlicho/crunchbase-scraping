import time,json,requests,os,urllib.parse
from dotenv import load_dotenv
from thefuzz import fuzz
import pandas as pd

load_dotenv()
class Airtable:
    def __init__(self):
        self.apikey = os.getenv('AIRTABLE_apikey')
        self.headers = {'Authorization': f'Bearer {self.apikey}'}
        self.PostHead = {'Authorization': f'Bearer {self.apikey}','Content-Type': 'application/json'}
    
    def Credd(self,view,crmid,prostable):
        return [view,crmid,prostable]

    def GetCompany(self,cred):
        # Fetch company data from Airtable
        print("Get all company data...")
        AllRecordIds = []
        offset = ''
        while True:
            CompanyTableURL = f'https://api.airtable.com/v0/{cred[1]}/{cred[2]}'
            params = {'offset': offset}
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

    def FuzMatch(self,CompanyRecords):
        print("Checking Company...")
        df = pd.read_excel('..\documents\data-shortly.xlsx')
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
                    ProsRec = self.CreateField(cred=ar.Credd(view="ATX Ventures",crmid="appjvhsxUUz6o0dzo",prostable="tblf4Ed9PaDo76QHH"),data=ProsData)
                    CompRec = self.CreateField(cred=ar.Credd(view="ATX Ventures",crmid="appjvhsxUUz6o0dzo",prostable="tblEssTJ1FlLrTj8Q"),data=CompData)
                    self.UpRec(cred=ar.Credd(view="ATX Ventures",crmid="appjvhsxUUz6o0dzo",prostable="tblf4Ed9PaDo76QHH"),data={"fields":{"Company Name":df.iloc[row_index,1],"Link to Company":[CompRec]}})
                    self.UpRec(cred=ar.Credd(view="ATX Ventures",crmid="appjvhsxUUz6o0dzo",prostable="tblEssTJ1FlLrTj8Q"),data={"fields":{"Company Name":df.iloc[row_index,1],"Is Prospect (Link to Prospects)":[ProsRec]}})
                except ValueError:
                    print("something error when creating data")

    def UpRec(self,cred,data):
        companyName = data['fields']['Company Name']
        response = requests.request(
            "PATCH",
            f"https://api.airtable.com/v0/{cred[1]}/{cred[2]}/"
            f"{requests.request('GET', f'https://api.airtable.com/v0/{cred[1]}/{cred[2]}?filterByFormula=%7BCompany+Name%7D%3D%27{urllib.parse.quote_plus(companyName)}%27', headers=self.headers).json()['records'][0]['id']}",
            headers=self.PostHead,
            data=json.dumps(data)
        )

        print("CRM PATHCING STATUS: ", response.status_code)
        if response.status_code != 200:
            print(f"something error when updating data to airtable. {response.status_code}")
            raise ValueError
        else:
            print(f"UPDATING {companyName} TO CRM DONE!")

    def CreateField(self,cred,data):
        response = requests.request("POST", f'https://api.airtable.com/v0/{cred[1]}/{cred[2]}', headers=self.PostHead, data=data)
        if response.status_code !=200:
            raise ValueError
        else:
            print(f"Success to create {json.loads(data)['fields']['Company Name']} fields")
            return json.loads(response.text)['id']

if __name__ == "__main__":
    ar = Airtable()
    credential = ar.Credd(view="ATX Ventures",crmid="appjvhsxUUz6o0dzo",prostable="tblf4Ed9PaDo76QHH")
    ar.FuzMatch(CompanyRecords=ar.GetCompany(cred=credential))