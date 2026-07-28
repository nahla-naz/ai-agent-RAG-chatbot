
import re
import time
import traceback
import logging


try:

    import shutil
    from tqdm import tqdm
    from langchain_ollama import OllamaEmbeddings
    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from PyPDF2 import PdfReader
    import os
    #import logging


    ## Document loaders from Langchain community ##
    #import langchain_community.document_loaders
    ## For table extraction
    #from langchain_community.document_loaders import PDFPlumberLoader
    ## For complex layouts
    #from langchain_community.document_loaders import UnstructuredPDFLoader

    import pdfplumber



    class Embedding_vectors():

        def __init__(self):
            
            self.wd = os.getcwd()
            self.docs_path = f"{self.wd}\\DOCUMENTS"

            self.pdf_path = ""

            # Vector DB path
            self.db_location = "./chroma/langchain_DB"

            self.EMBEDDING_MODEL = None
            self.SECTIONS = []
            self.add_documents = True
            self.documents = []
            self.ids = []

            self.retriever = None
            self.parts = []

            self.Combined_Text = []
            self.combined_text_str = None
            self.current_text = []

            self.current_heading = "Introduction"  # default heading

            self.docs_pdf_plumber = []

            self.docs_transcript = [
                                    ]



        def extract_pdf_docs_New(self):

                ''' Function to extract all documents - NEW '''

                print("Extracting data from documents...")

                file_count = 0 

                for file in os.listdir(self.docs_path):

                    file_count+=1

                    self.current_text = []
                    self.current_heading = "Introduction"
                    self.Combined_Text = []

                    new_path = os.path.join(self.docs_path, file)
                    print(f"\n {time.strftime('%H:%M:%S')} - Reading : {new_path}\n")
                    
                    if not file.lower().endswith(".pdf"):
                        continue

                    if(file in self.docs_transcript):
                         self.current_heading = "Additional Information"
                    
                    else:
                         self.current_heading = "Introduction"
                    
                    if (file in self.docs_pdf_plumber):
                        self.Get_sections_pdfplumber(file)
                    
                    else:
                         

                        try:
                            READER = PdfReader(str(new_path))
                        except Exception as e:
                            print(f" Failed to read {new_path}: {e}")
                            continue
                        
                        # print(f"\nPDF extraction:{READER}")
                        # logging.info(f"\nPDF extraction:{READER}")
                        #print(f"\nPDF extraction features:{dir(READER)}")
                        #logging.info(f"\nPDF extraction features:{dir(READER)}")

                        logging.info("Splitting text to sections...")

                        for i, page in enumerate(READER.pages):
                            print(f"Page {i}")
                            self.parts = []                 
                            page.extract_text(visitor_text=self.Remove_h_f)
                            text = "".join(self.parts)
                            if not text:
                                continue
                            self.Combined_Text.append(text)

                        self.combined_text_str = " ".join(self.Combined_Text)

                        #logging.info(f"\n Combined text : {self.combined_text_str} \n")
                        #print(f"\n Combined text : {self.combined_text_str} \n")


                        # 2 - Extract text from page - org code
                        # text = page.extract_text()
                        # logging.info(f"\n Page text {i}: {text} \n")
                                
                        
                        print("Splitting data to sections...")
                        lines = self.combined_text_str.splitlines()

                        i = 0

                        for line in lines:
                            line = line.strip()

                            ## TEST
                            # i+=1
                            # if( i == 1):
                            #     print("First line: ", line)


                            if not line:
                                continue
                            
                            if self.is_heading(line):

                                ## TEST
                                # if(i==1):
                                #      print("Heading found!")

                                # Add previous section to list
                                if self.current_text:
                                    self.SECTIONS.append((self.current_heading, "\n".join(self.current_text)))
                                    self.current_text = []
                                    logging.info(f"\n Heading:{self.current_heading}")
                                    print(f"\n {time.strftime('%H:%M:%S')} - Heading: {self.current_heading}")

                                self.current_heading = line

                            else:
                                self.current_text.append(line)

                        # Add last section to list
                        if self.current_text:
                            print(f"\n {time.strftime('%H:%M:%S')} - Heading: {self.current_heading}")
                            logging.info(f"\n Heading:{self.current_heading}")
                            self.SECTIONS.append((self.current_heading, "\n".join(self.current_text)))



                                


        def extract_pdf_docs_1(self):
                
                ''' Function 1 to extract from multiple PDFs'''

                print("Extracting data from documents...")

                for file in os.listdir(self.docs_path):

                    if not file.lower().endswith(".pdf"):
                         
                        continue
                    
                    new_path = self.docs_path + "\\" + file
                    print(f"\n{new_path}\n")

                    try:
                        READER = PdfReader(str(new_path))

                    except Exception as e:
                        print(f" Failed to read {new_path}: {e}")
                        continue

                    # print(f"\nPDF extraction:{READER}")
                    # logging.info(f"\nPDF extraction:{READER}")

                    #print(f"\nPDF extraction features:{dir(READER)}")
                    #logging.info(f"\nPDF extraction features:{dir(READER)}")



                    logging.info("Splitting text to sections...")

                    
                    i= 0

                    for i, page in enumerate(READER.pages):

                        print(f"Page {i}")

                        ## 1 - Remove header footer - working ##
                        self.parts = [] 
                        page.extract_text(visitor_text=self.Remove_h_f)
                        text = "".join(self.parts)
                        #logging.info(f"\n Page text {i}: {text} \n")

                        if not text:
                            continue 

                        self.Combined_Text.append(text)

                    self.combined_text_str = " ".join(self.Combined_Text)

                    #logging.info(f"\n Combined text : {self.combined_text_str} \n")
                    print(f"\n Combined text : {self.combined_text_str} \n")


                        # 2 - Extract text from page - org code
                        # text = page.extract_text()
                        # logging.info(f"\n Page text {i}: {text} \n")



                    


        def extract_pdf_docs_2(self):
             
                ''' Function 2 to extract from multiple PDFs'''

                print("Splitting data to sections...")


                ## Extract lines from text
                lines = self.combined_text_str.splitlines()

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                
                    if self.is_heading(line):

                        # Add previous section to list
                        if self.current_text:
                            self.SECTIONS.append((self.current_heading, "\n".join(self.current_text)))
                            self.current_text = []

                            logging.info(f"\n Heading:{self.current_heading}")
                            print(f"\n Heading: {self.current_heading}")

                        self.current_heading = line
                    else:
                        self.current_text.append(line)

                # Add last section to list
                if self.current_text:
                    self.SECTIONS.append((self.current_heading, "\n".join(self.current_text)))


     

       
        def is_heading(self,line):
            
            
                    ''' Function to extract headings from text to group as 'section' metadata '''

                    line_stripped = line.strip()
                    if not line_stripped:
                        return False
                    if line_stripped.isupper():   ## Text in upper case
                        return True
                    #if line_stripped.endswith(':'):
                    #    return True

                    ##if len(line_stripped) < 40 and line_stripped.istitle():    ## Text of len<40 and Text with
                    if  line_stripped.istitle():      ##  alternative Upper and lower case
                        return True
                    
                    return False
        
    
        
            ## TEST - Alternate Heading extraction method
            # def is_heading(self, line):
                    
            #         line = line.strip()
            #         if not line:
            #             return False

            #         if line.isupper():  ## Uppercase lines
            #             return True

            #         if re.match(r'^\d+(\.\d+)*(\s+.+)?$', line) and len(line) > 3:  ## line starting with sequence of digits
            #             return True

            #         if len(line) < 60 and line.istitle()  : ## Title case or short lines 
            #                                                                 ## No page numbers
            #             return True

            #         return False
        
        

        def Remove_h_f(self,text, cm, tm, fontDict, fontSize):

            ''' Function to ignore header and footer'''

            
            y = tm[5]

            if y > 50 and y < 720:
                self.parts.append(text)

            return self.parts




        def Get_sections_pypdf2(self):

            ## NOT USED 

            ## For single document only


            ''' Function to split Text to Sections using pypdf2 '''

            
            # Load PDF
            READER = PdfReader(self.pdf_path)

            # print(f"\nPDF extraction:{READER}")
            # logging.info(f"\nPDF extraction:{READER}")

            #print(f"\nPDF extraction features:{dir(READER)}")
            #logging.info(f"\nPDF extraction features:{dir(READER)}")


            current_heading = "Introduction"  # default heading
            


            logging.info("Splitting text to sections...")

            
            i= 0

            for i, page in enumerate(READER.pages):

                ## 1 - Remove header footer - working ##
                self.parts = [] 
                page.extract_text(visitor_text=self.Remove_h_f)
                text = "".join(self.parts)
                #logging.info(f"\n Page text {i}: {text} \n")


                # 2 - Extract text from page - org code
                # text = page.extract_text()
                # logging.info(f"\n Page text {i}: {text} \n")



                if not text:
                    continue
                
                ## Extract lines from text
                lines = text.splitlines()

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    if self.is_heading(line):

                        # Add previous section to list
                        if self.current_text:
                            self.SECTIONS.append((current_heading, "\n".join(self.current_text)))
                            self.current_text = []

                            #logging.info(f"\n Heading:{current_heading}")

                        current_heading = line
                    else:
                        self.current_text.append(line)

            # Add last section to list
            if self.current_text:
                self.SECTIONS.append((current_heading, "\n".join(self.current_text)))

            #print(f"\n Sections:{SECTIONS}")
            #logging.info(f"\n Sections:{self.SECTIONS}")
                
        
        def  Get_sections_pdfplumber(self,filename):

            ## Warning: small headings not identified

            ''' Function to split Text to Sections using pdfplumber '''

            current_heading = "Introduction"  # default heading
            #self.current_text = []

            ## CHANGE HEADING FONT SIZE THRESHOLD HERE
            if(filename == "Webscraped_output.pdf"):
                    
                    threshold = 13

            elif(filename==""):
                 
                    threshold = 25



             
            with pdfplumber.open(f".\\DOCUMENTS\\{filename}") as pdf:
                

                for i, page in enumerate(pdf.pages):
                        
                    #words = page.extract_words(extra_attrs=["fontname", "size"])
                
                        lines = page.extract_text_lines(
                                                    # layout=False,
                                                        strip=True, 
                                                        # return_chars=True
                                                        )
                        
                        
                        
                        for i, line in enumerate(lines):

                            #print(f"{line}\n\n")

                            line_str = line['text']

                            ## PREVIOUS METHOD
                            # line_size = [char['size'] for char in line['chars']]
                            # #print(line_size)
                            ## Check font size of whole line
                            # if (max(line_size)>13):   ## CHANGE FONT SIZE HERE
                            #     current_heading = line_str
                            #     #print(f"{heading}\n\n")

                             ## NEW METHOD
                            chars = line.get('chars', [])
                            if chars:
                                # Check the first character only
                                if chars[0]['size'] > threshold:  
                                 
                                        # Add previous section to list
                                        if self.current_text:
                                            self.SECTIONS.append((current_heading, "\n".join(self.current_text)))
                                            self.current_text = []

                                            logging.info(f"\n Heading:{current_heading}")
                                            print(f"\n {time.strftime('%H:%M:%S')} - Heading:{current_heading}")
                                            #logging.info(f"\n Text:{self.current_text}\n\n")

                                        current_heading = line_str
                                        
                                else:
                                    self.current_text.append(line_str)


                # Add last section to list
                if self.current_text:
                    self.SECTIONS.append((current_heading, "\n".join(self.current_text)))

            #print(f"\n Sections:{SECTIONS}")
            #logging.info(f"\n Sections:{self.SECTIONS}")
                
                                 

 

        def load_emb_model(self):
                
                # Load embedding model
                # print("Loading embedding model...")
                logging.info("Loading embedding model...")

                self.EMBEDDING_MODEL = OllamaEmbeddings(model="mxbai-embed-large")    

                ## Logging notes
                # print(f"\nEmbedding Model:{EMBEDDING_MODEL}")
                # logging.info(f"\nEmbedding Model:{EMBEDDING_MODEL}")

                #print(f"\nEmbedding Model features:{dir(EMBEDDING_MODEL)}")
                #logging.info(f"\nEmbedding Model features:{dir(EMBEDDING_MODEL)}")

                # print(f"\nEmbedding Model parameters:{EMBEDDING_MODEL._default_params}")
                # logging.info(f"\nEmbedding Model parameters:{EMBEDDING_MODEL._default_params}") 


        def split_to_chunks(self,):

            ''' Splitting Sections to Chunks using TEXT SPLITTER '''

    
            if os.path.exists(self.db_location):
                shutil.rmtree(self.db_location)

            


            ## Initialise Text splitter ##

            ## Parameters 
            ## 1000 - 200
            ## New - working: 500 - 100

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000,        
                                                    chunk_overlap=200, 
                                                        separators=
                                                                    ["\n\n",              # Paragraphs first
                                                                    "\n" ,             # Then lines
                                                                    ". " ,              # Then sentences
                                                                    " " ,               # Then words
                                                                    "" ]                # Finally characters
                                                                    )
                                        

            # print(f"\nSplitter:{splitter}")
            # logging.info(f"\nSplitter:{splitter}")

            # print(f"\nSplitter features:{dir(splitter)}")
            # logging.info(f"\nSplitter features:{dir(splitter)}")         

            

            
            

            logging.info("Preparing documents for embedding...")

            if self.add_documents:
                print(f"{time.strftime('%H:%M:%S')} - Preparing documents for embedding...")
                doc_id = 0

                for heading, section_text in tqdm(self.SECTIONS, desc="Processing sections"):

                    chunks = splitter.split_text(section_text)

                    for chunk in chunks:
                        self.documents.append(Document(page_content=chunk, metadata={"section": heading}))
                        self.ids.append(str(doc_id))
                        doc_id += 1

                        # print(f"\nChunk ID:{doc_id}")
                        #logging.info(f"\nChunk ID:{doc_id}")

                        # print(f"\nSection:{heading}")
                        #logging.info(f"\nSection:{heading}")

                        # print(f"\nChunk:{chunk}")
                        #logging.info(f"\nChunk:{chunk}")

                print(f"{time.strftime('%H:%M:%S')} - Prepared {len(self.documents)} document chunks.")
                logging.info(f"Prepared {len(self.documents)} document chunks.")


        def Get_emb_vectors(self):

                ''' Convert Documents to embedding vectors and store in Vector DB '''

                # Initialise Vector DB
                VECTOR_STORE = Chroma(
                    collection_name="Data",
                    persist_directory=self.db_location,
                    embedding_function=self.EMBEDDING_MODEL
                )

                # print(f"\nVectorDB:{VECTOR_STORE}")
                # logging.info(f"\nVectorDB:{VECTOR_STORE}")

                #print(f"\nVectorDB features:{dir(VECTOR_STORE)}")
                #logging.info(f"\nVectorDB features:{dir(VECTOR_STORE)}")

                

                if self.add_documents:

                    print(f"{time.strftime('%H:%M:%S')} - Embedding and storing documents...")
                    logging.info("Embedding and storing documents...")

                    batch_size = 50
                    total = len(self.documents)

                    for i in tqdm(range(0, total, batch_size), desc="Embedding documents"):
                        batch_docs = self.documents[i: i + batch_size]
                        batch_ids = self.ids[i: i + batch_size]
                        VECTOR_STORE.add_documents(documents=batch_docs, ids=batch_ids)

                    #vector_store.persist()



                ## Fetch top k relevant documents based on similarity 
                self.retriever = VECTOR_STORE.as_retriever(search_kwargs={"k": 2})   
                print(f"{time.strftime('%H:%M:%S')} - Retriever is ready.")
                logging.info(f"Retriever is ready.")

                # print(f"\nRetriever:{retriever}")
                # logging.info(f"\nRetriever:{retriever}")

                # #print(f"\nRetriever features:{dir(retriever)}")
                # #logging.info(f"\nRetriever features:{dir(retriever)}")


        def Get_existing_emb_vectors(self):
             

                ''' Use existing Vector DB '''

                # Initialise Vector DB
                VECTOR_STORE = Chroma(
                    collection_name="Data",
                    persist_directory=self.db_location,
                    embedding_function=self.EMBEDDING_MODEL
                )

                # print(f"\nVectorDB:{VECTOR_STORE}")
                # logging.info(f"\nVectorDB:{VECTOR_STORE}")

                #print(f"\nVectorDB features:{dir(VECTOR_STORE)}")
                #logging.info(f"\nVectorDB features:{dir(VECTOR_STORE)}")




                ## Fetch top k relevant documents based on similarity 
                self.retriever = VECTOR_STORE.as_retriever(search_kwargs={"k": 2})   
                print(f"{time.strftime('%H:%M:%S')} - Retriever is ready.")
                logging.info(f"Retriever is ready.")

                # print(f"\nRetriever:{retriever}")
                # logging.info(f"\nRetriever:{retriever}")

                # #print(f"\nRetriever features:{dir(retriever)}")
                # #logging.info(f"\nRetriever features:{dir(retriever)}")

             




        



except Exception as e:

    print("Error occured:",e)
    traceback.print_exc()
    logging.error(f"Error occured:{e}. Traceback:{traceback.print_exc()}")