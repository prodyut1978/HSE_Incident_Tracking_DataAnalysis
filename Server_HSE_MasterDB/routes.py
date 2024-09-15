import os
import csv
from flask import Flask
import pandas as pd
from flask import  render_template,url_for,redirect,flash,request,jsonify
from Server_HSE_MasterDB.Server_HSE_MasterDB_All_Modules.Server_HSE_MasterDB_Controllers import Server_HSE_MasterDB_Controller
from Server_HSE_MasterDB.Server_HSE_MasterDB_All_Modules.Server_HSE_MasterDB_Controllers import Server_HSE_MasterDB_Analysis
from Server_HSE_MasterDB.Server_HSE_LoginDB_All_Modules.Server_HSE_LoginDB_Models.Server_HSE_LoginDB_Models import User
from Server_HSE_MasterDB.Server_HSE_LoginDB_All_Modules.Server_HSE_LoginDB_Forms.Server_HSE_LoginDB_Forms import LoginForm, RegisterForm
from Server_HSE_MasterDB import app
from Server_HSE_MasterDB import db
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
   form = LoginForm()
   if form.validate_on_submit():
      user = User.query.filter_by(username=form.username.data).first()
      if user:
         if check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('ViewDashboard'))
      return '<h1>Invalid username or password</h1>'
   return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
   form = RegisterForm()
   if form.validate_on_submit():
      hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
      new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
      db.session.add(new_user)
      db.session.commit()
      flash(f'Account created for {form.username.data}! .. Please Login Now', 'success')
      return redirect(url_for('index'))   
   return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('index'))


UPLOAD_FOLDER = './Server_HSE_MasterDB/static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

@app.errorhandler(404)
def not_found_error(error):
   return render_template('overview_dummy.html'),404

@app.errorhandler(500)
def internal_error(error):
   return render_template('overview_dummy.html'),500

@app.route("/Overview")
@login_required
def overview():
   try:
      DataFrame_HSE_Incidents = Server_HSE_MasterDB_Controller.front_overview_IncidentsCounts()
      Total_Incident = Server_HSE_MasterDB_Controller.Total_MasterDB_Incident()
      Eventindex = Server_HSE_MasterDB_Controller.front_overview_Eventindex()
      LastfiveYears_MasterDB_Incident=Server_HSE_MasterDB_Controller.LastfiveYears_Incident()
      ChartJS_XY_Data_Incidents= DataFrame_HSE_Incidents. filter(['Event Year', 'No of Incidents']).values
      ChartJS_X_labels_Incidents = [row[0] for row in ChartJS_XY_Data_Incidents]
      ChartJS_Y_values_Incidents = [row[1] for row in ChartJS_XY_Data_Incidents]
      DataFrame_HSE_EmergencyCounts = Server_HSE_MasterDB_Controller.front_overview_EmergencyCounts()
      ChartJS_XY_Data_EmergencyPlots  = Server_HSE_MasterDB_Controller.front_overview_EmergencyPlots()
      ChartJS_X_labels_Emergency_1 = [row[0] for row in ChartJS_XY_Data_EmergencyPlots]
      ChartJS_X_labels_Emergency_2 = [row[1] for row in ChartJS_XY_Data_EmergencyPlots]
      ChartJS_X_labels_Emergency_3 = [row[2] for row in ChartJS_XY_Data_EmergencyPlots]
      ChartJS_Y_values_Emergency   = [row[3] for row in ChartJS_XY_Data_EmergencyPlots]
      ChartJS_Y_color_Emergency    = [row[4] for row in ChartJS_XY_Data_EmergencyPlots]
   except:
      flash("Populated Overview Page Failed, Please Import HSE Event File")
      return render_template('overview_dummy.html')
   finally:
      return render_template('overview.html' ,Total_Incident = Total_Incident, 
      LastfiveYears_MasterDB_Incident=LastfiveYears_MasterDB_Incident, 
      Eventindex=Eventindex, name=current_user.username, 
      DataFrame_HSE_Incidents = [DataFrame_HSE_Incidents.to_html(index=False, classes='data', 
      col_space= {'Event Year': 100, 'No of Projects': 150, 'No of Incidents': 150, 'Percentage Index': 150}, justify="justify-all")],
      DataFrame_HSE_EmergencyCounts = [DataFrame_HSE_EmergencyCounts.to_html(index=True, classes='data',
      col_space= {'No of Incidents': 10, 'Percent Per Year': 10, '':120}, justify="justify-all")],
      front_overview_EmergencyPlots=ChartJS_XY_Data_EmergencyPlots, 
      ChartJS_X_labels_Emergency_1= ChartJS_X_labels_Emergency_1,
      ChartJS_X_labels_Emergency_2= ChartJS_X_labels_Emergency_2,
      ChartJS_X_labels_Emergency_3= ChartJS_X_labels_Emergency_3,
      ChartJS_Y_values_Emergency=ChartJS_Y_values_Emergency, ChartJS_Y_color_Emergency=ChartJS_Y_color_Emergency,
      ChartJS_X_labels_Incidents=ChartJS_X_labels_Incidents, ChartJS_Y_values_Incidents=ChartJS_Y_values_Incidents)

@app.route("/Dashboard")
@login_required
def ViewDashboard():
   all_HSE_Inv = Server_HSE_MasterDB_Controller.get_dashboard_InvRec()
   flash("Master HSE Database Latest Five HSE Incident")
   return render_template('dashboard.html', all_HSE_Inv  = all_HSE_Inv, name=current_user.username)

@app.route("/PopulateEventBreakdown",  methods = ['GET', 'POST'])
def PopulateEventBreakdown():
   if request.method == 'POST':
      try:
         Eventyear = request.form['Eventyear']
         PopulateEventBreakdownBy_Year =Server_HSE_MasterDB_Controller.PopulateEventBreakdownBy_Year(Eventyear)
         TotalEntries= PopulateEventBreakdownBy_Year[0]
         Classification_DF_Report = PopulateEventBreakdownBy_Year[1]
         HSE_CrewManagerDFReport = PopulateEventBreakdownBy_Year[2]
         HSE_MonthlyBreakdownReport = PopulateEventBreakdownBy_Year[3]
         HSE_HSE_JobNameReport = PopulateEventBreakdownBy_Year[4]
         HSE_RecordablReport= PopulateEventBreakdownBy_Year[5]
         HSE_RiskLevelReport= PopulateEventBreakdownBy_Year[6]
         HSE_UnsafeActReport = PopulateEventBreakdownBy_Year[7]
      except:
         flash("Populated HSE Event Break Down by Year Failed")
      finally:
         return render_template('eventBreakdown.html', TotalEntries=TotalEntries, Eventyear=Eventyear,
         Classification_DF_Report = [Classification_DF_Report.to_html(index=False, classes='data',
         col_space= {'Event Classification': 250, 'Count': 200, 'Percent':200}, justify="justify-all")], 
         
         HSE_CrewManagerDFReport=[HSE_CrewManagerDFReport.to_html(index=False, classes='data',
         col_space= {'Manager Name': 250, 'Project Number': 250, 'Count': 200, 'Percent':200}, justify="justify-all")],

         HSE_MonthlyBreakdownReport=[HSE_MonthlyBreakdownReport.to_html(index=False, classes='data',
         col_space= {'Event By Month': 250, 'Count': 200, 'Percent':200}, justify="justify-all")],
         
         HSE_HSE_JobNameReport=[HSE_HSE_JobNameReport.to_html(index=False, classes='data',
         col_space= {'Project Name': 250, 'Project Number': 250, 'Count': 200, 'Percent':200}, justify="justify-all")],
         
         HSE_RecordablReport=[HSE_RecordablReport.to_html(index=False, classes='data',
         col_space= {'Recordable Index': 250, 'WCB Case': 200, 'Count':200}, justify="justify-all")],

         HSE_RiskLevelReport=[HSE_RiskLevelReport.to_html(index=False, classes='data',
         col_space= {'Emergency Level': 250, 'Count': 200, 'Percent':200}, justify="justify-all")],
         
         HSE_UnsafeActReport=[HSE_UnsafeActReport.to_html(index=False, classes='data',
         col_space= {'Unsafe Act': 250, 'Unsafe Condition': 250, 'Count': 200, 'Percent':200}, justify="justify-all")]
         )

@app.route("/ViewCrewReportYear",  methods = ['GET', 'POST'])
def ViewCrewReportYear():
   if request.method == 'POST':
      try:
         Projectyear = request.form['Projectyear']
         ViewCrewReportBy_Year =Server_HSE_MasterDB_Controller.ViewCrewReportBy_Year(Projectyear)
         TotalProjectEntries = ViewCrewReportBy_Year[0]
         ViewJobReportBy_Year_DF_Report= ViewCrewReportBy_Year[1]
         ViewJobRecordable_By_Year_DF_Report= ViewCrewReportBy_Year[2]
         CrewTotal_WCB_Report=ViewCrewReportBy_Year[3]
         CrewTotal_UnsafeAct_Report=ViewCrewReportBy_Year[4]
         
      except:
         flash("Populated HSE Project Report by Year Failed")
      finally:
         return render_template('viewCrewReport.html' , Projectyear=Projectyear, TotalProjectEntries=TotalProjectEntries,
         ViewJobReportBy_Year_DF_Report = [ViewJobReportBy_Year_DF_Report.to_html(index=True, classes='data',
         col_space= {'No of Classified Incidents': 2, '':150}, justify="justify-all")],
         
         ViewJobRecordable_By_Year_DF_Report = [ViewJobRecordable_By_Year_DF_Report.to_html(index=True, classes='data',
         col_space= {'No of Recordable Incidents': 2, '':180}, justify="justify-all")],
         
         CrewTotal_WCB_Report = [CrewTotal_WCB_Report.to_html(index=True, classes='data',
         col_space= {'No of WCB Incidents':150,  '':180}, justify="justify-all")],
         
         CrewTotal_UnsafeAct_Report = [CrewTotal_UnsafeAct_Report.to_html(index=True, classes='data',
         col_space= {'No of UnsafeAct Incidents':150,  '':180}, justify="justify-all")],)

@app.route("/ViewCountryReportYear",  methods = ['GET', 'POST'])
def ViewCountryReportYear():
   if request.method == 'POST':
      try:
         CountryEventyear = request.form['CountryEvent']
         ViewCountryReportBy_Year =Server_HSE_MasterDB_Controller.ViewCountryReportBy_Year(CountryEventyear)
         TotalEntries         = ViewCountryReportBy_Year[1]
         ViewCountryReport    = ViewCountryReportBy_Year[0]
         HSE_EmergencyLevelDF_Pivot = ViewCountryReportBy_Year[2]
         ViewCountryReport_Plot= ViewCountryReportBy_Year[3]

         ChartJS_XY_Data_Country= ViewCountryReport_Plot. filter(['Country', 'No of HSE Incidents']).values
         ChartJS_X_labels_Country = [row[0] for row in ChartJS_XY_Data_Country]
         ChartJS_Y_values_Country = [row[1] for row in ChartJS_XY_Data_Country]
             
      except:
         flash("Populated HSE Project Country Report by Year Failed")
      finally:
         return render_template ( 'viewCountryReport.html', TotalEntries=TotalEntries, CountryEventyear=CountryEventyear,
         ViewCountryReport = [ViewCountryReport.to_html(index=False, classes='data',
         col_space= {'Event Index': 100, 'Country': 200, 'Province/State/Division':200,  
         'No of HSE Incidents': 200, 'Event Percentage (%)':200}, justify="justify-all")],

         HSE_EmergencyLevelDF_Pivot = [HSE_EmergencyLevelDF_Pivot.to_html(index=True, classes='data',
         col_space= {'No of HSE Incidents': 2, 'Event Percentage (%)': 2, '':180}, justify="justify-all")],

         ChartJS_X_labels_Country=ChartJS_X_labels_Country,
         ChartJS_Y_values_Country=ChartJS_Y_values_Country,

         )

@app.route("/viewMasterDB")
def viewMasterDB():
   all_HSE_Inv = Server_HSE_MasterDB_Controller.view_master_InvRec()
   Total_Incident = Server_HSE_MasterDB_Controller.Total_MasterDB_Incident()
   flash("Master HSE Database Loading .... Please Wait to Load The Page .... It takes a While To Load")
   return render_template('viewmasterDB.html', all_HSE_Inv  = all_HSE_Inv, Total_Incident=Total_Incident)

@app.route('/search', methods = ['GET', 'POST'])
def search():
   if request.method == 'POST':
      try:
        id = request.form['id']
        EventDate = request.form['EventDate']
        ProjName = request.form['ProjName']
        ProjNum = request.form['ProjNum']
        ProjLoc = request.form['ProjLoc']

        EmergencyLevel = request.form['EmergencyLevel']
        HSEAdvisorInvestigator = request.form['HSEAdvisorInvestigator']
        HSEIncidentDetails = request.form['HSEIncidentDetails']
        Client = request.form['Client']
        CauseAnalysis = request.form['CauseAnalysis']

        UnsafeAct= request.form['UnsafeAct']
        UnsafeCond = request.form['UnsafeCond']
        EmployeeInvolved = request.form['EmployeeInvolved']
        Classification = request.form['Classification']
        RecordableFAMARWCLTI = request.form['RecordableFAMARWCLTI']
        
        WCBCase = request.form['WCBCase']
        ModifiedDays = request.form['ModifiedDays']
        BodyPart = request.form['BodyPart']
        EquipmentNumber = request.form['EquipmentNumber']
        CACompleted = request.form['CACompleted']
        SignOff = request.form['SignOff']
        
        search_HSE_Inv = Server_HSE_MasterDB_Controller.search_InvRec(id, EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                                                HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, UnsafeAct, \
                                                UnsafeCond, EmployeeInvolved, Classification, RecordableFAMARWCLTI, WCBCase, \
                                                ModifiedDays, BodyPart, EquipmentNumber, CACompleted, SignOff)
        Total_search_HSE_Inv= len(search_HSE_Inv)
        flash("Search Completed Successfully")
      except:
         flash("Incident Search Failed")
      finally:
        return render_template('searchresults.html', search_HSE_Inv  = search_HSE_Inv, Total_search_HSE_Inv=Total_search_HSE_Inv)

@app.route('/delete', methods = ['GET', 'POST'])  
def delete():
   id = request.form["id"]  
   try:
      Server_HSE_MasterDB_Controller.delete_InvRec(id)
      flash("Incident Deleted Successfully") 
   except:
      flash("Incident Cannot Be Deleted") 
   finally:
      return redirect(url_for('ViewDashboard'))

@app.route('/masterDBdelete', methods = ['GET', 'POST'])  
def masterDBdelete():
   id = request.form["id"]  
   try:
      Server_HSE_MasterDB_Controller.delete_InvRec(id)
      flash("Incident Deleted Successfully .... Please Wait to Reload The Page.... Takes a Minute to Reload") 
   except:
      flash("Incident Cannot Be Deleted") 
   finally:
      return redirect(url_for('viewMasterDB'))

@app.route('/masterDBupdate', methods = ['GET', 'POST'])
def masterDBupdate():
   if request.method == 'POST':
      try:
        id = request.form['id']
        EventDate = request.form['EventDate']
        ProjName = request.form['ProjName']
        ProjNum = request.form['ProjNum']
        ProjLoc = request.form['ProjLoc']

        EmergencyLevel = request.form['EmergencyLevel']
        HSEAdvisorInvestigator = request.form['HSEAdvisorInvestigator']
        HSEIncidentDetails = request.form['HSEIncidentDetails']
        Client = request.form['Client']
        CauseAnalysis = request.form['CauseAnalysis']

        UnsafeAct= request.form['UnsafeAct']
        UnsafeCond = request.form['UnsafeCond']
        EmployeeInvolved = request.form['EmployeeInvolved']
        Classification = request.form['Classification']
        RecordableFAMARWCLTI = request.form['RecordableFAMARWCLTI']
        
        WCBCase = request.form['WCBCase']
        ModifiedDays = request.form['ModifiedDays']
        BodyPart = request.form['BodyPart']
        EquipmentNumber = request.form['EquipmentNumber']
        CACompleted = request.form['CACompleted']
        SignOff = request.form['SignOff']
        
        Server_HSE_MasterDB_Controller.update_InvRec(id, EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                                                HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, UnsafeAct, \
                                                UnsafeCond, EmployeeInvolved, Classification, RecordableFAMARWCLTI, WCBCase, \
                                                ModifiedDays, BodyPart, EquipmentNumber, CACompleted, SignOff)
        
        flash("Incident Updated Successfully .... Please Wait to Reload The Page.... Takes a Minute to Reload")
      except:
         flash("Incident Updated Failed")
      finally:
        return redirect(url_for('viewMasterDB'))

@app.route('/update', methods = ['GET', 'POST'])
def update():
   if request.method == 'POST':
      try:
        id = request.form['id']
        EventDate = request.form['EventDate']
        ProjName = request.form['ProjName']
        ProjNum = request.form['ProjNum']
        ProjLoc = request.form['ProjLoc']

        EmergencyLevel = request.form['EmergencyLevel']
        HSEAdvisorInvestigator = request.form['HSEAdvisorInvestigator']
        HSEIncidentDetails = request.form['HSEIncidentDetails']
        Client = request.form['Client']
        CauseAnalysis = request.form['CauseAnalysis']

        UnsafeAct= request.form['UnsafeAct']
        UnsafeCond = request.form['UnsafeCond']
        EmployeeInvolved = request.form['EmployeeInvolved']
        Classification = request.form['Classification']
        RecordableFAMARWCLTI = request.form['RecordableFAMARWCLTI']
        
        WCBCase = request.form['WCBCase']
        ModifiedDays = request.form['ModifiedDays']
        BodyPart = request.form['BodyPart']
        EquipmentNumber = request.form['EquipmentNumber']
        CACompleted = request.form['CACompleted']
        SignOff = request.form['SignOff']
        
        Server_HSE_MasterDB_Controller.update_InvRec(id, EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                                                HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, UnsafeAct, \
                                                UnsafeCond, EmployeeInvolved, Classification, RecordableFAMARWCLTI, WCBCase, \
                                                ModifiedDays, BodyPart, EquipmentNumber, CACompleted, SignOff)
        
        flash("Incident Updated Successfully")
      except:
         flash("Incident Updated Failed")
      finally:
        return redirect(url_for('ViewDashboard'))

@app.route('/insert', methods = ['POST'])
def insert():
   if request.method == 'POST':
      try:
        EventDate = request.form['EventDate']
        ProjName = request.form['ProjName']
        ProjNum = request.form['ProjNum']
        ProjLoc = request.form['ProjLoc']

        EmergencyLevel = request.form['EmergencyLevel']
        HSEAdvisorInvestigator = request.form['HSEAdvisorInvestigator']
        HSEIncidentDetails = request.form['HSEIncidentDetails']
        Client = request.form['Client']
        CauseAnalysis = request.form['CauseAnalysis']

        UnsafeAct= request.form['UnsafeAct']
        UnsafeCond = request.form['UnsafeCond']
        EmployeeInvolved = request.form['EmployeeInvolved']
        Classification = request.form['Classification']
        RecordableFAMARWCLTI = request.form['RecordableFAMARWCLTI']
        
        WCBCase = request.form['WCBCase']
        ModifiedDays = request.form['ModifiedDays']
        BodyPart = request.form['BodyPart']
        EquipmentNumber = request.form['EquipmentNumber']
        CACompleted = request.form['CACompleted']
        SignOff = request.form['SignOff']
        
        Server_HSE_MasterDB_Controller.insert_InvRec(EventDate, ProjName, ProjNum, ProjLoc, EmergencyLevel, \
                                                HSEAdvisorInvestigator, HSEIncidentDetails, Client, CauseAnalysis, UnsafeAct, \
                                                UnsafeCond, EmployeeInvolved, Classification, RecordableFAMARWCLTI, WCBCase, \
                                                ModifiedDays, BodyPart, EquipmentNumber, CACompleted, SignOff)
        
        flash("Incident Added Successfully")
      except:
         flash("Incident Cannot Be Added")
      finally:
        return redirect(url_for('ViewDashboard'))

@app.route("/fileimport",  methods = ['GET', 'POST'])
def fileimport():
   if request.method == 'GET':
      return render_template('import.html')
  
@app.route("/RenderTextCSV",  methods = ['GET', 'POST'])
def RenderTextCSV():
   if request.method ==  'POST':
      try:
         user_csv = request.form.get('user_csv').split('\n')
         reader = csv.DictReader(user_csv)
         DataDF  = []
         results = []
         for row in reader:
            results.append(dict(row))
            DataDF.append(row)
         DataDF = pd.DataFrame(DataDF)
         LenDataDF = len(DataDF)
         Server_HSE_MasterDB_Controller.submitCSVToMasterDB(DataDF)
         fieldnames = [key for key in results[0].keys()]
         flash("Incident Imported Successfully")
         return render_template('importRenderTextCSV.html', results=results, fieldnames=fieldnames, len=len, LenDataDF=LenDataDF)
      except:
         flash("Incident Cannot Be Imported")
   
@app.route("/RenderFileCSV",  methods = ['GET', 'POST'])
def RenderFileCSV():
   if request.method ==  'POST':
      user_csv = request.files['user_csv']
      if user_csv.filename != '':
         file_path = os.path.join(app.config['UPLOAD_FOLDER'], user_csv.filename)
         user_csv.save(file_path)         
      results = []
      DataDF  = []
      with open(file_path) as file:
         csvfile =csv.DictReader(file)          
         for row in csvfile:
            results.append(dict(row))
            DataDF.append(row)   
      fieldnames = [key for key in results[0].keys()]
      DataDF = pd.DataFrame(DataDF)
      LenDataDF = len(DataDF)
      DataDF.rename(columns={"ï»¿EventDate":'EventDate'},inplace = True)
      Server_HSE_MasterDB_Controller.submitCSVToMasterDB(DataDF)
      flash("Incident Imported Successfully")
      return render_template('importRenderFileCSV.html',  results=results, fieldnames=fieldnames, len=len, LenDataDF=LenDataDF)
   
@app.route("/paginateviewMasterDB")
def paginateviewMasterDB():
   all_HSE_Inv = Server_HSE_MasterDB_Controller.view_master_InvRec()
   Total_Incident = Server_HSE_MasterDB_Controller.Total_MasterDB_Incident()
   return render_template('paginateviewMasterDB.html', all_HSE_Inv=all_HSE_Inv, Total_Incident=Total_Incident)

@app.route('/genProjectMapAll', methods = ['GET', 'POST'])  
def genProjectMapAll():
   try:
      Server_HSE_MasterDB_Controller.submitProjectMapToMasterDB()
      flash("Project Map Lat Long Generated Successfully, Click on View Map to see the Map View") 
   except:
      flash("Project Map Lat Long Generated Unsuccessful") 
   finally:
      return redirect(url_for('ViewDashboard'))
   
@app.route("/PopulateProjectMap",  methods = ['GET', 'POST'])
def PopulateProjectMap():
   if request.method == 'POST':
      try:
         ProjectMapYear = request.form['Projectmap']
         EventYear = ProjectMapYear
         populateMapDataBy_Year =Server_HSE_MasterDB_Controller.populateMapDataBy_Year(EventYear)
         data = pd.DataFrame(populateMapDataBy_Year)
         data.rename(columns={5:'Incidents_Count'},inplace = True)
         NumberOfProject=len(populateMapDataBy_Year)
         Incidents_Count= data.Incidents_Count.sum()
        
      except:
         flash("Populated HSE Project Map Report by Year Failed")
      finally:
         return render_template('populateMapData.html' , populateMapDataBy_Year=populateMapDataBy_Year, 
         ProjectMapYear=ProjectMapYear, NumberOfProject=NumberOfProject, Incidents_Count=Incidents_Count)

@app.route('/updateProjectMapData', methods = ['GET', 'POST'])
def updateProjectMapData():
   if request.method == 'POST':
      try:
        Proj_id = request.form['Proj_id']
        ProjectName = request.form['ProjectName']
        ProjectNumber = request.form['ProjectNumber']
        ProjectLocation = request.form['ProjectLocation']
        EventYear = request.form['EventYear']

        Incidents_Count = request.form['Incidents_Count']
        Latitude = request.form['Latitude']
        Longitude = request.form['Longitude']
      
        Server_HSE_MasterDB_Controller.update_ProjMapRec(Proj_id, ProjectName, ProjectNumber, ProjectLocation, EventYear, Incidents_Count, \
                    Latitude, Longitude)
        
        flash("Project Map Data Updated Updated Successfully")
      except:
         flash("Project Map Data Updated Failed")
      finally:
        return redirect(url_for('ViewDashboard'))

@app.route('/deleteProjectMapData', methods = ['GET', 'POST'])  
def deleteProjectMapData():
   Proj_id = request.form["Proj_id"]  
   try:
      Server_HSE_MasterDB_Controller.delete_ProjMapRec(Proj_id)
      flash("Project Map Data Deleted Successfully") 
   except:
      flash("Project Map Data Cannot Be Deleted") 
   finally:
      return redirect(url_for('ViewDashboard'))

@app.route("/ViewProjectMap",  methods = ['GET', 'POST'])
def ViewProjectMap():
   if request.method == 'POST':
      try:
         ProjectMapYear = request.form['ProjectMapYear']
         folium_map= Server_HSE_MasterDB_Controller.viewMapBy_Year(ProjectMapYear)

      except:
         flash("Project Map View Failed")
      finally:
         return render_template('viewProjectMap.html', folium_map=folium_map._repr_html_())

@app.route("/Analysisdata")
@login_required
def HSEDataAnalysis():
   return render_template('analysisdata.html', name=current_user.username,)

@app.route("/AnnualEventSummary",  methods = ['GET', 'POST'])
def AnnualEventSummary():
   HSE_Report_Class = request.form['HSE_Report_Class']
   EventSummaryYear = request.form['EventSummaryYear']
   EventSummaryPreparedBy = request.form['EventSummaryPreparedBy']
   EventSummaryPreparedDate = request.form['EventSummaryPreparedDate']
   AnnualEventSummary =Server_HSE_MasterDB_Analysis.Annual_EventSummary(EventSummaryYear)
   TotalEntries= AnnualEventSummary[0]
   HSE_RecordablReport_Merge = AnnualEventSummary[1]
   HSE_ClassificationReport_Merge = AnnualEventSummary[2]
   HSE_EmergencyReport_Merge_All =  AnnualEventSummary[3]
   HSE_MonthlyBreakdownReport_Merge= AnnualEventSummary[4]
   HSE_CrewManagerDFReport_Merge= AnnualEventSummary[5]
   HSE_UnsafeActReport_Merge= AnnualEventSummary[6]
   HSE_UnsafeActReport_Merge_Chart = pd.DataFrame(HSE_UnsafeActReport_Merge)
   HSE_UnsafeActReport_Merge = HSE_UnsafeActReport_Merge.loc[:,
                                    ['Event Index','HSE Unsafe Act','Event Count','Event Percentage (%)']]
   HSE_UnsafeCondReport_Merge = AnnualEventSummary[7]
   HSE_UnsafeCondReport_Merge_Chart = pd.DataFrame(HSE_UnsafeCondReport_Merge)
   HSE_UnsafeCondReport_Merge = HSE_UnsafeCondReport_Merge.loc[:,
                                    ['Event Index','HSE Unsafe Condition','Event Count','Event Percentage (%)']]

   if request.method == 'POST':
      if HSE_Report_Class   == '1':
         try:
            HSE_EmergencyReport_Merge = HSE_EmergencyReport_Merge_All.loc[:,
                                       ['Event Index','HSE Emergency Event','Event Count','Event Percentage (%)']]
            HSE_EmergencyReport_Merge = HSE_EmergencyReport_Merge.reset_index(drop=True)

            ChartJS_XY_Data_Recordable= HSE_RecordablReport_Merge. filter(['HSE Recordable Event', 'Event Count']).values
            ChartJS_X_labels_Recordable = [row[0] for row in ChartJS_XY_Data_Recordable]
            ChartJS_Y_values_Recordable = [row[1] for row in ChartJS_XY_Data_Recordable]

            ChartJS_XY_Data_Classification= HSE_ClassificationReport_Merge.filter(['HSE Classified Event', 'Event Count']).values
            ChartJS_X_labels_Classification = [row[0] for row in ChartJS_XY_Data_Classification]
            ChartJS_Y_values_Classification = [row[1] for row in ChartJS_XY_Data_Classification]

            ChartJS_XY_Data_Emergency= HSE_EmergencyReport_Merge_All.filter(['HSE Emergency Event', 'Event Count', 'Emergency_Color']).values
            ChartJS_X_labels_Emergency = [row[0] for row in ChartJS_XY_Data_Emergency]
            ChartJS_Y_values_Emergency = [row[1] for row in ChartJS_XY_Data_Emergency]
            ChartJS_Y_colors_Emergency = [row[2] for row in ChartJS_XY_Data_Emergency]            
         except:
            flash("Populated Annual Event Summary by Year Failed")
         finally:
            return render_template('annualEventSummary_Class_A.html', EventSummaryYear=EventSummaryYear, EventSummaryPreparedBy=EventSummaryPreparedBy, 
            EventSummaryPreparedDate=EventSummaryPreparedDate, TotalEntries=TotalEntries,

            HSE_RecordablReport_Merge = [HSE_RecordablReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Recordable Event': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_Recordable=ChartJS_X_labels_Recordable, ChartJS_Y_values_Recordable=ChartJS_Y_values_Recordable,

            HSE_ClassificationReport_Merge = [HSE_ClassificationReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Classified Event': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_Classification=ChartJS_X_labels_Classification, ChartJS_Y_values_Classification=ChartJS_Y_values_Classification,

            HSE_EmergencyReport_Merge = [HSE_EmergencyReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Emergency Event': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_Emergency=ChartJS_X_labels_Emergency, ChartJS_Y_values_Emergency=ChartJS_Y_values_Emergency,
            ChartJS_Y_colors_Emergency=ChartJS_Y_colors_Emergency,
            )
      elif HSE_Report_Class == '2':
         try:
            ChartJS_XY_Data_MonthlyBreakdown= HSE_MonthlyBreakdownReport_Merge.filter(['HSE Event By Month', 'Event Count']).values
            ChartJS_X_labels_MonthlyBreakdown = [row[0] for row in ChartJS_XY_Data_MonthlyBreakdown]
            ChartJS_Y_values_MonthlyBreakdown = [row[1] for row in ChartJS_XY_Data_MonthlyBreakdown]

            ChartJS_XY_Data_CrewManager= HSE_CrewManagerDFReport_Merge.filter(['HSE Project Manager', 'Event Count']).values
            ChartJS_X_labels_CrewManager = [row[0] for row in ChartJS_XY_Data_CrewManager]
            ChartJS_Y_values_CrewManager = [row[1] for row in ChartJS_XY_Data_CrewManager]
           
         except:
            flash("Populated Monthly Event Summary by Year Failed")
         finally:
            return render_template('annualEventSummary_Class_B.html', EventSummaryYear=EventSummaryYear, EventSummaryPreparedBy=EventSummaryPreparedBy, 
            EventSummaryPreparedDate=EventSummaryPreparedDate, TotalEntries=TotalEntries,

            HSE_MonthlyBreakdownReport_Merge = [HSE_MonthlyBreakdownReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Event By Month': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_MonthlyBreakdown=ChartJS_X_labels_MonthlyBreakdown, ChartJS_Y_values_MonthlyBreakdown=ChartJS_Y_values_MonthlyBreakdown,

            HSE_CrewManagerDFReport_Merge = [HSE_CrewManagerDFReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Project Manager': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_CrewManager=ChartJS_X_labels_CrewManager, ChartJS_Y_values_CrewManager=ChartJS_Y_values_CrewManager,

            )
      elif HSE_Report_Class == '3':
         try:
            ChartJS_XY_Data_UnsafeAct= HSE_UnsafeActReport_Merge_Chart.filter(['HSE Unsafe Act', 'Event Count' , 'UnsafeAct_Color']).values
            ChartJS_X_labels_UnsafeAct = [row[0] for row in ChartJS_XY_Data_UnsafeAct]
            ChartJS_Y_values_UnsafeAct = [row[1] for row in ChartJS_XY_Data_UnsafeAct]
            ChartJS_Y_Color_UnsafeAct = [row[2] for row in ChartJS_XY_Data_UnsafeAct]
            ChartJS_XY_Data_UnsafeCond= HSE_UnsafeCondReport_Merge_Chart.filter(['HSE Unsafe Condition', 'Event Count', 'UnsafeCond_Color']).values
            ChartJS_X_labels_UnsafeCond = [row[0] for row in ChartJS_XY_Data_UnsafeCond]
            ChartJS_Y_values_UnsafeCond = [row[1] for row in ChartJS_XY_Data_UnsafeCond]
            ChartJS_Y_Color_UnsafeCond = [row[2] for row in ChartJS_XY_Data_UnsafeCond]           
         except:
            flash("Populated Monthly Event Summary by Year Failed")
         finally:
            return render_template('annualEventSummary_Class_C.html', EventSummaryYear=EventSummaryYear, EventSummaryPreparedBy=EventSummaryPreparedBy, 
            EventSummaryPreparedDate=EventSummaryPreparedDate, TotalEntries=TotalEntries,

            HSE_UnsafeActReport_Merge = [HSE_UnsafeActReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Unsafe Act': 220, 'Event Count':110, 'Event Percentage (%)':200}, justify="justify-all")],
            ChartJS_X_labels_UnsafeAct=ChartJS_X_labels_UnsafeAct, ChartJS_Y_values_UnsafeAct=ChartJS_Y_values_UnsafeAct,
            ChartJS_Y_Color_UnsafeAct=ChartJS_Y_Color_UnsafeAct,

            HSE_UnsafeCondReport_Merge = [HSE_UnsafeCondReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Unsafe Condition': 220, 'Event Count':110, 'Event Percentage (%)':200}, justify="justify-all")],
            ChartJS_X_labels_UnsafeCond=ChartJS_X_labels_UnsafeCond, ChartJS_Y_values_UnsafeCond=ChartJS_Y_values_UnsafeCond,
            ChartJS_Y_Color_UnsafeCond=ChartJS_Y_Color_UnsafeCond,

            )
      else:
          return redirect(url_for('HSEDataAnalysis'))

@app.route("/AnnualProjectSummary",  methods = ['GET', 'POST'])
def AnnualProjectSummary():
   HSE_Project_Report_Class = request.form['Project_Report_Class']
   ProjectSummaryYear = request.form['ProjectSummaryYear']
   ProjectSummaryPreparedBy = request.form['ProjectSummaryPreparedBy']
   ProjectSummaryPreparedDate = request.form['ProjectSummaryPreparedDate']
   ProjectEventSummary =Server_HSE_MasterDB_Analysis.Annual_ProjectSummary(ProjectSummaryYear)
   TotalEntries= ProjectEventSummary[0]

   ## Class A
   ViewJobReportBy_Classification_Plot= ProjectEventSummary[1]
   ViewJobReportBy_Classification_Pivot= ProjectEventSummary[2]
   ViewJobReportBy_Recordable_Pivot= ProjectEventSummary[3]
   ViewJobReportBy_Recordable_Plot = ProjectEventSummary[4]
   HSE_EmergencyLevelDF_Pivot= ProjectEventSummary[5]
   HSE_EmergencyLevelDF_Plot = ProjectEventSummary[6]

   ## Class B
   HSE_WCB_Report_Pivot= ProjectEventSummary[7]
   HSE_WCB_Report_Plot = ProjectEventSummary[8]
   HSE_UnsafeAct_Report_Pivot= ProjectEventSummary[9]
   HSE_UnsafeAct_Report_Plot = ProjectEventSummary[10]
   HSE_UnsafeCond_Report_Pivot= ProjectEventSummary[11]
   HSE_UnsafeCond_Report_Plot = ProjectEventSummary[12]

   ## Class C
   HSE_CrewReport= ProjectEventSummary[13]
   HSE_CrewReport_Table = HSE_CrewReport.loc[:,
                                    ['Event Index','Project Name','Project Number', 'Project Location', 'No of HSE Incidents', 'Event Percentage (%)']]

   if request.method == 'POST':
      if HSE_Project_Report_Class   == '1':
         try:
            ViewJobReportBy_Classification_Plot= ViewJobReportBy_Classification_Plot.filter(['Project Name', 'Classification', 'No of Classified Incidents', 'Classified_Color', 'Project_Classification']).values
            ChartJS_X_labels_Classification_Plot_1 = [row[0] for row in ViewJobReportBy_Classification_Plot]
            ChartJS_X_labels_Classification_Plot_2 = [row[1] for row in ViewJobReportBy_Classification_Plot]
            ChartJS_Y_values_Classification_Plot   = [row[2] for row in ViewJobReportBy_Classification_Plot]
            ChartJS_Y_color_Classification_Plot    = [row[3] for row in ViewJobReportBy_Classification_Plot]
            ChartJS_X_labels_Classification_Plot_1_2 = [row[4] for row in ViewJobReportBy_Classification_Plot]

            ViewJobReportBy_Recordable_Plot= ViewJobReportBy_Recordable_Plot.filter(['Project Name', 'Recordable', 'No of Recordable Incidents', 
            'Recordable_Color', 'Project_Recordable']).values
            ChartJS_X_labels_Recordable_Plot_1 = [row[0] for row in ViewJobReportBy_Recordable_Plot]
            ChartJS_X_labels_Recordable_Plot_2 = [row[1] for row in ViewJobReportBy_Recordable_Plot]
            ChartJS_Y_values_Recordable_Plot   = [row[2] for row in ViewJobReportBy_Recordable_Plot]
            ChartJS_Y_color_Recordable_Plot    = [row[3] for row in ViewJobReportBy_Recordable_Plot]
            ChartJS_X_labels_Recordable_Plot_1_2 = [row[4] for row in ViewJobReportBy_Recordable_Plot]

            ViewJobReportBy_Emergency_Plot= HSE_EmergencyLevelDF_Plot.filter(['Project Name', 'Emergency Level', 'No Of EmergencyLevel Incidents', 
            'Emergency_Color', 'Project_Emergency']).values
            ChartJS_X_labels_Emergency_Plot_1 = [row[0] for row in ViewJobReportBy_Emergency_Plot]
            ChartJS_X_labels_Emergency_Plot_2 = [row[1] for row in ViewJobReportBy_Emergency_Plot]
            ChartJS_Y_values_Emergency_Plot   = [row[2] for row in ViewJobReportBy_Emergency_Plot]
            ChartJS_Y_color_Emergency_Plot    = [row[3] for row in ViewJobReportBy_Emergency_Plot]
            ChartJS_X_labels_Emergency_Plot_1_2 = [row[4] for row in ViewJobReportBy_Emergency_Plot]
                       
         except:
            flash("Populated Annual Project Summary by Year Failed")
         finally:
            return render_template('annualProjectSummary_Class_A.html', ProjectSummaryYear=ProjectSummaryYear, ProjectSummaryPreparedBy=ProjectSummaryPreparedBy, 
            ProjectSummaryPreparedDate=ProjectSummaryPreparedDate, TotalEntries=TotalEntries,
            
            ViewJobReportBy_Classification_Pivot = [ViewJobReportBy_Classification_Pivot.to_html(index=True, classes='data',
            col_space= {'No of Classified Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_Classification_Plot_1=ChartJS_X_labels_Classification_Plot_1,
            ChartJS_X_labels_Classification_Plot_2=ChartJS_X_labels_Classification_Plot_2,
            ChartJS_Y_values_Classification_Plot=ChartJS_Y_values_Classification_Plot,
            ChartJS_Y_color_Classification_Plot   = ChartJS_Y_color_Classification_Plot,
            ChartJS_X_labels_Classification_Plot_1_2=ChartJS_X_labels_Classification_Plot_1_2,

            ViewJobReportBy_Recordable_Pivot = [ViewJobReportBy_Recordable_Pivot.to_html(index=True, classes='data',
            col_space= {'No of Recordable Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_Recordable_Plot_1=ChartJS_X_labels_Recordable_Plot_1,
            ChartJS_X_labels_Recordable_Plot_2=ChartJS_X_labels_Recordable_Plot_2,
            ChartJS_Y_values_Recordable_Plot=ChartJS_Y_values_Recordable_Plot,
            ChartJS_Y_color_Recordable_Plot   = ChartJS_Y_color_Recordable_Plot,
            ChartJS_X_labels_Recordable_Plot_1_2=ChartJS_X_labels_Recordable_Plot_1_2,

            HSE_EmergencyLevelDF_Pivot = [HSE_EmergencyLevelDF_Pivot.to_html(index=True, classes='data',
            col_space= {'No Of EmergencyLevel Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_Emergency_Plot_1=ChartJS_X_labels_Emergency_Plot_1,
            ChartJS_X_labels_Emergency_Plot_2=ChartJS_X_labels_Emergency_Plot_2,
            ChartJS_Y_values_Emergency_Plot=ChartJS_Y_values_Emergency_Plot,
            ChartJS_Y_color_Emergency_Plot   = ChartJS_Y_color_Emergency_Plot,
            ChartJS_X_labels_Emergency_Plot_1_2=ChartJS_X_labels_Emergency_Plot_1_2,
            )

      elif HSE_Project_Report_Class == '2':
         try:
            HSE_WCB_Report_Plot= HSE_WCB_Report_Plot.filter(['Project Name', 'WCBCase', 'No of WCB Incidents', 
            'WCB_Color', 'Project_WCB']).values
            ChartJS_X_labels_WCB_Plot_1 = [row[0] for row in HSE_WCB_Report_Plot]
            ChartJS_X_labels_WCB_Plot_2 = [row[1] for row in HSE_WCB_Report_Plot]
            ChartJS_Y_values_WCB_Plot   = [row[2] for row in HSE_WCB_Report_Plot]
            ChartJS_Y_color_WCB_Plot    = [row[3] for row in HSE_WCB_Report_Plot]
            ChartJS_X_labels_WCB_Plot_1_2 = [row[4] for row in HSE_WCB_Report_Plot]

            HSE_UnsafeAct_Report_Plot= HSE_UnsafeAct_Report_Plot.filter(['Project Name', 'UnsafeAct', 'No of UnsafeAct Incidents', 
            'UnsafeAct_Color', 'Project_UnsafeAct']).values
            ChartJS_X_labels_UnsafeAct_Plot_1 = [row[0] for row in HSE_UnsafeAct_Report_Plot]
            ChartJS_X_labels_UnsafeAct_Plot_2 = [row[1] for row in HSE_UnsafeAct_Report_Plot]
            ChartJS_Y_values_UnsafeAct_Plot   = [row[2] for row in HSE_UnsafeAct_Report_Plot]
            ChartJS_Y_color_UnsafeAct_Plot    = [row[3] for row in HSE_UnsafeAct_Report_Plot]
            ChartJS_X_labels_UnsafeAct_Plot_1_2 = [row[4] for row in HSE_UnsafeAct_Report_Plot]


            HSE_UnsafeCond_Report_Plot= HSE_UnsafeCond_Report_Plot.filter(['Project Name', 'UnsafeCond', 'No of UnsafeCond Incidents', 
            'UnsafeCond_Color', 'Project_UnsafeCond']).values
            ChartJS_X_labels_UnsafeCond_Plot_1 = [row[0] for row in HSE_UnsafeCond_Report_Plot]
            ChartJS_X_labels_UnsafeCond_Plot_2 = [row[1] for row in HSE_UnsafeCond_Report_Plot]
            ChartJS_Y_values_UnsafeCond_Plot   = [row[2] for row in HSE_UnsafeCond_Report_Plot]
            ChartJS_Y_color_UnsafeCond_Plot    = [row[3] for row in HSE_UnsafeCond_Report_Plot]
            ChartJS_X_labels_UnsafeCond_Plot_1_2 = [row[4] for row in HSE_UnsafeCond_Report_Plot]
           
         except:
            flash("Populated Annual Project Summary by Year Failed")
         finally:
            return render_template('annualProjectSummary_Class_B.html',  ProjectSummaryYear=ProjectSummaryYear, ProjectSummaryPreparedBy=ProjectSummaryPreparedBy, 
            ProjectSummaryPreparedDate=ProjectSummaryPreparedDate, TotalEntries=TotalEntries,

            HSE_WCB_Report_Pivot = [HSE_WCB_Report_Pivot.to_html(index=True, classes='data',
            col_space= {'No of WCB Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_WCB_Plot_1=ChartJS_X_labels_WCB_Plot_1,
            ChartJS_X_labels_WCB_Plot_2=ChartJS_X_labels_WCB_Plot_2,
            ChartJS_Y_values_WCB_Plot=ChartJS_Y_values_WCB_Plot,
            ChartJS_Y_color_WCB_Plot   = ChartJS_Y_color_WCB_Plot,
            ChartJS_X_labels_WCB_Plot_1_2=ChartJS_X_labels_WCB_Plot_1_2,

            HSE_UnsafeAct_Report_Pivot = [HSE_UnsafeAct_Report_Pivot.to_html(index=True, classes='data',
            col_space= {'No of UnsafeAct Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_UnsafeAct_Plot_1=ChartJS_X_labels_UnsafeAct_Plot_1,
            ChartJS_X_labels_UnsafeAct_Plot_2=ChartJS_X_labels_UnsafeAct_Plot_2,
            ChartJS_Y_values_UnsafeAct_Plot=ChartJS_Y_values_UnsafeAct_Plot,
            ChartJS_Y_color_UnsafeAct_Plot   = ChartJS_Y_color_UnsafeAct_Plot,
            ChartJS_X_labels_UnsafeAct_Plot_1_2=ChartJS_X_labels_UnsafeAct_Plot_1_2,

            HSE_UnsafeCond_Report_Pivot = [HSE_UnsafeCond_Report_Pivot.to_html(index=True, classes='data',
            col_space= {'No of UnsafeCond Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_UnsafeCond_Plot_1=ChartJS_X_labels_UnsafeCond_Plot_1,
            ChartJS_X_labels_UnsafeCond_Plot_2=ChartJS_X_labels_UnsafeCond_Plot_2,
            ChartJS_Y_values_UnsafeCond_Plot=ChartJS_Y_values_UnsafeCond_Plot,
            ChartJS_Y_color_UnsafeCond_Plot   = ChartJS_Y_color_UnsafeCond_Plot,
            ChartJS_X_labels_UnsafeCond_Plot_1_2=ChartJS_X_labels_UnsafeCond_Plot_1_2,
            )
      
      elif HSE_Project_Report_Class == '3':
         try:
            HSE_CrewReport_Plot= HSE_CrewReport.filter(['Project Name', 'Project Number', 'No of HSE Incidents', 'Join']).values
            ChartJS_X_labels_CrewReport_Plot_1 = [row[0] for row in HSE_CrewReport_Plot]
            ChartJS_X_labels_CrewReport_Plot_2 = [row[1] for row in HSE_CrewReport_Plot]
            ChartJS_Y_values_CrewReport_Plot   = [row[2] for row in HSE_CrewReport_Plot]
            ChartJS_X_labels_CrewReport_Plot_1_2 = [row[3] for row in HSE_CrewReport_Plot]         
         except:
            flash("Populated Annual Project Summary by Year Failed")
         finally:
            return render_template('annualProjectSummary_Class_C.html',  ProjectSummaryYear=ProjectSummaryYear, ProjectSummaryPreparedBy=ProjectSummaryPreparedBy, 
            ProjectSummaryPreparedDate=ProjectSummaryPreparedDate, TotalEntries=TotalEntries,

            HSE_CrewReport_Table = [HSE_CrewReport_Table.to_html(index=False, classes='data',
            col_space= {'Event Index': 180, 'Project Name': 260, 'Project Number': 220,'Project Location': 220,
            'No of HSE Incidents':220, 'Event Percentage (%)':220}, justify="justify-all")],
            ChartJS_X_labels_CrewReport_Plot_1=ChartJS_X_labels_CrewReport_Plot_1, ChartJS_X_labels_CrewReport_Plot_2=ChartJS_X_labels_CrewReport_Plot_2,
            ChartJS_Y_values_CrewReport_Plot=ChartJS_Y_values_CrewReport_Plot, ChartJS_X_labels_CrewReport_Plot_1_2=ChartJS_X_labels_CrewReport_Plot_1_2,
            
            )
      else:
          return redirect(url_for('HSEDataAnalysis'))

@app.route("/SegmentedEventSummary",  methods = ['GET', 'POST'])
def SegmentedEventSummary():
   HSE_Report_Class = request.form['HSE_Report_Class']
   EventSummaryYear = request.form['EventSegYear']
   EventSegName = request.form['EventSegName']
   EventSegStartDate = request.form['EventSegStartDate']
   EventSegEndDate = request.form['EventSegEndDate']
   EventSummaryPreparedBy = request.form['EventSegPreparedBy']
   EventSummaryPreparedDate = request.form['EventSegPreparedDate']
   AnnualEventSummary =Server_HSE_MasterDB_Analysis.Segmented_EventSummary(EventSummaryYear, EventSegStartDate, EventSegEndDate)
   TotalEntries= AnnualEventSummary[0]
   ## Class A
   HSE_RecordablReport_Merge = AnnualEventSummary[1]
   HSE_ClassificationReport_Merge = AnnualEventSummary[2]
   HSE_EmergencyReport_Merge_All =  AnnualEventSummary[3]
   ## Class B
   HSE_MonthlyBreakdownReport_Merge= AnnualEventSummary[4]
   HSE_CrewManagerDFReport_Merge= AnnualEventSummary[5]
   ## Class C
   HSE_UnsafeActReport_Merge= AnnualEventSummary[6]
   HSE_UnsafeActReport_Merge_Chart = pd.DataFrame(HSE_UnsafeActReport_Merge)
   HSE_UnsafeActReport_Merge = HSE_UnsafeActReport_Merge.loc[:,
                                    ['Event Index','HSE Unsafe Act','Event Count','Event Percentage (%)']]
   HSE_UnsafeCondReport_Merge = AnnualEventSummary[7]
   HSE_UnsafeCondReport_Merge_Chart = pd.DataFrame(HSE_UnsafeCondReport_Merge)
   HSE_UnsafeCondReport_Merge = HSE_UnsafeCondReport_Merge.loc[:,
                                    ['Event Index','HSE Unsafe Condition','Event Count','Event Percentage (%)']]
   if request.method == 'POST':
      if HSE_Report_Class   == '1':
         try:
            HSE_EmergencyReport_Merge = HSE_EmergencyReport_Merge_All.loc[:,
                                       ['Event Index','HSE Emergency Event','Event Count','Event Percentage (%)']]
            HSE_EmergencyReport_Merge = HSE_EmergencyReport_Merge.reset_index(drop=True)

            ChartJS_XY_Data_Recordable= HSE_RecordablReport_Merge. filter(['HSE Recordable Event', 'Event Count']).values
            ChartJS_X_labels_Recordable = [row[0] for row in ChartJS_XY_Data_Recordable]
            ChartJS_Y_values_Recordable = [row[1] for row in ChartJS_XY_Data_Recordable]

            ChartJS_XY_Data_Classification= HSE_ClassificationReport_Merge.filter(['HSE Classified Event', 'Event Count']).values
            ChartJS_X_labels_Classification = [row[0] for row in ChartJS_XY_Data_Classification]
            ChartJS_Y_values_Classification = [row[1] for row in ChartJS_XY_Data_Classification]

            ChartJS_XY_Data_Emergency= HSE_EmergencyReport_Merge_All.filter(['HSE Emergency Event', 'Event Count', 'Emergency_Color']).values
            ChartJS_X_labels_Emergency = [row[0] for row in ChartJS_XY_Data_Emergency]
            ChartJS_Y_values_Emergency = [row[1] for row in ChartJS_XY_Data_Emergency]
            ChartJS_Y_colors_Emergency = [row[2] for row in ChartJS_XY_Data_Emergency]            
         except:
            flash("Populated Annual Segmented Event Summary by Year Failed")
         finally:
            return render_template('segmentEventSummary_Class_A.html', EventSummaryYear=EventSummaryYear, EventSummaryPreparedBy=EventSummaryPreparedBy, 
            EventSummaryPreparedDate=EventSummaryPreparedDate, TotalEntries=TotalEntries, EventSegName=EventSegName, EventSegStartDate=EventSegStartDate,
            EventSegEndDate=EventSegEndDate,

            HSE_RecordablReport_Merge = [HSE_RecordablReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Recordable Event': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_Recordable=ChartJS_X_labels_Recordable, ChartJS_Y_values_Recordable=ChartJS_Y_values_Recordable,

            HSE_ClassificationReport_Merge = [HSE_ClassificationReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Classified Event': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_Classification=ChartJS_X_labels_Classification, ChartJS_Y_values_Classification=ChartJS_Y_values_Classification,

            HSE_EmergencyReport_Merge = [HSE_EmergencyReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Emergency Event': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_Emergency=ChartJS_X_labels_Emergency, ChartJS_Y_values_Emergency=ChartJS_Y_values_Emergency,
            ChartJS_Y_colors_Emergency=ChartJS_Y_colors_Emergency,
            )
      elif HSE_Report_Class == '2':
         try:
            ChartJS_XY_Data_MonthlyBreakdown= HSE_MonthlyBreakdownReport_Merge.filter(['HSE Event By Month', 'Event Count']).values
            ChartJS_X_labels_MonthlyBreakdown = [row[0] for row in ChartJS_XY_Data_MonthlyBreakdown]
            ChartJS_Y_values_MonthlyBreakdown = [row[1] for row in ChartJS_XY_Data_MonthlyBreakdown]

            ChartJS_XY_Data_CrewManager= HSE_CrewManagerDFReport_Merge.filter(['HSE Project Manager', 'Event Count']).values
            ChartJS_X_labels_CrewManager = [row[0] for row in ChartJS_XY_Data_CrewManager]
            ChartJS_Y_values_CrewManager = [row[1] for row in ChartJS_XY_Data_CrewManager]
           
         except:
            flash("Populated Annual Segmented Event Summary by Year Failed")
         finally:
            return render_template('segmentEventSummary_Class_B.html', EventSummaryYear=EventSummaryYear, EventSummaryPreparedBy=EventSummaryPreparedBy, 
            EventSummaryPreparedDate=EventSummaryPreparedDate, TotalEntries=TotalEntries, EventSegName=EventSegName, EventSegStartDate=EventSegStartDate,
            EventSegEndDate=EventSegEndDate,

            HSE_MonthlyBreakdownReport_Merge = [HSE_MonthlyBreakdownReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Event By Month': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_MonthlyBreakdown=ChartJS_X_labels_MonthlyBreakdown, ChartJS_Y_values_MonthlyBreakdown=ChartJS_Y_values_MonthlyBreakdown,

            HSE_CrewManagerDFReport_Merge = [HSE_CrewManagerDFReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Project Manager': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_CrewManager=ChartJS_X_labels_CrewManager, ChartJS_Y_values_CrewManager=ChartJS_Y_values_CrewManager,

            )
      elif HSE_Report_Class == '3':
         try:
            ChartJS_XY_Data_UnsafeAct= HSE_UnsafeActReport_Merge_Chart.filter(['HSE Unsafe Act', 'Event Count', 'UnsafeAct_Color']).values
            ChartJS_X_labels_UnsafeAct = [row[0] for row in ChartJS_XY_Data_UnsafeAct]
            ChartJS_Y_values_UnsafeAct = [row[1] for row in ChartJS_XY_Data_UnsafeAct]
            ChartJS_Y_Color_UnsafeAct = [row[2] for row in ChartJS_XY_Data_UnsafeAct]
            ChartJS_XY_Data_UnsafeCond= HSE_UnsafeCondReport_Merge_Chart.filter(['HSE Unsafe Condition', 'Event Count','UnsafeCond_Color']).values
            ChartJS_X_labels_UnsafeCond = [row[0] for row in ChartJS_XY_Data_UnsafeCond]
            ChartJS_Y_values_UnsafeCond = [row[1] for row in ChartJS_XY_Data_UnsafeCond]
            ChartJS_Y_Color_UnsafeCond = [row[2] for row in ChartJS_XY_Data_UnsafeCond]           
         except:
            flash("Populated Annual Segmented Event Summary by Year Failed")
         finally:
            return render_template('segmentEventSummary_Class_C.html', EventSummaryYear=EventSummaryYear, EventSummaryPreparedBy=EventSummaryPreparedBy, 
            EventSummaryPreparedDate=EventSummaryPreparedDate, TotalEntries=TotalEntries, EventSegName=EventSegName, EventSegStartDate=EventSegStartDate,
            EventSegEndDate=EventSegEndDate,

            HSE_UnsafeActReport_Merge = [HSE_UnsafeActReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Unsafe Act': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_UnsafeAct=ChartJS_X_labels_UnsafeAct, ChartJS_Y_values_UnsafeAct=ChartJS_Y_values_UnsafeAct,
            ChartJS_Y_Color_UnsafeAct=ChartJS_Y_Color_UnsafeAct,

            HSE_UnsafeCondReport_Merge = [HSE_UnsafeCondReport_Merge.to_html(index=False, classes='data',
            col_space= {'Event Index': 100, 'HSE Unsafe Condition': 220, 'Event Count':110, 'Event Percentage (%)':140}, justify="justify-all")],
            ChartJS_X_labels_UnsafeCond=ChartJS_X_labels_UnsafeCond, ChartJS_Y_values_UnsafeCond=ChartJS_Y_values_UnsafeCond,
            ChartJS_Y_Color_UnsafeCond=ChartJS_Y_Color_UnsafeCond,

            )
      else:
          return redirect(url_for('HSEDataAnalysis'))

@app.route("/SegmentedProjectSummary",  methods = ['GET', 'POST'])
def SegmentedProjectSummary():
   HSE_Project_Report_Class = request.form['Project_Report_Class']
   ProjectSummaryYear = request.form['EventSegYear']
   EventSegName = request.form['EventSegName']
   EventSegStartDate = request.form['EventSegStartDate']
   EventSegEndDate = request.form['EventSegEndDate']
   ProjectSummaryPreparedBy = request.form['EventSegPreparedBy']
   ProjectSummaryPreparedDate = request.form['EventSegPreparedDate']

   ProjectEventSummary =Server_HSE_MasterDB_Analysis.Segmented_ProjectSummary(ProjectSummaryYear, EventSegStartDate, EventSegEndDate)
   TotalEntries= ProjectEventSummary[0]

   ## Class A
   ViewJobReportBy_Classification_Plot= ProjectEventSummary[1]
   ViewJobReportBy_Classification_Pivot= ProjectEventSummary[2]
   ViewJobReportBy_Recordable_Pivot= ProjectEventSummary[3]
   ViewJobReportBy_Recordable_Plot = ProjectEventSummary[4]
   HSE_EmergencyLevelDF_Pivot= ProjectEventSummary[5]
   HSE_EmergencyLevelDF_Plot = ProjectEventSummary[6]

   ## Class B
   HSE_WCB_Report_Pivot= ProjectEventSummary[7]
   HSE_WCB_Report_Plot = ProjectEventSummary[8]
   HSE_UnsafeAct_Report_Pivot= ProjectEventSummary[9]
   HSE_UnsafeAct_Report_Plot = ProjectEventSummary[10]
   HSE_UnsafeCond_Report_Pivot= ProjectEventSummary[11]
   HSE_UnsafeCond_Report_Plot = ProjectEventSummary[12]

   ## Class C
   HSE_CrewReport= ProjectEventSummary[13]
   HSE_CrewReport_Table = HSE_CrewReport.loc[:,['Event Index','Project Name','Project Number', 'Project Location', 
   'No of HSE Incidents', 'Event Percentage (%)']]

   if request.method == 'POST':
      if HSE_Project_Report_Class   == '1':
         try:
            ViewJobReportBy_Classification_Plot= ViewJobReportBy_Classification_Plot.filter(['Project Name', 'Classification', 'No of Classified Incidents', 'Classified_Color', 'Project_Classification']).values
            ChartJS_X_labels_Classification_Plot_1 = [row[0] for row in ViewJobReportBy_Classification_Plot]
            ChartJS_X_labels_Classification_Plot_2 = [row[1] for row in ViewJobReportBy_Classification_Plot]
            ChartJS_Y_values_Classification_Plot   = [row[2] for row in ViewJobReportBy_Classification_Plot]
            ChartJS_Y_color_Classification_Plot    = [row[3] for row in ViewJobReportBy_Classification_Plot]
            ChartJS_X_labels_Classification_Plot_1_2 = [row[4] for row in ViewJobReportBy_Classification_Plot]

            ViewJobReportBy_Recordable_Plot= ViewJobReportBy_Recordable_Plot.filter(['Project Name', 'Recordable', 'No of Recordable Incidents', 
            'Recordable_Color', 'Project_Recordable']).values
            ChartJS_X_labels_Recordable_Plot_1 = [row[0] for row in ViewJobReportBy_Recordable_Plot]
            ChartJS_X_labels_Recordable_Plot_2 = [row[1] for row in ViewJobReportBy_Recordable_Plot]
            ChartJS_Y_values_Recordable_Plot   = [row[2] for row in ViewJobReportBy_Recordable_Plot]
            ChartJS_Y_color_Recordable_Plot    = [row[3] for row in ViewJobReportBy_Recordable_Plot]
            ChartJS_X_labels_Recordable_Plot_1_2 = [row[4] for row in ViewJobReportBy_Recordable_Plot]

            ViewJobReportBy_Emergency_Plot= HSE_EmergencyLevelDF_Plot.filter(['Project Name', 'Emergency Level', 'No Of EmergencyLevel Incidents', 
            'Emergency_Color', 'Project_Emergency']).values
            ChartJS_X_labels_Emergency_Plot_1 = [row[0] for row in ViewJobReportBy_Emergency_Plot]
            ChartJS_X_labels_Emergency_Plot_2 = [row[1] for row in ViewJobReportBy_Emergency_Plot]
            ChartJS_Y_values_Emergency_Plot   = [row[2] for row in ViewJobReportBy_Emergency_Plot]
            ChartJS_Y_color_Emergency_Plot    = [row[3] for row in ViewJobReportBy_Emergency_Plot]
            ChartJS_X_labels_Emergency_Plot_1_2 = [row[4] for row in ViewJobReportBy_Emergency_Plot]
                       
         except:
            flash("Populated Segmented Project Summary by Year Failed")
         finally:
            return render_template('segmentProjectSummary_Class_A.html', ProjectSummaryYear=ProjectSummaryYear, ProjectSummaryPreparedBy=ProjectSummaryPreparedBy, 
            ProjectSummaryPreparedDate=ProjectSummaryPreparedDate, TotalEntries=TotalEntries, EventSegName=EventSegName, EventSegStartDate=EventSegStartDate,
            EventSegEndDate=EventSegEndDate,
            
            ViewJobReportBy_Classification_Pivot = [ViewJobReportBy_Classification_Pivot.to_html(index=True, classes='data',
            col_space= {'No of Classified Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_Classification_Plot_1=ChartJS_X_labels_Classification_Plot_1,
            ChartJS_X_labels_Classification_Plot_2=ChartJS_X_labels_Classification_Plot_2,
            ChartJS_Y_values_Classification_Plot=ChartJS_Y_values_Classification_Plot,
            ChartJS_Y_color_Classification_Plot   = ChartJS_Y_color_Classification_Plot,
            ChartJS_X_labels_Classification_Plot_1_2=ChartJS_X_labels_Classification_Plot_1_2,

            ViewJobReportBy_Recordable_Pivot = [ViewJobReportBy_Recordable_Pivot.to_html(index=True, classes='data',
            col_space= {'No of Recordable Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_Recordable_Plot_1=ChartJS_X_labels_Recordable_Plot_1,
            ChartJS_X_labels_Recordable_Plot_2=ChartJS_X_labels_Recordable_Plot_2,
            ChartJS_Y_values_Recordable_Plot=ChartJS_Y_values_Recordable_Plot,
            ChartJS_Y_color_Recordable_Plot   = ChartJS_Y_color_Recordable_Plot,
            ChartJS_X_labels_Recordable_Plot_1_2=ChartJS_X_labels_Recordable_Plot_1_2,

            HSE_EmergencyLevelDF_Pivot = [HSE_EmergencyLevelDF_Pivot.to_html(index=True, classes='data',
            col_space= {'No Of EmergencyLevel Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_Emergency_Plot_1=ChartJS_X_labels_Emergency_Plot_1,
            ChartJS_X_labels_Emergency_Plot_2=ChartJS_X_labels_Emergency_Plot_2,
            ChartJS_Y_values_Emergency_Plot=ChartJS_Y_values_Emergency_Plot,
            ChartJS_Y_color_Emergency_Plot   = ChartJS_Y_color_Emergency_Plot,
            ChartJS_X_labels_Emergency_Plot_1_2=ChartJS_X_labels_Emergency_Plot_1_2,
            )

      elif HSE_Project_Report_Class == '2':
         try:
            HSE_WCB_Report_Plot= HSE_WCB_Report_Plot.filter(['Project Name', 'WCBCase', 'No of WCB Incidents', 
            'WCB_Color', 'Project_WCB']).values
            ChartJS_X_labels_WCB_Plot_1 = [row[0] for row in HSE_WCB_Report_Plot]
            ChartJS_X_labels_WCB_Plot_2 = [row[1] for row in HSE_WCB_Report_Plot]
            ChartJS_Y_values_WCB_Plot   = [row[2] for row in HSE_WCB_Report_Plot]
            ChartJS_Y_color_WCB_Plot    = [row[3] for row in HSE_WCB_Report_Plot]
            ChartJS_X_labels_WCB_Plot_1_2 = [row[4] for row in HSE_WCB_Report_Plot]

            HSE_UnsafeAct_Report_Plot= HSE_UnsafeAct_Report_Plot.filter(['Project Name', 'UnsafeAct', 'No of UnsafeAct Incidents', 
            'UnsafeAct_Color', 'Project_UnsafeAct']).values
            ChartJS_X_labels_UnsafeAct_Plot_1 = [row[0] for row in HSE_UnsafeAct_Report_Plot]
            ChartJS_X_labels_UnsafeAct_Plot_2 = [row[1] for row in HSE_UnsafeAct_Report_Plot]
            ChartJS_Y_values_UnsafeAct_Plot   = [row[2] for row in HSE_UnsafeAct_Report_Plot]
            ChartJS_Y_color_UnsafeAct_Plot    = [row[3] for row in HSE_UnsafeAct_Report_Plot]
            ChartJS_X_labels_UnsafeAct_Plot_1_2 = [row[4] for row in HSE_UnsafeAct_Report_Plot]


            HSE_UnsafeCond_Report_Plot= HSE_UnsafeCond_Report_Plot.filter(['Project Name', 'UnsafeCond', 'No of UnsafeCond Incidents', 
            'UnsafeCond_Color', 'Project_UnsafeCond']).values
            ChartJS_X_labels_UnsafeCond_Plot_1 = [row[0] for row in HSE_UnsafeCond_Report_Plot]
            ChartJS_X_labels_UnsafeCond_Plot_2 = [row[1] for row in HSE_UnsafeCond_Report_Plot]
            ChartJS_Y_values_UnsafeCond_Plot   = [row[2] for row in HSE_UnsafeCond_Report_Plot]
            ChartJS_Y_color_UnsafeCond_Plot    = [row[3] for row in HSE_UnsafeCond_Report_Plot]
            ChartJS_X_labels_UnsafeCond_Plot_1_2 = [row[4] for row in HSE_UnsafeCond_Report_Plot]
           
         except:
            flash("Populated Segmented Project Summary by Year Failed")
         finally:
            return render_template('segmentProjectSummary_Class_B.html',   ProjectSummaryYear=ProjectSummaryYear, ProjectSummaryPreparedBy=ProjectSummaryPreparedBy, 
            ProjectSummaryPreparedDate=ProjectSummaryPreparedDate, TotalEntries=TotalEntries, EventSegName=EventSegName, EventSegStartDate=EventSegStartDate,
            EventSegEndDate=EventSegEndDate,

            HSE_WCB_Report_Pivot = [HSE_WCB_Report_Pivot.to_html(index=True, classes='data',
            col_space= {'No of WCB Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_WCB_Plot_1=ChartJS_X_labels_WCB_Plot_1,
            ChartJS_X_labels_WCB_Plot_2=ChartJS_X_labels_WCB_Plot_2,
            ChartJS_Y_values_WCB_Plot=ChartJS_Y_values_WCB_Plot,
            ChartJS_Y_color_WCB_Plot   = ChartJS_Y_color_WCB_Plot,
            ChartJS_X_labels_WCB_Plot_1_2=ChartJS_X_labels_WCB_Plot_1_2,

            HSE_UnsafeAct_Report_Pivot = [HSE_UnsafeAct_Report_Pivot.to_html(index=True, classes='data',
            col_space= {'No of UnsafeAct Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_UnsafeAct_Plot_1=ChartJS_X_labels_UnsafeAct_Plot_1,
            ChartJS_X_labels_UnsafeAct_Plot_2=ChartJS_X_labels_UnsafeAct_Plot_2,
            ChartJS_Y_values_UnsafeAct_Plot=ChartJS_Y_values_UnsafeAct_Plot,
            ChartJS_Y_color_UnsafeAct_Plot   = ChartJS_Y_color_UnsafeAct_Plot,
            ChartJS_X_labels_UnsafeAct_Plot_1_2=ChartJS_X_labels_UnsafeAct_Plot_1_2,

            HSE_UnsafeCond_Report_Pivot = [HSE_UnsafeCond_Report_Pivot.to_html(index=True, classes='data',
            col_space= {'No of UnsafeCond Incidents': 2, '':150}, justify="justify-all")],
            ChartJS_X_labels_UnsafeCond_Plot_1=ChartJS_X_labels_UnsafeCond_Plot_1,
            ChartJS_X_labels_UnsafeCond_Plot_2=ChartJS_X_labels_UnsafeCond_Plot_2,
            ChartJS_Y_values_UnsafeCond_Plot=ChartJS_Y_values_UnsafeCond_Plot,
            ChartJS_Y_color_UnsafeCond_Plot   = ChartJS_Y_color_UnsafeCond_Plot,
            ChartJS_X_labels_UnsafeCond_Plot_1_2=ChartJS_X_labels_UnsafeCond_Plot_1_2,
            )
      
      elif HSE_Project_Report_Class == '3':
         try:
            HSE_CrewReport_Plot= HSE_CrewReport.filter(['Project Name', 'Project Number', 'No of HSE Incidents', 'Join']).values
            ChartJS_X_labels_CrewReport_Plot_1 = [row[0] for row in HSE_CrewReport_Plot]
            ChartJS_X_labels_CrewReport_Plot_2 = [row[1] for row in HSE_CrewReport_Plot]
            ChartJS_Y_values_CrewReport_Plot   = [row[2] for row in HSE_CrewReport_Plot]
            ChartJS_X_labels_CrewReport_Plot_1_2 = [row[3] for row in HSE_CrewReport_Plot]         
         except:
            flash("Populated Segmented Project Summary by Year Failed")
         finally:
            return render_template('segmentProjectSummary_Class_C.html', ProjectSummaryYear=ProjectSummaryYear, ProjectSummaryPreparedBy=ProjectSummaryPreparedBy, 
            ProjectSummaryPreparedDate=ProjectSummaryPreparedDate, TotalEntries=TotalEntries, EventSegName=EventSegName, EventSegStartDate=EventSegStartDate,
            EventSegEndDate=EventSegEndDate,

            HSE_CrewReport_Table = [HSE_CrewReport_Table.to_html(index=False, classes='data',
            col_space= {'Event Index': 180, 'Project Name': 260, 'Project Number': 220,'Project Location': 220,
            'No of HSE Incidents':220, 'Event Percentage (%)':220}, justify="justify-all")],
            ChartJS_X_labels_CrewReport_Plot_1=ChartJS_X_labels_CrewReport_Plot_1, ChartJS_X_labels_CrewReport_Plot_2=ChartJS_X_labels_CrewReport_Plot_2,
            ChartJS_Y_values_CrewReport_Plot=ChartJS_Y_values_CrewReport_Plot, ChartJS_X_labels_CrewReport_Plot_1_2=ChartJS_X_labels_CrewReport_Plot_1_2,
            
            )
      else:
          return redirect(url_for('HSEDataAnalysis'))

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*" # <- You can change "*" for a domain for example "http://localhost"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
    return response

