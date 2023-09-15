from django.core.validators import RegexValidator


unicodealphavalidator = RegexValidator(
    r"^[a-zA-ZÀ-ÿ'\- ]+$",
    message="La saisie doit comporter uniquement des caractères alphabétiques avec apostrophe, tiret et espace.",
    code="Saisie invalide",
)

unicodecharfieldvalidator = RegexValidator(
    r"^[\da-zA-ZÀ-ÿ'@.\- ]+$",
    message="La saisie doit comporter uniquement des caractères alphanumériques avec apostrophe, tiret, @, point et espace.",
    code="Saisie invalide",
)

textfieldvalidator = RegexValidator(
    r"^[^<>&~`;%=\n\r\t\$\\\|\/\{\}\[\]\+\*]*$",
    message="La saisie ne doit pas comporter de caractères spéciaux.",
    code="Saisie invalide",
)

digitalcharfieldvalidator = RegexValidator(
    r"^[0-9]+$",
    message="La saisie doit comporter uniquement des caractères numériques.",
    code="Saisie invalide",
)
