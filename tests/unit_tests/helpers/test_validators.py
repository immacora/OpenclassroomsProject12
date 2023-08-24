import pytest
from django.core.exceptions import ValidationError
from helpers.validators import (
    unicodealphavalidator,
    unicodecharfieldvalidator,
    textfieldvalidator,
    digitalcharfieldvalidator,
)


@pytest.mark.django_db
class Testvalidators:
    """
    GIVEN a value from a user input
    WHEN the request is submitted
    THEN checks the return is OK
    """

    def test_unicodealphavalidator(self):
        """Checks that the return contains only alphabetic characters with apostrophe, hyphen and space."""

        # Valid input
        unicodealphavalidator("Nom-composé d'un utilisateur")

        # Invalid input
        invalid_inputs = ["123", "user1", "Special !@#$ characters"]
        for input_str in invalid_inputs:
            with pytest.raises(ValidationError):
                unicodealphavalidator(input_str)

    def test_unicodecharfieldvalidator(self):
        """Checks that the return contains only alphanumeric characters with apostrophe,\
        hyphen, @, point and space."""

        # Valid input
        valid_inputs = ["SARL @HOME", "Événement 2.0", "Rue de l'Hôtel-de-Ville"]
        for input_str in valid_inputs:
            unicodecharfieldvalidator(input_str)

        # Invalid input
        invalid_inputs = ["<script>alert('XSS')</script>", "event%name"]
        for input_str in invalid_inputs:
            with pytest.raises(ValidationError):
                unicodecharfieldvalidator(input_str)

    def test_textfieldvalidator(self):
        """Checks that the return does not contain special characters."""

        # Valid input
        valid_inputs = [
            "Notes sur l'événement 2.0 avec jean-pierre_DJ@contact.com (option DJ 2)"
        ]
        for input_str in valid_inputs:
            textfieldvalidator(input_str)

        # Invalid input
        invalid_inputs = ["<script>alert['XSS']</script>", "Special#chars&", "z={"]
        for input_str in invalid_inputs:
            with pytest.raises(ValidationError):
                textfieldvalidator(input_str)

    def test_digitalcharfieldvalidator(self):
        """Checks that the return contains only numeric characters."""

        # Valid input
        digitalcharfieldvalidator("056789")

        # Invalid input
        invalid_inputs = ["abc", "123.45", "1 2 3", "!"]
        for input_str in invalid_inputs:
            with pytest.raises(ValidationError):
                digitalcharfieldvalidator(input_str)
