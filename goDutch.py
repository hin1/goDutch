import modules.google_regex as regex
import modules.google_ocr as ocr
import pprint

def main():
    
    file = '/Users/seanchan/goDutch/test/testpic4.jpeg'
    pp = pprint.PrettyPrinter()
    response_dict = ocr.get_full_response_dict(file)
    receipt = regex.get_lines(response_dict,10)
    data = regex.get_item_price_dict(receipt)
    pp.pprint(data)

if __name__ == "__main__":
    main()
