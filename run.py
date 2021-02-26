from awesomenauts import *
from AN_HTML_generator import *


def main():

    #x = parse_naut_names()
    #create_json_file(x)

    json_data_file = "awesomenauts.json"
    template_file_name = "card_template.html"
    output_file_name = "nauts.html"

    nauts_json = load_json_file(json_data_file)
    print(nauts_json)

    html = json_to_HTML(data = nauts_json,
                        template_file_name=template_file_name)

    # Write the HTML output string to a file

    fp = open(output_file_name, 'wb')
    fp.write(html.encode('utf-8'))
    fp.close()

if __name__ == "__main__":
    main()
