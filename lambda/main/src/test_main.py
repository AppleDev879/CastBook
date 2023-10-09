import unittest
import csv
import traceback  # Import the traceback module
import my_parser
from association import Association


def get_key(key_name):
    try:
        with open(f'./lambda/main/test/keys/{key_name}', 'r') as key_file:
            reader = csv.DictReader(key_file)
            people = []
            for row in reader:
                name = row.get('Name')
                phones = set(row.get('Phone').split('&&'))
                emails = set(row.get('Email').split(
                    '&&')) if 'Email' in row else set()
                roles = set(row.get('Role').split('&&'))

                people.append(Association(name, phones, emails, roles))
            return {person.name: person for person in people}

    except Exception as e:  # Catch all exceptions for debugging
        print(f"Error opening or parsing {key_name}: {e}")
        traceback.print_exc()  # Print the traceback for detailed error information


class TestParsingFiles(unittest.TestCase):

    def run_test(self, result, key, test_no):
        # Check that the total number of matches equals the number in the key
        if len(key) > len(result):
            result_names = list(map(lambda x: x.name, result))
            for k_v in key:
                if k_v not in result_names:
                    print(f'\t❌[Test #{test_no}] > Result missing: {k_v}')
        elif len(key) < len(result):
            for r_v in result:
                if r_v.name not in key:
                    print(f'\t❌[Test #{test_no}] > Extra result entry: {r_v}')

        self.assertEqual(len(result), len(key))

        for entry in result:
            if entry.name not in key:
                print(
                    f'🚨 [Test #{test_no}] > {entry.name} not in key!\n\tEntry: {entry}')
            self.assertTrue(entry.name in key)
            if key[entry.name] != entry:
                print(
                    f'🚨 [Test #{test_no}] > {entry.name} does not match key!')
                print(f'\t❌ Try: {entry}')
                print(f'\t🔑 Key: {key[entry.name]}')
            self.assertTrue(key[entry.name] == entry)

    def test_role_matching(self):
        # Assuming patterns is the compiled regex pattern
        patterns, _ = my_parser.generate_regex_patterns_from_csv(
            './lambda/main/res/roles.csv')
        text = "Director / Producer Aaron Johns (214) 769-9834 aaronj2520@gmail.com 10:00 AM"
        matches = patterns.findall(text)
        self.assertTrue(len(matches) == 1)

    def test_example1(self):
        result = my_parser.test_filename(
            './lambda/main/test/samples/example1.pdf')
        key = get_key('key1.csv')
        self.run_test(result, key, 1)

    def test_example2(self):
        result = my_parser.test_filename(
            './lambda/main/test/samples/example2.pdf')
        key = get_key('key2.csv')
        self.run_test(result, key, 2)

    def test_example3(self):
        result = my_parser.test_filename(
            './lambda/main/test/samples/example3.pdf')
        key = get_key('key3.csv')
        self.run_test(result, key, 3)

    def test_example4(self):
        result = my_parser.test_filename(
            './lambda/main/test/samples/example4.pdf')
        key = get_key('key4.csv')
        self.run_test(result, key, 4)

    def test_example5(self):
        result = my_parser.test_filename(
            './lambda/main/test/samples/example5.pdf')
        key = get_key('key5.csv')
        self.run_test(result, key, 5)

    def test_example6(self):
        result = my_parser.test_filename(
            './lambda/main/test/samples/example6.pdf')
        key = get_key('key6.csv')
        self.run_test(result, key, 6)


if __name__ == '__main__':
    unittest.main()
