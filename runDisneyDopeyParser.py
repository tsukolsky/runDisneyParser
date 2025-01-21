import re, sys, argparse, time

DEBUG = False

SEX = "SEX"
AGE = "AGE"
FIVEK = "5k"
TENK = "10k"
HALF = "HALF MARATHON"
FULL = "MARATHON"
TOTAL_TIME = "TOTAL"

class Partcipant():
    def __init__(self, line : str):
        self.name = "Empty"
        self.age = 0
        self.sex = "NA"
        self.origin = "Unknown"

        self.line = line

        # Break the line into three parts - whats before the times, what's after, and the times themselves
        firstPos = self.GetFirstTimePosition(line)
        lastPos = self.GetLastTimePosition(line)
        preamble = line[:firstPos]
        postamble = line[lastPos:]
        self.stringTime = line[firstPos:lastPos]

        # Get the details
        self.ParsePreamble(preamble)
        self.ParseTimes(self.stringTime)
        self.origin = postamble.strip().strip(',')

    def __str__(self):
        return f"{self.line}\nParticipant: {self.name} {self.age} {self.sex} {self.origin}\n{self.stringTime}\n{self._times}"

    def ParsePreamble(self, preamble):
        # Preamble should have spaces inbetween values, some will be None or empty as well
        # SMITH, JOHN 33 M is an example
        subfields = preamble.split(' ')
        subfields = list(filter(None, subfields))
        nameString = " ".join(subfields[:-2])
        self.name = nameString
        self.age = subfields[-2].strip().strip(',')
        self.sex = subfields[-1].strip().strip(',')

    def ConvertToSeconds(self, timestring : str) -> int:
        # Takes in time in hh:mm:ss format, or mm:ss format if it's a respectable 5k/10k time, and returns seconds
        fields = timestring.split(':')
        totalTime = int(fields[-1]) + int(fields[-2])*60
        if len(fields) > 2:
            totalTime += int(fields[0])*60*60
        return totalTime

    def GetFirstTimePosition(self, middleString) -> int:
        # Get location of first time - this could be a 5k/10k split, so it might only have one semicolon
        # TODO: Unhandled error here if there is no start_pos, but that should have been cleared by earlier parse
        # to validate there is enough times
        start_pos = 0
        pattern = r"(\d+):(\d+)"
        res = re.split(pattern, middleString)
        matches = list(re.finditer(pattern, middleString))
        if matches:
            first_match = matches[0]
            start_pos = first_match.start()
            end_pos = first_match.end()
        else:
            print(f"Error parsing string {self.lastname}, full {self.line}, middle {middleString}")
        return start_pos

    def GetLastTimePosition(self, middleString) -> int:
        # Get location of last time - this should be a marathon time, so three objects in hh:mm:ss
        # TODO: Unhandled error here if there is no end_pos, but that should have been cleared by earlier parse
        # to validate there is enough times
        pattern = r"(\d+):(\d+):(\d+)"
        res = re.split(pattern, middleString)
        matches = list(re.finditer(pattern, middleString))

        if matches:
            last_match = matches[-1]
            start_pos = last_match.start()
            end_pos = last_match.end()
            return end_pos
        else:
            return 0

    def ParseTimes(self, times : str):
        print("Base class call")
        self.result = {FIVEK : 0, TENK : 0, HALF : 0, FULL : 0, TOTAL_TIME : 0}

    def GetCSVLine(self, separator : str) -> str:
        print("Base class call")
        return ""

class GoofyParticipant(Partcipant):
    def ParseTimes(self, times : str):
        # Take the time string and parse out all the times. Goofy has clock/net/clock/net, so grab #2 and #4 (1,3)
        individualResult = {HALF : 0, FULL : 0, TOTAL_TIME : 0}
        pattern = r"(\d+):(\d+):(\d+)"
        timeStr = times
        res = re.split(pattern, timeStr)
        matches = list(re.finditer(pattern, timeStr))
        if matches:
            last_match = matches[-1]
            start_pos = last_match.start()
            end_pos = last_match.end()
            times = timeStr[0:end_pos].split(" ")
        else:
            # no match, meaning it isn't there. this should never happen based on previous checks
            raise("error - unknown value in string field")
            pass

        numSec = self.ConvertToSeconds(times[-1])
        individualResult[FULL] = numSec
        numSec = self.ConvertToSeconds(times[-3])
        individualResult[HALF] = numSec

        # Save the final result and tally up their total time
        self.result = individualResult
        self.result[TOTAL_TIME] = self.result[HALF] + self.result[FULL]

    def GetCSVLine(self, separator : str) -> str:
        dataList = [self.name, self.age, self.sex, self.origin, self.result[HALF], self.result[FULL], self.result[TOTAL_TIME]]
        ostring = ""
        for item in dataList[:-1]:
            ostring += f"{item}{separator}"
        ostring += f"{dataList[-1]}"
        return ostring

class DopeyParticipant(Partcipant):
    def ParseTimes(self, times : str):
        # Take the time string and parse out all the times. Based on trackshack's PDF, there is always a marathon
        # or half marathon. Becuase we want to get Dopey results (original intent), we want only racers with
        # these last two larger times in their results. So assume* they are always there, and if one is missing
        # it's the 5k
        individualResult = {FIVEK : 0, TENK : 0, HALF : 0, FULL : 0, TOTAL_TIME : 0}
        pattern = r"(\d+):(\d+):(\d+)"
        timeStr = times
        res = re.split(pattern, timeStr)
        matches = list(re.finditer(pattern, timeStr))
        if matches:
            last_match = matches[-1]
            start_pos = last_match.start()
            end_pos = last_match.end()
            times = timeStr[0:end_pos].split(" ")
        else:
            # no match, meaning it isn't there. this should never happen based on previous checks
            raise("error - unknown value in string field")
            pass

        # Go backwards through the list, assuming full and half are ones always written in PDF
        # Why? Because in 2025 people had their bibs not working for the 5k or 10k, but were fixed in
        # half and full. This script does not accound for these issues completely. Excel is your friend
        # for that
        if len(times) > 0:
            numSec = self.ConvertToSeconds(times[-1])
            individualResult[FULL] = numSec
        if len(times) > 1:
            numSec = self.ConvertToSeconds(times[-2])
            individualResult[HALF] = numSec
        if len(times) > 2:
            numSec = self.ConvertToSeconds(times[-3])
            individualResult[TENK] = numSec
        if len(times) > 3:
            numSec = self.ConvertToSeconds(times[-4])
            individualResult[FIVEK] = numSec

        # Save the final result and tally up their total time
        self.result = individualResult
        self.result[TOTAL_TIME] = self.result[FIVEK] + self.result[TENK] + self.result[HALF] + self.result[FULL]

    def GetCSVLine(self, separator : str) -> str:
        dataList = [self.name, self.age, self.sex, self.origin, self.result[FIVEK], self.result[TENK],
                    self.result[HALF], self.result[FULL], self.result[TOTAL_TIME]]
        ostring = ""
        for item in dataList[:-1]:
            ostring += f"{item}{separator}"
        ostring += f"{dataList[-1]}"
        return ostring

def ParsePDF(filename : str, outputfile : str = None):
    # Using pyupdf4llm, parse a PDF and get the text lines in the document/file
    try:
        import pymupdf4llm as pdf
    except Exception as e:
        print(f"Unable to import library for parsing - pip[3] install pymupdf4llm")
        return []

    md_text = pdf.to_markdown(filename)
    if outputfile is not None:
        with open(outputfile, 'w') as ofh:
            num = ofh.write(md_text)
    lines = md_text.split('\n')
    return lines

def SetupArgparse():
    # Setup Argparse for runDisney program - you can choose to evaluate a pdf or markdown file
    parser = argparse.ArgumentParser(prog=__doc__, description="Parser for results data provided by TrackShack of runDisney Dopey Challenge. Exports a CSV for import into excel for further data analysis")
    parser.add_argument('-t', '--times', type=int, help='Minimum number of times to look for.', default=2)
    parser.add_argument('-o', '--output', type=str, help='Output file for excel formatted data', default="output/output.csv")
    parser.add_argument('-s', '--separater', type=str, help='separater of data for csv file. default is semicolon \';\'', default=';')
    parser.add_argument('-e', '--export', type=str, help="Export markdown of PDF parse to file specificed", default=None)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-m', '--markdown', type=str, help='Markdown file to parse')
    group.add_argument('-p','--pdf', type=str, help='Input PDF')

    dgroup = parser.add_mutually_exclusive_group(required=True)
    dgroup.add_argument('-g', '--goofy', action="store_true", default=False, help = "Goofy parse")
    dgroup.add_argument('-d', '--dopey', action="store_true", default= False, help = "Dopey parse")
    return parser

if __name__ == "__main__":
    # Setup argparse and grab input data
    parser = SetupArgparse()
    args = parser.parse_args()
    lines = []
    if args.markdown is not None:
        try:
            with open(args.markdown, 'r') as ifh:
                lines = ifh.readlines()
        except Exception as e:
            print(f"Unable to open and parse markdown file {args.markdown}: {str(e)}")
            sys.exit(-1)
    else:
        print(f"Converting PDF {args.pdf} to data")
        lines = ParsePDF(args.pdf, args.export)
    print(f"Grabbed {len(lines)} lines to parse")

    # Open output file and start parsing the input data
    ofh = open(args.output, 'w')
    for line in lines:
        line = line.lstrip().rstrip()

        # Check to see how many times are in the line - if less than the minimum (argparse option), throw it out
        pattern = r"(\d+):(\d+)"
        matches = re.findall(pattern, line)
        count = len(matches)
        if count >= args.times:
            if args.dopey:
                part = DopeyParticipant(line)
            else:
                part = GoofyParticipant(line)
            ofh.write(part.GetCSVLine(args.separater)+"\n")
    ofh.close()
    print(f"Successfully exported data to csv")
