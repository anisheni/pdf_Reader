# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 09:15:10 2021

@author: INANKUM29
"""

import tabula
import pandas as pd
import numpy
import re
import os
import pdfplumber
import camelot

os.chdir(r'C:\Users\inankum29\Desktop\python_code\Data\pdf_read')

#Appending all pdf files

ca1 = camelot.read_pdf('Global Job Structure Job Profile Manual R9_01092018_final version on 20180921.pdf', flavor='stream', pages='8-19')
main_df = pd.DataFrame()
ca = ca1
for i in range(len(ca)):
    print(ca1[i].df.columns)
    main_df = pd.concat([main_df,ca[i].df], ignore_index=True)
 
main_df.columns = ['Job_family','Job ID','page number','page_2']
main_df.to_csv('Jobs_list.csv')


#Function to fetch competency details
def second_sheet_2page(pdf_file,page1,page2,job_ref):
    try:
        print("##########JobRef#########:",job_ref)
        ########Tables Reading 
        #To read pdf with two page gap give first page as same page number u want to read and second page
        df = tabula.read_pdf(pdf_file, pages=str(page1)+'-'+str(page2-1), lattice=True)[0]
        if(len(df.columns)>2):
            df = df.iloc[:, [0,1,2]]
            df.columns.values[0] = "Career Level"
            df.columns.values[1] = "Definition"
            df.columns.values[2] = "Competencies"
        else:
            df = df.iloc[:, [0,1]]
            df.columns.values[0] = "Career Level"
            df.columns.values[1] = "Definition"
            print("^^^^^^^^^^^^^^^^^^^^^Two columns^^^^^^^^^^^^^^",job_ref)
        ##############Getting Top Data(like Functional area, Job ref, Version, Job)#################
        pdf = pdfplumber.open(pdf_file)
        txt = ''
        # TO read through pdf plumb first page will be less then the exact one and page 2 will be same i.e if u hve to read 87 and 88 page the page1:86, page2:88
        for i in range((page1-1),page2):
            txt  = txt+" "+pdf.pages[i].extract_text()
        index1   = txt.index('Printouts')
        index2   = txt.index('Page No:')
        new_text = txt[:index1] +txt[index2:]
        index3   = new_text.index('Career')
        cleaned_text    = new_text[:index3]
        funtional_area  = re.findall('Functional Area:(.*?)Job Family', cleaned_text)[0].strip()
        job_fam = cleaned_text.split("Job Family:")[-1].split("\nJob:")[0].strip()  
        job_ref = cleaned_text.split("Job Ref:")[-1].split("Version")[0].strip().replace(".",'')
        version = cleaned_text.split("Version")[-1].split("\n")[0].strip()
        job     = cleaned_text.split("Job:")[-1].split("Typical")[0].strip()
        typical = cleaned_text.split("Typical")[-1].split("Job Ref:")[0].strip().replace("Reporting Line:","")
        df['Job Ref'] = job_ref
        df['Version'] = version
        df['Functional Area'] = funtional_area
        df['Job Family'] = job_fam
        df['Job'] = job
        df = df.reindex(columns=['Job Ref','Version','Functional Area','Job Family','Job','Career Level','Definition','Competencies'])
        print("Job_Ref Done:",job_ref)
    except:
        print("$$$$$$$Error in Job Ref$$$$:",job_ref)
        df = pd.DataFrame(columns =['Job Ref','Version','Functional Area','Job Family','Job','Career Level','Definition','Competencies'], dtype=object)
        pass
    return df


def jd_repository(pdf,page1,page2,job_ref):
    #global pdf
    try:
        column_name = ['Job Ref','Version','Functional Area','Job Family','Job','Typical Reporting Line','Mission Statement','Category','Main Accountabilities']
        df = pd.DataFrame()
        #pdf = pdfplumber.open(file)
        txt = ''
        for i in range((page1-1),page2):
            txt  = txt+" "+pdf.pages[i].extract_text()
        index1   = txt.index('Printouts')
        index2   = txt.index('Page No:')
        new_text = txt[:index1] +txt[index2:]
        index3   = new_text.index('Career')
        cleaned_text    = new_text[:index3]
        funtional_area  = re.findall('Functional Area:(.*?)Job Family', cleaned_text)[0].strip()
        job_fam = cleaned_text.split("Job Family:")[-1].split("\nJob:")[0].strip()  
        job_ref = cleaned_text.split("Job Ref:")[-1].split("Version")[0].strip()
        job_ref = job_ref.replace(".",'')
        version = cleaned_text.split("Version")[-1].split("\n")[0].strip()
        job     = cleaned_text.split("Job:")[-1].split("Typical")[0].strip()
        typical = cleaned_text.split("Typical")[-1].split("Job Ref:")[0].strip().replace("Reporting Line:","")
        mission = cleaned_text.split("Mission")[-1].split("Main")[0].strip()
        mission = mission.replace('Mission','').replace('Statement:','').replace('\n','')
        #print("Functional Area:",funtional_area," Job Family:",job_fam," Job Reference:",job_ref," Version:",version," Job:",job," Typical:",typical, " Mission Statement:",mission)
        return_dict = {"Functional Area":funtional_area,"Job Family":job_fam,"Job Reference:":job_ref,"Version":version,"Job":job,"Typical":typical,"Mission Statement":mission}
        font_list = []
        for i in range((page1-1),page2):
            font_list.extend(pdf.pages[i].extract_words(extra_attrs=["fontname", "size"]))

        token = (re.findall(r'[0-9]\.',cleaned_text))
        token = token[1:]
        token.append('Page No')
        full_text = cleaned_text.split(token[1])[-1].split(token[2])[0].strip()
        tokenized_text = full_text.replace("\n",'').split()
        main_cat = []
        main_account_final = []
        for i in range(len(token)-1):
            full_text = cleaned_text.split(token[i])[-1].split(token[i+1])[0].strip()
            tokenized_text = full_text.replace("\n",'').split()
            first_index = next((index for (index, d) in enumerate(font_list) if ((font_list[index]["text"] == tokenized_text[0]) and (font_list[index+1]["text"] == tokenized_text[1]))), None)
            last_index = int(first_index)+len(tokenized_text)
            font_match_fetch = font_list[first_index:last_index]
            #print(len(tokenized_text)," Length match:",len(font_match_fetch))
            category = ''
            main_account = ''
            for j in range(len(font_match_fetch)):
                if((font_match_fetch[j]['fontname']=='BCDFEE+ABBvoice-Bold') or (font_match_fetch[j]['fontname']=='BCDGEE+ABBvoice-Bold')):
                    category = category+' '+font_match_fetch[j]['text']
                else:
                    main_account = main_account+' '+font_match_fetch[j]['text']
            main_cat.append(category.strip())
            main_account_final.append(main_account.strip())
        main_cat[0] = main_cat[0].replace("abilities:",'')    
        df['Category'] = main_cat
        df["Main Accountabilities"] = main_account_final
        df['Functional Area']       = funtional_area
        df['Job Ref']               = job_ref
        df['Version']               = version
        df['Job Family']            = job_fam
        df['Job']                   = job
        df['Typical Reporting Line']= typical
        df['Mission Statement']     = mission
        df = df.reindex(columns = ['Job Ref','Version','Functional Area','Job Family','Job','Typical Reporting Line','Mission Statement','Category','Main Accountabilities'])
        print("##############Jd Fetched Correctly:",job_ref)
    except:
        print("$$$$$$$$$$$$$Wrong Job Id",job_ref)
        column_name = ['Job Ref','Version','Functional Area','Job Family','Job','Typical Reporting Line','Mission Statement','Category','Main Accountabilities']
        df = pd.DataFrame(columns= column_name, dtype= object)
        pass
    return df
        
        
        
        
        


#Function to fetch competency details
jobs_list = pd.read_csv(r'Jobs_list.csv')
main_df = pd.DataFrame()
one_page_jd = []
for i in range(len(jobs_list)-1):
    
    jobs_list['page number'] = jobs_list['page number'].astype(int)
    pdf_file = "Global Job Structure Job Profile Manual R9_01092018_final version on 20180921.pdf"
    page_diff = jobs_list['page number'][i+1] - jobs_list['page number'][i]
    if(page_diff>0):
        df_return = second_sheet_2page(pdf_file,jobs_list['page number'][i],jobs_list['page number'][i+1],jobs_list['Job ID'][i])
        main_df = pd.concat([main_df,df_return], ignore_index=True)
    else:
        one_page_jd.append(jobs_list['Job ID'][i])
        print("$$$$$$$Single Page pdf$$$$:",jobs_list['Job ID'][i],jobs_list['page number'][i])
main_df.to_excel(r'test_2nd_sheet.xlsx')



#Function to fetch competency details
jobs_list = pd.read_csv(r'Jobs_list.csv')
jd_df = pd.DataFrame()
one_page_jd = []
pdf_file = "Global Job Structure Job Profile Manual R9_01092018_final version on 20180921.pdf"
pdf = pdfplumber.open(pdf_file)
for i in range(len(jobs_list)-1):
    jobs_list['page number'] = jobs_list['page number'].astype(int)
    page_diff = jobs_list['page number'][i+1] - jobs_list['page number'][i]
    if(page_diff>0):
        df_return = jd_repository(pdf,jobs_list['page number'][i],jobs_list['page number'][i+1],jobs_list['Job ID'][i])
        jd_df = pd.concat([jd_df,df_return], ignore_index=True)
    else:
        one_page_jd.append(jobs_list['Job ID'][i])
        print("$$$$$$$Single Page pdf$$$$:",jobs_list['Job ID'][i],jobs_list['page number'][i])

jd_df.to_excel(r'jd_description.xlsx', index = False)