import sqlite3
import pandas as pd
import googlemaps
import folium
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from Server_HSE_MasterDB.Server_HSE_MasterDB_All_Modules.Server_HSE_MasterDB_Models.Server_HSE_MasterDB_Model import get_db

DATABASE_NAME = ("./Server_HSE_MasterDB/Server_HSE_MasterDB_All_Modules/Server_HSE_MasterDB_Database/Server_HSE_MasterDB_Database.db")

def get_dashboard_InvRec():
    db = get_db()
    cursor = db.cursor()
    query = "SELECT id, EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                    HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, UnsafeAct, \
                    UnsafeCond, EmployeeInvolved, Classification, RecordableFAMARWCLTI, WCBCase, \
                    ModifiedDays, BodyPart, EquipmentNumber, CACompleted, SignOff FROM HSEIncidentLog_MASTER ORDER BY `EventDate` DESC"
    cursor.execute(query)
    return cursor.fetchmany(5)

def view_master_InvRec():
    db = get_db()
    cursor = db.cursor()
    query = "SELECT id, EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                    HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, UnsafeAct, \
                    UnsafeCond, EmployeeInvolved, Classification, RecordableFAMARWCLTI, WCBCase, \
                    ModifiedDays, BodyPart, EquipmentNumber, CACompleted, SignOff FROM HSEIncidentLog_MASTER ORDER BY `id` ASC"
    cursor.execute(query)
    return cursor.fetchall()

def insert_InvRec(EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                    HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, UnsafeAct, \
                    UnsafeCond, EmployeeInvolved, Classification, RecordableFAMARWCLTI, WCBCase, \
                    ModifiedDays, BodyPart, EquipmentNumber, CACompleted, SignOff):
    db = get_db()
    cursor = db.cursor()
    statement = "INSERT INTO HSEIncidentLog_MASTER (EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, UnsafeAct, \
                UnsafeCond, EmployeeInvolved, Classification, RecordableFAMARWCLTI, WCBCase, \
                ModifiedDays, BodyPart, EquipmentNumber, CACompleted, SignOff) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    cursor.execute(statement, [EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, 
                               HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, UnsafeAct, 
                               UnsafeCond, EmployeeInvolved, Classification, RecordableFAMARWCLTI, WCBCase, 
                               ModifiedDays, BodyPart, EquipmentNumber, CACompleted, SignOff])
    db.commit()
    return True

def front_overview_IncidentsCounts():
    conn = sqlite3.connect(DATABASE_NAME)
    Complete_df = pd.read_sql_query("select * from HSEIncidentLog_MASTER;", conn)
    Complete_df = pd.DataFrame(Complete_df)
    Complete_df['EventDate']   = pd.to_datetime(Complete_df['EventDate']).dt.strftime('%Y')

    Complete_df['EventDate']   = Complete_df.EventDate.astype (int)
    Complete_df = pd.DataFrame(Complete_df)
    x_min =(Complete_df['EventDate'].max())-5
    y_max = (Complete_df['EventDate'].max())
    Complete_df = Complete_df[(Complete_df.EventDate >= x_min) & (Complete_df.EventDate <= y_max)]

    Summary= Complete_df.groupby(['EventDate'], as_index=False).agg({"ProjName":pd.Series.nunique, "id":"count"})
    Summary   = pd.DataFrame(Summary)
    Summary['Percentage Index'] = round(100*Summary.id/Summary.id.sum(),1)
    Summary.rename(columns={'EventDate':'Event Year', "ProjName":'No of Projects','id':'No of Incidents', 'Percentage Index': 'Percentage Index'},inplace = True)
    DataFrame_HSE_IncidentsCounts = pd.DataFrame(Summary, index=None)
    return DataFrame_HSE_IncidentsCounts

def front_overview_Eventindex():
    conn = sqlite3.connect(DATABASE_NAME)
    Complete_df = pd.read_sql_query("select * from HSEIncidentLog_MASTER;", conn)
    Complete_df = pd.DataFrame(Complete_df)
    len_Complete_df = len(Complete_df)
    if len_Complete_df>0:
        Year_Days = 365.25
        Complete_df['EventDate']   = pd.to_datetime(Complete_df['EventDate']).dt.strftime('%Y')
        Complete_df['EventDate']   = Complete_df.EventDate.astype (int)
        Complete_df = pd.DataFrame(Complete_df)
        x_min =(Complete_df['EventDate'].max())-5
        y_max = (Complete_df['EventDate'].max())
        Complete_df = Complete_df[(Complete_df.EventDate >= x_min) & (Complete_df.EventDate <= y_max)]
        Numberof_incidents = len(Complete_df)
        Numberof_years= Complete_df.groupby(['EventDate'], as_index=False).count()
        Numberof_years = len(Numberof_years)
        Year_Days = 365.25
        Event_Index = round(100*(Numberof_incidents)/((Year_Days)*(Numberof_years)),1)
    else:
        Event_Index = 0

    return Event_Index

def front_overview_EmergencyCounts():
    conn = sqlite3.connect(DATABASE_NAME)
    Complete_df = pd.read_sql_query("select * from HSEIncidentLog_MASTER;", conn)
    Complete_df = pd.DataFrame(Complete_df)
    Complete_df['EventDate']   = pd.to_datetime(Complete_df['EventDate']).dt.strftime('%Y')


    Complete_df['EventDate']   = Complete_df.EventDate.astype (int)
    Complete_df = pd.DataFrame(Complete_df)
    x_min =(Complete_df['EventDate'].max())-5
    y_max = (Complete_df['EventDate'].max())
    Complete_df = Complete_df[(Complete_df.EventDate >= x_min) & (Complete_df.EventDate <= y_max)]
    
    Summary_I= Complete_df.groupby(['EventDate', 'EmergencyLevel'], as_index=False).agg({"id":"count"})
    Summary_I.rename(columns={'EventDate':'Year ⇩', 'EmergencyLevel': 'Emergency ⇨', 'id':'No of Incidents'},inplace = True)
    Summary_I = pd.DataFrame(Summary_I, index=None)

    Summary_M= Summary_I.groupby(['Year ⇩'], as_index=False).agg({"No of Incidents":"sum"})
    Summary_M.rename(columns={'No of Incidents':'Incident Per Year'},inplace = True)
    Summary_M = pd.DataFrame(Summary_M, index=None)

    Summary_F = pd.merge(Summary_I, Summary_M, how='left', on=['Year ⇩'])
    Summary_F['Percent Per Year'] = round(100*(Summary_F['No of Incidents'])/(Summary_F['Incident Per Year']),1)
    Summary_F  = Summary_F.loc[:,['Year ⇩','Emergency ⇨','No of Incidents','Percent Per Year']]
    
    DataFrame_HSE_EmergencyCounts = pd.DataFrame(Summary_F, index=None)
    DataFrame_HSE_EmergencyCounts=pd.pivot_table(DataFrame_HSE_EmergencyCounts, values=["No of Incidents", 'Percent Per Year'], index=["Year ⇩"], columns=["Emergency ⇨"])
    DataFrame_HSE_EmergencyCounts = pd.DataFrame(DataFrame_HSE_EmergencyCounts)

    return DataFrame_HSE_EmergencyCounts

def front_overview_EmergencyPlots_Color(a):
    if a == 'High ':
        return 'red'
    elif a == 'High':
        return 'red'
    elif a == 'Med':
        return 'yellow'
    elif a == 'Low':
        return 'green'
    else:
        return 'blue'

def front_overview_EmergencyPlots():
    conn = sqlite3.connect(DATABASE_NAME)
    Complete_df = pd.read_sql_query("select * from HSEIncidentLog_MASTER;", conn)
    Complete_df = pd.DataFrame(Complete_df)
    Complete_df['EventDate']   = pd.to_datetime(Complete_df['EventDate']).dt.strftime('%Y')

    Complete_df['EventDate']   = Complete_df.EventDate.astype (int)
    Complete_df = pd.DataFrame(Complete_df)
    x_min =(Complete_df['EventDate'].max())-5
    y_max = (Complete_df['EventDate'].max())
    Complete_df = Complete_df[(Complete_df.EventDate >= x_min) & (Complete_df.EventDate <= y_max)]
    
    Summary_I= Complete_df.groupby(['EventDate', 'EmergencyLevel'], as_index=False).agg({"id":"count"})
    Summary_I.rename(columns={'EventDate':'Year', 'EmergencyLevel': 'Emergency', 'id':'No of Incidents'},inplace = True)
    Summary_I = pd.DataFrame(Summary_I, index=None)

    Summary_M= Summary_I.groupby(['Year'], as_index=False).agg({"No of Incidents":"sum"})
    Summary_M.rename(columns={'No of Incidents':'Incident Per Year'},inplace = True)
    Summary_M = pd.DataFrame(Summary_M, index=None)

    Summary_F = pd.merge(Summary_I, Summary_M, how='left', on=['Year'])
    DataFrame_HSE_EmergencyPlots = pd.DataFrame(Summary_F)

    DataFrame_HSE_EmergencyPlots['Year']   = DataFrame_HSE_EmergencyPlots.Year.astype (str)
    DataFrame_HSE_EmergencyPlots['Emergency_Color']   = (DataFrame_HSE_EmergencyPlots['Emergency'].apply(front_overview_EmergencyPlots_Color))
    DataFrame_HSE_EmergencyPlots['Year_Emergency'] = DataFrame_HSE_EmergencyPlots[['Year', 'Emergency']].agg(';'.join, axis=1)
    DataFrame_HSE_EmergencyPlots = pd.DataFrame(DataFrame_HSE_EmergencyPlots)
    DataFrame_HSE_EmergencyPlots = DataFrame_HSE_EmergencyPlots. filter(['Year_Emergency', 'Year', 'Emergency', 'No of Incidents', 'Emergency_Color']).values
    return DataFrame_HSE_EmergencyPlots

def Total_MasterDB_Incident():
    conn = sqlite3.connect(DATABASE_NAME)
    Complete_df = pd.read_sql_query("select * from HSEIncidentLog_MASTER;", conn)
    Complete_df = pd.DataFrame(Complete_df)
    Total_Incident_Count = Complete_df['id'].count()
    return Total_Incident_Count

def LastfiveYears_Incident():
    conn = sqlite3.connect(DATABASE_NAME)
    Complete_df = pd.read_sql_query("select * from HSEIncidentLog_MASTER;", conn)
    Complete_df = pd.DataFrame(Complete_df)
    Complete_df['EventDate']   = pd.to_datetime(Complete_df['EventDate']).dt.strftime('%Y')
    Complete_df['EventDate']   = Complete_df.EventDate.astype (int)
    Complete_df = pd.DataFrame(Complete_df)
    x_min =(Complete_df['EventDate'].max())-5
    y_max = (Complete_df['EventDate'].max())
    Complete_df = Complete_df[(Complete_df.EventDate >= x_min) & (Complete_df.EventDate <= y_max)]
    Complete_df = pd.DataFrame(Complete_df)
    LastfiveYears_MasterDB_Incident = len(Complete_df)
    return LastfiveYears_MasterDB_Incident

def submitCSVToMasterDB(df):
    conn = sqlite3.connect(DATABASE_NAME)
    df.to_sql('HSEIncidentLog_MASTER', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()
    return True

def update_InvRec (id, EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                    HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, \
                    UnsafeAct, UnsafeCond, EmployeeInvolved, Classification, \
                    RecordableFAMARWCLTI, WCBCase, ModifiedDays, BodyPart, \
                    EquipmentNumber, CACompleted, SignOff):
    db = get_db()
    cursor = db.cursor()
    statement = "UPDATE HSEIncidentLog_MASTER SET EventDate = ?, ProjName = ?, ProjNum = ? , ProjLoc =?, EmergencyLevel=?,\
        HSEAdvisorInvestigator = ?, HSEIncidentDetails = ?, Client = ? , CauseAnalysis =?, UnsafeAct=?,\
        UnsafeCond = ?, EmployeeInvolved = ?, Classification = ? , RecordableFAMARWCLTI =?, WCBCase=?,\
        ModifiedDays = ?, BodyPart = ?, EquipmentNumber = ? , CACompleted =?, SignOff=? WHERE id = ?"
    cursor.execute(statement, [EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                    HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, \
                    UnsafeAct, UnsafeCond, EmployeeInvolved, Classification, \
                    RecordableFAMARWCLTI, WCBCase, ModifiedDays, BodyPart, \
                    EquipmentNumber, CACompleted, SignOff, id])
    db.commit()
    return True

def delete_InvRec(id):
    db = get_db()
    cursor = db.cursor()
    statement = "DELETE FROM HSEIncidentLog_MASTER WHERE id = ?"
    cursor.execute(statement, [id])
    db.commit()
    return True

def search_InvRec ( id = "" , EventDate = "", ProjName = "", ProjNum = "", ProjLoc = "", EmergencyLevel = "", \
                    HSEAdvisorInvestigator = "", HSEIncidentDetails = "", Client = "", CauseAnalysis= "", \
                    UnsafeAct ="", UnsafeCond = "", EmployeeInvolved = "", Classification = "",\
                    RecordableFAMARWCLTI = "", WCBCase = "", ModifiedDays = "", BodyPart = "",\
                    EquipmentNumber = "", CACompleted = "", SignOff = ""):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * FROM HSEIncidentLog_MASTER WHERE id = ? COLLATE NOCASE OR EventDate = ? COLLATE NOCASE OR ProjName = ? COLLATE NOCASE OR ProjNum = ? COLLATE NOCASE OR \
                ProjLoc = ? COLLATE NOCASE OR EmergencyLevel = ? COLLATE NOCASE OR HSEAdvisorInvestigator = ? COLLATE NOCASE OR HSEIncidentDetails = ? COLLATE NOCASE OR \
                Client = ? COLLATE NOCASE OR CauseAnalysis = ? COLLATE NOCASE OR UnsafeAct =? COLLATE NOCASE OR UnsafeCond = ? COLLATE NOCASE OR\
                EmployeeInvolved = ? COLLATE NOCASE OR Classification = ? COLLATE NOCASE OR RecordableFAMARWCLTI = ? COLLATE NOCASE OR WCBCase = ? COLLATE NOCASE OR \
                ModifiedDays = ? COLLATE NOCASE OR BodyPart = ? COLLATE NOCASE OR EquipmentNumber = ? COLLATE NOCASE OR CACompleted = ? COLLATE NOCASE OR SignOff = ? COLLATE NOCASE"
    
    cursor.execute(statement, [id, EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                    HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, \
                    UnsafeAct, UnsafeCond, EmployeeInvolved, Classification, \
                    RecordableFAMARWCLTI, WCBCase, ModifiedDays, BodyPart, \
                    EquipmentNumber, CACompleted, SignOff])
    
    rows=cursor.fetchall()
    return rows

def PopulateEventBreakdownBy_Year(year= ""):
    if((year)!=0):
        EndYearMonth   = 12
        BeginYearMonth = 1
        EndYearDay     = 31
        BeginYearDay   = 1
        Year_Get_Breakdown  = int(year)            
        Year_Get_End        = datetime.date(Year_Get_Breakdown , int(EndYearMonth), int(EndYearDay))
        Year_Get_Start      = datetime.date(Year_Get_Breakdown , int(BeginYearMonth), int(BeginYearDay))

        con = sqlite3.connect(DATABASE_NAME)
        Complete_df = pd.read_sql_query("select * from HSEIncidentLog_MASTER ORDER BY `id` ASC ;", con)
        data = pd.DataFrame(Complete_df)
        data['EventDate']   = pd.to_datetime(data['EventDate']).dt.strftime('%Y-%m-%d')
        Year_Get_End   = pd.to_datetime(Year_Get_End).strftime('%Y-%m-%d')
        Year_Get_Start = pd.to_datetime(Year_Get_Start).strftime('%Y-%m-%d')            
        data = data[(data['EventDate'] >= Year_Get_Start) & (data['EventDate'] <= Year_Get_End)]          
        data = data.reset_index(drop=True)
        TotalEntries = len(data)

        ## Generationing Classification Report
        HSE_ClassificationDF     = pd.DataFrame(data)
        HSE_ClassificationReport = HSE_ClassificationDF.groupby(['Classification'], as_index=False).id.count()
        HSE_ClassificationReport = pd.DataFrame(HSE_ClassificationReport)
        HSE_ClassificationReport.rename(columns={'Classification':'Event Classification', 'id':'Count'},inplace = True)
        HSE_ClassificationReport = HSE_ClassificationReport.reset_index(drop=True)
        HSE_ClassificationReport.sort_values(by=['Count'], ascending=False, inplace=True)
        HSE_ClassificationReport  = HSE_ClassificationReport.reset_index(drop=True)
        HSE_ClassificationReport['Percent'] = ((HSE_ClassificationReport['Count'] / HSE_ClassificationReport['Count'].sum())*100).round(1)
        HSE_ClassificationReport     = pd.DataFrame(HSE_ClassificationReport, index=None)

        ## Generationing Crew Manager Report
        HSE_CrewManagerDF        = pd.DataFrame(data)
        HSE_CrewManagerDFReport  = HSE_CrewManagerDF.groupby(['HSEAdvisorInvestigator','ProjNum'], as_index=False).id.count()
        HSE_CrewManagerDFReport  = pd.DataFrame(HSE_CrewManagerDFReport)
        HSE_CrewManagerDFReport.rename(columns={'HSEAdvisorInvestigator':'Manager Name', 'ProjNum':'Project Number', 'id':'Count'},inplace = True)
        HSE_CrewManagerDFReport  = HSE_CrewManagerDFReport.reset_index(drop=True)
        HSE_CrewManagerDFReport.sort_values(by=['Count'], ascending=False, inplace=True)
        HSE_CrewManagerDFReport  = HSE_CrewManagerDFReport.reset_index(drop=True)
        HSE_CrewManagerDFReport['Percent'] = ((HSE_CrewManagerDFReport['Count'] / HSE_CrewManagerDFReport['Count'].sum())*100).round(1)
        HSE_CrewManagerDFReport     = pd.DataFrame(HSE_CrewManagerDFReport, index=None)


        ## Generationing Monthly Breakdown Report
        HSE_MonthlyBreakdown         = pd.DataFrame(data)
        HSE_MonthlyBreakdown['EventDate'] = pd.to_datetime(HSE_MonthlyBreakdown['EventDate']).dt.strftime('%Y-%m')
        HSE_MonthlyBreakdownReport   = HSE_MonthlyBreakdown.groupby(['EventDate'], as_index=False).id.count()
        HSE_MonthlyBreakdownReport.rename(columns={'EventDate':'EventByMonth', 'id':'Count'},inplace = True)

        def trans_Month(y):
            if y == (str(Year_Get_Breakdown) + '-' + '01'):
                return "January"

            elif y == (str(Year_Get_Breakdown) + '-' + '02'):
                return "February"

            elif y == (str(Year_Get_Breakdown) + '-' + '03'):
                return "March"

            elif y == (str(Year_Get_Breakdown) + '-' + '04'):
                return "April"

            elif y == (str(Year_Get_Breakdown) + '-' + '05'):
                return "May"

            elif y == (str(Year_Get_Breakdown) + '-' + '06'):
                return "June"

            elif y == (str(Year_Get_Breakdown) + '-' + '07'):
                return "July"

            elif y == (str(Year_Get_Breakdown) + '-' + '08'):
                return "August"

            elif y == (str(Year_Get_Breakdown) + '-' + '09'):
                return "September"

            elif y == (str(Year_Get_Breakdown) + '-' + '10'):
                return "October"

            elif y == (str(Year_Get_Breakdown) + '-' + '11'):
                return "November"

            elif y == (str(Year_Get_Breakdown) + '-' + '12'):
                return "December"

            else:
                return y

        HSE_MonthlyBreakdownReport['Event By Month'] = HSE_MonthlyBreakdownReport['EventByMonth'].apply(trans_Month)
        HSE_MonthlyBreakdownReport                   = HSE_MonthlyBreakdownReport.loc[:,['Event By Month','Count']]
        HSE_MonthlyBreakdownReport                   = HSE_MonthlyBreakdownReport.reset_index(drop=True)
        HSE_MonthlyBreakdownReport['Percent']        =((HSE_MonthlyBreakdownReport['Count'] / HSE_MonthlyBreakdownReport['Count'].sum())*100).round(1)
        HSE_MonthlyBreakdownReport                   = pd.DataFrame(HSE_MonthlyBreakdownReport, index=None)

        ## Generationing Job Report
        HSE_JobNameDF          = pd.DataFrame(data)
        HSE_JobNameDF          = HSE_JobNameDF.groupby(['ProjName', 'ProjNum'], as_index=False).id.count()
        HSE_HSE_JobNameReport  = pd.DataFrame(HSE_JobNameDF)
        HSE_HSE_JobNameReport.rename(columns={'ProjName':'Project Name', 'ProjNum':'Project Number','id':'Count'},inplace = True)
        HSE_HSE_JobNameReport  = HSE_HSE_JobNameReport.reset_index(drop=True)                
        HSE_HSE_JobNameReport.sort_values(by=['Count'], ascending=False, inplace=True)
        HSE_HSE_JobNameReport  = HSE_HSE_JobNameReport.reset_index(drop=True)
        HSE_HSE_JobNameReport['Percent'] =((HSE_HSE_JobNameReport['Count'] / HSE_HSE_JobNameReport['Count'].sum())*100).round(1)
        HSE_HSE_JobNameReport            = pd.DataFrame(HSE_HSE_JobNameReport, index=None)

        ## Generationing Recordable Report
        HSE_RecordableDF     = pd.DataFrame(data)
        HSE_RecordablReport  = HSE_RecordableDF.groupby(['RecordableFAMARWCLTI','WCBCase'], as_index=False).id.count()
        HSE_RecordablReport  = pd.DataFrame(HSE_RecordablReport)
        HSE_RecordablReport.rename(columns={'RecordableFAMARWCLTI':'Recordable Index', 'WCBCase':'WCB Case', 'id':'Count'},inplace = True)
        HSE_RecordablReport  = HSE_RecordablReport.reset_index(drop=True)
        HSE_RecordablReport.sort_values(by=['Count'], ascending=False, inplace=True)
        HSE_RecordablReport  = HSE_RecordablReport.reset_index(drop=True)
        HSE_RecordablReport  = pd.DataFrame(HSE_RecordablReport, index=None)

        ## Generationing RiskLevel Report
        HSE_RiskLevelDF      = pd.DataFrame(data)
        HSE_RiskLevelDF      = HSE_RiskLevelDF.groupby(['EmergencyLevel'], as_index=False).id.count()
        HSE_RiskLevelReport  = pd.DataFrame(HSE_RiskLevelDF)
        HSE_RiskLevelReport.rename(columns={'EmergencyLevel':'Emergency Level', 'id':'Count'},inplace = True)
        HSE_RiskLevelReport  = HSE_RiskLevelReport.reset_index(drop=True)
        HSE_RiskLevelReport['Percent'] = ((HSE_RiskLevelReport['Count'] / HSE_RiskLevelReport['Count'].sum())*100).round(1)
        HSE_RiskLevelReport.sort_values(by=['Count'], ascending=False, inplace=True)
        HSE_RiskLevelReport  = HSE_RiskLevelReport.reset_index(drop=True)
        HSE_RiskLevelReport  = pd.DataFrame(HSE_RiskLevelReport, index=None)

        ## Generationing Unsafe Act Report
        HSE_UnsafeActDF      = pd.DataFrame(data)
        HSE_UnsafeActDF      = HSE_UnsafeActDF.groupby(['UnsafeAct','UnsafeCond'], as_index=False).id.count()
        HSE_UnsafeActReport  = pd.DataFrame(HSE_UnsafeActDF)
        HSE_UnsafeActReport.rename(columns={'UnsafeAct':'Unsafe Act', 'UnsafeCond': 'Unsafe Condition', 'id':'Count'},inplace = True)
        HSE_UnsafeActReport  = HSE_UnsafeActReport.reset_index(drop=True)
        HSE_UnsafeActReport['Percent'] = ((HSE_UnsafeActReport['Count'] / HSE_UnsafeActReport['Count'].sum())*100).round(1)
        HSE_UnsafeActReport.sort_values(by=['Count'], ascending=False, inplace=True)
        HSE_UnsafeActReport  = HSE_UnsafeActReport.reset_index(drop=True)
        HSE_UnsafeActReport  = pd.DataFrame(HSE_UnsafeActReport, index=None)
                
        return TotalEntries, HSE_ClassificationReport, HSE_CrewManagerDFReport, HSE_MonthlyBreakdownReport, HSE_HSE_JobNameReport, HSE_RecordablReport, HSE_RiskLevelReport,HSE_UnsafeActReport
                
def ViewCrewReportBy_Year(year= ""):
    if((year)!=0):
        EndYearMonth   = 12
        BeginYearMonth = 1
        EndYearDay     = 31
        BeginYearDay   = 1
        Year_Get         = int(year)           
        Year_Get_End     = datetime.date(Year_Get , int(EndYearMonth), int(EndYearDay))
        Year_Get_Start   = datetime.date(Year_Get , int(BeginYearMonth), int(BeginYearDay))
        
        con = sqlite3.connect(DATABASE_NAME)
        Complete_df = pd.read_sql_query("select * from HSEIncidentLog_MASTER ORDER BY `id` ASC ;", con)
        data = pd.DataFrame(Complete_df)
        data['EventDate']   = pd.to_datetime(data['EventDate']).dt.strftime('%Y-%m-%d')
        Year_Get_End   = pd.to_datetime(Year_Get_End).strftime('%Y-%m-%d')
        Year_Get_Start = pd.to_datetime(Year_Get_Start).strftime('%Y-%m-%d')            
        data = data[(data['EventDate'] >= Year_Get_Start) & (data['EventDate'] <= Year_Get_End)]          
        data = data.reset_index(drop=True)
        TotalEntries = len(data)      
        ViewJobReportBy_Year_DF     = pd.DataFrame(data, index=None)
        ViewJobReportBy_Year_DF_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','Classification'], as_index=False).agg({"id":"count"})
        ViewJobReportBy_Year_DF_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
        'Classification':'Classification', 'id':'No of Classified Incidents'},inplace = True)            
        ViewJobReportBy_Year_DF_Report = ViewJobReportBy_Year_DF_Report.reset_index(drop=True)
        ViewJobReportBy_Year_DF_Report  = pd.DataFrame(ViewJobReportBy_Year_DF_Report, index=None)    
        ViewJobReportBy_Year_DF_Report=pd.pivot_table(ViewJobReportBy_Year_DF_Report, values=["No of Classified Incidents"], index=['Project Name','Project Number','Project Location'], columns=["Classification"], fill_value = 0)
        ViewJobReportBy_Year_DF_Report = pd.DataFrame(ViewJobReportBy_Year_DF_Report)

        ViewJobRecordable_By_Year_DF_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','RecordableFAMARWCLTI'], as_index=False).agg({"id":"count"})
        ViewJobRecordable_By_Year_DF_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location', 
        'RecordableFAMARWCLTI':'Recordable', 'id':'No of Recordable Incidents'},inplace = True)            
        ViewJobRecordable_By_Year_DF_Report = ViewJobRecordable_By_Year_DF_Report.reset_index(drop=True)
        ViewJobRecordable_By_Year_DF_Report  = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report, index=None)    
        ViewJobRecordable_By_Year_DF_Report=pd.pivot_table(ViewJobRecordable_By_Year_DF_Report, values=["No of Recordable Incidents"], index=['Project Name','Project Number','Project Location'], columns=["Recordable"], fill_value = 0)
        ViewJobRecordable_By_Year_DF_Report = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report)            
        
        CrewTotal_WCB_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','WCBCase'], as_index=False).agg({"id":"count"})
        CrewTotal_WCB_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
                                                'WCBCase':'WCBCase', 'id':'No of WCB Incidents'},inplace = True)            
        CrewTotal_WCB_Report  = CrewTotal_WCB_Report.reset_index(drop=True)
        CrewTotal_WCB_Report = pd.DataFrame(CrewTotal_WCB_Report , index=None)
        CrewTotal_WCB_Report=pd.pivot_table(CrewTotal_WCB_Report, values=["No of WCB Incidents"], index=['Project Name','Project Number','Project Location'], columns=["WCBCase"], fill_value = 0)
        CrewTotal_WCB_Report = pd.DataFrame(CrewTotal_WCB_Report)

        CrewTotal_UnsafeAct_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','UnsafeAct','UnsafeCond'], as_index=False).agg({"id":"count"})
        CrewTotal_UnsafeAct_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
                                                'UnsafeAct':'UnsafeAct', 'UnsafeCond':'UnsafeCond', 'id':'No of UnsafeAct Incidents'},inplace = True)            
        CrewTotal_UnsafeAct_Report  = CrewTotal_UnsafeAct_Report.reset_index(drop=True)
        CrewTotal_UnsafeAct_Report = pd.DataFrame(CrewTotal_UnsafeAct_Report, index=None)
        CrewTotal_UnsafeAct_Report=pd.pivot_table(CrewTotal_UnsafeAct_Report, values=["No of UnsafeAct Incidents"], index=['Project Name','Project Number','Project Location'],
        columns=["UnsafeAct", "UnsafeCond"], fill_value = 0)
        CrewTotal_UnsafeAct_Report = pd.DataFrame(CrewTotal_UnsafeAct_Report)

        return TotalEntries, ViewJobReportBy_Year_DF_Report, ViewJobRecordable_By_Year_DF_Report, CrewTotal_WCB_Report, CrewTotal_UnsafeAct_Report

def submitProjectMapToMasterDB():
    conn = sqlite3.connect(DATABASE_NAME)
    Complete_df = pd.read_sql_query("select * from HSEIncidentLog_MASTER;", conn)
    Complete_df = pd.DataFrame(Complete_df)
    Complete_df  = Complete_df.loc[:,['id','EventDate', 'ProjName', 'ProjNum', 'ProjLoc']]
    Complete_df['EventDate']   = pd.to_datetime(Complete_df['EventDate']).dt.strftime('%Y')
    Complete_df = pd.DataFrame(Complete_df)
    Complete_df_1  = Complete_df.loc[:,['EventDate', 'ProjName', 'ProjNum', 'ProjLoc']]
    grouped_Complete_df_1 = Complete_df_1.groupby(['ProjName', 'ProjNum', 'ProjLoc'], as_index=False).agg({"EventDate": "unique"})
    grouped_Complete_df_1 = grouped_Complete_df_1.explode('EventDate')
    grouped_Complete_df_1 = pd.DataFrame(grouped_Complete_df_1, index=None)
    Complete_df_2  = Complete_df.loc[:,['ProjName','id']]
    grouped_Complete_df_2 = Complete_df_2.groupby(['ProjName'], as_index=False).agg({"id":"count"})
    grouped_Complete_df_2 = pd.DataFrame(grouped_Complete_df_2, index=None)
    ProjectMap_DF    = pd.merge(grouped_Complete_df_1, grouped_Complete_df_2,
                                        how='inner', on = ['ProjName'])
    ProjectMap_DF   = ProjectMap_DF.reset_index(drop=True)
    ProjectMap_DF.rename(columns={'ProjName':'ProjectName', 'ProjNum': 'ProjectNumber', 'ProjLoc':'ProjectLocation', 'EventDate':'EventYear', 'id':'Incidents_Count'},inplace = True)
    ProjectMap_DF = pd.DataFrame(ProjectMap_DF, index=None)
    AUTH_KEY = 'AIzaSyAOeYNc0Pbycx4Bv7tLpAgrOsZpD2tU5M4'
    gmaps_key = googlemaps.Client(AUTH_KEY)
    geocode_result =gmaps_key.geocode(ProjectMap_DF.iat[0,2])
    ProjectMap_DF["Latitude"]=""
    ProjectMap_DF["Longitude"]=""
    for i in range(0, len(ProjectMap_DF),1):
        geocode_result =gmaps_key.geocode(ProjectMap_DF.iat[i,2])
        try:
            lat =geocode_result[0]["geometry"]["location"]["lat"]
            lon =geocode_result[0]["geometry"]["location"]["lng"]
            ProjectMap_DF.iat[i,ProjectMap_DF.columns.get_loc("Latitude")] = lat
            ProjectMap_DF.iat[i,ProjectMap_DF.columns.get_loc("Longitude")] =lon
        except:
            lat =None
            lon=None       
    ProjectMap_DF.to_sql('HSEIncidentLog_PROJECTMAP', conn, if_exists='replace', index_label='Proj_id')
    conn.commit()
    conn.close()
    
def populateMapDataBy_Year(EventYear=""):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT * FROM HSEIncidentLog_PROJECTMAP WHERE EventYear = ?"
    cursor.execute(statement, [EventYear])
    rows=cursor.fetchall()
    return rows

def update_ProjMapRec (Proj_id, ProjectName, ProjectNumber, ProjectLocation, EventYear, Incidents_Count, \
                    Latitude, Longitude):
    db = get_db()
    cursor = db.cursor()
    statement = "UPDATE HSEIncidentLog_PROJECTMAP SET ProjectName = ?, ProjectNumber = ?, ProjectLocation = ? , EventYear =?, Incidents_Count=?,\
        Latitude = ?, Longitude = ? WHERE Proj_id = ?"
    cursor.execute(statement, [ProjectName, ProjectNumber, ProjectLocation, EventYear, Incidents_Count, \
                    Latitude, Longitude, Proj_id])
    db.commit()
    return True

def delete_ProjMapRec(Proj_id):
    db = get_db()
    cursor = db.cursor()
    statement = "DELETE FROM HSEIncidentLog_PROJECTMAP WHERE Proj_id = ?"
    cursor.execute(statement, [Proj_id])
    db.commit()
    return True

def Map_Color(a):
    if a in range(0, 6):
        return 'Low'
    elif a in range(6, 8):
        return 'Med'
    else:
        return 'High'

def viewMapBy_Year(EventYear=""):
    Year_Get         = str(EventYear) 
    conn = sqlite3.connect(DATABASE_NAME)
    statement = "SELECT * FROM HSEIncidentLog_PROJECTMAP"
    Complete_df = pd.read_sql_query(statement, conn)
    Complete_df = pd.DataFrame(Complete_df)

    Complete_df = Complete_df[(Complete_df['EventYear']== Year_Get)]          
    Complete_df = Complete_df.reset_index(drop=True)
    Complete_df['Map_Color'] = Complete_df['Incidents_Count'].apply(Map_Color)
    colors = {'High' : 'darkred', 'Med' : 'darkblue', 'Low' : 'darkgreen'}
    folium_map = folium.Map(location=[51.044308, -114.063087], zoom_start=6)

    Complete_df.apply(lambda row:folium.CircleMarker(location=[row["Latitude"], row["Longitude"]], 
                    radius=10, fill_color=colors[row['Map_Color']], fill_opacity=1,tooltip=row['Incidents_Count'], popup=row['ProjectName'])
                    .add_to(folium_map), axis=1)
    conn.commit()
    conn.close()
    print(Complete_df)
    return folium_map

def ViewCountryReportBy_Year(year= ""):
    if((year)!=0):
        EndYearMonth   = 12
        BeginYearMonth = 1
        EndYearDay     = 31
        BeginYearDay   = 1
        Year_Get         = int(year)           
        Year_Get_End     = datetime.date(Year_Get , int(EndYearMonth), int(EndYearDay))
        Year_Get_Start   = datetime.date(Year_Get , int(BeginYearMonth), int(BeginYearDay))
        
        con = sqlite3.connect(DATABASE_NAME)
        Complete_df = pd.read_sql_query("select * from HSEIncidentLog_MASTER ORDER BY `id` ASC ;", con)
        data = pd.DataFrame(Complete_df)
        data['EventDate']   = pd.to_datetime(data['EventDate']).dt.strftime('%Y-%m-%d')
        Year_Get_End   = pd.to_datetime(Year_Get_End).strftime('%Y-%m-%d')
        Year_Get_Start = pd.to_datetime(Year_Get_Start).strftime('%Y-%m-%d')            
        data = data[(data['EventDate'] >= Year_Get_Start) & (data['EventDate'] <= Year_Get_End)]          
        data = data.reset_index(drop=True)
        TotalEntries = len(data)      
        ViewCountryReport_Year_DF     = pd.DataFrame(data, index=None)
        ViewCountryReport_Year_DF[['City','Province', 'Country']] = ViewCountryReport_Year_DF.ProjLoc.str.split(",",expand=True,)

        ViewCountryReport  = ViewCountryReport_Year_DF.groupby(['Country', 'Province'], as_index=False).agg({"id":"count"})
        ViewCountryReport.rename(columns = {'Country': 'Country', 'Province':'Province/State/Division',
        'id':'No of HSE Incidents'},inplace = True)  
        ViewCountryReport = ViewCountryReport.reset_index(drop=True)
        ViewCountryReport['Event Percentage (%)'] = ((ViewCountryReport['No of HSE Incidents'] / ViewCountryReport['No of HSE Incidents'].sum())*100).round(1)
        ViewCountryReport         = pd.DataFrame(ViewCountryReport)
        ViewCountryReport.sort_values(by=['Country', 'No of HSE Incidents'], ascending=False, inplace=True)
        ViewCountryReport = ViewCountryReport.reset_index(drop=True) 
        ViewCountryReport = pd.DataFrame(ViewCountryReport)
        Index_Length      = len(ViewCountryReport)+1
        ViewCountryReport['Event Index'] = pd.Series(range(1,Index_Length))

        ViewCountryReport = ViewCountryReport.loc[:,
                                    ['Event Index','Country','Province/State/Division', 'No of HSE Incidents', 'Event Percentage (%)']]


        HSE_EmergencyLevelDF_Pivot  = pd.DataFrame(ViewCountryReport_Year_DF, index=None)
        HSE_EmergencyLevelDF_Pivot  = HSE_EmergencyLevelDF_Pivot.groupby(['Country', 'Province','EmergencyLevel'], as_index=False).agg({"id":"count"})
        HSE_EmergencyLevelDF_Pivot.rename(columns = {'Country': 'Country', 'Province':'Province/State/Division', 'EmergencyLevel': 'Emergency Level', 
        'id':'No of HSE Incidents'},inplace = True)
        HSE_EmergencyLevelDF_Pivot = HSE_EmergencyLevelDF_Pivot.reset_index(drop=True)
        HSE_EmergencyLevelDF_Pivot['Event Percentage (%)'] = ((HSE_EmergencyLevelDF_Pivot['No of HSE Incidents'] / HSE_EmergencyLevelDF_Pivot['No of HSE Incidents'].sum())*100).round(1)
        HSE_EmergencyLevelDF_Pivot         = pd.DataFrame(HSE_EmergencyLevelDF_Pivot)
        HSE_EmergencyLevelDF_Pivot.sort_values(by=['Country', 'No of HSE Incidents'], ascending=False, inplace=True)
        HSE_EmergencyLevelDF_Pivot = HSE_EmergencyLevelDF_Pivot.reset_index(drop=True) 
        HSE_EmergencyLevelDF_Pivot = pd.DataFrame(HSE_EmergencyLevelDF_Pivot)
        HSE_EmergencyLevelDF_Pivot=pd.pivot_table(HSE_EmergencyLevelDF_Pivot, 
        values=["No of HSE Incidents", "Event Percentage (%)"], index=['Country','Province/State/Division'], columns=["Emergency Level"], fill_value = 0)
        HSE_EmergencyLevelDF_Pivot = pd.DataFrame(HSE_EmergencyLevelDF_Pivot)


        ViewCountryReport_Plot  = ViewCountryReport_Year_DF.groupby(['Country'], as_index=False).agg({"id":"count"})
        ViewCountryReport_Plot.rename(columns = {'Country': 'Country', 
        'id':'No of HSE Incidents'},inplace = True)  
        ViewCountryReport_Plot = ViewCountryReport_Plot.reset_index(drop=True)
        ViewCountryReport_Plot = pd.DataFrame(ViewCountryReport_Plot)

        return ViewCountryReport, TotalEntries, HSE_EmergencyLevelDF_Pivot, ViewCountryReport_Plot

