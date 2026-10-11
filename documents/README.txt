Title: FHC dataset underlying the publication: A Customised Down-sampling Machine Learning Approach for Sepsis Prediction
Author: Qinhao Wu, Fei Ye, Qianqian Gu, Quan Xiao
Licence: CC0

Dataset Usage:
If you want to use this dataset, please reference the following article:
	Wu, Q., Ye, F., Gu, Q., Shao, F., Zhan, Z., Long, X., ... & Zhang, J. (2024). A customised down-sampling machine learning approach for sepsis prediction. International Journal of Medical Informatics. https://doi.org/10.1016/j.ijmedinf.2024.105365

Dataset Structure:
FHC Dataset
	|-sepsis
	|	|-*.csv: multiple septic patient records
	|
	|-nonsepsis
		|-*.csv: multiple non-septic patient records

Data Format: [Patient ID].csv
Data Description: Table data with the column names as vital signs, laboratory values, demographic information, and sepsis label ("0" for no sepsis and "1" for sepsis). Each csv file records a single patient.

Methododology:
The collected data contained laboratory test values and vital signs from adult ICU patients, including 69 sepsis cases and 46 non-septic cardiovascular-disease-only cases. The laboratory tests were conducted following the routine of clinical practice. The laboratory results were collected on a daily basis. The laboratory instruments and measurements are listed in the supplementary material. The items of daily laboratory tests were used as data features. The sepsis label was given by the intensivist's suspicion of onset time following the Sepsis-3 clinical criteria. Features in the FHC dataset contain 5 vital signs, 31 laboratory values and 4 demographic information. Vital signs collected manually by nurses include temperature (Temp), heart rate (HR), systolic blood pressure (SBP) and diastolic blood pressure (DBP).  

The laboratory routine for gathering the measurement is stated as follows: 
	- The fully automatic blood cell analyser, Sysmex XN-2800, provides the measurement for blood routine examination. Specifically, the colourimetric assay is used to detect haemoglobin. 
	- The electrolyte examination is provided by Mindray Global BS-820, which is used to detect the pH value. Specifically, the o-cresolphthalein complexone assay is used to detect the total calcium ions, and the enzymatic assay is used to detect potassium ions.
	- For the liver and coagulation function examination, the enzymatic assay is used to detect bilirubin direct and bilirubin total. 
	- STAGO STA-Compact provides the measurement, including prothrombin time, activated partial thromboplastin time and Fibrinogen, for the clotting, chromogenic, and immunologic examinations. 
	- For the blood gas analysis, a blood gas analyser, RAPIDPoint 500 System from Siemens Healthineers, is used to detect partial pressure of oxygen and partial pressure of carbon dioxide, etc.

Feature Description:
Feature Name	Feature Description (unit)
-Vital signs 
     Temp	Temperature  
     HR		Heart rate  
     O2Sat	Pulse oximetry (%)   
     SBP	Systolic blood pressure  
     DBP	Diastolic blood pressure    
-Laboratory values         
     ALT	Alanine transaminase (U/L)  
     AST	Aspartate transaminase (U/L)   
     BEb	BaseExcess (mmol/L)  
     BUN	Blood urea nitrogen (mmol/L)   
     Bilirubin direct	Bilirubin direct (µmol/L)  
     Bilirubin total	Bilirubin total (µmol/L) 
     Ca		Calcium (mmol/L) 
     Ca++	Calcium ion (mmol/L) 
     CL		Chloride (mmol/L) 
     Creatinine	Creatinine (µmol/L) 
     FiO2	Fraction of inspired oxygen (%) 
     Fibrinogen	Fibrinogen (g/L) 
     GLU	Glucose (mmol/L)  
     HCO3	Bicarbonate (mmol/L) 
     HCT 	Hematocrit (%)   
     HGB 	Hemoglobin (g/L)     
     INR 	International normalized ratio  
     K 		Potassium (mmol/L)  
     Na 	Sodium (mmol/L)  
     Platelets 	Platelets(count*$10^9/L$)  
     PT 	Prothrombin time (seconds)  
     PTT  	partial thromboplastin time (seconds)  
     PCO2 	Partial Pressure of Carbon Dioxide (mmHg)   
     pH 	Blood pH  
     PO2 	Partial pressure of oxygen (mmHg)  
     PaCO2 	Partial pressure of carbon dioxide from arterial blood (mmHg)  
     SBC 	Standard bicarbonate (mmol/L)  
     SaO2 	Oxygen saturation (%)   
     Troponin 	Troponin (ng/mL)   
     Urine	Urine Output(ml/d)   
     WBC 	Leukocyte count (count*$10^9/L$)    
-Demographic Information
     Age 	Years  
     Gender 	Female (``f'') or Male (``m'')  
     HospAdmTime Minutes between hospital admit and ICU admit  
     ICULOS 	ICU length-of-stay (minutes  since ICU admit)  



