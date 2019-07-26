import modules.google_regex as regex
import modules.google_ocr as ocr
import pprint

pp = pprint.PrettyPrinter()

def main():
    
    file = '/Users/seanchan/goDutch/test/testpic4.jpeg'
    
    response_dict = ocr.get_full_response_dict(file)
    data = regex.combined_parse_and_regex(response_dict,15)
    pp.pprint(data)

if __name__ == "__main__":
    main()
