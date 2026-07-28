import os
import pandas as pd
import time
import sys
import logging

class ReportUpdater:

    ''' Class to update Excel report of chat responses'''

    def __init__(self):

        self.output_dir = "./Reports"
        os.makedirs(self.output_dir, exist_ok=True)
        self.SCRIPT_FILE_NAME = __file__  
        self.Counter = 0


    def update_report_xlsx(self, RequestTime,ResponseTime, User_input, Response, Feedback,Timetaken, Chathistory, Context, PromptTemplate):

        ''' File to create and update excel report'''

        methodName = 'update_report_xlsx'
        try:
            
            output_file = os.path.join(self.output_dir, f"Report_{time.strftime('%d%m%y')}.xlsx")

           
            columns = ['RequestTime', 'ResponseTime', 'User_input', 'LLMResponse','Feedback','Timetaken', 'ChatHistory', 'Context', 'PromptTemplate']

            
            if os.path.exists(output_file):
                df = pd.read_excel(output_file)

            else:
                df = pd.DataFrame(columns=columns)

            new_row = {
                'RequestTime': RequestTime,
                'ResponseTime': ResponseTime,
                'User_input': User_input,
                'LLMResponse': Response,
                'Feedback': Feedback,
                'Timetaken': Timetaken,
                'ChatHistory': Chathistory,
                'Context' : Context,
                'PromptTemplate': PromptTemplate

            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            
            df.to_excel(output_file, index=False)

            print(f"Excel report updated.")
            logging.info(f'{self.SCRIPT_FILE_NAME}|Excel report updated.')

            
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"[{time.strftime('%d-%m-%y %H:%M:%S')}]| {self.SCRIPT_FILE_NAME}|{methodName}|Exception [{exc_type}], File [{fname}], Line [{exc_tb.tb_lineno}]")
            logging.error(f'{self.SCRIPT_FILE_NAME}|{methodName}|Exception [{exc_type}], File [{fname}], Line [{exc_tb.tb_lineno}]')
            logging.info(f'{self.SCRIPT_FILE_NAME}| {err}')
            return err

    def update_feedback(self, response_text, new_feedback):

        ''' Update feedback in report  '''

        methodName = 'update_feedback'

        print("Updating feedback in report...")

        try:
            output_file = os.path.join(self.output_dir, f"Report_{time.strftime('%d%m%y')}.xlsx")

            if not os.path.exists(output_file):
                raise FileNotFoundError("Report file not created.")

            df = pd.read_excel(output_file)

            # Find rows matching the LLM response 
            mask = df['LLMResponse'].astype(str).str.lower() == str(response_text).lower()
            matching_indices = df.index[mask].tolist()

            if not matching_indices:
                print(f"No rows found with response: {response_text}")
                return False

            # Update only the last matching row
            last_idx = matching_indices[-1]
            df.iloc[last_idx, df.columns.get_loc('Feedback')] = new_feedback

            df.to_excel(output_file, index=False)
            print(f"Feedback updated.")
            logging.info(f'{self.SCRIPT_FILE_NAME}|Feedback updated for last matched row.')
            return True


        except Exception as err:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"[{time.strftime('%d-%m-%y %H:%M:%S')}]| {self.SCRIPT_FILE_NAME}|{methodName}|Exception [{exc_type}], File [{fname}], Line [{exc_tb.tb_lineno}]")
            logging.error(f'{self.SCRIPT_FILE_NAME}|{methodName}|Exception [{exc_type}], File [{fname}], Line [{exc_tb.tb_lineno}]')
            logging.info(f'{self.SCRIPT_FILE_NAME}| {err}')
            return err