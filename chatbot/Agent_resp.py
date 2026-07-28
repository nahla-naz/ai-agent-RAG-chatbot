

import traceback
import logging
from chatbot.logging_config import setup_logging

setup_logging("logs","log")




try:

    


    
    print("\nLoading AI agent.... Please wait \n")
    logging.info("Loading AI agent...")

    #logging.info("Importing libraries...")

    ## Import all libraries
    import customtkinter as ctk
    from threading import Thread
    from langchain_ollama.llms import OllamaLLM
    from langchain_core.prompts import ChatPromptTemplate
    #from ollamavector_docx3 import retriever
    from chatbot.Vector_db_New import Embedding_vectors
    import time
    #from langchain.evaluation import load_evaluator,  EvaluatorType
    from sentence_transformers import SentenceTransformer, util
    #from sklearn.metrics.pairwise import cosine_similarity

    from langchain_core.chat_history import InMemoryChatMessageHistory
    from langchain_core.runnables.history import RunnableWithMessageHistory

    from chatbot.Reports import ReportUpdater

    
    #logging.info("Loading embedding model for evaluation...")
    ## Load model for Evaluation
    sim_model = SentenceTransformer('all-MiniLM-L6-v2')




    ''' Convert text to Embedding vectors and store in Vector DB'''

    Embed_vectors = Embedding_vectors()


    # NEW METHOD - extracting from multiple pdfs 
    # Note: Change Data description accordingly in prompt


    ## NEW - COMMENT OUT IF VECTOR STORE IS READY ##
    Embed_vectors.extract_pdf_docs_New()
    Embed_vectors.load_emb_model()
    Embed_vectors.split_to_chunks()
    Embed_vectors.Get_emb_vectors()

    ## USE EXISTING VECTOR STORE
    # Embed_vectors.load_emb_model()
    # Embed_vectors.Get_existing_emb_vectors()



    #logging.info("Loading LLM model...")
    #print("Loading LLM model...")

    model = OllamaLLM(
                        model="llama3.2",

                        temperature=0,     ## Less creative
                        top_k=0,           ## More conservative
                        num_predict=200,     ## No. of predicted tokens
                        tfs_z=1,            ## Impact of less probable tokens - disabled
                        seed = 2000,         ## Same response for same query

                        validate_model_on_init=True  ## check if model exists
                    )

    # print(f"\nModel:{model}")
    # logging.info(f"\nModel:{model}")

    # print(f"\nModel features:{dir(model)}") 
    # logging.info(f"\nModel features:{dir(model)}")

    # print(f"\nModel parameters:{model._generate_params}")
    # logging.info(f"\nModel parameters:{model._generate_params}")



    ## PROMPT TEMPLATE
    
    data_descr = ""  

    template = """You are a Customer support assistant having conversation with a user.
    Rules:
    1. ALWAYS connect question to the below provided chat history to get meaning. 
    2. If the provided data does not have the answer to user's question, ALWAYS ask the user to rephrase question or contact Customer support team for further assistance.
    3. DO NOT look for answers in chat history.
    4. Never ask to refer anything. 
    5. Reply in a friendly tone. 
    6. Admit it when specific information is not found.
    7. IMPORTANT: If answer is found in the "Frequently Asked Questions" or "Additional Information" sections, ONLY reply with that answer.
    8. Reply very briefly.
    9. NEVER ask questions in your reply. 
    10. DO NOT provide user's message in your reply.
    11. ALWAYS use the data provided when the user asks a question about it.
   
    12. Description of provided data: {data_descr}

    13. Here is the data: {data}

    14. User's current message: {question}

    15. Chat history: {history}
    """



    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    # print(f"\nPrompt template:{prompt}")
    # logging.info(f"\nPrompt template:{prompt}")

    # #print(f"\nPrompt template features:{dir(prompt)}")
    # #logging.info(f"\nPrompt template features:{dir(prompt)}")

    # print(f"\nPrompt length:{prompt.__len__}")
    # logging.info(f"\nPrompt length:{prompt.__len__}")

    # print(f"\nChain: {chain}")
    # logi.info(f"\nChain: {chain}")

    # #print(f"\nChain features: {dir(chain)}")
    # #logi.info(f"\nChain features: {dir(chain)}")


    ##  Adding chat history to memory
    store = {}

    def get_session_history(session_id: str) -> InMemoryChatMessageHistory:

        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()  ## initialise new chat history

        return store[session_id]

    chain = (prompt | model)
    chain = RunnableWithMessageHistory(
        chain,
        get_session_history,     ## chat history for the session
        input_messages_key="question",   
        history_messages_key="history", 
    )


    class Chatbot_fns:

        ''' Class to initialise Tkinter UI - used for Testing backend'''
        
        def __init__(self):
            
            ## common messages
            self.intents = { 
                        "greeting": {
                            "patterns": ["hello", "hi", "hey", "good morning", "good evening"],
                            "response": "Hello! It's nice to chat with you. How can I assist you today?"
                        },
                        "goodbye": {
                            "patterns": ["bye", "goodbye", "see you later", "farewell"],
                            "response": "Goodbye! Have a wonderful day!"
                        },
                        "fallback": {
                            "patterns": ["no", "that is not what i meant"],
                            "response": "I'm sorry, I didn’t understand that. Could you please rephrase your question?"
                        },
                        "thanks": {
                              "patterns": ["thank you", "thanks a lot"],
                            "response": "You're welcome! Happy to assist you. "
                        },
                        # "how are you":{
                        #     "patterns": ["How are you", "How do you do", "how are you doing", "How's everything with you"],
                        #     "response": "Hello! I'm doing well, thank you for asking. Is there something specific I can help you with today?"
                        # },
                        "okay": {
                              "patterns": ["okay", "okay great", "cool"],
                            "response": "If you have any other questions or need help with something else, feel free to ask!"

                        }
                        
                    }
            
            self.pattern_embeddings = []

            self.best_intent = "fallback"
            self.max_similarity = 0.0

            ## convert common input patterns to embeddings
            for intent, data in self.intents.items():
                for pattern in data.get("patterns", []):
                    emb = sim_model.encode(pattern, convert_to_tensor=True)
                    self.pattern_embeddings.append((intent, pattern, emb))


            self.report_updater = ReportUpdater()

            # self.root = root
            # self.root.title("AI Agent")
            # self.root.geometry("700x600+500+100")
            # ctk.set_appearance_mode("system")
            # ctk.set_default_color_theme("blue")

            # # Chat Frame
            # self.chat_display = ctk.CTkTextbox(
            #     master=root,
            #     wrap="word",
            #     font=ctk.CTkFont("Arial", 13),
            #     corner_radius=10,
            #     width=600,
            #     height=400
            # )
            # self.chat_display.pack(padx=20, pady=(20, 10), fill="both", expand=True)
            # self.chat_display.configure(state="disabled")

            # # Input Frame
            # input_frame = ctk.CTkFrame(master=root)
            # input_frame.pack(fill="x", padx=20, pady=(0, 10))

            # self.user_input = ctk.CTkEntry(input_frame, font=("Arial", 13), placeholder_text="Type your message...")
            # self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)
            # self.user_input.bind("<Return>", self.send_message)

            # self.send_button = ctk.CTkButton(input_frame, text="Send", command=self.send_message, width=80)
            # self.send_button.pack(side="right", pady=10)

            # # Status Label
            # self.status_label = ctk.CTkLabel(master=root, text="Model Ready", text_color="green", anchor="w")
            # self.status_label.pack(fill="x", padx=20, pady=(0, 10))

            # self.display_message(f"Bot: Hi, I can help you navigate the Web portal. Feel free to ask me anything! \n", "bot")

            # self.processing = False

            # ## Model status message
            # self.status_steps = [
            #     "Thinking...",
            #    # "Hold on, crafting your reply..."
            #    #  "Please wait...",
            #     # "Please wait...(2)",
            #    # "Please wait for AI agent to respond...(1)",
            #    # "Please wait for AI agent to respond...(2)",
            #     "Finding relevant data ...",
            #   #  "Finding relevant data ...(1)",
            #    # "Finding relevant data ...(2)",
            #    # "Finding relevant data ... (3)",
            #    # "Finding relevant data ... (4)",
            #    # "Finding relevant data ... (5)",
            #    # "Data found...",
            #    # "Generating response...",
            #     "Generating response... (1)",
            #     "Generating response... (2)",
            #     "Generating response... (3)",
            #     "Generating response... (4)",
            #     "Generating response... (5)",
            #     "Generating response... (6)",
            #     "Generating response... (7)",
            #     "Generating response... (8)",
            #     "Generating response... (9)",
            #     "Generating response... (10)",


            # ]
            # self.status_index = 0

            ###########################################################
            
            # # Evaluation tool - TESTING
            # Reference Q&A  - for evaluation 
            # self.reference_answers = {
            #    
            # }
        

        def show_dynamic_status(self):
                
                ''' Function to update Model status in UI '''
                
                def step_through_status(index=0):
                    if not self.processing or index >= len(self.status_steps):
                        return
                    message = self.status_steps[index]
                    self.update_status(message, "#68228B")
                    self.root.after(7000, lambda: step_through_status(index + 1)) 

                step_through_status()


        def send_message(self, event=None):

            ''' Get question from user and send it to model for response '''

            question = self.user_input.get().strip()
            if not question:
                return
            if question.lower() == 'q':
                self.root.quit()
                return
            

            self.display_message(f"\nYou: {question}\n", "user")
            self.user_input.delete(0, 'end')

            self.processing = True
            self.status_index = 0
            self.show_dynamic_status()  

            Thread(target=self.get_response, args=(question,), daemon=True).start()

        
        def initial_response(self,user_input: str):

            ''' Function to respond for common messages '''

            ## convert input to embeddings
            user_embedding = sim_model.encode(user_input, convert_to_tensor=True)

           ## Loop over common input pattern embeddings
            for intent, pattern, emb in self.pattern_embeddings:
                
                ## get similarity
                similarity = util.cos_sim(user_embedding, emb).item()

                if similarity > self.max_similarity:
                    self.max_similarity = similarity
                    self.best_intent = intent

            if self.max_similarity < 0.5:
                
                return None, True

            return self.intents[self.best_intent]["response"], False


                


        def get_response(self, question: str):
                
                ''' Function to invoke model and generate response 
                
                 '''
                try:
                    starttime = time.time()
                    starttime_ = time.strftime('%d/%m/%y %H:%M:%S')
                    print(f"{time.strftime('%H:%M:%S')} - User input received...")

                    LLM_OK = True

                    response, LLM_OK = self.initial_response(question)

                    if (LLM_OK):

                            print(f"{time.strftime('%H:%M:%S')} - Retrieving closest matches ...")
                            logging.info(f"User input received...")
                            logging.info(f"Retrieving closest matches ...")

                            docs = Embed_vectors.retriever.invoke(question, k=10)

                            ## View retrieved doc results
                            # print(f"\nRETRIEVED DOCS:::")
                            # logging.info("\nRETRIEVED DOCS:::")

                            # #print(f"\nRetreived docs Features: {dir(docs)}")
                            # #logging.info(f"\nRetreived docs Features: {dir(docs)}")

                            # for i, doc in enumerate(docs, 1):
                            #     print(f"\n--- DOC {i} ---\n{doc.page_content}")
                            #     logging.info(f"\n--- DOC {i} ---\n{doc.page_content}")

                            if not docs:
                                self.display_message("Bot: Sorry, I couldn't find any relevant data.\n", "bot")
                                return

                            context = "\n\n".join(
                                f"[Section: {doc.metadata.get('section', 'Unknown')}]\n{doc.page_content}"
                                for doc in docs
                            )

                            print("\nCONTEXT:", context)

                            logging.info(f"\nContext: {context}")

                        
                            ## Chat history

                            session_id = "chat-session-1"

                            ## get chat history for the session
                            history = get_session_history(session_id)

                            print(f"\nChat history:")
                            #logging.info(f"\nChat history:")

                            chathistory = []
                            for msg in history.messages:
                                print(f"{msg.content}")
                                chathistory.append(msg.content)
                                #logging.info(f" {msg.content}")

                            # print(f"\n{time.strftime('%H:%M:%S')} - Data retrieved.")
                            # print(f"\n{time.strftime('%H:%M:%S')} - Sending prompt to LLM model...")
                            logging.info("\nData retrieved.")
                            logging.info("\nSending prompt to LLM model...")

                            print(f"{time.strftime('%H:%M:%S')} - Data retrieved.")
                            print(f"{time.strftime('%H:%M:%S')} - Sending prompt to LLM model...")


                            response = chain.invoke(
                                    {
                                        "data_descr": data_descr,
                                        "data": context,
                                        "question": question,
                                    },
                                    config={"configurable": {"session_id": "chat-session-1"}},
                                )

                            ## Invoke model for response - org code
                            # response = chain.invoke({
                            #     "data_descr": data_descr,
                            #     "data": context,
                            #     "question": question
                            # })

                            print(f"{time.strftime('%H:%M:%S')} - Response received.")
                            logging.info(f"Response received.")


                            endtime = time.time()
                            timetaken = endtime - starttime

                            print(f"{time.strftime('%H:%M:%S')} - Time taken: {timetaken:.2f} seconds")
                            logging.info(f"Time taken: {timetaken:.2f} seconds")

                            ## Update excel report ##
                            self.report_updater.update_report_xlsx(starttime_,time.strftime('%d/%m/%y %H:%M:%S'),question,response,'',timetaken, chathistory, context, template)
                        

                            ## Display response in UI
                            #self.display_message(f"Bot: {response}\n", "bot")

                    return response

                            # print(f"\nLLM Response: {response}")
                            #logging.info(f"\nLLM Response: {response}")

                            #print(f"\nLLM Response features: {dir(response)}")
                            #logi.info(f"\nLLM Response features: {dir(response)}")

                            

                            ## EVALUATION TOOL - TESTING
                            # ## Check if question is within Reference Q&A (For evaluation) ##

                            # print(f"\nQuestion: {question}")
                            
                            # # Generate embeddings
                            # embq = sim_model.encode(question, convert_to_tensor=True)

                            # for qref in self.reference_answers:

                            #     emb_ref = sim_model.encode(response, convert_to_tensor=True)

                            #     # Reshape to 2D arrays for sklearn
                            #     embq = embq.reshape(1, -1)
                            #     emb_ref = emb_ref.reshape(1, -1)

                            #     # Cosine similarity
                            #     cos_simq = cosine_similarity(embq, emb_ref)[0][0]

                            #     if(cos_simq>0.5):

                            #         main_q = qref


                            
                                    
                            # if main_q in self.reference_answers:

                            #     ## Check if answer is within Reference Q&A (For evaluation) ##
                            
                            #     reference = self.reference_answers[main_q]
                            
                            #     # Generate embeddings
                            #     emb1 = sim_model.encode(reference, convert_to_tensor=True)
                            #     emb2 = sim_model.encode(response, convert_to_tensor=True)

                            #     # Reshape to 2D aray
                            #     emb1 = emb1.reshape(1, -1)
                            #     emb2 = emb2.reshape(1, -1)

                            #     # Cosine similarity
                            #     cos_sim = cosine_similarity(emb1, emb2)[0][0]

                            #     if(cos_sim>0.2):
                            #         result = "Correct answer"

                            #     else:
                            #         result = "Wrong answer"

                            #     status_text = f"{result} | Similarity score : {cos_sim:.2f}"
                                    

                                
                            # else:
                            #     # No reference question found
                            #     #avg_time = self.total_response_time / max(1, self.eval_count)

                            #     status_text = f"Question not found for evaluation..."
                            
                            # print(status_text)

                except Exception as e:
                    #self.display_message(f"Error: {str(e)}\n", "error")

                    print("Error occured:",e)
                    traceback.print_exc()

                    logging.error(f"Error occured:{e}. Traceback:{traceback.print_exc()}")

                #finally:
                    #self.processing = False
                    
                    #self.update_status("Model Ready", "green")



        def display_message(self, message, tag):

            ''' Function to format UI'''

            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", message)

            tag_color = {
                "user": "black",
                "bot": "black",
                "error": "red"
            }.get(tag, "white")

            self.chat_display.tag_add(tag, f'end-{len(message)}c', "end")
            self.chat_display.tag_config(tag, foreground=tag_color)
            self.chat_display.configure(state="disabled")
            self.chat_display.yview("end")


        def update_status(self, text, color):
            self.status_label.configure(text=text, text_color=color)


    #if __name__ == "__main__":

        #logging.info("Starting Tkinter application...")

        #root = ctk.CTk()
        #app = ChatbotGUI(root)
        #root.mainloop()


except Exception as e:

    print("Error occured:",e)
    traceback.print_exc()
    
    logging.error(f"Error occured:{e}. Traceback:{traceback.print_exc()}")
