import sys, getopt, os, csv
from googleCrawlers import GoogleMapsCrawler
import pandas as pd 


def generate_dict_keys(dfMainFile):

	registered = {}
	if len(dfMainFile) > 0:
		for i in range(0,len(dfMainFile)-1):
			key = (dfMainFile['Company_Name'].iloc[i] + dfMainFile['Street'].iloc[i]).encode("utf-8").hex()
			if key not in registered:
				registered[key] = 1

	return registered

def scrap_data (searchTermsFilePath,outputPath,mainFilePath):

	outputPath = outputPath.strip("/")
	
	header = ['Company_ID', 'Company_Name', 'Industry','Street','Town',
				'State','Zipcode','Country','Website', 'Phone_Number','Rate','Reviews','Register_Key']


	print (';'.join(header))

	if mainFilePath:
		dfMainFile = pd.read_csv(mainFilePath, sep=';',header=0,encoding='utf-8')
		registered = dfMainFile.set_index('Register_Key').T.to_dict('list')
		companyId = dfMainFile['Company_ID'].iloc[-1]
		dfMainFile = None
	else:
		registered = {}
		companyId =1
		mainFilePath = outputPath + "/main_data_file.csv"
		with open(mainFilePath, 'w') as file:
		 	writer = csv.writer(file,delimiter=";")
		 	writer = writer.writerow(header)
		 	file.close()
	
	searchTermsFile = open(searchTermsFilePath,"r")
	for searchTerm in searchTermsFile:
		crawler = GoogleMapsCrawler(registered,companyId)
		crawler.run(searchTerm)
		crawler.terminate(searchTerm,outputPath,mainFilePath)
		dfMainFile = pd.read_csv(mainFilePath, sep=';',header=0,encoding='utf-8')
		registered = dfMainFile.set_index('Register_Key').T.to_dict('list')
		companyId = crawler.companyId
		crawler = None

def main(argv):

	os.chdir(os.getcwd())
	parameters = ["input_file=","output_path=","main_file="]

	try:
		opts, args = getopt.getopt(argv,"hi:o:m:", parameters)

	except getopt.GetoptError:
		print ('no arguments passed')
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h','--help'):
			print ('scraper.py -i <search terms file> -o <output folder path> ' +
                    '-m <main data file if it exists>')
			sys.exit()
		elif opt in ("-i", "--input_file"):
			try:
				searchTermsFile = open(arg, 'r')
				searchTermsFile.close()
				searchTermsFilePath = arg
			except:
				print("The input file is invalid or not exists")
				sys.exit(2)
		elif opt in ("-o", "--output_path"):
			if os.path.isdir(arg):
				outputPath = arg
			else:
				print("The output folder path passed is invalid")
				sys.exit(2)
		elif opt in ("-m","--main_file"):
			if arg == "":
				mainFilePath = None
			else:
				try:
					mainFile = open(arg, 'r')
					mainFile.close()
					mainFilePath = arg
				except:
					print("The main data file is invalid or not exists")
					sys.exit(2)


	scrap_data(searchTermsFilePath,outputPath,mainFilePath)

if __name__ == "__main__":
   main(sys.argv[1:])
