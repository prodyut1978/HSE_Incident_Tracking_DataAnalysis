import sqlite3
DATABASE_NAME = ("./Server_HSE_MasterDB/Server_HSE_MasterDB_All_Modules/Server_HSE_MasterDB_Database/Server_HSE_MasterDB_Database.db")

def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def HSE_MasterDB_BackEnd_CreateTable():
    con = sqlite3.connect(DATABASE_NAME)
    cur=con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS HSEIncidentLog_MASTER (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                                                EventDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\
                                                                ProjName TEXT NOT NULL, \
                                                                ProjNum TEXT NOT NULL, \
                                                                ProjLoc TEXT NOT NULL, \
                                                                EmergencyLevel TEXT NOT NULL,\
                                                                HSEAdvisorInvestigator text NOT NULL,\
                                                                HSEIncidentDetails text NOT NULL,\
                                                                Client TEXT NOT NULL,\
                                                                CauseAnalysis TEXT NOT NULL,\
                                                                UnsafeAct TEXT NOT NULL,\
                                                                UnsafeCond TEXT NOT NULL,\
                                                                EmployeeInvolved TEXT NOT NULL,\
                                                                Classification TEXT NOT NULL,\
                                                                RecordableFAMARWCLTI TEXT NOT NULL,\
                                                                WCBCase TEXT NOT NULL,\
                                                                ModifiedDays TEXT NOT NULL,\
                                                                BodyPart TEXT NOT NULL,\
                                                                EquipmentNumber TEXT NOT NULL,\
                                                                CACompleted TEXT NOT NULL,\
                                                                SignOff TEXT NOT NULL)")

      
    cur.execute("CREATE TABLE IF NOT EXISTS HSEIncidentLog_TEMP (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                                                EventDate TEXT NOT NULL,\
                                                                ProjName TEXT NOT NULL, \
                                                                ProjNum TEXT NOT NULL, \
                                                                ProjLoc TEXT NOT NULL, \
                                                                EmergencyLevel TEXT NOT NULL,\
                                                                HSEAdvisorInvestigator text NOT NULL,\
                                                                HSEIncidentDetails text NOT NULL,\
                                                                Client TEXT NOT NULL,\
                                                                CauseAnalysis TEXT NOT NULL,\
                                                                UnsafeAct TEXT NOT NULL,\
                                                                UnsafeCond TEXT NOT NULL,\
                                                                EmployeeInvolved TEXT NOT NULL,\
                                                                Classification TEXT NOT NULL,\
                                                                RecordableFAMARWCLTI TEXT NOT NULL,\
                                                                WCBCase TEXT NOT NULL,\
                                                                ModifiedDays TEXT NOT NULL,\
                                                                BodyPart TEXT NOT NULL,\
                                                                EquipmentNumber TEXT NOT NULL,\
                                                                CACompleted TEXT NOT NULL,\
                                                                SignOff TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS HSEIncidentLog_PROJECTMAP (Proj_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                                                                ProjectName TEXT NOT NULL,\
                                                                ProjectNumber TEXT NOT NULL, \
                                                                ProjectLocation TEXT NOT NULL, \
                                                                EventYear INTEGER NOT NULL,\
                                                                Incidents_Count TEXT NOT NULL,\
                                                                Latitude REAL NOT NULL,\
                                                                Longitude REAL NOT NULL)")
    
    con.commit()
    con.close()




