""" This file is last updated on 18-Feb 2022
@author : jisha.iv"""

import os
import PyPDF2
from datetime import datetime
from tkinter import filedialog
import tkinter.messagebox
import math
import pandas as pd
import mysql.connector
from mysql.connector import (connection)
from mysql.connector import errorcode
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging


class pdfEncryptor:
    """
    This class is created for encryption of PDF files.
    """
    def __init__(self, folder):
        self.folder = folder
    def encryption(self):
        """
        This function is to encrypt all the  PDF files in the folder
        """
        try:
            files = os.listdir(self.folder) #getting all files from input folder
            global pdf_files
            for pdf_files in files:
                if pdf_files.endswith(".pdf"): #checking if the file is PDF or not
                    global output_file_writer_name
                    output_file_writer_name = pdf_files.split(".pdf")[0]  #getting the filename without .pdf extension
                    pdf_files_folder = os.path.join(self.folder, pdf_files) #reframing the pdf name with the directory
                    pdf_in_file = open(pdf_files_folder, "rb") #opening the file in binary mode
                    inputpdf = PyPDF2.PdfFileReader(pdf_in_file)
                    if inputpdf.isEncrypted:  #checking if the file is already encrypted
                        print("Sorry", pdf_files, "is already encrypted")
                        logging.info("Encrypted pdf found in the directory, {}".format(pdf_files))
                        continue #continue for loop
                    pages_no = inputpdf.numPages #getting the number pf pages in pdf file
                    output = PyPDF2.PdfFileWriter()
                    for i in range(pages_no):
                        inputpdf = PyPDF2.PdfFileReader(pdf_in_file)
                        output.addPage(inputpdf.getPage(i)) #encrypting all the pages with the password
                        output.encrypt(output_file_writer_name)
                    global current_time
                    current_time = datetime.now().replace(microsecond=0) #getting current datetime and removing microsecond part
                    new_current_time = datetime.strftime(current_time, "%Y_%B_%d_%H_%M_%S") #converting time to strin format
                    global output_file
                    output_file = output_file_writer_name + "_" + new_current_time + ".pdf" #making the output file name in "oldfilename_datetime" format
                    current_dir=os.getcwd() #getting the current working directory
                    output_dir=os.path.join(current_dir,"EncryptedPDFs") #making the structure of output directory
                    if not os.path.isdir(output_dir): #checking if such directory exists
                        os.mkdir(output_dir) #making the directory to store encrypted PDFs and csv file with details
                    global output_file_folder
                    output_file_folder = os.path.join(output_dir, output_file) #combining output file name with directory
                    with open(output_file_folder, "wb") as outputStream:
                        output.write(outputStream)
                    logging.info("{x} pdf file is successfully encrypted and saved as {y}".format(x=pdf_files,y=output_file)) #logging the usccessful message as info
                    file_size = os.path.getsize(output_file_folder) #getting the file size of encrypted pdf
                    global sizeofFile_KB
                    sizeofFile_KB = math.ceil(file_size / 1024) # converting it to KB , and ceiling
                    usermail = input("enter the mail id of the end user for {} file: ".format(pdf_files)) #Getting the user email id for sending pdf
                    self.send_email(usermail) #Calling the function to send email
                    self.write_to_csv(usermail) #calling the function to write to csv
                    self.write_to_db(usermail) #calling the function to write to database
        except Exception as e: #catching the error if occured
            logging.critical("Error occured while pdf encryption ") #logging the error
            logging.critical(e)  #logging the error

    def write_to_csv(self,usermail):
        """
        This function is to generate/update csv with encrypted pdf file details
        """
        try:
            path_csv = os.getcwd() #getting the current working directory
            csv_file = os.path.join(path_csv,"EncryptedPDFs\encryptedfiles.csv") #making file structure of csv file to write the encrypted PDF details
            Path = os.path.isfile(csv_file) # checking if such path exists
            if Path == True:
                df = pd.read_csv(csv_file) #if path exists , reading the csv file ad pandas dataframe
                data = pd.DataFrame([[output_file,output_file_writer_name, sizeofFile_KB, current_time,usermail]],
                                    columns=['File Name', 'File Password','FileSize(KB)', 'Encryption Time','User Email Id']) #making dataframe using the available inputs
                df = pd.concat([df, data]) #combining two dataframes

            else:
                data = [output_file, output_file_writer_name,sizeofFile_KB, current_time,usermail] #data fro datframe
                columns = ['File Name','File Password', 'FileSize(KB)', 'Encryption Time','User Email Id'] #column names for dataframe
                df = pd.DataFrame(data, columns).T #making a dataframe
            df.to_csv(csv_file, index=False) #writing dataframe info to csv file
            logging.info("encrypted pdf details were updated in csv file for {}".format(output_file)) #logging successful message as info
        except Exception as e:
            logging.critical("Error occured while writing encrypted pdf information to the csv file ") #Logging the error
            logging.critical(e)

    def connect_to_db(self):
        """
        This function is created for connecting to db
        """
        try:
            global cnx
            global mycursor
            cnx = connection.MySQLConnection(user='dhoni', password='dhoni07', host='127.0.0.1', database='new_sample')
            logging.info("Database connection established successfully ") #establishing connection with the database
            mycursor = cnx.cursor() # creating cursor object
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR: #catching access denied exception
                logging.critical("Incorrect credentials entered for db connection, program terminated") #logging the error
            elif err.errno == errorcode.ER_BAD_DB_ERROR: #catching incorrect db name error
                logging.critical("Wrong db name entered , program terminated ") #logging the error
            else:
                logging.critical(err) #logging the other errors

    def close_db(self):
        """
        This function is created for closing the db connection
        """
        try:
            mycursor.close() #closing cursor
            cnx.commit() #commiting changes
            cnx.close() #closing connection
            logging.info("DB connection closed successfully . ") #logging the successful message
        except Exception as e:
            logging.critical("Error occured while closing db connection ") #logging the error if occured
            logging.critical(e)

    def write_to_db(self,usermail):
        """
        This function is created for writing encrypted pdf information to db
        """
        try:
            query1 = """ CREATE TABLE IF NOT EXISTS encryptedFiles (file_name VARCHAR(200),file_password VARCHAR(200),filSizeKB int,encyrptionTime DATETIME,userMail VARCHAR(50))""" #db query to create table
            mycursor.execute(query1)
            query2 = """INSERT INTO encryptedFiles VALUES (%s,%s,%s,%s,%s)""" #DB query to insert values
            val=[(output_file,output_file_writer_name,sizeofFile_KB, current_time,usermail)] #This variable is to store input values as list of tuple
            mycursor.executemany(query2,val) #executing query for insert operation
            logging.info("The data of encrypted pdf files were successfully updated in db table for {} ".format(output_file)) #logging the info for successful insertion
        except Exception as e:
            logging.critical("Error occured while while writing encrypted pdf data to db") #logging the error
            logging.critical(e)

    def send_email(self,usermail):
        """This function is created for sending email to the user with encrypted pdf as attachment """
        try:
            fromaddr = "jishaiv23@gmail.com"
            toaddr = usermail
            msg = MIMEMultipart()  # instance of MIMEMultipart
            msg['From'] = fromaddr # storing the senders email address
            msg['To'] = toaddr # storing the receivers email address
            user_name=toaddr.split("@")[0]
            msg['Subject'] = "PDF Encryption Successful for %s  !!"%pdf_files   # storing the subject
            body = "Hi %s ,\nYour PDF file , %s is successfully encrypted !! \npassword : %s \nPlease find the attachment for encrypted PDF "%(user_name,pdf_files,output_file_writer_name)  # string to store the body of the mail
            msg.attach(MIMEText(body, 'plain'))  # attach the body with the msg instance
            filename = output_file # open the file to be sent
            attachment = open(output_file_folder, "rb")
            p = MIMEBase('application', 'octet-stream')    # instance of MIMEBase and named as p
            p.set_payload((attachment).read()) # To change the payload into encoded form
            encoders.encode_base64(p)   # encode into base64
            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(p)  # attach the instance 'p' to instance 'msg'
            s = smtplib.SMTP('smtp.gmail.com', 587)  # creates SMTP session
            s.starttls() # start TLS for security
            with open("password.txt","r") as file_obj: #opening password file
                password=file_obj.read()
            s.login(fromaddr,password) # # Authentication
            text = msg.as_string() # Converts the Multipart msg into a string
            s.sendmail(fromaddr, toaddr, text) # sending the mail
            logging.info("Email sent to the user successfully for {x} to {y}".format(x=output_file,y=usermail))
            s.quit()   # terminating the session
        except Exception as e:
            logging.critical("Error occured while sending the encrypted file to the end user") #logging th error
            logging.critical(e)
def main():

    logging.basicConfig(filename='pdfEncryptionFromFolder.log',
                        encoding='utf-8',
                        filemode='a',
                        format='%(asctime)s:%(levelname)s:%(message)s',
                        datefmt="%Y-%m-%d:%H-%M-%S",
                        level=logging.DEBUG
                        )
    try:
        root = tkinter.Tk()
        root.withdraw()
        tkinter.messagebox.showinfo("PDF Encryptor", "Please select a directory") #giving instruction to the user to choose directory
        folder = filedialog.askdirectory() #taking folder from user, where the PDFs were stored
        pdfencry = pdfEncryptor(folder) #creating instance for pdfEncryptor class
        pdfencry.connect_to_db() #calling connect to db function to establish db connection
        pdfencry.encryption() #calling the encryption function to encrypt the PDFs
        pdfencry.close_db() #calling close_db connection to close db
        tkinter.messagebox.showinfo("PDF Encryptor", "Encryption is successful") #showing successful message
        logging.info("The whole program executed successfully !") #logging successful message
    except Exception as e:
        logging.critical("Error occured ") #logging error
        logging.critical(e)

if __name__ == "__main__":
    main()


