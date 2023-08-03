from django.core.validators import RegexValidator


unicodealphavalidator = RegexValidator(
    r"^[a-zA-ZÀ-ÿ'\- ]+$",
    message="La saisie doit comporter uniquement des caractères alphabétiques avec apostrophe, tiret et espace.",
    code="Saisie invalide",
)

unicodecharfieldvalidator = RegexValidator(
    r"^[\da-zA-ZÀ-ÿ'@_\- ]+$",
    message="La saisie doit comporter uniquement des caractères alphanumériques avec apostrophe,\
    tiret, underscore, @ et espace.",
    code="Saisie invalide",
)
