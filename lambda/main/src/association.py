
class Association:
    def __init__(self, name, phones, emails, roles, source=''):
        self._name = name
        self._phones = phones
        self._emails = emails
        self._roles = roles
        self._source = source

    def to_dict(self):
        phones_as_list = list(self.phones)
        emails_as_list = list(self.emails)
        roles_as_list = list(self.roles)
        return {
            "name": self.name,
            "roles": roles_as_list,
            "phones": phones_as_list,
            "emails": emails_as_list,
            "source": self.source
        }

    def __str__(self):
        return self._name + " " + str(self._phones or set()) + " " + str(self._emails or set()) + " " + (str(self._roles or ' '))

    # Getter for 'emails' attribute
    @property
    def emails(self):
        return self._emails

    # Setter for 'name' attribute
    @emails.setter
    def emails(self, new_email):
        self._emails = new_email

    # Getter for 'name' attribute
    @property
    def name(self):
        return self._name

    # Setter for 'name' attribute
    @name.setter
    def name(self, new_name):
        self._name = new_name

    # Getter for 'phones' attribute
    @property
    def phones(self):
        return self._phones

    # Setter for 'phones' attribute
    @phones.setter
    def phones(self, new_phones):
        self._phones = new_phones

    # Getter for 'role' attribute
    @property
    def roles(self):
        return self._roles

    # Setter for 'role' attribute
    @roles.setter
    def roles(self, new_role):
        self._roles = new_role

    # Getter for 'source' attribute
    @property
    def source(self):
        return self._source

    # Setter for 'role' attribute
    @source.setter
    def source(self, new_source):
        self._source = new_source

    def __eq__(self, other):
        if isinstance(other, Association):
            set_a_emails_lower = {element.lower() for element in self.emails}
            set_b_emails_lower = {element.lower() for element in other.emails}

            set_a_roles_lower = {element.lower() for element in self.roles}
            set_b_roles_lower = {element.lower() for element in other.roles}

            return other.name == self.name and set_a_emails_lower == set_b_emails_lower and other.phones == self.phones and set_a_roles_lower == set_b_roles_lower
        return False
