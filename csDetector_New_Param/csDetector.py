from devNetwork import devNetwork
import sys
import csv 

# since the interface of the execution is only command line input, we want something to adapt our web service
# we will have an adapter class that will extend csDetector and parses the local input

class CsDetector:

    def executeTool(self, argv):
        # formattedResult can be used to print well formatted data in console (if executed from cli)
        # result instead can be used to return the list of community smells acronym if executed from external sources
        formattedResult, result, config = devNetwork(argv)
        return formattedResult, result, config


if __name__ == "__main__":

    inputData = sys.argv[1:]
    tool = CsDetector()
    formattedResults, results1, results2 = tool.executeTool(inputData)
    print(results1)
    print(results2)
    print(formattedResults)
    
    with open('dict.csv', 'w') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in formattedResults.items():
            writer.writerow([key, value])
