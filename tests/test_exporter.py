import copy
import csv
import io
import unittest

from contact_exporter import export_contacts


def parse(text):
    return list(csv.reader(io.StringIO(text, newline="")))


class ExportContactsTests(unittest.TestCase):
    def test_empty_input_has_header(self):
        self.assertEqual(parse(export_contacts([])), [["name", "postal_code"]])

    def test_returns_text(self):
        self.assertIsInstance(export_contacts([]), str)

    def test_regular_contact(self):
        self.assertEqual(
            parse(export_contacts([{"name": "Alice", "postal_code": "94105"}])),
            [["name", "postal_code"], ["Alice", "94105"]],
        )

    def test_preserves_leading_zero_postal_code(self):
        self.assertEqual(
            parse(export_contacts([{"name": "Alice", "postal_code": "02108"}])),
            [["name", "postal_code"], ["Alice", "02108"]],
        )

    def test_preserves_order_and_accepts_generator(self):
        contacts = ({"name": name, "postal_code": "94105"} for name in ["Bob", "Alice"])
        self.assertEqual(
            parse(export_contacts(contacts)),
            [["name", "postal_code"], ["Bob", "94105"], ["Alice", "94105"]],
        )

    def test_quotes_comma_and_double_quote(self):
        name = 'Bob, "Junior"'
        self.assertEqual(
            parse(export_contacts([{"name": name, "postal_code": "94105"}])),
            [["name", "postal_code"], [name, "94105"]],
        )

    def test_preserves_unicode(self):
        self.assertEqual(
            parse(export_contacts([{"name": "陈示例 🌱", "postal_code": "94105"}])),
            [["name", "postal_code"], ["陈示例 🌱", "94105"]],
        )

    def test_preserves_newline_inside_field(self):
        name = "Alice\nExample"
        self.assertEqual(
            parse(export_contacts([{"name": name, "postal_code": "94105"}])),
            [["name", "postal_code"], [name, "94105"]],
        )

    def test_does_not_modify_input(self):
        contacts = [{"name": "Alice", "postal_code": "94105", "note": "keep"}]
        original = copy.deepcopy(contacts)
        export_contacts(contacts)
        self.assertEqual(contacts, original)


if __name__ == "__main__":
    unittest.main()
