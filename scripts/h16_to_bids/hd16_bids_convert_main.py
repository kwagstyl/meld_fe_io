from converter import Converter


def main():

    converter = Converter()
    converter.new_dir()
    converter.transfer_csv()
    converter.case_list_convert()


if __name__ == '__main__':
    main()
