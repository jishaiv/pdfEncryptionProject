# pdfEncryptionProject :
This project is done as part of the Basic Python training 

#Tasks involved in this project  : 

1. Enable the user to choose one folder , and encrypt all the available PDFs in that folder . Discard already encrypted PDFs 
2. The password for the PDF should be in the form of filename_datetime 
3. Save the encrypted PDFs details (filename,file password, filesize,encryption time, usr email id) to a csv file 
4. Add the same details to mysql database table 
5. Send email to the end user aftr every PDF encryption, attaching the encrypted pdf , and informing him the password 

Implemetation :

1. By using tkinter package, the user will be prompted to choose one folder from the system 
2. Separate class is created for pdfencryption related activities and functions were created inside the classs for pdfencryption, saving details to csv, loading details to database and sending mail, connect to db, and closing the connection 
3. by using instance of pdfencryption intance , the function for pdf encryption wil be called after the user selects the folder. 
4. pdf encryption is performed using pyPDF2 package , from within the method. The encrypted file is named as oldfilename_datetime . password is goven as oldfilename. 
5. If encrypted pdfs are already present in the folder, those will be discarded. 
6. once encryption is done , the details (filename,file password, filesize,encryption time, usr email id) were added to one csv file , and one database table. 
7. The csv file and db table  will be created for the very first execution of the prgram . And then details will be added successively. 
8. The user email will be asked for each of the pdf file , and the encrypted file and password info  will be sent to her/him .
9. The encrypted files and csv file will be stored inside a separate directory inside current working directoy (This directory will be created during first execution ) 
10. mysql.connector is used for establishing the connetcion witg hmysql database . 
11. Logging is implemented for easy traching 
12. try-catch-finally is used for error exception handling . 



