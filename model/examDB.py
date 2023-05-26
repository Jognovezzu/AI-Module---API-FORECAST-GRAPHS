import copy
import json
import sqlite3
from typing import Dict, List, Tuple, Union
from xmlrpc.client import Boolean
import pandas


DATABASE_PATH = './model/db/exams.db'
#'./ai-api/model/db/exams.db'
DATABASE_SCRIPTS_PATH = './model/db/scripts'
#'./ai-api/model/db/scripts'

class ExamDB:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.sqlScripts = self._loadSqlScripts()
        self.conn.executescript(self.sqlScripts['drop_table'])
        self.conn.executescript(self.sqlScripts['create_tables'])
        self.conn.executescript(self.sqlScripts['create_relearned_tables'])
        self.conn.executescript(self.sqlScripts['create_recommendation_tables'])
        self.conn.executescript(self.sqlScripts['trigger_recommendation'])
    
    def _loadSqlScripts(self) -> Dict[str, str]:
        return {
        'drop_table': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/drop_table.sql'),
        'create_tables': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/exams_create_tables.sql'),
        'insert_exam_data': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/exams_insert_exam_data.sql'),
        'clean_exam': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/exams_clean_exam.sql'),
        'select_sensors_data': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/exams_select_sensors_data_by_exam.sql'),
        'create_relearned_tables': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/relearned_create_tables.sql'),
        'relearned_insert_data': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/relearned_insert_data.sql'),
        'create_recommendation_tables': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/recommendation_create_tables.sql'),
        'recommendation_insert_data': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/recommendation_insert_data.sql'),
        'recommendation_consult': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/recommendation_consult.sql'),
        'trigger_recommendation': self._loadScript(f'{DATABASE_SCRIPTS_PATH}/trigger_recommendation.sql')
            }

    def _loadScript(self, filename: str) -> str:
        script = ''
        with open(filename, 'r') as sqlFile:
            script = ''.join(sqlFile.readlines())

        return script

    def insertExamRegistries(self, registries: List[Union[str, float]]) -> None:
        try:
            self.conn = sqlite3.connect(DATABASE_PATH)

            self.conn.executemany(self.sqlScripts['insert_exam_data'], registries)
            self.conn.commit()
        except:
            print("ERROR INSERTEXAMREGISTRIES")
            self.conn.rollback()
        
        self.conn.close()

    def deleteRegistriesByExamId(self, examId: str) -> List[Tuple[Union[str, float]]]:
        try:
            self.conn = sqlite3.connect(DATABASE_PATH)
            cursor = self.conn.cursor()

            cursor.execute(self.sqlScripts['select_sensors_data'], (examId,))
            examData = copy.deepcopy(cursor.fetchall())
            self.conn.execute(self.sqlScripts['clean_exam'], (examId,))
            self.conn.commit()
        except:
            print("ERROR DELETEREGISTRIESBYEXAMID")
            self.conn.rollback()
        self.conn.close()

        return examData


    def insertRelearnedData(self, data: pandas.DataFrame) -> None:
        try:
            self.conn = sqlite3.connect(DATABASE_PATH)
            data.to_sql('relearnedData', self.conn, if_exists='append', index=False)
            self.conn.commit()
            print("ADICIONADO AO BD.....")

        except:
            print("ERRO AO ADICIONAR DATAFRAME AO BD....")
            self.conn.rollback()
            

        self.conn.close()

    def insert_final_rec(self, examId: str, doctor_recommendation: str) -> None:
        try:
            self.conn = sqlite3.connect(DATABASE_PATH)
            self.conn.execute(self.sqlScripts['update_recommendation_data'],[examId,doctor_recommendation])
            self.conn.commit()
        
        except:
            print("ERROR TO UPDATE FINAL RECOMMENDATION")
            self.conn.rollback()

        self.conn.close()


    def insertRecommendationData (self,examId: str, data: List[Union[str, float]]) -> None:
        try:
            graphs_json = data["graphs"]
            graphs_js = json.dumps(graphs_json)
            self.conn = sqlite3.connect(DATABASE_PATH)

            self.conn.execute(self.sqlScripts['recommendation_insert_data'],[examId,data["gaitType"],graphs_js])
            self.conn.commit()
        except:
            print("ERROR INSERT_RECOMMENDATION_DATA")
            self.conn.rollback()
        
        self.conn.close()

    def consultRecommendationData (self,examId: str) -> Dict:
        try:
            self.conn = sqlite3.connect(DATABASE_PATH)
            result = self.conn.execute(self.sqlScripts['recommendation_consult'],examId)
            if len(result)>0:
                examResult = {}
                examResult['gaitType'] = result[0][0]
                examResult['graphs'] = json.loads(result[0][1])

                return examResult
            else:
                return None
        except:
            print("ERROR CONSULT EXAM")
            self.conn.rollback()

        self.conn.close()

        

    def relearnedModel(self):
        print("Starting Relearned AI script")
        try:
            self.conn = sqlite3.connect(DATABASE_PATH)

        except:
            print("ERROR TO START RELEARNED AI SCRIPT")

        
        df = pd.read_sql_query("SELECT * FROM relearnedData", self.conn)
        df.drop(columns=["examId", "RECOMMENDATION_IA"],inplace=True)

        X = df.iloc[:, 0:9].values
        Y = df.iloc[:, 9].values

        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=0)

        sc = StandardScaler()
        X_train = sc.fit_transform(X_train)
        X_test = sc.transform(X_test)


        regressor = RandomForestClassifier(n_estimators=100, random_state=0)
        regressor.fit(X_train, y_train)
        y_pred = regressor.predict(X_test)

        lst = os.listdir('.')
        number_files = len(lst)
        name_model = 'model'+str(number_files)
        AI_MODELS_PATH = '../ai/AiModels_metrics'

        #CRIAR A FUNÇÃO PARA ESTRUTURAR O JSON
        #print(accuracy_score(y_test, y_pred))
        #print(f1_score(y_test,y_pred))

        aiModel = AiModel_(accuracy_score= accuracy_score(y_test, y_pred),f1_score=f1_score(y_test,y_pred))

        with open(f'{AI_MODELS_PATH}/{name_model}.json', 'w') as file: 
            json.dump(aiModel.toDict(), file)
        







