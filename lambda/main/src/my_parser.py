import spacy
import regex as re
import csv
from src.association import Association


def reformat_phone_number(text):
    # Extract all digit sequences from the string
    digits = re.findall(r'\d+', text)

    # Concatenate the digits to form a single string of digits
    all_digits = ''.join(digits)

    # If there are exactly 10 digits, format them. Otherwise, return an error or None.
    if len(all_digits) == 10:
        return f"{all_digits[:3]}-{all_digits[3:6]}-{all_digits[6:]}"
    else:
        return None  # or you can raise an error or return the input string unmodified


def reformat_name(text: str):
    # Remove leading and trailing spaces
    text = text.strip()

    # Split the text into words
    words = re.findall(r'\b\w+\b', text)

    # Keep track of words that should not be converted to title case
    preserve_case = set()

    # Identify words with special capitalization (e.g., "McCann")
    for word in words:
        if re.search(r'[a-z\p{Lu}]+\p{Lu}+', word, re.UNICODE) and not word.isupper() or len(word) == 2:
            preserve_case.add(word)

    # Convert the remaining words to title case
    words = [word.title() if word not in preserve_case else word for word in words]

    # Join the words back into a string
    result = ' '.join(words)

    return result


# Function to load the English NER model
def load_ner_model():
    print('Loading model')
    return spacy.load("en_core_web_trf", disable=[
        "tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"])

# Function to generate a list of regex patterns from a CSV file


def generate_regex_patterns_from_csv(csv_file_path):
    roles_caps_key = set()
    with open(csv_file_path, 'r') as roles_file:
        reader = csv.DictReader(roles_file)
        all_roles = []
        for row in reader:
            role = row['Role']
            abbreviation = row.get('Abbreviation')
            role_pattern = re.escape(role)
            all_roles.append(role_pattern)
            roles_caps_key.add(role)
            if abbreviation:
                all_roles.append(re.escape(abbreviation))
                roles_caps_key.add(abbreviation)

        all_roles = sorted(all_roles, key=lambda x: len(x), reverse=True)

        pattern = re.compile(r'\b(' + '|'.join(all_roles) +
                             r')(?:,|/| / )?(' + '|'.join(all_roles) + r')?\b', re.I)

    return pattern, roles_caps_key

# Function to compile a regex pattern from a list of words in a text file


def load_not_names_regex(text_file_path):
    with open(text_file_path, 'r') as file:
        text = file.read()
        # Split the text into words
        words = text.split()
        # Escape the words
        escaped_words = [re.escape(word) for word in words]
        # Return a regex
        return re.compile(r'\b(' + '|'.join(escaped_words) + r'){1,}\b', re.I)


# Have ChatGPT explain this one
def compile_regex_name_pattern():
    return re.compile(r"\b(?!N/A)\p{Lu}+[\p{L}'-]*(?:\s\p{Lu}+[\p{L}'-]+)*(?:\s\p{Lu}+[\p{L}'-]+)?(?:\s\p{Lu}+[\p{L}'-]+)?(?:\s\p{Lu}+[\p{L}'-]+)?(?:\s\p{Lu}+[\p{L}'-]+)?(?:\s\p{Lu}+[\p{L}'-]+)?\b", re.UNICODE)


def compile_regex_email_pattern():
    return re.compile(r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])')


class ContactsEngine:

    def __init__(self):
        self.nlp = load_ner_model()

    def get_contacts(self, text):
        # Split text into lines
        lines = text.split('\n')

        # Generate regex patterns for roles and abbreviations from a CSV file
        roles_patterns, roles_key = generate_regex_patterns_from_csv(
            './src/res/roles.csv')
        # Compile a regex pattern from a list of words in a text file
        not_names_pattern = load_not_names_regex(
            './src/res/not_names.txt')
        # Precompile regular expressions
        phone_pattern = re.compile(
            r"(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}")
        name_pattern = compile_regex_name_pattern()
        emails_pattern = compile_regex_email_pattern()

        # Initialize data structures
        ner_associations = dict()

        # Lines with phone numbers without matching names
        orphan_lines = set()

        for line in lines:
            # Filter into lines that contain a phone number
            if phone_pattern.search(line):
                # Load the NLP document
                doc = self.nlp(line)

                # Match the phone numbers
                phones = [(m.start(), m.group().strip())
                          for m in phone_pattern.finditer(line)]

                # Extract names
                names = [(ent.start_char, ent.end_char - 1, ent.text.strip())
                         for ent in doc.ents if ent.label_ == 'PERSON']

                # Match the emails
                email_candidates = [(m.start(), m.group().strip())
                                    for m in emails_pattern.finditer(line)]

                remaining_text = line

                # Match the phone numbers
                phones_to_remove = set()
                names_to_remove = set()

                for phone_start, phone in phones:
                    # We'll search for the closest name preceding the phone number
                    names_preceding_phone = [(_, name_end, name) for _, name_end,
                                             name in names if name_end < phone_start]
                    if names_preceding_phone:
                        closest_name = min(
                            names_preceding_phone, key=lambda x: abs(x[0] - phone_start))
                        if closest_name not in names_to_remove:
                            formatted_name = reformat_name(closest_name[2])
                            formatted_phone = reformat_phone_number(phone)
                            if formatted_name not in ner_associations:
                                ner_associations[formatted_name] = Association(
                                    formatted_name, {formatted_phone}, set(), set(), remaining_text)
                            else:
                                ner_associations[formatted_name].phones.add(
                                    formatted_phone)
                            names_to_remove.add(closest_name)
                            phones_to_remove.add((phone_start, phone))
                    else:
                        orphan_lines.add(line)

                for phone in phones_to_remove:
                    phones.remove(phone)
                    remaining_text.replace(phone[1], '')

                # Look for roles in the remaining text
                roles_in_line = []
                matches = list(re.finditer(roles_patterns, remaining_text))
                if matches:
                    roles_in_line += [(m.start(), m.end(), m.group().strip())
                                      for m in matches]

                # Filter roles to retain the most specific roles
                line_roles = set()
                for i, role in enumerate(roles_in_line):
                    longest_role = role
                    for j, role2 in enumerate(roles_in_line):
                        if i != j:
                            a, b = role[0], role[1]
                            c, d = role2[0], role2[1]
                            if a <= d and c <= b:
                                if len(role2[2]) > len(longest_role[2]):
                                    longest_role = role2
                    line_roles.add(longest_role)

                for name in names:
                    name_start, name_end, name_string = name[0], name[1], name[2]
                    if line_roles:
                        closest_role = min(line_roles, key=lambda x: min(
                            abs(x[0] - name_end), abs(x[1] - name_start)))
                        role_string = closest_role[2]
                        # Only add people with phone numbers, so make sure they are already in the list
                        if name_string in ner_associations:
                            def role_capitalization(role: str) -> str:
                                search_role_lower = role.lower()
                                for item in roles_key:
                                    if item.lower() == search_role_lower:
                                        return item
                                return None
                            # We don't store all the '/'-separated permutations of roles, lol
                            if '/' not in role_string and ',' not in role_string:
                                role_string = role_capitalization(role_string)
                            ner_associations[name_string].roles.add(
                                role_string)
                            ner_associations[name_string].source = remaining_text
                        remaining_text.replace(role_string, '')

                    emails_to_remove = set()
                    for email_start, email in email_candidates:
                        # We'll search for the closest name preceding the phone number
                        names_preceding_phone = [(_, name_end, name) for _, name_end,
                                                 name in names if name_end < email_start]
                        if names_preceding_phone:
                            closest_name = min(
                                names_preceding_phone, key=lambda x: abs(x[0] - email_start))
                            ner_associations[reformat_name(
                                closest_name[2])].emails.add(email)
                            names_to_remove.add(closest_name)
                            emails_to_remove.add((email_start, email))
                        else:
                            orphan_lines.add(line)

                    for email in emails_to_remove:
                        email_candidates.remove(email)
                        remaining_text.replace(email[1], '')

                # If fewer names than phone numbers are recognized OR if there is a remaining name without a matching phone, add the line to orphan_lines
                if phones:
                    # Find names by first removing all the roles
                    roles_in_line = [(m.start(), m.end(), m.group().strip())
                                     for m in roles_patterns.finditer(remaining_text)]

                    # Remove all roles so we can just search for names
                    for (role_start, role_end, _) in reversed(roles_in_line):
                        remaining_text = remaining_text[:role_start] + \
                            remaining_text[role_end:]

                    # Filter out not_names
                    nns = [(m.start(), m.end())
                           for m in re.finditer(not_names_pattern, remaining_text)]
                    for (nn_start, nn_end) in reversed(nns):
                        remaining_text = remaining_text[:nn_start] + \
                            remaining_text[nn_end:]

                    # Filter lines that don't contain two words side by side with the first letter capitalized
                    name_candidates = [(m.start(), m.end(), m.group().strip())
                                       for m in name_pattern.finditer(remaining_text)]
                    for phone_start, phone in phones:
                        # We'll search for the closest regex-matched name preceding the phone number
                        names_preceding_phone = [(name_start, name_end, name) for name_start, name_end,
                                                 name in name_candidates if name_end < phone_start]
                        if names_preceding_phone:
                            # Assume name comes before phone, find the name for a phone number
                            closest_name = min(
                                names_preceding_phone, key=lambda x: abs(x[1] - phone_start))

                            phone_name = reformat_name(closest_name[2])

                            if phone_name:
                                # Of the roles matched above, find the closest one to the name attached to the phone number
                                closest_role = min(roles_in_line, key=lambda x: min(
                                    abs(closest_name[0] - x[1]),
                                    abs(closest_name[1] - x[0])
                                ))[2] if roles_in_line else None
                                # Remove the phone number so it doesn't get picked up in the email
                                remaining_text.replace(phone, '')
                                # Sanitize phone number
                                phone = reformat_phone_number(phone)

                                # If we have a name, try to find an email for it
                                # Re-match the emails since removing phone numbers may change the matches
                                # Match the emails, starting after the name
                                regex_emails = set()
                                email_candidates = [(m.start(), m.group().strip())
                                                    for m in emails_pattern.finditer(remaining_text, pos=closest_name[0] + 1)]
                                if email_candidates:
                                    regex_emails.add(min(email_candidates, key=lambda x: abs(
                                        x[0] - closest_name[0]))[1] or '')

                                # Take care that the regex may have found a partial name..
                                # If the name is a first and last, let's try to match it with one we already have
                                if ' ' in phone_name:
                                    for x in ner_associations:
                                        if phone_name in x:
                                            phone_name = x

                                # Check if the name is already in the regular matches
                                if phone_name in ner_associations:
                                    ner_associations[phone_name].emails = set(
                                        list(ner_associations[phone_name].emails) + list(regex_emails))
                                    if closest_role:
                                        ner_associations[phone_name].roles = set(
                                            list(ner_associations[phone_name].roles) + [closest_role])
                                    ner_associations[phone_name].phones = set(
                                        list(ner_associations[phone_name].phones) + [phone])
                                    # Check if the name is >=2 in length, and a role is present, making it likelier to be a real name
                                elif len(phone_name) >= 2 and roles_in_line:
                                    ner_associations[phone_name] = Association(phone_name,
                                                                               {phone}, regex_emails, {closest_role} if closest_role else {}, remaining_text)

        # Print associations
        for val in ner_associations.values():
            print(val)

        # print('\nRegex associations: ')
        # for val in regex_associations.values():
        #     print(val)

        return list(ner_associations.values())


def main():
    engine = ContactsEngine()
    engine.test_filename('./test/samples/example8.pdf')


# Check if the script is being run as the main program
if __name__ == "__main__":
    main()
