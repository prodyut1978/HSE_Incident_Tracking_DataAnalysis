import sqlite3
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from Server_HSE_MasterDB.Server_HSE_MasterDB_All_Modules.Server_HSE_MasterDB_Models.Server_HSE_MasterDB_Model import get_db

DATABASE_NAME = ("./Server_HSE_MasterDB/Server_HSE_MasterDB_All_Modules/Server_HSE_MasterDB_Database/Server_HSE_MasterDB_Database.db")

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
def project_report_classificationPlots_Color(a):
    if a == 'Community':
        return 'red'
    elif a == 'Equipment':
        return 'green'
    elif a == 'Health':
        return 'yellow'
    elif a == 'Near Miss':
        return 'orange'
    elif a == 'Non work related':
        return 'purple'
    elif a == 'Environment':
        return 'brown'
    else:
        return 'blue'
def project_report_recordablePlots_Color(a):
    if a == 'FT - Fatal':
        return 'red'
    elif a == 'LTI - Lost Time Injury':
        return 'orange'
    elif a == 'MA - Medical Aid':
        return 'yellow'
    elif a == 'RWC - Restricted Work Case':
        return 'blue'
    elif a == 'FA - First Aid':
        return 'green'
    elif a == 'Non-Recordable':
        return 'brown'
    else:
        return 'blue'
def project_report_WCB_Color(a):
    if a == 'Yes':
        return 'red'
    elif a == 'No':
        return 'green'
    else:
        return 'blue'
def project_report_UnsafeAct_Cond_Color(a):   
    if a == 'Yes':
        return 'red'
    elif a == 'No':
        return 'green'
    else:
        return 'blue'

def Annual_EventSummary(year= ""):
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

        ## Generationing Recordable Report
        HSE_RecordableDF     = pd.DataFrame(data)
        HSE_RecordableDF     = HSE_RecordableDF.groupby(['RecordableFAMARWCLTI'], as_index=False).id.count()        
        HSE_RecordableDF.rename(columns={'RecordableFAMARWCLTI':'HSE Recordable Event', 'id':'Event Count'},inplace = True)
        HSE_RecordableDF  = HSE_RecordableDF.reset_index(drop=True)
        HSE_RecordableDF['Event Percentage (%)'] = ((HSE_RecordableDF['Event Count'] / HSE_RecordableDF['Event Count'].sum())*100).round(1)
        HSE_RecordablReport  = pd.DataFrame(HSE_RecordableDF)

        RecList   = ["Non-Recordable", "FA - First Aid", "MA - Medical Aid", "RWC - Restricted Work Case", "LTI - Lost Time Injury", "FT - Fatal"]
        RecListDF = pd.DataFrame({'HSE Recordable Event': RecList})
        RecListDF.sort_values(by=['HSE Recordable Event'],  inplace=True)
        RecListDF  = RecListDF.reset_index(drop=True)
        HSE_RecordablReport_Merge = pd.merge(HSE_RecordablReport, RecListDF, how='outer', on=['HSE Recordable Event','HSE Recordable Event'])
        fillZero = int(0)

        HSE_RecordablReport_Merge["Event Count"].fillna(fillZero, inplace = True)
        HSE_RecordablReport_Merge["Event Percentage (%)"].fillna(fillZero, inplace = True)
        HSE_RecordablReport_Merge['Event Count'] = (HSE_RecordablReport_Merge.loc[:,['Event Count']]).astype(int)
        HSE_RecordablReport_Merge         = pd.DataFrame(HSE_RecordablReport_Merge)
        HSE_RecordablReport_Merge.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_RecordablReport_Merge = HSE_RecordablReport_Merge.reset_index(drop=True) 
        HSE_RecordablReport_Merge = pd.DataFrame(HSE_RecordablReport_Merge) 
        Index_Length_Recordable           = len(HSE_RecordablReport_Merge)+1
        HSE_RecordablReport_Merge['Event Index'] = pd.Series(range(1,Index_Length_Recordable))
        HSE_RecordablReport_Merge = HSE_RecordablReport_Merge.loc[:,
                                    ['Event Index','HSE Recordable Event','Event Count','Event Percentage (%)']]
        HSE_RecordablReport_Merge                          = HSE_RecordablReport_Merge.reset_index(drop=True)
        HSE_RecordablReport_Merge                          = pd.DataFrame(HSE_RecordablReport_Merge)

        # ## Generationing Classification Report
        HSE_ClassificationDF     = pd.DataFrame(data)
        HSE_ClassificationReport = HSE_ClassificationDF.groupby(['Classification'], as_index=False).id.count()
        HSE_ClassificationReport = pd.DataFrame(HSE_ClassificationReport)
        HSE_ClassificationReport.rename(columns={'Classification':'HSE Classified Event', 'id':'Event Count'},inplace = True)
        HSE_ClassificationReport = HSE_ClassificationReport.reset_index(drop=True)
        HSE_ClassificationReport.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_ClassificationReport  = HSE_ClassificationReport.reset_index(drop=True)
        HSE_ClassificationReport['Event Percentage (%)'] = ((HSE_ClassificationReport['Event Count'] / HSE_ClassificationReport['Event Count'].sum())*100).round(1)
        HSE_ClassificationReport     = pd.DataFrame(HSE_ClassificationReport, index=None)

        ClassificList   = ["Equipment", "Health", "Near Miss", "Community", "Environment", "Non work related", "Vehicle"]
        ClassificListDF = pd.DataFrame({'HSE Classified Event': ClassificList})
        ClassificListDF.sort_values(by=['HSE Classified Event'],  inplace=True)
        ClassificListDF  = ClassificListDF.reset_index(drop=True)
        HSE_ClassificationReport_Merge = pd.merge(HSE_ClassificationReport, ClassificListDF, how='outer', on=['HSE Classified Event','HSE Classified Event'])
        fillZero = int(0)

        HSE_ClassificationReport_Merge["Event Count"].fillna(fillZero, inplace = True)
        HSE_ClassificationReport_Merge["Event Percentage (%)"].fillna(fillZero, inplace = True)
        HSE_ClassificationReport_Merge['Event Count'] = (HSE_ClassificationReport_Merge.loc[:,['Event Count']]).astype(int)
        HSE_ClassificationReport_Merge         = pd.DataFrame(HSE_ClassificationReport_Merge)
        HSE_ClassificationReport_Merge.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_ClassificationReport_Merge = HSE_ClassificationReport_Merge.reset_index(drop=True) 
        HSE_ClassificationReport_Merge = pd.DataFrame(HSE_ClassificationReport_Merge) 
        Index_Length_Classification           = len(HSE_ClassificationReport_Merge)+1
        HSE_ClassificationReport_Merge['Event Index'] = pd.Series(range(1,Index_Length_Classification))
        HSE_ClassificationReport_Merge = HSE_ClassificationReport_Merge.loc[:,
                                    ['Event Index','HSE Classified Event','Event Count','Event Percentage (%)']]
        HSE_ClassificationReport_Merge                          = HSE_ClassificationReport_Merge.reset_index(drop=True)
        HSE_ClassificationReport_Merge                          = pd.DataFrame(HSE_ClassificationReport_Merge)


        ## Generationing RiskLevel Report
        HSE_RiskLevelDF      = pd.DataFrame(data)
        HSE_RiskLevelDF      = HSE_RiskLevelDF.groupby(['EmergencyLevel'], as_index=False).id.count()
        HSE_RiskLevelReport  = pd.DataFrame(HSE_RiskLevelDF)
        HSE_RiskLevelReport.rename(columns={'EmergencyLevel':'HSE Emergency Event', 'id':'Event Count'},inplace = True)
        HSE_RiskLevelReport  = HSE_RiskLevelReport.reset_index(drop=True)
        HSE_RiskLevelReport['Event Percentage (%)'] = ((HSE_RiskLevelReport['Event Count'] / HSE_RiskLevelReport['Event Count'].sum())*100).round(1)
        HSE_RiskLevelReport.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_RiskLevelReport  = HSE_RiskLevelReport.reset_index(drop=True)
        HSE_RiskLevelReport  = pd.DataFrame(HSE_RiskLevelReport, index=None)

        RiskLevelList   = ["High", "Med", "Low"]
        RiskLevelListDF = pd.DataFrame({'HSE Emergency Event': RiskLevelList})
        RiskLevelListDF.sort_values(by=['HSE Emergency Event'],  inplace=True)
        RiskLevelListDF  = RiskLevelListDF.reset_index(drop=True)
        HSE_EmergencyReport_Merge = pd.merge(HSE_RiskLevelReport, RiskLevelListDF, how='outer', on=['HSE Emergency Event','HSE Emergency Event'])
        fillZero = int(0)

        HSE_EmergencyReport_Merge["Event Count"].fillna(fillZero, inplace = True)
        HSE_EmergencyReport_Merge["Event Percentage (%)"].fillna(fillZero, inplace = True)
        HSE_EmergencyReport_Merge['Event Count'] = (HSE_EmergencyReport_Merge.loc[:,['Event Count']]).astype(int)
        HSE_EmergencyReport_Merge         = pd.DataFrame(HSE_EmergencyReport_Merge)
        HSE_EmergencyReport_Merge.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_EmergencyReport_Merge = HSE_EmergencyReport_Merge.reset_index(drop=True) 
        HSE_EmergencyReport_Merge = pd.DataFrame(HSE_EmergencyReport_Merge) 
        Index_Length_Emergency           = len(HSE_EmergencyReport_Merge)+1
        HSE_EmergencyReport_Merge['Event Index'] = pd.Series(range(1,Index_Length_Emergency ))
        HSE_EmergencyReport_Merge = HSE_EmergencyReport_Merge.loc[:,
                                    ['Event Index','HSE Emergency Event','Event Count','Event Percentage (%)']]
        HSE_EmergencyReport_Merge                          = HSE_EmergencyReport_Merge.reset_index(drop=True)
        HSE_EmergencyReport_Merge['Emergency_Color']   = (HSE_EmergencyReport_Merge['HSE Emergency Event'].apply(front_overview_EmergencyPlots_Color))
        HSE_EmergencyReport_Merge                      = pd.DataFrame(HSE_EmergencyReport_Merge)


        ## Generationing Crew Manager Report
        HSE_CrewManagerDF        = pd.DataFrame(data)
        HSE_CrewManagerDFReport  = HSE_CrewManagerDF.groupby(['HSEAdvisorInvestigator'], as_index=False).id.count()
        HSE_CrewManagerDFReport  = pd.DataFrame(HSE_CrewManagerDFReport)
        HSE_CrewManagerDFReport.rename(columns={'HSEAdvisorInvestigator':'HSE Project Manager', 'id':'Event Count'},inplace = True)
        HSE_CrewManagerDFReport  = HSE_CrewManagerDFReport.reset_index(drop=True)
        HSE_CrewManagerDFReport.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_CrewManagerDFReport  = HSE_CrewManagerDFReport.reset_index(drop=True)
        HSE_CrewManagerDFReport['Event Percentage (%)'] = ((HSE_CrewManagerDFReport['Event Count'] / HSE_CrewManagerDFReport['Event Count'].sum())*100).round(1)
        HSE_CrewManagerDFReport     = pd.DataFrame(HSE_CrewManagerDFReport, index=None)

        HSE_CrewManagerDFReport_Merge = pd.DataFrame(HSE_CrewManagerDFReport) 
        Index_Length_CrewManager           = len(HSE_CrewManagerDFReport_Merge)+1
        HSE_CrewManagerDFReport_Merge['Event Index'] = pd.Series(range(1,Index_Length_CrewManager ))
        HSE_CrewManagerDFReport_Merge = HSE_CrewManagerDFReport_Merge.loc[:,
                                    ['Event Index','HSE Project Manager','Event Count','Event Percentage (%)']]
        HSE_CrewManagerDFReport_Merge                      = HSE_CrewManagerDFReport_Merge.reset_index(drop=True)
        HSE_CrewManagerDFReport_Merge                      = pd.DataFrame(HSE_CrewManagerDFReport_Merge)


        ## Generationing Monthly Breakdown Report
        HSE_MonthlyBreakdown         = pd.DataFrame(data)
        HSE_MonthlyBreakdown['EventDate'] = pd.to_datetime(HSE_MonthlyBreakdown['EventDate']).dt.strftime('%Y-%m')
        HSE_MonthlyBreakdownReport   = HSE_MonthlyBreakdown.groupby(['EventDate'], as_index=False).id.count()
        HSE_MonthlyBreakdownReport.rename(columns={'EventDate':'EventByMonth', 'id':'Event Count'},inplace = True)

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

        HSE_MonthlyBreakdownReport['HSE Event By Month'] = HSE_MonthlyBreakdownReport['EventByMonth'].apply(trans_Month)
        HSE_MonthlyBreakdownReport                   = HSE_MonthlyBreakdownReport.loc[:,['HSE Event By Month','Event Count']]
        HSE_MonthlyBreakdownReport                   = HSE_MonthlyBreakdownReport.reset_index(drop=True)
        HSE_MonthlyBreakdownReport['Event Percentage (%)']  =((HSE_MonthlyBreakdownReport['Event Count'] / HSE_MonthlyBreakdownReport['Event Count'].sum())*100).round(1)
        HSE_MonthlyBreakdownReport_Merge             = pd.DataFrame(HSE_MonthlyBreakdownReport, index=None)
        HSE_MonthlyBreakdownReport_Merge = HSE_MonthlyBreakdownReport_Merge.reset_index(drop=True)

        HSE_MonthlyBreakdownReport_Merge = pd.DataFrame(HSE_MonthlyBreakdownReport_Merge) 
        Index_Length_MonthlyBreakdown          = len(HSE_MonthlyBreakdownReport_Merge)+1
        HSE_MonthlyBreakdownReport_Merge['Event Index'] = pd.Series(range(1,Index_Length_MonthlyBreakdown ))
        HSE_MonthlyBreakdownReport_Merge = HSE_MonthlyBreakdownReport_Merge.loc[:,
                                    ['Event Index','HSE Event By Month','Event Count','Event Percentage (%)']]
        HSE_MonthlyBreakdownReport_Merge                          = HSE_MonthlyBreakdownReport_Merge.reset_index(drop=True)


        ## Generationing Unsafe Act Report
        HSE_UnsafeActDF      = pd.DataFrame(data)
        HSE_UnsafeActDF      = HSE_UnsafeActDF.groupby(['UnsafeAct'], as_index=False).id.count()
        HSE_UnsafeActReport  = pd.DataFrame(HSE_UnsafeActDF)
        HSE_UnsafeActReport.rename(columns={'UnsafeAct':'HSE Unsafe Act', 'id':'Event Count'},inplace = True)
        HSE_UnsafeActReport  = HSE_UnsafeActReport.reset_index(drop=True)
        HSE_UnsafeActReport['Event Percentage (%)'] = ((HSE_UnsafeActReport['Event Count'] / HSE_UnsafeActReport['Event Count'].sum())*100).round(1)
        HSE_UnsafeActReport  = pd.DataFrame(HSE_UnsafeActReport)        
        HSE_UnsafeActReport.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_UnsafeActReport  = HSE_UnsafeActReport.reset_index(drop=True)
        HSE_UnsafeActReport  = pd.DataFrame(HSE_UnsafeActReport)
        Index_Length_UnsafeAct          = len(HSE_UnsafeActReport)+1
        HSE_UnsafeActReport['Event Index'] = pd.Series(range(1,Index_Length_UnsafeAct))
        HSE_UnsafeActReport = HSE_UnsafeActReport.loc[:,
                                    ['Event Index','HSE Unsafe Act','Event Count','Event Percentage (%)']]
        HSE_UnsafeActReport_Merge  = pd.DataFrame(HSE_UnsafeActReport)
        HSE_UnsafeActReport_Merge['UnsafeAct_Color'] = HSE_UnsafeActReport_Merge['HSE Unsafe Act'].apply(project_report_UnsafeAct_Cond_Color)
        HSE_UnsafeActReport_Merge  = HSE_UnsafeActReport_Merge.reset_index(drop=True)
        HSE_UnsafeActReport_Merge  = pd.DataFrame(HSE_UnsafeActReport_Merge)


        ## Generationing Unsafe Condition Report
        HSE_UnsafeCondDF      = pd.DataFrame(data)
        HSE_UnsafeCondDF      = HSE_UnsafeCondDF.groupby(['UnsafeCond'], as_index=False).id.count()
        HSE_UnsafeCondReport  = pd.DataFrame(HSE_UnsafeCondDF)
        HSE_UnsafeCondReport.rename(columns={'UnsafeCond':'HSE Unsafe Condition', 'id':'Event Count'},inplace = True)
        HSE_UnsafeCondReport  = HSE_UnsafeCondReport.reset_index(drop=True)
        HSE_UnsafeCondReport['Event Percentage (%)'] = ((HSE_UnsafeCondReport['Event Count'] / HSE_UnsafeCondReport['Event Count'].sum())*100).round(1)
        HSE_UnsafeCondReport  = pd.DataFrame(HSE_UnsafeCondReport)        
        HSE_UnsafeCondReport.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_UnsafeCondReport  = HSE_UnsafeCondReport.reset_index(drop=True)
        HSE_UnsafeCondReport  = pd.DataFrame(HSE_UnsafeCondReport)

        Index_Length_UnsafeCond          = len(HSE_UnsafeCondReport)+1
        HSE_UnsafeCondReport['Event Index'] = pd.Series(range(1,Index_Length_UnsafeCond))
        HSE_UnsafeCondReport = HSE_UnsafeCondReport.loc[:,
                                    ['Event Index','HSE Unsafe Condition','Event Count','Event Percentage (%)']]
        HSE_UnsafeCondReport_Merge  = pd.DataFrame(HSE_UnsafeCondReport)
        HSE_UnsafeCondReport_Merge['UnsafeCond_Color'] = HSE_UnsafeCondReport_Merge['HSE Unsafe Condition'].apply(project_report_UnsafeAct_Cond_Color)
        HSE_UnsafeCondReport_Merge  = HSE_UnsafeCondReport_Merge.reset_index(drop=True)
        HSE_UnsafeCondReport_Merge  = pd.DataFrame(HSE_UnsafeCondReport_Merge)
                
        return TotalEntries, HSE_RecordablReport_Merge, HSE_ClassificationReport_Merge, HSE_EmergencyReport_Merge, HSE_MonthlyBreakdownReport_Merge, HSE_CrewManagerDFReport_Merge,\
               HSE_UnsafeActReport_Merge, HSE_UnsafeCondReport_Merge
              
def Annual_ProjectSummary(year= ""):
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

        ## Yearly project incidents Summary
        CrewTotal_DF_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc'], as_index=False).agg({"id":"count"})
        CrewTotal_DF_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
        'id':'No of HSE Incidents'},inplace = True)  
        CrewTotal_DF_Report = CrewTotal_DF_Report.reset_index(drop=True)            
        CrewTotal_DF_Report['Event Percentage (%)'] = ((CrewTotal_DF_Report['No of HSE Incidents'] / CrewTotal_DF_Report['No of HSE Incidents'].sum())*100).round(1)
        HSE_CrewReport         = pd.DataFrame(CrewTotal_DF_Report)
        HSE_CrewReport.sort_values(by=['No of HSE Incidents'], ascending=False, inplace=True)
        HSE_CrewReport = HSE_CrewReport.reset_index(drop=True) 
        HSE_CrewReport = pd.DataFrame(HSE_CrewReport)        
        Index_Length_Crew      = len(HSE_CrewReport)+1
        HSE_CrewReport['Event Index'] = pd.Series(range(1,Index_Length_Crew))
        HSE_CrewReport['Join'] = HSE_CrewReport[['Project Name', 'Project Number']].agg(';'.join, axis=1)
        HSE_CrewReport = HSE_CrewReport.loc[:,
                                    ['Event Index','Project Name','Project Number', 'Project Location', 'No of HSE Incidents', 'Event Percentage (%)', 'Join']]

        ## Classification
        ViewJobReportBy_Classification  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','Classification'], as_index=False).agg({"id":"count"})
        ViewJobReportBy_Classification.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
        'Classification':'Classification', 'id':'No of Classified Incidents'},inplace = True)            
        ViewJobReportBy_Classification = ViewJobReportBy_Classification.reset_index(drop=True)
        ViewJobReportBy_Classification_Plot  = pd.DataFrame(ViewJobReportBy_Classification, index=None)
        ViewJobReportBy_Classification_Plot['Classified_Color'] = ViewJobReportBy_Classification_Plot['Classification'].apply(project_report_classificationPlots_Color)
        ViewJobReportBy_Classification_Plot                   = ViewJobReportBy_Classification_Plot.reset_index(drop=True)
        ViewJobReportBy_Classification_Plot['Project_Classification'] = ViewJobReportBy_Classification_Plot[['Project Name', 'Classification']].agg(';'.join, axis=1)
        ViewJobReportBy_Classification_Plot = pd.DataFrame(ViewJobReportBy_Classification_Plot)      
        ViewJobReportBy_Classification_Pivot  = pd.DataFrame(ViewJobReportBy_Classification, index=None)
        ViewJobReportBy_Classification_Pivot=pd.pivot_table(ViewJobReportBy_Classification_Pivot, values=["No of Classified Incidents"], 
        index=['Project Name','Project Number','Project Location'], columns=["Classification"], fill_value = 0)
        ViewJobReportBy_Classification_Pivot = pd.DataFrame(ViewJobReportBy_Classification_Pivot)
        ## Recordable
        ViewJobRecordable_By_Year_DF_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','RecordableFAMARWCLTI'], as_index=False).agg({"id":"count"})
        ViewJobRecordable_By_Year_DF_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location', 
        'RecordableFAMARWCLTI':'Recordable', 'id':'No of Recordable Incidents'},inplace = True)            
        ViewJobRecordable_By_Year_DF_Report = ViewJobRecordable_By_Year_DF_Report.reset_index(drop=True)
        ViewJobRecordable_By_Year_DF_Report  = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report, index=None)
        ViewJobRecordable_By_Year_DF_Report_Plot  = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report, index=None)
        ViewJobRecordable_By_Year_DF_Report_Plot['Recordable_Color'] = ViewJobRecordable_By_Year_DF_Report_Plot['Recordable'].apply(project_report_recordablePlots_Color)
        ViewJobRecordable_By_Year_DF_Report_Plot                   = ViewJobRecordable_By_Year_DF_Report_Plot.reset_index(drop=True)
        ViewJobRecordable_By_Year_DF_Report_Plot['Project_Recordable'] = ViewJobRecordable_By_Year_DF_Report_Plot[['Project Name', 'Recordable']].agg(';'.join, axis=1)
        ViewJobRecordable_By_Year_DF_Report_Plot = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report_Plot)
        ViewJobRecordable_By_Year_DF_Report_Pivot  = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report, index=None)
        ViewJobRecordable_By_Year_DF_Report_Pivot=pd.pivot_table(ViewJobRecordable_By_Year_DF_Report_Pivot, 
        values=["No of Recordable Incidents"], index=['Project Name','Project Number','Project Location'], columns=["Recordable"], fill_value = 0)
        ViewJobRecordable_By_Year_DF_Report_Pivot = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report_Pivot)

        ## Generationing job Emergency Level Report
        HSE_EmergencyLevelDF      = pd.DataFrame(ViewJobReportBy_Year_DF)
        HSE_EmergencyLevelDF      = HSE_EmergencyLevelDF.groupby(['ProjName','ProjNum','ProjLoc','EmergencyLevel'], as_index=False).agg({"id":"count"})
        HSE_EmergencyLevelDF.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location', 
        'EmergencyLevel':'Emergency Level', 'id':'No Of EmergencyLevel Incidents'},inplace = True)            
        HSE_EmergencyLevelDF = HSE_EmergencyLevelDF.reset_index(drop=True)
        HSE_EmergencyLevelDF_Plot  = pd.DataFrame(HSE_EmergencyLevelDF, index=None)
        HSE_EmergencyLevelDF_Plot['Emergency_Color'] = HSE_EmergencyLevelDF_Plot['Emergency Level'].apply(front_overview_EmergencyPlots_Color)
        HSE_EmergencyLevelDF_Plot                   = HSE_EmergencyLevelDF_Plot.reset_index(drop=True)
        HSE_EmergencyLevelDF_Plot['Project_Emergency'] = HSE_EmergencyLevelDF_Plot[['Project Name', 'Emergency Level']].agg(';'.join, axis=1)
        HSE_EmergencyLevelDF_Plot = pd.DataFrame(HSE_EmergencyLevelDF_Plot)
        HSE_EmergencyLevelDF_Pivot  = pd.DataFrame(HSE_EmergencyLevelDF, index=None)
        HSE_EmergencyLevelDF_Pivot=pd.pivot_table(HSE_EmergencyLevelDF_Pivot, 
        values=["No Of EmergencyLevel Incidents"], index=['Project Name','Project Number','Project Location'], columns=["Emergency Level"], fill_value = 0)
        HSE_EmergencyLevelDF_Pivot = pd.DataFrame(HSE_EmergencyLevelDF_Pivot)

        ## Generationing job WCB Report
      
        CrewTotal_WCB_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','WCBCase'], as_index=False).agg({"id":"count"})
        CrewTotal_WCB_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
                                                'WCBCase':'WCBCase', 'id':'No of WCB Incidents'},inplace = True)            
        HSE_WCB_Report  = CrewTotal_WCB_Report.reset_index(drop=True)
        HSE_WCB_Report_Plot  = pd.DataFrame(HSE_WCB_Report, index=None)
        HSE_WCB_Report_Plot['WCB_Color'] = HSE_WCB_Report_Plot['WCBCase'].apply(project_report_WCB_Color)
        HSE_WCB_Report_Plot                   = HSE_WCB_Report_Plot.reset_index(drop=True)
        HSE_WCB_Report_Plot['Project_WCB'] = HSE_WCB_Report_Plot[['Project Name', 'WCBCase']].agg(';'.join, axis=1)
        HSE_WCB_Report_Plot = pd.DataFrame(HSE_WCB_Report_Plot)
        HSE_WCB_Report_Pivot = pd.DataFrame(HSE_WCB_Report , index=None)
        HSE_WCB_Report_Pivot=pd.pivot_table(HSE_WCB_Report_Pivot, values=["No of WCB Incidents"], 
        index=['Project Name','Project Number','Project Location'], columns=["WCBCase"], fill_value = 0)
        HSE_WCB_Report_Pivot = pd.DataFrame(HSE_WCB_Report_Pivot)


        ## Generationing job UnsafeAct Report

        CrewTotal_UnsafeAct_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','UnsafeAct'], as_index=False).agg({"id":"count"})
        CrewTotal_UnsafeAct_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
                                                'UnsafeAct':'UnsafeAct', 'id':'No of UnsafeAct Incidents'},inplace = True)            
        CrewTotal_UnsafeAct_Report  = CrewTotal_UnsafeAct_Report.reset_index(drop=True)
        HSE_UnsafeAct_Report = pd.DataFrame(CrewTotal_UnsafeAct_Report, index=None)
        HSE_UnsafeAct_Report_Plot  = pd.DataFrame(HSE_UnsafeAct_Report, index=None)
        HSE_UnsafeAct_Report_Plot['UnsafeAct_Color'] = HSE_UnsafeAct_Report_Plot['UnsafeAct'].apply(project_report_UnsafeAct_Cond_Color)
        HSE_UnsafeAct_Report_Plot                   = HSE_UnsafeAct_Report_Plot.reset_index(drop=True)
        HSE_UnsafeAct_Report_Plot['Project_UnsafeAct'] = HSE_UnsafeAct_Report_Plot[['Project Name', 'UnsafeAct']].agg(';'.join, axis=1)
        HSE_UnsafeAct_Report_Plot = pd.DataFrame(HSE_UnsafeAct_Report_Plot)
        HSE_UnsafeAct_Report_Pivot = pd.DataFrame(HSE_UnsafeAct_Report , index=None)
        HSE_UnsafeAct_Report_Pivot=pd.pivot_table(HSE_UnsafeAct_Report_Pivot, values=["No of UnsafeAct Incidents"], 
        index=['Project Name','Project Number','Project Location'],
        columns=["UnsafeAct"], fill_value = 0)
        HSE_UnsafeAct_Report_Pivot = pd.DataFrame(HSE_UnsafeAct_Report_Pivot)


         ## Generationing job UnsafeCond Report

        CrewTotal_UnsafeCond_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','UnsafeCond'], as_index=False).agg({"id":"count"})
        CrewTotal_UnsafeCond_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
                                                'UnsafeCond':'UnsafeCond', 'id':'No of UnsafeCond Incidents'},inplace = True)            
        CrewTotal_UnsafeCond_Report  = CrewTotal_UnsafeCond_Report.reset_index(drop=True)
        HSE_UnsafeCond_Report = pd.DataFrame(CrewTotal_UnsafeCond_Report, index=None)
        HSE_UnsafeCond_Report_Plot  = pd.DataFrame(HSE_UnsafeCond_Report, index=None)
        HSE_UnsafeCond_Report_Plot['UnsafeCond_Color'] = HSE_UnsafeCond_Report_Plot['UnsafeCond'].apply(project_report_UnsafeAct_Cond_Color)
        HSE_UnsafeCond_Report_Plot                   = HSE_UnsafeCond_Report_Plot.reset_index(drop=True)
        HSE_UnsafeCond_Report_Plot['Project_UnsafeCond'] = HSE_UnsafeCond_Report_Plot[['Project Name', 'UnsafeCond']].agg(';'.join, axis=1)
        HSE_UnsafeCond_Report_Plot = pd.DataFrame(HSE_UnsafeCond_Report_Plot)
        HSE_UnsafeCond_Report_Pivot = pd.DataFrame(HSE_UnsafeCond_Report , index=None)
        HSE_UnsafeCond_Report_Pivot=pd.pivot_table(HSE_UnsafeCond_Report_Pivot, values=["No of UnsafeCond Incidents"], 
        index=['Project Name','Project Number','Project Location'],
        columns=["UnsafeCond"], fill_value = 0)
        HSE_UnsafeCond_Report_Pivot = pd.DataFrame(HSE_UnsafeCond_Report_Pivot)


        return TotalEntries, ViewJobReportBy_Classification_Plot, ViewJobReportBy_Classification_Pivot, \
        ViewJobRecordable_By_Year_DF_Report_Pivot, ViewJobRecordable_By_Year_DF_Report_Plot,\
        HSE_EmergencyLevelDF_Pivot, HSE_EmergencyLevelDF_Plot,\
        HSE_WCB_Report_Pivot, HSE_WCB_Report_Plot,\
        HSE_UnsafeAct_Report_Pivot, HSE_UnsafeAct_Report_Plot,\
        HSE_UnsafeCond_Report_Pivot, HSE_UnsafeCond_Report_Plot, HSE_CrewReport
             
def Segmented_EventSummary(year= "", EventSegStartDate="", EventSegEndDate=""):
    if((year)!=0) & ((EventSegStartDate)!=0) & ((EventSegEndDate)!=0):
        Year_Get_Breakdown  = int(year)            
        Year_Get_End        = str(EventSegEndDate)
        Year_Get_Start      = str(EventSegStartDate)

        con = sqlite3.connect(DATABASE_NAME)
        Complete_df = pd.read_sql_query("SELECT * FROM HSEIncidentLog_MASTER ORDER BY `id` ASC ;", con)
        data = pd.DataFrame(Complete_df)
        data['EventDate']   = pd.to_datetime(data['EventDate']).dt.strftime('%Y-%m-%d')
        Year_Get_End   = pd.to_datetime(Year_Get_End).strftime('%Y-%m-%d')
        Year_Get_Start = pd.to_datetime(Year_Get_Start).strftime('%Y-%m-%d')            
        data = data[(data['EventDate'] >= Year_Get_Start) & (data['EventDate'] <= Year_Get_End)]          
        data = data.reset_index(drop=True)
        TotalEntries = len(data)

        ## Generationing Recordable Report
        HSE_RecordableDF     = pd.DataFrame(data)
        HSE_RecordableDF     = HSE_RecordableDF.groupby(['RecordableFAMARWCLTI'], as_index=False).id.count()        
        HSE_RecordableDF.rename(columns={'RecordableFAMARWCLTI':'HSE Recordable Event', 'id':'Event Count'},inplace = True)
        HSE_RecordableDF  = HSE_RecordableDF.reset_index(drop=True)
        HSE_RecordableDF['Event Percentage (%)'] = ((HSE_RecordableDF['Event Count'] / HSE_RecordableDF['Event Count'].sum())*100).round(1)
        HSE_RecordablReport  = pd.DataFrame(HSE_RecordableDF)

        RecList   = ["Non-Recordable", "FA - First Aid", "MA - Medical Aid", "RWC - Restricted Work Case", "LTI - Lost Time Injury", "FT - Fatal"]
        RecListDF = pd.DataFrame({'HSE Recordable Event': RecList})
        RecListDF.sort_values(by=['HSE Recordable Event'],  inplace=True)
        RecListDF  = RecListDF.reset_index(drop=True)
        HSE_RecordablReport_Merge = pd.merge(HSE_RecordablReport, RecListDF, how='outer', on=['HSE Recordable Event','HSE Recordable Event'])
        fillZero = int(0)

        HSE_RecordablReport_Merge["Event Count"].fillna(fillZero, inplace = True)
        HSE_RecordablReport_Merge["Event Percentage (%)"].fillna(fillZero, inplace = True)
        HSE_RecordablReport_Merge['Event Count'] = (HSE_RecordablReport_Merge.loc[:,['Event Count']]).astype(int)
        HSE_RecordablReport_Merge         = pd.DataFrame(HSE_RecordablReport_Merge)
        HSE_RecordablReport_Merge.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_RecordablReport_Merge = HSE_RecordablReport_Merge.reset_index(drop=True) 
        HSE_RecordablReport_Merge = pd.DataFrame(HSE_RecordablReport_Merge) 
        Index_Length_Recordable           = len(HSE_RecordablReport_Merge)+1
        HSE_RecordablReport_Merge['Event Index'] = pd.Series(range(1,Index_Length_Recordable))
        HSE_RecordablReport_Merge = HSE_RecordablReport_Merge.loc[:,
                                    ['Event Index','HSE Recordable Event','Event Count','Event Percentage (%)']]
        HSE_RecordablReport_Merge                          = HSE_RecordablReport_Merge.reset_index(drop=True)
        HSE_RecordablReport_Merge                          = pd.DataFrame(HSE_RecordablReport_Merge)

        # ## Generationing Classification Report
        HSE_ClassificationDF     = pd.DataFrame(data)
        HSE_ClassificationReport = HSE_ClassificationDF.groupby(['Classification'], as_index=False).id.count()
        HSE_ClassificationReport = pd.DataFrame(HSE_ClassificationReport)
        HSE_ClassificationReport.rename(columns={'Classification':'HSE Classified Event', 'id':'Event Count'},inplace = True)
        HSE_ClassificationReport = HSE_ClassificationReport.reset_index(drop=True)
        HSE_ClassificationReport.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_ClassificationReport  = HSE_ClassificationReport.reset_index(drop=True)
        HSE_ClassificationReport['Event Percentage (%)'] = ((HSE_ClassificationReport['Event Count'] / HSE_ClassificationReport['Event Count'].sum())*100).round(1)
        HSE_ClassificationReport     = pd.DataFrame(HSE_ClassificationReport, index=None)

        ClassificList   = ["Equipment", "Health", "Near Miss", "Community", "Environment", "Non work related", "Vehicle"]
        ClassificListDF = pd.DataFrame({'HSE Classified Event': ClassificList})
        ClassificListDF.sort_values(by=['HSE Classified Event'],  inplace=True)
        ClassificListDF  = ClassificListDF.reset_index(drop=True)
        HSE_ClassificationReport_Merge = pd.merge(HSE_ClassificationReport, ClassificListDF, how='outer', on=['HSE Classified Event','HSE Classified Event'])
        fillZero = int(0)

        HSE_ClassificationReport_Merge["Event Count"].fillna(fillZero, inplace = True)
        HSE_ClassificationReport_Merge["Event Percentage (%)"].fillna(fillZero, inplace = True)
        HSE_ClassificationReport_Merge['Event Count'] = (HSE_ClassificationReport_Merge.loc[:,['Event Count']]).astype(int)
        HSE_ClassificationReport_Merge         = pd.DataFrame(HSE_ClassificationReport_Merge)
        HSE_ClassificationReport_Merge.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_ClassificationReport_Merge = HSE_ClassificationReport_Merge.reset_index(drop=True) 
        HSE_ClassificationReport_Merge = pd.DataFrame(HSE_ClassificationReport_Merge) 
        Index_Length_Classification           = len(HSE_ClassificationReport_Merge)+1
        HSE_ClassificationReport_Merge['Event Index'] = pd.Series(range(1,Index_Length_Classification))
        HSE_ClassificationReport_Merge = HSE_ClassificationReport_Merge.loc[:,
                                    ['Event Index','HSE Classified Event','Event Count','Event Percentage (%)']]
        HSE_ClassificationReport_Merge                          = HSE_ClassificationReport_Merge.reset_index(drop=True)
        HSE_ClassificationReport_Merge                          = pd.DataFrame(HSE_ClassificationReport_Merge)


        ## Generationing RiskLevel Report
        HSE_RiskLevelDF      = pd.DataFrame(data)
        HSE_RiskLevelDF      = HSE_RiskLevelDF.groupby(['EmergencyLevel'], as_index=False).id.count()
        HSE_RiskLevelReport  = pd.DataFrame(HSE_RiskLevelDF)
        HSE_RiskLevelReport.rename(columns={'EmergencyLevel':'HSE Emergency Event', 'id':'Event Count'},inplace = True)
        HSE_RiskLevelReport  = HSE_RiskLevelReport.reset_index(drop=True)
        HSE_RiskLevelReport['Event Percentage (%)'] = ((HSE_RiskLevelReport['Event Count'] / HSE_RiskLevelReport['Event Count'].sum())*100).round(1)
        HSE_RiskLevelReport.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_RiskLevelReport  = HSE_RiskLevelReport.reset_index(drop=True)
        HSE_RiskLevelReport  = pd.DataFrame(HSE_RiskLevelReport, index=None)

        RiskLevelList   = ["High", "Med", "Low"]
        RiskLevelListDF = pd.DataFrame({'HSE Emergency Event': RiskLevelList})
        RiskLevelListDF.sort_values(by=['HSE Emergency Event'],  inplace=True)
        RiskLevelListDF  = RiskLevelListDF.reset_index(drop=True)
        HSE_EmergencyReport_Merge = pd.merge(HSE_RiskLevelReport, RiskLevelListDF, how='outer', on=['HSE Emergency Event','HSE Emergency Event'])
        fillZero = int(0)

        HSE_EmergencyReport_Merge["Event Count"].fillna(fillZero, inplace = True)
        HSE_EmergencyReport_Merge["Event Percentage (%)"].fillna(fillZero, inplace = True)
        HSE_EmergencyReport_Merge['Event Count'] = (HSE_EmergencyReport_Merge.loc[:,['Event Count']]).astype(int)
        HSE_EmergencyReport_Merge         = pd.DataFrame(HSE_EmergencyReport_Merge)
        HSE_EmergencyReport_Merge.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_EmergencyReport_Merge = HSE_EmergencyReport_Merge.reset_index(drop=True) 
        HSE_EmergencyReport_Merge = pd.DataFrame(HSE_EmergencyReport_Merge) 
        Index_Length_Emergency           = len(HSE_EmergencyReport_Merge)+1
        HSE_EmergencyReport_Merge['Event Index'] = pd.Series(range(1,Index_Length_Emergency ))
        HSE_EmergencyReport_Merge = HSE_EmergencyReport_Merge.loc[:,
                                    ['Event Index','HSE Emergency Event','Event Count','Event Percentage (%)']]
        HSE_EmergencyReport_Merge                          = HSE_EmergencyReport_Merge.reset_index(drop=True)
        HSE_EmergencyReport_Merge['Emergency_Color']   = (HSE_EmergencyReport_Merge['HSE Emergency Event'].apply(front_overview_EmergencyPlots_Color))
        HSE_EmergencyReport_Merge                      = pd.DataFrame(HSE_EmergencyReport_Merge)


        ## Generationing Crew Manager Report
        HSE_CrewManagerDF        = pd.DataFrame(data)
        HSE_CrewManagerDFReport  = HSE_CrewManagerDF.groupby(['HSEAdvisorInvestigator'], as_index=False).id.count()
        HSE_CrewManagerDFReport  = pd.DataFrame(HSE_CrewManagerDFReport)
        HSE_CrewManagerDFReport.rename(columns={'HSEAdvisorInvestigator':'HSE Project Manager', 'id':'Event Count'},inplace = True)
        HSE_CrewManagerDFReport  = HSE_CrewManagerDFReport.reset_index(drop=True)
        HSE_CrewManagerDFReport.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_CrewManagerDFReport  = HSE_CrewManagerDFReport.reset_index(drop=True)
        HSE_CrewManagerDFReport['Event Percentage (%)'] = ((HSE_CrewManagerDFReport['Event Count'] / HSE_CrewManagerDFReport['Event Count'].sum())*100).round(1)
        HSE_CrewManagerDFReport     = pd.DataFrame(HSE_CrewManagerDFReport, index=None)

        HSE_CrewManagerDFReport_Merge = pd.DataFrame(HSE_CrewManagerDFReport) 
        Index_Length_CrewManager           = len(HSE_CrewManagerDFReport_Merge)+1
        HSE_CrewManagerDFReport_Merge['Event Index'] = pd.Series(range(1,Index_Length_CrewManager ))
        HSE_CrewManagerDFReport_Merge = HSE_CrewManagerDFReport_Merge.loc[:,
                                    ['Event Index','HSE Project Manager','Event Count','Event Percentage (%)']]
        HSE_CrewManagerDFReport_Merge                      = HSE_CrewManagerDFReport_Merge.reset_index(drop=True)
        HSE_CrewManagerDFReport_Merge                      = pd.DataFrame(HSE_CrewManagerDFReport_Merge)


        ## Generationing Monthly Breakdown Report
        HSE_MonthlyBreakdown         = pd.DataFrame(data)
        HSE_MonthlyBreakdown['EventDate'] = pd.to_datetime(HSE_MonthlyBreakdown['EventDate']).dt.strftime('%Y-%m')
        HSE_MonthlyBreakdownReport   = HSE_MonthlyBreakdown.groupby(['EventDate'], as_index=False).id.count()
        HSE_MonthlyBreakdownReport.rename(columns={'EventDate':'EventByMonth', 'id':'Event Count'},inplace = True)

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

        HSE_MonthlyBreakdownReport['HSE Event By Month'] = HSE_MonthlyBreakdownReport['EventByMonth'].apply(trans_Month)
        HSE_MonthlyBreakdownReport                   = HSE_MonthlyBreakdownReport.loc[:,['HSE Event By Month','Event Count']]
        HSE_MonthlyBreakdownReport                   = HSE_MonthlyBreakdownReport.reset_index(drop=True)
        HSE_MonthlyBreakdownReport['Event Percentage (%)']  =((HSE_MonthlyBreakdownReport['Event Count'] / HSE_MonthlyBreakdownReport['Event Count'].sum())*100).round(1)
        HSE_MonthlyBreakdownReport_Merge             = pd.DataFrame(HSE_MonthlyBreakdownReport, index=None)
        HSE_MonthlyBreakdownReport_Merge = HSE_MonthlyBreakdownReport_Merge.reset_index(drop=True)

        HSE_MonthlyBreakdownReport_Merge = pd.DataFrame(HSE_MonthlyBreakdownReport_Merge) 
        Index_Length_MonthlyBreakdown          = len(HSE_MonthlyBreakdownReport_Merge)+1
        HSE_MonthlyBreakdownReport_Merge['Event Index'] = pd.Series(range(1,Index_Length_MonthlyBreakdown ))
        HSE_MonthlyBreakdownReport_Merge = HSE_MonthlyBreakdownReport_Merge.loc[:,
                                    ['Event Index','HSE Event By Month','Event Count','Event Percentage (%)']]
        HSE_MonthlyBreakdownReport_Merge                          = HSE_MonthlyBreakdownReport_Merge.reset_index(drop=True)


        ## Generationing Unsafe Act Report
        HSE_UnsafeActDF      = pd.DataFrame(data)
        HSE_UnsafeActDF      = HSE_UnsafeActDF.groupby(['UnsafeAct'], as_index=False).id.count()
        HSE_UnsafeActReport  = pd.DataFrame(HSE_UnsafeActDF)
        HSE_UnsafeActReport.rename(columns={'UnsafeAct':'HSE Unsafe Act', 'id':'Event Count'},inplace = True)
        HSE_UnsafeActReport  = HSE_UnsafeActReport.reset_index(drop=True)
        HSE_UnsafeActReport['Event Percentage (%)'] = ((HSE_UnsafeActReport['Event Count'] / HSE_UnsafeActReport['Event Count'].sum())*100).round(1)
        HSE_UnsafeActReport  = pd.DataFrame(HSE_UnsafeActReport)        
        HSE_UnsafeActReport.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_UnsafeActReport  = HSE_UnsafeActReport.reset_index(drop=True)
        HSE_UnsafeActReport  = pd.DataFrame(HSE_UnsafeActReport)
        Index_Length_UnsafeAct          = len(HSE_UnsafeActReport)+1
        HSE_UnsafeActReport['Event Index'] = pd.Series(range(1,Index_Length_UnsafeAct))
        HSE_UnsafeActReport = HSE_UnsafeActReport.loc[:,
                                    ['Event Index','HSE Unsafe Act','Event Count','Event Percentage (%)']]
        HSE_UnsafeActReport_Merge  = pd.DataFrame(HSE_UnsafeActReport)
        HSE_UnsafeActReport_Merge['UnsafeAct_Color'] = HSE_UnsafeActReport_Merge['HSE Unsafe Act'].apply(project_report_UnsafeAct_Cond_Color)
        HSE_UnsafeActReport_Merge  = HSE_UnsafeActReport_Merge.reset_index(drop=True)
        HSE_UnsafeActReport_Merge  = pd.DataFrame(HSE_UnsafeActReport_Merge)


        ## Generationing Unsafe Condition Report
        HSE_UnsafeCondDF      = pd.DataFrame(data)
        HSE_UnsafeCondDF      = HSE_UnsafeCondDF.groupby(['UnsafeCond'], as_index=False).id.count()
        HSE_UnsafeCondReport  = pd.DataFrame(HSE_UnsafeCondDF)
        HSE_UnsafeCondReport.rename(columns={'UnsafeCond':'HSE Unsafe Condition', 'id':'Event Count'},inplace = True)
        HSE_UnsafeCondReport  = HSE_UnsafeCondReport.reset_index(drop=True)
        HSE_UnsafeCondReport['Event Percentage (%)'] = ((HSE_UnsafeCondReport['Event Count'] / HSE_UnsafeCondReport['Event Count'].sum())*100).round(1)
        HSE_UnsafeCondReport  = pd.DataFrame(HSE_UnsafeCondReport)        
        HSE_UnsafeCondReport.sort_values(by=['Event Count'], ascending=False, inplace=True)
        HSE_UnsafeCondReport  = HSE_UnsafeCondReport.reset_index(drop=True)
        HSE_UnsafeCondReport  = pd.DataFrame(HSE_UnsafeCondReport)

        Index_Length_UnsafeCond          = len(HSE_UnsafeCondReport)+1
        HSE_UnsafeCondReport['Event Index'] = pd.Series(range(1,Index_Length_UnsafeCond))
        HSE_UnsafeCondReport = HSE_UnsafeCondReport.loc[:,
                                    ['Event Index','HSE Unsafe Condition','Event Count','Event Percentage (%)']]
        HSE_UnsafeCondReport_Merge  = pd.DataFrame(HSE_UnsafeCondReport)

        HSE_UnsafeCondReport_Merge['UnsafeCond_Color'] = HSE_UnsafeCondReport_Merge['HSE Unsafe Condition'].apply(project_report_UnsafeAct_Cond_Color)
        HSE_UnsafeCondReport_Merge  = HSE_UnsafeCondReport_Merge.reset_index(drop=True)
        HSE_UnsafeCondReport_Merge  = pd.DataFrame(HSE_UnsafeCondReport_Merge)
                
        return TotalEntries, HSE_RecordablReport_Merge, HSE_ClassificationReport_Merge, HSE_EmergencyReport_Merge, HSE_MonthlyBreakdownReport_Merge, HSE_CrewManagerDFReport_Merge,\
               HSE_UnsafeActReport_Merge, HSE_UnsafeCondReport_Merge

def Segmented_ProjectSummary(year= "", EventSegStartDate="", EventSegEndDate=""):
    if((year)!=0) & ((EventSegStartDate)!=0) & ((EventSegEndDate)!=0):
        Year_Get_Breakdown  = int(year)            
        Year_Get_End        = str(EventSegEndDate)
        Year_Get_Start      = str(EventSegStartDate)

        con = sqlite3.connect(DATABASE_NAME)
        Complete_df = pd.read_sql_query("SELECT * FROM HSEIncidentLog_MASTER ORDER BY `id` ASC ;", con)
        data = pd.DataFrame(Complete_df)
        data['EventDate']   = pd.to_datetime(data['EventDate']).dt.strftime('%Y-%m-%d')
        Year_Get_End   = pd.to_datetime(Year_Get_End).strftime('%Y-%m-%d')
        Year_Get_Start = pd.to_datetime(Year_Get_Start).strftime('%Y-%m-%d')            
        data = data[(data['EventDate'] >= Year_Get_Start) & (data['EventDate'] <= Year_Get_End)]  
        data = data.reset_index(drop=True)
        TotalEntries = len(data)      
        ViewJobReportBy_Year_DF     = pd.DataFrame(data, index=None)

        ## Yearly project incidents Summary
        CrewTotal_DF_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc'], as_index=False).agg({"id":"count"})
        CrewTotal_DF_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
        'id':'No of HSE Incidents'},inplace = True)  
        CrewTotal_DF_Report = CrewTotal_DF_Report.reset_index(drop=True)            
        CrewTotal_DF_Report['Event Percentage (%)'] = ((CrewTotal_DF_Report['No of HSE Incidents'] / CrewTotal_DF_Report['No of HSE Incidents'].sum())*100).round(1)
        HSE_CrewReport         = pd.DataFrame(CrewTotal_DF_Report)
        HSE_CrewReport.sort_values(by=['No of HSE Incidents'], ascending=False, inplace=True)
        HSE_CrewReport = HSE_CrewReport.reset_index(drop=True) 
        HSE_CrewReport = pd.DataFrame(HSE_CrewReport)        
        Index_Length_Crew      = len(HSE_CrewReport)+1
        HSE_CrewReport['Event Index'] = pd.Series(range(1,Index_Length_Crew))
        HSE_CrewReport['Join'] = HSE_CrewReport[['Project Name', 'Project Number']].agg(';'.join, axis=1)
        HSE_CrewReport = HSE_CrewReport.loc[:,
                                    ['Event Index','Project Name','Project Number', 'Project Location', 'No of HSE Incidents', 'Event Percentage (%)', 'Join']]

        ## Classification
        ViewJobReportBy_Classification  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','Classification'], as_index=False).agg({"id":"count"})
        ViewJobReportBy_Classification.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
        'Classification':'Classification', 'id':'No of Classified Incidents'},inplace = True)            
        ViewJobReportBy_Classification = ViewJobReportBy_Classification.reset_index(drop=True)
        ViewJobReportBy_Classification_Plot  = pd.DataFrame(ViewJobReportBy_Classification, index=None)
        ViewJobReportBy_Classification_Plot['Classified_Color'] = ViewJobReportBy_Classification_Plot['Classification'].apply(project_report_classificationPlots_Color)
        ViewJobReportBy_Classification_Plot                   = ViewJobReportBy_Classification_Plot.reset_index(drop=True)
        ViewJobReportBy_Classification_Plot['Project_Classification'] = ViewJobReportBy_Classification_Plot[['Project Name', 'Classification']].agg(';'.join, axis=1)
        ViewJobReportBy_Classification_Plot = pd.DataFrame(ViewJobReportBy_Classification_Plot)      
        ViewJobReportBy_Classification_Pivot  = pd.DataFrame(ViewJobReportBy_Classification, index=None)
        ViewJobReportBy_Classification_Pivot=pd.pivot_table(ViewJobReportBy_Classification_Pivot, values=["No of Classified Incidents"], 
        index=['Project Name','Project Number','Project Location'], columns=["Classification"], fill_value = 0)
        ViewJobReportBy_Classification_Pivot = pd.DataFrame(ViewJobReportBy_Classification_Pivot)
        ## Recordable
        ViewJobRecordable_By_Year_DF_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','RecordableFAMARWCLTI'], as_index=False).agg({"id":"count"})
        ViewJobRecordable_By_Year_DF_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location', 
        'RecordableFAMARWCLTI':'Recordable', 'id':'No of Recordable Incidents'},inplace = True)            
        ViewJobRecordable_By_Year_DF_Report = ViewJobRecordable_By_Year_DF_Report.reset_index(drop=True)
        ViewJobRecordable_By_Year_DF_Report  = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report, index=None)
        ViewJobRecordable_By_Year_DF_Report_Plot  = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report, index=None)
        ViewJobRecordable_By_Year_DF_Report_Plot['Recordable_Color'] = ViewJobRecordable_By_Year_DF_Report_Plot['Recordable'].apply(project_report_recordablePlots_Color)
        ViewJobRecordable_By_Year_DF_Report_Plot                   = ViewJobRecordable_By_Year_DF_Report_Plot.reset_index(drop=True)
        ViewJobRecordable_By_Year_DF_Report_Plot['Project_Recordable'] = ViewJobRecordable_By_Year_DF_Report_Plot[['Project Name', 'Recordable']].agg(';'.join, axis=1)
        ViewJobRecordable_By_Year_DF_Report_Plot = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report_Plot)
        ViewJobRecordable_By_Year_DF_Report_Pivot  = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report, index=None)
        ViewJobRecordable_By_Year_DF_Report_Pivot=pd.pivot_table(ViewJobRecordable_By_Year_DF_Report_Pivot, 
        values=["No of Recordable Incidents"], index=['Project Name','Project Number','Project Location'], columns=["Recordable"], fill_value = 0)
        ViewJobRecordable_By_Year_DF_Report_Pivot = pd.DataFrame(ViewJobRecordable_By_Year_DF_Report_Pivot)

        ## Generationing job Emergency Level Report
        HSE_EmergencyLevelDF      = pd.DataFrame(ViewJobReportBy_Year_DF)
        HSE_EmergencyLevelDF      = HSE_EmergencyLevelDF.groupby(['ProjName','ProjNum','ProjLoc','EmergencyLevel'], as_index=False).agg({"id":"count"})
        HSE_EmergencyLevelDF.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location', 
        'EmergencyLevel':'Emergency Level', 'id':'No Of EmergencyLevel Incidents'},inplace = True)            
        HSE_EmergencyLevelDF = HSE_EmergencyLevelDF.reset_index(drop=True)
        HSE_EmergencyLevelDF_Plot  = pd.DataFrame(HSE_EmergencyLevelDF, index=None)
        HSE_EmergencyLevelDF_Plot['Emergency_Color'] = HSE_EmergencyLevelDF_Plot['Emergency Level'].apply(front_overview_EmergencyPlots_Color)
        HSE_EmergencyLevelDF_Plot                   = HSE_EmergencyLevelDF_Plot.reset_index(drop=True)
        HSE_EmergencyLevelDF_Plot['Project_Emergency'] = HSE_EmergencyLevelDF_Plot[['Project Name', 'Emergency Level']].agg(';'.join, axis=1)
        HSE_EmergencyLevelDF_Plot = pd.DataFrame(HSE_EmergencyLevelDF_Plot)
        HSE_EmergencyLevelDF_Pivot  = pd.DataFrame(HSE_EmergencyLevelDF, index=None)
        HSE_EmergencyLevelDF_Pivot=pd.pivot_table(HSE_EmergencyLevelDF_Pivot, 
        values=["No Of EmergencyLevel Incidents"], index=['Project Name','Project Number','Project Location'], columns=["Emergency Level"], fill_value = 0)
        HSE_EmergencyLevelDF_Pivot = pd.DataFrame(HSE_EmergencyLevelDF_Pivot)

        ## Generationing job WCB Report
      
        CrewTotal_WCB_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','WCBCase'], as_index=False).agg({"id":"count"})
        CrewTotal_WCB_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
                                                'WCBCase':'WCBCase', 'id':'No of WCB Incidents'},inplace = True)            
        HSE_WCB_Report  = CrewTotal_WCB_Report.reset_index(drop=True)
        HSE_WCB_Report_Plot  = pd.DataFrame(HSE_WCB_Report, index=None)
        HSE_WCB_Report_Plot['WCB_Color'] = HSE_WCB_Report_Plot['WCBCase'].apply(project_report_WCB_Color)
        HSE_WCB_Report_Plot                   = HSE_WCB_Report_Plot.reset_index(drop=True)
        HSE_WCB_Report_Plot['Project_WCB'] = HSE_WCB_Report_Plot[['Project Name', 'WCBCase']].agg(';'.join, axis=1)
        HSE_WCB_Report_Plot = pd.DataFrame(HSE_WCB_Report_Plot)
        HSE_WCB_Report_Pivot = pd.DataFrame(HSE_WCB_Report , index=None)
        HSE_WCB_Report_Pivot=pd.pivot_table(HSE_WCB_Report_Pivot, values=["No of WCB Incidents"], 
        index=['Project Name','Project Number','Project Location'], columns=["WCBCase"], fill_value = 0)
        HSE_WCB_Report_Pivot = pd.DataFrame(HSE_WCB_Report_Pivot)


        ## Generationing job UnsafeAct Report

        CrewTotal_UnsafeAct_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','UnsafeAct'], as_index=False).agg({"id":"count"})
        CrewTotal_UnsafeAct_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
                                                'UnsafeAct':'UnsafeAct', 'id':'No of UnsafeAct Incidents'},inplace = True)            
        CrewTotal_UnsafeAct_Report  = CrewTotal_UnsafeAct_Report.reset_index(drop=True)
        HSE_UnsafeAct_Report = pd.DataFrame(CrewTotal_UnsafeAct_Report, index=None)
        HSE_UnsafeAct_Report_Plot  = pd.DataFrame(HSE_UnsafeAct_Report, index=None)
        HSE_UnsafeAct_Report_Plot['UnsafeAct_Color'] = HSE_UnsafeAct_Report_Plot['UnsafeAct'].apply(project_report_UnsafeAct_Cond_Color)
        HSE_UnsafeAct_Report_Plot                   = HSE_UnsafeAct_Report_Plot.reset_index(drop=True)
        HSE_UnsafeAct_Report_Plot['Project_UnsafeAct'] = HSE_UnsafeAct_Report_Plot[['Project Name', 'UnsafeAct']].agg(';'.join, axis=1)
        HSE_UnsafeAct_Report_Plot = pd.DataFrame(HSE_UnsafeAct_Report_Plot)
        HSE_UnsafeAct_Report_Pivot = pd.DataFrame(HSE_UnsafeAct_Report , index=None)
        HSE_UnsafeAct_Report_Pivot=pd.pivot_table(HSE_UnsafeAct_Report_Pivot, values=["No of UnsafeAct Incidents"], 
        index=['Project Name','Project Number','Project Location'],
        columns=["UnsafeAct"], fill_value = 0)
        HSE_UnsafeAct_Report_Pivot = pd.DataFrame(HSE_UnsafeAct_Report_Pivot)


         ## Generationing job UnsafeCond Report

        CrewTotal_UnsafeCond_Report  = ViewJobReportBy_Year_DF.groupby(['ProjName','ProjNum','ProjLoc','UnsafeCond'], as_index=False).agg({"id":"count"})
        CrewTotal_UnsafeCond_Report.rename(columns = {'ProjName': 'Project Name', 'ProjNum':'Project Number', 'ProjLoc':'Project Location',
                                                'UnsafeCond':'UnsafeCond', 'id':'No of UnsafeCond Incidents'},inplace = True)            
        CrewTotal_UnsafeCond_Report  = CrewTotal_UnsafeCond_Report.reset_index(drop=True)
        HSE_UnsafeCond_Report = pd.DataFrame(CrewTotal_UnsafeCond_Report, index=None)
        HSE_UnsafeCond_Report_Plot  = pd.DataFrame(HSE_UnsafeCond_Report, index=None)
        HSE_UnsafeCond_Report_Plot['UnsafeCond_Color'] = HSE_UnsafeCond_Report_Plot['UnsafeCond'].apply(project_report_UnsafeAct_Cond_Color)
        HSE_UnsafeCond_Report_Plot                   = HSE_UnsafeCond_Report_Plot.reset_index(drop=True)
        HSE_UnsafeCond_Report_Plot['Project_UnsafeCond'] = HSE_UnsafeCond_Report_Plot[['Project Name', 'UnsafeCond']].agg(';'.join, axis=1)
        HSE_UnsafeCond_Report_Plot = pd.DataFrame(HSE_UnsafeCond_Report_Plot)
        HSE_UnsafeCond_Report_Pivot = pd.DataFrame(HSE_UnsafeCond_Report , index=None)
        HSE_UnsafeCond_Report_Pivot=pd.pivot_table(HSE_UnsafeCond_Report_Pivot, values=["No of UnsafeCond Incidents"], 
        index=['Project Name','Project Number','Project Location'],
        columns=["UnsafeCond"], fill_value = 0)
        HSE_UnsafeCond_Report_Pivot = pd.DataFrame(HSE_UnsafeCond_Report_Pivot)


        return TotalEntries, ViewJobReportBy_Classification_Plot, ViewJobReportBy_Classification_Pivot, \
        ViewJobRecordable_By_Year_DF_Report_Pivot, ViewJobRecordable_By_Year_DF_Report_Plot,\
        HSE_EmergencyLevelDF_Pivot, HSE_EmergencyLevelDF_Plot,\
        HSE_WCB_Report_Pivot, HSE_WCB_Report_Plot,\
        HSE_UnsafeAct_Report_Pivot, HSE_UnsafeAct_Report_Plot,\
        HSE_UnsafeCond_Report_Pivot, HSE_UnsafeCond_Report_Plot, HSE_CrewReport